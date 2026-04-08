#!/usr/bin/env python3
"""Approval fatigue guard — detects rapid edit cycles without verification.

Triggered by: hooks.PostToolUse (Edit|Write)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext advisory on stdout

Tracks edit count per session. When edits exceed threshold without
a test run, suggests pausing to verify.

Advisory only — never blocks.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import (
    load_hook_input,
    output_passthrough,
    output_context,
    run_hook,
    get_emitter,
)

emit = get_emitter()

_EDIT_THRESHOLD = 15  # edits before warning
_TIME_WINDOW = 600  # 10 minutes
_COOLDOWN = 300  # 5 min between warnings
_STATE_FILE = (
    Path(
        os.environ.get(
            "CLAUDE_SESSION_STATE_DIR",
            os.path.join(
                os.environ.get("HOME", ""),
                ".claude",
                "session-state",
            ),
        ),
    )
    / "fatigue-guard.json"
)


def _load_state() -> dict:
    try:
        return json.loads(_STATE_FILE.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(
            f"[approval-fatigue] state load: {exc}",
            file=sys.stderr,
        )
        return {
            "edits": [],
            "last_warning": 0,
            "last_test": 0,
        }


def _save_state(state: dict) -> None:
    try:
        _STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _STATE_FILE.write_text(json.dumps(state))
    except OSError as exc:
        print(
            f"[approval-fatigue] state save: {exc}",
            file=sys.stderr,
        )


def main() -> None:
    data = load_hook_input()
    if not data:
        return

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Edit", "Write"):
        output_passthrough(data)
        return

    now = time.time()
    state = _load_state()

    # Record this edit
    edits = state.get("edits", [])
    edits.append(now)
    # Prune old edits outside time window
    edits = [t for t in edits if now - t < _TIME_WINDOW]
    state["edits"] = edits

    edit_count = len(edits)
    last_warning = state.get("last_warning", 0)
    last_test = state.get("last_test", 0)

    _save_state(state)

    # Check if we should warn
    if edit_count < _EDIT_THRESHOLD:
        output_passthrough(data)
        return

    if now - last_warning < _COOLDOWN:
        output_passthrough(data)
        return

    # Check if tests have been run recently
    mins = int(_TIME_WINDOW / 60)
    if last_test > 0 and now - last_test < _TIME_WINDOW:
        output_passthrough(data)
        return

    state["last_warning"] = now
    _save_state(state)

    emit(
        "approval_fatigue",
        {"edit_count": edit_count, "window_min": mins},
    )

    msg = (
        f"[approval-fatigue] {mins}分間に {edit_count} 回の編集。"
        "テスト実行なし。\n"
        "💡 一旦手を止めて、変更の方向性を確認してください:\n"
        "  - テストを実行して現状を確認\n"
        "  - Plan と照らし合わせて進捗を確認\n"
        "  - 泥沼化していないか振り返る"
    )
    output_context("PostToolUse", msg)


if __name__ == "__main__":
    run_hook("approval-fatigue-guard", main, fail_closed=False)
