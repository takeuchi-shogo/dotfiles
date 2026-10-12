"""Tests for cccc-complexity-gate.py."""

from __future__ import annotations

import json
import os
import stat
import sys
from importlib import import_module
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "policy"))

gate = import_module("cccc-complexity-gate")


def _write_fake_cccc(tmp_path: Path, *, exit_code: int, payload: dict) -> Path:
    """Create a tiny stub `cccc` that prints JSON and exits with exit_code."""
    script = tmp_path / "fake-cccc"
    body = {
        "exit_code": exit_code,
        "payload": payload,
    }
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        f"data = json.loads({json.dumps(json.dumps(body))})\n"
        "json.dump(data['payload'], sys.stdout)\n"
        "sys.exit(int(data['exit_code']))\n",
        encoding="utf-8",
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    return script


def test_is_skippable_filters_tests_and_unknown():
    assert gate._is_skippable("foo/bar_test.go") is True
    assert gate._is_skippable("src/foo.test.ts") is True
    assert gate._is_skippable("docs/readme.md") is True
    assert gate._is_skippable("src/main.py") is False


def test_get_changed_files_includes_untracked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
):
    """Untracked sources must be gated (agents often leave them unstaged)."""
    calls: list[tuple[str, ...]] = []

    def fake_check_output(args, **_kwargs):  # type: ignore[no-untyped-def]
        cmd = tuple(args)
        calls.append(cmd)
        if cmd[:3] == ("git", "diff", "--name-only"):
            return "tracked.py\n"
        if cmd[:2] == ("git", "ls-files"):
            return "brand_new.py\n"
        return ""

    monkeypatch.setattr(gate.subprocess, "check_output", fake_check_output)
    got = gate._get_changed_files()
    assert "tracked.py" in got
    assert "brand_new.py" in got
    assert any(c[:2] == ("git", "ls-files") for c in calls)


def test_resolve_thresholds_reads_cccc_toml(tmp_path: Path):
    (tmp_path / "cccc.toml").write_text(
        "max-cognitive = 12\nmax-cyclomatic = 9\n",
        encoding="utf-8",
    )
    cog, cyc, args = gate._resolve_thresholds(str(tmp_path))
    assert cog == 12
    assert cyc == 9
    assert args[0] == "--config"
    assert args[1].endswith("cccc.toml")


def test_resolve_thresholds_defaults_without_config(tmp_path: Path):
    cog, cyc, args = gate._resolve_thresholds(str(tmp_path))
    assert cog == gate.DEFAULT_MAX_COGNITIVE
    assert cyc == gate.DEFAULT_MAX_CYCLOMATIC
    assert "--no-config" in args


def test_collect_offenders_filters_by_threshold():
    report = {
        "files": [
            {
                "path": "a.py",
                "functions": [
                    {"name": "ok", "line": 1, "cognitive": 1, "cyclomatic": 1},
                    {
                        "name": "bad",
                        "line": 10,
                        "cognitive": 50,
                        "cyclomatic": 2,
                    },
                ],
            }
        ]
    }
    lines = gate._collect_offenders(report, 40, 40)
    assert len(lines) == 1
    assert "bad" in lines[0]
    assert "cognitive=50" in lines[0]


def test_main_skips_when_cccc_missing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
):
    monkeypatch.delenv("CCCC_GATE_DISABLE", raising=False)
    monkeypatch.delenv("CCCC_BIN", raising=False)
    monkeypatch.setattr(gate.shutil, "which", lambda _name: None)
    gate.main()
    err = capsys.readouterr().err
    assert "skip: cccc not found" in err
    assert capsys.readouterr().out == ""


def test_main_skips_when_disabled(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CCCC_GATE_DISABLE", "1")
    called = {"find": False}

    def _boom() -> str | None:
        called["find"] = True
        return None

    monkeypatch.setattr(gate, "_find_cccc", _boom)
    gate.main()
    assert called["find"] is False


def test_main_blocks_on_threshold(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    src = tmp_path / "hot.py"
    src.write_text("def hot():\n    return 1\n", encoding="utf-8")
    fake = _write_fake_cccc(
        tmp_path,
        exit_code=1,
        payload={
            "files": [
                {
                    "path": "hot.py",
                    "functions": [
                        {
                            "name": "hot",
                            "line": 1,
                            "cognitive": 99,
                            "cyclomatic": 3,
                        }
                    ],
                }
            ],
            "summary": {
                "cognitive": {"max": 99},
                "cyclomatic": {"max": 3},
            },
        },
    )
    monkeypatch.delenv("CCCC_GATE_DISABLE", raising=False)
    monkeypatch.setenv("CCCC_BIN", str(fake))
    monkeypatch.setattr(gate, "_repo_root", lambda: str(tmp_path))
    monkeypatch.setattr(gate, "_get_changed_files", lambda: ["hot.py"])

    gate.main()
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["decision"] == "block"
    assert "hot" in data["reason"]
    assert "cognitive=99" in data["reason"]


def test_main_passes_quietly(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    src = tmp_path / "ok.py"
    src.write_text("def ok():\n    return 1\n", encoding="utf-8")
    fake = _write_fake_cccc(
        tmp_path,
        exit_code=0,
        payload={"files": [], "summary": {}},
    )
    monkeypatch.delenv("CCCC_GATE_DISABLE", raising=False)
    monkeypatch.setenv("CCCC_BIN", str(fake))
    monkeypatch.setattr(gate, "_repo_root", lambda: str(tmp_path))
    monkeypatch.setattr(gate, "_get_changed_files", lambda: ["ok.py"])

    gate.main()
    assert capsys.readouterr().out == ""
