#!/usr/bin/env python3
from __future__ import annotations
"""Post-test analysis hook — suggests Codex analysis when tests fail.

Triggered by: hooks.PostToolUse (Bash)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext suggestion on stdout
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import (
    load_hook_input, output_passthrough, output_context,
    check_tool, run_hook,
)


TEST_COMMANDS = [
    re.compile(r"(?:go\s+test|pytest|npm\s+test|npx\s+jest|npx\s+vitest|bun\s+test|cargo\s+test|pnpm\s+test)"),
    re.compile(r"(?:npm|pnpm|bun|yarn)\s+run\s+test"),
]

FAILURE_PATTERNS = [
    re.compile(r"FAIL", re.IGNORECASE),
    re.compile(r"FAILED"),
    re.compile(r"failures?:\s*[1-9]", re.IGNORECASE),
    re.compile(r"errors?:\s*[1-9]", re.IGNORECASE),
    re.compile(r"AssertionError"),
    re.compile(r"AssertError"),
    re.compile(r"assert.*failed", re.IGNORECASE),
    re.compile(r"expected.*but\s+(?:got|received)", re.IGNORECASE),
    re.compile(r"panic:\s"),
    re.compile(r"--- FAIL:"),  # Go test
    re.compile(r"FAILURES!"),  # Python unittest
]


def is_test_command(command: str) -> bool:
    return any(p.search(command) for p in TEST_COMMANDS)


def has_test_failure(output: str) -> bool:
    return any(p.search(output) for p in FAILURE_PATTERNS)


def count_failures(output: str) -> int:
    # Try to extract failure count
    match = re.search(r"(\d+)\s+(?:failed|failures?|errors?)", output, re.IGNORECASE)
    if match:
        return int(match.group(1))
    # Count FAIL lines
    return len(re.findall(r"(?:FAIL|--- FAIL:)", output))


def main() -> None:
    data = load_hook_input()
    if not data:
        return

    if not check_tool(data, "Bash"):
        output_passthrough(data)
        return

    command = data.get("tool_input", {}).get("command", "")
    output = data.get("tool_output", "") or ""

    if not is_test_command(command):
        output_passthrough(data)
        return

    if has_test_failure(output):
        count = count_failures(output)
        count_str = f"{count}件の" if count > 0 else ""
        output_context("PostToolUse", (
            f"[Post-Test] {count_str}テスト失敗が検出されました。\n"
            "codex-debugger エージェントで根本原因を分析できます。\n"
            "または debugger エージェントで体系的にデバッグすることも可能です。"
        ))
        return

    output_passthrough(data)


if __name__ == "__main__":
    run_hook("post-test-analysis", main)
