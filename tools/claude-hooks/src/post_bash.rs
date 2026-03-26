//! PostToolUse/Bash — consolidates 5 hooks:
//! output-offload, error-to-codex, post-test-analysis, plan-lifecycle, review-feedback-tracker

use regex::Regex;

// ── output-offload ──────────────────────────────────────────────────

const LINE_THRESHOLD: usize = 150;
const CHAR_THRESHOLD: usize = 6000;

const LARGE_OUTPUT_CMDS: &[&str] = &[
    "cat ", "less ", "more ", "find ", "tree ", "git log", "git diff", "git show",
];

fn check_output_offload(command: &str, output: &str) -> Option<String> {
    let lines: Vec<&str> = output.split('\n').collect();
    let line_count = lines.len();
    let char_count = output.len();

    if line_count < LINE_THRESHOLD && char_count < CHAR_THRESHOLD {
        return None;
    }

    // Save to temp file
    let offload_dir = std::env::var("TMPDIR")
        .unwrap_or_else(|_| "/tmp".to_string());
    let offload_dir = format!("{}/claude-tool-outputs", offload_dir);
    let _ = std::fs::create_dir_all(&offload_dir);

    let ts = crate::io::now_secs() as u64;
    let cmd_hash = &format!("{:x}", md5_simple(command.as_bytes()))[..8];
    let filepath = format!("{}/{}_{}.log", offload_dir, ts, cmd_hash);
    let _ = std::fs::write(&filepath, format!("$ {}\n\n{}", command, output));

    let mut parts = vec![
        format!(
            "[Output Offload] 大きな出力を検出 ({}行, {}文字)",
            line_count, char_count
        ),
        format!("全文保存先: {}", filepath),
        "compaction 後に Read ツールで参照可能です。".to_string(),
    ];

    let cmd_lower = command.trim().to_lowercase();
    if !LARGE_OUTPUT_CMDS.iter().any(|c| cmd_lower.starts_with(c)) {
        parts.push(
            "推奨: 次回は grep, head -n, tail -n, | wc -l 等で出力を絞ってください。".to_string(),
        );
    }

    Some(parts.join("\n"))
}

fn md5_simple(data: &[u8]) -> u64 {
    // Simple hash for filename uniqueness (not cryptographic)
    let mut h: u64 = 0xcbf29ce484222325;
    for &b in data {
        h ^= b as u64;
        h = h.wrapping_mul(0x100000001b3);
    }
    h
}

// ── error-to-codex ──────────────────────────────────────────────────

const IGNORE_COMMANDS: &[&str] = &[
    "git status", "git log", "git diff", "git branch",
    "ls", "cat", "head", "tail", "pwd", "which", "echo",
    "codex", "gemini",
];

fn error_patterns() -> Vec<Regex> {
    vec![
        Regex::new(r"Traceback \(most recent call last\)").unwrap(),
        Regex::new(r"(?:Error|Exception):\s+\S").unwrap(),
        Regex::new(r"panic:\s").unwrap(),
        Regex::new(r"FAIL\s+\S").unwrap(),
        Regex::new(r"npm ERR!").unwrap(),
        Regex::new(r"error\[E\d+\]").unwrap(),
        Regex::new(r"(?i)cannot find module").unwrap(),
        Regex::new(r"undefined reference").unwrap(),
        Regex::new(r"(?i)segmentation fault").unwrap(),
        Regex::new(r"fatal error").unwrap(),
        Regex::new(r"compilation failed").unwrap(),
        Regex::new(r"(?i)build failed").unwrap(),
        Regex::new(r"SyntaxError:").unwrap(),
        Regex::new(r"TypeError:").unwrap(),
        Regex::new(r"ReferenceError:").unwrap(),
    ]
}

fn load_fix_guides() -> Vec<(String, String, String)> {
    let path = crate::io::references_dir().join("error-fix-guides.md");
    let content = match std::fs::read_to_string(&path) {
        Ok(c) => c,
        Err(_) => return Vec::new(),
    };

    let mut guides = Vec::new();
    let mut key = String::new();
    let mut cause = String::new();
    let mut fix = String::new();

    for line in content.lines() {
        let trimmed = line.trim();
        if let Some(rest) = trimmed.strip_prefix("### ") {
            if !key.is_empty() && (!cause.is_empty() || !fix.is_empty()) {
                guides.push((key.clone(), cause.clone(), fix.clone()));
            }
            key = rest.trim().to_lowercase();
            cause.clear();
            fix.clear();
        } else if let Some(rest) = trimmed.strip_prefix("- **原因**:") {
            cause = rest.trim().to_string();
        } else if let Some(rest) = trimmed.strip_prefix("- **修正**:") {
            fix = rest.trim().to_string();
        }
    }
    if !key.is_empty() && (!cause.is_empty() || !fix.is_empty()) {
        guides.push((key, cause, fix));
    }
    guides
}

// ── error 6-category classification ─────────────────────────────────

fn classify_error(output: &str) -> &'static str {
    let lower = output.to_lowercase();
    if lower.contains("permission denied") || lower.contains("eacces") || lower.contains("operation not permitted") {
        "PermissionDenied"
    } else if (lower.contains("no such file") || lower.contains("enoent")) && !lower.contains("module") {
        "FileNotFound"
    } else if lower.contains("file has changed") || lower.contains("content mismatch") || lower.contains("stale") {
        "EditMismatch"
    } else if lower.contains("syntaxerror") || lower.contains("parse error") || lower.contains("unexpected token") {
        "SyntaxError"
    } else if lower.contains("rate limit") || lower.contains("429") || lower.contains("too many requests") {
        "RateLimit"
    } else if lower.contains("timeout") || lower.contains("etimedout") || lower.contains("timed out") {
        "Timeout"
    } else {
        ""
    }
}

fn recovery_template(category: &str) -> &'static str {
    match category {
        "PermissionDenied" =>
            "リカバリ: ファイルの権限を確認してください。sudo は使わず、適切なパスに書き込むか chmod で最小限の権限を設定してください。",
        "FileNotFound" =>
            "リカバリ: ファイルパスを確認してください。Glob ツールで正しいパスを検索してから再試行してください。",
        "EditMismatch" =>
            "リカバリ: ファイルが変更されています。Read ツールで最新の内容を取得してから、再度 Edit してください。",
        "SyntaxError" =>
            "リカバリ: エラーの行番号を Read ツールで確認し、構文エラーを修正してください。",
        "RateLimit" =>
            "リカバリ: レート制限に達しました。別のタスクに切り替えるか、しばらく待ってから再試行してください。",
        "Timeout" =>
            "リカバリ: コマンドがタイムアウトしました。処理を分割するか、run_in_background で実行してください。",
        _ => "",
    }
}

fn check_error_to_codex(command: &str, output: &str) -> Option<String> {
    let cmd_lower = command.trim().to_lowercase();
    if IGNORE_COMMANDS.iter().any(|ic| cmd_lower.starts_with(ic)) {
        return None;
    }
    if output.len() < 20 {
        return None;
    }
    if output.to_lowercase().contains("already exists") {
        return None;
    }

    let patterns = error_patterns();
    let error_match = patterns.iter().find_map(|p| {
        p.find(output).map(|m| m.as_str().to_string())
    })?;

    // Emit event
    crate::events::emit_event(
        "error",
        &serde_json::json!({
            "message": &error_match,
            "command": &command[..command.len().min(200)],
        }),
    );

    let mut parts = vec![format!(
        "[Error-to-Codex] エラーが検出されました: {}",
        error_match
    )];

    // Try fix guides
    let guides = load_fix_guides();
    let output_lower = output.to_lowercase();
    for (key, cause, fix) in &guides {
        if output_lower.contains(key) {
            if !cause.is_empty() {
                parts.push(format!("推定原因: {}", cause));
            }
            if !fix.is_empty() {
                parts.push(format!("推奨修正: {}", fix));
            }
            break;
        }
    }

    // 6-category recovery template
    let category = classify_error(output);
    let recovery = recovery_template(category);
    if !recovery.is_empty() {
        parts.push(recovery.to_string());
    }

    parts.push("codex-debugger エージェントを使用してこのエラーの根本原因を分析できます。".to_string());
    parts.push(format!("コマンド: {}", &command[..command.len().min(100)]));

    Some(parts.join("\n"))
}

// ── post-test-analysis ──────────────────────────────────────────────

fn test_command_patterns() -> Vec<Regex> {
    vec![
        Regex::new(r"(?:go\s+test|pytest|npm\s+test|npx\s+jest|npx\s+vitest|bun\s+test|cargo\s+test|pnpm\s+test)").unwrap(),
        Regex::new(r"(?:npm|pnpm|bun|yarn)\s+run\s+test").unwrap(),
    ]
}

fn failure_patterns() -> Vec<Regex> {
    vec![
        Regex::new(r"(?i)FAIL").unwrap(),
        Regex::new(r"FAILED").unwrap(),
        Regex::new(r"(?i)failures?:\s*[1-9]").unwrap(),
        Regex::new(r"(?i)errors?:\s*[1-9]").unwrap(),
        Regex::new(r"Assert(?:ion)?Error").unwrap(),
        Regex::new(r"(?i)assert.*failed").unwrap(),
        Regex::new(r"(?i)expected.*but\s+(?:got|received)").unwrap(),
        Regex::new(r"panic:\s").unwrap(),
        Regex::new(r"--- FAIL:").unwrap(),
        Regex::new(r"FAILURES!").unwrap(),
    ]
}

fn check_post_test(command: &str, output: &str) -> Option<String> {
    let tc = test_command_patterns();
    if !tc.iter().any(|p| p.is_match(command)) {
        return None;
    }

    let fp = failure_patterns();
    if !fp.iter().any(|p| p.is_match(output)) {
        return None;
    }

    // Count failures
    let count = Regex::new(r"(?i)(\d+)\s+(?:failed|failures?|errors?)")
        .ok()
        .and_then(|re| re.captures(output))
        .and_then(|c| c.get(1))
        .and_then(|m| m.as_str().parse::<usize>().ok())
        .unwrap_or_else(|| {
            Regex::new(r"(?:FAIL|--- FAIL:)")
                .map(|re| re.find_iter(output).count())
                .unwrap_or(0)
        });

    let count_str = if count > 0 {
        format!("{}件の", count)
    } else {
        String::new()
    };

    Some(format!(
        "[Post-Test] {}テスト失敗が検出されました。\n\
         codex-debugger エージェントで根本原因を分析できます。\n\
         または debugger エージェントで体系的にデバッグすることも可能です。",
        count_str
    ))
}

// ── plan-lifecycle ──────────────────────────────────────────────────

fn check_plan_lifecycle(command: &str, output: &str) -> Option<String> {
    if !command.contains("git commit") {
        return None;
    }

    let output_lower = output.to_lowercase();
    if !output_lower.contains("file changed")
        && !output_lower.contains("files changed")
        && !output_lower.contains("insertion")
        && !output_lower.contains("create mode")
    {
        return None;
    }

    let repo_root = std::process::Command::new("git")
        .args(["--no-optional-locks", "rev-parse", "--show-toplevel"])
        .output()
        .ok()
        .filter(|o| o.status.success())
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())?;

    let active_dir = format!("{}/docs/plans/active", repo_root);
    let plans: Vec<String> = std::fs::read_dir(&active_dir)
        .ok()?
        .filter_map(|e| e.ok())
        .map(|e| e.file_name().to_string_lossy().to_string())
        .filter(|f| f.ends_with(".md") && !f.starts_with('.'))
        .collect();

    if plans.is_empty() {
        return None;
    }

    let commit_msg = std::process::Command::new("git")
        .args(["--no-optional-locks", "log", "-1", "--pretty=%B"])
        .current_dir(&repo_root)
        .output()
        .ok()
        .filter(|o| o.status.success())
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
        .unwrap_or_default();

    if commit_msg.is_empty() {
        return None;
    }

    let msg_lower = commit_msg.to_lowercase();
    let referenced: Vec<&String> = plans
        .iter()
        .filter(|plan| {
            let parts: Vec<&str> = plan.trim_end_matches(".md").splitn(4, '-').collect();
            let binding = plan.as_str();
            let topic = parts.get(3).unwrap_or(&binding);
            msg_lower.contains(&topic.to_lowercase())
        })
        .collect();

    if referenced.is_empty() {
        return None;
    }

    let plan_list: Vec<String> = referenced.iter().map(|p| format!("`{}`", p)).collect();
    Some(format!(
        "[plan-lifecycle] アクティブ計画 {} に関連するコミットを検出。\n\
         計画が完了した場合は `docs/plans/active/` → `docs/plans/completed/` に移動してください。",
        plan_list.join(", ")
    ))
}

// ── review-feedback-tracker ─────────────────────────────────────────

fn check_review_feedback(command: &str, _output: &str) -> Option<String> {
    if !Regex::new(r"\bgit\s+commit\b").ok()?.is_match(command) {
        return None;
    }

    // Check for pending findings
    let data_dir = std::env::var("AUTOEVOLVE_DATA_DIR")
        .map(std::path::PathBuf::from)
        .unwrap_or_else(|_| {
            std::path::PathBuf::from(crate::io::home_dir())
                .join(".claude")
                .join("agent-memory")
        });

    let findings_path = data_dir.join("learnings/review-findings.jsonl");
    let feedback_path = data_dir.join("learnings/review-feedback.jsonl");

    if !findings_path.exists() {
        return None;
    }

    // Read resolved IDs
    let resolved: std::collections::HashSet<String> = if feedback_path.exists() {
        std::fs::read_to_string(&feedback_path)
            .unwrap_or_default()
            .lines()
            .filter_map(|l| serde_json::from_str::<serde_json::Value>(l).ok())
            .filter_map(|v| v["finding_id"].as_str().map(|s| s.to_string()))
            .collect()
    } else {
        std::collections::HashSet::new()
    };

    // Read pending findings
    let pending: Vec<serde_json::Value> = std::fs::read_to_string(&findings_path)
        .unwrap_or_default()
        .lines()
        .filter_map(|l| serde_json::from_str(l).ok())
        .filter(|v: &serde_json::Value| {
            v["id"]
                .as_str()
                .map(|id| !resolved.contains(id))
                .unwrap_or(false)
        })
        .collect();

    if pending.is_empty() {
        return None;
    }

    // Get committed diff
    let diff = std::process::Command::new("git")
        .args(["--no-optional-locks", "diff", "HEAD~1..HEAD", "--unified=0"])
        .output()
        .ok()
        .filter(|o| o.status.success())
        .map(|o| String::from_utf8_lossy(&o.stdout).to_string())
        .unwrap_or_default();

    if diff.is_empty() {
        return None;
    }

    // Parse diff changed lines
    let mut changed: std::collections::HashMap<String, std::collections::HashSet<i64>> =
        std::collections::HashMap::new();
    let mut current_file = String::new();
    let hunk_re = Regex::new(r"\+(\d+)(?:,(\d+))?").unwrap();

    for line in diff.lines() {
        if let Some(rest) = line.strip_prefix("+++ b/") {
            current_file = rest.to_string();
        } else if line.starts_with("@@ ") && !current_file.is_empty() {
            if let Some(caps) = hunk_re.captures(line) {
                let start: i64 = caps[1].parse().unwrap_or(0);
                let count: i64 = caps.get(2).map(|m| m.as_str().parse().unwrap_or(1)).unwrap_or(1);
                let set = changed.entry(current_file.clone()).or_default();
                for i in start..start + count {
                    set.insert(i);
                }
            }
        }
    }

    let mut accepted = 0usize;
    let mut ignored = 0usize;
    let ts = crate::io::iso_now();

    for finding in &pending {
        let id = finding["id"].as_str().unwrap_or("");
        if id.is_empty() {
            continue;
        }
        let file = finding["file"].as_str().unwrap_or("");
        let line = finding["line"].as_i64().unwrap_or(0);

        let outcome = if changed.iter().any(|(diff_file, lines)| {
            (diff_file.ends_with(file) || file.ends_with(diff_file.as_str()))
                && (line == 0 || lines.iter().any(|&cl| (cl - line).abs() <= 5))
        }) {
            "accepted"
        } else {
            "ignored"
        };

        // Record feedback
        let entry = serde_json::json!({
            "timestamp": ts,
            "finding_id": id,
            "outcome": outcome,
            "reason": "",
        });
        if let Ok(mut f) = std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(&feedback_path)
        {
            use std::io::Write;
            let _ = writeln!(f, "{}", entry);
        }

        if outcome == "accepted" {
            accepted += 1;
        } else {
            ignored += 1;
        }
    }

    if accepted + ignored > 0 {
        Some(format!(
            "[Review Feedback] {} 件のレビュー指摘を追跡: {} accepted, {} ignored",
            accepted + ignored,
            accepted,
            ignored
        ))
    } else {
        None
    }
}

// ── stagnation detector (merged from stagnation-detector.py) ────────

const STAG_WINDOW: usize = 20;
const STAG_CONSEC_THRESHOLD: usize = 5;
const STAG_SAME_ERROR_THRESHOLD: usize = 3;
const STAG_COOLDOWN_SECS: f64 = 30.0;
const STAG_TTL: f64 = 2.0 * 3600.0;

fn has_error(output: &str) -> bool {
    let patterns = error_patterns();
    patterns.iter().any(|p| p.is_match(output))
}

fn check_stagnation(command: &str, output: &str) -> Option<String> {
    let cmd_lower = command.trim().to_lowercase();
    if IGNORE_COMMANDS.iter().any(|ic| cmd_lower.starts_with(ic)) || output.len() < 10 {
        return None;
    }

    let now = crate::io::now_secs();
    let state_path = crate::io::state_dir().join("stagnation-state.json");
    let mut state = crate::io::read_json_state(&state_path);

    // TTL reset
    let created = state["created_at"].as_f64().unwrap_or(0.0);
    if now - created > STAG_TTL || created == 0.0 {
        state = serde_json::json!({
            "created_at": now,
            "bash_history": [],
            "consecutive_failures": 0,
            "last_suggestion_time": 0.0
        });
    }

    let is_error = has_error(output);

    // Update history
    let mut history: Vec<serde_json::Value> = state["bash_history"]
        .as_array().cloned().unwrap_or_default();
    history.push(serde_json::json!({
        "command": &command[..command.len().min(200)],
        "is_error": is_error,
        "ts": now,
    }));
    if history.len() > STAG_WINDOW {
        history = history[history.len() - STAG_WINDOW..].to_vec();
    }
    state["bash_history"] = serde_json::json!(history);

    // Consecutive failures
    let mut consec = state["consecutive_failures"].as_u64().unwrap_or(0) as usize;
    if is_error { consec += 1; } else { consec = 0; }
    state["consecutive_failures"] = serde_json::json!(consec);

    // Cooldown
    let last_suggest = state["last_suggestion_time"].as_f64().unwrap_or(0.0);
    if now - last_suggest < STAG_COOLDOWN_SECS {
        crate::io::write_json_state(&state_path, &state);
        return None;
    }

    // Pattern 1: same error type repeated
    let recent_errors: Vec<_> = history.iter().rev().take(6)
        .filter(|h| h["is_error"].as_bool().unwrap_or(false))
        .collect();
    if recent_errors.len() >= STAG_SAME_ERROR_THRESHOLD {
        state["last_suggestion_time"] = serde_json::json!(now);
        crate::events::emit_event("pattern", &serde_json::json!({
            "type": "stagnation_detected",
            "stagnation_type": "same_error_type",
            "consecutive_failures": consec,
        }));
        crate::io::write_json_state(&state_path, &state);
        return Some(
            "[Stagnation] 同種エラーが3回連続しています。別のアプローチを検討してください\
             （別ツール、問題の分解、codex-debugger での根本原因分析）。".to_string()
        );
    }

    // Pattern 2: consecutive failures
    if consec >= STAG_CONSEC_THRESHOLD {
        state["last_suggestion_time"] = serde_json::json!(now);
        crate::events::emit_event("pattern", &serde_json::json!({
            "type": "stagnation_detected",
            "stagnation_type": "consecutive_failures",
            "consecutive_failures": consec,
        }));
        crate::io::write_json_state(&state_path, &state);
        return Some(format!(
            "[Stagnation] 連続 {} 回失敗しています。\
             現在のアプローチに固執せず、問題を再定義してください。",
            consec
        ));
    }

    crate::io::write_json_state(&state_path, &state);
    None
}

// ── main entry ──────────────────────────────────────────────────────

pub fn run(raw: &str, data: &serde_json::Value) -> Result<(), String> {
    let command = data["tool_input"]["command"]
        .as_str()
        .unwrap_or("");
    let output = data["tool_output"].as_str().unwrap_or("");

    let mut contexts: Vec<String> = Vec::new();

    if let Some(ctx) = check_output_offload(command, output) {
        contexts.push(ctx);
    }
    if let Some(ctx) = check_error_to_codex(command, output) {
        contexts.push(ctx);
    }
    if let Some(ctx) = check_post_test(command, output) {
        // Skip if error-to-codex already caught this
        if contexts.is_empty() || !contexts.last().map(|c| c.contains("Error-to-Codex")).unwrap_or(false) {
            contexts.push(ctx);
        }
    }
    if let Some(ctx) = check_plan_lifecycle(command, output) {
        contexts.push(ctx);
    }
    if let Some(ctx) = check_review_feedback(command, output) {
        contexts.push(ctx);
    }
    if let Some(ctx) = check_stagnation(command, output) {
        contexts.push(ctx);
    }

    if contexts.is_empty() {
        crate::io::passthrough(raw);
    } else {
        crate::io::context("PostToolUse", &contexts.join("\n\n"));
    }

    Ok(())
}
