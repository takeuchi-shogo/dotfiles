#!/usr/bin/env python3
"""MCP tool audit logger.

Logs all MCP tool invocations for security auditing.
Blocks dangerous MCP operations (e.g., destructive GitHub actions).
"""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

# MCP operations that should be blocked or warned about
DANGEROUS_MCP_PATTERNS = {
    "mcp__github__delete": "Destructive GitHub operation",
    "mcp__filesystem__delete": "Filesystem deletion via MCP",
    "mcp__filesystem__move": "Filesystem move via MCP",
}


def _summarize_input(tool_input):
    """Create a safe summary of tool input (truncate large values)."""
    if not isinstance(tool_input, dict):
        return str(tool_input)[:200]
    summary = {}
    for k, v in tool_input.items():
        s = str(v)
        summary[k] = s[:100] + "..." if len(s) > 100 else s
    return summary


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = data.get("tool_name", "")

    # Only process MCP tools
    if not tool_name.startswith("mcp__"):
        return

    tool_input = data.get("tool_input", {})
    timestamp = datetime.now().isoformat()

    # Build audit entry
    audit_entry = {
        "timestamp": timestamp,
        "tool": tool_name,
        "input_summary": _summarize_input(tool_input),
        "session_id": data.get("session_id", "unknown"),
    }

    # Persist audit log
    log_dir = os.path.expanduser("~/.claude/agent-memory/logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "mcp-audit.jsonl")

    with open(log_path, "a") as f:
        f.write(json.dumps(audit_entry) + "\n")

    # Check for dangerous operations
    for pattern, reason in DANGEROUS_MCP_PATTERNS.items():
        if pattern in tool_name:
            print(
                json.dumps(
                    {
                        "error": f"MCP audit block: {reason}",
                        "tool": tool_name,
                        "suggestion": "Use safer alternatives or confirm this is intentional",
                    }
                ),
                file=sys.stderr,
            )
            sys.exit(2)

    # Emit event for AutoEvolve tracking
    try:
        from session_events import emit_event

        emit_event(
            "pattern",
            {
                "type": "mcp_tool_usage",
                "tool": tool_name,
            },
        )
    except ImportError:
        sys.stderr.write("mcp-audit: session_events not available, skipping emit\n")


if __name__ == "__main__":
    main()
