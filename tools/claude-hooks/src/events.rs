use regex::Regex;
use std::io::Write;
use std::path::PathBuf;

struct Rule {
    pattern: Regex,
    score: f64,
    failure_mode: &'static str,
}

fn importance_rules() -> Vec<Rule> {
    vec![
        Rule {
            pattern: Regex::new(r"(?i)EACCES|Permission denied").unwrap(),
            score: 0.9,
            failure_mode: "FM-006",
        },
        Rule {
            pattern: Regex::new(r"(?i)segfault|SIGSEGV|OOM|out of memory").unwrap(),
            score: 1.0,
            failure_mode: "FM-009",
        },
        Rule {
            pattern: Regex::new(r"GP-00[1-5]").unwrap(),
            score: 0.8,
            failure_mode: "FM-005",
        },
        Rule {
            pattern: Regex::new(r"(?i)security|vulnerability|injection").unwrap(),
            score: 0.9,
            failure_mode: "FM-010",
        },
        Rule {
            pattern: Regex::new(r"(?i)Cannot find module|ModuleNotFoundError").unwrap(),
            score: 0.5,
            failure_mode: "FM-007",
        },
        Rule {
            pattern: Regex::new(r"(?i)TypeError|ReferenceError").unwrap(),
            score: 0.5,
            failure_mode: "FM-008",
        },
        Rule {
            pattern: Regex::new(r"(?i)timeout|ETIMEDOUT").unwrap(),
            score: 0.6,
            failure_mode: "FM-009",
        },
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
        Rule {
            pattern: Regex::new(r"(?i)\bwarnings?\s*:").unwrap(),
            score: 0.2,
            failure_mode: "",
        },
        Rule {
            pattern: Regex::new(r"(?i)deprecated").unwrap(),
            score: 0.3,
            failure_mode: "",
        },
    ]
}

fn base_importance(category: &str) -> f64 {
    match category {
        "error" => 0.5,
        "quality" => 0.6,
        "pattern" => 0.4,
        "correction" => 0.7,
        _ => 0.5,
    }
}

fn compute_importance(category: &str, searchable: &str) -> (f64, f64, String) {
    let rules = importance_rules();
    for rule in &rules {
        if rule.pattern.is_match(searchable) {
            return (rule.score, 0.8, rule.failure_mode.to_string());
        }
    }
    (base_importance(category), 0.5, String::new())
}

fn get_data_dir() -> PathBuf {
    if let Ok(dir) = std::env::var("AUTOEVOLVE_DATA_DIR") {
        return PathBuf::from(dir);
    }
    PathBuf::from(crate::io::home_dir())
        .join(".claude")
        .join("agent-memory")
}

/// Check if this event is a duplicate (same category + skill_name within the same second).
/// Uses a JSON state file to track recently emitted keys.
fn is_duplicate_emit(category: &str, data: &serde_json::Value) -> bool {
    let now_sec = crate::io::now_secs() as u64;
    let skill = data
        .get("skill_name")
        .and_then(|v| v.as_str())
        .or_else(|| data.get("rule").and_then(|v| v.as_str()))
        .unwrap_or("");
    let file = data
        .get("file")
        .and_then(|v| v.as_str())
        .unwrap_or("");
    let key = format!("{}:{}:{}:{}", category, skill, file, now_sec);

    let state_path = get_data_dir().join("current-session-dedup.json");
    let mut seen: std::collections::HashSet<String> =
        std::fs::read_to_string(&state_path)
            .ok()
            .and_then(|s| serde_json::from_str(&s).ok())
            .unwrap_or_default();

    if seen.contains(&key) {
        return true;
    }

    seen.insert(key);
    // Cap at 200 entries — HashSet order is non-deterministic, so this is
    // not LRU but a simple size limit. Acceptable because worst case is
    // a duplicate event in the JSONL (not data loss).
    if seen.len() > 200 {
        seen.clear();
    }
    // Only write if serialization succeeds; skip on failure to avoid
    // writing empty string which would reset dedup state (I-1 fix).
    if let Ok(serialized) = serde_json::to_string(&seen) {
        let _ = std::fs::write(&state_path, serialized);
    }
    false
}

/// Emit a session event to current-session.jsonl (compatible with session_events.py).
/// Deduplicates events with the same category+skill+file within the same second.
pub fn emit_event(category: &str, data: &serde_json::Value) {
    if is_duplicate_emit(category, data) {
        return;
    }

    let dir = get_data_dir();
    let path = dir.join("current-session.jsonl");

    if std::fs::create_dir_all(&dir).is_err() {
        return;
    }

    let searchable = data.to_string();
    let (importance, confidence, failure_mode) = compute_importance(category, &searchable);

    let entry = serde_json::json!({
        "timestamp": crate::io::iso_now(),
        "category": category,
        "importance": (importance * 100.0).round() / 100.0,
        "confidence": (confidence * 100.0).round() / 100.0,
        "failure_mode": failure_mode,
        "failure_type": "generalization",
        "scored_by": "rule",
        "promotion_status": "pending",
        "data": data,
    });

    if let Ok(mut f) = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(&path)
    {
        let _ = writeln!(f, "{}", entry);
    }
}
