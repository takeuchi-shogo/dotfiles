#!/usr/bin/env python3
"""auto-triage calibration の人間裁定を記録する判断 frontier ロガー.

auto-triage skill は learned 昇格候補を mechanical/advisory/reject/defer に
**無人分類** する (dry-run)。calibration phase では人間が日次 .triage レポートを
見てその分類の正否を裁定する。本ロガーはその裁定を記録し、2 つの価値を生む:

  1. **Wave3 allowlist の素材** — 人間が「mechanical で正しい」と確認した
     scope/key の集合 = 無人 PR 化を許してよい範囲。
  2. **判断 frontier メトリクス** — auto-triage の分類が人間の裁定とどれだけ
     一致するか (agreement rate)。「AI の方針判断が人間に追いついているか」を
     時系列で観測可能にする個人版指標 (Anthropic 再帰的自己改善記事 Mythos 64%
     の個人スケール翻訳)。

本ロガーは保存プリミティブであり、裁定の対話駆動は呼び出し側 (calibration
セッション) が行う。auto-triage skill 本体の dry-run no-write 保証とは独立
(本ロガーの書き込み先は agent-memory であって repo artifact ではない)。

Usage:
    # 1 件の裁定を記録
    calibration-verdict-logger.py log --key <8hex> --scope <s> \
        --auto mechanical --verdict agree \
        [--corrected advisory] [--note ...] [--report 2026-06-06]

    # 集計 (agreement rate + mechanical-confirmed allowlist)
    calibration-verdict-logger.py stats [--last N]

冪等キーは extract-promotion-candidates.py の candidate_key (SHA1) と同一前提。
stats は key ごとに最新裁定を採用 (last-wins) するため、再裁定で上書きできる。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from storage import get_data_dir, read_jsonl

CLASSES = ("mechanical", "advisory", "reject", "defer")
PROMOTE_CLASSES = ("adopted", "rejected")
ALL_CLASSES = CLASSES + PROMOTE_CLASSES
SOURCES = ("auto-triage", "promote")
VERDICTS = ("agree", "disagree")


def _ledger_path() -> Path:
    return get_data_dir() / "learnings" / "triage-calibration.jsonl"


def _validate(v: dict) -> None:
    """裁定フィールドを検証する。boundary で fail fast (NO-OP フォールバック禁止)。"""
    auto, verdict, corrected = v.get("auto"), v.get("verdict"), v.get("corrected")
    source = v.get("source", "auto-triage")
    if not v.get("key"):
        raise ValueError("key は必須")
    if source not in SOURCES:
        raise ValueError(f"source must be one of {SOURCES}, got {source!r}")
    allowed = CLASSES if source == "auto-triage" else PROMOTE_CLASSES
    if auto not in allowed:
        raise ValueError(
            f"source={source} では auto は {allowed} のいずれか, got {auto!r}"
        )
    if verdict not in VERDICTS:
        raise ValueError(f"verdict must be one of {VERDICTS}, got {verdict!r}")
    if corrected is not None and corrected not in allowed:
        raise ValueError(
            f"source={source} では corrected は {allowed} のいずれか, got {corrected!r}"
        )
    if verdict == "agree" and corrected is not None and corrected != auto:
        raise ValueError("corrected が auto と矛盾 (agree なのに別分類を指定)")


def log_verdict(verdict_fields: dict) -> dict:
    """裁定 1 件を triage-calibration.jsonl に追記する。

    verdict_fields: key(必須) / scope / auto / verdict / corrected / note / report。
    """
    _validate(verdict_fields)
    now = datetime.now()
    entry = {
        "date": now.strftime("%Y-%m-%d"),
        "key": verdict_fields["key"],
        "scope": verdict_fields.get("scope"),
        "source": verdict_fields.get("source", "auto-triage"),
        "auto": verdict_fields["auto"],
        "verdict": verdict_fields["verdict"],
        "corrected": verdict_fields.get("corrected"),
        "note": verdict_fields.get("note", ""),
        "report": verdict_fields.get("report"),
        "ts": now.isoformat(timespec="seconds"),
    }
    path = _ledger_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def _latest_by_key(entries: list[dict]) -> list[dict]:
    """key ごとに最新 (ts 昇順で後勝ち) の裁定だけ残す。"""
    latest: dict[str, dict] = {}
    for e in entries:
        k = e.get("key")
        if not k:
            continue
        prev = latest.get(k)
        if prev is None or e.get("ts", "") >= prev.get("ts", ""):
            latest[k] = e
    return list(latest.values())


def compute_stats(entries: list[dict], last: int | None = None) -> dict:
    """agreement rate (トレンド) と mechanical-confirmed allowlist を返す。

    意味論が異なるため `last` の適用範囲を分ける:
      - **agreement_rate / per_class / total_verdicts**: トレンド指標 → `last` 窓。
      - **mechanical_confirmed (Wave3 allowlist)**: 累積成果物 → 常に全期間集計。
        `last` で truncate すると過去に human-confirmed したキーが allowlist から
        欠落し Wave3 着手時に不完全になるため (PR #61 review 🟡)。
    """
    all_verdicts = _latest_by_key(entries)
    all_verdicts.sort(key=lambda e: e.get("ts", ""))

    # トレンド統計のみ last 窓を適用
    windowed = all_verdicts[-last:] if last is not None else all_verdicts
    total = len(windowed)
    agree = sum(1 for e in windowed if e.get("verdict") == "agree")

    per_class: dict[str, dict] = {}
    extra_classes = sorted(
        {e.get("auto") for e in windowed if e.get("auto")} - set(ALL_CLASSES)
    )
    for cls in (*ALL_CLASSES, *extra_classes):
        subset = [e for e in windowed if e.get("auto") == cls]
        n = len(subset)
        a = sum(1 for e in subset if e.get("verdict") == "agree")
        per_class[cls] = {
            "n": n,
            "agree": a,
            "agreement_rate": round(a / n, 3) if n else None,
        }

    per_source: dict[str, dict] = {}
    for src in SOURCES:
        subset = [e for e in windowed if e.get("source", "auto-triage") == src]
        n = len(subset)
        a = sum(1 for e in subset if e.get("verdict") == "agree")
        per_source[src] = {
            "n": n,
            "agree": a,
            "agreement_rate": round(a / n, 3) if n else None,
        }

    # Wave3 allowlist: 全期間の auto==mechanical かつ verdict==agree (last 非適用)
    confirmed = [
        {"key": e.get("key"), "scope": e.get("scope")}
        for e in all_verdicts
        if e.get("auto") == "mechanical"
        and e.get("verdict") == "agree"
        and e.get("source", "auto-triage") == "auto-triage"
    ]
    confirmed_scopes = sorted({c["scope"] for c in confirmed if c["scope"]})

    return {
        "window": last,  # null=全期間。トレンド統計のみに影響
        "total_verdicts": total,
        "agreement_rate": round(agree / total, 3) if total else None,
        "per_class": per_class,
        "per_source": per_source,
        "mechanical_confirmed": {
            "scope_note": "全期間集計 (--last 非適用)",
            "count": len(confirmed),
            "scopes": confirmed_scopes,
            "keys": [c["key"] for c in confirmed],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="auto-triage calibration verdict logger"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_log = sub.add_parser("log", help="裁定 1 件を記録")
    p_log.add_argument("--key", required=True, help="候補の冪等キー (SHA1 先頭でも可)")
    p_log.add_argument("--scope", default=None)
    p_log.add_argument(
        "--source",
        default="auto-triage",
        choices=SOURCES,
        help="裁定対象の自動判断の出所 (auto-triage 分類 / learned-promote PR)",
    )
    p_log.add_argument("--auto", required=True, help=f"自動側の判断 {ALL_CLASSES}")
    p_log.add_argument("--verdict", required=True, help=f"人間の裁定 {VERDICTS}")
    p_log.add_argument(
        "--corrected", default=None, help="disagree 時の正しい分類 (任意)"
    )
    p_log.add_argument("--note", default="")
    p_log.add_argument(
        "--report", default=None, help="対象 .triage レポートの日付/パス (任意)"
    )

    p_stats = sub.add_parser("stats", help="agreement rate + allowlist を集計")
    p_stats.add_argument("--last", type=int, default=None, help="直近 N 件のみ集計")

    args = parser.parse_args(argv)

    if args.cmd == "log":
        entry = log_verdict(
            {
                "key": args.key,
                "scope": args.scope,
                "source": args.source,
                "auto": args.auto,
                "verdict": args.verdict,
                "corrected": args.corrected,
                "note": args.note,
                "report": args.report,
            }
        )
        print(json.dumps(entry, ensure_ascii=False))
        return 0

    if args.cmd == "stats":
        stats = compute_stats(read_jsonl(_ledger_path()), last=args.last)
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
