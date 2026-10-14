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
  4. agent-credential / least-privilege signals (default: on)
     Premise: agents inherit the operator's privileges unless scoped.
     Sources: deny-rules-catalog.md "Premise" (Speaker Deck / @dkfj).

Exit codes:
  0 — audit completed (with or without findings)
  1 — settings.json unreadable / malformed
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

SETTINGS_PATH = Path.home() / ".claude" / "settings.json"

ALLOW_COUNT_WARN = 100
BASH_WILDCARD_WARN = 10

# Secret-path deny substrings expected for least-privilege / no-direct-read.
# Matched as substring against deny rules (catalog + settings).
EXPECTED_SECRET_DENY_MARKERS = (
    ".env",
    "~/.ssh",
    "~/.aws",
    "~/.gnupg",
    "printenv",
    "Bash(env",  # covers Bash(env) and Bash(env *)
)

# Env-var names that often mean long-lived user credentials shared with agents.
SHARED_CREDENTIAL_ENV_HINTS = (
    "AWS_SECRET_ACCESS_KEY",
    "AWS_ACCESS_KEY_ID",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GH_TOKEN",
    "GITHUB_TOKEN",
)


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


def load_settings(path: Path = SETTINGS_PATH) -> dict | None:
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        print(f"settings.json not found at {path}", file=sys.stderr)
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


def find_missing_secret_denies(deny: list[str]) -> list[str]:
    """Return expected secret markers not covered by any deny rule substring."""
    missing: list[str] = []
    for marker in EXPECTED_SECRET_DENY_MARKERS:
        if not any(marker in rule for rule in deny):
            missing.append(marker)
    return missing


def find_shared_credential_env_signals(
    environ: dict[str, str] | None = None,
) -> list[str]:
    """Flag long-lived user credential env vars visible to the audit process.

    Premise: default agent inherits operator env. Prefer agent-dedicated /
    short-lived / proxy-execution over shared long-lived keys.
    """
    env = environ if environ is not None else os.environ
    hits: list[str] = []
    for name in SHARED_CREDENTIAL_ENV_HINTS:
        if env.get(name):
            hits.append(
                f"{name} is set in process env "
                "(prefer agent-dedicated / short-lived / proxy execution)"
            )
    return hits


def least_privilege_signals(allow: list[str], deny: list[str]) -> list[str]:
    """Heuristic signals that allow surface may exceed least privilege."""
    signals: list[str] = []
    bash_wildcards = [r for r in allow if r.startswith("Bash(") and "*" in r]
    if len(bash_wildcards) >= BASH_WILDCARD_WARN:
        signals.append(
            f"Bash wildcard allows: {len(bash_wildcards)} "
            f">= {BASH_WILDCARD_WARN} (scope creep / least-privilege risk)"
        )
    if len(allow) >= ALLOW_COUNT_WARN:
        signals.append(
            f"allow count {len(allow)} >= {ALLOW_COUNT_WARN} "
            "(review whether grants are still minimal)"
        )
    # Broad "can do anything shell" style grants
    for rule in allow:
        if rule in {"Bash(*)", "Bash", "Bash(sudo *)"}:
            signals.append(f"overly broad allow: {rule}")
    if not deny:
        signals.append("deny list empty — agent may share full user privilege surface")
    return signals


def print_truncated_list(header: str, items: list[str], limit: int = 20) -> None:
    if not items:
        return
    print(f"\n{header}: {len(items)}")
    for line in items[:limit]:
        print(f"  - {line}")
    if len(items) > limit:
        print(f"  ... ({len(items) - limit} more)")


def print_agent_credential_section(allow: list[str], deny: list[str]) -> None:
    print("\n=== Agent credentials / least privilege ===")
    print(
        "Premise: by default an agent runs with the operator's privileges "
        "(see deny-rules-catalog.md Premise)."
    )
    missing = find_missing_secret_denies(deny)
    print_truncated_list(
        "Missing expected secret-path denies (direct-read stage)",
        missing,
    )
    if not missing:
        print("\nSecret-path deny markers: ok (expected markers present)")

    shared = find_shared_credential_env_signals()
    print_truncated_list(
        "Shared long-lived credential env signals",
        shared,
    )
    if not shared:
        print("\nShared credential env signals: none detected in audit process env")

    lp = least_privilege_signals(allow, deny)
    print_truncated_list("Least-privilege signals", lp)
    if not lp:
        print("\nLeast-privilege signals: none")

    print(
        "\nGuidance (Speaker Deck 4 stages, safer downward): "
        "direct-read → env inject → store inject → proxy execution. "
        "Prefer agent-dedicated credentials; do not pass secret values when "
        "an allowed operation proxy suffices."
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--settings",
        type=Path,
        default=SETTINGS_PATH,
        help="Path to settings.json (default: ~/.claude/settings.json)",
    )
    parser.add_argument(
        "--agent-credentials",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Emit agent-dedicated credential / least-privilege signals (default: on)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    settings = load_settings(args.settings)
    if settings is None:
        return 1

    perms = settings.get("permissions", {}) or {}
    allow = perms.get("allow", []) or []
    deny = perms.get("deny", []) or []
    mcp_servers = settings.get("mcpServers", {}) or {}

    print(f"=== Permission Audit ({args.settings}) ===")
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

    if args.agent_credentials:
        print_agent_credential_section(allow, deny)

    print("\n=== Done. No automatic deletion — review and prune manually. ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
