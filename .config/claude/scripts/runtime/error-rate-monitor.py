#!/usr/bin/env python3
"""Error Rate Supervisor — Bash エラーのスパイクを検出する PostToolUse hook。

AlphaLab の Supervisor が「エラーレートスパイク時にドメイン知識をパッチ」する
機能に着想。
5分ウィンドウで同系統エラーが3回以上発生した場合に警告を出力する。

Triggered by: PostToolUse (matcher: Bash)
Input: stdin (hook JSON passthrough)
Output: stdout (passthrough), stderr (warnings)
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

# --- エラー分類パターン（failure-taxonomy.md 準拠） ---
ERROR_PATTERNS: dict[str, re.Pattern] = {
    "FM-001": re.compile(
        r"nil pointer|cannot read propert|undefined is not|NoneType", re.IGNORECASE
    ),
    "FM-008": re.compile(
        r"build failed|compilation failed|type.?error|cannot find module", re.IGNORECASE
    ),
    "PERM": re.compile(r"permission denied|EACCES", re.IGNORECASE),
    "NOTFOUND": re.compile(
        r"no such file|ENOENT|command not found|not found", re.IGNORECASE
    ),
    "SYNTAX": re.compile(r"syntax error|SyntaxError|unexpected token", re.IGNORECASE),
    "TIMEOUT": re.compile(r"timed? ?out|ETIMEDOUT", re.IGNORECASE),
}

WINDOW_SECONDS = 300  # 5分
SPIKE_THRESHOLD = 3  # 同系統3回でスパイク


def classify_error(text: str) -> str:
    """エラーテキストを FM コードに分類する。"""
    for code, pattern in ERROR_PATTERNS.items():
        if pattern.search(text):
            return code
    return "UNKNOWN"


def get_state_path() -> Path:
    """セッション固有の状態ファイルパスを返す。"""
    session_id = (
        os.environ.get("CLAUDE_SESSION_ID")
        or os.environ.get("CLAUDE_CONVERSATION_ID")
        or str(os.getpid())
    )
    return Path(f"/tmp/claude-error-rate-{session_id}.json")


def load_state(path: Path) -> dict:
    """状態ファイルを読み込む。"""
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        sys.stderr.write(f"[error-rate-monitor] state load failed: {e}\n")
    return {"errors": []}


def save_state(path: Path, state: dict) -> None:
    """状態ファイルを保存する。"""
    try:
        path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    except OSError as e:
        sys.stderr.write(f"[error-rate-monitor] state save failed: {e}\n")


def prune_old_errors(errors: list[dict], now: float) -> list[dict]:
    """ウィンドウ外の古いエラーを除去する。"""
    cutoff = now - WINDOW_SECONDS
    return [e for e in errors if e.get("ts", 0) > cutoff]


def append_to_negative_knowledge(fm_code: str, error_text: str, count: int) -> None:
    """negative-knowledge.md にスパイクパターンを追記する（存在する場合のみ）。"""
    try:
        neg_path = (
            Path(__file__).resolve().parent.parent.parent
            / ".config"
            / "claude"
            / "references"
            / "negative-knowledge.md"
        )
        # dotfiles 構造: scripts/runtime/ → dotfiles root
        # 代替パス: symlink 経由
        alt_path = Path.home() / ".claude" / "references" / "negative-knowledge.md"

        target = (
            neg_path if neg_path.exists() else (alt_path if alt_path.exists() else None)
        )
        if not target:
            return

        from datetime import datetime, timezone

        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        anti_pattern = f"[{fm_code}] Error spike ({count}x in 5min): {error_text[:80]}"
        entry = (
            f"| {ts} | auto | {anti_pattern} | Error rate spike detected | failure |"
        )

        content = target.read_text(encoding="utf-8")
        lines = content.splitlines()
        lines.append(entry)

        # ローテート: ヘッダ7行 + データ200行
        header = lines[:7]
        data_lines = lines[7:]
        if len(data_lines) > 200:
            data_lines = data_lines[-200:]
        lines = header + data_lines

        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError as e:
        sys.stderr.write(f"[error-rate-monitor] negative-knowledge write failed: {e}\n")


def main() -> None:
    # stdin パススルー
    data = sys.stdin.read()
    sys.stdout.write(data)

    try:
        hook_input = json.loads(data) if data.strip() else {}
    except json.JSONDecodeError:
        return

    # Bash ツールのエラーのみ処理
    tool_name = hook_input.get("tool_name", "")
    if tool_name != "Bash":
        return

    response = hook_input.get("tool_response", {})
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except (json.JSONDecodeError, TypeError):
            return

    stderr = str(response.get("stderr", ""))
    exit_code = response.get("exit_code", 0)

    # エラーなしならスキップ
    if exit_code == 0 and not stderr.strip():
        return

    # エラー分類
    error_text = stderr[:500] if stderr else f"exit_code={exit_code}"
    fm_code = classify_error(error_text)

    # 状態を更新
    now = time.time()
    state_path = get_state_path()
    state = load_state(state_path)

    errors = prune_old_errors(state.get("errors", []), now)
    errors.append({"ts": now, "fm": fm_code, "text": error_text[:200]})
    state["errors"] = errors
    save_state(state_path, state)

    # スパイク検出: 同系統エラーが閾値以上
    same_fm_count = sum(1 for e in errors if e.get("fm") == fm_code)
    if same_fm_count >= SPIKE_THRESHOLD:
        spike_header = (
            f"\n[ERROR_RATE_SPIKE] {fm_code}: {same_fm_count} errors"
            f" in {WINDOW_SECONDS}s window.\n"
        )
        warning = (
            spike_header
            + "このアプローチは壊れている可能性があります。再プランを推奨します。\n"
            + f"直近のエラー: {error_text[:100]}\n"
        )
        sys.stderr.write(warning)

        # negative-knowledge.md に追記
        append_to_negative_knowledge(fm_code, error_text, same_fm_count)


if __name__ == "__main__":
    main()
