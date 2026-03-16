//! PostToolUse/* — fires on ALL tool calls.
//! Currently: doom-loop detection.
//! Future: exploration spiral, context pressure, artifact index.

use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

const DOOM_LOOP_WINDOW: usize = 20;
const DOOM_LOOP_THRESHOLD: usize = 3;
const DOOM_LOOP_COOLDOWN: f64 = 300.0;
const TTL_SECS: f64 = 2.0 * 3600.0;

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

// ── main entry ──────────────────────────────────────────────────────

pub fn run(raw: &str, data: &serde_json::Value) -> Result<(), String> {
    let tool_name = data["tool_name"].as_str().unwrap_or("");
    let mut contexts: Vec<String> = Vec::new();

    if let Some(ctx) = check_doom_loop(tool_name, data) {
        contexts.push(ctx);
    }

    // (exploration spiral, context pressure, artifact index will be added in later tasks)

    if contexts.is_empty() {
        crate::io::passthrough(raw);
    } else {
        crate::io::context("PostToolUse", &contexts.join("\n\n"));
    }
    Ok(())
}
