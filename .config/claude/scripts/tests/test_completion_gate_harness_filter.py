"""Harness Review Gate の session-aware filter が実際に効くことの回帰テスト.

配線バグ: `_get_session_initial_harness()` は `CLAUDE_SESSION_ID` env だけを見ていたが、
hook 実行環境にその env は無い (常に None)。snapshot は harness-snapshot.py が
毎セッション書いていたのに読む側が存在せず、filter は一度も動いていなかった。
session_id は hook の stdin payload から来るので、引数で受け取れることを固定する。
"""

import importlib.util
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
