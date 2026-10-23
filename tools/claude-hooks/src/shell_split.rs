//! Bash コマンド文字列を単純コマンドの断片に分ける最小の分割器。
//!
//! 語の分割とクォート除去は呼び出し側で `shlex` に任せ、ここでは shlex が扱わない構文だけを処理する:
//! - 区切り: 改行・`;`・`&&`・`||`・`|`・`|&`・`&`・サブシェルの `(` `)`
//! - 置換: `$(…)`・`` `…` ``・`<(…)`・`>(…)` は本体を取り出し、元の位置を [`DYNAMIC`] に置き換える
//! - 変数展開 `$NAME` / `${…}`、`$'…'`、heredoc 本文、コメント
//!
//! bash の完全な文法ではない。解釈できない入力は `Err` を返し、呼び出し側が fail-closed に倒す。

/// 実行時にしか値が決まらない語を表すプレースホルダ。`$` を含むので「動的な語」と判定できる。
pub const DYNAMIC: &str = "$__DYNAMIC__";

/// クォートされていない展開は単語分割で複数の引数になり得るので、2 語として表す。
const UNQUOTED_DYNAMIC: &str = "$__DYNAMIC__ $__DYNAMIC__";

/// `$( $( … ) )` の入れ子上限。超えたら解釈を諦めて `Err` にする（再帰の深さを抑える）。
const MAX_NESTING: usize = 8;

#[derive(Debug, Default)]
pub struct Split {
    /// 置換を [`DYNAMIC`] に置き換えた単純コマンドの断片。`shlex::split` に渡す前提。
    pub segments: Vec<String>,
    /// `$(…)`・バッククォート・プロセス置換・サブシェルの本体。コマンドとして再検査する。
    pub nested: Vec<String>,
    /// heredoc 本文と、区切り語がクォートされていたか（クォート時は本文が展開されない）。
    pub heredocs: Vec<(String, bool)>,
    /// `$'…'` (ANSI-C quoting) を含んでいたか。
    pub ansi_c: bool,
}

pub fn split(src: &str) -> Result<Split, String> {
    let chars: Vec<char> = src.chars().collect();
    let mut splitter = Splitter::new(&chars, 0, 0);
    splitter.run(false)?;
    Ok(splitter.out)
}

/// 読み終えていない heredoc。改行に達したら本文を読む。
struct PendingHeredoc {
    delimiter: String,
    strip_tabs: bool,
    quoted: bool,
}

#[derive(Default)]
struct Splitter<'a> {
    chars: &'a [char],
    pos: usize,
    depth: usize,
    cur: String,
    out: Split,
    pending: Vec<PendingHeredoc>,
}

impl<'a> Splitter<'a> {
    fn new(chars: &'a [char], pos: usize, depth: usize) -> Self {
        Splitter {
            chars,
            pos,
            depth,
            ..Default::default()
        }
    }

    fn peek(&self, offset: usize) -> Option<char> {
        self.chars.get(self.pos + offset).copied()
    }

    /// `n` 文字をそのまま現在の断片へ写す。
    fn take(&mut self, n: usize) {
        for _ in 0..n {
            if let Some(c) = self.peek(0) {
                self.cur.push(c);
                self.pos += 1;
            }
        }
    }

    fn flush(&mut self) {
        if !self.cur.trim().is_empty() {
            self.out.segments.push(std::mem::take(&mut self.cur));
        }
        self.cur.clear();
    }

    /// `until_paren` が真なら、対応する `)` の位置で止まる（`)` は消費しない）。
    fn run(&mut self, until_paren: bool) -> Result<(), String> {
        while let Some(c) = self.peek(0) {
            match c {
                ')' if until_paren => return Ok(()),
                '\\' => self.take(2),
                '\'' => {
                    let body = self.read_until('\'', false)?;
                    self.cur.push_str(&format!("'{body}'"));
                }
                '"' => self.double_quoted()?,
                '`' => self.backtick(UNQUOTED_DYNAMIC)?,
                '$' => self.dollar()?,
                '<' | '>' if self.peek(1) == Some('(') => {
                    self.pos += 1;
                    self.substitution(UNQUOTED_DYNAMIC)?;
                }
                '<' if self.peek(1) == Some('<') && self.peek(2) == Some('<') => self.take(3),
                '<' if self.peek(1) == Some('<') => self.heredoc_operator()?,
                '(' => {
                    self.flush();
                    self.pos += 1;
                    let body = self.nested_body()?;
                    self.out.nested.push(body);
                }
                '#' if self.at_word_start() => self.skip_comment(),
                '&' if self.is_redirect_ampersand() => self.take(1),
                '\n' => {
                    self.flush();
                    self.pos += 1;
                    self.read_heredoc_bodies();
                }
                ';' | '|' | '&' | ')' => {
                    self.flush();
                    self.pos += 1;
                }
                _ => self.take(1),
            }
        }
        if until_paren {
            return Err("unclosed `(`".to_string());
        }
        self.flush();
        // 改行が来ないまま終わった heredoc は本文が空
        for heredoc in std::mem::take(&mut self.pending) {
            self.out.heredocs.push((String::new(), heredoc.quoted));
        }
        Ok(())
    }

    /// 開き文字の次から `close` までを返し、`close` の直後へ進む。`escapes` なら `\` の次は閉じとみなさない。
    fn read_until(&mut self, close: char, escapes: bool) -> Result<String, String> {
        let start = self.pos + 1;
        let mut i = start;
        loop {
            match self.chars.get(i) {
                None => return Err(format!("unterminated `{close}`")),
                Some(&c) if c == close => break,
                Some('\\') if escapes => i += 2,
                Some(_) => i += 1,
            }
        }
        self.pos = i + 1;
        Ok(self.chars[start..i].iter().collect())
    }

    fn double_quoted(&mut self) -> Result<(), String> {
        self.take(1);
        loop {
            match self.peek(0) {
                None => return Err("unterminated double quote".to_string()),
                Some('"') => break,
                Some('\\') => self.take(2),
                Some('`') => self.backtick(DYNAMIC)?,
                Some('$') if self.peek(1) == Some('(') => {
                    self.pos += 1;
                    self.substitution(DYNAMIC)?;
                }
                Some(_) => self.take(1),
            }
        }
        self.take(1);
        Ok(())
    }

    /// クォート外の `$`。置換・ANSI-C 文字列・変数展開をプレースホルダにする。
    fn dollar(&mut self) -> Result<(), String> {
        let is_name = |c: char| c == '_' || c.is_ascii_alphanumeric();
        match self.peek(1) {
            Some('(') => {
                self.pos += 1;
                return self.substitution(UNQUOTED_DYNAMIC);
            }
            // `$'…'` の中身は `\` でエスケープされるので、単純な `'` 対応では閉じを誤る
            Some('\'') => {
                self.pos += 1;
                self.read_until('\'', true)?;
                self.out.ansi_c = true;
                self.cur.push_str(DYNAMIC);
                return Ok(());
            }
            // `${X:-$(cmd)}` の中の置換も拾えるよう、`{` 以降は通常どおり読み進める
            Some('{') => self.pos += 1,
            Some(c) if is_name(c) => {
                self.pos += 1;
                while self.peek(0).is_some_and(is_name) {
                    self.pos += 1;
                }
            }
            Some('@' | '*' | '#' | '?' | '!' | '-' | '$') => self.pos += 2,
            _ => {
                self.take(1);
                return Ok(());
            }
        }
        self.cur.push_str(UNQUOTED_DYNAMIC);
        Ok(())
    }

    /// `(` の位置から本体を取り出し、元の位置に `placeholder` を置く。
    fn substitution(&mut self, placeholder: &str) -> Result<(), String> {
        self.pos += 1;
        let body = self.nested_body()?;
        self.out.nested.push(body);
        self.cur.push_str(placeholder);
        Ok(())
    }

    /// 現在位置から対応する `)` までを本体として返し、`)` の直後へ進む。
    fn nested_body(&mut self) -> Result<String, String> {
        if self.depth >= MAX_NESTING {
            return Err("nesting too deep".to_string());
        }
        let start = self.pos;
        let mut inner = Splitter::new(self.chars, start, self.depth + 1);
        inner.run(true)?;
        self.pos = inner.pos + 1;
        Ok(self.chars[start..inner.pos].iter().collect())
    }

    fn backtick(&mut self, placeholder: &str) -> Result<(), String> {
        let body = self.read_until('`', true)?;
        self.out.nested.push(body);
        self.cur.push_str(placeholder);
        Ok(())
    }

    /// `<<` / `<<-` と区切り語を読む。本文は次の改行で読む。
    fn heredoc_operator(&mut self) -> Result<(), String> {
        self.pos += 2;
        let strip_tabs = self.peek(0) == Some('-');
        if strip_tabs {
            self.pos += 1;
        }
        while matches!(self.peek(0), Some(' ' | '\t')) {
            self.pos += 1;
        }
        let (mut delimiter, mut quoted) = (String::new(), false);
        while let Some(c) = self.peek(0) {
            if c.is_whitespace() || ";|&<>()".contains(c) {
                break;
            }
            self.pos += 1;
            if matches!(c, '\'' | '"' | '\\') {
                quoted = true;
            } else {
                delimiter.push(c);
            }
        }
        if delimiter.is_empty() {
            return Err("heredoc without delimiter".to_string());
        }
        self.pending.push(PendingHeredoc {
            delimiter,
            strip_tabs,
            quoted,
        });
        Ok(())
    }

    fn read_heredoc_bodies(&mut self) {
        for heredoc in std::mem::take(&mut self.pending) {
            let mut body = String::new();
            while self.pos < self.chars.len() {
                let end = self.chars[self.pos..]
                    .iter()
                    .position(|&c| c == '\n')
                    .map_or(self.chars.len(), |i| self.pos + i);
                let line: String = self.chars[self.pos..end].iter().collect();
                self.pos = (end + 1).min(self.chars.len());
                let compared = if heredoc.strip_tabs {
                    line.trim_start_matches('\t')
                } else {
                    line.as_str()
                };
                if compared == heredoc.delimiter {
                    break;
                }
                body.push_str(&line);
                body.push('\n');
            }
            self.out.heredocs.push((body, heredoc.quoted));
        }
    }

    fn at_word_start(&self) -> bool {
        self.pos == 0
            || matches!(
                self.chars[self.pos - 1],
                ' ' | '\t' | '\n' | ';' | '&' | '|' | '(' | ')'
            )
    }

    fn skip_comment(&mut self) {
        while !matches!(self.peek(0), None | Some('\n')) {
            self.pos += 1;
        }
    }

    /// `2>&1` / `<&0` / `&>log` の `&` はリダイレクトの一部で、区切りではない。
    fn is_redirect_ampersand(&self) -> bool {
        let prev = self.pos.checked_sub(1).map(|i| self.chars[i]);
        matches!(prev, Some('<' | '>')) || self.peek(1) == Some('>')
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// 断片を ` | ` で連結する（`DD` は 2 語の、`D` は 1 語のプレースホルダ）。
    fn render(src: &str) -> String {
        let split = split(src).unwrap();
        let segments: Vec<&str> = split.segments.iter().map(|s| s.trim()).collect();
        segments
            .join(" | ")
            .replace(UNQUOTED_DYNAMIC, "DD")
            .replace(DYNAMIC, "D")
    }

    #[test]
    #[rustfmt::skip]
    fn splits_outside_quotes_redirects_and_comments() {
        let cases = [
            ("a; b && c || d | e |& f & g\nh", "a | b | c | d | e | f | g | h"),
            (r#"git commit -m "a; b" --no-verify"#, r#"git commit -m "a; b" --no-verify"#),
            ("git commit -m x 2>&1 &>log <<< y", "git commit -m x 2>&1 &>log <<< y"),
            (r#"git commit -m $MSG "$X" `id`"#, r#"git commit -m DD "$X" DD"#),
            (r"echo $'it\'s'; git commit -n", "echo D | git commit -n"),
            ("# don't\ngit commit -n; echo a#b", "git commit -n | echo a#b"),
        ];
        for (src, expected) in cases {
            assert_eq!(render(src), expected, "{src:?}");
        }
    }

    #[test]
    fn extracts_nested_and_heredoc_bodies() {
        let s = split(r#"echo "$(git commit -n)" `id` <(ls) (cd x && git status)"#).unwrap();
        assert_eq!(
            s.nested,
            ["git commit -n", "id", "ls", "cd x && git status"]
        );

        let src = "git commit -m \"$(cat <<'EOF'\nfix: don't (break)\nEOF\n)\" --no-verify";
        assert_eq!(render(src), r#"git commit -m "D" --no-verify"#);
        let body = split(src).unwrap().nested.remove(0);
        assert_eq!(
            split(&body).unwrap().heredocs,
            [("fix: don't (break)\n".into(), true)]
        );

        let s = split("sh <<-EOF\n\tgit commit -n\n\tEOF\necho ok").unwrap();
        assert_eq!(s.heredocs, [("\tgit commit -n\n".into(), false)]);
    }

    #[test]
    fn rejects_unbalanced_or_too_deep_input() {
        let deep = format!("{}x{}", "$(".repeat(20), ")".repeat(20));
        for src in [
            "echo 'x", "echo \"x", "echo $(x", "echo `x", "echo $'x", &deep,
        ] {
            assert!(split(src).is_err(), "{src:?}");
        }
    }
}
