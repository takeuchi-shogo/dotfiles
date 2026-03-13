//! UserPromptSubmit — agent-router: keyword detection for Codex/Gemini/Async/Scheduled delegation

use regex::Regex;

const CODEX_KEYWORDS_JA: &[&str] = &[
    "設計", "アーキテクチャ", "どう実装", "どうすべき", "トレードオフ",
    "比較して", "どちらがいい", "なぜ動かない", "原因", "バグ",
    "デバッグ", "リファクタ", "最適化", "パフォーマンス",
];

const CODEX_KEYWORDS_EN: &[&str] = &[
    "design", "architecture", "how to implement", "trade-off", "compare",
    "which is better", "root cause", "bug", "debug", "refactor",
    "optimize", "performance",
];

const GEMINI_KEYWORDS_JA: &[&str] = &[
    "調べて", "リサーチ", "調査して", "検索して", "コードベース全体",
    "リポジトリ全体", "全体を分析", "ライブラリ", "ベストプラクティス",
    "ドキュメント", "読んで", "読み取って", "内容を確認",
];

const GEMINI_KEYWORDS_EN: &[&str] = &[
    "research", "investigate", "look up", "search for", "entire codebase",
    "whole repository", "analyze all", "library", "best practice",
    "documentation", "read this", "extract from",
];

const ASYNC_KEYWORDS: &[&str] = &[
    "バックグラウンド", "background", "並列", "parallel",
    "レポート", "report", "分析して", "analyze",
];

const SCHEDULED_KEYWORDS: &[&str] = &[
    "あとで", "later", "明日", "tomorrow", "定期的", "recurring",
    "毎朝", "毎日", "スケジュール", "schedule", "フォローアップ",
];

fn match_keywords(text: &str, keywords: &[&str]) -> Vec<String> {
    let text_lower = text.to_lowercase();
    keywords
        .iter()
        .filter(|kw| text_lower.contains(&kw.to_lowercase()))
        .map(|kw| kw.to_string())
        .collect()
}

fn match_regex_keywords(text: &str, patterns: &[&str]) -> bool {
    patterns.iter().any(|p| {
        Regex::new(&format!("(?i){}", p))
            .map(|re| re.is_match(text))
            .unwrap_or(false)
    })
}

pub fn run(raw: &str, data: &serde_json::Value) -> Result<(), String> {
    let prompt = data["user_prompt"]
        .as_str()
        .or_else(|| data["content"].as_str())
        .unwrap_or("");

    if prompt.is_empty() || prompt.len() < 10 {
        crate::io::passthrough(raw);
        return Ok(());
    }

    // Priority 1: Multimodal files → Gemini
    let mm_re = Regex::new(
        r"(?i)\.(pdf|mp4|mov|avi|mkv|webm|mp3|wav|m4a|flac|ogg|png|jpe?g|gif|webp|svg)(?:[^a-zA-Z0-9]|$)"
    ).unwrap();

    if let Some(caps) = mm_re.captures(prompt) {
        let ext = caps.get(1).map(|m| m.as_str()).unwrap_or("");
        crate::io::context(
            "UserPromptSubmit",
            &format!(
                "[Agent Router] マルチモーダルファイル (.{}) が検出されました。\
                 Gemini CLI (1Mコンテキスト) での処理を推奨します。\
                 gemini-explore エージェントまたは gemini スキルを使用してください。",
                ext
            ),
        );
        return Ok(());
    }

    // Priority 2: Codex keywords
    let mut codex_matches = match_keywords(prompt, CODEX_KEYWORDS_JA);
    codex_matches.extend(match_keywords(prompt, CODEX_KEYWORDS_EN));
    if !codex_matches.is_empty() {
        let keywords: Vec<String> = codex_matches.into_iter().take(3).collect();
        crate::io::context(
            "UserPromptSubmit",
            &format!(
                "[Agent Router] 設計/推論キーワード ({}) が検出されました。\
                 Codex CLI での深い分析を検討してください。\
                 codex スキル、codex-debugger エージェント、または直接 codex exec で実行できます。",
                keywords.join(", ")
            ),
        );
        return Ok(());
    }

    // Priority 3: Gemini keywords
    let mut gemini_matches = match_keywords(prompt, GEMINI_KEYWORDS_JA);
    gemini_matches.extend(match_keywords(prompt, GEMINI_KEYWORDS_EN));
    if !gemini_matches.is_empty() {
        let keywords: Vec<String> = gemini_matches.into_iter().take(3).collect();
        crate::io::context(
            "UserPromptSubmit",
            &format!(
                "[Agent Router] リサーチ/分析キーワード ({}) が検出されました。\
                 Gemini CLI (1Mコンテキスト + Google Search) での調査を検討してください。\
                 gemini-explore エージェントまたは gemini スキルを使用できます。",
                keywords.join(", ")
            ),
        );
        return Ok(());
    }

    // Priority 4: Scheduled
    if match_regex_keywords(prompt, SCHEDULED_KEYWORDS) {
        crate::io::context(
            "UserPromptSubmit",
            "Scheduled パターン推奨: このタスクは将来の時刻に実行すると効果的です。\
             CronCreate ツールまたは /loop スキルの使用を検討してください。\
             実行時のライブデータで分析するため、単なるリマインダーより有用です。",
        );
        return Ok(());
    }

    // Priority 5: Async
    if match_regex_keywords(prompt, ASYNC_KEYWORDS) {
        crate::io::context(
            "UserPromptSubmit",
            "Async パターン推奨: このタスクは独立して実行できます。\
             Agent(run_in_background=true) または /research スキルで\
             メインコンテキストを圧迫せず並列実行できます。",
        );
        return Ok(());
    }

    // No match
    crate::io::passthrough(raw);
    Ok(())
}
