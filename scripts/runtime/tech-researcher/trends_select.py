#!/usr/bin/env python3
"""trends_select.py — adoption-ledger から adopted 記事をランク付けして出力する。

(2) 消費層 (SP0) の共通コア。pull (task trends) / push (zsh first-open digest、将来の
朝 Discord push) が本モジュールを共有し、ランキング・描画ロジックの重複を防ぐ。

ランク: novelty+concreteness 降順 → reliability 降順 → date 降順。
窓: asof を含む直近 days 日間 (aggregate.py と同一セマンティクス)。
scores 不在 (旧形式レコードは null) は 0 扱いで末尾に落ちる。

Usage:
    trends_select.py <ledger.jsonl> [--days N] [--top K] [--asof YYYY-MM-DD]
                                    [--format term|json]

設計: docs/superpowers/specs/2026-06-10-knowledge-intake-pipeline-design.md §6.1
純ロジック: 引数の ledger path とオプションのみに依存し副作用を持たない。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta


def _num(v) -> float:
    """数値のみ通す (bool は int の subclass なので明示除外)。

    非数値 score で select() を落とさない。
    """
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else 0.0


def select(
    lines: list[str], asof: date, days: int, top: int | None = None
) -> list[dict]:
    """adopted=true を日付窓内で抽出し、url dedup + score ソート済みで返す。

    ランク: novelty+concreteness 降順 → reliability 降順 → date 降順。
    窓: asof を含む直近 days 日間 (aggregate.py と同一セマンティクス)。
    """
    cutoff = (asof - timedelta(days=days - 1)).isoformat()
    asof_s = asof.isoformat()
    seen: dict[str, dict] = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue  # ledger は append-only。他 writer 由来の不正行で全体を落とさない
        if not isinstance(rec, dict) or not rec.get("adopted"):
            continue
        d = rec.get("date") or ""
        if not (cutoff <= d <= asof_s):
            continue
        url = rec.get("url")
        if not url:
            continue
        prev = seen.get(url)
        if prev is None or d > (prev.get("date") or ""):
            seen[url] = rec

    # 安定ソート 2 段: date 降順 → score key で再ソート → 同点は新しい日付が先に残る
    items = sorted(seen.values(), key=lambda r: r.get("date") or "", reverse=True)

    def score_key(rec: dict):
        s = rec.get("scores") or {}
        nov = _num(s.get("novelty"))
        con = _num(s.get("concreteness"))
        rel = _num(s.get("reliability"))
        return (-(nov + con), -rel)

    items.sort(key=score_key)
    return items[:top] if top else items


def render_term(items: list[dict], days: int) -> str:
    """ターミナル向け表示。URL は素のまま出力 (Ghostty 等が自動でリンク化する)。"""
    out = [f"📡 AI Tech Trends — 直近{days}日 (adoption-ledger)"]
    if not items:
        out.append(f"  (直近{days}日の採用記事なし)")
        return "\n".join(out) + "\n"
    for i, rec in enumerate(items, 1):
        s = rec.get("scores") or {}
        badge = (
            f"n{s.get('novelty') or '-'}"
            f" c{s.get('concreteness') or '-'}"
            f" r{s.get('reliability') or '-'}"
        )
        title = (rec.get("title") or "(no title)")[:72]
        day = (rec.get("date") or "")[5:]
        out.append(f" {i:>2}. [{badge}] {title}  ({rec.get('domain', '?')}, {day})")
        out.append(f"     {rec['url']}")
    return "\n".join(out) + "\n"


def render_json(items: list[dict]) -> str:
    return json.dumps(items, ensure_ascii=False)


def _parse_date(s: str) -> date | None:
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", help="adoption-ledger.jsonl path")
    parser.add_argument("--days", type=int, default=3)
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--asof", default=None, help="基準日 YYYY-MM-DD (既定: 今日)")
    parser.add_argument("--format", choices=("term", "json"), default="term")
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
        lines = []

    items = select(lines, asof=asof, days=args.days, top=args.top)
    if args.format == "json":
        sys.stdout.write(render_json(items) + "\n")
    else:
        sys.stdout.write(render_term(items, days=args.days))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
