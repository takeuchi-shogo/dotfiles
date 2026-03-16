use std::io::Read;
use std::path::PathBuf;

pub fn read_stdin() -> String {
    let mut buf = String::new();
    let _ = std::io::stdin().read_to_string(&mut buf);
    buf
}

pub fn passthrough(raw: &str) {
    print!("{}", raw);
}

pub fn context(event_name: &str, msg: &str) {
    let output = serde_json::json!({
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": msg
        }
    });
    print!("{}", output);
}

pub fn deny(reason: &str) -> ! {
    // Security audit log — record every deny event
    audit_log_deny(reason);
    eprintln!("{}", reason);
    std::process::exit(2);
}

/// Append a deny event to the security audit log (JSONL).
fn audit_log_deny(reason: &str) {
    let log_dir = std::path::PathBuf::from(home_dir())
        .join(".claude")
        .join("agent-memory")
        .join("security");
    if std::fs::create_dir_all(&log_dir).is_err() {
        return;
    }
    let log_path = log_dir.join("audit.jsonl");

    let entry = serde_json::json!({
        "timestamp": iso_now(),
        "event": "deny",
        "reason": &reason[..reason.len().min(500)],
        "session_id": std::env::var("CLAUDE_SESSION_ID").unwrap_or_default(),
        "cwd": std::env::current_dir()
            .map(|p| p.to_string_lossy().to_string())
            .unwrap_or_default(),
    });

    if let Ok(mut f) = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(&log_path)
    {
        use std::io::Write;
        let _ = writeln!(f, "{}", entry);
    }
}

pub fn home_dir() -> String {
    std::env::var("HOME").unwrap_or_default()
}

pub fn state_dir() -> PathBuf {
    let dir = std::env::var("CLAUDE_SESSION_STATE_DIR").unwrap_or_else(|_| {
        format!("{}/.claude/session-state", home_dir())
    });
    PathBuf::from(dir)
}

pub fn references_dir() -> PathBuf {
    PathBuf::from(format!("{}/.claude/references", home_dir()))
}

pub fn which(name: &str) -> bool {
    if let Ok(path) = std::env::var("PATH") {
        for dir in path.split(':') {
            if std::path::Path::new(dir).join(name).exists() {
                return true;
            }
        }
    }
    false
}

/// Read a JSON state file, return empty object on failure.
pub fn read_json_state(path: &std::path::Path) -> serde_json::Value {
    std::fs::read_to_string(path)
        .ok()
        .and_then(|s| serde_json::from_str(&s).ok())
        .unwrap_or_else(|| serde_json::json!({}))
}

/// Write a JSON state file, creating parent dirs if needed.
pub fn write_json_state(path: &std::path::Path, data: &serde_json::Value) {
    if let Some(parent) = path.parent() {
        let _ = std::fs::create_dir_all(parent);
    }
    let _ = std::fs::write(path, serde_json::to_string(data).unwrap_or_default());
}

/// Append a single JSON line to a JSONL file, creating parent dirs if needed.
/// Enforces max_lines by dropping oldest 20% when exceeded.
pub fn append_jsonl(path: &std::path::Path, entry: &serde_json::Value, max_lines: usize) {
    if let Some(parent) = path.parent() {
        let _ = std::fs::create_dir_all(parent);
    }

    let existing = std::fs::read_to_string(path).unwrap_or_default();
    let line_count = existing.lines().count();

    if line_count >= max_lines {
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

/// Get current UNIX timestamp as f64.
pub fn now_secs() -> f64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs_f64()
}

/// Format UNIX seconds as ISO 8601 UTC string.
pub fn unix_to_iso(secs: u64) -> String {
    let time_s = (secs % 60) as u32;
    let time_m = ((secs / 60) % 60) as u32;
    let time_h = ((secs / 3600) % 24) as u32;
    let days = (secs / 86400) as i64;

    // Howard Hinnant's civil_from_days algorithm
    let z = days + 719468;
    let era = (if z >= 0 { z } else { z - 146096 }) / 146097;
    let doe = (z - era * 146097) as u32;
    let yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
    let y = yoe as i64 + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = doy - (153 * mp + 2) / 5 + 1;
    let m = if mp < 10 { mp + 3 } else { mp - 9 };
    let y = if m <= 2 { y + 1 } else { y };

    format!(
        "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z",
        y, m, d, time_h, time_m, time_s
    )
}

pub fn iso_now() -> String {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();
    unix_to_iso(secs)
}
