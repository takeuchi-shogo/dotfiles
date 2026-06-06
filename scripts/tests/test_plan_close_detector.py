"""plan-close-detector の純ロジック検証。

実行: uv run pytest scripts/tests/test_plan_close_detector.py
"""

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lifecycle"))

pcd = importlib.import_module("plan-close-detector")


def _write(tmp_path, name, body):
    f = tmp_path / name
    f.write_text(body, encoding="utf-8")
    return f


def test_extract_signals_reads_lifecycle_artifacts_asserts(tmp_path):
    body = (
        "---\n"
        "lifecycle: active\n"
        'artifacts: "a.py, b.sh"\n'
        'asserts: "plan-close-tests"\n'
        "---\n\n"
        "- [x] done\n"
        "- [ ] todo\n"
    )
    f = _write(tmp_path, "p.md", body)
    sig = pcd.extract_signals(f)
    assert sig.lifecycle == "active"
    assert sig.artifacts == '"a.py, b.sh"'
    assert sig.asserts == '"plan-close-tests"'
    assert sig.checkboxes_total == 2
    assert sig.checkboxes_done == 1


def test_extract_signals_falls_back_to_status(tmp_path):
    # 既存 plan は status: のみ。lifecycle 欠落時は status を後方互換で読む。
    f = _write(tmp_path, "old.md", "---\nstatus: completed\n---\n# old\n")
    assert pcd.extract_signals(f).lifecycle == "completed"


def test_artifacts_present_all_exist(tmp_path, monkeypatch):
    (tmp_path / "a.py").write_text("x")
    (tmp_path / "b.sh").write_text("y")
    monkeypatch.setattr(pcd, "REPO_ROOT", tmp_path)
    assert pcd.artifacts_present('"a.py, b.sh"') is True


def test_artifacts_present_missing_one(tmp_path, monkeypatch):
    (tmp_path / "a.py").write_text("x")
    monkeypatch.setattr(pcd, "REPO_ROOT", tmp_path)
    assert pcd.artifacts_present("a.py, b.sh") is False


def test_asserts_satisfied_allowlisted(monkeypatch):
    monkeypatch.setattr(pcd, "ASSERTS", {"ok": ["true"], "ng": ["false"]})
    assert pcd.asserts_satisfied("ok") is True
    assert pcd.asserts_satisfied("ok, ng") is False


def test_asserts_satisfied_rejects_non_allowlisted(monkeypatch):
    monkeypatch.setattr(pcd, "ASSERTS", {"ok": ["true"]})
    assert pcd.asserts_satisfied("rm -rf /") is False
    assert pcd.asserts_satisfied("! task validate-configs") is False


def test_classify_misplaced():
    s = pcd.Signals(
        path=Path("docs/plans/active/x.md"),
        lifecycle="completed",
        artifacts=None,
        asserts=None,
        checkboxes_total=0,
        checkboxes_done=0,
    )
    v = pcd.classify(s, stale_days=5, tree_clean=True)
    assert v.result == "MISPLACED" and v.tier == 1


def test_classify_verified_done_requires_assert_and_clean_tree(monkeypatch):
    monkeypatch.setattr(pcd, "ASSERTS", {"ok": ["true"]})
    s = pcd.Signals(
        path=Path("x.md"),
        lifecycle="active",
        artifacts=None,
        asserts="ok",
        checkboxes_total=3,
        checkboxes_done=0,
    )
    assert pcd.classify(s, stale_days=1, tree_clean=True).result == "VERIFIED_DONE"
    assert pcd.classify(s, stale_days=1, tree_clean=False).result == "HEALTHY"


def test_classify_artifacts_present_is_tier2(monkeypatch, tmp_path):
    (tmp_path / "a.py").write_text("x")
    monkeypatch.setattr(pcd, "REPO_ROOT", tmp_path)
    s = pcd.Signals(
        path=Path("x.md"),
        lifecycle="active",
        artifacts="a.py",
        asserts=None,
        checkboxes_total=3,
        checkboxes_done=0,
    )
    v = pcd.classify(s, stale_days=1, tree_clean=True)
    assert v.result == "ARTIFACTS_PRESENT" and v.tier == 2


def test_classify_likely_done_is_tier2():
    s = pcd.Signals(
        path=Path("x.md"),
        lifecycle="active",
        artifacts=None,
        asserts=None,
        checkboxes_total=4,
        checkboxes_done=4,
    )
    v = pcd.classify(s, stale_days=40, tree_clean=True)
    assert v.result == "LIKELY_DONE" and v.tier == 2


def test_classify_healthy_recent():
    s = pcd.Signals(
        path=Path("x.md"),
        lifecycle="active",
        artifacts=None,
        asserts=None,
        checkboxes_total=4,
        checkboxes_done=1,
    )
    assert pcd.classify(s, stale_days=3, tree_clean=True).result == "HEALTHY"


def test_git_stale_days_handles_untracked(tmp_path, monkeypatch):
    monkeypatch.setattr(pcd, "REPO_ROOT", tmp_path)
    f = tmp_path / "x.md"
    f.write_text("---\nstatus: active\n---\n")
    assert pcd.git_stale_days(f) >= 0


def test_artifacts_present_rejects_path_traversal(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (tmp_path / "secret.txt").write_text("x")
    monkeypatch.setattr(pcd, "REPO_ROOT", repo)
    assert pcd.artifacts_present("../secret.txt") is False
    (repo / "ok.py").write_text("y")
    assert pcd.artifacts_present("ok.py") is True


def test_classify_none_lifecycle_stale_is_reported():
    s = pcd.Signals(
        path=Path("x.md"),
        lifecycle=None,
        artifacts=None,
        asserts=None,
        checkboxes_total=0,
        checkboxes_done=0,
    )
    assert pcd.classify(s, stale_days=40, tree_clean=True).result == "STALE"
    assert pcd.classify(s, stale_days=3, tree_clean=True).result == "HEALTHY"


def test_plan_moves_misplaced_to_correct_dir(tmp_path, monkeypatch):
    active = tmp_path / "docs/plans/active"
    active.mkdir(parents=True)
    (active / "x.md").write_text("---\nlifecycle: deferred\n---\n# x\n")
    monkeypatch.setattr(pcd, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(pcd, "ACTIVE_DIR", active)
    moves = pcd.plan_moves()
    assert any(
        m["to"].endswith("paused/x.md") and m["result"] == "MISPLACED" for m in moves
    )


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
