//! PreToolUse handlers — consolidates:
//! pre-bash (git add -A block), pre-edit (protect-linter + search-first),
//! pre-search (search-first mark), pre-websearch (suggest-gemini), pre-commit (secret check)

use regex::Regex;
use std::path::Path;

// ── pre-bash: block git add -A/--all/. ──────────────────────────────

pub fn pre_bash(data: &serde_json::Value) -> Result<(), String> {
    let command = data["tool_input"]["command"].as_str().unwrap_or("");
    let re = Regex::new(r"git\s+add\s+(-A|--all|\.\s*$|\.\s)").unwrap();
    if re.is_match(command) {
        crate::io::deny(
            "一括追加は禁止です。ファイルを個別に確認し、必要なものだけ追加してください",
        );
    }
    Ok(())
}

// ── pre-edit: protect-linter-config + search-first-gate ─────────────

const BLOCKED_FILES: &[&str] = &[
    ".eslintrc", ".eslintrc.js", ".eslintrc.cjs", ".eslintrc.json", ".eslintrc.yml",
    "eslint.config.js", "eslint.config.mjs", "eslint.config.ts",
    "biome.json", "biome.jsonc",
    ".prettierrc", ".prettierrc.js", ".prettierrc.cjs", ".prettierrc.json", ".prettierrc.yml",
    "prettier.config.js", "prettier.config.mjs",
    ".oxlintrc.json", ".swiftlint.yml",
    ".golangci.yml", ".golangci.yaml",
    ".markdownlint.json", ".markdownlint.yaml",
    ".stylelintrc", ".stylelintrc.json",
];

const MIXED_FILES: &[(&str, &[&str])] = &[
    ("pyproject.toml", &["[tool.ruff", "[tool.black", "[tool.isort", "[tool.pylint", "[tool.mypy"]),
    ("Cargo.toml", &["[lints", "[lints.clippy", "[lints.rust"]),
];

fn check_protect_linter(data: &serde_json::Value) -> Option<String> {
    let file_path = data["tool_input"]["file_path"]
        .as_str()
        .or_else(|| data["tool_input"]["path"].as_str())
        .unwrap_or("");

    if file_path.is_empty() {
        return None;
    }

    let basename = Path::new(file_path)
        .file_name()
        .map(|n| n.to_string_lossy().to_string())
        .unwrap_or_default();

    // Pure linter configs — always block
    if BLOCKED_FILES.contains(&basename.as_str()) {
        let reason = format!(
            "BLOCKED: `{}` はリンター/フォーマッター設定ファイルです。\n\
             コードを修正してください。リンター設定を変更してはいけません。\n\
             WHY: エージェントが lint 違反をコード修正ではなく設定変更で回避するのを防止するため。",
            basename
        );
        crate::io::deny(&reason);
    }

    // Mixed-use files — block linter sections only
    for (filename, patterns) in MIXED_FILES {
        if basename == *filename && !patterns.is_empty() {
            let new_string = data["tool_input"]["new_string"].as_str().unwrap_or("");
            let content = data["tool_input"]["content"].as_str().unwrap_or("");
            let old_string = data["tool_input"]["old_string"].as_str().unwrap_or("");
            let edit_content = format!("{}\n{}\n{}", old_string, new_string, content);

            for pattern in *patterns {
                if edit_content.contains(pattern) {
                    let reason = format!(
                        "BLOCKED: `{}` のリンター設定セクション ({}) を変更しようとしています。\n\
                         コードを修正してください。リンター設定を変更してはいけません。",
                        basename, pattern
                    );
                    crate::io::deny(&reason);
                }
            }
        }
    }

    None
}

const SESSION_TTL: f64 = 2.0 * 60.0 * 60.0;

fn check_search_first_edit(data: &serde_json::Value) -> Option<String> {
    let state_path = crate::io::state_dir().join("search-first.json");
    let mut state = crate::io::read_json_state(&state_path);
    let now = crate::io::now_secs();

    // Reset if session expired
    let started = state["started"].as_f64().unwrap_or(0.0);
    if now - started > SESSION_TTL || started == 0.0 {
        state = serde_json::json!({"started": now, "searched": false, "warned": false});
    }

    if state["searched"].as_bool().unwrap_or(false) || state["warned"].as_bool().unwrap_or(false) {
        return None;
    }

    let file_path = data["tool_input"]["file_path"].as_str().unwrap_or("");
    let ext = Path::new(file_path)
        .extension()
        .map(|e| e.to_string_lossy().to_lowercase())
        .unwrap_or_default();

    // Skip non-code files
    if ["md", "json", "yaml", "yml", "toml", "txt", ""].contains(&ext.as_str()) {
        return None;
    }

    state["warned"] = serde_json::json!(true);
    crate::io::write_json_state(&state_path, &state);

    Some(
        "[Search-First] このセッションでまだ検索（Grep/Glob）が実行されていません。\
         既存コードを確認してから編集することを推奨します。\
         この警告はセッション中1回のみ表示されます。"
            .to_string(),
    )
}

pub fn pre_edit(_raw: &str, data: &serde_json::Value) -> Result<(), String> {
    // protect-linter-config (may call deny → exit 2)
    check_protect_linter(data);

    // search-first-gate
    if let Some(ctx) = check_search_first_edit(data) {
        crate::io::context("PreToolUse", &ctx);
    }
    // If no context was output, no stdout is needed for PreToolUse allow

    Ok(())
}

// ── pre-search: mark as searched ────────────────────────────────────

pub fn pre_search(data: &serde_json::Value) -> Result<(), String> {
    let tool_name = data["tool_name"].as_str().unwrap_or("");
    if ["Grep", "Glob", "Read"].contains(&tool_name) {
        let state_path = crate::io::state_dir().join("search-first.json");
        let mut state = crate::io::read_json_state(&state_path);
        let now = crate::io::now_secs();

        let started = state["started"].as_f64().unwrap_or(0.0);
        if now - started > SESSION_TTL || started == 0.0 {
            state = serde_json::json!({"started": now, "searched": true, "warned": false});
        } else {
            state["searched"] = serde_json::json!(true);
        }
        crate::io::write_json_state(&state_path, &state);
    }
    Ok(())
}

// ── pre-websearch: suggest gemini ───────────────────────────────────

const SIMPLE_QUERIES: &[&str] = &[
    "error message", "version", "changelog", "release notes",
    "stackoverflow", "github issue", "npm package",
    "エラーメッセージ", "バージョン", "リリースノート",
];

const RESEARCH_KEYWORDS: &[&str] = &[
    "documentation", "best practice", "comparison", "vs",
    "library", "framework", "tutorial", "guide",
    "architecture", "migration", "upgrade", "pattern",
    "api reference", "specification", "benchmark",
    "ドキュメント", "ベストプラクティス", "比較",
    "ライブラリ", "フレームワーク", "チュートリアル",
    "アーキテクチャ", "マイグレーション", "パターン",
];

pub fn pre_websearch(_raw: &str, data: &serde_json::Value) -> Result<(), String> {
    let query = data["tool_input"]["query"].as_str().unwrap_or("");
    if query.is_empty() {
        return Ok(());
    }

    let q_lower = query.to_lowercase();

    // Skip simple queries
    if SIMPLE_QUERIES.iter().any(|sq| q_lower.contains(sq)) {
        return Ok(());
    }

    // Suggest Gemini for research queries
    let is_research = RESEARCH_KEYWORDS.iter().any(|rk| q_lower.contains(rk)) || query.len() > 100;

    if is_research {
        crate::io::context(
            "PreToolUse",
            "[Suggest-Gemini] 複雑なリサーチが検出されました。\
             Gemini CLI (1Mコンテキスト + Google Search grounding) の方が\
             より包括的な結果を得られる可能性があります。\n\
             gemini-explore エージェントまたは gemini スキルの使用を検討してください。\n\
             結果は .claude/docs/research/ に保存できます。",
        );
    }

    Ok(())
}

// ── pre-commit: secret detection ────────────────────────────────────

const SECRET_PATTERNS: &[&str] = &[
    r"sk-[a-zA-Z0-9]{20,}",
    r"ghp_[a-zA-Z0-9]{36,}",
    r"AKIA[A-Z0-9]{16}",
    r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----",
];

pub fn pre_commit(raw: &str, data: &serde_json::Value) -> Result<(), String> {
    let command = data["tool_input"]["command"].as_str().unwrap_or("");

    // Get staged diff to check for secrets
    let diff = std::process::Command::new("git")
        .args(["diff", "--cached", "--diff-filter=ACM"])
        .output()
        .ok()
        .map(|o| String::from_utf8_lossy(&o.stdout).to_string())
        .unwrap_or_default();

    if diff.is_empty() {
        crate::io::passthrough(raw);
        return Ok(());
    }

    for pattern_str in SECRET_PATTERNS {
        if let Ok(re) = Regex::new(pattern_str) {
            if re.is_match(&diff) {
                crate::io::deny(&format!(
                    "BLOCKED: コミットにシークレットが含まれている可能性があります (pattern: {})\n\
                     機密情報をコミットしないでください。該当ファイルを確認し、シークレットを削除してから再度コミットしてください。",
                    pattern_str
                ));
            }
        }
    }

    // Check commit message format (conventional commit)
    let msg_match = Regex::new(r#"-m\s+["']([^"']+)["']"#)
        .ok()
        .and_then(|re| re.captures(command))
        .and_then(|c| c.get(1))
        .map(|m| m.as_str().to_string());

    if let Some(msg) = &msg_match {
        let conventional = Regex::new(
            r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?!?:\s"
        ).unwrap();
        if !conventional.is_match(msg) {
            crate::io::context(
                "PreToolUse",
                "[Pre-Commit] コミットメッセージが Conventional Commit 形式に従っていません。\n\
                 形式: <type>(<scope>): <description>\n\
                 例: feat: add user authentication",
            );
            return Ok(());
        }
    }

    crate::io::passthrough(raw);
    Ok(())
}
