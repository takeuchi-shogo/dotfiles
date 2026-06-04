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


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
