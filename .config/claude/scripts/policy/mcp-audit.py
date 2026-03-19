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
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import get_emitter, load_hook_input, rotate_and_append, run_hook

# MCP operations that should be blocked
DANGEROUS_MCP_PREFIXES = [
    ("mcp__github__delete", "Destructive GitHub operation"),
    ("mcp__filesystem__delete", "Filesystem deletion via MCP"),
    ("mcp__filesystem__move", "Filesystem move via MCP"),
]


def _check_skill_mcp_scope(tool_name: str, skill_name: str) -> None:
    """Warn if MCP tool is not in the active skill's mcp-tools."""
    skills_dir = Path(__file__).resolve().parent.parent.parent / "skills"
    skill_file = skills_dir / skill_name / "SKILL.md"
    if not skill_file.exists():
        return

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
                            f"[MCP Audit] MCP server "
                            f"'{server}' はスキル "
                            f"'{skill_name}' の "
                            f"mcp-tools 外です",
                            file=sys.stderr,
                        )
                return
    except OSError as exc:
        print(
            f"[MCP Audit] skill scope check error: {exc}",
            file=sys.stderr,
        )


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

    # Check for dangerous operations (startswith for precision)
    for prefix, reason in DANGEROUS_MCP_PREFIXES:
        if tool_name.startswith(prefix):
            print(f"BLOCKED: MCP audit block — {reason} ({tool_name})", file=sys.stderr)
            sys.exit(2)

    # Skill-level MCP tool scoping (advisory)
    skill_name = os.environ.get("CLAUDE_SKILL", "")
    if skill_name:
        _check_skill_mcp_scope(tool_name, skill_name)

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
