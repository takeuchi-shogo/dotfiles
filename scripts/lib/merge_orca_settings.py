"""Merge managed Orca settings into the live orca-data.json.

SSOT: <repo>/.config/orca/settings.json → settings (allowlisted keys only)
Live: ~/Library/Application Support/orca/profiles/local-default/orca-data.json
      (self-rewriting; worktrees / SSH / accounts / unmanaged keys preserved)

Usage:
  python3 scripts/lib/merge_orca_settings.py
  python3 scripts/lib/merge_orca_settings.py --ssot PATH --live PATH
  python3 scripts/lib/merge_orca_settings.py --validate-ssot
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SSOT = REPO_ROOT / ".config" / "orca" / "settings.json"

# Portable user prefs only. Paths, accounts, cookies, telemetry stay in live.
ALLOWED_KEYS = frozenset(
    {
        "appFontFamily",
        "appIcon",
        "autoRenameBranchFromWork",
        "branchPrefix",
        "branchPrefixCustom",
        "browserSshWorkspaceRoutingEnabled",
        "defaultTaskSource",
        "disabledTuiAgents",
        "editorAutoSave",
        "editorAutoSaveDelayMs",
        "editorFontFamily",
        "editorMinimapEnabled",
        "editorWordWrap",
        "experimentalActivity",
        "experimentalAgentDashboardMode",
        "experimentalAgentDashboardPopout",
        "leftSidebarAppearanceMode",
        "leftSidebarTintColor",
        "leftSidebarTintOpacity",
        "markdownReviewToolsEnabled",
        "minimizeToTrayOnClose",
        "nestedWorkerMaxDepth",
        "nestWorkspaces",
        "openInApplications",
        "refreshLocalBaseRefOnWorktreeCreate",
        "richMarkdownSpellcheckEnabled",
        "tabAutoGenerateTitle",
        "terminalActivePaneOpacity",
        "terminalAllowOsc52Clipboard",
        "terminalClipboardOnSelect",
        "terminalCursorBlink",
        "terminalCursorStyle",
        "terminalDividerColorDark",
        "terminalDividerColorLight",
        "terminalDividerThicknessPx",
        "terminalFastScrollSensitivity",
        "terminalFocusFollowsMouse",
        "terminalFontFamily",
        "terminalFontSize",
        "terminalFontWeight",
        "terminalFontWeightBold",
        "terminalGpuAcceleration",
        "terminalInactivePaneOpacity",
        "terminalJISYenToBackslash",
        "terminalLigatures",
        "terminalLineHeight",
        "terminalMacOptionAsAlt",
        "terminalMouseHideWhileTyping",
        "terminalPaneOpacityTransitionMs",
        "terminalRightClickToPaste",
        "terminalScrollbackRows",
        "terminalScrollSensitivity",
        "terminalShortcutPolicy",
        "terminalThemeDark",
        "terminalThemeLight",
        "terminalTuiScrollSensitivity",
        "terminalUseSeparateLightTheme",
        "theme",
        "uiLanguage",
        "visibleTaskProviders",
        "windowBackgroundBlur",
        "worktreeVisibilityDefaults",
    }
)


def default_live_path() -> Path:
    home = Path.home()
    if sys.platform == "darwin":
        return (
            home
            / "Library"
            / "Application Support"
            / "orca"
            / "profiles"
            / "local-default"
            / "orca-data.json"
        )
    return home / ".config" / "orca" / "profiles" / "local-default" / "orca-data.json"


def load_ssot(ssot_path: Path) -> dict[str, Any]:
    try:
        data = json.loads(ssot_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"load_ssot: invalid JSON at {ssot_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"load_ssot: {ssot_path} root must be an object")
    settings = data.get("settings")
    if not isinstance(settings, dict) or not settings:
        raise ValueError(f"load_ssot: {ssot_path} must have non-empty settings object")
    unknown = sorted(set(settings) - ALLOWED_KEYS)
    if unknown:
        raise ValueError(
            f"load_ssot: {ssot_path} has unmanaged keys (refused): {', '.join(unknown)}"
        )
    return dict(settings)


def load_live(live_path: Path) -> dict[str, Any] | None:
    if not live_path.exists():
        return None
    try:
        data = json.loads(live_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"load_live: invalid JSON at {live_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"load_live: {live_path} root must be an object")
    return data


def merge_settings(live: dict[str, Any], ssot: dict[str, Any]) -> dict[str, Any]:
    current = live.get("settings")
    settings = dict(current) if isinstance(current, dict) else {}
    settings.update(ssot)
    out = dict(live)
    out["settings"] = settings
    return out


def settings_unchanged(live: dict[str, Any], ssot: dict[str, Any]) -> bool:
    current = live.get("settings")
    if not isinstance(current, dict):
        return False
    return all(current.get(key) == value for key, value in ssot.items())


def atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent), prefix=".orca-data.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp:
            tmp.write(text)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ssot", type=Path, default=DEFAULT_SSOT)
    parser.add_argument("--live", type=Path, default=None)
    parser.add_argument(
        "--validate-ssot",
        action="store_true",
        help="validate SSOT only and exit without reading live",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print planned merge and exit without writing",
    )
    args = parser.parse_args(argv)

    try:
        ssot = load_ssot(args.ssot)
        if args.validate_ssot:
            print(f"ok  {args.ssot} ({len(ssot)} settings)")
            return 0
        live_path = args.live if args.live is not None else default_live_path()
        live = load_live(live_path)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if live is None:
        print(f"skip  live not found: {live_path}")
        return 0

    if args.dry_run:
        print(f"dry-run: would merge {len(ssot)} settings into {live_path}")
        return 0

    if settings_unchanged(live, ssot):
        print(f"ok  already current ({len(ssot)} settings) {live_path}")
        return 0

    atomic_write(live_path, merge_settings(live, ssot))
    print(f"ok  merged {len(ssot)} settings into {live_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
