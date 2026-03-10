#!/usr/bin/env python3
from __future__ import annotations
"""Checkpoint manager — auto-saves session state during heavy work.

Triggered by: hooks.PostToolUse (Edit|Write)
Input: stdin JSON (hook protocol)
Output: stdout JSON (with optional additionalContext)
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

EDIT_THRESHOLD = 15
CONTEXT_PCT_THRESHOLD = 60
TIME_THRESHOLD_SECONDS = 30 * 60
COOLDOWN_SECONDS = 5 * 60
MAX_CHECKPOINTS = 5


def _get_state_dir() -> Path:
    return Path(os.environ.get(
        "CLAUDE_SESSION_STATE_DIR",
        os.path.join(os.environ.get("HOME", ""), ".claude", "session-state"),
    ))


def _get_counter_path() -> Path:
    return _get_state_dir() / "edit-counter.json"


def _read_counter() -> dict:
    try:
        return json.loads(_get_counter_path().read_text())
    except Exception:
        return {"count": 0, "lastReset": time.time() * 1000, "recentEdits": []}


def _last_checkpoint_time(state_dir: Path | None = None) -> float:
    pointer = (state_dir or _get_state_dir()) / "last-checkpoint.json"
    try:
        data = json.loads(pointer.read_text())
        return datetime.fromisoformat(data["timestamp"]).timestamp()
    except Exception:
        return 0.0


def should_checkpoint(
    counter: dict,
    last_checkpoint_time: float,
    context_pct: int = 0,
) -> str | bool:
    """checkpoint すべきか判定する。すべき場合は trigger 文字列を返す。"""
    now = time.time()

    if now - last_checkpoint_time < COOLDOWN_SECONDS:
        return False

    edit_count = counter.get("count", 0)

    if edit_count >= EDIT_THRESHOLD:
        return "auto:edit_threshold"

    if context_pct >= CONTEXT_PCT_THRESHOLD:
        return "auto:context_threshold"

    if last_checkpoint_time > 0 and (now - last_checkpoint_time) >= TIME_THRESHOLD_SECONDS:
        return "auto:time_threshold"

    if last_checkpoint_time == 0:
        session_start = counter.get("lastReset", now * 1000) / 1000
        if (now - session_start) >= TIME_THRESHOLD_SECONDS:
            return "auto:time_threshold"

    return False


def save_checkpoint(
    trigger: str,
    state_dir: Path | None = None,
    edit_count: int = 0,
    context_pct: int = 0,
    focus_files: list[str] | None = None,
    active_profile: str = "default",
) -> Path:
    """checkpoint を保存し、last-checkpoint.json ポインタを更新する。"""
    sd = state_dir or _get_state_dir()
    cp_dir = sd / "checkpoints"
    cp_dir.mkdir(parents=True, exist_ok=True)

    branch = _run_git("branch --show-current")
    git_status = _run_git("status --porcelain")

    ts = datetime.now(timezone.utc)
    data = {
        "timestamp": ts.isoformat(),
        "trigger": trigger,
        "working_on": _infer_working_on(focus_files, branch),
        "focus": (focus_files or [])[:10],
        "branch": branch,
        "git_status": git_status,
        "edit_count": edit_count,
        "context_usage_pct": context_pct,
        "active_profile": active_profile,
    }

    filename = f"checkpoint-{ts.strftime('%Y%m%dT%H%M%S')}.json"
    cp_path = cp_dir / filename
    cp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    pointer = sd / "last-checkpoint.json"
    pointer.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    _cleanup_old_checkpoints(cp_dir)
    return cp_path


def _cleanup_old_checkpoints(cp_dir: Path) -> None:
    files = sorted(cp_dir.glob("checkpoint-*.json"))
    while len(files) > MAX_CHECKPOINTS:
        files.pop(0).unlink(missing_ok=True)


def _run_git(args: str) -> str:
    try:
        result = subprocess.run(
            ["git"] + args.split(),
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def _infer_working_on(focus_files: list[str] | None, branch: str) -> str:
    if branch and branch not in ("master", "main"):
        return branch
    if focus_files:
        return Path(focus_files[0]).stem
    return ""


def _extract_focus_files(input_data: dict) -> list[str]:
    files = []
    tool_input = input_data.get("tool_input", {})
    fp = tool_input.get("file_path", "")
    if fp:
        files.append(fp)
    counter = _read_counter()
    for edit in counter.get("recentEdits", [])[-10:]:
        f = edit.get("file", "")
        if f and f not in files:
            files.append(f)
    return files


def main() -> None:
    data = sys.stdin.read()
    try:
        input_data = json.loads(data) if data.strip() else {}
    except json.JSONDecodeError:
        input_data = {}

    try:
        counter = _read_counter()
        lct = _last_checkpoint_time()
        trigger = should_checkpoint(counter, lct)

        if trigger:
            focus = _extract_focus_files(input_data)
            save_checkpoint(
                trigger=trigger,
                edit_count=counter.get("count", 0),
                focus_files=focus,
            )
            json.dump({
                **input_data,
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": (
                        f"[Checkpoint] セッション状態を保存しました "
                        f"(trigger: {trigger}, edits: {counter.get('count', 0)})"
                    ),
                },
            }, sys.stdout)
            return
    except Exception:
        pass

    sys.stdout.write(data)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
