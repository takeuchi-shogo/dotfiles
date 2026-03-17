#!/usr/bin/env python3
"""SubagentStop performance monitor.

Tracks sub-agent execution duration and emits metrics.
Plays a subtle notification sound on sub-agent completion.
"""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    session_id = data.get("session_id", "unknown")
    stop_hook_active = data.get("stop_hook_active", False)
    timestamp = datetime.now().isoformat()

    # Build log entry
    log_entry = {
        "timestamp": timestamp,
        "session_id": session_id,
        "event": "subagent_complete",
        "stop_hook_active": stop_hook_active,
    }

    # Persist to metrics
    log_dir = os.path.expanduser("~/.claude/agent-memory/logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "subagent-metrics.jsonl")

    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    # Emit via session_events if available
    try:
        from session_events import emit_event

        emit_event(
            "pattern",
            {
                "type": "subagent_complete",
                "session_id": session_id,
                "stop_hook_active": stop_hook_active,
            },
        )
    except ImportError:
        sys.stderr.write(
            "subagent-monitor: session_events not available, skipping emit\n"
        )

    # Notify completion with subtle sound
    os.system("afplay /System/Library/Sounds/Tink.aiff &")

    # Print to stdout for transcript context
    print(f"Sub-agent completed (session: {session_id[:8]}...)")


if __name__ == "__main__":
    main()
