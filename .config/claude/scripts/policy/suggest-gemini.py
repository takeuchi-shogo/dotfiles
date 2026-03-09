#!/usr/bin/env python3
from __future__ import annotations
"""Suggest Gemini hook — recommends Gemini CLI for complex research before WebSearch.

Triggered by: hooks.PreToolUse (WebSearch)
Input: JSON with tool_name, tool_input on stdin
Output: JSON with additionalContext suggestion on stdout
"""
import json
import sys


SIMPLE_QUERIES = [
    "error message", "version", "changelog", "release notes",
    "stackoverflow", "github issue", "npm package",
    "エラーメッセージ", "バージョン", "リリースノート",
]

RESEARCH_KEYWORDS = [
    "documentation", "best practice", "comparison", "vs",
    "library", "framework", "tutorial", "guide",
    "architecture", "migration", "upgrade", "pattern",
    "api reference", "specification", "benchmark",
    "ドキュメント", "ベストプラクティス", "比較",
    "ライブラリ", "フレームワーク", "チュートリアル",
    "アーキテクチャ", "マイグレーション", "パターン",
]


def is_simple_query(query: str) -> bool:
    query_lower = query.lower()
    return any(sq in query_lower for sq in SIMPLE_QUERIES)


def is_research_query(query: str) -> bool:
    query_lower = query.lower()
    if any(rk in query_lower for rk in RESEARCH_KEYWORDS):
        return True
    # Complex queries (long) are likely research
    if len(query) > 100:
        return True
    return False


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    query = data.get("tool_input", {}).get("query", "") or ""

    if not query or is_simple_query(query):
        json.dump(data, sys.stdout)
        return

    if is_research_query(query):
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": (
                    "[Suggest-Gemini] 複雑なリサーチが検出されました。"
                    "Gemini CLI (1Mコンテキスト + Google Search grounding) の方が"
                    "より包括的な結果を得られる可能性があります。\n"
                    "gemini-explore エージェントまたは gemini スキルの使用を検討してください。\n"
                    "結果は .claude/docs/research/ に保存できます。"
                ),
            }
        }, sys.stdout)
        return

    json.dump(data, sys.stdout)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        json.dump({}, sys.stdout)
