#!/usr/bin/env python3
from __future__ import annotations
"""Agent router hook — detects keywords in user input and suggests Codex/Gemini delegation.

Triggered by: hooks.UserPromptSubmit
Input: JSON with user prompt on stdin
Output: JSON with additionalContext suggestion on stdout
"""
import json
import re
import sys


CODEX_KEYWORDS_JA = [
    "設計", "アーキテクチャ", "どう実装", "どうすべき",
    "トレードオフ", "比較して", "どちらがいい",
    "なぜ動かない", "原因", "バグ", "デバッグ",
    "リファクタ", "最適化", "パフォーマンス",
]

CODEX_KEYWORDS_EN = [
    "design", "architecture", "how to implement", "trade-off",
    "compare", "which is better", "why.*not working", "root cause",
    "bug", "debug", "refactor", "optimize", "performance",
]

GEMINI_KEYWORDS_JA = [
    "調べて", "リサーチ", "調査して", "検索して",
    "コードベース全体", "リポジトリ全体", "全体を分析",
    "ライブラリ", "ベストプラクティス", "ドキュメント",
    "読んで", "読み取って", "内容を確認",
]

GEMINI_KEYWORDS_EN = [
    "research", "investigate", "look up", "search for",
    "entire codebase", "whole repository", "analyze all",
    "library", "best practice", "documentation",
    "read this", "extract from",
]

MULTIMODAL_PATTERN = re.compile(
    r'\.(pdf|mp4|mov|avi|mkv|webm|mp3|wav|m4a|flac|ogg|png|jpe?g|gif|webp|svg)(?=[^a-zA-Z0-9]|$)',
    re.IGNORECASE,
)


def detect_multimodal(text: str) -> list[str]:
    return list(set(MULTIMODAL_PATTERN.findall(text)))


def match_keywords(text: str, keywords: list[str]) -> list[str]:
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    prompt = data.get("user_prompt", "") or data.get("content", "")
    if not prompt or len(prompt) < 10:
        json.dump(data, sys.stdout)
        return

    # Priority 1: Multimodal files → Gemini
    mm_files = detect_multimodal(prompt)
    if mm_files:
        exts = ", ".join(f".{e}" for e in mm_files)
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": (
                    f"[Agent Router] マルチモーダルファイル ({exts}) が検出されました。"
                    "Gemini CLI (1Mコンテキスト) での処理を推奨します。"
                    "gemini-explore エージェントまたは gemini スキルを使用してください。"
                ),
            }
        }, sys.stdout)
        return

    # Priority 2: Codex keywords
    codex_matches = match_keywords(prompt, CODEX_KEYWORDS_JA + CODEX_KEYWORDS_EN)
    if codex_matches:
        keywords = ", ".join(codex_matches[:3])
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": (
                    f"[Agent Router] 設計/推論キーワード ({keywords}) が検出されました。"
                    "Codex CLI での深い分析を検討してください。"
                    "codex スキル、codex-debugger エージェント、または直接 codex exec で実行できます。"
                ),
            }
        }, sys.stdout)
        return

    # Priority 3: Gemini keywords
    gemini_matches = match_keywords(prompt, GEMINI_KEYWORDS_JA + GEMINI_KEYWORDS_EN)
    if gemini_matches:
        keywords = ", ".join(gemini_matches[:3])
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": (
                    f"[Agent Router] リサーチ/分析キーワード ({keywords}) が検出されました。"
                    "Gemini CLI (1Mコンテキスト + Google Search) での調査を検討してください。"
                    "gemini-explore エージェントまたは gemini スキルを使用できます。"
                ),
            }
        }, sys.stdout)
        return

    # No match — pass through
    json.dump(data, sys.stdout)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Non-blocking — never prevent user input
        pass
