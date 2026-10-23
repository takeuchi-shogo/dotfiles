//! `git commit` のよくある hook 迂回を検出する（`claude-hooks pre-bash` から呼ぶ）。
//!
//! 単純コマンドへの分割は引用符の外の `;` `&&` `||` `|` 改行だけ。語の分割は `shlex`。
//! 分割できない入力・eval / bash -c / 変数経由などの凝った回避は通す（既知の穴）。

const REASON: &str = "BLOCKED [hook-bypass]: git hook を迂回する書き方が検出されました。\n\
     WHY: `--no-verify` / `-n`、`HUSKY=0` / `LEFTHOOK=0`、`core.hooksPath` の上書きは\
     lefthook の commit gate を素通りさせるため。\n\
     FIX: 通常の `git commit` を使い、hook の失敗を直してから再実行してください。";

/// 値を次の語で取る git のグローバルオプション（`-c` は別扱い）。
const GIT_GLOBAL_WITH_VALUE: &[&str] = &["-C", "--git-dir", "--work-tree"];

/// hook 迂回なら deny 理由を返す。解釈できない入力は通す。
pub fn bypass_reason(command: &str) -> Option<&'static str> {
    split_commands(command)
        .iter()
        .any(|segment| is_bypass(segment))
        .then_some(REASON)
}

/// 引用符の外で `;` `&&` `||` `|` 改行に沿って単純コマンドへ分ける。
fn split_commands(src: &str) -> Vec<String> {
    let mut out = Vec::new();
    let mut cur = String::new();
    let mut quote: Option<char> = None;
    let mut chars = src.chars().peekable();
    while let Some(c) = chars.next() {
        if let Some(q) = quote {
            cur.push(c);
            if c == q {
                quote = None;
            } else if c == '\\' {
                if let Some(next) = chars.next() {
                    cur.push(next);
                }
            }
            continue;
        }
        match c {
            '\'' | '"' => {
                quote = Some(c);
                cur.push(c);
            }
            '\\' => {
                cur.push(c);
                if let Some(next) = chars.next() {
                    cur.push(next);
                }
            }
            ';' | '\n' => flush_segment(&mut out, &mut cur),
            '&' if chars.peek() == Some(&'&') => {
                chars.next();
                flush_segment(&mut out, &mut cur);
            }
            '|' => {
                if chars.peek() == Some(&'|') {
                    chars.next();
                }
                flush_segment(&mut out, &mut cur);
            }
            _ => cur.push(c),
        }
    }
    flush_segment(&mut out, &mut cur);
    out
}

fn flush_segment(out: &mut Vec<String>, cur: &mut String) {
    if !cur.trim().is_empty() {
        out.push(std::mem::take(cur));
    }
    cur.clear();
}

fn is_bypass(segment: &str) -> bool {
    let Some(words) = shlex::split(segment) else {
        return false;
    };
    let Some(git_at) = git_index(&words) else {
        return false;
    };
    let env: Vec<(String, String)> = words[..git_at]
        .iter()
        .filter_map(|w| assignment(w))
        .collect();
    git_commit_bypass(&words[git_at + 1..], &env)
}

/// 代入と `env` を飛ばした先頭が `git` なら、その添字を返す。
fn git_index(words: &[String]) -> Option<usize> {
    let mut i = skip_assignments(words, 0);
    if words.get(i).is_some_and(|w| base(w) == "env") {
        i = skip_env_args(words, i + 1);
    }
    words.get(i).is_some_and(|w| base(w) == "git").then_some(i)
}

fn skip_assignments(words: &[String], mut i: usize) -> usize {
    while words.get(i).and_then(|w| assignment(w)).is_some() {
        i += 1;
    }
    i
}

fn skip_env_args(words: &[String], mut i: usize) -> usize {
    while i < words.len() {
        if assignment(&words[i]).is_some() {
            i += 1;
            continue;
        }
        if words[i] == "-u" || words[i] == "--unset" {
            i += 2;
            continue;
        }
        if words[i].starts_with('-') {
            i += 1;
            continue;
        }
        break;
    }
    i
}

fn git_commit_bypass(args: &[String], env: &[(String, String)]) -> bool {
    let (sub, rest, hooks_path) = parse_git_globals(args);
    sub == Some("commit") && (hooks_path || env_disables(env) || commit_no_verify(rest))
}

/// `git` の直後からサブコマンドまで。`-c core.hooksPath` があれば印を付ける。
fn parse_git_globals(args: &[String]) -> (Option<&str>, &[String], bool) {
    let mut i = 0;
    let mut hooks_path = false;
    while let Some(arg) = args.get(i).map(String::as_str) {
        if arg == "-c" {
            hooks_path |= args.get(i + 1).is_some_and(|spec| is_hooks_path(spec));
            i += 2;
            continue;
        }
        if GIT_GLOBAL_WITH_VALUE.contains(&arg) {
            i += 2;
            continue;
        }
        if arg.starts_with('-') {
            i += 1;
            continue;
        }
        return (Some(arg), &args[i + 1..], hooks_path);
    }
    (None, &[], hooks_path)
}

fn is_hooks_path(spec: &str) -> bool {
    spec.split('=')
        .next()
        .unwrap_or_default()
        .eq_ignore_ascii_case("core.hooksPath")
}

fn env_disables(env: &[(String, String)]) -> bool {
    env.iter().any(|(key, value)| {
        matches!(key.as_str(), "HUSKY" | "LEFTHOOK")
            && !matches!(value.to_ascii_lowercase().as_str(), "1" | "true")
    })
}

fn commit_no_verify(args: &[String]) -> bool {
    for arg in args {
        if arg == "--" {
            return false;
        }
        if arg == "--no-verify" || arg.starts_with("--no-verify=") {
            return true;
        }
        // `-m "- add new feature"` のような値は空白や記号を含むので、短いフラグの束ではない
        if let Some(cluster) = arg
            .strip_prefix('-')
            .filter(|s| !s.is_empty() && s.chars().all(|c| c.is_ascii_alphabetic()))
        {
            if short_flags_have_n(cluster) {
                return true;
            }
        }
    }
    false
}

/// `-an` の `n` を検出する。`-m` 以降は値、`-uno` の `u` 以降も値なので見ない。
fn short_flags_have_n(cluster: &str) -> bool {
    for c in cluster.chars() {
        match c {
            'n' => return true,
            'm' | 'F' | 'c' | 'C' | 't' | 'u' | 'S' => return false,
            _ => {}
        }
    }
    false
}

fn assignment(word: &str) -> Option<(String, String)> {
    let (name, value) = word.split_once('=')?;
    let valid = name.starts_with(|c: char| c == '_' || c.is_ascii_alphabetic())
        && name.chars().all(|c| c == '_' || c.is_ascii_alphanumeric());
    valid.then(|| (name.to_string(), value.to_string()))
}

fn base(word: &str) -> &str {
    word.rsplit('/').next().unwrap_or(word)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn splits_on_operators_outside_quotes() {
        let got = split_commands(r#"git add a && git commit -m "a; b" --no-verify"#);
        assert_eq!(got.len(), 2, "{got:?}");
        assert!(got[1].contains("--no-verify"));
        assert!(got[1].contains(r#""a; b""#));
    }

    #[test]
    fn short_n_in_cluster_but_not_in_untracked_value() {
        assert!(short_flags_have_n("an"));
        assert!(short_flags_have_n("n"));
        assert!(!short_flags_have_n("am"));
        assert!(!short_flags_have_n("uno"));
    }
}
