"""Tests for cccc-complexity-gate.py."""

from __future__ import annotations

import json
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
    body = {"exit_code": exit_code, "payload": payload}
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


def test_is_test_path_does_not_match_latest_price():
    assert gate._is_test_path("src/latest_price.py") is False
    assert gate._is_test_path("pkg/contest_runner.py") is False
    assert gate._is_test_path("tests/test_foo.py") is True
    assert gate._is_test_path("foo/test_helper.py") is True
    assert gate._is_test_path("foo/bar_test.go") is True
    assert gate._is_test_path("src/foo.test.ts") is True


def test_is_skippable_filters_tests_and_unknown():
    assert gate._is_skippable("foo/bar_test.go") is True
    assert gate._is_skippable("src/foo.test.ts") is True
    assert gate._is_skippable("docs/readme.md") is True
    assert gate._is_skippable("src/main.py") is False
    assert gate._is_skippable("src/latest_price.py") is False


def test_get_dirty_files_includes_untracked(monkeypatch: pytest.MonkeyPatch):
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
    got = gate._get_dirty_files()
    assert "tracked.py" in got
    assert "brand_new.py" in got


def test_resolve_thresholds_reads_cccc_toml(tmp_path: Path):
    (tmp_path / "cccc.toml").write_text(
        "max-cognitive = 12\nmax-cyclomatic = 9\n",
        encoding="utf-8",
    )
    cog, cyc, args = gate._resolve_thresholds(str(tmp_path))
    assert cog == 12
    assert cyc == 9
    assert args[0] == "--config"
    assert "--max-cognitive=1000000" in args


def test_resolve_thresholds_reads_dot_cccc_toml(tmp_path: Path):
    (tmp_path / ".cccc.toml").write_text(
        "max-cognitive = 7\nmax-cyclomatic = 8\n",
        encoding="utf-8",
    )
    cog, cyc, args = gate._resolve_thresholds(str(tmp_path))
    assert cog == 7
    assert cyc == 8
    assert args[1].endswith(".cccc.toml")


def test_resolve_thresholds_defaults_without_config(tmp_path: Path):
    cog, cyc, args = gate._resolve_thresholds(str(tmp_path))
    assert cog == gate.DEFAULT_MAX_COGNITIVE
    assert cyc == gate.DEFAULT_MAX_CYCLOMATIC
    assert "--no-config" in args


def test_parse_hunk_lines():
    diff = (
        "@@ -1,2 +10,3 @@\n"
        "+a\n+b\n+c\n"
        "@@ -5 +20,0 @@\n"
        "-deleted\n"
    )
    assert gate._parse_hunk_lines(diff) == {10, 11, 12}


def test_functions_touching_filters_unchanged():
    functions = [
        {"name": "old", "line": 1, "cognitive": 99, "cyclomatic": 50},
        {"name": "edited", "line": 40, "cognitive": 50, "cyclomatic": 2},
        {"name": "later", "line": 80, "cognitive": 60, "cyclomatic": 2},
    ]
    touching = gate._functions_touching(functions, {42})
    assert [f["name"] for f in touching] == ["edited"]


def test_collect_offenders_only_changed_functions():
    report = {
        "files": [
            {
                "path": "a.py",
                "functions": [
                    {"name": "untouched", "line": 1, "cognitive": 99, "cyclomatic": 50},
                    {"name": "touched", "line": 50, "cognitive": 55, "cyclomatic": 2},
                ],
            }
        ]
    }
    lines = gate._collect_offenders(report, 40, 40, {"a.py": {50, 51}})
    assert len(lines) == 1
    assert "touched" in lines[0]


def test_main_skips_when_cccc_missing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
):
    monkeypatch.delenv("CCCC_GATE_DISABLE", raising=False)
    monkeypatch.delenv("CCCC_BIN", raising=False)
    monkeypatch.setattr(gate.shutil, "which", lambda _name: None)
    monkeypatch.setattr(sys, "argv", ["cccc-complexity-gate.py"])
    gate.main()
    captured = capsys.readouterr()
    assert "skip: cccc not found" in captured.err
    assert captured.out == ""


def test_main_skips_when_disabled(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CCCC_GATE_DISABLE", "1")
    called = {"find": False}

    def _boom() -> str | None:
        called["find"] = True
        return None

    monkeypatch.setattr(gate, "_find_cccc", _boom)
    monkeypatch.setattr(sys, "argv", ["cccc-complexity-gate.py"])
    gate.main()
    assert called["find"] is False


def test_main_blocks_on_changed_function(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    src = tmp_path / "hot.py"
    src.write_text("def hot():\n    return 1\n", encoding="utf-8")
    fake = _write_fake_cccc(
        tmp_path,
        exit_code=0,
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
            "summary": {},
        },
    )
    monkeypatch.delenv("CCCC_GATE_DISABLE", raising=False)
    monkeypatch.setenv("CCCC_BIN", str(fake))
    monkeypatch.setattr(gate, "_repo_root", lambda: str(tmp_path))
    monkeypatch.setattr(gate, "_select_targets", lambda _r: (["hot.py"], None, None))
    monkeypatch.setattr(
        gate,
        "_changed_lines_map",
        lambda *_a, **_k: {"hot.py": None},
    )
    monkeypatch.setattr(gate, "_get_retry_count", lambda: 0)
    monkeypatch.setattr(gate, "_set_retry_count", lambda _n: None)
    monkeypatch.setattr(sys, "argv", ["cccc-complexity-gate.py"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    gate.main()
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["decision"] == "block"
    assert "hot" in data["reason"]
    assert "cognitive=99" in data["reason"]


def test_main_soft_fail_no_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    src = tmp_path / "x.py"
    src.write_text("def x():\n    return 1\n", encoding="utf-8")
    bad = tmp_path / "bad-cccc"
    bad.write_text(
        "#!/usr/bin/env python3\nimport sys\nprint('not-json')\nsys.exit(2)\n",
        encoding="utf-8",
    )
    bad.chmod(bad.stat().st_mode | stat.S_IEXEC)
    monkeypatch.delenv("CCCC_GATE_DISABLE", raising=False)
    monkeypatch.setenv("CCCC_BIN", str(bad))
    monkeypatch.setattr(gate, "_repo_root", lambda: str(tmp_path))
    monkeypatch.setattr(gate, "_select_targets", lambda _r: (["x.py"], None, None))
    monkeypatch.setattr(sys, "argv", ["cccc-complexity-gate.py"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    gate.main()
    captured = capsys.readouterr()
    assert "soft-fail" in captured.err
    assert captured.out == ""


def test_truncation_reported(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    paths = [f"f{i}.py" for i in range(gate.MAX_TARGET_FILES + 5)]
    for p in paths:
        (tmp_path / p).write_text("def f():\n    return 1\n", encoding="utf-8")
    fake = _write_fake_cccc(
        tmp_path,
        exit_code=0,
        payload={
            "files": [
                {
                    "path": "f0.py",
                    "functions": [
                        {"name": "f", "line": 1, "cognitive": 99, "cyclomatic": 1}
                    ],
                }
            ],
            "summary": {},
        },
    )
    monkeypatch.delenv("CCCC_GATE_DISABLE", raising=False)
    monkeypatch.setenv("CCCC_BIN", str(fake))
    monkeypatch.setattr(gate, "_repo_root", lambda: str(tmp_path))
    monkeypatch.setattr(gate, "_select_targets", lambda _r: (paths, None, None))
    monkeypatch.setattr(
        gate,
        "_changed_lines_map",
        lambda root, targets, **_k: {t: None for t in targets},
    )
    monkeypatch.setattr(gate, "_get_retry_count", lambda: 0)
    monkeypatch.setattr(gate, "_set_retry_count", lambda _n: None)
    monkeypatch.setattr(sys, "argv", ["cccc-complexity-gate.py"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    gate.main()
    captured = capsys.readouterr()
    assert "truncating targets" in captured.err
    data = json.loads(captured.out)
    assert "省略 5 件" in data["reason"]


def test_retry_cap_allows_stop(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
):
    monkeypatch.delenv("CCCC_GATE_DISABLE", raising=False)
    monkeypatch.setattr(gate, "_find_cccc", lambda: "/bin/true")
    monkeypatch.setattr(gate, "_repo_root", lambda: "/tmp")
    monkeypatch.setattr(gate, "_get_retry_count", lambda: gate.MAX_RETRIES)
    reset = {"called": False}
    monkeypatch.setattr(
        gate, "_reset_retries", lambda: reset.__setitem__("called", True)
    )
    monkeypatch.setattr(sys, "argv", ["cccc-complexity-gate.py"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    gate.main()
    captured = capsys.readouterr()
    assert "リトライ上限" in captured.err
    assert captured.out == ""
    assert reset["called"] is True


def test_check_cli_exits_one_on_block(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
):
    src = tmp_path / "hot.py"
    src.write_text("def hot():\n    return 1\n", encoding="utf-8")
    fake = _write_fake_cccc(
        tmp_path,
        exit_code=0,
        payload={
            "files": [
                {
                    "path": "hot.py",
                    "functions": [
                        {"name": "hot", "line": 1, "cognitive": 99, "cyclomatic": 1}
                    ],
                }
            ],
            "summary": {},
        },
    )
    monkeypatch.delenv("CCCC_GATE_DISABLE", raising=False)
    monkeypatch.setenv("CCCC_BIN", str(fake))
    monkeypatch.setattr(gate, "_repo_root", lambda: str(tmp_path))
    monkeypatch.setattr(gate, "_select_targets", lambda _r: (["hot.py"], None, None))
    monkeypatch.setattr(
        gate, "_changed_lines_map", lambda *_a, **_k: {"hot.py": None}
    )
    monkeypatch.setattr(sys, "argv", ["cccc-complexity-gate.py", "--check"])

    with pytest.raises(SystemExit) as exc:
        gate.main()
    assert exc.value.code == 1


def test_branch_files_warns_when_shallow(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(gate, "_resolve_merge_base", lambda: None)
    monkeypatch.setattr(gate, "_git_lines", lambda args, **_k: [])
    paths, warning = gate._get_branch_files()
    assert paths == []
    assert warning is not None
    assert "shallow" in warning or "merge-base unavailable" in warning
