#!/usr/bin/env python3
"""MCP tool audit logger (PreToolUse/mcp__.*).

Logs all MCP tool invocations for security auditing.
Blocks dangerous MCP operations (e.g., destructive GitHub actions).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import get_emitter, load_hook_input, run_hook

# MCP operations that should be blocked
DANGEROUS_MCP_PREFIXES = [
    ("mcp__github__delete", "Destructive GitHub operation"),
    ("mcp__filesystem__delete", "Filesystem deletion via MCP"),
    ("mcp__filesystem__move", "Filesystem move via MCP"),
]

LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB


def _summarize_input(tool_input: object) -> dict[str, str] | str:
    """Create a safe summary of tool input (truncate large values)."""
    if not isinstance(tool_input, dict):
        return str(tool_input)[:200]
    summary = {}
    for k, v in tool_input.items():
        s = str(v)
        summary[k] = s[:100] + "..." if len(s) > 100 else s
    return summary


def _rotate_if_needed(log_path: str) -> None:
    """Rotate log file if it exceeds LOG_MAX_BYTES."""
    try:
        if os.path.exists(log_path) and os.path.getsize(log_path) > LOG_MAX_BYTES:
            rotated = log_path + ".1"
            if os.path.exists(rotated):
                os.remove(rotated)
            os.rename(log_path, rotated)
    except OSError as e:
        print(f"[mcp-audit] log rotation warning: {e}", file=sys.stderr)


def _audit(data: dict) -> None:
    tool_name = data.get("tool_name", "")

    if not tool_name.startswith("mcp__"):
        return

    tool_input = data.get("tool_input", {})
    timestamp = datetime.now(timezone.utc).isoformat()

    audit_entry = {
        "timestamp": timestamp,
        "tool": tool_name,
        "input_summary": _summarize_input(tool_input),
        "session_id": data.get("session_id", "unknown"),
    }

    # Persist audit log with rotation
    log_dir = os.path.expanduser("~/.claude/agent-memory/logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "mcp-audit.jsonl")

    _rotate_if_needed(log_path)

    try:
        with open(log_path, "a") as f:
            f.write(json.dumps(audit_entry) + "\n")
    except OSError as e:
        print(f"[mcp-audit] log write warning: {e}", file=sys.stderr)

    # Check for dangerous operations (startswith for precision)
    for prefix, reason in DANGEROUS_MCP_PREFIXES:
        if tool_name.startswith(prefix):
            print(f"BLOCKED: MCP audit block — {reason} ({tool_name})", file=sys.stderr)
            sys.exit(2)

    # Emit event for AutoEvolve tracking
    emit = get_emitter()
    emit("pattern", {"type": "mcp_tool_usage", "tool": tool_name})


def main() -> None:
    data = load_hook_input()
    if not data:
        return
    _audit(data)


if __name__ == "__main__":
    run_hook("mcp-audit", main)
