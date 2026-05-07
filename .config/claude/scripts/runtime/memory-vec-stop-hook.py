#!/usr/bin/env python3
"""Memory vector index Stop hook (Phase C).

If memory/*.md is newer than ~/.claude/skill-data/memory-vec/index.db,
fire-and-forget a background reindex via Node. Always exits 0 within ~100ms
so session termination is never blocked.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

MEMORY_DIR = (
    Path.home() / ".claude" / "projects" / "-Users-takeuchishougo-dotfiles" / "memory"
)
SKILL_DATA = Path.home() / ".claude" / "skill-data" / "memory-vec"
INDEX_DB = SKILL_DATA / "index.db"
REINDEX_SCRIPT = SKILL_DATA / "reindex.ts"
LOG_FILE = Path.home() / ".claude" / "logs" / "memory-vec.log"


def _log(stage: str, error: BaseException) -> None:
    """Append failure to log; swallow log failure (hook must not block)."""
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "source": "memory-vec-stop-hook",
            "stage": stage,
            "error": f"{type(error).__name__}: {error}",
            "traceback": traceback.format_exc(),
        }
        with LOG_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        # Disk full / permission denied — Stop hook must still exit 0.
        # Cannot escalate further without violating the no-block contract.
        return


def _drain_stdin() -> None:
    try:
        sys.stdin.read()
    except OSError as exc:
        _log("drain_stdin", exc)


def _log_event(stage: str, payload: dict) -> None:
    """Record a non-exception event without traceback."""
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "source": "memory-vec-stop-hook",
            "stage": stage,
        }
        entry.update(payload)
        with LOG_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        # Disk full / permission denied — Stop hook contract requires exit 0.
        return


def main() -> int:
    _drain_stdin()

    if not MEMORY_DIR.is_dir() or not REINDEX_SCRIPT.is_file():
        return 0

    node_bin = shutil.which("node")
    if node_bin is None:
        _log_event("node_missing", {"note": "node binary not found in PATH"})
        return 0

    try:
        md_files = list(MEMORY_DIR.glob("*.md"))
        if not md_files:
            return 0

        latest_md_mtime = max(f.stat().st_mtime for f in md_files)
        db_mtime = INDEX_DB.stat().st_mtime if INDEX_DB.is_file() else 0.0

        if latest_md_mtime <= db_mtime:
            return 0

        subprocess.Popen(
            [
                node_bin,
                "--experimental-strip-types",
                "--no-warnings",
                str(REINDEX_SCRIPT),
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except (OSError, ValueError) as exc:
        _log("dispatch", exc)

    return 0


if __name__ == "__main__":
    sys.exit(main())
