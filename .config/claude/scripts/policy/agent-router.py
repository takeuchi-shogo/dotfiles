#!/usr/bin/env python3
"""Agent router hook — detects keywords in user input and suggests Codex/Gemini delegation.

Triggered by: hooks.UserPromptSubmit
Input: JSON with user prompt on stdin
Output: JSON with additionalContext suggestion on stdout
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import (  # noqa: E402
    load_hook_input,
    output_passthrough,
    output_context,
)


CODEX_KEYWORDS_JA = [
    "設計",
    "アーキテクチャ",
    "どう実装",
    "どうすべき",
    "トレードオフ",
    "比較して",
    "どちらがいい",
    "なぜ動かない",
    "原因",
    "バグ",
    "デバッグ",
    "リファクタ",
    "最適化",
    "パフォーマンス",
]

CODEX_KEYWORDS_EN = [
    "design",
    "architecture",
    "how to implement",
    "trade-off",
    "compare",
    "which is better",
    "why.*not working",
    "root cause",
    "bug",
    "debug",
    "refactor",
    "optimize",
    "performance",
]

GEMINI_KEYWORDS_JA = [
    "調べて",
    "リサーチ",
    "調査して",
    "検索して",
    "コードベース全体",
    "リポジトリ全体",
    "全体を分析",
    "ライブラリ",
    "ベストプラクティス",
    "ドキュメント",
    "読んで",
    "読み取って",
    "内容を確認",
]

GEMINI_KEYWORDS_EN = [
    "research",
    "investigate",
    "look up",
    "search for",
    "entire codebase",
    "whole repository",
    "analyze all",
    "library",
    "best practice",
    "documentation",
    "read this",
    "extract from",
]

# --- 委譲パターン推奨 ---
# NOTE: 「調べて」「リサーチ」「research」「investigate」は GEMINI_KEYWORDS と重複するため除外
# Gemini が Priority 3 で先にマッチするため、ここに含めても dead branch になる
ASYNC_KEYWORDS = [
    r"バックグラウンド",
    r"background",
    r"並列",
    r"parallel",
    r"レポート",
    r"report",
    r"分析して",
    r"analyze",
]

SCHEDULED_KEYWORDS = [
    r"あとで",
    r"later",
    r"明日",
    r"tomorrow",
    r"定期的",
    r"recurring",
    r"毎朝",
    r"毎日",
    r"スケジュール",
    r"schedule",
    r"フォローアップ",
    r"follow.?up",
]

MULTIMODAL_PATTERN = re.compile(
    r"\.(pdf|mp4|mov|avi|mkv|webm|mp3|wav|m4a|flac|ogg|png|jpe?g|gif|webp|svg)(?=[^a-zA-Z0-9]|$)",
    re.IGNORECASE,
)


def detect_multimodal(text: str) -> list[str]:
    return list(set(MULTIMODAL_PATTERN.findall(text)))


def match_keywords(text: str, keywords: list[str]) -> list[str]:
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]


def match_keywords_regex(text: str, patterns: list[str]) -> list[str]:
    """Match keywords using regex patterns (case-insensitive)."""
    matched = []
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            matched.append(pattern)
    return matched


def main() -> None:
    data = load_hook_input()
    if not data:
        return

    prompt = data.get("user_prompt", "") or data.get("content", "")
    if not prompt or len(prompt) < 10:
        output_passthrough(data)
        return

    # Priority 1: Multimodal files → Gemini
    mm_files = detect_multimodal(prompt)
    if mm_files:
        exts = ", ".join(f".{e}" for e in mm_files)
        output_context(
            "UserPromptSubmit",
            (
                f"[Agent Router] マルチモーダルファイル ({exts}) が検出されました。"
                "Gemini CLI (1Mコンテキスト) での処理を推奨します。"
                "gemini-explore エージェントまたは gemini スキルを使用してください。"
            ),
        )
        return

    # Priority 2: Codex keywords
    codex_matches = match_keywords(prompt, CODEX_KEYWORDS_JA + CODEX_KEYWORDS_EN)
    if codex_matches:
        keywords = ", ".join(codex_matches[:3])
        output_context(
            "UserPromptSubmit",
            (
                f"[Agent Router] 設計/推論キーワード ({keywords}) が検出されました。"
                "Codex CLI での深い分析を検討してください。"
                "codex スキル、codex-debugger エージェント、または直接 codex exec で実行できます。"
            ),
        )
        return

    # Priority 3: Gemini keywords
    gemini_matches = match_keywords(prompt, GEMINI_KEYWORDS_JA + GEMINI_KEYWORDS_EN)
    if gemini_matches:
        keywords = ", ".join(gemini_matches[:3])
        output_context(
            "UserPromptSubmit",
            (
                f"[Agent Router] リサーチ/分析キーワード ({keywords}) が検出されました。"
                "Gemini CLI (1Mコンテキスト + Google Search) での調査を検討してください。"
                "gemini-explore エージェントまたは gemini スキルを使用できます。"
            ),
        )
        return

    # Priority 4: Scheduled delegation pattern (takes precedence over async)
    scheduled_matches = match_keywords_regex(prompt, SCHEDULED_KEYWORDS)
    if scheduled_matches:
        output_context(
            "UserPromptSubmit",
            (
                "💡 Scheduled パターン推奨: このタスクは将来の時刻に実行すると効果的です。"
                "CronCreate ツールまたは /loop スキルの使用を検討してください。"
                "実行時のライブデータで分析するため、単なるリマインダーより有用です。"
            ),
        )
        return

    # Priority 5: Async delegation pattern
    async_matches = match_keywords_regex(prompt, ASYNC_KEYWORDS)
    if async_matches:
        output_context(
            "UserPromptSubmit",
            (
                "💡 Async パターン推奨: このタスクは独立して実行できます。"
                "Agent(run_in_background=true) または /research スキルで"
                "メインコンテキストを圧迫せず並列実行できます。"
            ),
        )
        return

    # No match — pass through
    output_passthrough(data)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Non-blocking — never prevent user input, but log for debugging
        import traceback

        sys.stderr.write(f"[agent-router] unexpected error: {e}\n")
        sys.stderr.write(traceback.format_exc())
