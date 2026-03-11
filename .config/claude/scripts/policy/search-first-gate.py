#!/usr/bin/env python3
"""Search-First Gate — reminds agent to search before writing new code.

Tracks whether Grep/Glob/Read have been used in the session.
On the first Edit/Write, if no search has occurred, injects a reminder.
Uses a simple state file to avoid repeated warnings.

Triggered by: hooks.PreToolUse (Edit|Write)
Input: JSON with tool_name, tool_input on stdin
Output: JSON with additionalContext on stdout (first edit only)
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import output_context  # noqa: E402

STATE_DIR = Path(
    os.environ.get(
        "CLAUDE_SESSION_STATE_DIR",
        os.path.join(os.environ.get("HOME", ""), ".claude", "session-state"),
    )
)
STATE_FILE = STATE_DIR / "search-first.json"
SESSION_TTL = 2 * 60 * 60  # 2 hours — reset after session timeout


def _load_state() -> dict:
    try:
        state = json.loads(STATE_FILE.read_text())
        if time.time() - state.get("started", 0) > SESSION_TTL:
            return {"started": time.time(), "searched": False, "warned": False}
        return state
    except (OSError, json.JSONDecodeError, ValueError):
        return {"started": time.time(), "searched": False, "warned": False}


def _save_state(state: dict) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state))
    except OSError as e:
        print(f"[search-first-gate] state save failed: {e}", file=sys.stderr)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = data.get("tool_name", "")
    state = _load_state()

    # Track search tools — if we see Grep/Glob/Read, mark as searched
    if tool_name in ("Grep", "Glob", "Read"):
        state["searched"] = True
        _save_state(state)
        return

    # Only act on Edit/Write
    if tool_name not in ("Edit", "Write"):
        return

    # Already searched or already warned — pass through
    if state.get("searched") or state.get("warned"):
        return

    # First Edit/Write without prior search — warn once
    file_path = data.get("tool_input", {}).get("file_path", "")

    # Skip non-code files (markdown, config, etc.)
    ext = os.path.splitext(file_path)[1].lower()
    if ext in (".md", ".json", ".yaml", ".yml", ".toml", ".txt", ""):
        return

    state["warned"] = True
    _save_state(state)

    output_context(
        "PreToolUse",
        "[Search-First] このセッションでまだ検索（Grep/Glob）が実行されていません。"
        "既存コードを確認してから編集することを推奨します。"
        "この警告はセッション中1回のみ表示されます。",
    )


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        print(f"[search-first-gate] error: {e}", file=sys.stderr)
