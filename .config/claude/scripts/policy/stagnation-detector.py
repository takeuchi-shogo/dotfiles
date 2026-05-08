#!/usr/bin/env python3
"""Stagnation detector — suggests strategy switches on repeated failures.

Triggered by: hooks.PostToolUse (Bash)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext suggestion on stdout

EvoX demand-driven pattern: only intervene when stagnation is detected.
While progress is being made, this hook stays silent.
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import (
    check_tool,
    get_emitter,
    load_hook_input,
    output_context,
    output_passthrough,
    run_hook,
)
from storage import get_data_dir

emit = get_emitter()

# --- Constants ---
WINDOW_SIZE = 20
CONSECUTIVE_FAILURE_THRESHOLD = 5
SAME_ERROR_TYPE_THRESHOLD = 3
SAME_FILE_EDIT_THRESHOLD = 5
COOLDOWN_STEPS = 3
CONSOLIDATE_INTERVAL = 20  # Successful commands between knowledge consolidation prompts
SESSION_MAX_AGE_SECONDS = 7200  # 2h
STATE_FILE = get_data_dir() / "stagnation-state.json"

ERROR_PATTERNS = [
    re.compile(r"Traceback \(most recent call last\)"),
    re.compile(r"(?:Error|Exception):\s+\S"),
    re.compile(r"panic:\s"),
    re.compile(r"FAIL\s+\S"),
    re.compile(r"npm ERR!"),
    re.compile(r"error\[E\d+\]"),
    re.compile(r"cannot find module", re.IGNORECASE),
    re.compile(r"undefined reference"),
    re.compile(r"segmentation fault", re.IGNORECASE),
    re.compile(r"fatal error"),
    re.compile(r"compilation failed"),
    re.compile(r"build failed", re.IGNORECASE),
    re.compile(r"SyntaxError:"),
    re.compile(r"TypeError:"),
    re.compile(r"ReferenceError:"),
]

IGNORE_COMMANDS = [
    "git status",
    "git log",
    "git diff",
    "git branch",
    "ls",
    "cat",
    "head",
    "tail",
    "pwd",
    "which",
    "echo",
    "codex",
    "gemini",
]

# --- Friction Detection Constants ---

COMMAND_FAMILIES: dict[str, list[str]] = {
    "validation": [
        "pytest",
        "npm test",
        "cargo test",
        "go test",
        "task validate",
        "npm run lint",
        "eslint",
        "biome",
        "ruff",
        "mypy",
        "tsc",
    ],
    "build": ["npm run build", "cargo build", "go build", "make", "task build"],
    "install": ["npm install", "pip install", "cargo add", "go get", "brew install"],
}

ENVIRONMENT_ERROR_CLASSES: dict[str, re.Pattern] = {
    "permission_denied": re.compile(
        r"permission denied|EACCES|Operation not permitted", re.IGNORECASE
    ),
    "file_not_found": re.compile(
        r"No such file or directory|ENOENT|FileNotFoundError", re.IGNORECASE
    ),
    "timeout": re.compile(r"timed? ?out|ETIMEDOUT|deadline exceeded", re.IGNORECASE),
    "rate_limit": re.compile(r"rate limit|429|too many requests", re.IGNORECASE),
    "port_in_use": re.compile(r"EADDRINUSE|address already in use", re.IGNORECASE),
}

FRICTION_ACTION_SURFACES = {
    "validation_ping_pong": "narrow_validation",
    "environment_blocker": "fix_environment",
}

VALIDATION_PING_PONG_THRESHOLD = 3
ENVIRONMENT_BLOCKER_THRESHOLD = 2


# --- State Management ---


def _new_state() -> dict:
    return {
        "created_at": time.time(),
        "bash_history": [],
        "consecutive_failures": 0,
        "successful_commands": 0,
        "same_file_edits": {},
        "last_suggestion_time": 0.0,
    }


def load_state() -> dict:
    """State file を読み込む。古い場合は空の state を返す。"""
    if not STATE_FILE.exists():
        return _new_state()
    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        created = state.get("created_at", 0)
        if time.time() - created > SESSION_MAX_AGE_SECONDS:
            return _new_state()
        return state
    except (json.JSONDecodeError, OSError) as exc:
        emit("error", {"message": f"stagnation state load failed: {exc}"})
        return _new_state()


def save_state(state: dict) -> None:
    """State file をアトミックに上書き保存。"""
    import os

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, STATE_FILE)


# --- Detection Logic ---


def _has_error(output: str) -> str | None:
    """出力からエラーパターンを検出する。"""
    for pattern in ERROR_PATTERNS:
        match = pattern.search(output)
        if match:
            return match.group(0)
    return None


def _is_info_command(command: str) -> bool:
    cmd_lower = command.strip().lower()
    return any(cmd_lower.startswith(ic) for ic in IGNORE_COMMANDS)


def _classify_command_family(command: str) -> str | None:
    """コマンドをファミリに分類する。"""
    cmd_lower = command.strip().lower()
    for family, prefixes in COMMAND_FAMILIES.items():
        if any(cmd_lower.startswith(p) for p in prefixes):
            return family
    return None


def _classify_error_class(output: str) -> str | None:
    """出力から環境エラークラスを分類する。"""
    for cls, pattern in ENVIRONMENT_ERROR_CLASSES.items():
        if pattern.search(output):
            return cls
    return None


def _extract_file_target(command: str) -> str | None:
    """Bash コマンドから対象ファイルパスを推定する。"""
    match = re.search(
        r"(?:^|\s)(\S+\.(?:py|js|ts|tsx|go|rs|md|json|yaml|yml))\b", command
    )
    return match.group(1) if match else None


def _now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def detect_stagnation(state: dict) -> tuple[str, str] | None:
    """停滞パターンを検出する。(stagnation_type, suggestion) を返す。"""
    history = state.get("bash_history", [])
    if len(history) < 3:
        return None

    # Cooldown: 前回提案後 30 秒は再提案しない
    if time.time() - state.get("last_suggestion_time", 0.0) < 30:
        return None

    # Pattern 1: 同種エラーの反復 (直近 6 件中 3+ 回)
    recent_errors = [h for h in history[-6:] if h["exit_code_inferred"] == "error"]
    if len(recent_errors) >= SAME_ERROR_TYPE_THRESHOLD:
        error_cmds = [(e["command"].split() or [""])[0] for e in recent_errors]
        if len(set(error_cmds)) <= 2:
            return (
                "same_error_type",
                "同種エラーが3回連続しています。structural variation を検討してください"
                "（別アプローチ、別ツール、問題の分解）。",
            )

    # Pattern 2: 連続失敗 (5 回)
    consecutive = state.get("consecutive_failures", 0)
    if consecutive >= CONSECUTIVE_FAILURE_THRESHOLD:
        return (
            "consecutive_failures",
            f"連続 {consecutive} 回失敗しています。"
            "`/codex:rescue --read-only` で根本原因分析を推奨します。"
            "現在のアプローチに固執せず、問題を再定義してください。",
        )

    # Pattern 3: 同一ファイルへの過剰編集 (5 回超)
    file_edits = state.get("same_file_edits", {})
    for filepath, count in file_edits.items():
        if count > SAME_FILE_EDIT_THRESHOLD:
            name = Path(filepath).name
            return (
                "excessive_file_edits",
                f"{name} への編集が {count} 回を超えました。"
                "設計の見直しを検討してください（refinement 限界）。"
                "ファイルの責務分割や、異なる設計パターンの適用を検討。",
            )

    # Pattern 4: alignment tipping — 改善提案の方向性が偏り続ける
    if len(history) >= WINDOW_SIZE:
        error_types = [
            h.get("error_class") or (h.get("command", "").split() or ["unknown"])[0]
            for h in history[-WINDOW_SIZE:]
            if h["exit_code_inferred"] == "error"
        ]
        if error_types:
            unique_ratio = len(set(error_types)) / len(error_types)
            if unique_ratio < 0.3 and len(error_types) >= 5:
                dominant = max(set(error_types), key=error_types.count)
                return (
                    "alignment_tipping",
                    f"エラーパターンが '{dominant}' に偏っています"
                    f" (多様性: {unique_ratio:.0%})。"
                    "同一方向の修正を繰り返している可能性があります。"
                    "問題を別の角度から捉え直すか、人間にエスカレーションしてください。",
                )

    return None


# --- Friction Detection ---


def detect_friction(state: dict) -> dict | None:
    """Friction パターンを検出する。検出時は friction event dict を返す。"""
    history = state.get("bash_history", [])
    if len(history) < 2:
        return None

    # Cooldown: stagnation と共有
    if time.time() - state.get("last_suggestion_time", 0.0) < 30:
        return None

    recent = history[-8:]

    # Pattern: validation_ping_pong
    validation_failures = [
        h
        for h in recent
        if h.get("command_family") == "validation"
        and h["exit_code_inferred"] == "error"
    ]
    if len(validation_failures) >= VALIDATION_PING_PONG_THRESHOLD:
        commands = [h["command"] for h in validation_failures]
        return {
            "friction_class": "validation_ping_pong",
            "action_surface": "narrow_validation",
            "severity": "warning",
            "command_family": "validation",
            "target_hint": commands[-1][:200],
            "evidence": {
                "commands": commands[-5:],
                "failure_count": len(validation_failures),
            },
        }

    # Pattern: environment_blocker
    recent_env_errors: dict[str, list[str]] = {}
    for h in recent:
        ec = h.get("error_class")
        if ec:
            recent_env_errors.setdefault(ec, []).append(h["command"])
    for error_class, cmds in recent_env_errors.items():
        if len(cmds) >= ENVIRONMENT_BLOCKER_THRESHOLD:
            return {
                "friction_class": "environment_blocker",
                "action_surface": "fix_environment",
                "severity": "warning",
                "command_family": "environment",
                "target_hint": error_class,
                "evidence": {
                    "error_class": error_class,
                    "commands": cmds[-5:],
                    "failure_count": len(cmds),
                },
            }

    return None


# --- Main ---


def main() -> None:
    data = load_hook_input()
    if not data:
        return
    if not check_tool(data, "Bash"):
        output_passthrough(data)
        return

    command = data.get("tool_input", {}).get("command", "")
    output = data.get("tool_output", "") or ""
    if not isinstance(output, str):
        output = str(output)

    if _is_info_command(command) or len(output) < 10:
        output_passthrough(data)
        return

    # State 更新
    state = load_state()
    error_match = _has_error(output)
    is_error = error_match is not None

    entry = {
        "command": command[:200],
        "exit_code_inferred": "error" if is_error else "success",
        "timestamp": _now_iso(),
        "file_target": _extract_file_target(command),
        "command_family": _classify_command_family(command),
        "error_class": _classify_error_class(output) if is_error else None,
    }

    state["bash_history"].append(entry)
    state["bash_history"] = state["bash_history"][-WINDOW_SIZE:]

    if is_error:
        state["consecutive_failures"] += 1
    else:
        state["consecutive_failures"] = 0
        state["successful_commands"] = state.get("successful_commands", 0) + 1

    # ファイル編集追跡 (成功した実行のみ)
    file_target = entry.get("file_target")
    if file_target and not is_error:
        edits = state.get("same_file_edits", {})
        edits[file_target] = edits.get(file_target, 0) + 1
        state["same_file_edits"] = edits

    # Friction 検出（stagnation より先 — より具体的な action surface を提供）
    friction = detect_friction(state)
    if friction:
        state["last_suggestion_time"] = time.time()

        try:
            from session_events import emit_event

            emit_event("pattern", {"type": "friction_event", **friction})
        except Exception as exc:
            emit("error", {"message": f"friction event emit failed: {exc}"})

        action = FRICTION_ACTION_SURFACES.get(friction["friction_class"], "replan")
        emit(
            "pattern",
            {
                "type": "friction_detected",
                "friction_class": friction["friction_class"],
                "action_surface": action,
                "message": f"Friction: {friction['friction_class']}",
            },
        )

        save_state(state)
        output_context(
            "PostToolUse",
            f"[Friction: {friction['friction_class']}] "
            f"推奨: {action}。同じアプローチの繰り返しではなく戦略変更を検討。",
        )
        return

    # 停滞検知（friction に該当しない汎用パターン）
    result = detect_stagnation(state)
    if result:
        stagnation_type, suggestion = result
        state["last_suggestion_time"] = time.time()

        emit(
            "pattern",
            {
                "type": "stagnation_detected",
                "stagnation_type": stagnation_type,
                "consecutive_failures": state["consecutive_failures"],
                "message": suggestion,
            },
        )

        save_state(state)
        output_context("PostToolUse", f"[Stagnation Detector] {suggestion}")
        return

    # Consolidate heartbeat（CORAL inspired — 成功パスでの定期的な知識整理）
    successful = state.get("successful_commands", 0)
    if successful >= CONSOLIDATE_INTERVAL:
        state["successful_commands"] = 0
        emit(
            "pattern",
            {
                "type": "consolidate_heartbeat",
                "successful_commands": CONSOLIDATE_INTERVAL,
            },
        )
        save_state(state)
        output_context(
            "PostToolUse",
            "[Consolidate Heartbeat] "
            "成功が続いています。最近うまくいったアプローチを振り返り、"
            "再利用可能なパターンがあれば記録を検討してください。",
        )
        return

    save_state(state)
    output_passthrough(data)


if __name__ == "__main__":
    run_hook("stagnation-detector", main)
