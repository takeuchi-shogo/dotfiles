#!/usr/bin/env python3
"""SubagentStop performance monitor.

Tracks sub-agent completion and emits metrics.
Plays a subtle notification sound on macOS.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import get_emitter, load_hook_input, rotate_and_append, run_hook


def _play_notification_sound() -> None:
    """Play a subtle notification sound on macOS."""
    if platform.system() != "Darwin":
        return
    try:
        subprocess.Popen(
            ["/usr/bin/afplay", "/System/Library/Sounds/Tink.aiff"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError as e:
        print(f"[subagent-monitor] sound warning: {e}", file=sys.stderr)


def _monitor(data: dict) -> None:
    session_id = str(data.get("session_id") or "unknown")
    stop_hook_active = data.get("stop_hook_active", False)
    timestamp = datetime.now(timezone.utc).isoformat()

    log_entry = {
        "timestamp": timestamp,
        "session_id": session_id,
        "event": "subagent_complete",
        "stop_hook_active": stop_hook_active,
    }

    # Persist to metrics with rotation
    log_dir = os.path.expanduser("~/.claude/agent-memory/logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "subagent-metrics.jsonl")
    rotate_and_append(log_path, json.dumps(log_entry))

    # Emit via session_events
    emit = get_emitter()
    emit(
        "pattern",
        {
            "type": "subagent_complete",
            "session_id": session_id,
            "stop_hook_active": stop_hook_active,
        },
    )

    _play_notification_sound()


def main() -> None:
    data = load_hook_input()
    if not data:
        return
    _monitor(data)


if __name__ == "__main__":
    run_hook("subagent-monitor", main)
