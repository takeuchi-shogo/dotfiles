#!/usr/bin/env python3
"""Remove old FM-012 info-level entries (consecutive_reads=5).

Usage:
    python3 tools/cleanup-fm012-info.py [--dry-run]
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PATTERNS = Path.home() / ".claude" / "agent-memory" / "learnings" / "patterns.jsonl"


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    if not PATTERNS.exists():
        print("patterns.jsonl not found")
        return

    lines = PATTERNS.read_text(encoding="utf-8").splitlines()
    kept: list[str] = []
    removed = 0

    for line in lines:
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            kept.append(line)
            continue

        entry_type = entry.get("type", "")
        fm = entry.get("failure_mode", "")
        reads = entry.get(
            "consecutive_reads",
            entry.get("data", {}).get("consecutive_reads", 0),
        )

        is_info = (entry_type == "exploration_spiral" or fm == "FM-012") and reads <= 5

        if is_info:
            removed += 1
        else:
            kept.append(line)

    print(f"Total: {len(lines)}, Remove: {removed}, Keep: {len(kept)}")

    if dry_run:
        print("(dry-run, no changes)")
        return

    tmp = PATTERNS.with_suffix(".tmp")
    tmp.write_text(
        "\n".join(kept) + ("\n" if kept else ""),
        encoding="utf-8",
    )
    os.replace(tmp, PATTERNS)
    print("Done.")


if __name__ == "__main__":
    main()
