"""Tests for blocked-item handling in the completion-gate Ralph Loop.

The Opus 5.5 prompting guide continues an unattended run only when items are
open *and no blocker is stated*. Before this change the gate counted every
``- [ ]`` line, so an agent that correctly reported "blocked on the user" was
told to continue up to MAX_RALPH_ITERATIONS times anyway.
"""

import json
import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "policy"))

gate = import_module("completion-gate")


def _scan(monkeypatch, tmp_path, body: str):
    """Run the real plan scanner over one plan file in an isolated plan dir."""
    (tmp_path / "2026-09-24-example.md").write_text(body)
    monkeypatch.setattr(gate, "PLAN_DIRS", [str(tmp_path)])
    monkeypatch.setattr(gate, "_load_plan_snapshot", lambda: {})
    monkeypatch.setattr(gate, "_is_session_relevant", lambda *a: True)
    return gate._find_incomplete_plan()


def test_blocked_item_is_not_counted_as_pending(monkeypatch, tmp_path):
    """
    前提: plan の未チェック項目は 1 件だけで、それに (blocked: ...) が付いている。
    検証: 続行を促す未完了項目が無いので None を返す (gate は停止を許す)。
    """
    body = (
        "- [x] step A\n- [ ] step B (blocked: API key を user が発行するまで進めない)\n"
    )
    assert _scan(monkeypatch, tmp_path, body) is None


def test_unblocked_items_remain_pending_next_to_blocked_one(monkeypatch, tmp_path):
    """
    前提: blocked 項目と、blocker の無い未チェック項目が混在する。
    検証: blocker の無い項目だけが pending として返る。
    """
    body = "- [ ] step B (blocked: waiting for review)\n- [ ] step C\n"
    result = _scan(monkeypatch, tmp_path, body)
    assert result is not None
    _, pending, _ = result
    assert pending == ["- [ ] step C"]


def test_continue_message_asks_for_the_blocker(monkeypatch, capsys):
    """
    前提: 未完了 plan があり、Ralph Loop の上限には達していない。
    検証: 差し戻し文が、塞がっている項目に blocker を書く方法を示している。
    """
    plan = ("2026-09-24-example", ["- [ ] step C"], "all steps done")
    monkeypatch.setattr(gate, "_get_retry_count", lambda: 0)
    monkeypatch.setattr(gate, "_reset_retries", lambda: None)
    monkeypatch.setattr(gate, "_get_ralph_count", lambda: 0)
    monkeypatch.setattr(gate, "_set_ralph_count", lambda n: None)
    monkeypatch.setattr(gate, "_reset_ralph", lambda: None)
    monkeypatch.setattr(gate, "_find_incomplete_plan", lambda: plan)
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    gate.main()
    reason = json.loads(capsys.readouterr().out)["reason"]
    assert "(blocked:" in reason
