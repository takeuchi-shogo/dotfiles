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

import json
from datetime import date, timedelta


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
