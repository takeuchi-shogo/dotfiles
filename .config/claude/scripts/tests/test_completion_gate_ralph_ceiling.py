"""Tests for the Ralph Loop iteration ceiling in completion-gate.py.

Regression for the shared-counter bug: the safety valve compared the retry
counter against MAX_RETRIES (2) before the Ralph Loop branch ran, while the
Ralph branch advanced that same counter. MAX_RALPH_ITERATIONS was therefore
unreachable and a Ralph Loop stopped after 2 iterations. Sharing the counter
also leaked the other way: iterations spent in a Ralph Loop pushed the retry
count past MAX_RETRIES, so the next stop skipped the test and harness gates.
"""

import json
import sys
from importlib import import_module
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "policy"))

gate = import_module("completion-gate")

PLAN = ("2026-07-31-example", ["  - [ ] step A"], "all steps done")


def _run(
    monkeypatch, capsys, *, retries=0, ralph=0, incomplete=None, harness_block=None
) -> dict:
    """Drive main() with both counters stubbed and the plan scanner faked.

    The downstream gates run real git and filesystem checks, so they are stubbed
    out too — otherwise these assertions would flip with the worktree's state.
    """
    seen: dict = {}

    monkeypatch.setattr(gate, "_get_retry_count", lambda: retries)
    monkeypatch.setattr(gate, "_set_retry_count", lambda n: seen.update(retry_set=n))
    monkeypatch.setattr(gate, "_reset_retries", lambda: seen.update(retry_reset=True))
    monkeypatch.setattr(gate, "_get_ralph_count", lambda: ralph)
    monkeypatch.setattr(gate, "_set_ralph_count", lambda n: seen.update(ralph_set=n))
    monkeypatch.setattr(gate, "_reset_ralph", lambda: seen.update(ralph_reset=True))
    monkeypatch.setattr(gate, "_find_incomplete_plan", lambda: incomplete)

    def _harness_gate(session_id: str = ""):
        seen["harness_gate_reached"] = True
        return harness_block

    def _test_command():
        seen["test_gate_reached"] = True
        return None

    monkeypatch.setattr(gate, "_check_harness_review_gate", _harness_gate)
    monkeypatch.setattr(gate, "_detect_test_command", _test_command)
    monkeypatch.delenv("CLAUDE_SKIP_TEST_GATE", raising=False)
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    gate.main()
    out = capsys.readouterr().out
    seen["payload"] = json.loads(out) if out.strip() else {}
    return seen


def test_ralph_loop_survives_past_max_retries(monkeypatch, capsys):
    """A stale retry count must not cut a Ralph Loop short."""
    result = _run(
        monkeypatch, capsys, retries=gate.MAX_RETRIES, ralph=0, incomplete=PLAN
    )

    assert result["payload"]["decision"] == "block"
    assert result["ralph_set"] == 1


def test_ralph_loop_stops_at_max_ralph_iterations(monkeypatch, capsys):
    """The ceiling that ends the loop is MAX_RALPH_ITERATIONS, on its own counter."""
    result = _run(monkeypatch, capsys, ralph=gate.MAX_RALPH_ITERATIONS, incomplete=PLAN)

    assert result["payload"].get("decision") is None
    assert result.get("ralph_reset") is True


def test_ralph_iterations_do_not_leak_into_the_test_gate(monkeypatch, capsys):
    """Finishing a plan after many Ralph iterations must not skip the test gate.

    The shared counter used to land here above MAX_RETRIES, so the safety valve
    allowed the stop before the test and harness gates ever ran.
    """
    result = _run(
        monkeypatch, capsys, retries=0, ralph=gate.MAX_RALPH_ITERATIONS, incomplete=None
    )

    assert result.get("harness_gate_reached") is True
    assert result.get("test_gate_reached") is True
    assert result.get("ralph_reset") is True


def test_completed_plan_clears_the_ralph_counter(monkeypatch, capsys):
    """No incomplete plan means the next Ralph Loop starts from zero."""
    result = _run(monkeypatch, capsys, ralph=3, incomplete=None)

    assert result.get("ralph_reset") is True


def test_ralph_ceiling_stays_under_the_stop_hook_block_cap():
    """Claude Code overrides a Stop hook after 8 consecutive blocks.

    A ceiling at or above that is dead config: the runtime stops the loop first.
    """
    assert gate.MAX_RALPH_ITERATIONS < 8


def test_without_plan_the_ceiling_is_max_retries(monkeypatch, capsys):
    """No incomplete plan: the test-gate ceiling stays at MAX_RETRIES."""
    result = _run(monkeypatch, capsys, retries=gate.MAX_RETRIES, incomplete=None)

    assert result["payload"].get("decision") != "block"
    assert result.get("retry_reset") is True


def test_graduated_mode_still_hands_back_at_the_ralph_ceiling(monkeypatch, capsys):
    """Stopping with an incomplete plan is exactly when handback is needed."""
    monkeypatch.setattr(gate, "COMPLETION_MODE", "graduated")
    monkeypatch.setattr(gate, "_generate_handback_report", lambda: "HANDBACK")

    result = _run(monkeypatch, capsys, ralph=gate.MAX_RALPH_ITERATIONS, incomplete=PLAN)

    assert result["payload"].get("decision") is None
    assert result["payload"]["systemMessage"] == "HANDBACK"


@pytest.mark.parametrize(
    "exc",
    [
        PermissionError("plans dir unreadable"),
        UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte"),
    ],
)
def test_plan_scan_error_falls_back_to_the_test_gate_ceiling(monkeypatch, capsys, exc):
    """An unreadable plan directory must not take the whole gate down."""

    def boom():
        raise exc

    monkeypatch.setattr(gate, "_find_incomplete_plan", boom)
    monkeypatch.setattr(gate, "_get_retry_count", lambda: gate.MAX_RETRIES)
    monkeypatch.setattr(gate, "_reset_retries", lambda: None)
    monkeypatch.setattr(gate, "_reset_ralph", lambda: None)
    monkeypatch.delenv("CLAUDE_SKIP_TEST_GATE", raising=False)
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    gate.main()

    assert capsys.readouterr().err


def test_ralph_ceiling_does_not_bypass_the_harness_review_gate(monkeypatch, capsys):
    """Exhausting the Ralph budget stops the nagging, not the mandatory gates."""
    result = _run(
        monkeypatch,
        capsys,
        ralph=gate.MAX_RALPH_ITERATIONS,
        incomplete=PLAN,
        harness_block={"decision": "block", "reason": "harness review required"},
    )

    assert result["payload"]["decision"] == "block"
    assert result.get("ralph_reset") is not True


def test_ralph_block_clears_a_stale_test_failure_count(monkeypatch, capsys):
    """Plan work breaks the consecutive-test-failure chain.

    Otherwise a retry count left at MAX_RETRIES rides through the whole Ralph
    Loop and lets the next stop skip the test and harness gates.
    """
    result = _run(
        monkeypatch, capsys, retries=gate.MAX_RETRIES, ralph=0, incomplete=PLAN
    )

    assert result["payload"]["decision"] == "block"
    assert result.get("retry_reset") is True


def test_counters_are_separate_files():
    """Guard the premise: one shared file would make these tests vacuous."""
    assert gate.RALPH_COUNTER_FILE != gate.COUNTER_FILE
