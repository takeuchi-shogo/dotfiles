"""merge_orca_settings の純ロジック検証。

実行: uvx pytest scripts/tests/test_merge_orca_settings.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

import merge_orca_settings as mos  # noqa: E402


def _write_json(path: Path, data: object) -> Path:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def test_load_ssot_returns_settings_when_keys_are_allowed(tmp_path: Path) -> None:
    ssot = _write_json(
        tmp_path / "settings.json",
        {"settings": {"theme": "dark", "terminalFontSize": 12}},
    )

    assert mos.load_ssot(ssot) == {"theme": "dark", "terminalFontSize": 12}


def test_load_ssot_raises_when_key_is_unmanaged(tmp_path: Path) -> None:
    ssot = _write_json(
        tmp_path / "settings.json",
        {"settings": {"theme": "dark", "opencodeSessionCookie": "secret"}},
    )

    with pytest.raises(ValueError, match="unmanaged keys"):
        mos.load_ssot(ssot)


def test_load_ssot_raises_when_settings_empty(tmp_path: Path) -> None:
    ssot = _write_json(tmp_path / "settings.json", {"settings": {}})

    with pytest.raises(ValueError, match="non-empty settings"):
        mos.load_ssot(ssot)


def test_load_live_returns_none_when_missing(tmp_path: Path) -> None:
    assert mos.load_live(tmp_path / "missing.json") is None


def test_merge_settings_overwrites_managed_keys_and_keeps_others() -> None:
    live = {
        "schemaVersion": 1,
        "worktreeMeta": {"wt-1": {"name": "keep-me"}},
        "settings": {
            "theme": "light",
            "workspaceDir": "/Users/me/orca/workspaces",
            "terminalFontSize": 13,
        },
    }

    merged = mos.merge_settings(live, {"theme": "dark", "terminalFontSize": 12})

    assert merged["settings"]["theme"] == "dark"
    assert merged["settings"]["terminalFontSize"] == 12
    assert merged["settings"]["workspaceDir"] == "/Users/me/orca/workspaces"
    assert merged["worktreeMeta"] == {"wt-1": {"name": "keep-me"}}
    assert live["settings"]["theme"] == "light"


def test_settings_unchanged_is_true_when_managed_values_match() -> None:
    live = {"settings": {"theme": "dark", "workspaceDir": "/tmp"}}

    assert mos.settings_unchanged(live, {"theme": "dark"}) is True
    assert mos.settings_unchanged(live, {"theme": "light"}) is False


def test_main_skips_when_live_missing(tmp_path: Path) -> None:
    ssot = _write_json(tmp_path / "settings.json", {"settings": {"theme": "dark"}})

    code = mos.main(["--ssot", str(ssot), "--live", str(tmp_path / "absent.json")])

    assert code == 0
    assert not (tmp_path / "absent.json").exists()


def test_main_writes_merged_settings(tmp_path: Path) -> None:
    ssot = _write_json(
        tmp_path / "settings.json",
        {"settings": {"theme": "dark", "terminalFontSize": 12}},
    )
    live_path = _write_json(
        tmp_path / "orca-data.json",
        {
            "worktreeMeta": {"wt-1": {}},
            "settings": {"theme": "light", "workspaceDir": "/tmp/ws"},
        },
    )

    code = mos.main(["--ssot", str(ssot), "--live", str(live_path)])

    assert code == 0
    written = json.loads(live_path.read_text(encoding="utf-8"))
    assert written["settings"]["theme"] == "dark"
    assert written["settings"]["terminalFontSize"] == 12
    assert written["settings"]["workspaceDir"] == "/tmp/ws"
    assert written["worktreeMeta"] == {"wt-1": {}}


def test_main_validate_ssot_does_not_read_live(tmp_path: Path) -> None:
    ssot = _write_json(tmp_path / "settings.json", {"settings": {"theme": "dark"}})

    assert mos.main(["--ssot", str(ssot), "--validate-ssot"]) == 0


def test_main_returns_error_when_ssot_has_secret_key(tmp_path: Path) -> None:
    ssot = _write_json(
        tmp_path / "settings.json",
        {"settings": {"workspaceDir": "/Users/me/orca"}},
    )

    assert mos.main(["--ssot", str(ssot), "--validate-ssot"]) == 1
