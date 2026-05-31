#!/usr/bin/env python3
"""SessionStart hook: Agent-BOM-lite — per-event runtime configuration snapshot.

Records ONE line per SessionStart event to session-bom.jsonl for supply-chain
forensics. Unlike skills-lock.json / .mcp.json (which are *definitions*), this
captures the *runtime configuration in effect* when a session started.

Design constraints:
- Observation-only + fail-open: NEVER blocks session startup.
- NEVER writes to stdout — SessionStart stdout is injected into the prompt/cache
  prefix (see docs/research/2026-05-04-sessionstart-audit.md). Errors go to stderr.
- "present_instruction_surfaces" is existence-only; a hook cannot confirm what
  Claude actually loaded into context.

Retention is delegated to hook_utils.rotate_and_append (10MB rotation).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import rotate_and_append  # noqa: E402

SCHEMA_VERSION = 1
LOG_PATH = os.path.expanduser("~/.claude/agent-memory/logs/session-bom.jsonl")


def _read_payload() -> dict:
    try:
        raw = sys.stdin.read()
    except (OSError, ValueError) as exc:
        print(f"[session-bom] stdin read failed: {exc}", file=sys.stderr)
        return {}
    if not raw.strip():
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"[session-bom] payload parse failed: {exc}", file=sys.stderr)
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _load_json(path: str) -> object | None:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as exc:
        print(f"[session-bom] cannot read {path}: {exc}", file=sys.stderr)
        return None


def _repo_trust(cwd: str) -> str:
    """git toplevel of cwd, or 'untracked' if not a repo / on error."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=3,
            cwd=cwd,
        )
    except (subprocess.TimeoutExpired, OSError, FileNotFoundError) as exc:
        print(f"[session-bom] git probe failed: {exc}", file=sys.stderr)
        return "untracked"
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return "untracked"


def _settings_facts() -> tuple[int | None, list[str] | None]:
    """(allowed_tools_count, enabled_mcpjson_servers) from ~/.claude/settings.json."""
    data = _load_json(os.path.expanduser("~/.claude/settings.json"))
    if not isinstance(data, dict):
        return None, None
    allow = data.get("permissions", {}).get("allow")
    count = len(allow) if isinstance(allow, list) else None
    enabled = data.get("enabledMcpjsonServers")
    enabled = sorted(enabled) if isinstance(enabled, list) else None
    return count, enabled


def _configured_mcp_servers(cwd: str) -> list[str] | None:
    """MCP servers declared in <cwd>/.mcp.json (None if file absent)."""
    path = os.path.join(cwd, ".mcp.json")
    if not os.path.exists(path):
        return None
    data = _load_json(path)
    if not isinstance(data, dict):
        return None
    servers = data.get("mcpServers")
    return sorted(servers.keys()) if isinstance(servers, dict) else []


def _active_skills_count(cwd: str) -> int | None:
    """skills count from <cwd>/skills-lock.json (None if file absent)."""
    path = os.path.join(cwd, "skills-lock.json")
    if not os.path.exists(path):
        return None
    data = _load_json(path)
    if not isinstance(data, dict):
        return None
    skills = data.get("skills")
    if isinstance(skills, (dict, list)):
        return len(skills)
    return None


def _present_instruction_surfaces(cwd: str) -> list[str]:
    """Existence check only — cannot confirm what Claude actually loaded."""
    candidates = [
        os.path.expanduser("~/.claude/CLAUDE.md"),
        os.path.join(cwd, "CLAUDE.md"),
        os.path.join(cwd, ".claude", "CLAUDE.md"),
        os.path.join(cwd, "AGENTS.md"),
    ]
    return [p for p in candidates if os.path.isfile(p)]


def main() -> None:
    payload = _read_payload()
    cwd = payload.get("cwd") or os.getcwd()
    allowed_tools_count, enabled_mcpjson = _settings_facts()

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "session_id": payload.get("session_id", "unknown"),
        "source": payload.get("source", "unknown"),
        "model": payload.get("model", "unknown"),
        "cwd": cwd,
        "repo_trust": _repo_trust(cwd),
        "allowed_tools_count": allowed_tools_count,
        "enabled_mcpjson_servers": enabled_mcpjson,
        "configured_mcp_servers": _configured_mcp_servers(cwd),
        "active_skills_count": _active_skills_count(cwd),
        "present_instruction_surfaces": _present_instruction_surfaces(cwd),
        "schema_version": SCHEMA_VERSION,
    }

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    rotate_and_append(LOG_PATH, json.dumps(entry))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — observation-only; never block startup, never stdout
        print(f"[session-bom] snapshot skipped: {exc}", file=sys.stderr)
