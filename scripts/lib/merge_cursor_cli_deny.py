"""Merge managed Cursor CLI deny rules into live ~/.cursor/cli-config.json.

SSOT: <repo>/.cursor/cli-permissions.json → permissions.deny
Live: ~/.cursor/cli-config.json (self-rewriting; auth/model/allow preserved)

Usage:
  python3 scripts/lib/merge_cursor_cli_deny.py
  python3 scripts/lib/merge_cursor_cli_deny.py --ssot PATH --live PATH
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
DEFAULT_SSOT = REPO_ROOT / ".cursor" / "cli-permissions.json"
DEFAULT_LIVE = Path.home() / ".cursor" / "cli-config.json"

MINIMAL_LIVE: dict[str, Any] = {
    "version": 1,
    "editor": {"vimMode": False},
    "permissions": {"allow": [], "deny": []},
}


def load_deny(ssot_path: Path) -> list[str]:
    data = json.loads(ssot_path.read_text(encoding="utf-8"))
    deny = data.get("permissions", {}).get("deny")
    if not isinstance(deny, list) or not deny:
        raise ValueError(
            f"load_deny: {ssot_path} must have non-empty permissions.deny list"
        )
    if not all(isinstance(item, str) and item for item in deny):
        raise ValueError(
            f"load_deny: {ssot_path} permissions.deny must be non-empty strings"
        )
    return list(deny)


def load_live(live_path: Path) -> dict[str, Any]:
    if not live_path.exists():
        return json.loads(json.dumps(MINIMAL_LIVE))
    try:
        data = json.loads(live_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"load_live: invalid JSON at {live_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"load_live: {live_path} root must be an object")
    return data


def merge_deny(live: dict[str, Any], deny: list[str]) -> dict[str, Any]:
    permissions = live.get("permissions")
    if not isinstance(permissions, dict):
        permissions = {}
    permissions = dict(permissions)
    if "allow" not in permissions or not isinstance(permissions["allow"], list):
        permissions["allow"] = []
    permissions["deny"] = list(deny)
    out = dict(live)
    out["permissions"] = permissions
    if "version" not in out:
        out["version"] = 1
    if "editor" not in out or not isinstance(out["editor"], dict):
        out["editor"] = {"vimMode": False}
    return out


def atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent), prefix=".cli-config.", suffix=".tmp"
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
    parser.add_argument("--live", type=Path, default=DEFAULT_LIVE)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print deny count and exit without writing",
    )
    args = parser.parse_args(argv)

    try:
        deny = load_deny(args.ssot)
        live = load_live(args.live)
        merged = merge_deny(live, deny)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"dry-run: would set {len(deny)} deny rules on {args.live}")
        return 0

    atomic_write(args.live, merged)
    print(f"ok  merged {len(deny)} deny rules into {args.live}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
