#!/usr/bin/env python3
"""SessionStart hook: snapshot current harness file changes.

Stop hook (completion-gate.py) compares this snapshot against
the current state to detect harness changes made WITHIN the session.
Without this snapshot, parallel sessions trigger false-positive
"Harness Review Gate" warnings on each other's edits.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

SESSION_STATE_DIR = Path(os.path.expanduser("~/.claude/session-state"))
SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def _get_session_id() -> str:
    """Read session_id from stdin JSON or env."""
    raw = ""
    try:
        raw = sys.stdin.read()
    except (OSError, ValueError) as exc:
        print(f"[harness-snapshot] stdin read failed: {exc}", file=sys.stderr)
    if raw:
        try:
            payload = json.loads(raw)
            sid = payload.get("session_id", "")
            if sid:
                return sid
        except json.JSONDecodeError as exc:
            print(f"[harness-snapshot] JSON parse failed: {exc}", file=sys.stderr)
    return os.environ.get("CLAUDE_SESSION_ID", "")


def _snapshot_harness_status() -> list[str]:
    """Get current uncommitted file paths via git diff."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=os.getcwd(),
        )
        if result.returncode != 0:
            return []
        return [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except (subprocess.TimeoutExpired, OSError, FileNotFoundError) as exc:
        print(f"[harness-snapshot] git diff failed: {exc}", file=sys.stderr)
        return []


def main() -> None:
    session_id = _get_session_id()
    if not session_id:
        print("[harness-snapshot] no session_id, snapshot skipped", file=sys.stderr)
        return
    if not SESSION_ID_PATTERN.fullmatch(session_id):
        print(
            "[harness-snapshot] invalid session_id format, snapshot skipped",
            file=sys.stderr,
        )
        return

    SESSION_STATE_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_path = SESSION_STATE_DIR / f"initial-harness-{session_id}.txt"

    # Already snapshot exists (resume case)? skip to keep first snapshot
    if snapshot_path.exists():
        return

    files = _snapshot_harness_status()
    snapshot_path.write_text("\n".join(files) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
