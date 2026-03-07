#!/usr/bin/env python3
"""Error-to-Codex hook — suggests codex-debugger when Bash errors are detected.

Triggered by: hooks.PostToolUse (Bash)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext suggestion on stdout
"""
import json
import re
import sys


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
    "git status", "git log", "git diff", "git branch",
    "ls", "cat", "head", "tail", "pwd", "which", "echo",
    "codex", "gemini",  # Prevent infinite loops
]


def is_info_command(command: str) -> bool:
    cmd_lower = command.strip().lower()
    return any(cmd_lower.startswith(ic) for ic in IGNORE_COMMANDS)


def has_error(output: str) -> str | None:
    for pattern in ERROR_PATTERNS:
        match = pattern.search(output)
        if match:
            return match.group(0)
    return None


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = data.get("tool_name", "")
    if tool_name != "Bash":
        json.dump(data, sys.stdout)
        return

    command = data.get("tool_input", {}).get("command", "")
    output = data.get("tool_output", "") or ""

    # Skip info commands and short output
    if is_info_command(command) or len(output) < 20:
        json.dump(data, sys.stdout)
        return

    # Skip "already exists" and similar benign messages
    if "already exists" in output.lower():
        json.dump(data, sys.stdout)
        return

    error_match = has_error(output)
    if error_match:
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    f"[Error-to-Codex] エラーが検出されました: {error_match}\n"
                    "codex-debugger エージェントを使用してこのエラーの根本原因を分析できます。\n"
                    "コマンド: " + command[:100]
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
