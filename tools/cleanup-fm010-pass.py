#!/usr/bin/env python3
"""One-off cleanup: remove FM-010 PASS entries from patterns.jsonl.

Usage:
    python3 tools/cleanup-fm010-pass.py [--dry-run]
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

        fm = entry.get("failure_mode")
        entry_type = entry.get("type", "")
        is_pass_injection = (
            fm == "FM-010"
            and entry.get("clean") is True
            and entry_type == "injection_scan"
        )
        is_pass_security = (
            fm == "FM-010"
            and entry.get("verdict") == "PASS"
            and entry_type == "skill_security_scan"
        )
        if is_pass_injection or is_pass_security:
            removed += 1
        else:
            kept.append(line)

    print(f"Total: {len(lines)}, Remove: {removed}, Keep: {len(kept)}")

    if dry_run:
        print("(dry-run, no changes)")
    else:
        # Atomic write: tmp → rename to avoid partial writes
        tmp = PATTERNS.with_suffix(".tmp")
        tmp.write_text(
            "\n".join(kept) + ("\n" if kept else ""),
            encoding="utf-8",
        )
        os.replace(tmp, PATTERNS)
        print("Done.")


if __name__ == "__main__":
    main()
