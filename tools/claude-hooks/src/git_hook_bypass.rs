//! `git commit` の hook 迂回を検出する（`claude-hooks pre-bash` から呼ぶ）。
//!
//! `settings.json` の deny は `git commit --no-verify *` のような前置パターンしか見ないため、
//! 末尾の `--no-verify`、`HUSKY=0` / `LEFTHOOK=0` などの env、`git -c core.hooksPath=…`、
//! alias、ラッパー経由の実行がすり抜ける。ここではそれらを argv 単位で判定する。
//!
//! - [`shell_split`] で単純コマンドに分け、各断片を `shlex` で語に分ける
//! - `git` は先頭に限らず語の列のどこに現れても調べる（`sudo` / `timeout` / `xargs` などを列挙しない）
//! - `bash -c` / `sh -c` / `eval` / `!` alias / `$(…)` / サブシェルの中身は再帰で調べる
//! - 解釈に自信が持てない入力（heredoc・`$'…'`・git 引数中の変数や置換・解釈できない入れ子）は、
//!   生の文字列が迂回マーカーを含むときだけ block する (fail-closed)
//!
//! 意図的に扱わないもの（永続 `git config core.hooksPath`、別の Bash 呼び出しで export した値、
//! `git push` / `git merge` の `--no-verify` など）は deny-rules-catalog.md に記録している。

use crate::shell_split;

const BYPASS_REASON: &str = "BLOCKED [hook-bypass]: git hook を迂回する書き方が検出されました。\n\
     WHY: `--no-verify` / `-n`、`HUSKY=0` / `LEFTHOOK=0` / `LEFTHOOK_EXCLUDE` などの env、\
     `core.hooksPath` の上書き、xargs 経由の引数追加は lefthook の commit gate を素通りさせるため。\n\
     FIX: 通常の `git commit` を使い、hook の失敗を直してから再実行してください。";

const UNVERIFIABLE_REASON: &str = "BLOCKED [hook-bypass-unverifiable]: hook 迂回の語を含むコマンドを安全と確認できませんでした。\n\
     WHY: heredoc・`$'…'`・変数や置換・解釈できない入れ子があると実際の argv を確定できないため、\
     迂回の語（`--no-verify` / `HUSKY` / `LEFTHOOK` / `core.hooksPath` など）を含む場合は fail-closed で止めます。\n\
     FIX: 変数や置換を使わない形に書き直してください。commit メッセージにこれらの語を書きたいだけなら\
     ファイルに書いて `git commit -F <file>` で渡してください。";

/// 再帰（`bash -c` の中の `eval` の中の … や alias の展開）の上限。
const MAX_DEPTH: usize = 4;
/// これより長い入力は解釈せず「確認できない」扱いにする。
const MAX_COMMAND_BYTES: usize = 100_000;

/// 解釈に自信が持てないとき、生の文字列（小文字化）がこれを含めば block する。
#[rustfmt::skip]
const MARKERS: &[&str] = &[
    "no-veri", "hookspath", "husky", "lefthook", "skip=", "git_config", "config-env", "alias.",
];

/// `-c` で実行文字列を受け取るコマンド（`su` も同じ形）。
const SHELLS: &[&str] = &[
    "sh", "bash", "zsh", "dash", "ksh", "mksh", "ash", "fish", "su",
];

/// 値を必ず取る `git commit` の長いオプション（`=` が無ければ次の語が値）。
#[rustfmt::skip]
const COMMIT_LONG_WITH_VALUE: &[&str] = &[
    "message", "file", "template", "author", "date", "cleanup", "fixup", "squash",
    "reuse-message", "reedit-message", "trailer", "pathspec-from-file",
];

/// 値を次の語で取る git のグローバルオプション（`-c` / `--config-env` は別扱い）。
#[rustfmt::skip]
const GIT_GLOBAL_WITH_VALUE: &[&str] = &[
    "-C", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--attr-source",
];

/// dotfiles の git 設定。alias を足しても、このバイナリを再ビルドすれば判定が追従する。
const GIT_CONFIG: &str = include_str!("../../../.config/git/config");

type Env = Vec<(String, String)>;

/// hook 迂回なら deny 理由を返す。
pub fn bypass_reason(command: &str) -> Option<&'static str> {
    let mut checker = Checker::default();
    if command.len() > MAX_COMMAND_BYTES {
        checker.unverifiable = true;
    } else {
        checker.check_str(command, &mut Env::new(), 0);
    }
    if checker.bypass {
        Some(BYPASS_REASON)
    } else if checker.unverifiable && has_marker(command) {
        Some(UNVERIFIABLE_REASON)
    } else {
        None
    }
}

#[derive(Default)]
struct Checker {
    /// 迂回と判定できた
    bypass: bool,
    /// 実際の argv を確定できない箇所があった
    unverifiable: bool,
}

impl Checker {
    /// コマンド文字列を検査する。`env` には同じ文字列内で先に設定・export された値が溜まる。
    fn check_str(&mut self, src: &str, env: &mut Env, depth: usize) {
        if depth > MAX_DEPTH {
            self.unverifiable = true;
            return;
        }
        let Ok(split) = shell_split::split(src) else {
            self.unverifiable = true;
            return;
        };
        self.unverifiable |= split.ansi_c || !split.heredocs.is_empty();
        let mut commands = Vec::new();
        for segment in &split.segments {
            match shlex::split(segment) {
                Some(words) => commands.push(words),
                None => self.unverifiable = true,
            }
        }
        let mut stdin_shell = false;
        for words in &commands {
            stdin_shell |= self.check_words(words, env, depth);
        }
        // 置換・サブシェル・heredoc の中身は、この文字列で設定された env をすべて引き継いだとみなす
        for body in &split.nested {
            self.check_str(body, &mut env.clone(), depth + 1);
        }
        let runs_shell = stdin_shell
            || commands
                .iter()
                .flatten()
                .any(|w| base(w) == "eval" || SHELLS.contains(&base(w)));
        for (body, quoted) in &split.heredocs {
            // クォートした区切り語の本文は展開されないので、shell が読むときだけコマンドとして調べる
            if !quoted || runs_shell {
                self.check_str(body, &mut env.clone(), depth + 1);
            }
        }
        if stdin_shell {
            // `echo '…' | sh` のように shell が標準入力を読むなら、空白を含む語もコマンドとして調べる
            for word in commands
                .iter()
                .flatten()
                .filter(|w| w.contains(char::is_whitespace))
            {
                self.check_str(word, &mut env.clone(), depth + 1);
            }
        }
    }

    /// 1 つの単純コマンドを検査する。先頭の shell が標準入力からコマンドを読むなら true。
    fn check_words(&mut self, words: &[String], env: &mut Env, depth: usize) -> bool {
        let words = skip_keywords(words);
        let assigns = words.iter().take_while(|w| assignment(w).is_some()).count();
        let Some(head) = words.get(assigns) else {
            // `LEFTHOOK=0; git commit` のような代入だけの文は後続へ引き継ぐ
            env.extend(words.iter().filter_map(|w| assignment(w)));
            return false;
        };
        if matches!(
            base(head),
            "export" | "declare" | "typeset" | "readonly" | "local"
        ) {
            env.extend(words[assigns + 1..].iter().filter_map(|w| assignment(w)));
            return false;
        }
        if is_dynamic(head) {
            // `$G commit -n` のように実行するコマンド自体が動的なら、git かもしれないものとして調べる
            self.unverifiable = true;
            let inline = env_before(env, words, assigns);
            self.check_git(&words[assigns + 1..], &inline, false, true, depth);
        }
        let mut stdin_shell = false;
        let outer: &Env = env;
        for (i, word) in words.iter().enumerate() {
            let rest = &words[i + 1..];
            let inline = || env_before(outer, words, i);
            match base(word) {
                "git" => {
                    let via_xargs = words[..i].iter().any(|w| base(w) == "xargs");
                    self.check_git(rest, &inline(), via_xargs, false, depth);
                }
                "eval" => self.check_str(&rest.join(" "), &mut inline(), depth + 1),
                name if SHELLS.contains(&name) => match shell_payload(rest) {
                    Some(payload) => self.check_str(payload, &mut inline(), depth + 1),
                    None => stdin_shell |= i == assigns,
                },
                _ => {}
            }
        }
        self.unverifiable |= stdin_shell;
        stdin_shell
    }

    /// `git` の直後からの引数を検査する。`dynamic_head` はコマンド名が変数だった場合。
    fn check_git(
        &mut self,
        args: &[String],
        env: &Env,
        via_xargs: bool,
        dynamic_head: bool,
        depth: usize,
    ) {
        if depth > MAX_DEPTH {
            self.unverifiable = true;
            return;
        }
        let globals = GitGlobals::parse(args);
        self.bypass |= globals.overrides_hooks;
        self.unverifiable |= globals.dynamic;
        let Some(index) = globals.subcommand else {
            if dynamic_head {
                self.check_commit(args, env, via_xargs);
            }
            return;
        };
        let (sub, rest) = (args[index].as_str(), &args[index + 1..]);
        if is_dynamic(sub) {
            // `git $SUB -n` は commit かもしれない
            self.unverifiable = true;
            self.check_commit(rest, env, via_xargs);
        } else if let Some(value) = repo_alias(sub) {
            self.expand_alias(value, rest, env, via_xargs, depth);
        } else if sub == "commit" {
            self.check_commit(rest, env, via_xargs);
        }
    }

    fn expand_alias(
        &mut self,
        value: &str,
        rest: &[String],
        env: &Env,
        via_xargs: bool,
        depth: usize,
    ) {
        if let Some(shell) = value.strip_prefix('!') {
            let command = format!("{shell} {}", rest.join(" "));
            self.check_str(&command, &mut env.clone(), depth + 1);
            return;
        }
        match shlex::split(value) {
            Some(mut args) => {
                args.extend_from_slice(rest);
                self.check_git(&args, env, via_xargs, false, depth + 1);
            }
            None => self.unverifiable = true,
        }
    }

    fn check_commit(&mut self, args: &[String], env: &Env, via_xargs: bool) {
        // xargs は標準入力から引数を足すので argv を確定できない
        self.bypass |= via_xargs || env_disables_hooks(env) || commit_args_bypass(args);
        self.unverifiable |= args.iter().any(|a| is_dynamic(a));
    }
}

/// `git` とサブコマンドの間（`-C dir` / `-c key=value` など）の解析結果。
#[derive(Default)]
struct GitGlobals {
    subcommand: Option<usize>,
    overrides_hooks: bool,
    dynamic: bool,
}

impl GitGlobals {
    fn parse(args: &[String]) -> Self {
        let mut globals = GitGlobals::default();
        let mut i = 0;
        while let Some(arg) = args.get(i).map(String::as_str) {
            match arg {
                "-c" | "--config-env" => {
                    globals.overrides_hooks |=
                        args.get(i + 1).is_some_and(|spec| overrides_hooks(spec));
                    i += 2;
                }
                _ if arg.starts_with("--config-env=") => {
                    globals.overrides_hooks |= overrides_hooks(&arg["--config-env=".len()..]);
                    i += 1;
                }
                _ if GIT_GLOBAL_WITH_VALUE.contains(&arg) => i += 2,
                _ if arg.starts_with('-') => i += 1,
                _ => {
                    globals.subcommand = Some(i);
                    break;
                }
            }
        }
        let end = globals.subcommand.unwrap_or(args.len());
        globals.dynamic = args[..end].iter().any(|a| is_dynamic(a));
        globals
    }
}

/// `-c key=value` / `--config-env key=ENVVAR` が hooksPath を上書きするか。
/// その場で alias を定義して commit を包む書き方も、展開を追わずに迂回とみなす。
fn overrides_hooks(spec: &str) -> bool {
    let key = spec
        .split('=')
        .next()
        .unwrap_or_default()
        .to_ascii_lowercase();
    is_dynamic(&key) || key == "core.hookspath" || key.starts_with("alias.")
}

/// dotfiles の `[alias]` から値を引く（alias 名は大文字小文字を区別しない）。
fn repo_alias(name: &str) -> Option<&'static str> {
    let mut in_alias_section = false;
    for line in GIT_CONFIG.lines().map(str::trim) {
        if line.starts_with('[') {
            in_alias_section = line.eq_ignore_ascii_case("[alias]");
            continue;
        }
        let entry = line.split_once('=').filter(|_| in_alias_section);
        if let Some((_, value)) = entry.filter(|(key, _)| key.trim().eq_ignore_ascii_case(name)) {
            return Some(value.trim());
        }
    }
    None
}

/// commit hook を無効化・差し替えする環境変数があるか。
fn env_disables_hooks(env: &Env) -> bool {
    env.iter().any(|(key, value)| {
        let lower = value.to_ascii_lowercase();
        match key.as_str() {
            // `0` / `false` で無効化される。有効を示す値以外はすべて止める (fail-closed)
            "HUSKY" | "LEFTHOOK" => !matches!(lower.as_str(), "1" | "true"),
            "LEFTHOOK_EXCLUDE" | "SKIP" => !value.is_empty(),
            // 設定ファイルや lefthook 本体を差し替えられる
            "LEFTHOOK_CONFIG" | "LEFTHOOK_BIN" => true,
            "GIT_CONFIG_PARAMETERS" => lower.contains("hookspath") || lower.contains("alias."),
            // GIT_CONFIG_COUNT の値ではなく実在する KEY_n だけを見る（巨大な COUNT でもループしない）
            _ if key.starts_with("GIT_CONFIG_KEY_") => {
                lower == "core.hookspath" || lower.starts_with("alias.")
            }
            _ => false,
        }
    })
}

enum CommitArg {
    Bypass,
    TakesValue,
    /// `>` / `2>` のように対象が次の語にあるリダイレクト
    BareRedirect,
    Other,
}

/// `git commit` の引数に hook を止めるフラグ、または中身を確定できない動的な引数があるか。
fn commit_args_bypass(args: &[String]) -> bool {
    let mut i = 0;
    while let Some(arg) = args.get(i).map(String::as_str) {
        if arg == "--" || arg == "--end-of-options" {
            return false;
        }
        i += match commit_arg(arg) {
            CommitArg::Bypass => return true,
            CommitArg::TakesValue | CommitArg::BareRedirect => 2,
            CommitArg::Other => 1,
        };
    }
    false
}

fn commit_arg(raw: &str) -> CommitArg {
    if raw
        .trim_start_matches(|c: char| c.is_ascii_digit())
        .starts_with(['<', '>'])
        || raw.starts_with("&>")
    {
        let bare = raw
            .chars()
            .all(|c| c.is_ascii_digit() || "<>&|".contains(c));
        return if bare && !raw.ends_with(|c: char| c.is_ascii_digit()) {
            CommitArg::BareRedirect
        } else {
            CommitArg::Other
        };
    }
    // `--no-verify>log` のように語の直後に付いたリダイレクトは切り落とす
    let arg = raw.find(['<', '>']).map_or(raw, |end| &raw[..end]);
    if let Some(long) = arg.strip_prefix("--") {
        let name = long.split('=').next().unwrap_or_default();
        // `--no-veri` 以上の長さなら git は `--no-verify` の省略形として受け付ける
        if is_dynamic(name) || (name.len() >= "no-veri".len() && "no-verify".starts_with(name)) {
            return CommitArg::Bypass;
        }
        let takes_value = !long.contains('=') && COMMIT_LONG_WITH_VALUE.contains(&name);
        return if takes_value {
            CommitArg::TakesValue
        } else {
            CommitArg::Other
        };
    }
    match arg.strip_prefix('-') {
        Some(cluster) if !cluster.is_empty() => short_cluster(cluster),
        // 単語分割や置換で `--no-verify` に化け得る
        _ if is_dynamic(arg) => CommitArg::Bypass,
        _ => CommitArg::Other,
    }
}

/// `-am` のような短いオプションの束。
fn short_cluster(cluster: &str) -> CommitArg {
    for (i, c) in cluster.char_indices() {
        match c {
            'n' | '$' | '`' => return CommitArg::Bypass,
            // 残りがあればそれが値、無ければ次の語が値
            'm' | 'F' | 'c' | 'C' | 't' => {
                return if i + 1 == cluster.len() {
                    CommitArg::TakesValue
                } else {
                    CommitArg::Other
                };
            }
            // `-u[<mode>]` / `-S[<keyid>]` は値が省略可能なので、次の語は消費しない
            'u' | 'S' => return CommitArg::Other,
            _ => {}
        }
    }
    CommitArg::Other
}

/// `bash -c '…'` / `bash -lc '…'` / `su -c '…'` の実行文字列（`-c` を含む短いフラグの次の語）。
fn shell_payload(args: &[String]) -> Option<&str> {
    let flag = args.iter().position(|arg| {
        arg.strip_prefix('-').is_some_and(|flags| {
            flags.contains('c') && flags.chars().all(|c| c.is_ascii_alphabetic())
        })
    })?;
    args.get(flag + 1).map(String::as_str)
}

/// 先頭の `{` `!` や制御構文の予約語を飛ばす（`if git commit -n; then` など）。
fn skip_keywords(words: &[String]) -> &[String] {
    const KEYWORDS: &[&str] = &[
        "{", "}", "!", "if", "then", "else", "elif", "do", "while", "until", "time",
    ];
    let start = words
        .iter()
        .take_while(|w| KEYWORDS.contains(&w.as_str()))
        .count();
    &words[start..]
}

fn assignment(word: &str) -> Option<(String, String)> {
    let (name, value) = word.split_once('=')?;
    let valid = name.starts_with(|c: char| c == '_' || c.is_ascii_alphabetic())
        && name.chars().all(|c| c == '_' || c.is_ascii_alphanumeric());
    valid.then(|| (name.to_string(), value.to_string()))
}

/// 文字列内で設定済みの env に、`words[..end]` の `NAME=value`（`env` / `sudo` の引数を含む）を足す。
fn env_before(env: &Env, words: &[String], end: usize) -> Env {
    let mut merged = env.clone();
    merged.extend(words[..end].iter().filter_map(|w| assignment(w)));
    merged
}

fn is_dynamic(word: &str) -> bool {
    word.contains(['$', '`'])
}

fn base(word: &str) -> &str {
    word.rsplit('/').next().unwrap_or(word)
}

fn has_marker(command: &str) -> bool {
    let lower = command.to_ascii_lowercase();
    MARKERS.iter().any(|marker| lower.contains(marker))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn repo_aliases_come_from_dotfiles_git_config() {
        assert_eq!(repo_alias("cm"), Some("commit -m"));
        assert_eq!(repo_alias("CANE"), Some("commit --amend --no-edit"));
        assert_eq!(repo_alias("st"), Some("status -sb"));
        assert_eq!(repo_alias("commit"), None);
    }

    /// 値が省略可能な `-u` / `-S` は次の語を消費しない。値必須の `-m` などは消費する。
    #[test]
    #[rustfmt::skip]
    fn commit_args_consume_values_only_when_required() {
        let cases = [
            ("-u -n", true), ("--untracked-files --no-verify", true), ("-S -n", true),
            ("-m x --no-verify>log", true), ("-m x > log -n", true),
            ("-uno -m -n", false), ("--message --no-verify", false), ("-m x -- --no-verify", false),
            ("-m x 2>&1 > -n", false), ("-m x --no-verify2>err", false),
        ];
        for (args, expected) in cases {
            let words: Vec<String> = args.split(' ').map(str::to_string).collect();
            assert_eq!(commit_args_bypass(&words), expected, "{args}");
        }
    }
}
