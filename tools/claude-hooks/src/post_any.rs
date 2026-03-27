//! PostToolUse/* — fires on ALL tool calls.
//! Detections: doom-loop, exploration spiral, context pressure, artifact index.

use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

const DOOM_LOOP_WINDOW: usize = 20;
const DOOM_LOOP_THRESHOLD: usize = 3;
const DOOM_LOOP_COOLDOWN: f64 = 300.0;
const TTL_SECS: f64 = 2.0 * 3600.0;

// ── exploration spiral constants ────────────────────────────────────
const EXPLORATION_INFO_THRESHOLD: u64 = 5;
const EXPLORATION_WARNING_THRESHOLD: u64 = 7;
const EXPLORATION_CRITICAL_THRESHOLD: u64 = 10;
const READ_TOOLS: &[&str] = &["Read", "Grep", "Glob", "WebFetch", "WebSearch"];
const ACTION_TOOLS: &[&str] = &["Edit", "Write", "Bash", "Agent", "Skill"];

// ── context pressure constants ──────────────────────────────────────
const CONTEXT_PRESSURE_STALE_SECS: f64 = 60.0;

// ── doom-loop detection ─────────────────────────────────────────────

fn extract_key_args(tool_name: &str, input: &serde_json::Value) -> String {
    match tool_name {
        "Bash" => {
            let cmd = input["command"].as_str().unwrap_or("");
            cmd.chars().take(50).collect()
        }
        "Edit" => {
            let file = input["file_path"].as_str().unwrap_or("");
            let old = input["old_string"].as_str().unwrap_or("");
            let old_trunc: String = old.chars().take(100).collect();
            format!("{}{}", file, old_trunc)
        }
        "Read" => input["file_path"].as_str().unwrap_or("").to_string(),
        "Grep" => {
            let pattern = input["pattern"].as_str().unwrap_or("");
            let path = input["path"].as_str().unwrap_or("");
            format!("{}{}", pattern, path)
        }
        "Glob" => input["pattern"].as_str().unwrap_or("").to_string(),
        "Write" => input["file_path"].as_str().unwrap_or("").to_string(),
        _ => {
            let raw = format!("{}{}", tool_name, input);
            raw.chars().take(200).collect()
        }
    }
}

fn fingerprint(tool_name: &str, key_args: &str) -> u64 {
    let mut hasher = DefaultHasher::new();
    tool_name.hash(&mut hasher);
    key_args.hash(&mut hasher);
    hasher.finish()
}

fn tool_label(tool_name: &str, input: &serde_json::Value) -> String {
    match tool_name {
        "Bash" => {
            let cmd = input["command"].as_str().unwrap_or("");
            let short: String = cmd.chars().take(40).collect();
            format!("Bash: {}", short)
        }
        "Edit" | "Write" | "Read" => {
            let file = input["file_path"].as_str().unwrap_or("");
            let basename = std::path::Path::new(file)
                .file_name()
                .map(|n| n.to_string_lossy().to_string())
                .unwrap_or_else(|| file.to_string());
            format!("{}: {}", tool_name, basename)
        }
        "Grep" => {
            let pattern = input["pattern"].as_str().unwrap_or("");
            format!("Grep: {}", pattern)
        }
        "Glob" => {
            let pattern = input["pattern"].as_str().unwrap_or("");
            format!("Glob: {}", pattern)
        }
        _ => tool_name.to_string(),
    }
}

fn check_doom_loop(tool_name: &str, data: &serde_json::Value) -> Option<String> {
    let input = &data["tool_input"];
    let key_args = extract_key_args(tool_name, input);
    let hash = fingerprint(tool_name, &key_args);
    let now = crate::io::now_secs();

    let state_path = crate::io::state_dir().join("doom-loop.json");
    let mut state = crate::io::read_json_state(&state_path);

    // TTL reset
    let last_reset = state["lastReset"].as_f64().unwrap_or(now);
    if now - last_reset > TTL_SECS {
        state = serde_json::json!({
            "fingerprints": [],
            "lastReset": now,
            "lastWarned": {}
        });
    }

    // Read existing fingerprints
    let mut fps: Vec<serde_json::Value> = state["fingerprints"]
        .as_array()
        .cloned()
        .unwrap_or_default();

    // Append new entry
    fps.push(serde_json::json!({
        "hash": hash,
        "tool": tool_name,
        "ts": now
    }));

    // Keep sliding window
    if fps.len() > DOOM_LOOP_WINDOW {
        fps = fps[fps.len() - DOOM_LOOP_WINDOW..].to_vec();
    }

    // Count occurrences of this hash in the window
    let count = fps.iter().filter(|e| e["hash"].as_u64() == Some(hash)).count();

    // Save state
    state["fingerprints"] = serde_json::json!(fps);
    if state["lastWarned"].is_null() {
        state["lastWarned"] = serde_json::json!({});
    }
    crate::io::write_json_state(&state_path, &state);

    if count >= DOOM_LOOP_THRESHOLD {
        // Cooldown check
        let hash_key = hash.to_string();
        let last_warned = state["lastWarned"][&hash_key].as_f64().unwrap_or(0.0);
        if now - last_warned < DOOM_LOOP_COOLDOWN {
            return None;
        }

        // Update lastWarned
        let mut state = crate::io::read_json_state(&state_path);
        if let Some(obj) = state["lastWarned"].as_object_mut() {
            obj.insert(hash_key, serde_json::json!(now));
        }
        crate::io::write_json_state(&state_path, &state);

        let label = tool_label(tool_name, input);

        // Emit AutoEvolve event
        crate::events::emit_event(
            "pattern",
            &serde_json::json!({
                "type": "doom_loop",
                "tool": tool_name,
                "count": count,
                "hash": hash,
            }),
        );

        Some(format!(
            "[Doom-Loop] `{}` が{}回繰り返されています（直近{}回のツール呼び出し内）。\n\
             同じアプローチを繰り返しても解決しません。根本原因を分析し、別の方法を試してください。",
            label, count, DOOM_LOOP_WINDOW
        ))
    } else {
        None
    }
}

// ── exploration spiral detection ────────────────────────────────────

fn check_exploration_spiral(tool_name: &str) -> Option<String> {
    let now = crate::io::now_secs();
    let state_path = crate::io::state_dir().join("exploration-tracker.json");
    let mut state = crate::io::read_json_state(&state_path);

    // TTL reset
    let last_reset = state["lastReset"].as_f64().unwrap_or(now);
    if now - last_reset > TTL_SECS {
        state = serde_json::json!({
            "consecutive_reads": 0,
            "warned_info": false,
            "warned_warning": false,
            "warned_critical": false,
            "lastReset": now
        });
    }

    let mut consecutive_reads = state["consecutive_reads"].as_u64().unwrap_or(0);
    let mut warned_info = state["warned_info"].as_bool().unwrap_or(false);
    let mut warned_warning = state["warned_warning"].as_bool().unwrap_or(false);
    let mut warned_critical = state["warned_critical"].as_bool().unwrap_or(false);

    if ACTION_TOOLS.contains(&tool_name) {
        consecutive_reads = 0;
        warned_info = false;
        warned_warning = false;
        warned_critical = false;
    } else if READ_TOOLS.contains(&tool_name) {
        consecutive_reads += 1;
    }

    state["consecutive_reads"] = serde_json::json!(consecutive_reads);
    state["warned_info"] = serde_json::json!(warned_info);
    state["warned_warning"] = serde_json::json!(warned_warning);
    state["warned_critical"] = serde_json::json!(warned_critical);
    if state["lastReset"].is_null() {
        state["lastReset"] = serde_json::json!(now);
    }

    // Critical (10): emit event + replan intervention
    let result = if consecutive_reads >= EXPLORATION_CRITICAL_THRESHOLD && !warned_critical {
        state["warned_critical"] = serde_json::json!(true);
        state["warned_warning"] = serde_json::json!(true);
        state["warned_info"] = serde_json::json!(true);

        crate::events::emit_event(
            "pattern",
            &serde_json::json!({
                "type": "exploration_spiral",
                "consecutive_reads": consecutive_reads,
                "severity": "critical",
            }),
        );

        Some(format!(
            "[Exploration Spiral: CRITICAL] 読み取りツールが{}回連続しています（Edit/Write/Bash なし）。\n\
             深刻な探索スパイラルです。現在の計画を見直し、リプランしてください。",
            consecutive_reads
        ))
    // Warning (7): emit event + session warning
    } else if consecutive_reads >= EXPLORATION_WARNING_THRESHOLD && !warned_warning {
        state["warned_warning"] = serde_json::json!(true);
        state["warned_info"] = serde_json::json!(true);

        crate::events::emit_event(
            "pattern",
            &serde_json::json!({
                "type": "exploration_spiral",
                "consecutive_reads": consecutive_reads,
                "severity": "warning",
            }),
        );

        Some(format!(
            "[Exploration Spiral: WARNING] 読み取りツールが{}回連続しています（Edit/Write/Bash なし）。\n\
             十分な情報が集まっているなら、行動に移ってください。情報が不足なら、具体的に何を探しているか明確にしてください。",
            consecutive_reads
        ))
    // Info (5): log only, no event emission
    } else if consecutive_reads >= EXPLORATION_INFO_THRESHOLD && !warned_info {
        state["warned_info"] = serde_json::json!(true);
        eprintln!(
            "[Exploration Spiral: INFO] consecutive_reads={} — info threshold, no event emitted",
            consecutive_reads
        );
        None
    } else {
        None
    };

    crate::io::write_json_state(&state_path, &state);
    result
}

// ── context pressure monitor ───────────────────────────────────────

fn check_context_pressure() -> Option<String> {
    let now = crate::io::now_secs();
    let state_dir = crate::io::state_dir();

    // Read pressure data written by statusline
    let pressure_path = state_dir.join("context-pressure.json");
    let pressure = crate::io::read_json_state(&pressure_path);

    let used_pct = match pressure["used_pct"].as_f64() {
        Some(v) => v,
        None => return None,
    };

    let ts = pressure["ts"].as_f64().unwrap_or(0.0);
    if now - ts > CONTEXT_PRESSURE_STALE_SECS {
        return None; // stale data
    }

    // Read warned state
    let warned_path = state_dir.join("context-pressure-warned.json");
    let mut warned = crate::io::read_json_state(&warned_path);

    // TTL reset
    let last_reset = warned["lastReset"].as_f64().unwrap_or(now);
    if now - last_reset > TTL_SECS {
        warned = serde_json::json!({
            "warned_80": false,
            "warned_90": false,
            "warned_95": false,
            "lastReset": now
        });
    }

    let warned_80 = warned["warned_80"].as_bool().unwrap_or(false);
    let warned_90 = warned["warned_90"].as_bool().unwrap_or(false);
    let warned_95 = warned["warned_95"].as_bool().unwrap_or(false);

    // Higher thresholds take priority
    let result = if used_pct >= 95.0 && !warned_95 {
        warned["warned_95"] = serde_json::json!(true);
        warned["warned_90"] = serde_json::json!(true);
        warned["warned_80"] = serde_json::json!(true);

        crate::events::emit_event(
            "pattern",
            &serde_json::json!({
                "type": "context_pressure",
                "used_pct": used_pct,
                "threshold": 95,
            }),
        );

        Some(format!(
            "[Context Pressure] コンテキスト使用率 {:.0}% — 緊急。\n\
             即座に /checkpoint で状態を保存し、新セッションに切り替えてください。",
            used_pct
        ))
    } else if used_pct >= 90.0 && !warned_90 {
        warned["warned_90"] = serde_json::json!(true);
        warned["warned_80"] = serde_json::json!(true);

        crate::events::emit_event(
            "pattern",
            &serde_json::json!({
                "type": "context_pressure",
                "used_pct": used_pct,
                "threshold": 90,
            }),
        );

        Some(format!(
            "[Context Pressure] コンテキスト使用率 {:.0}% — 危険。\n\
             サブエージェントに委譲するか /compact を実行してください。",
            used_pct
        ))
    } else if used_pct >= 80.0 && !warned_80 {
        warned["warned_80"] = serde_json::json!(true);

        Some(format!(
            "[Context Pressure] コンテキスト使用率 {:.0}%。\n\
             Read に offset/limit を指定し、Bash 出力を grep/head/tail でフィルタしてください。",
            used_pct
        ))
    } else if used_pct >= 70.0 {
        eprintln!("[Context Pressure] {:.0}% — approaching threshold", used_pct);
        None
    } else {
        None
    };

    if warned["lastReset"].is_null() {
        warned["lastReset"] = serde_json::json!(now);
    }
    crate::io::write_json_state(&warned_path, &warned);
    result
}

// ── artifact index ─────────────────────────────────────────────────

fn record_artifact(tool_name: &str, data: &serde_json::Value) {
    let input = &data["tool_input"];

    let (action, file) = match tool_name {
        "Read" => {
            let file = input["file_path"].as_str().unwrap_or("").to_string();
            ("read", file)
        }
        "Edit" => {
            let file = input["file_path"].as_str().unwrap_or("").to_string();
            ("modified", file)
        }
        "Write" => {
            let file_str = input["file_path"].as_str().unwrap_or("");
            let action = if std::path::Path::new(file_str).exists() {
                "modified"
            } else {
                "created"
            };
            (action, file_str.to_string())
        }
        "Grep" | "Glob" => {
            let path = input["path"].as_str().unwrap_or("");
            let file = if path.is_empty() {
                ".".to_string()
            } else {
                path.to_string()
            };
            ("searched", file)
        }
        _ => return, // Skip non-tracked tools
    };

    let entry = serde_json::json!({
        "ts": crate::io::iso_now(),
        "tool": tool_name,
        "action": action,
        "file": file,
    });

    let index_path = crate::io::state_dir().join("artifact-index.jsonl");
    crate::io::append_jsonl(&index_path, &entry, 1000);
}

// ── main entry ──────────────────────────────────────────────────────

pub fn run(raw: &str, data: &serde_json::Value) -> Result<(), String> {
    let tool_name = data["tool_name"].as_str().unwrap_or("");
    let mut contexts: Vec<String> = Vec::new();

    if let Some(ctx) = check_doom_loop(tool_name, data) {
        contexts.push(ctx);
    }

    if let Some(ctx) = check_exploration_spiral(tool_name) {
        contexts.push(ctx);
    }

    if let Some(ctx) = check_context_pressure() {
        contexts.push(ctx);
    }

    record_artifact(tool_name, data);

    if contexts.is_empty() {
        crate::io::passthrough(raw);
    } else {
        crate::io::context("PostToolUse", &contexts.join("\n\n"));
    }
    Ok(())
}
