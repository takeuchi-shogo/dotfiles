#!/usr/bin/env python3
"""Migrate subagent_complete/mcp_tool_usage to telemetry.jsonl.

Usage:
    python3 tools/migrate-telemetry.py [--dry-run]
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

LEARNINGS = Path.home() / ".claude" / "agent-memory" / "learnings"
PATTERNS = LEARNINGS / "patterns.jsonl"
TELEMETRY = LEARNINGS / "telemetry.jsonl"

TELEMETRY_TYPES = {"subagent_complete", "mcp_tool_usage"}


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    if not PATTERNS.exists():
        print("patterns.jsonl not found")
        return

    lines = PATTERNS.read_text(encoding="utf-8").splitlines()
    kept: list[str] = []
    migrated: list[str] = []

    for line in lines:
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            kept.append(line)
            continue

        if entry.get("type", "") in TELEMETRY_TYPES:
            migrated.append(line)
        else:
            kept.append(line)

    print(f"Total: {len(lines)}, Migrate: {len(migrated)}, Keep: {len(kept)}")

    if dry_run:
        print("(dry-run, no changes)")
        return

    # Append migrated entries to telemetry.jsonl
    with open(TELEMETRY, "a", encoding="utf-8") as f:
        for line in migrated:
            f.write(line + "\n")

    # Atomic write patterns.jsonl
    tmp = PATTERNS.with_suffix(".tmp")
    tmp.write_text(
        "\n".join(kept) + ("\n" if kept else ""),
        encoding="utf-8",
    )
    os.replace(tmp, PATTERNS)
    print(f"Done. Migrated {len(migrated)} entries to telemetry.jsonl")


if __name__ == "__main__":
    main()
