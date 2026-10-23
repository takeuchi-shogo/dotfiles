//! Git hook bypass detection for PreToolUse (pre-bash).
//!
//! `settings.json` の deny (`git commit --no-verify *` / `git commit -n *` /
//! `git commit -n`) が拾えない書き方を止める。
//!
//! 判定は [ptuf](https://github.com/watany-dev/ptuf) の
//! `core.git.{no-verify,env-bypass,config-override-bypass}` を参考にしつつ、
//! シェル字句解析 → argv トークン単位にしている（正規表現マッチは使わない）。
//! 移植で変えた点: この repo の git alias（`cm` / `cane`）展開、同一行の
//! `export` 引き継ぎ、`--config-env` / `GIT_CONFIG_*`、`--no-verify>log` と
//! git が受け付ける `--no-veri*` 省略形。
//!
//! deny が通してしまう典型例:
//! - `git commit -m "…" --no-verify`（フラグが末尾）
//! - `HUSKY=0 git commit …` / `LEFTHOOK=0 git commit …`
//! - `git -c core.hooksPath=… commit …`

use crate::shell_lex::{self, Command};

const DENY_MESSAGE: &str = "BLOCKED [hook-bypass]: git hook を迂回する書き方が検出されました。\n\
     WHY: `settings.json` の deny は `git commit --no-verify` / `-n` の前置形しか\
     見ないため、末尾の `--no-verify`、hook 無効化 env、`git -c core.hooksPath=…` 等が通り得る。\n\
     FIX: 通常の `git commit` を使い、hook の失敗を直してから再実行してください。\n\
     `--no-verify` / `-n` / hook 無効化は禁止です。";

/// `.config/git/config` `[alias]` のうち commit 系（dotfiles SSOT）。
const COMMIT_ALIASES: &[(&str, &[&str])] = &[
    ("cm", &["commit", "-m"]),
    ("cane", &["commit", "--amend", "--no-edit"]),
];

/// Deny reason when the command bypasses git/lefthook hooks; `None` if clean.
pub fn bypass_reason(command: &str) -> Option<&'static str> {
    if is_bypass(command) {
        Some(DENY_MESSAGE)
    } else {
        None
    }
}

fn is_bypass(command: &str) -> bool {
    let cmds = shell_lex::parse_commands(command);
    let mut ambient: Vec<(String, String)> = Vec::new();
    for cmd in &cmds {
        absorb_export(cmd, &mut ambient);
        if command_is_bypass(cmd, &ambient) {
            return true;
        }
    }
    false
}

fn absorb_export(cmd: &Command, ambient: &mut Vec<(String, String)>) {
    // `export KEY=VAL` と、シェルと同様の裸代入 `KEY=VAL`（後続コマンドに効く）
    if cmd.head.is_empty() {
        for (k, v) in &cmd.env_assignments {
            upsert(ambient, k, v);
        }
        return;
    }
    if basename(&cmd.head) != "export" {
        return;
    }
    for arg in &cmd.args {
        if let Some((k, v)) = split_kv(arg) {
            upsert(ambient, k, v);
        }
    }
    for (k, v) in &cmd.env_assignments {
        upsert(ambient, k, v);
    }
}

fn upsert(env: &mut Vec<(String, String)>, key: &str, value: &str) {
    if let Some(slot) = env.iter_mut().find(|(k, _)| k == key) {
        slot.1 = value.to_string();
    } else {
        env.push((key.to_string(), value.to_string()));
    }
}

fn split_kv(word: &str) -> Option<(&str, &str)> {
    let eq = word.find('=')?;
    if eq == 0 {
        return None;
    }
    Some((&word[..eq], &word[eq + 1..]))
}

fn command_is_bypass(cmd: &Command, ambient: &[(String, String)]) -> bool {
    let merged_env = merge_env(ambient, &cmd.env_assignments);
    let Some((sub, rest)) = git_commit_argv(cmd) else {
        return false;
    };
    if commit_args_have_no_verify(&rest) {
        return true;
    }
    if has_hooks_path_override(cmd, &merged_env, sub) {
        return true;
    }
    env_bypasses_hooks(&merged_env)
}

fn merge_env(ambient: &[(String, String)], inline: &[(String, String)]) -> Vec<(String, String)> {
    let mut out = ambient.to_vec();
    for (k, v) in inline {
        upsert(&mut out, k, v);
    }
    out
}

/// Resolve `git` (+ alias) into (`commit`, args_after_commit) when this is a commit.
fn git_commit_argv(cmd: &Command) -> Option<(&'static str, Vec<String>)> {
    if !is_git_head(&cmd.head) {
        return None;
    }
    let expanded = expand_git_args(&cmd.args);
    let (sub, rest) = skip_git_globals(&expanded)?;
    if sub != "commit" {
        return None;
    }
    Some(("commit", rest))
}

fn is_git_head(head: &str) -> bool {
    basename(head) == "git"
}

fn basename(path: &str) -> &str {
    path.rsplit('/').next().unwrap_or(path)
}

fn expand_git_args(args: &[String]) -> Vec<String> {
    if args.is_empty() {
        return Vec::new();
    }
    for (alias, expansion) in COMMIT_ALIASES {
        if args[0] == *alias {
            let mut out: Vec<String> = expansion.iter().map(|s| (*s).to_string()).collect();
            out.extend(args[1..].iter().cloned());
            return out;
        }
    }
    args.to_vec()
}

/// Skip `git` global options; return (subcommand, rest).
fn skip_git_globals(args: &[String]) -> Option<(String, Vec<String>)> {
    let mut i = 0;
    while i < args.len() {
        let a = args[i].as_str();
        if a == "-c" || a == "-C" || a == "--git-dir" || a == "--work-tree"
            || a == "--namespace" || a == "--exec-path" || a == "--super-prefix"
            || a == "--config-env"
        {
            i += 2; // flag + value (best-effort; missing value → stop)
            continue;
        }
        if a.starts_with("-c") && a.len() > 2 {
            // unusual; treat as one token
            i += 1;
            continue;
        }
        if let Some(rest) = a.strip_prefix("--config-env=") {
            let _ = rest;
            i += 1;
            continue;
        }
        if a.starts_with("--git-dir=")
            || a.starts_with("--work-tree=")
            || a.starts_with("--namespace=")
            || a.starts_with("--exec-path=")
            || a.starts_with("--super-prefix=")
        {
            i += 1;
            continue;
        }
        if a.starts_with('-') {
            // other globals (-p, --no-pager, …)
            i += 1;
            continue;
        }
        let sub = a.to_string();
        let rest = args[i + 1..].to_vec();
        return Some((sub, rest));
    }
    None
}

fn commit_args_have_no_verify(args: &[String]) -> bool {
    let mut i = 0;
    while i < args.len() {
        let raw = args[i].as_str();
        let flag = strip_redir_suffix(raw);
        if is_no_verify_long(flag) {
            return true;
        }
        if is_no_verify_short(flag) {
            return true;
        }
        // value-taking commit options: skip attached/next value
        if takes_value_short(flag) || takes_value_long(flag) {
            if flag.contains('=') || short_has_attached_value(flag) {
                i += 1;
            } else {
                i += 2;
            }
            continue;
        }
        i += 1;
    }
    false
}

/// `--no-verify>log` → `--no-verify`
fn strip_redir_suffix(token: &str) -> &str {
    let bytes = token.as_bytes();
    let mut i = 0;
    while i < bytes.len() {
        if bytes[i] == b'>' || bytes[i] == b'<' {
            // keep leading fd like `2>` only when whole token is redirect — for flags, cut here
            if i > 0 {
                return &token[..i];
            }
        }
        i += 1;
    }
    token
}

fn is_no_verify_long(flag: &str) -> bool {
    // git が受け付ける省略は `--no-veri` 以上（`--no-ver` は --no-verbose と曖昧）。
    const FULL: &str = "--no-verify";
    const MIN: &str = "--no-veri";
    if !flag.starts_with("--") {
        return false;
    }
    if flag.len() < MIN.len() {
        return false;
    }
    FULL.starts_with(flag)
}

fn is_no_verify_short(flag: &str) -> bool {
    if !flag.starts_with('-') || flag.starts_with("--") || flag == "-" {
        return false;
    }
    let chars: Vec<char> = flag[1..].chars().collect();
    let mut i = 0;
    while i < chars.len() {
        match chars[i] {
            'n' => return true,
            // value-taking: remainder is the value (e.g. `-uno` → `-u` + `no`)
            'm' | 'F' | 't' | 'c' | 'C' | 'u' => return false,
            _ => i += 1,
        }
    }
    false
}

fn takes_value_short(flag: &str) -> bool {
    if !flag.starts_with('-') || flag.starts_with("--") {
        return false;
    }
    let body = &flag[1..];
    body.starts_with('m')
        || body.starts_with('F')
        || body.starts_with('t')
        || body.starts_with('c')
        || body.starts_with('C')
        || body.starts_with('u')
}

fn short_has_attached_value(flag: &str) -> bool {
    if !flag.starts_with('-') || flag.starts_with("--") {
        return false;
    }
    flag.len() > 2
}

fn takes_value_long(flag: &str) -> bool {
    let base = flag.split('=').next().unwrap_or(flag);
    matches!(
        base,
        "--message"
            | "--file"
            | "--template"
            | "--author"
            | "--date"
            | "--cleanup"
            | "--fixup"
            | "--squash"
            | "--reuse-message"
            | "--reedit-message"
            | "--untracked-files"
    ) || base == "-m"
        || base == "-F"
        || base == "-t"
        || base == "-c"
        || base == "-C"
}

fn has_hooks_path_override(cmd: &Command, env: &[(String, String)], _sub: &str) -> bool {
    if git_argv_overrides_hooks_path(cmd) {
        return true;
    }
    env_overrides_hooks_path(env)
}

fn git_argv_overrides_hooks_path(cmd: &Command) -> bool {
    if !is_git_head(&cmd.head) {
        return false;
    }
    let args = expand_git_args(&cmd.args);
    let mut i = 0;
    while i < args.len() {
        let a = args[i].as_str();
        if a == "-c" {
            if let Some(spec) = args.get(i + 1) {
                if is_hooks_path_assignment(spec) {
                    return true;
                }
            }
            i += 2;
            continue;
        }
        if let Some(spec) = a.strip_prefix("-c") {
            if !spec.is_empty() && is_hooks_path_assignment(spec) {
                return true;
            }
        }
        if a == "--config-env" {
            if let Some(spec) = args.get(i + 1) {
                if config_env_targets_hooks_path(spec) {
                    return true;
                }
            }
            i += 2;
            continue;
        }
        if let Some(spec) = a.strip_prefix("--config-env=") {
            if config_env_targets_hooks_path(spec) {
                return true;
            }
        }
        // stop at subcommand
        if !a.starts_with('-') {
            break;
        }
        i += 1;
    }
    false
}

fn is_hooks_path_assignment(spec: &str) -> bool {
    let (key, _val) = spec.split_once('=').unwrap_or((spec, ""));
    key.eq_ignore_ascii_case("core.hooksPath")
}

fn config_env_targets_hooks_path(spec: &str) -> bool {
    // `core.hooksPath:ENVVAR` or `core.hooksPath=ENVVAR` (git accepts `:`)
    let key = spec.split([':', '=']).next().unwrap_or(spec);
    key.eq_ignore_ascii_case("core.hooksPath")
}

fn env_overrides_hooks_path(env: &[(String, String)]) -> bool {
    if let Some((_, params)) = env.iter().find(|(k, _)| k == "GIT_CONFIG_PARAMETERS") {
        if params_contain_hooks_path(params) {
            return true;
        }
    }
    let Some((_, count_s)) = env.iter().find(|(k, _)| k == "GIT_CONFIG_COUNT") else {
        return false;
    };
    let Ok(count) = count_s.parse::<usize>() else {
        return false;
    };
    for idx in 0..count {
        let key_name = format!("GIT_CONFIG_KEY_{idx}");
        if let Some((_, key)) = env.iter().find(|(k, _)| *k == key_name) {
            if key.eq_ignore_ascii_case("core.hooksPath") {
                return true;
            }
        }
    }
    false
}

fn params_contain_hooks_path(params: &str) -> bool {
    // values look like: `'core.hooksPath=/x'` or `core.hooksPath=/x`
    for piece in params.split_whitespace() {
        let cleaned = piece.trim_matches(|c| c == '\'' || c == '"');
        if is_hooks_path_assignment(cleaned) {
            return true;
        }
    }
    params.to_ascii_lowercase().contains("core.hookspath")
}

fn env_bypasses_hooks(env: &[(String, String)]) -> bool {
    for (k, v) in env {
        match k.as_str() {
            // HUSKY: この repo は lefthook 運用で実質無効だが、インライン無効化は止める
            "HUSKY" if is_falsy(v) => return true,
            "LEFTHOOK" if is_falsy(v) => return true,
            "LEFTHOOK_EXCLUDE" if !v.is_empty() => return true,
            "SKIP" if !v.is_empty() => return true,
            _ => {}
        }
    }
    false
}

fn is_falsy(v: &str) -> bool {
    matches!(v.trim().to_ascii_lowercase().as_str(), "0" | "false" | "no" | "off" | "")
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
    fn must_heredoc_message_with_trailing_no_verify() {
        let cmd = "git commit -m \"$(cat <<'EOF'\nbody\nEOF\n)\" --no-verify";
        assert!(is_bypass(cmd));
    }

    #[test]
    fn must_semicolon_inside_message_with_trailing_no_verify() {
        assert!(is_bypass(r#"git commit -m "a; b" --no-verify"#));
    }

    #[test]
    fn must_quoted_no_verify_flags() {
        assert!(is_bypass(r#"git commit '--no-verify' -m x"#));
        assert!(is_bypass(r#"git commit "-n" -m x"#));
    }

    #[test]
    fn must_quoted_hooks_path_override() {
        assert!(is_bypass(
            r#"git -c "core.hooksPath=/dev/null" commit -m x"#
        ));
    }

    #[test]
    fn must_quoted_husky_env() {
        assert!(is_bypass(r#"HUSKY="0" git commit -m x"#));
    }

    #[test]
    fn must_not_block_normal_commits() {
        assert!(!is_bypass(r#"git commit -m "fix" src/main.rs"#));
        assert!(!is_bypass("git commit -F notes.txt"));
        assert!(!is_bypass("git commit -m initial"));
        assert!(!is_bypass("git commit -uno -m x"));
        assert!(!is_bypass(
            r#"git commit -m "docs: mention --no-verify is forbidden""#
        ));
        assert!(!is_bypass(
            r#"git commit -m "docs: note that -n means dry-run on push""#
        ));
    }

    #[test]
    fn lefthook_env_bypass_is_blocked() {
        assert!(is_bypass(r#"LEFTHOOK=0 git commit -m "x""#));
        assert!(is_bypass("LEFTHOOK=off /usr/bin/git commit -m x"));
        assert!(is_bypass(
            "LEFTHOOK_EXCLUDE=publicity-review git commit -m x"
        ));
        assert!(is_bypass("SKIP=hook git commit -m x"));
    }

    #[test]
    fn export_then_commit_is_blocked() {
        assert!(is_bypass("export LEFTHOOK=0; git commit -m x"));
        assert!(is_bypass(
            "export LEFTHOOK_EXCLUDE=check-new-todo && git commit -m x"
        ));
        assert!(is_bypass("export SKIP=hooks; git cm 'x'"));
        // 裸代入も後続 commit に効く（bash と同様）
        assert!(is_bypass("LEFTHOOK=0; git commit -m x"));
    }

    #[test]
    fn git_aliases_cm_and_cane_are_checked() {
        assert!(is_bypass(r#"git cm "x" --no-verify"#));
        assert!(is_bypass("git cane --no-verify"));
        assert!(is_bypass("LEFTHOOK=0 git cm 'x'"));
        assert!(!is_bypass(r#"git cm "feat: ok""#));
    }

    #[test]
    fn core_hooks_path_override_is_blocked() {
        assert!(is_bypass(
            r#"git -c core.hooksPath=/dev/null commit -m "x""#
        ));
        assert!(is_bypass(
            "git -c core.hooksPath=/tmp/empty commit -m msg"
        ));
    }

    #[test]
    fn config_env_and_git_config_env_overrides_are_blocked() {
        assert!(is_bypass(
            "git --config-env core.hooksPath=HP commit -m x"
        ));
        assert!(is_bypass(
            "git --config-env=core.hooksPath:HP commit -m x"
        ));
        assert!(is_bypass(
            "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=/tmp/empty git commit -m x"
        ));
        assert!(is_bypass(
            r#"GIT_CONFIG_PARAMETERS="'core.hooksPath=/tmp/empty'" git commit -m x"#
        ));
    }

    #[test]
    fn redirect_stuck_and_abbrev_no_verify_are_blocked() {
        assert!(is_bypass("git commit -m x --no-verify>log"));
        assert!(is_bypass("git commit --no-veri -m x"));
        assert!(is_bypass("git commit --no-verif -m x"));
    }

    #[test]
    fn ambiguous_short_abbrev_is_not_treated_as_no_verify() {
        // git rejects these as ambiguous; we must not over-match `--no-ver`
        assert!(!is_bypass("git commit --no-ver -m x"));
        assert!(!is_bypass("git commit --no-v -m x"));
    }

    #[test]
    fn env_bypass_without_commit_is_not_blocked() {
        assert!(!is_bypass("HUSKY=0 npm test"));
        assert!(!is_bypass("LEFTHOOK=0 git status"));
        assert!(!is_bypass("SKIP=x git status"));
    }

    #[test]
    fn hooks_path_without_commit_is_not_blocked() {
        assert!(!is_bypass("git -c core.hooksPath=/tmp/empty status"));
        assert!(!is_bypass(
            "git -c core.hooksPath=/tmp/empty config --get core.hooksPath"
        ));
    }

    #[test]
    fn gitx_is_not_treated_as_git() {
        assert!(!is_bypass("gitx commit --no-verify -m x"));
    }

    #[test]
    fn bypass_reason_is_some_only_when_blocked() {
        assert!(bypass_reason(r#"HUSKY="0" git commit -m x"#).is_some());
        assert!(bypass_reason(r#"git commit -m "ok""#).is_none());
    }

    #[test]
    fn pipeline_and_chained_commit_still_blocked() {
        assert!(is_bypass("echo hi | git commit -m x --no-verify"));
        assert!(is_bypass("true && git commit -n -m x"));
    }
}
