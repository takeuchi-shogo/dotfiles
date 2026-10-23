//! 公開エントリ `claude-hooks pre-bash` で、よくある git commit の hook 迂回だけを止める。

use std::io::Write;
use std::process::{Command, Stdio};

const BYPASS: &str = "BLOCKED [hook-bypass]";

fn pre_bash(command: &str) -> (Option<i32>, String) {
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

fn allowed(commands: &[&str]) {
    expect_all(commands, 0, "");
}

#[test]
fn allows_ordinary_commits_and_messages() {
    allowed(&[
        r#"git commit -m "msg""#,
        r#"git commit -am "msg""#,
        r#"git -C dir commit -m "msg""#,
        "git commit -u",
        r#"git commit -uno -m "msg""#,
        "git commit --amend --no-edit",
        r#"git add src/a.rs && git commit -m "msg""#,
        r#"git commit -m "docs: --no-verify と HUSKY=0 を禁止""#,
        r#"git commit -m "- add new feature""#,
        r#"git commit -m "- fix lint""#,
        r#"git commit -m "- refactor""#,
        r#"git commit -m"- n""#,
        r#"git commit --message="- n""#,
        r#"git commit -am "- new""#,
        "git commit -m \"$(cat <<'EOF'\nchore: lefthook と --no-verify の説明\nEOF\n)\"",
        "git add lefthook.yml && git commit -m \"$(cat <<'EOF'\nchore: document lefthook\nEOF\n)\"",
        "LEFTHOOK=1 git commit -m msg",
    ]);
}

#[test]
fn allows_non_commit_commands() {
    allowed(&[
        "git log -n 3",
        "git push --no-verify",
        "git status",
        r#"echo git commit -n"#,
        "gh pr create --body \"$(cat <<EOF\nlefthook と --no-verify\nEOF\n)\"",
        r#"rg -n "core.hooksPath|LEFTHOOK" .config"#,
        "git commit -m 'unterminated --no-verify",
        r#"bash -c 'git commit -m x --no-verify'"#,
        r#"eval git commit -n"#,
    ]);
}

#[test]
fn blocks_no_verify_and_n() {
    blocked(&[
        "git commit --no-verify -m x",
        "git commit -m x --no-verify",
        r#"git commit -m "a; b" --no-verify"#,
        "git commit -n -m x",
        "git commit -m x -n",
        "git commit -anm x",
        r#"git commit -nm"fix bug""#,
        r#"git commit -anm"wip 1""#,
        "git commit -nm修正",
        "git commit -nm x",
        "/usr/bin/git commit -n -m x",
    ]);
}

#[test]
fn blocks_hook_disabling_env() {
    blocked(&[
        "HUSKY=0 git commit -m x",
        "LEFTHOOK=0 git commit -m x",
        "LEFTHOOK=false git commit -m x",
        "env HUSKY=0 git commit -m x",
        "env -i LEFTHOOK=0 git commit -m x",
    ]);
}

#[test]
fn blocks_hooks_path_on_commit() {
    blocked(&[
        "git -c core.hooksPath=/dev/null commit -m x",
        r#"git -c "core.hooksPath=/dev/null" commit -m x"#,
        "git -C dir -c core.hooksPath=/dev/null commit -m x",
        "git -c Core.HooksPath=/dev/null commit -m x",
    ]);
}

#[test]
fn blocks_bypass_after_operators() {
    blocked(&[
        "git add a; git commit -n -m x",
        "git add a && git commit -m x -n",
        "false || git commit -n -m x",
        "echo msg | git commit -F - --no-verify",
        "git add a\ngit commit --no-verify -m x",
    ]);
}
