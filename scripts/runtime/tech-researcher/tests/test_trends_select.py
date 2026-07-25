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
    harness_relevance: int | None = None,
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
        if harness_relevance is not None:
            scores["harness_relevance"] = harness_relevance
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


def test_harness_below_threshold_excluded():
    lines = [
        _line("2026-06-09", "https://hi", harness_relevance=5),
        _line("2026-06-09", "https://lo", harness_relevance=2),
    ]
    items = trends_select.select_harness_candidates(
        lines, asof=ASOF, days=3, min_relevance=4
    )
    assert [r["url"] for r in items] == ["https://hi"]


def test_harness_thin_night_returns_empty():
    lines = [
        _line("2026-06-09", "https://a", harness_relevance=2),
        _line("2026-06-09", "https://b", harness_relevance=3),
    ]
    items = trends_select.select_harness_candidates(
        lines, asof=ASOF, days=3, min_relevance=4
    )
    assert items == []


def test_harness_sort_relevance_desc_then_date():
    lines = [
        _line("2026-06-09", "https://mid", harness_relevance=4),
        _line("2026-06-09", "https://top", harness_relevance=5),
        _line("2026-06-08", "https://tie-old", harness_relevance=5),
    ]
    items = trends_select.select_harness_candidates(
        lines, asof=ASOF, days=7, min_relevance=4
    )
    assert [r["url"] for r in items] == [
        "https://top",
        "https://tie-old",
        "https://mid",
    ]


def test_harness_missing_axis_treated_as_zero_excluded():
    lines = [
        _line("2026-06-09", "https://has", harness_relevance=4),
        _line("2026-06-09", "https://old"),
    ]
    items = trends_select.select_harness_candidates(
        lines, asof=ASOF, days=3, min_relevance=1
    )
    assert [r["url"] for r in items] == ["https://has"]


def test_harness_adopted_false_excluded():
    lines = [
        _line("2026-06-09", "https://yes", harness_relevance=5),
        _line("2026-06-09", "https://no", adopted=False, harness_relevance=5),
    ]
    items = trends_select.select_harness_candidates(
        lines, asof=ASOF, days=3, min_relevance=4
    )
    assert [r["url"] for r in items] == ["https://yes"]


def test_harness_window_cutoff_excludes_old():
    lines = [
        _line("2026-06-09", "https://new", harness_relevance=5),
        _line("2026-06-01", "https://old", harness_relevance=5),
    ]
    items = trends_select.select_harness_candidates(
        lines, asof=ASOF, days=3, min_relevance=4
    )
    assert [r["url"] for r in items] == ["https://new"]


def test_harness_url_dedup_keeps_latest_date():
    lines = [
        _line("2026-06-08", "https://a/1", harness_relevance=2),
        _line("2026-06-09", "https://a/1", harness_relevance=5),
    ]
    items = trends_select.select_harness_candidates(
        lines, asof=ASOF, days=7, min_relevance=4
    )
    assert len(items) == 1
    assert items[0]["date"] == "2026-06-09"


REPORT = """## AI Tech Trends 2026-06-09

- [2] [example.com] 記事Aの一行要約。
- [5] [example.com] 記事Bの一行要約。

## 出典

- [2] [example.com] 記事A
  https://a/1
- [5] [example.com] 記事B
  https://a/2
- [9] [example.com] 要約なし記事
  https://a/3
"""


def test_load_summaries_joins_by_index():
    m = trends_select.load_summaries([REPORT])
    assert m == {
        "https://a/1": "記事Aの一行要約。",
        "https://a/2": "記事Bの一行要約。",
    }


def test_load_summaries_without_sources_section_is_empty():
    assert trends_select.load_summaries(["- [1] [x] 要約のみで出典なし"]) == {}


def test_load_summaries_later_report_wins():
    older = REPORT
    newer = REPORT.replace("記事Aの一行要約。", "更新された要約。")
    m = trends_select.load_summaries([older, newer])
    assert m["https://a/1"] == "更新された要約。"


def test_render_term_inserts_summary_between_title_and_url():
    items = trends_select.select(
        [_line("2026-06-09", "https://a/1", title="記事A")], asof=ASOF, days=3
    )
    out = trends_select.render_term(
        items, days=3, summaries={"https://a/1": "記事Aの一行要約。"}
    )
    lines = out.splitlines()
    i = next(n for n, ln in enumerate(lines) if "記事A" in ln)
    assert lines[i + 1].strip() == "└ 記事Aの一行要約。"
    assert lines[i + 2].strip() == "https://a/1"


def test_render_term_without_summaries_unchanged():
    items = trends_select.select(
        [_line("2026-06-09", "https://a/1")], asof=ASOF, days=3
    )
    assert trends_select.render_term(items, days=3) == trends_select.render_term(
        items, days=3, summaries={}
    )


def test_main_reports_dir_shows_summary(tmp_path, capsys):
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(_line("2026-06-09", "https://a/1") + "\n", encoding="utf-8")
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "2026-06-09.md").write_text(REPORT, encoding="utf-8")
    rc = trends_select.main(
        [str(ledger), "--asof", "2026-06-10", "--reports-dir", str(reports)]
    )
    assert rc == 0
    assert "└ 記事Aの一行要約。" in capsys.readouterr().out


def test_main_reports_dir_missing_degrades_silently(tmp_path, capsys):
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(_line("2026-06-09", "https://a/1") + "\n", encoding="utf-8")
    rc = trends_select.main(
        [str(ledger), "--asof", "2026-06-10", "--reports-dir", str(tmp_path / "nope")]
    )
    assert rc == 0
    assert "https://a/1" in capsys.readouterr().out


def test_render_term_summary_truncation_boundary():
    items = trends_select.select(
        [_line("2026-06-09", "https://a/1")], asof=ASOF, days=3
    )
    exact = "あ" * 100
    out = trends_select.render_term(items, days=3, summaries={"https://a/1": exact})
    assert f"└ {exact}\n" in out
    assert "…" not in out
    over = "い" * 101
    out = trends_select.render_term(items, days=3, summaries={"https://a/1": over})
    assert f"└ {'い' * 100}…" in out
    assert "い" * 101 not in out


def test_render_term_summary_strips_control_chars():
    items = trends_select.select(
        [_line("2026-06-09", "https://a/1")], asof=ASOF, days=3
    )
    esc, bel = chr(27), chr(7)
    out = trends_select.render_term(
        items, days=3, summaries={"https://a/1": f"要約{esc}[31m注入{bel}文"}
    )
    assert esc not in out
    assert bel not in out
    assert "要約[31m注入文" in out


def test_main_multiple_reports_newest_wins(tmp_path, capsys):
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(_line("2026-06-09", "https://a/1") + "\n", encoding="utf-8")
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "2026-06-09.md").write_text(REPORT, encoding="utf-8")
    (reports / "2026-06-10.md").write_text(
        REPORT.replace("記事Aの一行要約。", "翌日の更新要約。"), encoding="utf-8"
    )
    rc = trends_select.main(
        [str(ledger), "--asof", "2026-06-10", "--reports-dir", str(reports)]
    )
    assert rc == 0
    assert "└ 翌日の更新要約。" in capsys.readouterr().out


def test_main_json_format_ignores_reports_dir(tmp_path, capsys):
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(_line("2026-06-09", "https://a/1") + "\n", encoding="utf-8")
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "2026-06-09.md").write_text(REPORT, encoding="utf-8")
    rc = trends_select.main(
        [
            str(ledger),
            "--asof",
            "2026-06-10",
            "--format",
            "json",
            "--reports-dir",
            str(reports),
        ]
    )
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed[0]["url"] == "https://a/1"
    assert "記事Aの一行要約。" not in json.dumps(parsed, ensure_ascii=False)


def test_main_report_read_error_warns_and_degrades(tmp_path, capsys):
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(_line("2026-06-09", "https://a/1") + "\n", encoding="utf-8")
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "2026-06-09.md").write_bytes(bytes([0xFF, 0xFE, 0x00]) + b"broken")
    rc = trends_select.main(
        [str(ledger), "--asof", "2026-06-10", "--reports-dir", str(reports)]
    )
    assert rc == 0
    captured = capsys.readouterr()
    assert "https://a/1" in captured.out
    assert "WARN: report read failed" in captured.err
