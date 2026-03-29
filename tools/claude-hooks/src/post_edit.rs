//! PostToolUse/Edit|Write — consolidates 4 hooks:
//! auto-format, suggest-compact (edit counter + loop detection), golden-check, checkpoint-manager

use regex::Regex;
use std::path::{Path, PathBuf};
use std::process::Command;

// ── auto-format ─────────────────────────────────────────────────────

fn find_tool(name: &str) -> Option<String> {
    if crate::io::which(name) {
        Some(name.to_string())
    } else {
        None
    }
}

fn run_silent(cmd: &str, args: &[&str]) -> bool {
    Command::new(cmd)
        .args(args)
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::null())
        .status()
        .map(|s| s.success())
        .unwrap_or(false)
}

fn run_capture(cmd: &str, args: &[&str]) -> (bool, String) {
    match Command::new(cmd)
        .args(args)
        .env("NO_COLOR", "1")
        .output()
    {
        Ok(o) => {
            let out = format!(
                "{}{}",
                String::from_utf8_lossy(&o.stdout),
                String::from_utf8_lossy(&o.stderr)
            );
            (o.status.success(), out)
        }
        Err(_) => (false, String::new()),
    }
}

fn trim_lines(text: &str, max: usize) -> Vec<String> {
    text.lines()
        .map(|l| l.trim_end().to_string())
        .filter(|l| !l.is_empty())
        .take(max)
        .collect()
}

/// Check if a Prettier config exists by walking up from the file.
fn has_prettier_config(file_path: &str) -> bool {
    let prettier_configs: &[&str] = &[
        ".prettierrc", ".prettierrc.js", ".prettierrc.cjs",
        ".prettierrc.json", ".prettierrc.yml", ".prettierrc.yaml",
        "prettier.config.js", "prettier.config.mjs",
    ];
    let mut dir = Path::new(file_path).parent();
    while let Some(d) = dir {
        for cfg in prettier_configs {
            if d.join(cfg).exists() {
                return true;
            }
        }
        if d.join(".git").exists() {
            break;
        }
        dir = d.parent();
    }
    false
}

fn format_typescript(file_path: &str) -> Vec<String> {
    let oxlint = find_tool("oxlint").unwrap_or_else(|| "npx --yes oxlint@latest".to_string());

    // Format: use Prettier if config exists, otherwise Biome
    if has_prettier_config(file_path) {
        let prettier = find_tool("prettier").unwrap_or_else(|| "npx prettier".to_string());
        let prettier_parts: Vec<&str> = prettier.split_whitespace().collect();
        if prettier_parts.len() == 1 {
            run_silent(prettier_parts[0], &["--write", file_path]);
        } else {
            let _ = Command::new(prettier_parts[0])
                .args(&prettier_parts[1..])
                .args(["--write", file_path])
                .stdout(std::process::Stdio::null())
                .stderr(std::process::Stdio::null())
                .status();
        }
    } else {
        let biome = find_tool("biome").unwrap_or_else(|| "npx --yes @biomejs/biome@latest".to_string());
        let biome_parts: Vec<&str> = biome.split_whitespace().collect();
        if biome_parts.len() == 1 {
            run_silent(biome_parts[0], &["format", "--write", file_path]);
        } else {
            let _ = Command::new(biome_parts[0])
                .args(&biome_parts[1..])
                .args(["format", "--write", file_path])
                .stdout(std::process::Stdio::null())
                .stderr(std::process::Stdio::null())
                .status();
        }
    }

    // Lint
    let oxlint_parts: Vec<&str> = oxlint.split_whitespace().collect();
    let (ok, output) = if oxlint_parts.len() == 1 {
        run_capture(oxlint_parts[0], &["--fix", file_path])
    } else {
        match Command::new(oxlint_parts[0])
            .args(&oxlint_parts[1..])
            .args(["--fix", file_path])
            .env("NO_COLOR", "1")
            .output()
        {
            Ok(o) => (
                o.status.success(),
                format!(
                    "{}{}",
                    String::from_utf8_lossy(&o.stdout),
                    String::from_utf8_lossy(&o.stderr)
                ),
            ),
            Err(_) => (false, String::new()),
        }
    };

    if !ok && !output.is_empty() {
        trim_lines(&output, 20)
            .into_iter()
            .filter(|l| !l.starts_with("Found") && !l.starts_with("Finished") && !l.contains("oxlint"))
            .collect()
    } else {
        Vec::new()
    }
}

fn format_python(file_path: &str) -> Vec<String> {
    let ruff = find_tool("ruff").unwrap_or_else(|| "ruff".to_string());
    run_silent(&ruff, &["format", file_path]);
    let (ok, output) = run_capture(&ruff, &["check", "--fix", file_path]);
    if !ok && !output.is_empty() && !output.contains("All checks passed") {
        trim_lines(&output, 20)
            .into_iter()
            .filter(|l| !l.starts_with("Found"))
            .collect()
    } else {
        Vec::new()
    }
}

fn format_go(file_path: &str) -> Vec<String> {
    let gofmt = find_tool("gofmt").unwrap_or_else(|| "gofmt".to_string());
    run_silent(&gofmt, &["-w", file_path]);

    let dir = Path::new(file_path)
        .parent()
        .map(|p| p.to_string_lossy().to_string())
        .unwrap_or_else(|| ".".to_string());
    let pattern = format!("{}/...", dir);

    if crate::io::which("golangci-lint") {
        let (ok, output) =
            run_capture("golangci-lint", &["run", "--fix", "--new-from-rev=HEAD", &pattern]);
        if !ok && !output.is_empty() {
            trim_lines(&output, 20)
                .into_iter()
                .filter(|l| !l.starts_with("level=") && !l.contains("congrats"))
                .collect()
        } else {
            Vec::new()
        }
    } else {
        let (ok, output) = run_capture("go", &["vet", &pattern]);
        if !ok && !output.is_empty() {
            trim_lines(&output, 20)
        } else {
            Vec::new()
        }
    }
}

/// Check if a project-level formatter config exists by walking up from the file.
/// Returns true if a config file for the given language is found.
/// Go (gofmt) is always considered configured — it's the language standard.
fn has_project_formatter_config(file_path: &str, lang: &str) -> bool {
    let config_files: &[&str] = match lang {
        "python" => &[
            "pyproject.toml",
            "ruff.toml",
            ".ruff.toml",
            "setup.cfg",
            ".flake8",
        ],
        "typescript" => &[
            "biome.json",
            "biome.jsonc",
            ".prettierrc",
            ".prettierrc.js",
            ".prettierrc.cjs",
            ".prettierrc.json",
            ".prettierrc.yml",
            ".prettierrc.yaml",
            "prettier.config.js",
            "prettier.config.mjs",
            ".eslintrc",
            ".eslintrc.js",
            ".eslintrc.cjs",
            ".eslintrc.json",
            ".eslintrc.yml",
            "eslint.config.js",
            "eslint.config.mjs",
        ],
        "go" => return true, // gofmt is always safe
        _ => return false,
    };

    let mut dir = Path::new(file_path).parent();
    while let Some(d) = dir {
        for cfg in config_files {
            if d.join(cfg).exists() {
                return true;
            }
        }
        // Stop at git root — don't walk beyond the project
        if d.join(".git").exists() {
            break;
        }
        dir = d.parent();
    }
    false
}

fn auto_format(file_path: &str) -> Option<(String, Vec<String>)> {
    if file_path.is_empty() {
        return None;
    }

    let ext = Path::new(file_path)
        .extension()
        .map(|e| e.to_string_lossy().to_lowercase())
        .unwrap_or_default();

    let (tool, errors) = match ext.as_str() {
        "ts" | "tsx" | "js" | "jsx" => {
            if !has_project_formatter_config(file_path, "typescript") {
                eprintln!("[Auto-Format] skip: no formatter config found for {}", ext);
                return None;
            }
            ("Oxlint", format_typescript(file_path))
        }
        "py" => {
            if !has_project_formatter_config(file_path, "python") {
                eprintln!("[Auto-Format] skip: no formatter config found for {}", ext);
                return None;
            }
            ("Ruff", format_python(file_path))
        }
        "go" => ("go vet", format_go(file_path)),
        "json" | "jsonc" | "css" | "scss" => {
            if !has_project_formatter_config(file_path, "typescript") {
                eprintln!("[Auto-Format] skip: no formatter config found for {}", ext);
                return None;
            }
            let biome = find_tool("biome").unwrap_or_else(|| "npx --yes @biomejs/biome@latest".to_string());
            let parts: Vec<&str> = biome.split_whitespace().collect();
            if parts.len() == 1 {
                run_silent(parts[0], &["format", "--write", file_path]);
            } else {
                let _ = Command::new(parts[0])
                    .args(&parts[1..])
                    .args(["format", "--write", file_path])
                    .stdout(std::process::Stdio::null())
                    .stderr(std::process::Stdio::null())
                    .status();
            }
            return None;
        }
        _ => return None,
    };

    if errors.is_empty() {
        let basename = Path::new(file_path)
            .file_name()
            .map(|n| n.to_string_lossy().to_string())
            .unwrap_or_default();
        eprintln!("[Auto-Format] OK: {}", basename);
        None
    } else {
        Some((tool.to_string(), errors))
    }
}

// ── suggest-compact (edit counter + loop detection) ─────────────────

const LOOP_WINDOW_MS: u64 = 10 * 60 * 1000;
const LOOP_THRESHOLD: usize = 3;
const MAX_RECENT_EDITS: usize = 20;

fn update_edit_counter(file_path: &str) -> Option<String> {
    let counter_path = crate::io::state_dir().join("edit-counter.json");
    let mut counter = crate::io::read_json_state(&counter_path);

    let now = crate::io::now_secs() as u64;
    let now_ms = now * 1000;

    // Reset if older than 2 hours
    let last_reset = counter["lastReset"].as_u64().unwrap_or(now_ms);
    if now_ms - last_reset > 2 * 60 * 60 * 1000 {
        counter = serde_json::json!({"count": 0, "lastReset": now_ms, "recentEdits": []});
    }

    let count = counter["count"].as_u64().unwrap_or(0) + 1;
    counter["count"] = serde_json::json!(count);

    // Track recent edits for loop detection
    let mut recent: Vec<serde_json::Value> = counter["recentEdits"]
        .as_array()
        .cloned()
        .unwrap_or_default();
    recent.push(serde_json::json!({"file": file_path, "timestamp": now_ms}));

    // Prune stale + cap
    recent.retain(|e| {
        e["timestamp"].as_u64().unwrap_or(0) + LOOP_WINDOW_MS > now_ms
    });
    if recent.len() > MAX_RECENT_EDITS {
        recent = recent[recent.len() - MAX_RECENT_EDITS..].to_vec();
    }

    // Check for loop
    let loop_count = recent
        .iter()
        .filter(|e| e["file"].as_str() == Some(file_path))
        .count();

    counter["recentEdits"] = serde_json::json!(recent);
    crate::io::write_json_state(&counter_path, &counter);

    // Stderr warnings at thresholds
    if count == 30 {
        eprintln!("[Token] 30 edits in this session. Consider compacting context if response quality degrades.");
    } else if count == 50 {
        eprintln!("[Token] 50 edits reached. Strongly recommend delegating to subagents or compacting.");
    }

    if loop_count >= LOOP_THRESHOLD {
        let basename = Path::new(file_path)
            .file_name()
            .map(|n| n.to_string_lossy().to_string())
            .unwrap_or_default();
        Some(format!(
            "[Loop Detection] {} が {} 回編集されています（10分以内）。\
             修正ループの可能性があります。このファイルへの編集を一旦停止し、アプローチを見直してください。\
             この警告は情報提供であり、修正不要です。",
            basename, loop_count
        ))
    } else {
        None
    }
}

// ── golden-check ────────────────────────────────────────────────────

const WARNING_COOLDOWN: f64 = 300.0;

fn is_duplicate_warning(file_path: &str, rule: &str) -> bool {
    let state_path = crate::io::state_dir().join("golden-warnings.json");
    let mut state = crate::io::read_json_state(&state_path);
    let now = crate::io::now_secs();
    let key = format!("{}:{}", file_path, rule);

    let last = state[&key].as_f64().unwrap_or(0.0);
    if now - last < WARNING_COOLDOWN {
        return true;
    }

    // Prune old entries
    let obj = state.as_object_mut();
    if let Some(obj) = obj {
        obj.retain(|_, v| now - v.as_f64().unwrap_or(0.0) < WARNING_COOLDOWN);
        obj.insert(key, serde_json::json!(now));
    }
    crate::io::write_json_state(&state_path, &state);
    false
}

fn strip_comments(content: &str, ext: &str) -> String {
    match ext {
        "py" => content
            .lines()
            .filter(|l| !l.trim_start().starts_with('#'))
            .collect::<Vec<_>>()
            .join("\n"),
        "ts" | "tsx" | "js" | "jsx" | "go" => content
            .lines()
            .filter(|l| !l.trim_start().starts_with("//"))
            .collect::<Vec<_>>()
            .join("\n"),
        _ => content.to_string(),
    }
}

/// Paths excluded from golden principles checks.
/// Infrastructure, docs, and config files generate false positives (CRIT-004).
/// NOTE: `/scripts/` was previously excluded entirely, but this silenced legitimate
/// GP-004 violations in harness scripts. Now only non-code infra paths are excluded.
const GP_EXCLUDE_PATTERNS: &[&str] = &[
    "/.worktrees/",
    "/agent-memory/",
    "/node_modules/",
    "/.git/",
];

const GP_EXCLUDE_EXTENSIONS: &[&str] = &["md", "mdc", "toml", "yml", "yaml", "txt", "rst"];

fn is_gp_excluded(file_path: &str) -> bool {
    // Check path patterns
    if GP_EXCLUDE_PATTERNS
        .iter()
        .any(|pat| file_path.contains(pat))
    {
        return true;
    }
    // Check file extensions
    let ext = Path::new(file_path)
        .extension()
        .map(|e| e.to_string_lossy().to_lowercase())
        .unwrap_or_default();
    GP_EXCLUDE_EXTENSIONS.contains(&ext.as_str())
}

/// Simple string similarity ratio (2 * matching_chars / total_chars).
/// Approximates Python's SequenceMatcher.ratio().
fn similarity_ratio(a: &str, b: &str) -> f64 {
    if a.is_empty() && b.is_empty() {
        return 1.0;
    }
    if a.is_empty() || b.is_empty() {
        return 0.0;
    }
    let a_chars: Vec<char> = a.chars().collect();
    let b_chars: Vec<char> = b.chars().collect();
    let len_a = a_chars.len();
    let len_b = b_chars.len();
    // LCS length via DP
    let mut dp = vec![vec![0usize; len_b + 1]; len_a + 1];
    for i in 1..=len_a {
        for j in 1..=len_b {
            dp[i][j] = if a_chars[i - 1] == b_chars[j - 1] {
                dp[i - 1][j - 1] + 1
            } else {
                dp[i - 1][j].max(dp[i][j - 1])
            };
        }
    }
    2.0 * dp[len_a][len_b] as f64 / (len_a + len_b) as f64
}

fn check_golden_principles(content: &str, file_path: &str, tool_name: &str, old_string: Option<&str>) -> Vec<String> {
    if is_gp_excluded(file_path) {
        return Vec::new();
    }

    let ext = Path::new(file_path)
        .extension()
        .map(|e| e.to_string_lossy().to_lowercase())
        .unwrap_or_default();

    let mut warnings = Vec::new();

    // GP-002: Boundary validation
    let filtered = strip_comments(content, &ext);
    let raw_input_patterns: Vec<Regex> = match ext.as_str() {
        "ts" | "tsx" | "js" | "jsx" => vec![
            Regex::new(r"req\.body\[").unwrap(),
            Regex::new(r"req\.query\[").unwrap(),
            Regex::new(r"req\.params\[").unwrap(),
            Regex::new(r"request\.body\[").unwrap(),
        ],
        "py" => vec![
            Regex::new(r"sys\.argv\[").unwrap(),
            Regex::new(r"request\.form\[").unwrap(),
            Regex::new(r"request\.args\[").unwrap(),
            Regex::new(r"request\.json\[").unwrap(),
        ],
        "go" => vec![
            Regex::new(r"os\.Args\[").unwrap(),
            Regex::new(r"r\.URL\.Query\(\)\.Get\(").unwrap(),
            Regex::new(r"r\.FormValue\(").unwrap(),
        ],
        _ => vec![],
    };
    if raw_input_patterns.iter().any(|p| p.is_match(&filtered))
        && !is_duplicate_warning(file_path, "GP-002")
    {
        let msg = "[GP-002] 外部入力の直接使用が検出されました。バウンダリでバリデーションを行ってください（Zod, Pydantic 等）。";
        warnings.push(msg.to_string());
        crate::events::emit_event("quality", &serde_json::json!({"rule": "GP-002", "file": file_path}));
    }

    // GP-003: Dependency files
    let dep_files = [
        "package.json", "go.mod", "Cargo.toml", "requirements.txt", "pyproject.toml",
    ];
    let basename = Path::new(file_path)
        .file_name()
        .map(|n| n.to_string_lossy().to_string())
        .unwrap_or_default();
    if dep_files.contains(&basename.as_str()) && !is_duplicate_warning(file_path, "GP-003") {
        let msg = format!(
            "[GP-003] 依存ファイル `{}` が変更されました。新規依存の追加は慎重に — 退屈な技術を好む原則を確認してください。",
            basename
        );
        warnings.push(msg);
        crate::events::emit_event("quality", &serde_json::json!({"rule": "GP-003", "file": file_path}));
    }

    // GP-004, GP-005 are enforced as BLOCK in pre_tool.rs (with emit_event)

    // GP-009: Ghost file detection (Write only)
    if tool_name == "Write" && !Path::new(file_path).exists() {
        if let Some(dir) = Path::new(file_path).parent() {
            if dir.is_dir() {
                let new_stem = Path::new(file_path)
                    .file_stem()
                    .map(|s| s.to_string_lossy().to_lowercase())
                    .unwrap_or_default();
                if let Ok(entries) = std::fs::read_dir(dir) {
                    for entry in entries.flatten() {
                        let existing = entry.file_name().to_string_lossy().to_string();
                        let existing_stem = Path::new(&existing)
                            .file_stem()
                            .map(|s| s.to_string_lossy().to_lowercase())
                            .unwrap_or_default();
                        if existing_stem != new_stem && similarity_ratio(&new_stem, &existing_stem) > 0.7 {
                            if !is_duplicate_warning(file_path, "GP-009") {
                                let msg = format!(
                                    "[GP-009] 類似名のファイル `{}` が同ディレクトリに存在します。新規作成ではなく既存ファイルの修正を検討してください。",
                                    existing
                                );
                                warnings.push(msg);
                                crate::events::emit_event("quality", &serde_json::json!({"rule": "GP-009", "file": file_path}));
                            }
                            break;
                        }
                    }
                }
            }
        }
    }

    // GP-010: Comment ratio (Write only — Edit の new_string はスニペットなので false positive になる)
    let comment_skip_exts = ["md", "txt", "json", "yaml", "yml", "toml"];
    if tool_name == "Write" && !comment_skip_exts.contains(&ext.as_str()) {
        let lines: Vec<&str> = content.lines().filter(|l| !l.trim().is_empty()).collect();
        if lines.len() >= 20 {
            let markers: &[&str] = match ext.as_str() {
                "py" | "sh" | "bash" => &["#"],
                "ts" | "tsx" | "js" | "jsx" | "go" | "rs" => &["//"],
                _ => &["//", "#"],
            };
            let comment_count = lines.iter().filter(|l| {
                let trimmed = l.trim_start();
                markers.iter().any(|m| trimmed.starts_with(m))
            }).count();
            let ratio = comment_count as f64 / lines.len() as f64;
            if ratio > 0.4 && !is_duplicate_warning(file_path, "GP-010") {
                let pct = (ratio * 100.0) as u32;
                let msg = format!(
                    "[GP-010] コメント比率が {}% と高すぎます（閾値: 40%）。コードが自己文書化されるよう、冗長なコメントを削除してください。",
                    pct
                );
                warnings.push(msg);
                crate::events::emit_event("quality", &serde_json::json!({"rule": "GP-010", "file": file_path}));
            }
        }
    }

    // GP-011: Breaking change detection (Edit only)
    if tool_name == "Edit" {
        let old_str = old_string.unwrap_or("");
        if !old_str.is_empty() && matches!(ext.as_str(), "ts" | "tsx" | "js" | "jsx") {
            let export_re = Regex::new(r"(?m)^export\s+(?:default\s+)?(?:function|const|type|interface|class|enum)\s+\w+").unwrap();
            let old_exports: Vec<&str> = export_re.find_iter(old_str).map(|m| m.as_str()).collect();
            if !old_exports.is_empty() {
                let new_exports: Vec<&str> = export_re.find_iter(content).map(|m| m.as_str()).collect();
                let changed: Vec<&&str> = old_exports.iter().filter(|e| !new_exports.contains(e)).collect();
                if !changed.is_empty() && !is_duplicate_warning(file_path, "GP-011") {
                    let preview: String = changed[0].chars().take(80).collect();
                    let msg = format!(
                        "[GP-011] export されたシグネチャの変更を検出: `{}`。呼び出し元への影響を確認してください（`git grep` で参照元を検索）。",
                        &preview
                    );
                    warnings.push(msg);
                    crate::events::emit_event("quality", &serde_json::json!({"rule": "GP-011", "file": file_path}));
                }
            }
        }
    }

    warnings
}

// ── checkpoint-manager ──────────────────────────────────────────────

const EDIT_THRESHOLD: u64 = 15;
const TIME_THRESHOLD: f64 = 30.0 * 60.0;
const CHECKPOINT_COOLDOWN: f64 = 5.0 * 60.0;
const MAX_CHECKPOINTS: usize = 5;

fn check_checkpoint(file_path: &str) -> Option<String> {
    let state_dir = crate::io::state_dir();
    let counter_path = state_dir.join("edit-counter.json");
    let last_cp_path = state_dir.join("last-checkpoint.json");

    let counter = crate::io::read_json_state(&counter_path);
    let now = crate::io::now_secs();

    let last_cp_time = crate::io::read_json_state(&last_cp_path)["timestamp"]
        .as_str()
        .and_then(|ts| {
            // Parse ISO timestamp to epoch (approximate)
            // Just check if it exists and is recent
            Some(ts)
        })
        .map(|_| {
            std::fs::metadata(&last_cp_path)
                .ok()
                .and_then(|m| m.modified().ok())
                .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
                .map(|d| d.as_secs_f64())
                .unwrap_or(0.0)
        })
        .unwrap_or(0.0);

    if last_cp_time > 0.0 && now - last_cp_time < CHECKPOINT_COOLDOWN {
        return None;
    }

    let edit_count = counter["count"].as_u64().unwrap_or(0);

    let trigger = if edit_count >= EDIT_THRESHOLD {
        "auto:edit_threshold"
    } else if last_cp_time > 0.0 && now - last_cp_time >= TIME_THRESHOLD {
        "auto:time_threshold"
    } else if last_cp_time == 0.0 {
        let session_start = counter["lastReset"].as_u64().unwrap_or((now * 1000.0) as u64) as f64 / 1000.0;
        if now - session_start >= TIME_THRESHOLD {
            "auto:time_threshold"
        } else {
            return None;
        }
    } else {
        return None;
    };

    // Save checkpoint
    let cp_dir = state_dir.join("checkpoints");
    let _ = std::fs::create_dir_all(&cp_dir);

    let branch = std::process::Command::new("git")
        .args(["--no-optional-locks", "branch", "--show-current"])
        .output()
        .ok()
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
        .unwrap_or_default();

    let ts = crate::io::iso_now();
    let cp_data = serde_json::json!({
        "timestamp": ts,
        "trigger": trigger,
        "branch": branch,
        "edit_count": edit_count,
        "focus": [file_path],
    });

    let filename = format!("checkpoint-{}.json", ts.replace(':', ""));
    let _ = std::fs::write(
        cp_dir.join(&filename),
        serde_json::to_string_pretty(&cp_data).unwrap_or_default(),
    );
    let _ = std::fs::write(
        &last_cp_path,
        serde_json::to_string_pretty(&cp_data).unwrap_or_default(),
    );

    // Cleanup old checkpoints
    if let Ok(entries) = std::fs::read_dir(&cp_dir) {
        let mut files: Vec<PathBuf> = entries
            .filter_map(|e| e.ok())
            .map(|e| e.path())
            .filter(|p| p.file_name().map(|n| n.to_string_lossy().starts_with("checkpoint-")).unwrap_or(false))
            .collect();
        files.sort();
        while files.len() > MAX_CHECKPOINTS {
            if let Some(old) = files.first() {
                let _ = std::fs::remove_file(old);
            }
            files.remove(0);
        }
    }

    Some(format!(
        "[Checkpoint] セッション状態を保存しました (trigger: {}, edits: {})",
        trigger, edit_count
    ))
}

// ── edit-failure-tracker (merged from edit-failure-tracker.py) ───────

fn classify_edit_failure(content: &str) -> &'static str {
    let c = content.to_lowercase();
    if c.contains("not found in file") || c.contains("not unique") {
        "str_replace_mismatch"
    } else if c.contains("whitespace") || c.contains("indentation") {
        "whitespace_mismatch"
    } else if c.contains("no such file") || c.contains("does not exist") {
        "file_not_found"
    } else if c.contains("permission") {
        "permission_denied"
    } else if c.contains("read") && c.contains("first") {
        "read_before_edit"
    } else {
        "other"
    }
}

fn track_edit_failure(tool_name: &str, file_path: &str, data: &serde_json::Value) {
    let is_error = data["tool_result"]["is_error"].as_bool().unwrap_or(false);
    if !is_error {
        return;
    }

    let result_content = data["tool_result"]["content"]
        .as_str()
        .unwrap_or("");
    let pattern = classify_edit_failure(result_content);
    let ext = Path::new(file_path)
        .extension()
        .map(|e| e.to_string_lossy().to_string())
        .unwrap_or_default();

    crate::events::emit_event(
        "error",
        &serde_json::json!({
            "message": format!("{} failed: {}", tool_name, &result_content[..result_content.len().min(200)]),
            "tool_name": tool_name,
            "file_path": file_path,
            "file_ext": ext,
            "failure_pattern": pattern,
            "failure_mode": "FM-016",
            "failure_type": "tool_interface",
        }),
    );
}

// ── main entry ──────────────────────────────────────────────────────

pub fn run(raw: &str, data: &serde_json::Value) -> Result<(), String> {
    let tool_name = data["tool_name"].as_str().unwrap_or("");
    let file_path = data["tool_input"]["file_path"]
        .as_str()
        .unwrap_or("");

    // Track edit failures (side effect: emits event on failure)
    track_edit_failure(tool_name, file_path, data);

    let content = if tool_name == "Write" {
        data["tool_input"]["content"].as_str().unwrap_or("")
    } else {
        data["tool_input"]["new_string"].as_str().unwrap_or("")
    };
    let content = if content.is_empty() {
        data["tool_output"].as_str().unwrap_or("")
    } else {
        content
    };

    let mut contexts: Vec<String> = Vec::new();

    // 1. Auto-format (side effect: modifies file on disk)
    if let Some((tool, errors)) = auto_format(file_path) {
        let basename = Path::new(file_path)
            .file_name()
            .map(|n| n.to_string_lossy().to_string())
            .unwrap_or_default();
        eprintln!("[Auto-Lint] {}: {} issue(s) in {}", tool, errors.len(), basename);
        let mut parts = vec![format!(
            "[Auto-Lint] {} が {} で問題を検出:",
            tool, basename
        )];
        parts.push(String::new());
        for e in &errors {
            parts.push(format!("  {}", e));
        }
        parts.push(String::new());
        parts.push("FIX: 上記の lint エラーを修正してください。リンター設定は変更せず、コードを修正すること。".to_string());
        contexts.push(parts.join("\n"));
    }

    // 2. Edit counter + loop detection (side effect: updates state file)
    if let Some(ctx) = update_edit_counter(file_path) {
        contexts.push(ctx);
    }

    // 3. Golden principles check (side effect: emits events)
    let old_string = data["tool_input"]["old_string"].as_str();
    let gp_warnings = check_golden_principles(content, file_path, tool_name, old_string);
    if !gp_warnings.is_empty() {
        let mut all = gp_warnings;
        all.push("golden-cleanup エージェントで詳細なプリンシプルスキャンを実行できます。".to_string());
        contexts.push(all.join("\n"));
    }

    // 4. Checkpoint check (side effect: saves checkpoint)
    if let Some(ctx) = check_checkpoint(file_path) {
        contexts.push(ctx);
    }

    if contexts.is_empty() {
        crate::io::passthrough(raw);
    } else {
        crate::io::context("PostToolUse", &contexts.join("\n\n"));
    }

    Ok(())
}
