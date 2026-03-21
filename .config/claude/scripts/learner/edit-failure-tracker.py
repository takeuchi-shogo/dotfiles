#!/usr/bin/env python3
"""Edit/Write ツール失敗トラッカー。

PostToolUse hook として Edit|Write の失敗を計測し、
session_events に記録する。

記事 "The Harness Problem" の知見:
  モデルのせいに見える失敗の多くはツールフォーマットの問題。
  失敗パターンを計測することで、委譲戦略の最適化に活用する。

Triggered by: PostToolUse (Edit|Write)
Input: JSON on stdin (tool_name, tool_input, tool_result)
Output: stdout passthrough
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))


def main() -> None:
    data = sys.stdin.read()

    try:
        hook_input = json.loads(data)
    except (json.JSONDecodeError, ValueError):
        sys.stdout.write(data)
        return

    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})
    tool_result = hook_input.get("tool_result", {})

    is_error = tool_result.get("is_error", False)
    if not is_error:
        sys.stdout.write(data)
        return

    from session_events import emit_event

    result_content = tool_result.get("content", "")
    if isinstance(result_content, list):
        result_content = " ".join(
            item.get("text", "") for item in result_content if isinstance(item, dict)
        )

    # 失敗パターンの分類
    failure_pattern = _classify_failure(result_content)

    file_path = tool_input.get("file_path", "")
    file_ext = Path(file_path).suffix if file_path else ""

    emit_event(
        "error",
        {
            "message": f"{tool_name} failed: {result_content[:200]}",
            "tool_name": tool_name,
            "file_path": file_path,
            "file_ext": file_ext,
            "failure_pattern": failure_pattern,
            "failure_mode": "FM-016",
            "failure_type": "tool_interface",
        },
    )

    sys.stdout.write(data)


def _classify_failure(content: str) -> str:
    """Edit/Write の失敗内容からパターンを分類する。"""
    c = content.lower()
    if "not found in file" in c or "not unique" in c:
        return "str_replace_mismatch"
    if "whitespace" in c or "indentation" in c:
        return "whitespace_mismatch"
    if "no such file" in c or "does not exist" in c:
        return "file_not_found"
    if "permission" in c:
        return "permission_denied"
    if "encoding" in c or "utf" in c:
        return "encoding_error"
    if "read" in c and "first" in c:
        return "read_before_edit"
    return "other"


if __name__ == "__main__":
    main()
