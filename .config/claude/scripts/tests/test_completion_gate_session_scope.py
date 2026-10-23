"""Tests for per-session state in the completion-gate Ralph Loop.

The plan snapshot and the Ralph / retry counters used to be single
machine-wide files. A session started later in another repo overwrote the
snapshot with ``plans: {}``, so every existing plan here looked "created this
session" and blocked stop; any session whose Stop found no plan reset the
shared counter, so the loop restarted at 1/7 instead of reaching its ceiling.
"""

import io
import json
import os
import shutil
import subprocess
import sys
from importlib import import_module
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS / "lib"))
sys.path.insert(0, str(SCRIPTS / "policy"))

gate = import_module("completion-gate")


@pytest.fixture
def isolated(monkeypatch, tmp_path):
    """Point every file main() touches at tmp_path and stub the unrelated gates.

    main() rebinds the module-level paths, so they are monkeypatched here to be
    restored at teardown and never reach the real ~/.claude or $TMPDIR files.
    """
    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    state = tmp_path / "state"
    state.mkdir()
    monkeypatch.setattr(gate, "PLAN_DIRS", [str(plan_dir)])
    monkeypatch.setattr(
        gate, "SNAPSHOT_FILE", str(state / "active-plans-snapshot.json")
    )
    monkeypatch.setattr(gate, "COUNTER_DIR", str(tmp_path))
    monkeypatch.setattr(gate, "RALPH_COUNTER_FILE", str(tmp_path / "ralph-iterations"))
    monkeypatch.setattr(gate, "COUNTER_FILE", str(tmp_path / "retries"))
    monkeypatch.setattr(gate, "_check_fabricated_claims", lambda d: None)
    monkeypatch.setattr(gate, "_check_harness_review_gate", lambda s: None)
    monkeypatch.setattr(gate, "_detect_test_command", lambda: None)
    return plan_dir, state


def _run_stop(monkeypatch, capsys, session_id: str) -> str:
    monkeypatch.setattr(
        sys, "stdin", io.StringIO(json.dumps({"session_id": session_id}))
    )
    gate.main()
    return capsys.readouterr().out


def test_session_scoped_appends_id_before_extension():
    """
    検証: session_id があればファイル名に埋め込み、拡張子は保つ。
    """
    assert gate._session_scoped("/s/active-plans-snapshot.json", "ab-12") == (
        "/s/active-plans-snapshot-ab-12.json"
    )
    assert gate._session_scoped("/t/ralph-iterations", "ab-12") == (
        "/t/ralph-iterations-ab-12"
    )


@pytest.mark.parametrize(
    "bad", ["", "../etc", "a/b", "a b", "ab\n", "a\x00b", "é", "x" * 129]
)
def test_session_scoped_rejects_unusable_ids(bad):
    """
    前提: session_id は hook stdin 由来で、ファイル名に直接埋め込まれる。
    検証: ディレクトリを抜けうる文字・非 ASCII・ファイル名長上限を超える長さは
          採用せず、元のパスを返す。
    """
    assert gate._session_scoped("/t/ralph-iterations", bad) == "/t/ralph-iterations", (
        bad
    )


def test_other_sessions_snapshot_does_not_make_old_plan_relevant(
    monkeypatch, capsys, isolated
):
    """
    前提: 未完了の plan が 1 つあり、この session (A) の開始時 snapshot に
          記録済みで、その後は変更されていない。別 repo の session (B) が
          後から共有の snapshot を plans: {} で上書きしている。
    検証: A の Stop は A の snapshot を読むので、この plan では block しない。
    """
    plan_dir, state = isolated
    plan = plan_dir / "2026-10-13-old.md"
    plan.write_text("- [ ] T0\n")
    (state / "active-plans-snapshot.json").write_text(json.dumps({"plans": {}}))
    (state / "active-plans-snapshot-sessA.json").write_text(
        json.dumps({"plans": {plan.name: {"mtime": os.path.getmtime(plan) * 1000}}})
    )

    out = _run_stop(monkeypatch, capsys, "sessA")

    assert '"decision": "block"' not in out, out


def test_plan_missing_from_this_sessions_snapshot_still_blocks(
    monkeypatch, capsys, isolated
):
    """
    前提: 上のテストと同じ plan だが、A の snapshot には載っていない
          (A の開始後に作られた plan)。
    検証: Ralph Loop が block する。上のテストの非 block が早期 return による
          見かけの成功ではないことの対照。
    """
    plan_dir, state = isolated
    (plan_dir / "2026-10-21-new.md").write_text("- [ ] T0\n")
    (state / "active-plans-snapshot-sessA.json").write_text(json.dumps({"plans": {}}))

    out = _run_stop(monkeypatch, capsys, "sessA")

    assert "[Ralph Loop]" in json.loads(out)["reason"]


def test_ralph_count_is_written_per_session_and_survives_other_sessions_stop(
    monkeypatch, capsys, isolated, tmp_path
):
    """
    前提: session A には未完了 plan があり (snapshot 不在 = 全 plan relevant)。
    事前: A の Stop を 1 回走らせた後、plan の無い repo の session B の Stop が走る。
    検証: カウンタは A 専用ファイルに 1 として残り、共有ファイルは作られない。
    """
    plan_dir, _ = isolated
    plan = plan_dir / "2026-10-21-new.md"
    plan.write_text("- [ ] T0\n")
    _run_stop(monkeypatch, capsys, "sessA")

    plan.unlink()
    _run_stop(monkeypatch, capsys, "sessB")

    assert (tmp_path / "ralph-iterations-sessA").read_text() == "1"
    assert not (tmp_path / "ralph-iterations").exists()


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
@pytest.mark.parametrize(
    ("session_id", "expected"),
    [
        ("t-123", "active-plans-snapshot-t-123.json"),
        ("../x", "active-plans-snapshot.json"),
        (None, "active-plans-snapshot.json"),
    ],
)
def test_session_load_writes_the_snapshot_name_the_gate_reads(
    tmp_path, session_id, expected
):
    """
    前提: snapshot の書き手は session-load.js、読み手は completion-gate.py で、
          ファイル名規則は両側に別々に書かれている。
    検証: session-load.js が書くファイル名が、gate の _session_scoped と一致する。
    """
    proc = subprocess.run(
        ["node", str(SCRIPTS / "runtime" / "session-load.js")],
        input=json.dumps({"session_id": session_id}),
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env={**os.environ, "HOME": str(tmp_path)},
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr

    written = sorted(
        p.name
        for p in (tmp_path / ".claude" / "session-state").glob("active-plans-snapshot*")
    )
    gate_name = os.path.basename(
        gate._session_scoped("active-plans-snapshot.json", session_id or "")
    )
    assert written == [expected] == [gate_name]
