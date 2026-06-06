#!/usr/bin/env python3
"""aggregate.py — adoption-ledger.jsonl の直近30日採用ドメイン集計 (read-only)。

採用 (adopted=true) された記事の出典ドメインを頻度集計し、
「採用上位ドメイン (RSS候補)」markdown section を stdout に出力する。
情報源の自動追加はしない (Phase 3 で human-in-loop 昇格を扱う)。

Usage:
    aggregate.py <ledger.jsonl> [--days N] [--top K] [--asof YYYY-MM-DD]

純ロジック: 引数の ledger path とオプションのみに依存し副作用を持たない。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta

AXES = ("novelty", "reliability", "concreteness")
"""多軸選別スコアの軸 (Phase 2 Task 2.2)。1-5 スケール。"""


def _clamp_score(v: object) -> float | None:
    """1-5 へ clamp。数値でない/bool/null は None (平均から除外)。

    記録時は LLM の raw 値を ledger に残し、平均算出時のみ範囲外を丸める。
    """
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    return min(5.0, max(1.0, float(v)))


def _parse_date(s: str) -> date | None:
    """YYYY-MM-DD を date に。失敗時 None (malformed line tolerant)。"""
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def aggregate(lines: list[str], *, asof: date, days: int) -> dict[str, dict[str, int]]:
    """ledger 行 (str) のリストからドメイン別 {adopted, total} を集計。

    直近 days 日 (asof を含む窓: asof-days+1 .. asof) のみ対象。
    JSON parse 不能行・date 不正行はスキップする (捏造せず黙って捨てる)。
    """
    cutoff = asof - timedelta(days=days - 1)
    stats: dict[str, dict[str, int]] = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        d = _parse_date(str(rec.get("date", "")))
        if d is None or d < cutoff or d > asof:
            continue
        domain = rec.get("domain")
        if not domain or not isinstance(domain, str):
            continue
        bucket = stats.setdefault(domain, {"adopted": 0, "total": 0})
        bucket["total"] += 1
        if rec.get("adopted") is True:
            bucket["adopted"] += 1
    return stats


def render(stats: dict[str, dict[str, int]], *, days: int, top: int) -> str:
    """集計を markdown に。並び: 採用数降順 → total 降順 → ドメイン名昇順。"""
    ranked = sorted(
        stats.items(),
        key=lambda kv: (-kv[1]["adopted"], -kv[1]["total"], kv[0]),
    )
    ranked = [(dom, s) for dom, s in ranked if s["adopted"] > 0][:top]

    out = [f"## 採用上位ドメイン (直近{days}日, RSS候補)", ""]
    if not ranked:
        out.append("_採用実績なし (ledger が空、または窓内に adopted=true なし)_")
        return "\n".join(out) + "\n"
    out.append("| ドメイン | 採用 | 収集 | 採用率 |")
    out.append("|---|---|---|---|")
    for dom, s in ranked:
        rate = s["adopted"] / s["total"] if s["total"] else 0.0
        safe = dom.replace(
            "|", "&#124;"
        )  # markdown table 破壊防止 (host 内の | を無害化)
        out.append(f"| {safe} | {s['adopted']} | {s['total']} | {rate:.0%} |")
    out.append("")
    out.append(
        "> read-only 集計。情報源の自動追加はしない (Phase 3 で承認ベース昇格)。"
    )
    return "\n".join(out) + "\n"


def _accumulate_scores(sums: dict[str, list], scores: object) -> None:
    """adopted 行の scores を軸別 [合計, 件数] に加算 (clamp 後、null/非数は除外)。"""
    if not isinstance(scores, dict):
        return
    for a in AXES:
        cv = _clamp_score(scores.get(a))
        if cv is None:
            continue
        sums[a][0] += cv
        sums[a][1] += 1


def aggregate_by_source(lines: list[str], *, asof: date, days: int) -> dict[str, dict]:
    """source_id (=feed URL, D1) 別に採用率・観測日数・多軸平均を集計。

    source_id を持つ行のみ対象 (Phase 1 行は source_id 欠落で除外、null-tolerant)。
    adopted=true 行の scores のみ平均に算入。total>0 の source は採用0でも残す
    (Phase 3 の降格候補可視化のため domain ビューと異なり 0採用も出す)。
    観測日数 = ledger に当該 source が現れた日付の異なり数 (採用率の分母の厚みを示す)。
    """
    cutoff = asof - timedelta(days=days - 1)
    stats: dict[str, dict] = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        sid = rec.get("source_id")
        if not sid or not isinstance(sid, str):
            continue
        d = _parse_date(str(rec.get("date", "")))
        if d is None or d < cutoff or d > asof:
            continue
        b = stats.setdefault(
            sid,
            {
                "adopted": 0,
                "total": 0,
                "days": set(),
                "sums": {a: [0.0, 0] for a in AXES},
            },
        )
        b["total"] += 1
        b["days"].add(d.isoformat())
        if rec.get("adopted") is True:
            b["adopted"] += 1
            _accumulate_scores(b["sums"], rec.get("scores"))
    return stats


def render_by_source(stats: dict[str, dict], *, days: int, top: int) -> str:
    """source 別パフォーマンスを markdown に。並び: 採用数→total→source_id。"""
    ranked = sorted(
        stats.items(),
        key=lambda kv: (-kv[1]["adopted"], -kv[1]["total"], kv[0]),
    )[:top]

    out = [f"## ソース別パフォーマンス (直近{days}日, source_id=feed URL)", ""]
    if not ranked:
        out.append(
            "_source_id 付き採用データなし (Phase 1 行のみ、または窓内データなし)_"
        )
        return "\n".join(out) + "\n"
    out.append(
        "| source_id | 採用 | 収集 | 採用率 | 観測日数 | 新規性 | 信頼性 | 具体性 |"
    )
    out.append("|---|---|---|---|---|---|---|---|")
    for sid, s in ranked:
        rate = s["adopted"] / s["total"] if s["total"] else 0.0
        means = []
        for a in AXES:
            total, count = s["sums"][a]
            means.append(f"{total / count:.1f}" if count else "—")
        safe = sid.replace("|", "&#124;")
        out.append(
            f"| {safe} | {s['adopted']} | {s['total']} | {rate:.0%} | "
            f"{len(s['days'])} | {means[0]} | {means[1]} | {means[2]} |"
        )
    out.append("")
    out.append(
        "> source 別採用実績 (採用0件の source も降格候補として表示)。"
        "Phase 3 自動昇格降格はこのスコアを使う (Phase 2 は read-only)。"
    )
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", help="adoption-ledger.jsonl path")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument(
        "--asof", default=None, help="集計基準日 YYYY-MM-DD (既定: 今日)"
    )
    parser.add_argument(
        "--by-source",
        action="store_true",
        help="source_id 別パフォーマンス節を追記 (Phase 2)",
    )
    args = parser.parse_args(argv)

    asof = _parse_date(args.asof) if args.asof else date.today()
    if asof is None:
        print(f"ERROR: invalid --asof: {args.asof}", file=sys.stderr)
        return 2
    if args.days < 1 or args.top < 1:
        print("ERROR: --days and --top must be >= 1", file=sys.stderr)
        return 2

    try:
        with open(args.ledger, encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []  # ledger 未生成 = 空集計 (エラーにしない)

    stats = aggregate(lines, asof=asof, days=args.days)
    sys.stdout.write(render(stats, days=args.days, top=args.top))
    if args.by_source:
        by_src = aggregate_by_source(lines, asof=asof, days=args.days)
        sys.stdout.write("\n" + render_by_source(by_src, days=args.days, top=args.top))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
