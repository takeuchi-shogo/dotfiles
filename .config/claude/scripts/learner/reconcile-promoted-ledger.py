#!/usr/bin/env python3
"""マージ済み learned-promote manifest を promoted-ledger に反映する。

merge-coupled idempotency モデルの後半。run-learned-promote.sh は昇格候補を
artifact 編集 + manifest (docs/learned-promote/<run>.json) としてブランチ/PR にする
だけで ledger には触らない。PR がマージされると manifest が master に到達する。
このスクリプトは master 上に存在する manifest (= 人間がマージを承認したもの) の
processed key (adopted / rejected の両方) を promoted-ledger.jsonl へ追記する。

これにより「PR をマージしなければ ledger に入らない = 却下した learned は再提案される」
という PR ゲートと冪等性の整合が取れる。

入力: docs/learned-promote/*.json (manifest) + learnings/promoted-ledger.jsonl
出力: stdout に JSON サマリ {"appended": N, "skipped": M, "entries": [...]}
副作用: --dry-run でなければ ledger へ追記 (flock 下で既存 key は skip)。

ledger は正本なので壊れた行は無言 skip せず例外で surface する (silent failure 回避)。
manifest は外部入力なので壊れた 1 件は skip する (全体を止めない)。
"""

from __future__ import annotations

import argparse
import fcntl
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# 冪等キー = generalized_detail/detail の SHA1 (extract-promotion-candidates.py と一致)
_KEY_RE = re.compile(r"^[0-9a-f]{40}$")


def load_ledger_keys(ledger_path: Path) -> set[str]:
    """既存 ledger の key 集合を返す。

    ledger は正本のため、壊れた JSON 行は無言 skip せず ValueError で surface する。
    空行は無視する。
    """
    keys: set[str] = set()
    if not ledger_path.exists():
        return keys
    for lineno, line in enumerate(
        ledger_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"corrupt ledger line {lineno} in {ledger_path}: {exc}"
            ) from exc
        k = rec.get("key")
        if k:
            keys.add(k)
    return keys


def load_manifest_entries(manifest_dir: Path) -> list[dict]:
    """manifest ディレクトリ内の全 *.json から processed promotion を平坦化して返す。

    各エントリ: {key, decision, target_artifact, scope, manifest}
    決定 (adopted / rejected) の両方を processed として扱う。manifest は外部入力なので
    壊れた/不正なものは stderr 警告 + skip (1 件で全体を止めない)。
    """
    entries: list[dict] = []
    if not manifest_dir.exists():
        return entries
    for path in sorted(manifest_dir.glob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            print(
                f"[reconcile] WARN: skip unreadable manifest {path.name}: {exc}",
                file=sys.stderr,
            )
            continue
        promotions = doc.get("promotions")
        if not isinstance(promotions, list):
            print(
                f"[reconcile] WARN: manifest {path.name} has no promotions list",
                file=sys.stderr,
            )
            continue
        seen_in_file: set[str] = set()
        for p in promotions:
            if not isinstance(p, dict):
                continue
            key = p.get("key")
            decision = p.get("decision")
            if not isinstance(key, str) or not _KEY_RE.match(key):
                print(
                    f"[reconcile] WARN: {path.name}: invalid key, skip: {key!r}",
                    file=sys.stderr,
                )
                continue
            if decision not in ("adopted", "rejected"):
                # 未知 decision は ledger に入れない (再提案させる方が安全)。
                print(
                    f"[reconcile] WARN: {path.name}: bad decision {decision!r}",
                    file=sys.stderr,
                )
                continue
            if key in seen_in_file:
                # 同一 manifest 内の重複は設計違反。最初の 1 件のみ採用し警告。
                print(
                    f"[reconcile] WARN: {path.name}: dup key {key[:12]}",
                    file=sys.stderr,
                )
                continue
            seen_in_file.add(key)
            entries.append(
                {
                    "key": key,
                    "decision": decision,
                    "target_artifact": p.get("target_artifact", ""),
                    "scope": p.get("scope", ""),
                    "manifest": path.name,
                }
            )
    return entries


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _plan(existing: set[str], manifest_entries: list[dict]) -> tuple[list[dict], int]:
    """追記すべき record と skip 数を計算する (副作用なし)。"""
    appended: list[dict] = []
    skipped = 0
    seen_this_run: set[str] = set()
    for entry in manifest_entries:
        key = entry["key"]
        if key in existing or key in seen_this_run:
            skipped += 1
            continue
        seen_this_run.add(key)
        appended.append(
            {
                "timestamp": _now_iso(),
                "key": key,
                "decision": entry["decision"],
                "target_artifact": entry["target_artifact"],
                "scope": entry["scope"],
                "source": "reconcile",
                "manifest": entry["manifest"],
            }
        )
    return appended, skipped


def reconcile(manifest_dir: Path, ledger_path: Path, dry_run: bool) -> dict:
    """master 上の manifest key で未記録のものを ledger に追記する。

    冪等: 同一 key は manifest に複数回現れても、また再実行しても 1 度しか追記しない。
    実行時は flock で ledger を排他ロックし、lock 取得後に key を再読込してから追記する
    (同時 reconcile による二重 append を防ぐ)。
    """
    manifest_entries = load_manifest_entries(manifest_dir)

    if dry_run:
        existing = load_ledger_keys(ledger_path)
        appended, skipped = _plan(existing, manifest_entries)
        return {
            "appended": len(appended),
            "skipped": skipped,
            "dry_run": True,
            "entries": appended,
        }

    # manifest が無ければ ledger を一切触らない (空ファイル作成も避ける)。
    if not manifest_entries:
        return {"appended": 0, "skipped": 0, "dry_run": False, "entries": []}

    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    # a+b (read+append binary) + flock。lock 後に key を再読込し write を直列化する。
    # append mode は write を必ず末尾に行うが、末尾改行判定の read のため "+b" にする。
    with open(ledger_path, "a+b") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            existing = load_ledger_keys(ledger_path)
            appended, skipped = _plan(existing, manifest_entries)
            if appended:
                payload = "\n".join(json.dumps(r, ensure_ascii=False) for r in appended)
                # 末尾改行で終わっていなければ補い、追記行が前行と結合するのを防ぐ。
                f.seek(0, 2)
                prefix = b""
                if f.tell() > 0:
                    f.seek(-1, 2)
                    if f.read(1) != b"\n":
                        prefix = b"\n"
                    f.seek(0, 2)
                f.write(prefix + (payload + "\n").encode("utf-8"))
                f.flush()
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    return {
        "appended": len(appended),
        "skipped": skipped,
        "dry_run": False,
        "entries": appended,
    }


def main() -> int:
    learnings = Path.home() / ".claude" / "agent-memory" / "learnings"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest-dir",
        type=Path,
        required=True,
        help="docs/learned-promote ディレクトリ (master 上の merged manifest)",
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        default=learnings / "promoted-ledger.jsonl",
        help="promoted-ledger.jsonl のパス",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="追記せず、追記予定のみ JSON 出力",
    )
    args = parser.parse_args()

    result = reconcile(args.manifest_dir, args.ledger, args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
