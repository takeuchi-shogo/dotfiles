#!/usr/bin/env python3
"""MCP skill hint — suggest /skill-creator when a new MCP server is registered.

Triggered by: hooks.PostToolUse (Edit|Write)
Input: JSON with tool_name, tool_input (file_path + new_string/content) on stdin
Output: JSON with additionalContext hint when MCP config files are edited

Purpose: 記事 "Hermes as a personal analyst" (2026-04-14 /absorb) の知見から、
新規 MCP 接続時に skill-creator の起動を促すヒント通知を行う。自動生成はしない。
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import (
    check_tool,
    load_hook_input,
    output_context,
    output_passthrough,
    run_hook,
)

# MCP 設定ファイル候補 (basename 一致)
MCP_CONFIG_BASENAMES = (".claude.json", ".mcp.json", "mcp.json")

HINT_MESSAGE = (
    "💡 [mcp-skill-hint] MCP 設定が変更されました。\n"
    "新しい MCP server を追加した場合、`/skill-creator` で既存ツールと"
    "組み合わせたタスク固有スキルを生成することを検討してください\n"
    "(例: 朝ブリーフィングに DefiLlama を統合する skill、"
    "research スキルに Dune を統合する skill 等)。\n"
    "MCP を skill 抽象層に引き上げることで、"
    "低レベル tool 直接呼びより安定した運用ができます。\n"
    "参考: `.config/claude/references/mcp-toolshed.md`"
)


def main() -> None:
    data = load_hook_input()

    if not check_tool(data, ["Edit", "Write"]):
        output_passthrough(data)
        return

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    basename = Path(file_path).name

    if basename not in MCP_CONFIG_BASENAMES:
        output_passthrough(data)
        return

    # 追加内容を取得 (Edit は new_string、Write は content)
    added = tool_input.get("new_string") or tool_input.get("content") or ""
    if not added:
        output_passthrough(data)
        return

    # MCP server 関連キーワードが追加内容に含まれるかチェック
    # (true positive を高めるための最小検出)
    if "mcpServers" not in added and '"command"' not in added:
        output_passthrough(data)
        return

    output_context("PostToolUse", HINT_MESSAGE)


if __name__ == "__main__":
    run_hook("mcp-skill-hint", main)
