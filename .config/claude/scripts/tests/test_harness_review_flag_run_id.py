"""harness_review_flag.py write は PASS の review-metrics 記録を要求する。

背景: /review の結果保存が 8 回中 0 回しか行われなかった。フラグ書き出しを
Run Metrics 記録 (verdict=PASS, run_id 一致) に依存させて、保存漏れを止める。
前提: tmp の git repo に未 commit の harness 変更があり、AUTOEVOLVE_DATA_DIR は tmp。
"""

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
HARNESS = "scripts/policy/x.py"


def _git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


@pytest.fixture
def lib(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    (repo / "scripts/policy").mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    (repo / HARNESS).write_text("v1\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "init")
    (repo / HARNESS).write_text("v2\n")
    monkeypatch.chdir(repo)
    monkeypatch.setenv("CLAUDE_SESSION_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("AUTOEVOLVE_DATA_DIR", str(tmp_path / "data"))
    spec = importlib.util.spec_from_file_location(
        "hrf_rid", SCRIPTS / "lib/harness_review_flag.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _metrics(tmp_path, entries):
    d = tmp_path / "data" / "learnings"
    d.mkdir(parents=True)
    (d / "review-metrics.jsonl").write_text(
        "".join(json.dumps(e) + "\n" for e in entries)
    )


def _run(lib, monkeypatch, *args):
    monkeypatch.setattr("sys.argv", ["x", "write", *args])
    try:
        lib.main()
    except SystemExit as e:
        return e.code
    return 0


def test_write_succeeds_with_pass_metrics(lib, tmp_path, monkeypatch):
    """前提: run_id=rv-1 の PASS 記録が現在の内容の fingerprint を持つ。
    検証: exit 0 で check が True。
    """
    fp = lib.fingerprint(lib.get_changed_harness_files())
    _metrics(
        tmp_path, [{"run_id": "rv-1", "verdict": "PASS", "harness_fingerprint": fp}]
    )
    assert _run(lib, monkeypatch, "--run-id", "rv-1") == 0
    assert lib.check_flag() is True


def test_write_with_stale_fingerprint_fails(lib, tmp_path, monkeypatch):
    """前提: rv-1 の PASS は v2 の内容に対するもので、その後ハーネスを v3 に編集した。
    検証: 過去の PASS の run_id を使い回しても exit 1 でフラグは書かれない。
    """
    fp = lib.fingerprint(lib.get_changed_harness_files())
    _metrics(
        tmp_path, [{"run_id": "rv-1", "verdict": "PASS", "harness_fingerprint": fp}]
    )
    (tmp_path / "repo" / HARNESS).write_text("v3\n")
    assert _run(lib, monkeypatch, "--run-id", "rv-1") == 1
    assert lib.check_flag() is False


def test_write_without_run_id_fails(lib, tmp_path, monkeypatch, capsys):
    """前提: PASS 記録はある。検証: --run-id 無しは exit 1、フラグは書かれない。"""
    _metrics(tmp_path, [{"run_id": "rv-1", "verdict": "PASS"}])
    assert _run(lib, monkeypatch) == 1
    assert "--run-id" in capsys.readouterr().err
    assert lib.check_flag() is False


def test_write_unknown_run_id_fails(lib, tmp_path, monkeypatch, capsys):
    """検証: 記録に無い run_id は exit 1。run_id と emit_review_metrics を案内する。"""
    _metrics(tmp_path, [{"run_id": "rv-1", "verdict": "PASS"}])
    assert _run(lib, monkeypatch, "--run-id", "rv-9") == 1
    err = capsys.readouterr().err
    assert "rv-9" in err and "emit_review_metrics" in err
    assert lib.check_flag() is False


def test_write_non_pass_verdict_fails(lib, tmp_path, monkeypatch):
    """検証: run_id が一致しても verdict が PASS 以外なら exit 1。"""
    _metrics(tmp_path, [{"run_id": "rv-1", "verdict": "NEEDS_HUMAN_REVIEW"}])
    assert _run(lib, monkeypatch, "--run-id", "rv-1") == 1
    assert lib.check_flag() is False


def test_write_metrics_file_absent_fails(lib, monkeypatch):
    """前提: review-metrics.jsonl が存在しない。検証: exit 1。"""
    assert _run(lib, monkeypatch, "--run-id", "rv-1") == 1


def test_write_metrics_file_unreadable_fails(lib, tmp_path, monkeypatch):
    """前提: PASS 記録はあるが review-metrics.jsonl が読めない (PermissionError)。
    検証: exit 1 でフラグも作られない (読めないものを PASS 扱いしない)。
    """
    _metrics(tmp_path, [{"run_id": "rv-1", "verdict": "PASS"}])

    def deny(*args, **kwargs):
        raise PermissionError("denied")

    monkeypatch.setattr(Path, "read_text", deny)
    assert _run(lib, monkeypatch, "--run-id", "rv-1") == 1
    monkeypatch.undo()
    monkeypatch.chdir(tmp_path / "repo")
    monkeypatch.setenv("CLAUDE_SESSION_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("AUTOEVOLVE_DATA_DIR", str(tmp_path / "data"))
    assert lib.check_flag() is False


def test_flag_is_written_for_the_verified_content_only(lib, tmp_path, monkeypatch):
    """前提: 照合 (v2 の PASS) の直後、書き込み前にハーネスが v3 に編集される。
    検証: 書かれるのは照合した v2 のフラグで、v3 の check は False のまま。
    """
    fp = lib.fingerprint(lib.get_changed_harness_files())
    _metrics(
        tmp_path, [{"run_id": "rv-1", "verdict": "PASS", "harness_fingerprint": fp}]
    )
    real = lib.has_pass_metrics

    def verify_then_edit(run_id, verified_fp):
        ok = real(run_id, verified_fp)
        (tmp_path / "repo" / HARNESS).write_text("v3\n")
        return ok

    monkeypatch.setattr(lib, "has_pass_metrics", verify_then_edit)
    assert _run(lib, monkeypatch, "--run-id", "rv-1") == 0
    assert lib.check_flag() is False
