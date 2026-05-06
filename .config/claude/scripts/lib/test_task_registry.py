#!/usr/bin/env python3
"""task_registry.py のテスト"""

import os
import tempfile
from pathlib import Path

# テスト用の一時ファイルを設定
tmpdir = tempfile.mkdtemp()
os.environ["TASK_REGISTRY_PATH"] = str(Path(tmpdir) / "test-registry.jsonl")

# テスト対象をインポート（環境変数設定後）
import importlib  # noqa: E402
import task_registry  # noqa: E402

importlib.reload(task_registry)
from task_registry import (  # noqa: E402
    register,
    update_status,
    get_latest,
    list_active,
    REGISTRY_PATH,
)


def test_register_and_get():
    entry_id = register("async", "research", "テストタスク")
    assert entry_id.startswith("tr-")
    result = get_latest(entry_id)
    assert result is not None
    assert result["status"] == "pending"
    assert result["source_skill"] == "research"


def test_update_status():
    entry_id = register("sync", "review", "レビュータスク")
    update_status(entry_id, "completed", output_path="/tmp/result.md")
    result = get_latest(entry_id)
    assert result["status"] == "completed"
    assert result["output_path"] == "/tmp/result.md"
    assert "completed_at" in result


def test_list_active():
    REGISTRY_PATH.unlink(missing_ok=True)
    id1 = register("async", "research", "アクティブ1")
    id2 = register("scheduled", "manual", "アクティブ2")
    update_status(id1, "running")
    id3 = register("sync", "review", "完了済み")
    update_status(id3, "completed")
    active = list_active()
    active_ids = [e["id"] for e in active]
    assert id1 in active_ids
    assert id2 in active_ids
    assert id3 not in active_ids


def test_metadata_roundtrip():
    """metadata は register と update_status の両方で保存される。"""
    parent_id = register("async", "research", "親タスク")
    child_id = register(
        "sync",
        "research",
        "子タスク",
        metadata={"parent_id": parent_id, "query": "test"},
    )
    result = get_latest(child_id)
    assert result["metadata"]["parent_id"] == parent_id
    assert result["metadata"]["query"] == "test"

    update_status(
        child_id,
        "completed",
        metadata={"token_usage": 1234, "duration_ms": 5678},
    )
    final = get_latest(child_id)
    assert final["metadata"]["token_usage"] == 1234
    assert final["metadata"]["duration_ms"] == 5678


if __name__ == "__main__":
    test_register_and_get()
    print("PASS: test_register_and_get")
    test_update_status()
    print("PASS: test_update_status")
    test_list_active()
    print("PASS: test_list_active")
    test_metadata_roundtrip()
    print("PASS: test_metadata_roundtrip")
    print("All tests passed!")
