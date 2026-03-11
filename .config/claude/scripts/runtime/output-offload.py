#!/usr/bin/env python3
"""Output Offload — save large Bash outputs to file for post-compaction recovery.

When tool_output exceeds threshold, saves full output to a temp file and advises
the model to use filtered commands (grep, head, tail) to reduce context consumption.

Triggered by: hooks.PostToolUse (Bash)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext on stdout (if large output detected)
"""

from __future__ import annotations

import hashlib
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import (
    load_hook_input,
    output_passthrough,
    output_context,
    check_tool,
    run_hook,
)

LINE_THRESHOLD = 150
CHAR_THRESHOLD = 6000
OFFLOAD_DIR = Path(os.environ.get("TMPDIR", "/tmp")) / "claude-tool-outputs"

# Commands that naturally produce large output — don't nag
LARGE_OUTPUT_COMMANDS = [
    "cat ",
    "less ",
    "more ",
    "find ",
    "tree ",
    "git log",
    "git diff",
    "git show",
]


def _is_expected_large(command: str) -> bool:
    cmd_lower = command.strip().lower()
    return any(cmd_lower.startswith(c) for c in LARGE_OUTPUT_COMMANDS)


def _save_output(command: str, output: str) -> Path:
    OFFLOAD_DIR.mkdir(parents=True, exist_ok=True)
    cmd_hash = hashlib.md5(command.encode()).hexdigest()[:8]
    ts = int(time.time())
    filepath = OFFLOAD_DIR / f"{ts}_{cmd_hash}.log"
    filepath.write_text(f"$ {command}\n\n{output}", encoding="utf-8")
    return filepath


def main() -> None:
    data = load_hook_input()
    if not data:
        return

    if not check_tool(data, "Bash"):
        output_passthrough(data)
        return

    command = data.get("tool_input", {}).get("command", "")
    output = data.get("tool_output", "") or ""

    lines = output.split("\n")
    line_count = len(lines)
    char_count = len(output)

    if line_count < LINE_THRESHOLD and char_count < CHAR_THRESHOLD:
        output_passthrough(data)
        return

    # Save full output
    filepath = _save_output(command, output)

    # Build guidance
    parts = [
        f"[Output Offload] 大きな出力を検出 ({line_count}行, {char_count}文字)",
        f"全文保存先: {filepath}",
        "compaction 後に Read ツールで参照可能です。",
    ]

    if not _is_expected_large(command):
        parts.append(
            "推奨: 次回は grep, head -n, tail -n, | wc -l 等で出力を絞ってください。"
        )

    output_context("PostToolUse", "\n".join(parts))


if __name__ == "__main__":
    run_hook("output-offload", main)
