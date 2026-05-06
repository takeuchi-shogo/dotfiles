#!/usr/bin/env python3
"""タスクレジストリ — Async/Scheduled サブエージェントの成果物追跡"""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

REGISTRY_PATH = Path(
    os.environ.get(
        "TASK_REGISTRY_PATH",
        os.path.expanduser("~/.claude/agent-memory/task-registry.jsonl"),
    )
)


def _next_id() -> str:
    """UUID で TOCTOU レースを回避し、日付プレフィックスで可読性を保持。"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    short_uuid = uuid.uuid4().hex[:6]
    return f"tr-{today}-{short_uuid}"


def _has_running_task() -> bool:
    """running 状態のタスクが存在するか確認。単一 in_progress 制約の強制。"""
    if not REGISTRY_PATH.exists():
        return False
    entries: dict[str, dict] = {}
    for line in REGISTRY_PATH.read_text().splitlines():
        try:
            entry = json.loads(line)
            eid = entry.get("id", "")
            if eid:
                entries.setdefault(eid, {}).update(entry)
        except json.JSONDecodeError:
            continue
    return any(e.get("status") == "running" for e in entries.values())


def register(
    pattern: str,
    source_skill: str,
    task_description: str,
    output_path: str | None = None,
    agent_id: str | None = None,
    cron_id: str | None = None,
    metadata: dict | None = None,
) -> str:
    """新しいタスクをレジストリに登録し、ID を返す。

    metadata は任意拡張点。parent_id（親タスク id）、query、token_usage
    など schema 必須でない構造化情報を格納する。
    """
    entry_id = _next_id()
    entry = {
        "id": entry_id,
        "pattern": pattern,
        "source_skill": source_skill,
        "task_description": task_description,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if output_path:
        entry["output_path"] = output_path
    if agent_id:
        entry["agent_id"] = agent_id
    if cron_id:
        entry["cron_id"] = cron_id
    if metadata:
        entry["metadata"] = metadata

    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_PATH, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry_id


def update_status(
    entry_id: str,
    status: str,
    output_path: str | None = None,
    error: str | None = None,
    metadata: dict | None = None,
) -> None:
    """既存エントリのステータスを更新（同じ id で新しい行を追記）。

    単一 in_progress 制約: running に遷移する場合、
    既に running のタスクがあれば ValueError を送出。
    """
    if status == "running" and _has_running_task():
        current = get_latest(entry_id)
        if not current or current.get("status") != "running":
            raise ValueError(
                "別のタスクが running 状態です。"
                "先に完了させてから新しいタスクを開始してください。"
            )
    update = {
        "id": entry_id,
        "status": status,
    }
    if status in ("completed", "failed", "cancelled"):
        update["completed_at"] = datetime.now(timezone.utc).isoformat()
    if output_path:
        update["output_path"] = output_path
    if error:
        update["error"] = error
    if metadata:
        update["metadata"] = metadata

    with open(REGISTRY_PATH, "a") as f:
        f.write(json.dumps(update, ensure_ascii=False) + "\n")


def get_latest(entry_id: str) -> dict | None:
    """指定 ID の最新エントリを取得（最後の行が有効）。"""
    if not REGISTRY_PATH.exists():
        return None
    result: dict = {}
    for line in REGISTRY_PATH.read_text().splitlines():
        try:
            entry = json.loads(line)
            if entry.get("id") == entry_id:
                result.update(entry)
        except json.JSONDecodeError:
            continue
    return result if result else None


def list_active() -> list[dict]:
    """pending/running のエントリ一覧を返す。"""
    if not REGISTRY_PATH.exists():
        return []
    entries: dict[str, dict] = {}
    for line in REGISTRY_PATH.read_text().splitlines():
        try:
            entry = json.loads(line)
            eid = entry.get("id", "")
            if eid:
                entries.setdefault(eid, {}).update(entry)
        except json.JSONDecodeError:
            continue
    return [e for e in entries.values() if e.get("status") in ("pending", "running")]
