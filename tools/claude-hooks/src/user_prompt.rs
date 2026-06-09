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
    "毎朝", "毎日", "スケジュール", "schedule", "フォローアップ", "follow.?up",
];

fn match_keywords(text: &str, keywords: &[&str]) -> Vec<String> {
    let text_lower = text.to_lowercase();
    keywords
        .iter()
        .filter(|kw| text_lower.contains(&kw.to_lowercase()))
        .map(|kw| kw.to_string())
        .collect()
}

fn match_regex_keywords(text: &str, patterns: &[&str]) -> Vec<String> {
    patterns
        .iter()
        .filter(|p| {
            Regex::new(&format!("(?i){}", p))
                .map(|re| re.is_match(text))
                .unwrap_or(false)
        })
        .map(|p| p.to_string())
        .collect()
}

fn multimodal_regex() -> Regex {
    Regex::new(
        r"(?i)\.(pdf|mp4|mov|avi|mkv|webm|mp3|wav|m4a|flac|ogg|png|jpe?g|gif|webp|svg)(?:[^a-zA-Z0-9]|$)",
    )
    .unwrap()
}

fn log_routing(suggested: &str, keywords: &[String], prompt: &str) {
    let matched: Vec<&String> = keywords.iter().take(3).collect();
    crate::events::emit_event(
        "agent_routing",
        &serde_json::json!({
            "suggested": suggested,
            "keywords_matched": matched,
            "prompt_length": prompt.chars().count(),
        }),
    );
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
    if let Some(caps) = multimodal_regex().captures(prompt) {
        let ext = caps.get(1).map(|m| m.as_str()).unwrap_or("");
        log_routing("multimodal", &[ext.to_string()], prompt);
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
        log_routing("codex", &keywords, prompt);
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
        log_routing("gemini", &keywords, prompt);
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
    let scheduled = match_regex_keywords(prompt, SCHEDULED_KEYWORDS);
    if !scheduled.is_empty() {
        log_routing("scheduled", &scheduled, prompt);
        crate::io::context(
            "UserPromptSubmit",
            "Scheduled パターン推奨: このタスクは将来の時刻に実行すると効果的です。\
             CronCreate ツールまたは /loop スキルの使用を検討してください。\
             実行時のライブデータで分析するため、単なるリマインダーより有用です。",
        );
        return Ok(());
    }

    // Priority 5: Async
    let async_matched = match_regex_keywords(prompt, ASYNC_KEYWORDS);
    if !async_matched.is_empty() {
        log_routing("async", &async_matched, prompt);
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn multimodal_detects_pdf() {
        assert!(multimodal_regex().is_match("この report.pdf を読んで"));
    }

    #[test]
    fn multimodal_detects_image() {
        assert!(multimodal_regex().is_match("screenshot.png を確認"));
    }

    #[test]
    fn multimodal_detects_video_and_audio() {
        let re = multimodal_regex();
        assert!(re.is_match("clip.mp4 を変換"));
        assert!(re.is_match("track.mp3 を再生"));
    }

    #[test]
    fn multimodal_case_insensitive() {
        assert!(multimodal_regex().is_match("DOC.PDF を開く"));
    }

    #[test]
    fn multimodal_rejects_embedded() {
        assert!(!multimodal_regex().is_match("notapdfx"));
    }

    #[test]
    fn match_keywords_japanese() {
        let m = match_keywords("このAPIの設計を考えて", CODEX_KEYWORDS_JA);
        assert!(m.contains(&"設計".to_string()));
    }

    #[test]
    fn match_keywords_english() {
        let m = match_keywords("design the architecture", CODEX_KEYWORDS_EN);
        assert!(m.contains(&"design".to_string()));
    }

    #[test]
    fn match_keywords_english_case_insensitive() {
        let m = match_keywords("DEBUG this", CODEX_KEYWORDS_EN);
        assert!(m.contains(&"debug".to_string()));
    }

    #[test]
    fn match_keywords_gemini_research() {
        let m = match_keywords("リサーチして", GEMINI_KEYWORDS_JA);
        assert!(m.contains(&"リサーチ".to_string()));
    }

    #[test]
    fn match_keywords_no_match() {
        assert!(match_keywords("hello world", CODEX_KEYWORDS_JA).is_empty());
    }

    #[test]
    fn regex_keywords_scheduled() {
        assert!(!match_regex_keywords("明日やって", SCHEDULED_KEYWORDS).is_empty());
    }

    #[test]
    fn regex_keywords_followup_optional_separator() {
        assert!(!match_regex_keywords("please follow-up", SCHEDULED_KEYWORDS).is_empty());
        assert!(!match_regex_keywords("followup later", SCHEDULED_KEYWORDS).is_empty());
    }

    #[test]
    fn regex_keywords_async() {
        assert!(!match_regex_keywords("バックグラウンドで実行", ASYNC_KEYWORDS).is_empty());
    }

    #[test]
    fn regex_keywords_case_insensitive() {
        assert!(!match_regex_keywords("PARALLEL run", ASYNC_KEYWORDS).is_empty());
    }

    #[test]
    fn regex_keywords_no_match() {
        assert!(match_regex_keywords("普通の依頼", SCHEDULED_KEYWORDS).is_empty());
    }
}
