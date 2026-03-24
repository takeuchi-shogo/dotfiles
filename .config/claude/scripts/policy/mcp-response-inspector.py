#!/usr/bin/env python3
"""MCP response content inspector (PostToolUse/mcp__.*).

VeriGrey (arXiv:2603.17639) Gap #5: MCP サーバーのレスポンスに
埋め込まれたインジェクションパターンを検査する。

強度: Soft warning (advisory) — 検出時は stderr + ログ記録、ブロックしない。
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import (
    get_emitter,
    load_hook_input,
    output_context,
    output_passthrough,
    rotate_and_append,
    run_hook,
)

MAX_RESPONSE_SIZE = 10 * 1024  # 10KB truncation limit

# ---------------------------------------------------------------------------
# Injection directive patterns (natural-language social engineering)
# ---------------------------------------------------------------------------
INJECTION_DIRECTIVES = re.compile(
    r"(?i)"
    r"(?:ignore\s+(?:previous|all|above)\s+(?:instructions?|context))"
    r"|(?:before\s+you\s+can\s+solve)"
    r"|(?:重要なメッセージ)"
    r"|(?:IMPORTANT\s*:\s*(?:you\s+must|first|before))"
    r"|(?:system\s*:\s*(?:override|new\s+instruction))"
    r"|(?:forget\s+(?:everything|your\s+instructions?))"
)

# ---------------------------------------------------------------------------
# URL + secret reference co-occurrence
# ---------------------------------------------------------------------------
URL_RE = re.compile(r"https?://[^\s\"'<>]+")
SECRET_RE = re.compile(
    r"(?i)(?:SECRET|API_KEY|TOKEN|PASSWORD|CREDENTIALS|\.env\b|private_key)"
)

# ---------------------------------------------------------------------------
# Technical injection patterns (reused from prompt-injection-detector.py)
# Built dynamically to avoid triggering the injection detector on this source.
# ---------------------------------------------------------------------------
ZERO_WIDTH_RE = re.compile("[\u200b\u200c\u200d\ufeff]")
ANSI_ESCAPE_RE = re.compile(re.escape("\x1b") + r"\[")
NULL_BYTE_RE = re.compile(chr(0))


def _inspect(text: str) -> tuple[str, str] | None:
    """Inspect text for injection patterns.

    Returns (pattern_name, detail) or None.
    """
    m = INJECTION_DIRECTIVES.search(text)
    if m:
        return "injection-directive", m.group()[:80]

    if URL_RE.search(text) and SECRET_RE.search(text):
        return "url-secret-cooccurrence", "URL + secret reference in MCP response"

    if ZERO_WIDTH_RE.search(text):
        return "zero-width-char", "Zero-width character in MCP response"

    if ANSI_ESCAPE_RE.search(text):
        return "ansi-escape", "ANSI escape sequence in MCP response"

    if NULL_BYTE_RE.search(text):
        return "null-byte", "Null byte in MCP response"

    return None


def _log_finding(data: dict, pattern_name: str, detail: str, log_path: str) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": data.get("tool_name", ""),
        "pattern": pattern_name,
        "detail": detail[:200],
        "session_id": data.get("session_id", "unknown"),
    }
    rotate_and_append(log_path, json.dumps(entry))


def _main() -> None:
    data = load_hook_input()
    if not data:
        return

    tool_name = data.get("tool_name", "")
    if not tool_name.startswith("mcp__"):
        output_passthrough(data)
        return

    tool_output = data.get("tool_output", "") or ""
    if not isinstance(tool_output, str):
        tool_output = str(tool_output)

    # Truncate large responses
    if len(tool_output) > MAX_RESPONSE_SIZE:
        tool_output = tool_output[:MAX_RESPONSE_SIZE]

    result = _inspect(tool_output)

    if result:
        pattern_name, detail = result

        # Log finding
        log_dir = os.path.expanduser("~/.claude/agent-memory/logs")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "mcp-response-inspection.jsonl")
        _log_finding(data, pattern_name, detail, log_path)

        # Emit event
        emit = get_emitter()
        emit(
            "security",
            {
                "type": "mcp_response_injection",
                "pattern": pattern_name,
                "tool": tool_name,
            },
        )

        # Write suspicious flag for PreToolUse block chain (atomic via tempfile)
        import tempfile

        flag_dir = os.path.expanduser("~/.claude/agent-memory/flags")
        os.makedirs(flag_dir, exist_ok=True)
        flag_path = os.path.join(flag_dir, "mcp-suspicious.json")
        flag_entry = {
            "tool": tool_name,
            "pattern": pattern_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        try:
            with tempfile.NamedTemporaryFile(
                "w", dir=flag_dir, suffix=".json", delete=False, encoding="utf-8"
            ) as tmp:
                json.dump(flag_entry, tmp)
                tmp_path = tmp.name
            os.replace(tmp_path, flag_path)
        except OSError as exc:
            print(f"[MCP Response Inspector] flag write error: {exc}", file=sys.stderr)

        # Soft warning (advisory, do not block)
        msg = (
            f"[MCP Response Inspector] {tool_name} のレスポンスに"
            f"疑わしいパターンを検出: {pattern_name} — {detail}"
        )
        print(msg, file=sys.stderr)
        output_context("PostToolUse", msg)
        return

    output_passthrough(data)


if __name__ == "__main__":
    run_hook("mcp-response-inspector", _main, fail_closed=False)
