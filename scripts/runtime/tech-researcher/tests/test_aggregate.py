"""aggregate.py の純ロジック検証。

実行: uv run pytest scripts/runtime/tech-researcher/tests/test_aggregate.py
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import aggregate  # noqa: E402


def _line(d: str, domain: str, adopted: bool, url: str = "https://x/y") -> str:
    return json.dumps(
        {
            "ts": f"{d}T00:00:00+09:00",
            "date": d,
            "domain": domain,
            "url": url,
            "title": "t",
            "adopted": adopted,
        },
        ensure_ascii=False,
    )


ASOF = date(2026, 6, 4)


def test_counts_adopted_and_total_per_domain():
    lines = [
        _line("2026-06-04", "zenn.dev", True),
        _line("2026-06-04", "zenn.dev", False),
        _line("2026-06-03", "qiita.com", True),
    ]
    stats = aggregate.aggregate(lines, asof=ASOF, days=30)
    assert stats["zenn.dev"] == {"adopted": 1, "total": 2}
    assert stats["qiita.com"] == {"adopted": 1, "total": 1}


def test_30day_window_excludes_old_records():
    lines = [
        _line("2026-06-04", "in.window", True),
        _line("2026-05-06", "in.window", True),  # 30 日窓 (5/6..6/4) の境界内
        _line("2026-05-05", "out.window", True),  # 窓外 (31 日前)
    ]
    stats = aggregate.aggregate(lines, asof=ASOF, days=30)
    assert stats["in.window"]["adopted"] == 2
    assert "out.window" not in stats


def test_future_records_excluded():
    lines = [_line("2026-06-05", "future.dev", True)]
    stats = aggregate.aggregate(lines, asof=ASOF, days=30)
    assert "future.dev" not in stats


def test_empty_ledger_renders_no_adoption_notice():
    stats = aggregate.aggregate([], asof=ASOF, days=30)
    assert stats == {}
    out = aggregate.render(stats, days=30, top=10)
    assert "採用実績なし" in out


def test_malformed_lines_are_skipped():
    lines = [
        "not json at all",
        "{broken json",
        "",
        json.dumps({"date": "garbage", "domain": "bad.date", "adopted": True}),
        json.dumps({"date": "2026-06-04", "adopted": True}),  # domain 欠落
        _line("2026-06-04", "good.dev", True),
    ]
    stats = aggregate.aggregate(lines, asof=ASOF, days=30)
    assert stats == {"good.dev": {"adopted": 1, "total": 1}}


def test_render_orders_by_adopted_then_total_then_name():
    lines = [
        _line("2026-06-04", "b.dev", True),
        _line("2026-06-04", "b.dev", True),
        _line("2026-06-04", "a.dev", True),
        _line("2026-06-04", "a.dev", True),
        _line("2026-06-04", "a.dev", False),  # a: adopted2 total3, b: adopted2 total2
        _line("2026-06-04", "c.dev", True),
    ]
    stats = aggregate.aggregate(lines, asof=ASOF, days=30)
    out = aggregate.render(stats, days=30, top=10)
    rows = [
        ln for ln in out.splitlines() if ln.startswith("| ") and "ドメイン" not in ln
    ]
    order = [r.split("|")[1].strip() for r in rows]
    # adopted 降順 → 同数は total 降順 (a:3 > b:2) → c は adopted1 で最後
    assert order == ["a.dev", "b.dev", "c.dev"]


def test_render_excludes_zero_adopted_domains():
    lines = [
        _line("2026-06-04", "adopted.dev", True),
        _line("2026-06-04", "noisy.dev", False),
    ]
    stats = aggregate.aggregate(lines, asof=ASOF, days=30)
    out = aggregate.render(stats, days=30, top=10)
    assert "adopted.dev" in out
    assert "noisy.dev" not in out


def test_top_k_limits_rows():
    lines = [_line("2026-06-04", f"d{i}.dev", True) for i in range(5)]
    stats = aggregate.aggregate(lines, asof=ASOF, days=30)
    out = aggregate.render(stats, days=30, top=2)
    rows = [
        ln for ln in out.splitlines() if ln.startswith("| ") and "ドメイン" not in ln
    ]
    assert len(rows) == 2


def test_render_escapes_pipe_in_domain():
    lines = [_line("2026-06-04", "evil.com|x", True)]
    stats = aggregate.aggregate(lines, asof=ASOF, days=30)
    out = aggregate.render(stats, days=30, top=10)
    assert "evil.com&#124;x" in out
    # 生の | がテーブル行に残らない (ヘッダ区切りの | とは別)
    rows = [ln for ln in out.splitlines() if "evil.com" in ln]
    assert all("evil.com&#124;x" in r for r in rows)


def test_main_rejects_nonpositive_days_and_top(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(_line("2026-06-04", "x.dev", True) + "\n", encoding="utf-8")
    assert aggregate.main([str(ledger), "--days", "0"]) == 2
    assert aggregate.main([str(ledger), "--top", "0"]) == 2
    assert aggregate.main([str(ledger), "--days", "-1"]) == 2


def test_main_missing_ledger_is_empty_not_error(tmp_path, capsys):
    missing = tmp_path / "nope.jsonl"
    assert aggregate.main([str(missing), "--asof", "2026-06-04"]) == 0
    assert "採用実績なし" in capsys.readouterr().out


def _line_v2(
    d: str,
    domain: str,
    adopted: bool,
    source_id: str = "https://feed/x",
    scores: dict | None = None,
    url: str = "https://x/y",
) -> str:
    """Phase 2 v2 スキーマ行 (source_id + scores 付き)。"""
    return json.dumps(
        {
            "ts": f"{d}T00:00:00+09:00",
            "date": d,
            "domain": domain,
            "url": url,
            "title": "t",
            "adopted": adopted,
            "source_id": source_id,
            "scores": scores,
        },
        ensure_ascii=False,
    )


def test_clamp_score_bounds_and_rejects_non_numbers():
    assert aggregate._clamp_score(7) == 5.0
    assert aggregate._clamp_score(0) == 1.0
    assert aggregate._clamp_score(3) == 3.0
    assert aggregate._clamp_score(None) is None
    assert aggregate._clamp_score(True) is None
    assert aggregate._clamp_score("4") is None


def test_by_source_counts_and_day_distinct():
    lines = [
        _line_v2("2026-06-04", "a.dev", True, source_id="feed-a"),
        _line_v2("2026-06-04", "a.dev", False, source_id="feed-a"),
        _line_v2("2026-06-03", "a.dev", True, source_id="feed-a"),
    ]
    stats = aggregate.aggregate_by_source(lines, asof=ASOF, days=30)
    assert stats["feed-a"]["adopted"] == 2
    assert stats["feed-a"]["total"] == 3
    assert len(stats["feed-a"]["days"]) == 2


def test_by_source_ignores_phase1_rows_without_source_id():
    lines = [
        _line("2026-06-04", "a.dev", True),
        _line_v2("2026-06-04", "a.dev", True, source_id="feed-a"),
    ]
    stats = aggregate.aggregate_by_source(lines, asof=ASOF, days=30)
    assert set(stats.keys()) == {"feed-a"}
    assert stats["feed-a"]["total"] == 1
    dom = aggregate.aggregate(lines, asof=ASOF, days=30)
    assert dom["a.dev"]["total"] == 2


def test_by_source_averages_scores_with_clamp():
    lines = [
        _line_v2(
            "2026-06-04",
            "a.dev",
            True,
            source_id="feed-a",
            scores={"novelty": 7, "reliability": 4, "concreteness": 0},
        ),
        _line_v2(
            "2026-06-04",
            "a.dev",
            True,
            source_id="feed-a",
            scores={"novelty": 3, "reliability": 2, "concreteness": None},
        ),
    ]
    stats = aggregate.aggregate_by_source(lines, asof=ASOF, days=30)
    sums = stats["feed-a"]["sums"]
    assert sums["novelty"] == [5.0 + 3.0, 2]
    assert sums["reliability"] == [4.0 + 2.0, 2]
    assert sums["concreteness"] == [1.0, 1]


def test_by_source_keeps_zero_adopted_sources():
    lines = [_line_v2("2026-06-04", "a.dev", False, source_id="noisy-feed")]
    stats = aggregate.aggregate_by_source(lines, asof=ASOF, days=30)
    assert "noisy-feed" in stats
    assert stats["noisy-feed"]["adopted"] == 0
    out = aggregate.render_by_source(stats, days=30, top=10)
    assert "noisy-feed" in out
    assert "0%" in out


def test_render_by_source_empty_notice():
    out = aggregate.render_by_source({}, days=30, top=10)
    assert "採用データなし" in out


def test_render_by_source_dash_when_no_scores():
    lines = [_line_v2("2026-06-04", "a.dev", True, source_id="feed-a", scores=None)]
    stats = aggregate.aggregate_by_source(lines, asof=ASOF, days=30)
    out = aggregate.render_by_source(stats, days=30, top=10)
    assert "—" in out


def test_main_by_source_appends_section(tmp_path, capsys):
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(
        _line_v2("2026-06-04", "a.dev", True, source_id="feed-a") + "\n",
        encoding="utf-8",
    )
    rc = aggregate.main([str(ledger), "--asof", "2026-06-04", "--by-source"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "採用上位ドメイン" in out
    assert "ソース別パフォーマンス" in out


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
