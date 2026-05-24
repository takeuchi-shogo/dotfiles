#!/usr/bin/env python3
"""
Permission audit: summarize permissions.allow / deny and flag pruning candidates.

Manual trigger (no cron). Read-only — never mutates settings.json.

Output (stdout):
  1. counts (allow / deny) + tool-type histogram
  2. pruning candidates:
     - path-specific allows where the path no longer exists
     - mcp__* allows for MCP servers that are disabled / not configured
  3. scope-creep signals: Bash wildcards, large allow lists

Exit codes:
  0 — audit completed (with or without findings)
  1 — settings.json unreadable / malformed
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

SETTINGS_PATH = Path.home() / ".claude" / "settings.json"

ALLOW_COUNT_WARN = 100
BASH_WILDCARD_WARN = 10


def categorize(rule: str) -> str:
    head = rule.split("(", 1)[0]
    if head.startswith("mcp__"):
        return "mcp"
    return head or "other"


def expand_path(token: str) -> str:
    return os.path.expanduser(os.path.expandvars(token))


def extract_path_candidate(rule: str) -> str | None:
    m = re.match(r"^(Read|Write|Edit|Glob|Grep)\(([^)]+)\)$", rule)
    if not m:
        return None
    arg = m.group(2).strip()
    if any(ch in arg for ch in "*?["):
        return None
    if arg.startswith(("~", "/", "./")) or "/" in arg:
        return arg
    return None


def load_settings() -> dict | None:
    try:
        with SETTINGS_PATH.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        print(f"settings.json not found at {SETTINGS_PATH}", file=sys.stderr)
    except json.JSONDecodeError as exc:
        print(f"settings.json malformed: {exc}", file=sys.stderr)
    return None


def print_histogram(allow: list[str]) -> None:
    hist = Counter(categorize(r) for r in allow)
    print("\nAllow tool-type histogram:")
    for tool, count in sorted(hist.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {tool:<10} {count}")


def find_missing_paths(allow: list[str]) -> list[tuple[str, str]]:
    missing: list[tuple[str, str]] = []
    for rule in allow:
        candidate = extract_path_candidate(rule)
        if candidate is None:
            continue
        expanded = expand_path(candidate)
        if not Path(expanded).exists():
            missing.append((rule, expanded))
    return missing


def find_unknown_mcp_grants(allow: list[str], mcp_servers: dict) -> list[str]:
    disabled_mcp = {
        name
        for name, conf in mcp_servers.items()
        if isinstance(conf, dict) and conf.get("enabled") is False
    }
    unknown: list[str] = []
    for rule in allow:
        if not rule.startswith("mcp__"):
            continue
        m = re.match(r"^mcp__([A-Za-z0-9_-]+)__", rule)
        if not m:
            continue
        server = m.group(1)
        if server in disabled_mcp:
            unknown.append(f"{rule}  (server disabled)")
        elif mcp_servers and server not in mcp_servers:
            unknown.append(f"{rule}  (server not configured)")
    return unknown


def print_truncated_list(header: str, items: list[str], limit: int = 20) -> None:
    if not items:
        return
    print(f"\n{header}: {len(items)}")
    for line in items[:limit]:
        print(f"  - {line}")
    if len(items) > limit:
        print(f"  ... ({len(items) - limit} more)")


def main() -> int:
    settings = load_settings()
    if settings is None:
        return 1

    perms = settings.get("permissions", {}) or {}
    allow = perms.get("allow", []) or []
    deny = perms.get("deny", []) or []
    mcp_servers = settings.get("mcpServers", {}) or {}

    print(f"=== Permission Audit ({SETTINGS_PATH}) ===")
    print(f"allow: {len(allow)} rules")
    print(f"deny : {len(deny)} rules")
    if len(allow) >= ALLOW_COUNT_WARN:
        print(f"  [warn] allow >= {ALLOW_COUNT_WARN} — review recommended")

    print_histogram(allow)

    bash_wildcards = [r for r in allow if r.startswith("Bash(") and ":*" in r]
    if len(bash_wildcards) >= BASH_WILDCARD_WARN:
        print(
            f"\n[signal] Bash wildcard grants: {len(bash_wildcards)} "
            f">= {BASH_WILDCARD_WARN} — scope creep possible"
        )

    missing_paths = find_missing_paths(allow)
    print_truncated_list(
        "Pruning candidates (path missing)",
        [f"{rule}  →  {expanded}" for rule, expanded in missing_paths],
    )

    unknown_mcp = find_unknown_mcp_grants(allow, mcp_servers)
    print_truncated_list("MCP grants for disabled/unknown servers", unknown_mcp)

    print("\n=== Done. No automatic deletion — review and prune manually. ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
