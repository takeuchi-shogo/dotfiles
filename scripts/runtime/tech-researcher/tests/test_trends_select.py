"""trends_select.py の純ロジック検証。

実行: uv run pytest scripts/runtime/tech-researcher/tests/test_trends_select.py
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import trends_select  # noqa: E402

ASOF = date(2026, 6, 10)


def _line(
    d: str,
    url: str,
    adopted: bool = True,
    novelty: int | None = 3,
    reliability: int | None = 3,
    concreteness: int | None = 3,
    title: str = "t",
    domain: str = "example.com",
) -> str:
    scores = None
    if novelty is not None:
        scores = {
            "novelty": novelty,
            "reliability": reliability,
            "concreteness": concreteness,
        }
    return json.dumps(
        {
            "ts": f"{d}T00:00:00+09:00",
            "date": d,
            "domain": domain,
            "url": url,
            "title": title,
            "adopted": adopted,
            "source_id": "https://feed.example/rss",
            "scores": scores,
        },
        ensure_ascii=False,
    )


def test_adopted_false_excluded():
    lines = [
        _line("2026-06-09", "https://a/1"),
        _line("2026-06-09", "https://a/2", adopted=False),
    ]
    items = trends_select.select(lines, asof=ASOF, days=3)
    assert [r["url"] for r in items] == ["https://a/1"]


def test_window_cutoff_excludes_old():
    lines = [
        _line("2026-06-09", "https://a/new"),
        _line("2026-06-01", "https://a/old"),
    ]
    items = trends_select.select(lines, asof=ASOF, days=3)
    assert [r["url"] for r in items] == ["https://a/new"]


def test_window_includes_asof_day_and_cutoff_day():
    lines = [
        _line("2026-06-10", "https://a/today"),
        _line("2026-06-08", "https://a/cutoff-day"),
        _line("2026-06-07", "https://a/before-cutoff"),
    ]
    items = trends_select.select(lines, asof=ASOF, days=3)
    urls = {r["url"] for r in items}
    assert urls == {"https://a/today", "https://a/cutoff-day"}


def test_url_dedup_keeps_latest_date():
    lines = [
        _line("2026-06-08", "https://a/1", novelty=1, reliability=1, concreteness=1),
        _line("2026-06-09", "https://a/1", novelty=5, reliability=5, concreteness=5),
    ]
    items = trends_select.select(lines, asof=ASOF, days=7)
    assert len(items) == 1
    assert items[0]["date"] == "2026-06-09"


def test_sort_score_desc_then_reliability_then_date():
    lines = [
        _line("2026-06-09", "https://low", novelty=2, concreteness=2, reliability=5),
        _line("2026-06-09", "https://high", novelty=5, concreteness=4, reliability=1),
        _line(
            "2026-06-09", "https://tie-rel5", novelty=4, concreteness=4, reliability=5
        ),
        _line(
            "2026-06-09", "https://tie-rel2", novelty=4, concreteness=4, reliability=2
        ),
        _line(
            "2026-06-09", "https://tie-new", novelty=3, concreteness=3, reliability=3
        ),
        _line(
            "2026-06-08", "https://tie-old", novelty=3, concreteness=3, reliability=3
        ),
    ]
    items = trends_select.select(lines, asof=ASOF, days=7)
    urls = [r["url"] for r in items]
    assert urls == [
        "https://high",  # novelty+concreteness=9
        "https://tie-rel5",  # 8, reliability=5
        "https://tie-rel2",  # 8, reliability=2
        "https://tie-new",  # 6, 同点 → date 降順
        "https://tie-old",  # 6
        "https://low",  # 4
    ]


def test_scores_null_ranks_last():
    lines = [
        _line("2026-06-09", "https://scored", novelty=1, concreteness=1, reliability=1),
        _line("2026-06-09", "https://null", novelty=None),
    ]
    items = trends_select.select(lines, asof=ASOF, days=3)
    assert [r["url"] for r in items] == ["https://scored", "https://null"]


def test_non_numeric_scores_treated_as_zero():
    rec = json.loads(_line("2026-06-09", "https://a/bad"))
    rec["scores"] = {"novelty": "high", "concreteness": True}
    lines = [
        json.dumps(rec),
        _line("2026-06-09", "https://a/good", novelty=1, concreteness=1, reliability=1),
    ]
    items = trends_select.select(lines, asof=ASOF, days=3)
    assert [r["url"] for r in items] == ["https://a/good", "https://a/bad"]


def test_top_limit():
    lines = [_line("2026-06-09", f"https://a/{i}") for i in range(10)]
    items = trends_select.select(lines, asof=ASOF, days=3, top=4)
    assert len(items) == 4


def test_malformed_and_blank_lines_skipped():
    lines = ["not json", "", _line("2026-06-09", "https://a/1")]
    items = trends_select.select(lines, asof=ASOF, days=3)
    assert len(items) == 1


def test_missing_url_skipped():
    rec = json.loads(_line("2026-06-09", "https://a/1"))
    del rec["url"]
    items = trends_select.select([json.dumps(rec)], asof=ASOF, days=3)
    assert items == []


def test_render_term_contains_urls_in_rank_order():
    lines = [
        _line("2026-06-09", "https://high", novelty=5, concreteness=5, title="High"),
        _line("2026-06-09", "https://low", novelty=1, concreteness=1, title="Low"),
    ]
    items = trends_select.select(lines, asof=ASOF, days=3)
    out = trends_select.render_term(items, days=3)
    assert "https://high" in out and "https://low" in out
    assert out.index("https://high") < out.index("https://low")
    assert "High" in out and "example.com" in out


def test_render_term_empty():
    out = trends_select.render_term([], days=3)
    assert "採用記事なし" in out


def test_render_json_roundtrip():
    lines = [_line("2026-06-09", "https://a/1")]
    items = trends_select.select(lines, asof=ASOF, days=3)
    parsed = json.loads(trends_select.render_json(items))
    assert parsed[0]["url"] == "https://a/1"


def test_main_missing_ledger_exits_zero(tmp_path, capsys):
    rc = trends_select.main([str(tmp_path / "none.jsonl"), "--asof", "2026-06-10"])
    assert rc == 0
    assert "採用記事なし" in capsys.readouterr().out


def test_main_invalid_asof_exits_two(tmp_path, capsys):
    rc = trends_select.main([str(tmp_path / "none.jsonl"), "--asof", "junk"])
    assert rc == 2


def test_main_renders_real_file(tmp_path, capsys):
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(_line("2026-06-09", "https://a/1", title="Article") + "\n")
    rc = trends_select.main([str(ledger), "--asof", "2026-06-10", "--days", "3"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "https://a/1" in out and "Article" in out


def test_scores_not_dict_does_not_crash():
    rec = json.loads(_line("2026-06-09", "https://a/bad"))
    rec["scores"] = "high"
    lines = [
        json.dumps(rec),
        _line("2026-06-09", "https://a/good", novelty=2, concreteness=2),
    ]
    items = trends_select.select(lines, asof=ASOF, days=3)
    assert [r["url"] for r in items] == ["https://a/good", "https://a/bad"]
    out = trends_select.render_term(items, days=3)
    assert "https://a/bad" in out


def test_render_term_strips_control_chars():
    rtl_override = chr(0x202E)
    evil_title = "Ti\x1b[31mtle" + rtl_override
    lines = [_line("2026-06-09", "https://a/x\x1b]8;;evil", title=evil_title)]
    items = trends_select.select(lines, asof=ASOF, days=3)
    out = trends_select.render_term(items, days=3)
    assert "\x1b" not in out
    assert rtl_override not in out
