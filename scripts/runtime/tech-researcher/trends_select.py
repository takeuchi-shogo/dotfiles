#!/usr/bin/env python3
"""trends_select.py — adoption-ledger から adopted 記事をランク付けして出力する。

(2) 消費層 (SP0) の共通コア。pull (task trends) / push (zsh first-open digest、将来の
朝 Discord push) が本モジュールを共有し、ランキング・描画ロジックの重複を防ぐ。

ランク: novelty+concreteness 降順 → reliability 降順 → date 降順。
窓: asof を含む直近 days 日間 (aggregate.py と同一セマンティクス)。
scores 不在 (旧形式レコードは null) は 0 扱いで末尾に落ちる。

Usage:
    trends_select.py <ledger.jsonl> [--days N] [--top K] [--asof YYYY-MM-DD]
                                    [--format term|json] [--reports-dir DIR]

設計: docs/superpowers/specs/2026-06-10-knowledge-intake-pipeline-design.md §6.1
純ロジック: 引数の ledger path とオプションのみに依存し副作用を持たない。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta


def _num(v) -> float:
    """数値のみ通す (bool は int の subclass なので明示除外)。

    非数値 score で select() を落とさない。
    """
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else 0.0


def _collect_adopted_window(lines: list[str], asof: date, days: int) -> list[dict]:
    """adopted=true を日付窓で抽出し url dedup して返す (未ソート)。

    同 url は最新日の採用レコードを残す。窓は asof を含む直近 days 日間
    (aggregate.py と同一セマンティクス)。select() と select_harness_candidates()
    が窓・dedup ロジックを共有する。
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
    return list(seen.values())


def _axis(rec: dict, name: str) -> float:
    """scores オブジェクトから軸 name の数値を取り出す (不在/非数値/非 dict は 0)。"""
    raw = rec.get("scores")
    s = raw if isinstance(raw, dict) else {}
    return _num(s.get(name))


def select(
    lines: list[str], asof: date, days: int, top: int | None = None
) -> list[dict]:
    """adopted=true を日付窓内で抽出し、url dedup + score ソート済みで返す。

    ランク: novelty+concreteness 降順 → reliability 降順 → date 降順。
    窓: asof を含む直近 days 日間 (aggregate.py と同一セマンティクス)。
    """
    # 安定ソート 2 段: date 降順 → score key で再ソート → 同点は新しい日付が先に残る
    items = sorted(
        _collect_adopted_window(lines, asof, days),
        key=lambda r: r.get("date") or "",
        reverse=True,
    )

    def score_key(rec: dict):
        nov = _axis(rec, "novelty")
        con = _axis(rec, "concreteness")
        rel = _axis(rec, "reliability")
        return (-(nov + con), -rel)

    items.sort(key=score_key)
    return items[:top] if top else items


def select_harness_candidates(
    lines: list[str], asof: date, days: int, min_relevance: float
) -> list[dict]:
    """harness_relevance >= min_relevance の adopted 記事を relevance 降順で返す。

    Phase 5 (Task 5.2 absorb→PR bridge) の候補選択土台。「AI トレンドとして重要」
    (select) とは別軸で「自分のハーネスを改善しうるか」(harness_relevance) を見る。
    ランク: harness_relevance 降順 → date 降順 (同点は新しい記事を先頭)。
    閾値未満は除外する — 薄い晩は空リストを返し、5.2 側で PR ゼロに落ちる
    (死蔵 PR 防止の閾値ベース流量制御)。harness_relevance 不在 (旧レコード) は 0 扱い。
    min_relevance は 1 以上を渡すこと — 0 だと 0.0 >= 0 で旧 3 軸レコードが混入する。
    上位 N 件は呼び出し側で slice する (select() の top と異なり CLI 非公開のため)。
    """
    items = [
        r
        for r in _collect_adopted_window(lines, asof, days)
        if _axis(r, "harness_relevance") >= min_relevance
    ]
    items.sort(key=lambda r: r.get("date") or "", reverse=True)
    items.sort(key=lambda r: -_axis(r, "harness_relevance"))
    return items


def _printable(s: str) -> str:
    """制御文字 (ANSI/OSC エスケープ・bidi 制御含む) を除去。

    untrusted feed 由来の端末注入防御。
    """
    return "".join(ch for ch in s if ch.isprintable())


_REPORT_ENTRY = re.compile(r"^- \[(\d+)\] \[[^\]]*\] (.+)$")


def load_summaries(report_texts: list[str]) -> dict[str, str]:
    """日次 report の 1 行要約を url に突合して返す。

    report 構造: 前半に `- [N] [domain] 要約`、`## 出典` 以降に
    `- [N] [domain] title` + 次行インデント URL。両者を [N] で join する。
    後の report が同一 url を上書きする (呼び出し側は古い順に渡す)。
    要約は enrichment — 形式不一致・出典なし report は黙って空になり、
    digest は従来どおり title+URL で成立する。
    """
    out: dict[str, str] = {}
    for text in report_texts:
        head, sep, tail = text.partition("## 出典")
        if not sep:
            continue
        summaries: dict[str, str] = {}
        for line in head.splitlines():
            m = _REPORT_ENTRY.match(line.strip())
            if m:
                summaries[m.group(1)] = m.group(2).strip()
        idx: str | None = None
        for line in tail.splitlines():
            m = _REPORT_ENTRY.match(line.strip())
            if m:
                idx = m.group(1)
                continue
            url = line.strip()
            if not idx or not url.startswith(("http://", "https://")):
                continue
            if idx in summaries:
                out[url] = summaries[idx]
            idx = None
    return out


def render_term(
    items: list[dict], days: int, summaries: dict[str, str] | None = None
) -> str:
    """ターミナル向け表示。URL は素のまま出力 (Ghostty 等が自動でリンク化する)。

    summaries (url→1行要約) に該当があれば title と URL の間に 1 行挟む。
    """
    out = [f"📡 AI Tech Trends — 直近{days}日 (adoption-ledger)"]
    if not items:
        out.append(f"  (直近{days}日の採用記事なし)")
        return "\n".join(out) + "\n"
    for i, rec in enumerate(items, 1):
        raw = rec.get("scores")
        s = raw if isinstance(raw, dict) else {}
        badge = (
            f"n{s.get('novelty') or '-'}"
            f" c{s.get('concreteness') or '-'}"
            f" r{s.get('reliability') or '-'}"
        )
        title = _printable(str(rec.get("title") or "(no title)"))[:72]
        day = (rec.get("date") or "")[5:]
        out.append(f" {i:>2}. [{badge}] {title}  ({rec.get('domain', '?')}, {day})")
        summary = (summaries or {}).get(rec["url"])
        if summary:
            t = _printable(summary)
            out.append(f"     └ {t[:100]}{'…' if len(t) > 100 else ''}")
        out.append(f"     {_printable(str(rec['url']))}")
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
    parser.add_argument(
        "--reports-dir",
        default=None,
        help="日次 report (<date>.md) から 1 行要約を突合して表示 (term のみ)",
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
        lines = []

    items = select(lines, asof=asof, days=args.days, top=args.top)
    summaries: dict[str, str] | None = None
    if args.reports_dir and args.format == "term":
        texts = []
        for i in range(args.days - 1, -1, -1):
            day = (asof - timedelta(days=i)).isoformat()
            try:
                with open(f"{args.reports_dir}/{day}.md", encoding="utf-8") as f:
                    texts.append(f.read())
            except FileNotFoundError:
                continue
            except (OSError, UnicodeDecodeError) as e:
                print(f"[trends_select] WARN: report read failed: {e}", file=sys.stderr)
                continue
        summaries = load_summaries(texts)

    if args.format == "json":
        sys.stdout.write(render_json(items) + "\n")
    else:
        sys.stdout.write(render_term(items, days=args.days, summaries=summaries))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
