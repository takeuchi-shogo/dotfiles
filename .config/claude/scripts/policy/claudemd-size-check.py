#!/usr/bin/env python3
"""
PostToolUse hook: warn when CLAUDE.md / AGENTS.md / references/*.md exceed
size budgets defined in docs/adr/0007-thin-claudemd-thick-rules.md.

Reads PostToolUse JSON from stdin (matcher: Edit|Write), inspects the affected
file path, and prints a soft warning to stderr if the size exceeds the budget.
Exit code is always 0 (does not block).

Budgets (file size in bytes; read as UTF-8 byte count):
  - CLAUDE.md          : ≤ 4096
  - AGENTS.md          : ≤ 4096
  - references/*.md    : ≤ 8192

Disable with env var: CLAUDEMD_SIZE_CHECK=0
"""

import json
import os
import sys
from pathlib import Path

HOME = Path.home()

# (path-suffix-or-pattern, byte_budget, label)
BUDGETS = [
    ("CLAUDE.md", 4096, "CLAUDE.md"),
    ("AGENTS.md", 4096, "AGENTS.md"),
    ("/.codex/AGENTS.md", 4096, ".codex/AGENTS.md"),
]
REFERENCES_BUDGET = 8192


def is_target(path: str) -> tuple[int | None, str | None]:
    """Return (budget_bytes, label) if path is in scope, else (None, None)."""
    name = Path(path).name
    p = path.replace("\\", "/")
    if name == "CLAUDE.md":
        return 4096, "CLAUDE.md"
    if name == "AGENTS.md" and "/.codex/" in p:
        return 4096, ".codex/AGENTS.md"
    if name == "AGENTS.md":
        return 4096, "AGENTS.md"
    if "/references/" in p and name.endswith(".md"):
        return REFERENCES_BUDGET, "references"
    return None, None


def main() -> int:
    if os.environ.get("CLAUDEMD_SIZE_CHECK") == "0":
        return 0
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("path") or ""
    if not path:
        return 0
    budget, label = is_target(path)
    if budget is None:
        return 0
    target = Path(path)
    if not target.exists() or target.is_dir():
        return 0
    try:
        size = target.stat().st_size
    except OSError:
        return 0
    if size > budget:
        rel = str(target).replace(str(HOME), "~")
        msg = (
            f"[claudemd-size-check] {label} budget exceeded: "
            f"{size}B > {budget}B  ({rel})\n"
            f"  Consider moving content to references/ "
            f"(see docs/adr/0007-thin-claudemd-thick-rules.md)"
        )
        print(msg, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
