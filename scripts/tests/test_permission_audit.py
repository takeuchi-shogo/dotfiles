"""Tests for scripts/lifecycle/permission-audit.py"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "lifecycle" / "permission-audit.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("permission_audit", MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["permission_audit"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def pa():
    return _load_module()


def test_missing_secret_denies_detects_gaps(pa):
    deny = ["Bash(rm -rf *)"]
    missing = pa.find_missing_secret_denies(deny)
    assert ".env" in missing
    assert "~/.aws" in missing


def test_missing_secret_denies_ok_when_present(pa):
    deny = [
        "Read(.env*)",
        "Read(~/.ssh/**)",
        "Read(~/.aws/**)",
        "Read(~/.gnupg/**)",
        "Bash(printenv)",
        "Bash(env)",
    ]
    assert pa.find_missing_secret_denies(deny) == []


def test_shared_credential_env_signals(pa):
    env = {"AWS_SECRET_ACCESS_KEY": "x", "PATH": "/usr/bin"}
    hits = pa.find_shared_credential_env_signals(env)
    assert len(hits) == 1
    assert "AWS_SECRET_ACCESS_KEY" in hits[0]


def test_least_privilege_broad_allow(pa):
    signals = pa.least_privilege_signals(["Bash(*)"], ["Read(.env*)"])
    assert any("overly broad allow: Bash(*)" in s for s in signals)


def test_least_privilege_empty_deny(pa):
    signals = pa.least_privilege_signals(["Read"], [])
    assert any("deny list empty" in s for s in signals)


def test_main_with_agent_credentials(tmp_path, pa, capsys, monkeypatch):
    settings = {
        "permissions": {
            "allow": ["Read", "Bash(git status *)"],
            "deny": [
                "Read(.env*)",
                "Read(~/.ssh/**)",
                "Read(~/.aws/**)",
                "Read(~/.gnupg/**)",
                "Bash(printenv)",
                "Bash(env)",
            ],
        },
        "mcpServers": {},
    }
    path = tmp_path / "settings.json"
    path.write_text(json.dumps(settings), encoding="utf-8")
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)

    ec = pa.main(["--settings", str(path)])
    assert ec == 0
    out = capsys.readouterr().out
    assert "Agent credentials / least privilege" in out
    assert "Secret-path deny markers: ok" in out


def test_main_can_disable_agent_credentials(tmp_path, pa, capsys):
    settings = {"permissions": {"allow": [], "deny": []}, "mcpServers": {}}
    path = tmp_path / "settings.json"
    path.write_text(json.dumps(settings), encoding="utf-8")
    ec = pa.main(["--settings", str(path), "--no-agent-credentials"])
    assert ec == 0
    out = capsys.readouterr().out
    assert "Agent credentials / least privilege" not in out
