"""Harness Review Gate の session-aware filter が実際に効くことの回帰テスト.

配線バグ: `_get_session_initial_harness()` は `CLAUDE_SESSION_ID` env だけを見ていたが、
hook 実行環境にその env は無い (常に None)。snapshot は harness-snapshot.py が
毎セッション書いていたのに読む側が存在せず、filter は一度も動いていなかった。
session_id は hook の stdin payload から来るので、引数で受け取れることを固定する。
"""

import importlib.util
import io
import json
import sys
from pathlib import Path

SPEC = Path(__file__).resolve().parent.parent / "policy" / "completion-gate.py"


def _load():
    spec = importlib.util.spec_from_file_location("completion_gate", SPEC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_snapshot(home: Path, sid: str, files: list[str]) -> None:
    d = home / ".claude" / "session-state"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"initial-harness-{sid}.txt").write_text("\n".join(files) + "\n")


def test_snapshot_read_via_session_id_argument(tmp_path, monkeypatch):
    _write_snapshot(tmp_path, "sid-1", ["CLAUDE.md"])
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("CLAUDE_SESSION_ID", raising=False)
    assert _load()._get_session_initial_harness("sid-1") == {"CLAUDE.md"}


def test_no_session_id_yields_empty_set(tmp_path, monkeypatch):
    """env も引数も無ければ空集合 (back-compat: filter を素通り)。"""
    _write_snapshot(tmp_path, "sid-1", ["CLAUDE.md"])
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("CLAUDE_SESSION_ID", raising=False)
    assert _load()._get_session_initial_harness() == set()


def test_env_still_works_as_fallback(tmp_path, monkeypatch):
    _write_snapshot(tmp_path, "sid-env", ["CLAUDE.md"])
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("CLAUDE_SESSION_ID", "sid-env")
    assert _load()._get_session_initial_harness() == {"CLAUDE.md"}


def test_session_id_is_basenamed(tmp_path, monkeypatch):
    """snapshot パスは session_id で組み立てるので path traversal を持ち込ませない。"""
    _write_snapshot(tmp_path, "sid-1", ["CLAUDE.md"])
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("CLAUDE_SESSION_ID", raising=False)
    assert _load()._get_session_initial_harness("../../etc/sid-1") == {"CLAUDE.md"}


def test_env_fallback_is_also_basenamed(tmp_path, monkeypatch):
    """引数が空のとき使う env 側も正規化する (env は信頼できる前提を置かない)。"""
    _write_snapshot(tmp_path, "sid-1", ["CLAUDE.md"])
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("CLAUDE_SESSION_ID", "../../etc/sid-1")
    assert _load()._get_session_initial_harness() == {"CLAUDE.md"}


def test_dot_session_id_rejected(tmp_path, monkeypatch):
    """basename が "." / ".." に潰れる入力はディレクトリを指すので拒否する。"""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("CLAUDE_SESSION_ID", raising=False)
    mod = _load()
    assert mod._get_session_initial_harness("..") == set()
    assert mod._get_session_initial_harness("some/dir/") == set()


def test_preexisting_changes_excluded_but_new_ones_kept(tmp_path, monkeypatch):
    """セッション開始時からの変更は落とし、開始後の変更は残す。"""
    _write_snapshot(tmp_path, "sid-1", ["CLAUDE.md"])
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("CLAUDE_SESSION_ID", raising=False)
    mod = _load()

    class _Result:
        returncode = 0
        stdout = "CLAUDE.md\n.config/claude/settings.json\nREADME.md\n"

    monkeypatch.setattr(mod.subprocess, "run", lambda *a, **k: _Result())

    assert mod._get_changed_harness_files("sid-1") == [".config/claude/settings.json"]
    # 引数なしでは filter が効かず、開始時からの CLAUDE.md まで残る (バグ再現)
    assert "CLAUDE.md" in mod._get_changed_harness_files()


def _run_main(mod, monkeypatch, payload, seen):
    """main() を stdin payload つきで走らせ、gate に届いた session_id を捕まえる。"""

    def _gate(session_id: str = ""):
        seen["session_id"] = session_id
        return None

    monkeypatch.setattr(mod, "_check_harness_review_gate", _gate)
    monkeypatch.setattr(mod, "_find_incomplete_plan", lambda: None)
    monkeypatch.setattr(mod, "_detect_test_command", lambda: None)
    monkeypatch.setattr(mod, "_get_retry_count", lambda: 0)
    monkeypatch.setattr(mod, "_reset_ralph", lambda: None)
    monkeypatch.setattr(mod, "_reset_retries", lambda: None)
    monkeypatch.setattr(mod, "_check_fabricated_claims", lambda _d: None)
    monkeypatch.delenv("CLAUDE_SKIP_TEST_GATE", raising=False)
    monkeypatch.setattr(sys, "stdin", io.StringIO(payload))
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False, raising=False)
    mod.main()


def test_main_wires_stdin_session_id_into_the_gate(monkeypatch):
    """配線の回帰: main() の呼び出しで引数を落とすとこのテストが落ちる。"""
    seen: dict = {}
    mod = _load()
    _run_main(mod, monkeypatch, json.dumps({"session_id": "sid-from-stdin"}), seen)
    assert seen["session_id"] == "sid-from-stdin"


def test_main_survives_non_object_stdin_json(monkeypatch):
    """valid JSON でも object でなければ .get は無い。落とさず素通りさせる。"""
    seen: dict = {}
    mod = _load()
    _run_main(mod, monkeypatch, "null", seen)
    assert seen["session_id"] == ""
