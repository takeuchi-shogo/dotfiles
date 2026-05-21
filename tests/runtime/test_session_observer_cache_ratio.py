"""Unit tests for session_observer cache ratio + warning emission.

Plan: docs/plans/active/2026-05-22-token-cache-observer-extension.md
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_RUNTIME_DIR = (
    Path(__file__).resolve().parents[2] / ".config" / "claude" / "scripts" / "runtime"
)
sys.path.insert(0, str(_RUNTIME_DIR))

import session_observer_fmt as fmt  # noqa: E402
import session_observer_parse as parse  # noqa: E402


def _usage(cr: int, cw: int, inp: int = 100) -> dict:
    return {
        "input_tokens": inp,
        "cache_read_input_tokens": cr,
        "cache_creation_input_tokens": cw,
    }


@pytest.fixture(autouse=True)
def _reset_tracker():
    parse.reset_cache_tracker()
    yield
    parse.reset_cache_tracker()


class TestCacheRatio:
    def test_cold_start_returns_none(self):
        ev = parse._make_usage_event(_usage(0, 0, 0), "opus", {}, "sid")
        assert ev["cache_ratio"] is None
        assert "warning" not in ev

    def test_healthy_ratio_no_warning(self):
        ev = parse._make_usage_event(_usage(cr=900, cw=0, inp=100), "opus", {}, "sid")
        assert ev["cache_ratio"] == pytest.approx(0.9)
        assert "warning" not in ev

    def test_only_input_zero_division_guard(self):
        # input>0, no cache activity yet — ratio is 0.0, not error
        ev = parse._make_usage_event(_usage(cr=0, cw=0, inp=500), "opus", {}, "sid")
        assert ev["cache_ratio"] == 0.0
        assert "warning" not in ev


class TestWarningTrigger:
    def test_low_ratio_alone_no_warning(self):
        # ratio < 30% but streak too short (read=0, create>0 only 1 turn)
        ev = parse._make_usage_event(_usage(cr=0, cw=500, inp=100), "opus", {}, "sid")
        assert ev["cache_ratio"] == pytest.approx(0.0)
        assert "warning" not in ev

    def test_streak_alone_high_ratio_no_warning(self):
        # cache_read present で 5 ターン回しても streak が立たない
        for _ in range(5):
            ev = parse._make_usage_event(
                _usage(cr=900, cw=50, inp=100), "opus", {}, "sid"
            )
        assert "warning" not in ev

    def test_warning_fires_on_4th_consecutive_miss(self):
        events = [
            parse._make_usage_event(_usage(cr=0, cw=500, inp=100), "opus", {}, "sid")
            for _ in range(4)
        ]
        # Only the 4th event crosses streak > 3
        assert "warning" not in events[2]
        assert events[3]["warning"] == "cache_miss_burst"
        assert events[3]["cache_create_streak"] == 4

    def test_cache_read_breaks_streak(self):
        # 3 misses → cache_read 1 回 → 4 misses。recovery で streak が reset
        for _ in range(3):
            parse._make_usage_event(_usage(cr=0, cw=500, inp=100), "opus", {}, "sid")
        recovery = parse._make_usage_event(
            _usage(cr=400, cw=0, inp=100), "opus", {}, "sid"
        )
        assert "warning" not in recovery
        events = [
            parse._make_usage_event(_usage(cr=0, cw=500, inp=100), "opus", {}, "sid")
            for _ in range(4)
        ]
        # Streak resets and only crosses limit on the 4th post-recovery miss
        assert "warning" not in events[2]
        assert events[3]["warning"] == "cache_miss_burst"

    def test_high_ratio_above_80_never_warns(self):
        for _ in range(10):
            ev = parse._make_usage_event(
                _usage(cr=900, cw=0, inp=100), "opus", {}, "sid"
            )
            assert "warning" not in ev


class TestExistingFormatPreserved:
    def test_compact_includes_existing_fields(self):
        ev = parse._make_usage_event(_usage(cr=100, cw=50, inp=10), "opus", {}, "sid")
        line = fmt.usage(ev, compact=True)
        # 既存フィールド (in/out/cr/cw) は維持されている
        assert "in=10" in line
        assert "cr=100" in line
        assert "cw=50" in line
        # 追加フィールド
        assert "ratio=" in line

    def test_rich_includes_existing_fields(self):
        ev = parse._make_usage_event(_usage(cr=900, cw=0, inp=100), "opus", {}, "sid")
        line = fmt.usage(ev, compact=False)
        assert "cache_read=900" in line
        assert "cache_create=0" in line
        assert "ratio=90%" in line

    def test_legacy_raw_keys_still_supported(self):
        # 旧 API 形式 (cache_read_input_tokens) を直接食わせても落ちない
        legacy = {
            "input_tokens": 100,
            "output_tokens": 50,
            "cache_read_input_tokens": 800,
            "cache_creation_input_tokens": 0,
        }
        line = fmt.usage(legacy, compact=False)
        assert "cache_read=800" in line
        assert "ratio=n/a" in line  # cache_ratio フィールド未指定

    def test_warning_appended_only_when_present(self):
        ev = parse._make_usage_event(_usage(cr=900, cw=0, inp=100), "opus", {}, "sid")
        line = fmt.usage(ev, compact=False)
        assert "cache warning" not in line


class TestWarningFormatting:
    def test_warning_shown_in_rich(self):
        for _ in range(4):
            ev = parse._make_usage_event(
                _usage(cr=0, cw=500, inp=100), "opus", {}, "sid"
            )
        line = fmt.usage(ev, compact=False)
        assert "cache warning: cache_miss_burst" in line
        assert "streak=4" in line

    def test_warning_shown_in_compact(self):
        for _ in range(4):
            ev = parse._make_usage_event(
                _usage(cr=0, cw=500, inp=100), "opus", {}, "sid"
            )
        line = fmt.usage(ev, compact=True)
        assert "cache_miss_burst" in line
