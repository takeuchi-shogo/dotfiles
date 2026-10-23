//! Git hook bypass detection for PreToolUse (pre-bash).
//!
//! `settings.json` の deny (`git commit --no-verify *` / `git commit -n *`) が
//! 拾えない書き方を止める。判定は ptuf の
//! `core.git.{no-verify,env-bypass,config-override-bypass}` を参考にした。
//!
//! deny が通してしまう典型例:
//! - `git commit -m "…" --no-verify`（フラグが末尾）
//! - `HUSKY=0 git commit …` / `LEFTHOOK=0 git commit …`
//! - `git -c core.hooksPath=… commit …`

use regex::Regex;

pub fn bypass_reason(command: &str) -> Option<String> {
    if !is_bypass(command) {
        return None;
    }
    Some(
        "BLOCKED [hook-bypass]: git hook を迂回する書き方が検出されました。\n\
         WHY: `settings.json` の deny は `git commit --no-verify` / `-n` の前置形しか\
         見ないため、末尾の `--no-verify`、`HUSKY=0`/`LEFTHOOK=0`、\
         `git -c core.hooksPath=…` が通り得る。\n\
         FIX: 通常の `git commit` を使い、hook の失敗を直してから再実行してください。\n\
         `--no-verify` / `-n` / hook 無効化は禁止です。"
            .to_string(),
    )
}

fn is_bypass(command: &str) -> bool {
    let spans = git_commit_arg_spans(command);
    if spans.is_empty() {
        return false;
    }
    if spans.iter().any(|args| commit_args_have_no_verify(args)) {
        return true;
    }
    if has_hooks_path_override_on_commit(command) {
        return true;
    }
    has_env_hook_bypass_on_commit(command)
}

/// `git … commit` の各出現について、subcommand 直後の引数列を返す。
/// bulk-add と同じ fail-closed 方針（引用文もヒットし得る）。
fn git_commit_arg_spans(command: &str) -> Vec<&str> {
    let git_commit = Regex::new(
        r#"(?:^|[\s;&|`(<'"])(?:[\w.-]*/)*git(?:[^\n;&|]*?)[\s\\]+commit\b((?:\\\n|[^\n;&|])*)"#,
    )
    .unwrap();
    git_commit
        .captures_iter(command)
        .filter_map(|caps| caps.get(1).map(|m| m.as_str()))
        .collect()
}

fn commit_args_have_no_verify(args: &str) -> bool {
    // メッセージ文字列内の `-n` 誤爆を減らすため、引用符スパーンを潰してから見る。
    let unquoted = strip_shell_quotes(args);
    if Regex::new(r"(?i)(?:^|[\s\\])--no-verify(?:\s|$)")
        .unwrap()
        .is_match(&unquoted)
    {
        return true;
    }
    // `commit` でのみ `-n` は no-verify。結合短オプション (`-an` 等) も含める。
    Regex::new(r"(?:^|[\s\\])-[^-]*n")
        .unwrap()
        .is_match(&unquoted)
}

fn strip_shell_quotes(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    let mut chars = s.chars().peekable();
    while let Some(c) = chars.next() {
        match c {
            '"' | '\'' => {
                let quote = c;
                while let Some(inner) = chars.next() {
                    if inner == quote {
                        break;
                    }
                    // 引用内は空白に置換し、フラグ誤検出を避ける
                    out.push(' ');
                }
            }
            _ => out.push(c),
        }
    }
    out
}

/// `git -c core.hooksPath=… commit`（同一 invocation）を検出する。
fn has_hooks_path_override_on_commit(command: &str) -> bool {
    // git config key は case-insensitive。`-c` と `--config` の両方を見る。
    let re = Regex::new(
        r#"(?i)(?:^|[\s;&|`(<'"])(?:[\w.-]*/)*git\b(?:[^\n;&|]*?)(?:[\s\\]+-c\s+core\.hooksPath(?:\s|=)|[\s\\]+--config(?:=|\s+)core\.hooksPath(?:\s|=))(?:[^\n;&|]*?)[\s\\]+commit\b"#,
    )
    .unwrap();
    re.is_match(command)
}

/// `HUSKY=0 git commit` / `LEFTHOOK=0 git commit`（falsy 代入）を検出する。
fn has_env_hook_bypass_on_commit(command: &str) -> bool {
    let re = Regex::new(
        r#"(?i)(?:^|[\s;&|`(<'"])(?:HUSKY|LEFTHOOK)=(?:0|false|no|off)\b(?:[^\n;&|]*?)(?:[\w.-]*/)*git(?:[^\n;&|]*?)[\s\\]+commit\b"#,
    )
    .unwrap();
    re.is_match(command)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn trailing_no_verify_is_blocked() {
        assert!(is_bypass(r#"git commit -m "fix" --no-verify"#));
        assert!(is_bypass(r#"git commit -am "x" --no-verify"#));
        assert!(is_bypass("git commit -m msg --no-verify"));
    }

    #[test]
    fn leading_no_verify_and_short_n_are_blocked() {
        assert!(is_bypass("git commit --no-verify -m x"));
        assert!(is_bypass("git commit -n -m x"));
        assert!(is_bypass("git commit -n"));
        assert!(is_bypass("git commit -an -m x"));
    }

    #[test]
    fn husky_and_lefthook_env_bypass_are_blocked() {
        assert!(is_bypass(r#"HUSKY=0 git commit -m "x""#));
        assert!(is_bypass(r#"LEFTHOOK=0 git commit -m "x""#));
        assert!(is_bypass("husky=false git commit -m x"));
        assert!(is_bypass("LEFTHOOK=off /usr/bin/git commit -m x"));
    }

    #[test]
    fn core_hooks_path_override_is_blocked() {
        assert!(is_bypass(r#"git -c core.hooksPath=/dev/null commit -m "x""#));
        assert!(is_bypass("git -c core.hooksPath=/tmp/empty commit -m msg"));
        assert!(is_bypass("git --config core.hooksPath=/tmp/empty commit -m msg"));
    }

    #[test]
    fn normal_git_commit_is_not_blocked() {
        assert!(!is_bypass(r#"git commit -m "feat: add feature""#));
        assert!(!is_bypass("git commit -m 'fix typo'"));
        assert!(!is_bypass("git commit -am 'chore: bump'"));
        assert!(!is_bypass("git status"));
        assert!(!is_bypass("git add src/main.rs"));
    }

    #[test]
    fn env_bypass_without_commit_is_not_blocked() {
        assert!(!is_bypass("HUSKY=0 npm test"));
        assert!(!is_bypass("LEFTHOOK=0 git status"));
    }

    #[test]
    fn hooks_path_without_commit_is_not_blocked() {
        assert!(!is_bypass("git -c core.hooksPath=/tmp/empty status"));
        assert!(!is_bypass(
            "git -c core.hooksPath=/tmp/empty config --get core.hooksPath"
        ));
    }

    #[test]
    fn minus_n_inside_commit_message_is_not_blocked() {
        assert!(!is_bypass(
            r#"git commit -m "docs: note that -n means dry-run on push""#
        ));
        assert!(!is_bypass(
            r#"git commit -m 'mention --no-verify is forbidden'"#
        ));
    }

    #[test]
    fn bypass_reason_is_some_only_when_blocked() {
        assert!(bypass_reason("HUSKY=0 git commit -m x").is_some());
        assert!(bypass_reason(r#"git commit -m "ok""#).is_none());
    }
}
