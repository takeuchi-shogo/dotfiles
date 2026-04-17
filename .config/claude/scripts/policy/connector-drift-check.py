#!/usr/bin/env python3
"""MCP connector drift checker.

Reads the 4 canonical MCP connector sources and reports drifts:
  1. .mcp.json                         (mcpServers)
  2. .claude/settings.json             (enabledMcpjsonServers)
  3. .codex/config.toml                ([mcp_servers.*])
  4. Hardcoded native plugin servers

Drifts = servers present in one source but missing where they should be enabled
(e.g., scite defined in .mcp.json but not in enabledMcpjsonServers).

Usage:
    connector-drift-check.py              # human-readable report
    connector-drift-check.py --json       # machine-readable
    connector-drift-check.py --fail-on-drift  # exit 2 if drift found
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

# Native servers (built into Claude Code / plugins, not in .mcp.json)
NATIVE_SERVERS = frozenset({"obsidian", "brave-search", "plugin_discord_discord"})


@dataclass
class SourceInventory:
    name: str
    path: str
    exists: bool
    servers: set[str] = field(default_factory=set)
    error: str | None = None


def _load_mcp_json(repo_root: Path) -> SourceInventory:
    path = repo_root / ".mcp.json"
    inv = SourceInventory(name=".mcp.json", path=str(path), exists=path.exists())
    if not inv.exists:
        return inv
    try:
        cfg = json.loads(path.read_text())
        inv.servers = set(cfg.get("mcpServers", {}))
    except (json.JSONDecodeError, OSError) as exc:
        inv.error = str(exc)
    return inv


def _load_settings_json(repo_root: Path) -> SourceInventory:
    path = repo_root / ".config" / "claude" / "settings.json"
    inv = SourceInventory(
        name="settings.json (enabledMcpjsonServers)",
        path=str(path),
        exists=path.exists(),
    )
    if not inv.exists:
        return inv
    try:
        cfg = json.loads(path.read_text())
        inv.servers = set(cfg.get("enabledMcpjsonServers", []))
    except (json.JSONDecodeError, OSError) as exc:
        inv.error = str(exc)
    return inv


def _load_codex_toml(repo_root: Path) -> SourceInventory:
    path = repo_root / ".codex" / "config.toml"
    inv = SourceInventory(
        name=".codex/config.toml",
        path=str(path),
        exists=path.exists(),
    )
    if not inv.exists:
        return inv
    try:
        with open(path, "rb") as f:
            cfg = tomllib.load(f)
        inv.servers = set(cfg.get("mcp_servers", {}))
    except (tomllib.TOMLDecodeError, OSError) as exc:
        inv.error = str(exc)
    return inv


def _load_native() -> SourceInventory:
    return SourceInventory(
        name="plugin native",
        path="<hardcoded>",
        exists=True,
        servers=set(NATIVE_SERVERS),
    )


def collect_inventories(repo_root: Path) -> list[SourceInventory]:
    return [
        _load_mcp_json(repo_root),
        _load_settings_json(repo_root),
        _load_codex_toml(repo_root),
        _load_native(),
    ]


def detect_drifts(inventories: list[SourceInventory]) -> list[dict]:
    """Detect drifts between the 4 sources.

    Drift kinds:
      - defined_but_not_enabled: in .mcp.json but not in enabledMcpjsonServers
      - codex_only: in Codex but not in any Claude source
      - claude_only: in Claude sources but not in Codex (informational)
    """
    by_name = {inv.name: inv for inv in inventories}
    mcp_json = by_name[".mcp.json"].servers
    enabled = by_name["settings.json (enabledMcpjsonServers)"].servers
    codex = by_name[".codex/config.toml"].servers
    native = by_name["plugin native"].servers

    drifts: list[dict] = []

    # 1. defined in .mcp.json but not enabled
    for srv in sorted(mcp_json - enabled):
        drifts.append(
            {
                "kind": "defined_but_not_enabled",
                "server": srv,
                "detail": (
                    f"'{srv}' defined in .mcp.json but missing from "
                    "enabledMcpjsonServers"
                ),
            }
        )

    # 2. Codex-only (not in any Claude-side source)
    claude_all = mcp_json | enabled | native
    for srv in sorted(codex - claude_all):
        drifts.append(
            {
                "kind": "codex_only",
                "server": srv,
                "detail": f"'{srv}' configured in Codex only",
            }
        )

    # 3. Claude-only (not in Codex) — informational
    for srv in sorted((mcp_json | enabled) - codex - native):
        drifts.append(
            {
                "kind": "claude_only",
                "server": srv,
                "detail": f"'{srv}' configured for Claude only (not in Codex)",
            }
        )

    return drifts


def _fmt_text(inventories: list[SourceInventory], drifts: list[dict]) -> str:
    lines = ["=== Connector Drift Report ==="]
    for inv in inventories:
        status = (
            "OK"
            if inv.exists and not inv.error
            else ("MISSING" if not inv.exists else "ERROR")
        )
        lines.append(f"\nSource: {inv.name}  [{status}]")
        lines.append(f"  path: {inv.path}")
        if inv.error:
            lines.append(f"  error: {inv.error}")
        if inv.servers:
            lines.append(
                f"  servers ({len(inv.servers)}): {', '.join(sorted(inv.servers))}"
            )

    lines.append("\n=== Drifts ===")
    if not drifts:
        lines.append("  (none detected)")
    else:
        for d in drifts:
            lines.append(f"  [{d['kind']}] {d['detail']}")
    return "\n".join(lines)


def _fmt_json(inventories: list[SourceInventory], drifts: list[dict]) -> str:
    return json.dumps(
        {
            "sources": [
                {
                    "name": inv.name,
                    "path": inv.path,
                    "exists": inv.exists,
                    "servers": sorted(inv.servers),
                    "error": inv.error,
                }
                for inv in inventories
            ],
            "drifts": drifts,
            "drift_count": len(drifts),
        },
        indent=2,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check MCP connector drift across 4 sources."
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument(
        "--fail-on-drift",
        action="store_true",
        help="Exit 2 if any drift is detected (including informational).",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root (defaults to script's parent 4 levels up).",
    )
    args = parser.parse_args()

    if args.repo_root is None:
        # Script lives at .config/claude/scripts/policy/<name>.py
        # parents: [0]=policy, [1]=scripts, [2]=claude, [3]=.config, [4]=repo root
        args.repo_root = Path(__file__).resolve().parents[4]

    inventories = collect_inventories(args.repo_root)
    drifts = detect_drifts(inventories)

    output = (
        _fmt_json(inventories, drifts) if args.json else _fmt_text(inventories, drifts)
    )
    print(output)

    if args.fail_on_drift and drifts:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
