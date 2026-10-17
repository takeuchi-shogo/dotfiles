"""Harness review PASS flag は「レビューした内容」に束縛されること。

旧実装は変更ファイル名の集合だけを鍵にしていたため、PASS 後に同じファイルを
編集してもフラグが有効なまま (false green) だった。
前提: tmp の git repo に scripts/policy/x.py を commit 済みで、未 commit の編集がある。
検証: write 後の編集・untracked 追加・binary 変更・git 失敗で check が False。
"""

import importlib.util
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
HARNESS = "scripts/policy/x.py"


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


@pytest.fixture
def env(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    (repo / "scripts/policy").mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    (repo / HARNESS).write_text("v1\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "init")
    (repo / HARNESS).write_text("v2\n")  # uncommitted harness change
    monkeypatch.chdir(repo)
    monkeypatch.setenv("CLAUDE_SESSION_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("CLAUDE_SESSION_ID", raising=False)
    return repo, _load("hrf", "lib/harness_review_flag.py")


def test_write_then_check_passes(env):
    _, lib = env
    assert lib.check_flag() is False
    assert lib.write_flag() is True
    assert lib.check_flag() is True


def test_edit_after_write_invalidates_flag(env):
    repo, lib = env
    lib.write_flag()
    (repo / HARNESS).write_text("v3 edited after review\n")
    assert lib.check_flag() is False  # 旧実装 (ファイル名集合の md5) では True だった


def test_untracked_marker_file_after_write_invalidates_flag(env):
    repo, lib = env
    lib.write_flag()
    (repo / "scripts/policy/new.py").write_text("x\n")
    assert lib.check_flag() is False


def test_untracked_content_edit_invalidates_flag(env):
    repo, lib = env
    (repo / "scripts/policy/new.py").write_text("a\n")
    lib.write_flag()
    assert lib.check_flag() is True
    (repo / "scripts/policy/new.py").write_text("b\n")
    assert lib.check_flag() is False


def test_binary_change_detected(env):
    repo, lib = env
    (repo / HARNESS).write_bytes(bytes([0, 1, 2]))
    lib.write_flag()
    (repo / HARNESS).write_bytes(bytes([0, 1, 3]))
    assert lib.check_flag() is False


def test_fingerprint_failure_blocks_and_write_exits_nonzero(env, monkeypatch, capsys):
    _, lib = env
    lib.write_flag()

    def boom(*a, **k):
        raise subprocess.TimeoutExpired("git", 1)

    monkeypatch.setattr(lib, "_git", boom)
    assert lib.check_flag() is False
    monkeypatch.setattr("sys.argv", ["x", "write"])
    with pytest.raises(SystemExit) as e:
        lib.main()
    assert e.value.code == 1
    assert "write failed" in capsys.readouterr().err


def test_gate_and_lib_agree(env):
    repo, lib = env
    gate = _load("completion_gate", "policy/completion-gate.py")
    assert gate._check_harness_review_gate("sid") is not None
    lib.write_flag()
    assert gate._check_harness_review_gate("sid") is None
    (repo / HARNESS).write_text("edited again\n")
    assert gate._check_harness_review_gate("sid") is not None


def test_gate_blocks_when_flag_lib_cannot_load(tmp_path):
    """前提: policy/completion-gate.py の隣の lib/harness_review_flag.py が構文エラー。
    検証: import は落ちず、harness gate が lib の読み込み失敗を理由に block する。
    """
    (tmp_path / "policy").mkdir()
    (tmp_path / "lib").mkdir()
    gate_src = SCRIPTS / "policy" / "completion-gate.py"
    (tmp_path / "policy" / "completion-gate.py").write_text(gate_src.read_text())
    (tmp_path / "lib" / "harness_review_flag.py").write_text("def broken(:\n")
    spec = importlib.util.spec_from_file_location(
        "gate_broken_lib", tmp_path / "policy" / "completion-gate.py"
    )
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    result = gate._check_harness_review_gate()
    assert result is not None and result["decision"] == "block"
    assert "SyntaxError" in result["reason"]


def test_flag_lib_itself_is_a_harness_file():
    """前提: gate の実装は lib/harness_review_flag.py に一本化されている。
    検証: このファイルだけの変更でも gate の対象になる (自分自身を素通りさせない)。
    """
    flag = _load("hrf_marker", "lib/harness_review_flag.py")
    assert flag._has_marker(".config/claude/scripts/lib/harness_review_flag.py")
