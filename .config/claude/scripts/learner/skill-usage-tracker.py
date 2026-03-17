#!/usr/bin/env python3
"""Skill usage tracker — logs which skills are invoked and when.

Listens on PreToolUse for Skill tool calls, records to JSONL for AutoEvolve analysis.
"""

import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = data.get("tool_name", "")
    if tool_name != "Skill":
        return

    tool_input = data.get("tool_input", {})
    skill_name = tool_input.get("skill", "unknown")

    # Log to JSONL
    log_dir = (
        Path(
            os.environ.get(
                "AUTOEVOLVE_DATA_DIR", os.path.expanduser("~/.claude/agent-memory")
            )
        )
        / "metrics"
    )
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "skill-usage.jsonl"

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "skill": skill_name,
        "args": tool_input.get("args", ""),
        "cwd": os.getcwd(),
    }

    with open(log_file, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
