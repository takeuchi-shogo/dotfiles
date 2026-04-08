#!/usr/bin/env python3
"""Write/check harness review PASS flag.

Used by:
  - /review skill: writes flag after PASS verdict on harness changes
  - completion-gate.py: checks flag existence (via shared constants)

Usage:
  python3 harness_review_flag.py write   # write PASS flag
  python3 harness_review_flag.py check   # exit 0 if flag exists, 1 otherwise
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile

HARNESS_PATH_MARKERS = [
    "scripts/policy/",
    "scripts/runtime/",
    "settings.json",
    "CLAUDE.md",
    "/agents/",
]

FLAG_DIR = os.path.join(tempfile.gettempdir(), "claude-harness-review")


def get_changed_harness_files() -> list[str]:
    """Get uncommitted harness file changes."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return []
        return sorted(
            f.strip()
            for f in result.stdout.splitlines()
            if f.strip() and any(m in f for m in HARNESS_PATH_MARKERS)
        )
    except (subprocess.TimeoutExpired, OSError):
        return []


def flag_path(files: list[str]) -> str:
    """Flag file path keyed by changed harness file set."""
    os.makedirs(FLAG_DIR, exist_ok=True)
    content = "\n".join(files)
    h = hashlib.md5(content.encode()).hexdigest()[:12]
    return os.path.join(FLAG_DIR, f"pass-{h}")


def write_flag() -> bool:
    """Write PASS flag for current harness changes. Returns True if written."""
    files = get_changed_harness_files()
    if not files:
        return False
    path = flag_path(files)
    with open(path, "w") as f:
        f.write("PASS")
    return True


def check_flag() -> bool:
    """Check if PASS flag exists for current harness changes."""
    files = get_changed_harness_files()
    if not files:
        return True  # no harness changes — no flag needed
    return os.path.exists(flag_path(files))


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: harness_review_flag.py [write|check]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "write":
        if write_flag():
            print("[Harness Review Flag] PASS flag written.")
        else:
            print("[Harness Review Flag] No harness changes.")
    elif cmd == "check":
        sys.exit(0 if check_flag() else 1)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
