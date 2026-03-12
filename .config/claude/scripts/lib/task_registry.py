#!/usr/bin/env python3
"""タスクレジストリ — Async/Scheduled サブエージェントの成果物追跡"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

REGISTRY_PATH = Path(
    os.environ.get(
        "TASK_REGISTRY_PATH",
        os.path.expanduser("~/.claude/agent-memory/task-registry.jsonl"),
    )
)


def _next_id() -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    seq = 1
    if REGISTRY_PATH.exists():
        for line in REGISTRY_PATH.read_text().splitlines():
            try:
                entry = json.loads(line)
                if entry.get("id", "").startswith(f"tr-{today}-"):
                    num = int(entry["id"].split("-")[-1])
                    seq = max(seq, num + 1)
            except (json.JSONDecodeError, ValueError):
                continue
    return f"tr-{today}-{seq:04d}"


def register(
    pattern: str,
    source_skill: str,
    task_description: str,
    output_path: str | None = None,
    agent_id: str | None = None,
    cron_id: str | None = None,
) -> str:
    """新しいタスクをレジストリに登録し、ID を返す。"""
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

    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_PATH, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry_id


def update_status(
    entry_id: str,
    status: str,
    output_path: str | None = None,
    error: str | None = None,
) -> None:
    """既存エントリのステータスを更新（同じ id で新しい行を追記）。"""
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
