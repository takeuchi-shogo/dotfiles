"""Regression tests for hook_utils.run_hook's fail-open/fail-closed contract.

references/hook-failure-policy.md catalogs 24/30 hook callers as fail-open
(fail_closed=False, the default) — if a hook crashes unexpectedly, run_hook
is supposed to print `{}` and let the session continue rather than blocking
it. No test previously exercised run_hook directly (`grep run_hook
scripts/tests/` turned up nothing); this file fixes that gap.
"""

import io
import json
import sys
from importlib import import_module
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "policy"))

hook_utils = import_module("hook_utils")
run_hook = hook_utils.run_hook
load_hook_input = hook_utils.load_hook_input

# A real, currently-wired PostToolUse hook (settings.json Edit|Write matcher)
# that calls run_hook(..., fail_closed=False) — used below to exercise the
# stdin-reading path through an actual hook, not just hook_utils in isolation.
pib = import_module("plan-implement-bridge")


def test_run_hook_fail_open_prints_empty_json_and_does_not_exit(capsys):
    def _boom():
        raise ValueError("synthetic failure")

    run_hook("fake-hook", _boom, fail_closed=False)

    captured = capsys.readouterr()
    assert json.loads(captured.out) == {}
    assert "[fake-hook] error: synthetic failure" in captured.err


def test_run_hook_default_fail_closed_arg_is_fail_open(capsys):
    """Pin run_hook's default: omitting fail_closed must behave like False.

    references/hook-failure-policy.md counts 12 callers that omit fail_closed
    entirely (relying on the default). Every other test in this file passes
    fail_closed=False explicitly, so none of them would catch the default
    flipping from False to True. This test calls run_hook without the
    keyword to guard that regression.
    """

    def _boom():
        raise ValueError("synthetic failure")

    run_hook("fake-hook", _boom)

    captured = capsys.readouterr()
    assert json.loads(captured.out) == {}
    assert "[fake-hook] error: synthetic failure" in captured.err


def test_run_hook_fail_closed_exits_with_code_2(capsys):
    def _boom():
        raise ValueError("synthetic failure")

    with pytest.raises(SystemExit) as exc_info:
        run_hook("fake-hook", _boom, fail_closed=True)

    assert exc_info.value.code == 2
    assert "failed-closed" in capsys.readouterr().err


def test_run_hook_propagates_systemexit_unchanged():
    def _blocks():
        sys.exit(7)

    with pytest.raises(SystemExit) as exc_info:
        run_hook("fake-hook", _blocks, fail_closed=False)

    assert exc_info.value.code == 7


def test_load_hook_input_malformed_json_returns_empty_dict(monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO("{not valid json"))
    assert load_hook_input() == {}


def test_load_hook_input_empty_stdin_returns_empty_dict(monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))
    assert load_hook_input() == {}


def test_real_hook_survives_malformed_stdin(monkeypatch, capsys):
    """End-to-end: a wired hook must not crash on malformed stdin.

    load_hook_input() returns {} for malformed JSON, so main() should read
    that, return early, and print nothing.
    """
    monkeypatch.setattr(sys, "stdin", io.StringIO("{not valid json"))

    run_hook("plan-implement-bridge", pib.main, fail_closed=False)

    assert capsys.readouterr().out == ""


def test_real_hook_survives_missing_keys_payload(monkeypatch, capsys):
    """A payload missing tool_input must not crash check_tool/_is_plan_file."""
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"tool_name": "Edit"})))

    run_hook("plan-implement-bridge", pib.main, fail_closed=False)

    out = capsys.readouterr().out
    assert json.loads(out) == {"tool_name": "Edit"}  # output_passthrough(data)
