---
status: active
last_reviewed: 2026-04-23
---

# OpenDev Harness Improvements Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** OpenDev 論文の知見を元に、Doom-Loop 検出・探索スパイラル検出・コンテキスト圧力監視・Artifact Index・エラー6分類・リソースバウンディング定数一覧を実装する。

**Architecture:** `claude-hooks` Rust バイナリに新モジュール `post_any.rs` を追加し、全 PostToolUse で発火させる。既存の `post_bash.rs` にエラー6分類を拡張。statusline からコンテキスト圧力を状態ファイルに書き出す。

**Tech Stack:** Rust (serde_json, regex), Python (statusline), Markdown (reference doc)

**Design Doc:** `docs/plans/2026-03-16-opendev-harness-improvements-design.md`

---

## Task 1: `events.rs` に FM-011〜013 を追加

**Files:**
- Modify: `tools/claude-hooks/src/events.rs:11-59`

**Step 1: FM ルールを追加**

`importance_rules()` に以下3件を追加（既存ルールの直後）:

```rust
Rule {
    pattern: Regex::new(r"doom.loop|doom_loop").unwrap(),
    score: 0.7,
    failure_mode: "FM-011",
},
Rule {
    pattern: Regex::new(r"exploration.spiral|exploration_spiral").unwrap(),
    score: 0.5,
    failure_mode: "FM-012",
},
Rule {
    pattern: Regex::new(r"context.pressure|context_pressure").unwrap(),
    score: 0.8,
    failure_mode: "FM-013",
},
```

**Step 2: ビルド確認**

Run: `cd tools/claude-hooks && cargo build --release 2>&1 | tail -5`
Expected: `Finished` with no errors

**Step 3: コミット**

```bash
git add tools/claude-hooks/src/events.rs
git commit -m "✨ feat: add FM-011/012/013 failure modes for OpenDev patterns"
```

---

## Task 2: `io.rs` に Artifact Index 書き込みユーティリティを追加

**Files:**
- Modify: `tools/claude-hooks/src/io.rs`

**Step 1: `append_jsonl` 関数を追加**

`write_json_state` の直後に追加:

```rust
/// Append a single JSON line to a JSONL file, creating parent dirs if needed.
/// Enforces max_lines by rotating: drops oldest lines when exceeded.
pub fn append_jsonl(path: &std::path::Path, entry: &serde_json::Value, max_lines: usize) {
    if let Some(parent) = path.parent() {
        let _ = std::fs::create_dir_all(parent);
    }

    // Read existing lines count
    let existing = std::fs::read_to_string(path).unwrap_or_default();
    let line_count = existing.lines().count();

    if line_count >= max_lines {
        // Keep last (max_lines - max_lines/5) lines to avoid rotating every call
        let keep = max_lines - max_lines / 5;
        let lines: Vec<&str> = existing.lines().collect();
        let trimmed = lines[lines.len().saturating_sub(keep)..].join("\n");
        let _ = std::fs::write(path, format!("{}\n{}\n", trimmed, entry));
    } else {
        if let Ok(mut f) = std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(path)
        {
            use std::io::Write;
            let _ = writeln!(f, "{}", entry);
        }
    }
}
```

**Step 2: ビルド確認**

Run: `cd tools/claude-hooks && cargo build --release 2>&1 | tail -5`
Expected: `Finished` with no errors

**Step 3: コミット**

```bash
git add tools/claude-hooks/src/io.rs
git commit -m "✨ feat: add append_jsonl utility with max-lines rotation"
```

---

## Task 3: `post_any.rs` を作成 — Doom-Loop Detection

**Files:**
- Create: `tools/claude-hooks/src/post_any.rs`

**Step 1: モジュールのスケルトン + Doom-Loop 検出を実装**

```rust
//! PostToolUse(*) — universal observer for all tool calls.
//! doom-loop detection, exploration spiral, context pressure, artifact index.

use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

// ── constants ───────────────────────────────────────────────────────

const DOOM_LOOP_WINDOW: usize = 20;
const DOOM_LOOP_THRESHOLD: usize = 3;
const DOOM_LOOP_COOLDOWN: f64 = 300.0; // seconds

// ── doom-loop detection ─────────────────────────────────────────────

fn fingerprint_hash(tool_name: &str, data: &serde_json::Value) -> u64 {
    let mut hasher = DefaultHasher::new();
    tool_name.hash(&mut hasher);

    let key_str = match tool_name {
        "Bash" => {
            let cmd = data["tool_input"]["command"].as_str().unwrap_or("");
            cmd.chars().take(50).collect::<String>()
        }
        "Edit" => {
            let fp = data["tool_input"]["file_path"].as_str().unwrap_or("");
            let old = data["tool_input"]["old_string"].as_str().unwrap_or("");
            format!("{}:{}", fp, &old[..old.len().min(100)])
        }
        "Read" => {
            data["tool_input"]["file_path"].as_str().unwrap_or("").to_string()
        }
        "Grep" => {
            let pat = data["tool_input"]["pattern"].as_str().unwrap_or("");
            let path = data["tool_input"]["path"].as_str().unwrap_or("");
            format!("{}:{}", pat, path)
        }
        "Glob" => {
            data["tool_input"]["pattern"].as_str().unwrap_or("").to_string()
        }
        "Write" => {
            data["tool_input"]["file_path"].as_str().unwrap_or("").to_string()
        }
        _ => {
            let input = data["tool_input"].to_string();
            input.chars().take(200).collect::<String>()
        }
    };

    key_str.hash(&mut hasher);
    hasher.finish()
}

fn check_doom_loop(tool_name: &str, data: &serde_json::Value) -> Option<String> {
    let state_path = crate::io::state_dir().join("doom-loop.json");
    let mut state = crate::io::read_json_state(&state_path);
    let now = crate::io::now_secs();

    // TTL: reset after 2 hours
    let last_reset = state["lastReset"].as_f64().unwrap_or(now);
    if now - last_reset > 2.0 * 3600.0 {
        state = serde_json::json!({"lastReset": now, "fingerprints": [], "lastWarned": 0.0});
    }

    let fp = fingerprint_hash(tool_name, data);

    let mut fingerprints: Vec<serde_json::Value> = state["fingerprints"]
        .as_array()
        .cloned()
        .unwrap_or_default();

    fingerprints.push(serde_json::json!({"hash": fp, "tool": tool_name, "ts": now}));

    // Keep only last DOOM_LOOP_WINDOW entries
    if fingerprints.len() > DOOM_LOOP_WINDOW {
        fingerprints = fingerprints[fingerprints.len() - DOOM_LOOP_WINDOW..].to_vec();
    }

    // Count occurrences of current fingerprint
    let count = fingerprints
        .iter()
        .filter(|e| e["hash"].as_u64() == Some(fp))
        .count();

    state["fingerprints"] = serde_json::json!(fingerprints);

    // Check cooldown
    let last_warned = state["lastWarned"].as_f64().unwrap_or(0.0);
    let should_warn = count >= DOOM_LOOP_THRESHOLD && (now - last_warned > DOOM_LOOP_COOLDOWN);

    if should_warn {
        state["lastWarned"] = serde_json::json!(now);
    }

    crate::io::write_json_state(&state_path, &state);

    if should_warn {
        let cmd_hint = match tool_name {
            "Bash" => {
                let cmd = data["tool_input"]["command"].as_str().unwrap_or("");
                format!("`Bash: {}`", &cmd[..cmd.len().min(60)])
            }
            _ => format!("`{}`", tool_name),
        };

        crate::events::emit_event(
            "pattern",
            &serde_json::json!({
                "type": "doom_loop",
                "tool": tool_name,
                "count": count,
                "window": DOOM_LOOP_WINDOW,
            }),
        );

        Some(format!(
            "[Doom-Loop] {} が{}回繰り返されています（直近{}回のツール呼び出し内）。\n\
             同じアプローチを繰り返しても解決しません。根本原因を分析し、別の方法を試してください。",
            cmd_hint, count, DOOM_LOOP_WINDOW
        ))
    } else {
        None
    }
}

// ── main entry (partial — exploration/pressure/artifact added in later tasks) ──

pub fn run(raw: &str, data: &serde_json::Value) -> Result<(), String> {
    let tool_name = data["tool_name"].as_str().unwrap_or("");

    let mut contexts: Vec<String> = Vec::new();

    if let Some(ctx) = check_doom_loop(tool_name, data) {
        contexts.push(ctx);
    }

    if contexts.is_empty() {
        crate::io::passthrough(raw);
    } else {
        crate::io::context("PostToolUse", &contexts.join("\n\n"));
    }

    Ok(())
}
```

**Step 2: `main.rs` にディスパッチ追加**

`mod post_any;` を追加し、match に `"post-any" => post_any::run(&raw, &data),` を追加。

**Step 3: ビルド確認**

Run: `cd tools/claude-hooks && cargo build --release 2>&1 | tail -5`
Expected: `Finished` with no errors

**Step 4: コミット**

```bash
git add tools/claude-hooks/src/post_any.rs tools/claude-hooks/src/main.rs
git commit -m "✨ feat: add post-any module with doom-loop detection"
```

---

## Task 4: Exploration Spiral Detection を `post_any.rs` に追加

**Files:**
- Modify: `tools/claude-hooks/src/post_any.rs`

**Step 1: 定数とツール分類を追加**

```rust
const EXPLORATION_THRESHOLD: usize = 5;

const READ_TOOLS: &[&str] = &["Read", "Grep", "Glob", "WebFetch", "WebSearch"];
const ACTION_TOOLS: &[&str] = &["Edit", "Write", "Bash", "Agent", "Skill"];

fn is_read_tool(tool_name: &str) -> bool {
    READ_TOOLS.contains(&tool_name)
}

fn is_action_tool(tool_name: &str) -> bool {
    ACTION_TOOLS.contains(&tool_name)
}
```

**Step 2: 検出関数を追加**

```rust
fn check_exploration_spiral(tool_name: &str) -> Option<String> {
    let state_path = crate::io::state_dir().join("exploration-tracker.json");
    let mut state = crate::io::read_json_state(&state_path);
    let now = crate::io::now_secs();

    // TTL: reset after 2 hours
    let last_reset = state["lastReset"].as_f64().unwrap_or(now);
    if now - last_reset > 2.0 * 3600.0 {
        state = serde_json::json!({
            "lastReset": now,
            "consecutive_reads": 0,
            "warned": false,
        });
    }

    if is_action_tool(tool_name) {
        // Reset on action
        state["consecutive_reads"] = serde_json::json!(0);
        state["warned"] = serde_json::json!(false);
        crate::io::write_json_state(&state_path, &state);
        return None;
    }

    if is_read_tool(tool_name) {
        let count = state["consecutive_reads"].as_u64().unwrap_or(0) + 1;
        state["consecutive_reads"] = serde_json::json!(count);

        let already_warned = state["warned"].as_bool().unwrap_or(false);

        if count >= EXPLORATION_THRESHOLD as u64 && !already_warned {
            state["warned"] = serde_json::json!(true);
            crate::io::write_json_state(&state_path, &state);

            crate::events::emit_event(
                "pattern",
                &serde_json::json!({
                    "type": "exploration_spiral",
                    "consecutive_reads": count,
                }),
            );

            return Some(format!(
                "[Exploration Spiral] 読み取りツールが{}回連続しています（Edit/Write/Bash なし）。\n\
                 十分な情報が集まっているなら、行動に移ってください。\
                 情報が不足なら、具体的に何を探しているか明確にしてください。",
                count
            ));
        }

        crate::io::write_json_state(&state_path, &state);
    }

    // Non-categorized tools: don't change counter
    None
}
```

**Step 3: `run()` に統合**

`check_doom_loop` の直後に追加:

```rust
if let Some(ctx) = check_exploration_spiral(tool_name) {
    contexts.push(ctx);
}
```

**Step 4: ビルド確認**

Run: `cd tools/claude-hooks && cargo build --release 2>&1 | tail -5`
Expected: `Finished` with no errors

**Step 5: コミット**

```bash
git add tools/claude-hooks/src/post_any.rs
git commit -m "✨ feat: add exploration spiral detection to post-any"
```

---

## Task 5: Context Pressure Monitor

**Files:**
- Modify: `tools/claude-hooks/src/post_any.rs`
- Modify: `.config/claude/scripts/context-monitor.py`

**Step 1: statusline に context-pressure.json 書き出しを追加**

`context-monitor.py` の `main()` 関数内、`context_info = get_context_from_data(data)` の直後に追加:

```python
# Write context pressure to state file for hooks
if context_info:
    pressure_file = os.path.join(
        os.environ.get("CLAUDE_SESSION_STATE_DIR",
                       os.path.join(os.environ.get("HOME", ""), ".claude", "session-state")),
        "context-pressure.json"
    )
    try:
        os.makedirs(os.path.dirname(pressure_file), exist_ok=True)
        import time
        with open(pressure_file, "w") as f:
            json.dump({"used_pct": context_info["percent"], "ts": time.time()}, f)
    except OSError:
        pass
```

**Step 2: Rust 側 — コンテキスト圧力チェック関数を追加**

```rust
const PRESSURE_STALE_SECS: f64 = 60.0; // Ignore data older than 60s

fn check_context_pressure() -> Option<String> {
    let state_path = crate::io::state_dir().join("context-pressure.json");
    let pressure = crate::io::read_json_state(&state_path);

    let used_pct = pressure["used_pct"].as_f64()?;
    let ts = pressure["ts"].as_f64().unwrap_or(0.0);
    let now = crate::io::now_secs();

    // Skip stale data
    if now - ts > PRESSURE_STALE_SECS {
        return None;
    }

    // Check thresholds (one-shot per session)
    let warned_path = crate::io::state_dir().join("context-pressure-warned.json");
    let mut warned = crate::io::read_json_state(&warned_path);

    // TTL: reset after 2 hours
    let last_reset = warned["lastReset"].as_f64().unwrap_or(now);
    if now - last_reset > 2.0 * 3600.0 {
        warned = serde_json::json!({
            "lastReset": now,
            "warned_80": false,
            "warned_90": false,
            "warned_95": false,
        });
    }

    let (threshold, key, msg) = if used_pct >= 95.0 && !warned["warned_95"].as_bool().unwrap_or(false) {
        (95, "warned_95",
         format!(
            "[Context Pressure] コンテキスト使用率 {:.0}% — 緊急。\n\
             即座に `/checkpoint` で状態を保存し、新セッションに切り替えてください。",
            used_pct
        ))
    } else if used_pct >= 90.0 && !warned["warned_90"].as_bool().unwrap_or(false) {
        (90, "warned_90",
         format!(
            "[Context Pressure] コンテキスト使用率 {:.0}% — 危険。\n\
             サブエージェントに委譲するか `/compact` を実行してください。",
            used_pct
        ))
    } else if used_pct >= 80.0 && !warned["warned_80"].as_bool().unwrap_or(false) {
        (80, "warned_80",
         format!(
            "[Context Pressure] コンテキスト使用率 {:.0}%。\n\
             Read に offset/limit を指定し、Bash 出力を grep/head/tail でフィルタしてください。",
            used_pct
        ))
    } else {
        if used_pct >= 70.0 {
            eprintln!("[Context Pressure] {:.0}% — approaching threshold", used_pct);
        }
        return None;
    };

    warned[key] = serde_json::json!(true);
    crate::io::write_json_state(&warned_path, &warned);

    if threshold >= 90 {
        crate::events::emit_event(
            "pattern",
            &serde_json::json!({
                "type": "context_pressure",
                "used_pct": used_pct,
                "threshold": threshold,
            }),
        );
    }

    Some(msg)
}
```

**Step 3: `run()` に統合**

exploration spiral の直後に追加:

```rust
if let Some(ctx) = check_context_pressure() {
    contexts.push(ctx);
}
```

**Step 4: ビルド確認**

Run: `cd tools/claude-hooks && cargo build --release 2>&1 | tail -5`
Expected: `Finished` with no errors

**Step 5: コミット**

```bash
git add tools/claude-hooks/src/post_any.rs .config/claude/scripts/context-monitor.py
git commit -m "✨ feat: add context pressure monitor with statusline integration"
```

---

## Task 6: Artifact Index を `post_any.rs` に追加

**Files:**
- Modify: `tools/claude-hooks/src/post_any.rs`

**Step 1: Artifact Index 書き込み関数を追加**

```rust
const ARTIFACT_MAX_LINES: usize = 1000;

fn record_artifact(tool_name: &str, data: &serde_json::Value) {
    let index_path = crate::io::state_dir().join("artifact-index.jsonl");

    let (action, file) = match tool_name {
        "Read" => ("read", data["tool_input"]["file_path"].as_str().unwrap_or("")),
        "Edit" => ("modified", data["tool_input"]["file_path"].as_str().unwrap_or("")),
        "Write" => {
            let fp = data["tool_input"]["file_path"].as_str().unwrap_or("");
            if std::path::Path::new(fp).exists() {
                ("modified", fp)
            } else {
                ("created", fp)
            }
        }
        "Grep" => ("searched", data["tool_input"]["path"].as_str().unwrap_or(".")),
        "Glob" => ("searched", data["tool_input"]["path"].as_str().unwrap_or(".")),
        _ => return, // Don't track other tools
    };

    if file.is_empty() && action != "searched" {
        return;
    }

    let entry = serde_json::json!({
        "ts": crate::io::iso_now(),
        "tool": tool_name,
        "action": action,
        "file": file,
    });

    crate::io::append_jsonl(&index_path, &entry, ARTIFACT_MAX_LINES);
}
```

**Step 2: `run()` に統合**

context pressure の直後、`if contexts.is_empty()` の直前に追加:

```rust
// Always record artifact (no context output)
record_artifact(tool_name, data);
```

**Step 3: ビルド確認**

Run: `cd tools/claude-hooks && cargo build --release 2>&1 | tail -5`
Expected: `Finished` with no errors

**Step 4: コミット**

```bash
git add tools/claude-hooks/src/post_any.rs
git commit -m "✨ feat: add artifact index tracking to post-any"
```

---

## Task 7: Error Recovery 6分類を `post_bash.rs` に追加

**Files:**
- Modify: `tools/claude-hooks/src/post_bash.rs`

**Step 1: エラーカテゴリ enum と分類関数を追加**

`check_error_to_codex` 関数の直前に追加:

```rust
enum ErrorCategory {
    PermissionDenied,
    FileNotFound,
    EditMismatch,
    SyntaxError,
    RateLimit,
    Timeout,
    Unknown,
}

fn classify_error(output: &str) -> ErrorCategory {
    let lower = output.to_lowercase();
    if lower.contains("permission denied") || lower.contains("eacces") || lower.contains("operation not permitted") {
        ErrorCategory::PermissionDenied
    } else if lower.contains("no such file") || lower.contains("enoent") || lower.contains("not found") && !lower.contains("module") {
        ErrorCategory::FileNotFound
    } else if lower.contains("file has changed") || lower.contains("content mismatch") || lower.contains("stale") {
        ErrorCategory::EditMismatch
    } else if lower.contains("syntaxerror") || lower.contains("parse error") || lower.contains("unexpected token") {
        ErrorCategory::SyntaxError
    } else if lower.contains("rate limit") || lower.contains("429") || lower.contains("too many requests") {
        ErrorCategory::RateLimit
    } else if lower.contains("timeout") || lower.contains("etimedout") || lower.contains("timed out") {
        ErrorCategory::Timeout
    } else {
        ErrorCategory::Unknown
    }
}

fn recovery_template(category: &ErrorCategory) -> &'static str {
    match category {
        ErrorCategory::PermissionDenied =>
            "リカバリ: ファイルの権限を確認してください。sudo は使わず、適切なパスに書き込むか chmod で最小限の権限を設定してください。",
        ErrorCategory::FileNotFound =>
            "リカバリ: ファイルパスを確認してください。Glob ツールで正しいパスを検索してから再試行してください。",
        ErrorCategory::EditMismatch =>
            "リカバリ: ファイルが変更されています。Read ツールで最新の内容を取得してから、再度 Edit してください。",
        ErrorCategory::SyntaxError =>
            "リカバリ: エラーの行番号を Read ツールで確認し、構文エラーを修正してください。",
        ErrorCategory::RateLimit =>
            "リカバリ: レート制限に達しました。別のタスクに切り替えるか、しばらく待ってから再試行してください。",
        ErrorCategory::Timeout =>
            "リカバリ: コマンドがタイムアウトしました。処理を分割するか、run_in_background で実行してください。",
        ErrorCategory::Unknown => "",
    }
}
```

**Step 2: `check_error_to_codex` にカテゴリ別テンプレート注入を追加**

既存の `parts.push("codex-debugger エージェントを...` の直前に追加:

```rust
    let category = classify_error(output);
    let recovery = recovery_template(&category);
    if !recovery.is_empty() {
        parts.push(recovery.to_string());
    }
```

**Step 3: ビルド確認**

Run: `cd tools/claude-hooks && cargo build --release 2>&1 | tail -5`
Expected: `Finished` with no errors

**Step 4: コミット**

```bash
git add tools/claude-hooks/src/post_bash.rs
git commit -m "✨ feat: add 6-category error classification with recovery templates"
```

---

## Task 8: `settings.json` に post-any hook エントリを追加

**Files:**
- Modify: `.config/claude/settings.json`

**Step 1: PostToolUse 配列に追加**

既存の `PostToolUse` 配列の末尾（Skill tracker の後）に追加:

```json
{
    "hooks": [
        {
            "type": "command",
            "command": "$HOME/dotfiles/tools/claude-hooks/target/release/claude-hooks post-any",
            "timeout": 5,
            "statusMessage": "Observing..."
        }
    ]
}
```

**Step 2: 動作確認**

Claude Code を再起動し、Read ツールを数回使って `~/.claude/session-state/exploration-tracker.json` が更新されることを確認。

**Step 3: コミット**

```bash
git add .config/claude/settings.json
git commit -m "🔧 chore: register post-any hook for universal tool observation"
```

---

## Task 9: `references/resource-bounds.md` を作成

**Files:**
- Create: `.config/claude/references/resource-bounds.md`

**Step 1: リソースバウンディング定数一覧を作成**

```markdown
# Resource Bounds（リソース制限定数一覧）

全 hook の閾値と定数を一元管理。変更時はこのファイルと対応する Rust ソースの両方を更新すること。

## 検出系

| 定数 | 値 | ソース | 根拠 |
|---|---|---|---|
| Doom-Loop Window | 20 fingerprints | `post_any.rs` | OpenDev 論文準拠。件数ベース（時間ではなく） |
| Doom-Loop Threshold | 3 repeats | `post_any.rs` | OpenDev 論文準拠。false positive と検出速度のバランス |
| Doom-Loop Cooldown | 300s | `post_any.rs` | 同じ警告のスパム防止 |
| Exploration Spiral Threshold | 5 consecutive reads | `post_any.rs` | OpenDev 論文準拠 |
| Edit Loop Threshold | 3 edits / 10min | `post_edit.rs` | 同一ファイルの修正ループ検出 |
| Edit Loop Window | 10 min | `post_edit.rs` | 短すぎると正常な反復を誤検出 |
| Context Pressure Warning | 80% | `post_any.rs` | autocompact=80% に合わせる |
| Context Pressure Critical | 90% | `post_any.rs` | OpenDev 論文準拠 |
| Context Pressure Emergency | 95% | `post_any.rs` | OpenDev: 99% → 95% に前倒し |
| Context Pressure Stale | 60s | `post_any.rs` | statusline 更新間隔考慮 |

## 出力制御系

| 定数 | 値 | ソース | 根拠 |
|---|---|---|---|
| Output Offload Lines | 150 lines | `post_bash.rs` | OpenDev: 8000文字。行数ベースで直感的に |
| Output Offload Chars | 6000 chars | `post_bash.rs` | トークン消費の実測値ベース |
| Artifact Index Max Lines | 1000 entries | `post_any.rs` | セッション内のファイル操作上限 |

## 安全弁系

| 定数 | 値 | ソース | 根拠 |
|---|---|---|---|
| Completion Gate Max Retries | 2 | `completion-gate.py` | 無限ループ防止 |
| Edit Counter Compact Suggestion | 30 / 50 edits | `post_edit.rs` | 経験値 |
| Max Recent Edits (loop buffer) | 20 entries | `post_edit.rs` | メモリ効率 |
| Golden Warning Cooldown | 300s | `post_edit.rs` | 同一警告のスパム防止 |
| Checkpoint Edit Threshold | 15 edits | `post_edit.rs` | 十分な変更量で自動保存 |
| Checkpoint Time Threshold | 30 min | `post_edit.rs` | 時間ベースの自動保存 |
| Checkpoint Cooldown | 5 min | `post_edit.rs` | 連続保存を防止 |
| Max Checkpoints | 5 files | `post_edit.rs` | ディスク使用量制限 |

## セッション管理系

| 定数 | 値 | ソース | 根拠 |
|---|---|---|---|
| Session State TTL | 2 hours | 全 hook 共通 | セッション寿命の想定上限 |
| Search-First Session TTL | 2 hours | `pre_tool.rs` | セッション TTL に合わせる |

## AutoEvolve Failure Mode コード

| FM | 説明 | importance | 検出元 |
|---|---|---|---|
| FM-005 | Golden Principles 違反 | 0.8 | `post_edit.rs` |
| FM-006 | Permission denied | 0.9 | `events.rs` |
| FM-007 | Module not found | 0.5 | `events.rs` |
| FM-008 | TypeError/ReferenceError | 0.5 | `events.rs` |
| FM-009 | Memory/timeout/segfault | 1.0/0.6 | `events.rs` |
| FM-010 | Security/injection | 0.9 | `events.rs` |
| FM-011 | Doom-Loop detected | 0.7 | `post_any.rs` |
| FM-012 | Exploration Spiral | 0.5 | `post_any.rs` |
| FM-013 | Context Pressure ≥90% | 0.8 | `post_any.rs` |
```

**Step 2: コミット**

```bash
git add .config/claude/references/resource-bounds.md
git commit -m "📝 docs: add resource-bounds reference with all hook constants"
```

---

## Task 10: 統合ビルド + 動作確認

**Files:**
- 全体

**Step 1: クリーンビルド**

Run: `cd tools/claude-hooks && cargo build --release 2>&1`
Expected: `Finished` with no errors, no warnings

**Step 2: バイナリサイズ確認**

Run: `ls -lh tools/claude-hooks/target/release/claude-hooks`
Expected: 数 MB 以内（strip + LTO が効いている）

**Step 3: 手動テスト — Doom-Loop**

```bash
# Doom-Loop テスト用の入力を3回送信
for i in 1 2 3; do
echo '{"tool_name":"Bash","tool_input":{"command":"npm test"},"tool_output":"FAIL"}' | \
  tools/claude-hooks/target/release/claude-hooks post-any 2>/dev/null
echo "---"
done
```
Expected: 3回目に `[Doom-Loop]` メッセージが含まれる

**Step 4: 手動テスト — Exploration Spiral**

```bash
# 5回連続 Read
for i in 1 2 3 4 5; do
echo '{"tool_name":"Read","tool_input":{"file_path":"src/main.rs"},"tool_output":"..."}' | \
  tools/claude-hooks/target/release/claude-hooks post-any 2>/dev/null
echo "---"
done
```
Expected: 5回目に `[Exploration Spiral]` メッセージが含まれる

**Step 5: 手動テスト — Artifact Index**

```bash
echo '{"tool_name":"Edit","tool_input":{"file_path":"src/lib.rs","old_string":"old","new_string":"new"},"tool_output":"ok"}' | \
  tools/claude-hooks/target/release/claude-hooks post-any 2>/dev/null
cat ~/.claude/session-state/artifact-index.jsonl | tail -1
```
Expected: `{"ts":"...","tool":"Edit","action":"modified","file":"src/lib.rs"}` のような JSONL エントリ

**Step 6: 状態ファイルクリーンアップ**

```bash
rm -f ~/.claude/session-state/doom-loop.json
rm -f ~/.claude/session-state/exploration-tracker.json
rm -f ~/.claude/session-state/artifact-index.jsonl
rm -f ~/.claude/session-state/context-pressure-warned.json
```

**Step 7: コミット（テスト状態ファイル除外確認）**

Run: `git status`
Expected: テスト中に変更されたソースファイルのみ。session-state は gitignore 対象。

---

## Task 11: 設計ドキュメントの完了マーク + Plan 移動

**Step 1: Plan を completed に移動**

```bash
mkdir -p docs/plans/completed
mv docs/plans/2026-03-16-opendev-harness-improvements.md docs/plans/completed/
mv docs/plans/2026-03-16-opendev-harness-improvements-design.md docs/plans/completed/
```

**Step 2: 最終コミット**

```bash
git add docs/plans/
git commit -m "📝 docs: complete OpenDev harness improvements — move plans to completed"
```

---

## Progress

- [ ] Task 1: events.rs FM-011〜013 追加
- [ ] Task 2: io.rs append_jsonl ユーティリティ
- [ ] Task 3: post_any.rs — Doom-Loop Detection
- [ ] Task 4: post_any.rs — Exploration Spiral Detection
- [ ] Task 5: post_any.rs + context-monitor.py — Context Pressure Monitor
- [ ] Task 6: post_any.rs — Artifact Index
- [ ] Task 7: post_bash.rs — Error Recovery 6分類
- [ ] Task 8: settings.json — post-any hook 登録
- [ ] Task 9: resource-bounds.md 作成
- [ ] Task 10: 統合ビルド + 動作確認
- [ ] Task 11: Plan 完了 + 移動
