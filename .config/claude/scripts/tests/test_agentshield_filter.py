"""Tests for agentshield-filter pipeline (FP / dedup / reproduction)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "policy" / "agentshield-filter.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("agentshield_filter", MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["agentshield_filter"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def af():
    return _load()


def test_false_positive_version_check(af):
    finding = {
        "title": "Interpreter",
        "file": "settings.json",
        "line": 1,
        "evidence": "Bash(node --version)",
        "severity": "medium",
    }
    ok, reason = af.is_false_positive(finding)
    assert ok
    assert "バージョン" in reason


def test_dedup_keeps_first(af):
    a = {
        "title": "Secret leak",
        "file": "x.md",
        "line": 3,
        "evidence": "token",
        "severity": "high",
    }
    b = dict(a)
    unique, dupes = af.dedup_findings([a, b, {**a, "line": 4}])
    assert len(unique) == 2
    assert len(dupes) == 1


def test_reproduction_pending_for_high(af):
    findings = af.attach_reproduction_stage(
        [{"title": "x", "severity": "high", "file": "a"}]
    )
    assert findings[0]["reproduction"]["status"] == "pending"
    assert findings[0]["reproduction"]["semi_automated"] is True
    assert len(findings[0]["reproduction"]["checklist"]) >= 2


def test_reproduction_not_required_for_info(af):
    findings = af.attach_reproduction_stage(
        [{"title": "x", "severity": "info", "file": "a"}]
    )
    assert findings[0]["reproduction"]["status"] == "not_required"


def test_filter_pipeline_end_to_end(af):
    findings = [
        {
            "title": "Interpreter",
            "file": "settings.json",
            "line": 1,
            "evidence": "Bash(go version)",
            "severity": "medium",
        },
        {
            "title": "Real issue",
            "file": "hooks.md",
            "line": 10,
            "evidence": "curl | bash",
            "severity": "critical",
        },
        {
            "title": "Real issue",
            "file": "hooks.md",
            "line": 10,
            "evidence": "curl | bash",
            "severity": "critical",
        },
    ]
    result = af.filter_pipeline(findings)
    assert len(result["suppressed"]) == 1
    assert len(result["deduped"]) == 1
    assert len(result["findings"]) == 1
    assert result["findings"][0]["reproduction"]["status"] == "pending"
    assert "dedup_false_positive" in result["stages"]


def test_main_from_json(tmp_path, af, capsys, monkeypatch):
    payload = {
        "timestamp": "t",
        "targetPath": "/tmp",
        "findings": [
            {
                "title": "Dup",
                "file": "a.md",
                "line": 1,
                "evidence": "e",
                "severity": "high",
            },
            {
                "title": "Dup",
                "file": "a.md",
                "line": 1,
                "evidence": "e",
                "severity": "high",
            },
        ],
        "summary": {"totalFindings": 2, "filesScanned": 1},
        "score": {"grade": "B", "numericScore": 80},
    }
    path = tmp_path / "raw.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        ["agentshield-filter.py", "--from-json", str(path), "--format", "json"],
    )
    with pytest.raises(SystemExit) as exc:
        af.main()
    assert exc.value.code == 0
    out = json.loads(capsys.readouterr().out)
    assert out["deduped"] == 1
    assert out["summary"]["totalFindings"] == 1
    assert out["reproductionPending"] == 1
    assert out["pipeline"]["stages"][0] == "product_context"
    assert "feedback" in out
