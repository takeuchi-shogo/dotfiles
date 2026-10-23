//! 公開エントリ `claude-hooks pre-bash` を実バイナリで起動し、git commit の hook 迂回が
//! block されること・通常の commit が通ることを確かめる（settings.json の PreToolUse と同じ入力形式）。

use std::io::Write;
use std::process::{Command, Stdio};
use std::time::{Duration, Instant};

const BYPASS: &str = "BLOCKED [hook-bypass]";
const UNVERIFIABLE: &str = "BLOCKED [hook-bypass-unverifiable]";

/// `claude-hooks pre-bash` に Bash の PreToolUse 入力を渡し、(exit code, stderr) を返す。
fn pre_bash(command: &str) -> (Option<i32>, String) {
    // deny は監査ログを $HOME 配下に書くので、実 HOME を汚さないよう一時ディレクトリに向ける
    let home = std::env::temp_dir().join(format!("claude-hooks-it-{}", std::process::id()));
    let mut child = Command::new(env!("CARGO_BIN_EXE_claude-hooks"))
        .arg("pre-bash")
        .env("HOME", &home)
        .stdin(Stdio::piped())
        .stdout(Stdio::null())
        .stderr(Stdio::piped())
        .spawn()
        .expect("spawn claude-hooks");
    let input = serde_json::json!({ "tool_name": "Bash", "tool_input": { "command": command } });
    let mut stdin = child.stdin.take().expect("stdin");
    stdin
        .write_all(input.to_string().as_bytes())
        .expect("write stdin");
    drop(stdin);
    let output = child.wait_with_output().expect("wait claude-hooks");
    (
        output.status.code(),
        String::from_utf8_lossy(&output.stderr).into_owned(),
    )
}

/// すべての `commands` が exit `code` で終わり、stderr が `prefix` で始まることを確かめる。
fn expect_all(commands: &[&str], code: i32, prefix: &str) {
    let failures: Vec<String> = commands
        .iter()
        .filter_map(|command| {
            let (status, stderr) = pre_bash(command);
            let ok = status == Some(code) && stderr.starts_with(prefix);
            (!ok).then(|| format!("  {command:?}\n    -> exit {status:?}, stderr: {stderr:?}"))
        })
        .collect();
    assert!(
        failures.is_empty(),
        "expected exit {code} with {prefix:?}:\n{}",
        failures.join("\n")
    );
}

fn blocked(commands: &[&str]) {
    expect_all(commands, 2, BYPASS);
}

fn blocked_fail_closed(commands: &[&str]) {
    expect_all(commands, 2, UNVERIFIABLE);
}

fn allowed(commands: &[&str]) {
    expect_all(commands, 0, "");
}

#[test]
fn allows_ordinary_commits() {
    allowed(&[
        r#"git commit -m "msg""#,
        r#"git commit -m 'fix: typo' src/main.rs"#,
        r#"git -C dir commit -m "msg""#,
        r#"git -C "$HOME/dotfiles" commit -m "msg""#,
        r#"git commit -am "msg""#,
        "git commit -u",
        r#"git commit -u -m "msg""#,
        r#"git commit -uno -m "msg""#,
        "git commit --untracked-files=no -m msg",
        "git commit -F notes.txt",
        "git commit --amend --no-edit",
        r#"git add src/a.rs && git commit -m "msg" && git push"#,
        "git commit -m msg\ngit log -n 3",
        "git commit -m \"$(cat <<'EOF'\n✨ feat: 追加\n\nBody with don't, (parens) and `code`.\nEOF\n)\"",
        r#"git commit -m "$(cat msg.txt)""#,
        r#"git cm "msg""#,
        "nice -n 5 git commit -m msg",
        "LEFTHOOK=1 git commit -m msg",
    ]);
}

#[test]
fn allows_messages_and_searches_that_only_mention_bypass_words() {
    allowed(&[
        r#"git commit -m "docs: --no-verify と HUSKY=0 を禁止""#,
        r#"git cm -n"#,
        r#"rg -n "core.hooksPath|LEFTHOOK_EXCLUDE" .config lefthook.yml"#,
        "git log -n 5 --grep=no-verify",
        "git add lefthook.yml && git commit -m \"$(cat <<'EOF'\nchore: document lefthook and --no-verify\nEOF\n)\"",
        "gh pr create --body \"$(cat <<EOF\nlefthook の設定を更新\nEOF\n)\"",
        r#"git commit -m $'a\nHUSKY=0'"#,
        "env -S 'git commit -m x'",
    ]);
}

#[test]
fn blocks_no_verify_and_n_in_any_position() {
    blocked(&[
        "git commit --no-verify -m x",
        "git commit -m x --no-verify",
        r#"git commit -m "a; b" --no-verify"#,
        "git commit -n -m x",
        "git commit -m x -n",
        "git commit -anm x",
        r#"git commit -m x "--no-verify""#,
        "git commit -m x '-n'",
        "git commit -m x --no-veri",
        "git commit -m x --no-verify>log",
        "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\n)\" --no-verify",
    ]);
}

#[test]
fn blocks_hook_disabling_env() {
    blocked(&[
        "HUSKY=0 git commit -m x",
        r#"HUSKY="0" git commit -m x"#,
        "LEFTHOOK=0 git commit -m x",
        "LEFTHOOK=false git commit -m x",
        "LEFTHOOK_EXCLUDE=lint git commit -m x",
        "LEFTHOOK_CONFIG=/tmp/empty.yml git commit -m x",
        "SKIP=lint git commit -m x",
        "LEFTHOOK=0; git commit -m x",
        "export LEFTHOOK=0; git commit -m x",
        "export HUSKY=0 && git commit -m x",
    ]);
}

#[test]
fn blocks_hooks_path_overrides_including_with_dash_c_dir() {
    blocked(&[
        "git -c core.hooksPath=/dev/null commit -m x",
        r#"git -c "core.hooksPath=/dev/null" commit -m x"#,
        "git -C dir -c core.hooksPath=/dev/null commit -m x",
        "git -c core.hooksPath=/dev/null -C dir commit -m x",
        "git -c Core.HooksPath commit -m x",
        "git --config-env core.hooksPath=HP commit -m x",
        "git --config-env=core.hooksPath=HP commit -m x",
        "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=/dev/null git commit -m x",
        r#"GIT_CONFIG_PARAMETERS="'core.hooksPath=/dev/null'" git commit -m x"#,
    ]);
}

#[test]
fn blocks_aliases_resolved_at_subcommand_position() {
    blocked(&[
        r#"git cm "x" --no-verify"#,
        "git cane --no-verify",
        "git cane -n",
        r#"git -C dir cm "x" -n"#,
        r#"git -c user.name=a cane --no-verify"#,
        "HUSKY=0 git cm x",
        "git -c alias.ci='commit --no-verify' ci -m x",
        "git -c alias.ci='!git commit -n' ci -m x",
    ]);
}

#[test]
fn blocks_bypass_after_newlines_and_operators() {
    blocked(&[
        "git status\ngit commit -m x --no-verify",
        "git add a\n\nHUSKY=0 git commit -m x",
        "export HUSKY=0\ngit commit -m x",
        "git add a; git commit -n -m x",
        "git add a && git commit -m x -n",
        "false || git commit -n -m x",
        "echo msg | git commit -F - --no-verify",
        "git add a & git commit -n -m x",
    ]);
}

#[test]
fn blocks_bypass_inside_wrappers_subshells_and_blocks() {
    blocked(&[
        "env HUSKY=0 git commit -m x",
        "env -i LEFTHOOK=0 git commit -m x",
        "bash -c 'git commit -m x --no-verify'",
        r#"sh -c "git commit -n -m x""#,
        "bash -lc 'LEFTHOOK=0 git commit -m x'",
        r#"bash -c "sh -c 'eval git commit --no-verify -m x'""#,
        r#"eval "git commit -m x --no-verify""#,
        "eval git commit -n -m x",
        "git ls-files -m | xargs git commit -m x",
        "xargs -n1 git commit --no-verify -m x",
        "timeout 30 git commit -n -m x",
        "(git commit -n -m x)",
        "(cd sub && git commit -n -m x)",
        "{ git commit -n -m x; }",
        "sudo HUSKY=0 git commit -m x",
        r#"echo "$(git commit -n -m x)""#,
        "if git commit -n -m x; then echo ok; fi",
        "cat <<EOF | sh\ngit commit -n -m x\nEOF",
        "echo 'git commit -n -m x' | bash",
        "env -S 'HUSKY=0 git commit -m x'",
        "env --split-string 'LEFTHOOK=0 git commit -m x'",
        "env --split-string='HUSKY=0 git commit -m x'",
        "env -S 'git commit -m x -n'",
        r#"bash -c $'git commit -m x -n'"#,
        r#"eval $'git commit -n'"#,
    ]);
}

#[test]
fn blocks_git_that_is_not_the_first_word() {
    blocked(&[
        "/usr/bin/git commit -n -m x",
        "command git commit -n -m x",
        "nohup git commit --no-verify -m x",
        r#""git" commit -n -m x"#,
        r"\git commit -n -m x",
        "G=git; $G commit -n -m x",
    ]);
}

#[test]
fn optional_untracked_value_does_not_hide_following_flag() {
    blocked(&[
        "git commit -u -n -m x",
        "git commit -u --no-verify",
        "git commit --untracked-files --no-verify -m x",
    ]);
}

#[test]
fn blocks_dynamic_words_in_commit_option_position() {
    blocked(&[
        "git commit $FLAGS -m x",
        r#"git commit -m x "$EXTRA""#,
        "git commit -m x $(printf -- -n)",
        "git commit $'--no-verify' -m x",
        "git $(echo commit) -n -m x",
    ]);
}

#[test]
fn fails_closed_when_unparsed_commit_has_bypass_token() {
    let deep = format!("{}x{} git commit -m x -n", "$(".repeat(10), ")".repeat(10));
    let long = format!("{} git commit -m x -n", "a".repeat(100_001));
    blocked_fail_closed(&[
        "git commit -m 'unterminated --no-verify",
        r#"git commit -m x -n ${v//(/}"#,
        &deep,
        &long,
    ]);
}

#[test]
fn work_is_bounded_for_huge_counts_and_deep_nesting() {
    let deep = |tail: &str| format!("{}x{}{tail}", "$(".repeat(5_000), ")".repeat(5_000));
    let long = format!("{} git commit -m x -n", "a".repeat(100_001));
    let started = Instant::now();
    blocked(&["GIT_CONFIG_COUNT=99999999999999999999 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=/dev/null git commit -m x"]);
    allowed(&[
        "GIT_CONFIG_COUNT=99999999999999999999 git commit -m x",
        &deep(""),
        &format!("{} git commit -m x", "a".repeat(100_001)),
    ]);
    blocked_fail_closed(&[&deep(" git commit -m x -n"), &long]);
    assert!(
        started.elapsed() < Duration::from_secs(10),
        "took {:?}",
        started.elapsed()
    );
}
