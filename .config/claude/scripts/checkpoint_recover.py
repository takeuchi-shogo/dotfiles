#!/usr/bin/env python3
from __future__ import annotations
"""Checkpoint recovery — detects abnormal session end and injects recovery context.

Triggered by: hooks.SessionStart
Output: stdout text (SessionStart hook protocol)
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


def _get_state_dir() -> Path:
    return Path(os.environ.get(
        "CLAUDE_SESSION_STATE_DIR",
        os.path.join(os.environ.get("HOME", ""), ".claude", "session-state"),
    ))


def check_recovery(state_dir: Path | None = None) -> str | None:
    """前回セッションの異常終了を検出し、復元メッセージを返す。"""
    sd = state_dir or _get_state_dir()
    cp_path = sd / "last-checkpoint.json"

    if not cp_path.exists():
        return None

    try:
        cp = json.loads(cp_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None

    try:
        cp_time = datetime.fromisoformat(cp["timestamp"])
    except (KeyError, ValueError):
        return None

    now = datetime.now(timezone.utc)

    if now - cp_time > timedelta(hours=24):
        return None

    ss_path = sd / "last-session.json"
    if ss_path.exists():
        try:
            ss = json.loads(ss_path.read_text())
            ss_time = datetime.fromisoformat(ss["timestamp"])
            if ss_time >= cp_time:
                return None
        except (json.JSONDecodeError, KeyError, ValueError):
            pass

    lines = [
        "[Checkpoint Recovery] 前回セッションが中断された可能性があります。",
        f"  最後の checkpoint: {cp.get('timestamp', 'unknown')}",
    ]
    if cp.get("working_on"):
        lines.append(f"  作業中: {cp['working_on']}")
    if cp.get("focus"):
        files = ", ".join(cp["focus"][:5])
        lines.append(f"  フォーカス: {files}")
    if cp.get("branch"):
        lines.append(f"  ブランチ: {cp['branch']}")
    if cp.get("git_status"):
        lines.append(f"  未コミット変更: {cp['git_status'][:200]}")
    if cp.get("edit_count"):
        lines.append(f"  編集回数: {cp['edit_count']}")

    return "\n".join(lines)


def main() -> None:
    try:
        msg = check_recovery()
        if msg:
            print(msg)
    except Exception:
        pass


if __name__ == "__main__":
    main()
