"""sources.py の pure logic 検証。

実行: uv run pytest scripts/runtime/tech-researcher/tests/test_sources.py
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sources  # noqa: E402

ASOF = date(2026, 6, 6)


# --- is_safe_feed_url / parse_seed (SSRF guard) ---


@pytest.mark.parametrize(
    "url",
    [
        "https://zenn.dev/topics/ai/feed",
        "http://example.com/feed.xml",
        "https://huggingface.co/blog/feed.xml",
        "https://host.com:8443/feed",  # 通常 port は許可
    ],
)
def test_is_safe_feed_url_allows_public_http(url):
    assert sources.is_safe_feed_url(url) is True


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "ftp://example.com/x",
        "http://127.0.0.1/feed",
        "http://localhost:8080/feed",
        "https://169.254.169.254/latest/meta-data/",  # IMDS
        "http://10.0.0.5/feed",
        "http://192.168.1.1/feed",
        "http://172.16.0.1/feed",
        "http://172.31.255.255/feed",
        "http://[::1]:9000/feed",
        "http://0.0.0.0/feed",
        "https://user:pass@127.0.0.1/feed",  # userinfo で偽装しても host で弾く
        "not a url",
    ],
)
def test_is_safe_feed_url_blocks_unsafe(url):
    assert sources.is_safe_feed_url(url) is False


def test_is_safe_feed_url_allows_172_outside_private_range():
    # 172.32.x は private 範囲外 (16-31 のみ private)
    assert sources.is_safe_feed_url("http://172.32.0.1/feed") is True
    assert sources.is_safe_feed_url("http://172.15.0.1/feed") is True


def test_parse_seed_strips_comments_blanks_and_unsafe():
    text = "\n".join(
        [
            "# header comment",
            "",
            "https://zenn.dev/topics/ai/feed   # inline comment",
            "  https://qiita.com/tags/ai/feed.atom  ",
            "ftp://bad/x",  # non-http → skip
            "http://127.0.0.1/feed",  # private → skip
            "https://huggingface.co/blog/feed.xml",
        ]
    )
    assert sources.parse_seed(text) == [
        "https://zenn.dev/topics/ai/feed",
        "https://qiita.com/tags/ai/feed.atom",
        "https://huggingface.co/blog/feed.xml",
    ]


# --- bootstrap_rows ---


def test_bootstrap_empty_ledger_seeds_all_as_active():
    seeds = ["https://a.dev/feed", "https://b.dev/feed"]
    rows = sources.bootstrap_rows([], seeds, asof=ASOF)
    assert [r["value"] for r in rows] == seeds
    assert all(r["type"] == "web" for r in rows)
    assert all(r["status"] == "active" for r in rows)
    assert all(r["score"] == 0.0 and r["last_adopted"] is None for r in rows)
    assert all(r["added_date"] == "2026-06-06" for r in rows)


def test_bootstrap_is_idempotent_and_preserves_existing():
    existing = [
        json.dumps(
            {
                "type": "web",
                "value": "https://a.dev/feed",
                "added_date": "2026-06-01",
                "score": 0.42,
                "last_adopted": "2026-06-05",
                "status": "retired",  # 進化結果
            }
        )
    ]
    seeds = ["https://a.dev/feed", "https://b.dev/feed"]  # a は既存, b は新規
    rows = sources.bootstrap_rows(existing, seeds, asof=ASOF)
    by_val = {r["value"]: r for r in rows}
    # 既存 a の status/score/added_date は維持 (seed 再実行で潰さない)
    assert by_val["https://a.dev/feed"]["status"] == "retired"
    assert by_val["https://a.dev/feed"]["score"] == 0.42
    assert by_val["https://a.dev/feed"]["added_date"] == "2026-06-01"
    # 新規 b のみ追加
    assert by_val["https://b.dev/feed"]["status"] == "active"
    assert len(rows) == 2


def test_bootstrap_skips_malformed_existing_lines():
    existing = ["not json", "{broken", json.dumps({"type": "web"})]  # value 欠落
    rows = sources.bootstrap_rows(existing, ["https://a.dev/feed"], asof=ASOF)
    assert [r["value"] for r in rows] == ["https://a.dev/feed"]


# --- list_active ---


def _src(value, status="active", typ="web"):
    return json.dumps(
        {
            "type": typ,
            "value": value,
            "added_date": "2026-06-01",
            "score": 0.0,
            "last_adopted": None,
            "status": status,
        }
    )


def test_list_active_filters_status_and_type():
    lines = [
        _src("https://a.dev/feed", "active"),
        _src("https://b.dev/feed", "retired"),
        _src("https://c.dev/feed", "candidate"),
        _src("kw-llm", "active", typ="keyword"),
    ]
    assert sources.list_active(lines) == ["https://a.dev/feed", "kw-llm"]
    assert sources.list_active(lines, type_filter="web") == ["https://a.dev/feed"]
    assert sources.list_active(lines, type_filter="keyword") == ["kw-llm"]


# --- refresh_rows ---


def _adopt(d, source_id, adopted, scores=None):
    rec = {
        "ts": f"{d}T00:00:00+09:00",
        "date": d,
        "domain": "x.dev",
        "url": f"https://x.dev/{d}",
        "title": "t",
        "adopted": adopted,
        "source_id": source_id,
        "scores": scores,
    }
    return json.dumps(rec, ensure_ascii=False)


def test_refresh_computes_score_and_last_adopted():
    ledger = [_src("https://a.dev/feed"), _src("https://b.dev/feed")]
    adoption = [
        _adopt("2026-06-06", "https://a.dev/feed", True),
        _adopt("2026-06-06", "https://a.dev/feed", False),
        _adopt("2026-06-04", "https://a.dev/feed", True),
        # b は採用なし
        _adopt("2026-06-05", "https://b.dev/feed", False),
    ]
    rows = sources.refresh_rows(ledger, adoption, asof=ASOF, days=30)
    by = {r["value"]: r for r in rows}
    # a: adopted 2 / total 3
    assert by["https://a.dev/feed"]["score"] == pytest.approx(2 / 3, abs=1e-4)
    assert by["https://a.dev/feed"]["last_adopted"] == "2026-06-06"
    # b: adopted 0 / total 1
    assert by["https://b.dev/feed"]["score"] == 0.0
    assert by["https://b.dev/feed"]["last_adopted"] is None


def test_refresh_keeps_status_unchanged():
    ledger = [_src("https://a.dev/feed", status="candidate")]
    adoption = [_adopt("2026-06-06", "https://a.dev/feed", True)]
    rows = sources.refresh_rows(ledger, adoption, asof=ASOF, days=30)
    assert rows[0]["status"] == "candidate"  # D4: 昇格降格しない


def test_refresh_window_excludes_old_for_score_but_keeps_last_adopted_history():
    # 既存 last_adopted が窓外でも history として保持
    line = json.dumps(
        {
            "type": "web",
            "value": "https://a.dev/feed",
            "added_date": "2026-01-01",
            "score": 0.9,
            "last_adopted": "2026-03-01",
            "status": "active",
        }
    )
    rows = sources.refresh_rows([line], [], asof=ASOF, days=30)
    assert rows[0]["score"] == 0.0  # 窓内観測なし
    assert rows[0]["last_adopted"] == "2026-03-01"  # 既存 history 維持


def test_refresh_ignores_orphan_and_phase1_rows():
    ledger = [_src("https://a.dev/feed")]
    adoption = [
        _adopt("2026-06-06", "https://orphan.dev/feed", True),  # ledger に無い (E7)
        json.dumps(  # Phase 1 行: source_id 欠落
            {"date": "2026-06-06", "domain": "a.dev", "adopted": True}
        ),
    ]
    rows = sources.refresh_rows(ledger, adoption, asof=ASOF, days=30)
    assert len(rows) == 1
    assert rows[0]["score"] == 0.0  # a への寄与なし


# --- prune_lines ---


def test_prune_splits_by_keep_window():
    adoption = [
        _adopt("2026-06-06", "s", True),  # 窓内
        _adopt("2026-03-09", "s", True),  # keep_days=90 窓内境界 (90日: 3/9..6/6)
        _adopt("2026-03-08", "s", True),  # 窓外 (91日前)
    ]
    kept, archived = sources.prune_lines(adoption, asof=ASOF, keep_days=90)
    assert len(kept) == 2
    assert len(archived) == 1
    assert "2026-03-08" in archived[0]


def test_prune_keeps_malformed_and_skips_blank():
    adoption = ["not json", "", _adopt("2026-01-01", "s", True)]
    kept, archived = sources.prune_lines(adoption, asof=ASOF, keep_days=90)
    assert "not json" in kept  # 日付不明は保守的に kept
    assert len(archived) == 1  # 古い valid 行のみ archive


@pytest.mark.parametrize(
    "url",
    [
        "http://2130706433/x",
        "http://0x7f000001/x",
        "http://017700000001/x",
        "http://0177.0.0.1/x",
        "http://0x7f.0.0.1/x",
        "http://0xA9FEA9FE/x",
        "http://[::ffff:127.0.0.1]/x",
        "http://[0:0:0:0:0:ffff:7f00:1]/x",
        "http://0/x",
        "http://127.1/x",
        "http://127.0.1/x",
        "http://0x7f.1/x",
    ],
)
def test_is_safe_feed_url_blocks_alternative_ip_encodings(url):
    """prefix 一致で bypass される別表記 loopback/IMDS を canonical 化して拒否。"""
    assert sources.is_safe_feed_url(url) is False


def test_is_safe_feed_url_still_allows_public_after_hardening():
    assert sources.is_safe_feed_url("https://zenn.dev/topics/ai/feed") is True
    assert sources.is_safe_feed_url("http://172.32.0.1/feed") is True
    assert sources.is_safe_feed_url("https://huggingface.co/blog/feed.xml") is True


def test_refresh_skips_keyword_sources():
    """keyword source は feed source_id と join できず score をリセットしない (F6)。"""
    kw = json.dumps(
        {
            "type": "keyword",
            "value": "Claude Code",
            "added_date": "2026-06-01",
            "score": 0.77,
            "last_adopted": "2026-06-05",
            "status": "active",
        }
    )
    rows = sources.refresh_rows([kw], [], asof=ASOF, days=30)
    assert rows[0]["score"] == 0.77
    assert rows[0]["last_adopted"] == "2026-06-05"


def test_cmd_bootstrap_rejects_invalid_asof(tmp_path):
    seed = tmp_path / "sources.txt"
    seed.write_text("https://zenn.dev/topics/ai/feed\n", encoding="utf-8")
    ledger = tmp_path / "sl.jsonl"
    rc = sources.main(
        [
            "bootstrap",
            "--seed",
            str(seed),
            "--ledger",
            str(ledger),
            "--asof",
            "2026-13-99",
        ]
    )
    assert rc == 2
    assert not ledger.exists()


def test_cmd_refresh_rejects_invalid_asof(tmp_path):
    ledger = tmp_path / "sl.jsonl"
    ledger.write_text(_src("https://a.dev/feed"), encoding="utf-8")
    adoption = tmp_path / "al.jsonl"
    adoption.write_text("", encoding="utf-8")
    rc = sources.main(
        [
            "refresh",
            "--ledger",
            str(ledger),
            "--adoption",
            str(adoption),
            "--asof",
            "nope",
        ]
    )
    assert rc == 2


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
