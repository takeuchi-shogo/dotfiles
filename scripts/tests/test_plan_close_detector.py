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


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
