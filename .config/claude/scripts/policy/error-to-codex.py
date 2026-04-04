#!/usr/bin/env python3
"""Error-to-Codex hook — suggests codex-debugger when Bash errors are detected.

Also injects fix guidance from error-fix-guides.md when available.

Triggered by: hooks.PostToolUse (Bash)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext suggestion on stdout
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import (
    load_hook_input,
    output_passthrough,
    output_context,
    check_tool,
    run_hook,
    get_emitter,
    resolve_reference,
)

emit = get_emitter()


ERROR_PATTERNS = [
    re.compile(r"Traceback \(most recent call last\)"),
    re.compile(r"(?:Error|Exception):\s+\S"),
    re.compile(r"panic:\s"),
    re.compile(r"FAIL\s+\S"),
    re.compile(r"npm ERR!"),
    re.compile(r"error\[E\d+\]"),  # Rust compiler errors
    re.compile(r"cannot find module", re.IGNORECASE),
    re.compile(r"undefined reference"),
    re.compile(r"segmentation fault", re.IGNORECASE),
    re.compile(r"fatal error"),
    re.compile(r"compilation failed"),
    re.compile(r"build failed", re.IGNORECASE),
    re.compile(r"SyntaxError:"),
    re.compile(r"TypeError:"),
    re.compile(r"ReferenceError:"),
]

# Commands that are just info-gathering — don't suggest debugging
IGNORE_COMMANDS = [
    "git status",
    "git log",
    "git diff",
    "git branch",
    "ls",
    "cat",
    "head",
    "tail",
    "pwd",
    "which",
    "echo",
    "codex",
    "gemini",  # Prevent infinite loops
]

GUIDES_PATH = resolve_reference("error-fix-guides.md")


def load_fix_guides() -> dict[str, tuple[str, str]]:
    """Parse error-fix-guides.md into {header_keyword: (cause, fix)} dict.

    Note: hooks run as separate processes, so no in-process caching is possible.
    Expected format in error-fix-guides.md:
      ### <error keyword>
      - **原因**: <cause text>
      - **修正**: <fix text>
    """
    guides: dict[str, tuple[str, str]] = {}
    if not GUIDES_PATH.exists():
        return guides

    try:
        content = GUIDES_PATH.read_text(encoding="utf-8")
    except OSError:
        return guides

    current_key = ""
    cause = ""
    fix = ""

    for line in content.split("\n"):
        line_s = line.strip()
        if line_s.startswith("### "):
            if current_key and (cause or fix):
                guides[current_key.lower()] = (cause, fix)
            current_key = line_s[4:].strip()
            cause = ""
            fix = ""
        elif line_s.startswith("- **原因**:"):
            cause = line_s.split(":", 1)[1].strip() if ":" in line_s else ""
        elif line_s.startswith("- **修正**:"):
            fix = line_s.split(":", 1)[1].strip() if ":" in line_s else ""

    if current_key and (cause or fix):
        guides[current_key.lower()] = (cause, fix)

    return guides


def find_fix_guide(error_text: str) -> tuple[str, str] | None:
    """Find a matching fix guide for the given error text."""
    guides = load_fix_guides()
    error_lower = error_text.lower()
    for key, value in guides.items():
        if key in error_lower:
            return value
    return None


def is_info_command(command: str) -> bool:
    cmd_lower = command.strip().lower()
    return any(cmd_lower.startswith(ic) for ic in IGNORE_COMMANDS)


def has_error(output: str) -> str | None:
    for pattern in ERROR_PATTERNS:
        match = pattern.search(output)
        if match:
            line_start = output.rfind("\n", 0, match.start()) + 1
            line_end = output.find("\n", match.end())
            if line_end == -1:
                line_end = len(output)
            return output[line_start:line_end][:200]
    return None


def main() -> None:
    data = load_hook_input()
    if not data:
        return

    if not check_tool(data, "Bash"):
        output_passthrough(data)
        return

    command = data.get("tool_input", {}).get("command", "")
    output = data.get("tool_output", "") or ""

    # Skip info commands and short output
    if is_info_command(command) or len(output) < 20:
        output_passthrough(data)
        return

    # Skip "already exists" and similar benign messages
    if "already exists" in output.lower():
        output_passthrough(data)
        return

    error_match = has_error(output)
    if error_match:
        emit(
            "error",
            {
                "message": error_match,
                "command": command[:200],
            },
        )
        # Build context message
        context_parts = [
            f"[Error-to-Codex] エラーが検出されました: {error_match}",
        ]

        # Try to find a fix guide
        guide = find_fix_guide(output)
        if guide:
            cause, fix = guide
            if cause:
                context_parts.append(f"推定原因: {cause}")
            if fix:
                context_parts.append(f"推奨修正: {fix}")

        context_parts.append(
            "codex-debugger エージェントを使用してこのエラーの根本原因を分析できます。"
        )
        context_parts.append("コマンド: " + command[:100])

        output_context("PostToolUse", "\n".join(context_parts))
        return

    output_passthrough(data)


if __name__ == "__main__":
    run_hook("error-to-codex", main)
