#!/usr/bin/env python3
"""Cluster error events from learnings/*.jsonl by FM failure-mode codes."""

from __future__ import annotations

import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from storage import get_data_dir  # noqa: E402

_FM_RE = re.compile(r"FM-\d{3}")

logger = logging.getLogger("autoevolve")


def _setup_logger() -> None:
    if logger.handlers:
        return
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)


def _read_error_events(data_dir: Path) -> list[dict]:
    """learnings/ 配下の全 .jsonl から category==error を抽出する。"""
    learnings_dir = data_dir / "learnings"
    if not learnings_dir.exists():
        return []

    events: list[dict] = []
    for jsonl_file in learnings_dir.glob("*.jsonl"):
        try:
            lines = jsonl_file.read_text(encoding="utf-8").splitlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("category") == "error":
                        entry["_source_file"] = jsonl_file.name
                        events.append(entry)
                except json.JSONDecodeError:
                    continue
        except OSError as exc:
            logger.warning("failure-clusterer: failed to read %s: %s", jsonl_file, exc)

    return events


def _extract_fm_code(event: dict) -> str:
    """イベントから FM コードを抽出する。なければ FM-UNKNOWN。"""
    # 直接 failure_mode フィールドを優先
    fm = event.get("failure_mode", "") or ""
    if _FM_RE.match(fm.strip()):
        return fm.strip()

    # メッセージ・データの文字列全体を検索
    searchable = json.dumps(event, ensure_ascii=False)
    match = _FM_RE.search(searchable)
    if match:
        return match.group()

    return "FM-UNKNOWN"


def _make_instance(event: dict) -> dict:
    """クラスタ instances 用のエントリを構築する。"""
    data = event if "data" not in event else {**event.get("data", {}), **event}
    return {
        "session_id": data.get("session_id", ""),
        "timestamp": data.get("timestamp", ""),
        "message": str(data.get("message", data.get("error", "")))[:200],
        "file": data.get("file", data.get("path", "")),
    }


def _date_str(ts: str) -> str:
    """ISO 8601 タイムスタンプを YYYY-MM-DD に変換する。空文字はそのまま返す。"""
    if not ts:
        return ""
    try:
        return ts[:10]
    except Exception:
        return ""


def _build_clusters(events: list[dict]) -> dict[str, dict]:
    """イベント一覧から FM コード別クラスタ辞書を構築する。"""
    clusters: dict[str, dict] = {}

    for event in events:
        fm_code = _extract_fm_code(event)
        instance = _make_instance(event)
        ts = instance.get("timestamp", "")

        if fm_code not in clusters:
            clusters[fm_code] = {
                "fm_code": fm_code,
                "instances": [],
                "first_seen": _date_str(ts),
                "last_seen": _date_str(ts),
            }

        cluster = clusters[fm_code]
        cluster["instances"].append(instance)

        date = _date_str(ts)
        if date:
            if not cluster["first_seen"] or date < cluster["first_seen"]:
                cluster["first_seen"] = date
            if not cluster["last_seen"] or date > cluster["last_seen"]:
                cluster["last_seen"] = date

    return clusters


_FM_ROOT_CAUSES: dict[str, str] = {
    "FM-001": "Null Safety Violation",
    "FM-002": "Error Suppression",
    "FM-003": "Dependency Drift",
    "FM-004": "Type Safety Violation",
    "FM-005": "Boundary Validation Miss",
    "FM-006": "Permission/Access Error",
    "FM-007": "Module Resolution Failure",
    "FM-008": "Build/Compilation Failure",
    "FM-009": "Resource Exhaustion",
    "FM-010": "Security Vulnerability",
    "FM-011": "Plan Adherence Failure",
    "FM-012": "Information Invention",
    "FM-013": "Tool Output Misinterpretation",
    "FM-014": "Intent Misalignment",
    "FM-015": "Premature Action",
    "FM-016": "Result Fabrication",
    "FM-017": "Feature Stubbing",
    "FM-UNKNOWN": "Unknown Error",
}


def _load_existing(output_path: Path) -> dict:
    """既存クラスタファイルを読み込む。存在しなければ空の構造を返す。"""
    if not output_path.exists():
        return {"clusters": []}
    try:
        data = json.loads(output_path.read_text(encoding="utf-8"))
        if "clusters" not in data:
            data["clusters"] = []
        return data
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("failure-clusterer: failed to load existing clusters: %s", exc)
        return {"clusters": []}


def _merge_clusters(existing: dict, new_clusters: dict[str, dict]) -> list[dict]:
    """既存クラスタと新クラスタをマージして最終リストを返す。"""
    # 既存クラスタを fm_code でインデックス化
    existing_by_fm: dict[str, dict] = {}
    for cluster in existing.get("clusters", []):
        fm = cluster.get("fm_code", "")
        if fm:
            existing_by_fm[fm] = cluster

    # 新インスタンスをマージ
    for fm_code, new_cluster in new_clusters.items():
        if fm_code in existing_by_fm:
            ex = existing_by_fm[fm_code]
            ex_instances = ex.get("instances", [])
            # タイムスタンプで重複排除（session_id + timestamp が同じものは除く）
            existing_keys = {
                (i.get("session_id", ""), i.get("timestamp", "")) for i in ex_instances
            }
            added = 0
            for inst in new_cluster["instances"]:
                key = (inst.get("session_id", ""), inst.get("timestamp", ""))
                if key not in existing_keys:
                    ex_instances.append(inst)
                    existing_keys.add(key)
                    added += 1

            ex["instances"] = ex_instances
            ex["frequency"] = len(ex_instances)

            # first_seen / last_seen を更新
            new_first = new_cluster.get("first_seen", "")
            new_last = new_cluster.get("last_seen", "")
            if new_first and (not ex.get("first_seen") or new_first < ex["first_seen"]):
                ex["first_seen"] = new_first
            if new_last and (not ex.get("last_seen") or new_last > ex["last_seen"]):
                ex["last_seen"] = new_last

            if added:
                logger.info(
                    "failure-clusterer: merged %d new instances into %s", added, fm_code
                )
        else:
            # 新クラスタを追加
            idx = len(existing_by_fm) + 1
            cluster_id = f"cluster-{idx:03d}"
            existing_by_fm[fm_code] = {
                "id": cluster_id,
                "fm_code": fm_code,
                "root_cause": _FM_ROOT_CAUSES.get(fm_code, "Unknown"),
                "instances": new_cluster["instances"],
                "frequency": len(new_cluster["instances"]),
                "first_seen": new_cluster.get("first_seen", ""),
                "last_seen": new_cluster.get("last_seen", ""),
                "status": "open",
            }
            logger.info(
                "failure-clusterer: created new cluster %s for %s (%d instances)",
                cluster_id,
                fm_code,
                len(new_cluster["instances"]),
            )

    # frequency を再計算（既存クラスタで instances がすでにあった場合）
    for cluster in existing_by_fm.values():
        cluster["frequency"] = len(cluster.get("instances", []))

    # fm_code でソートして返す
    return sorted(existing_by_fm.values(), key=lambda c: c.get("fm_code", ""))


def main() -> None:
    _setup_logger()
    data = sys.stdin.read()

    try:
        data_dir = get_data_dir()
        output_dir = data_dir / "clusters"
        os.makedirs(output_dir, exist_ok=True)
        output_path = output_dir / "failure-clusters.json"

        events = _read_error_events(data_dir)
        logger.info("failure-clusterer: read %d error events", len(events))

        if not events:
            logger.info("failure-clusterer: no error events found, exiting")
            sys.stdout.write(data)
            return

        new_clusters = _build_clusters(events)
        existing = _load_existing(output_path)
        merged = _merge_clusters(existing, new_clusters)

        output = {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "clusters": merged,
        }
        output_path.write_text(
            json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info(
            "failure-clusterer: wrote %d clusters to %s", len(merged), output_path
        )

    except Exception as exc:
        logger.error("failure-clusterer: fatal error: %s", exc)
        sys.stdout.write(data)
        sys.exit(1)

    sys.stdout.write(data)


if __name__ == "__main__":
    main()
