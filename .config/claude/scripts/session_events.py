"""AutoEvolve session event collector.

セッション中のイベントを一時ファイルに蓄積し、
セッション終了時に jsonl にフラッシュする共有モジュール。

Usage (from other hooks):
    from session_events import emit_event
    emit_event("error", {"message": "TypeError", "command": "npm test"})
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def _get_data_dir() -> Path:
    """データディレクトリを遅延評価で返す。

    テスト時に AUTOEVOLVE_DATA_DIR を差し替えられるよう、
    呼び出しごとに環境変数を読む。
    """
    return Path(os.environ.get(
        "AUTOEVOLVE_DATA_DIR",
        os.path.join(os.environ.get("HOME", ""), ".claude", "agent-memory"),
    ))


def _temp_path() -> Path:
    return _get_data_dir() / "current-session.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def emit_event(category: str, data: dict) -> None:
    """セッション中のイベントを一時ファイルに追記する。"""
    path = _temp_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"timestamp": _now_iso(), "category": category, **data}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def flush_session() -> list[dict]:
    """一時ファイルのイベントを全て読み出し、ファイルを削除する。"""
    path = _temp_path()
    if not path.exists():
        return []
    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    path.unlink(missing_ok=True)
    return events


def append_to_learnings(filename: str, data: dict) -> None:
    """learnings/ ディレクトリに jsonl エントリを追記する。"""
    path = _get_data_dir() / "learnings" / f"{filename}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"timestamp": _now_iso(), **data}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def append_to_metrics(data: dict) -> None:
    """metrics/ ディレクトリにセッションメトリクスを追記する。"""
    path = _get_data_dir() / "metrics" / "session-metrics.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"timestamp": _now_iso(), **data}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
