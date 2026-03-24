#!/usr/bin/env python3
"""MCP tool audit logger (PreToolUse/mcp__.*).

Logs all MCP tool invocations for security auditing.
Blocks dangerous MCP operations (e.g., destructive GitHub actions).

Skill-level MCP scoping: when CLAUDE_SKILL is set and the skill
declares `mcp-tools:` in its SKILL.md, warns on out-of-scope servers.
For general tool scoping (non-MCP), see tool-scope-enforcer.py.
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
    rotate_and_append,
    run_hook,
)

# MCP operations that should be blocked
# Entries starting with ^ are treated as regex patterns, others use startswith.
DANGEROUS_MCP_PREFIXES = [
    ("mcp__github__delete", "Destructive GitHub operation"),
    ("mcp__filesystem__delete", "Filesystem deletion via MCP"),
    ("mcp__filesystem__move", "Filesystem move via MCP"),
    ("^mcp__.*__truncate$", "Destructive truncate operation"),
]

# Known MCP servers (unknown servers trigger a warning, not a block)
KNOWN_MCP_SERVERS = {
    "obsidian",
    "playwright",
    "brave-search",
    "context7",
    "alphaxiv",
    "plugin_discord_discord",
}


def _check_skill_mcp_scope(tool_name: str, skill_name: str) -> bool:
    """Check if MCP tool is in the active skill's mcp-tools.

    Returns True if scope violation detected (soft block).
    """
    skills_dir = Path(__file__).resolve().parent.parent.parent / "skills"
    skill_file = skills_dir / skill_name / "SKILL.md"
    if not skill_file.exists():
        return False

    try:
        content = skill_file.read_text()
        for line in content.split("\n"):
            if line.startswith("mcp-tools:"):
                allowed = [t.strip() for t in line.split(":", 1)[1].strip().split(",")]
                parts = tool_name.split("__")
                if len(parts) >= 2:
                    server = parts[1]
                    if server not in allowed:
                        print(
                            f"[MCP Audit] SCOPE VIOLATION: MCP server "
                            f"'{server}' はスキル "
                            f"'{skill_name}' の "
                            f"mcp-tools 外です。"
                            f"このツールを使用する正当な理由がありますか？",
                            file=sys.stderr,
                        )
                        return True
                return False
    except OSError as exc:
        print(
            f"[MCP Audit] skill scope check error: {exc}",
            file=sys.stderr,
        )
    return False


# ---------------------------------------------------------------------------
# T5: Tool call sequence anomaly detection (VeriGrey arXiv:2603.17639)
# ---------------------------------------------------------------------------
_READ_KEYWORDS = {"read", "get", "fetch", "search", "list", "query", "info"}
_SEND_KEYWORDS = {
    "reply",
    "send",
    "post",
    "create_issue",
    "create_pr",
    "write_note",
    "patch_note",
}


def _check_sequence_anomaly(tool_name: str, session_id: str, log_path: str) -> None:
    """Detect read→send tool transitions that may indicate data exfiltration."""
    if not os.path.exists(log_path):
        return

    tool_lower = tool_name.lower()
    is_send = any(kw in tool_lower for kw in _SEND_KEYWORDS)
    if not is_send:
        return

    # Read recent log entries for this session
    try:
        with open(log_path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return

    # Check last 10 entries for a read→send pattern
    recent = []
    for line in reversed(lines[-20:]):
        try:
            entry = json.loads(line)
            if entry.get("session_id") == session_id:
                recent.append(entry.get("tool", ""))
                if len(recent) >= 10:
                    break
        except (json.JSONDecodeError, KeyError):
            continue

    for prev_tool in recent[1:]:  # skip current (not yet logged)
        prev_lower = prev_tool.lower()
        if any(kw in prev_lower for kw in _READ_KEYWORDS):
            msg = (
                f"[MCP Audit] SEQUENCE WARNING: "
                f"読み取り系ツール ({prev_tool}) → 送信系ツール ({tool_name}) "
                f"の遷移を検出。データ漏洩パターンの可能性があります。"
            )
            print(msg, file=sys.stderr)
            return


def _summarize_input(tool_input: object) -> dict[str, str] | str:
    """Create a safe summary of tool input (truncate large values)."""
    if not isinstance(tool_input, dict):
        return str(tool_input)[:200]
    summary = {}
    for k, v in tool_input.items():
        s = str(v)
        summary[k] = s[:100] + "..." if len(s) > 100 else s
    return summary


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
    rotate_and_append(log_path, json.dumps(audit_entry))

    # Check for dangerous operations (startswith or regex)
    for prefix, reason in DANGEROUS_MCP_PREFIXES:
        if prefix.startswith("^"):
            if re.match(prefix, tool_name):
                print(
                    f"BLOCKED: MCP audit block — {reason} ({tool_name})",
                    file=sys.stderr,
                )
                sys.exit(2)
        elif tool_name.startswith(prefix):
            print(f"BLOCKED: MCP audit block — {reason} ({tool_name})", file=sys.stderr)
            sys.exit(2)

    # Warn on unknown MCP servers
    parts = tool_name.split("__")
    if len(parts) >= 2:
        server = parts[1]
        if server not in KNOWN_MCP_SERVERS:
            print(
                f"[MCP Audit] WARNING: Unknown MCP server '{server}' "
                f"(tool: {tool_name}). Verify this server is trusted.",
                file=sys.stderr,
            )

    # Skill-level MCP tool scoping (soft block — VeriGrey Tool Filter)
    skill_name = os.environ.get("CLAUDE_SKILL", "")
    if skill_name:
        scope_violated = _check_skill_mcp_scope(tool_name, skill_name)
        if scope_violated:
            audit_entry["scope_violation"] = True
            rotate_and_append(log_path, json.dumps(audit_entry))
            sys.exit(2)

    # Sequence anomaly detection (VeriGrey arXiv:2603.17639)
    _check_sequence_anomaly(tool_name, data.get("session_id", "unknown"), log_path)

    # Emit event for AutoEvolve tracking
    emit = get_emitter()
    emit("pattern", {"type": "mcp_tool_usage", "tool": tool_name})


def main() -> None:
    data = load_hook_input()
    if not data:
        return
    _audit(data)


if __name__ == "__main__":
    run_hook("mcp-audit", main, fail_closed=True)
