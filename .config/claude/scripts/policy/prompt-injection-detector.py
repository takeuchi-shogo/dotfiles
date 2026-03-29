#!/usr/bin/env python3
"""Prompt injection detector (PreToolUse/Bash|Edit|Write).

ツール入力に含まれるインジェクションパターンを検出しブロックする。
"""

from __future__ import annotations

import base64
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import (
    guard_action,
    load_hook_input,
    rotate_and_append,
    run_hook,
)

# ---------------------------------------------------------------------------
# Detection patterns
# ---------------------------------------------------------------------------

ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d\ufeff]")

ANSI_ESCAPE_RE = re.compile(r"\x1b\[|\\033\[|\\x1b\[")

NULL_BYTE_RE = re.compile(r"\x00|\\x00|\\0(?![0-9])")

# Base64: 20+ contiguous ASCII alphanumeric / +/= characters
BASE64_CANDIDATE_RE = re.compile(r"[A-Za-z0-9+/=]{20,}")

SUSPICIOUS_DECODED = ("eval(", "exec(", "import os", "subprocess", "__import__")

# Nested command substitution: $( ... $( ... $( ... ) ... ) ... )
# We detect 3+ levels of nesting.
COMMAND_SUB_OPEN = re.compile(r"\$\(")

# Sensitive file access (Bash only) — defense-in-depth over permissions deny list
SENSITIVE_FILE_RE = re.compile(
    r"(?:cat|less|head|tail|vi|vim|nano|code|bat)\s+.*"
    r"(?:\.env\b|~/\.aws/credentials|~/\.ssh/id_|\.pem\b)",
    re.IGNORECASE,
)

# Dangerous Bash commands (Bash only) — pipe-to-shell, destructive ops, credential theft
DANGEROUS_BASH_RE = re.compile(
    r"(?:curl|wget)\s+\S+\s*\|\s*(?:ba)?sh"
    r"|rm\s+-rf\s+[/~]"
    r"|security\s+find-generic-password\s+-w"
    r"|gh\s+auth\s+token",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Dual-mode sanitization (strip quoted strings / heredocs)
# ---------------------------------------------------------------------------

_QUOTED_RE = re.compile(r"""(?:"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|`[^`]*`)""")
_HEREDOC_RE = re.compile(r"<<-?\s*(\w+).*?\n.*?\1", re.DOTALL)


def _sanitize(text: str) -> str:
    """Remove quoted strings and heredoc bodies to detect hidden patterns."""
    text = _QUOTED_RE.sub("", text)
    text = _HEREDOC_RE.sub("", text)
    return text


def _count_max_nesting(text: str) -> int:
    """Count the maximum nesting depth of $(...) in *text*."""
    depth = 0
    max_depth = 0
    i = 0
    while i < len(text):
        if text[i] == "$" and i + 1 < len(text) and text[i + 1] == "(":
            depth += 1
            max_depth = max(max_depth, depth)
            i += 2
        elif text[i] == ")" and depth > 0:
            depth -= 1
            i += 1
        else:
            i += 1
    return max_depth


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------


def _extract_text(data: dict) -> list[str]:
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    texts = []
    if tool_name == "Bash":
        texts.append(tool_input.get("command", ""))
    elif tool_name == "Write":
        texts.append(tool_input.get("content", ""))
    elif tool_name == "Edit":
        texts.append(tool_input.get("new_string", ""))
        texts.append(tool_input.get("old_string", ""))
    return [t for t in texts if t]


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------


def _check_base64(text: str) -> tuple[bool, str]:
    """Check for base64-encoded suspicious payloads."""
    for match in BASE64_CANDIDATE_RE.finditer(text):
        candidate = match.group()
        try:
            decoded = base64.b64decode(candidate, validate=True).decode(
                "utf-8", errors="ignore"
            )
        except Exception:
            continue
        for pattern in SUSPICIOUS_DECODED:
            if pattern in decoded:
                return True, f"base64 decoded contains '{pattern}'"
    return False, ""


def _scan(data: dict) -> tuple[bool, str, str]:
    """Scan tool input for injection patterns.

    Returns (blocked, pattern_name, detail).
    """
    tool_name = data.get("tool_name", "")
    texts = _extract_text(data)

    for text in texts:
        # 1. Zero-width Unicode
        m = ZERO_WIDTH_RE.search(text)
        if m:
            return True, "zero-width-unicode", f"U+{ord(m.group()):04X}"

        # 2. ANSI escape sequences
        if ANSI_ESCAPE_RE.search(text):
            return True, "ansi-escape", "ANSI escape sequence detected"

        # 3. Null byte
        if NULL_BYTE_RE.search(text):
            return True, "null-byte", "null byte detected"

        # 4. Base64-encoded suspicious patterns
        found, detail = _check_base64(text)
        if found:
            return True, "base64-payload", detail

        # 5. Nested command substitution (Bash only, 3+ levels)
        if tool_name == "Bash" and _count_max_nesting(text) >= 3:
            return True, "nested-command-substitution", "depth >= 3"

        # 6. Sensitive file access (Bash only)
        if tool_name == "Bash" and SENSITIVE_FILE_RE.search(text):
            return True, "sensitive-file-access", "sensitive file pattern in command"

        # 7. Dangerous Bash commands (Bash only)
        if tool_name == "Bash" and DANGEROUS_BASH_RE.search(text):
            return True, "dangerous-bash-command", "dangerous command pattern detected"

        # Dual-mode: re-scan sanitized text (quoted/heredoc stripped)
        sanitized = _sanitize(text)
        if sanitized != text:
            if ZERO_WIDTH_RE.search(sanitized):
                return True, "zero-width-unicode(sanitized)", "hidden in quotes"
            if ANSI_ESCAPE_RE.search(sanitized):
                return True, "ansi-escape(sanitized)", "hidden in quotes"
            if tool_name == "Bash" and SENSITIVE_FILE_RE.search(sanitized):
                return True, "sensitive-file-access(sanitized)", "hidden in quotes"
            if tool_name == "Bash" and DANGEROUS_BASH_RE.search(sanitized):
                return True, "dangerous-bash-command(sanitized)", "hidden in quotes"

    return False, "", ""


# ---------------------------------------------------------------------------
# Audit logging
# ---------------------------------------------------------------------------


def _log_block(data: dict, pattern_name: str, detail: str) -> None:
    log_dir = os.path.expanduser("~/.claude/agent-memory/logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "prompt-injection.jsonl")

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": data.get("tool_name", ""),
        "pattern": pattern_name,
        "detail": detail,
        "session_id": data.get("session_id", "unknown"),
    }
    rotate_and_append(log_path, json.dumps(entry))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

_FLAG_PATH = os.path.expanduser("~/.claude/agent-memory/flags/mcp-suspicious.json")
_FLAG_TTL_SECONDS = 300  # 5 minutes


def _check_suspicious_flag() -> None:
    """Check for PostToolUse suspicious flag and warn if recent."""
    try:
        if not os.path.exists(_FLAG_PATH):
            return
        with open(_FLAG_PATH, encoding="utf-8") as f:
            flag = json.load(f)
        ts = flag.get("timestamp", "")
        if not ts:
            return
        flag_time = datetime.fromisoformat(ts)
        age = (datetime.now(timezone.utc) - flag_time).total_seconds()
        if age <= _FLAG_TTL_SECONDS:
            print(
                f"[prompt-injection-detector] WARNING: MCP suspicious flag active "
                f"(tool={flag.get('tool')}, pattern={flag.get('pattern')}, "
                f"age={int(age)}s)",
                file=sys.stderr,
            )
    except (json.JSONDecodeError, OSError, ValueError, TypeError) as exc:
        print(f"[prompt-injection-detector] flag check error: {exc}", file=sys.stderr)


def main() -> None:
    data = load_hook_input()
    if not data:
        return

    # Check PostToolUse suspicious flag (block chain)
    _check_suspicious_flag()

    blocked, pattern_name, detail = _scan(data)

    if blocked:
        _log_block(data, pattern_name, detail)
        if guard_action("prompt-injection-detector", pattern_name, detail):
            sys.exit(2)
        return

    # Clean — skip recording to avoid audit.jsonl noise (~945 identical records/cycle)
    # Only blocked/suspicious events are worth recording (via _log_block above)


if __name__ == "__main__":
    run_hook("prompt-injection-detector", main, fail_closed=True)
