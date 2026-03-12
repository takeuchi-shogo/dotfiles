"""Shared storage utilities for AutoEvolve data access.

Provides common functions for locating the data directory and reading JSONL files.
Used by trace_sampler, evaluator_metrics, session_events, and other modules.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


def get_data_dir() -> Path:
    """Return the data directory, respecting AUTOEVOLVE_DATA_DIR for tests.

    Falls back to ~/.claude/agent-memory using Path.home() to avoid
    issues when HOME is unset.
    """
    override = os.environ.get("AUTOEVOLVE_DATA_DIR")
    if override:
        return Path(override)
    return Path.home() / ".claude" / "agent-memory"


def read_jsonl(path: Path) -> list[dict]:
    """Read a JSONL file and return a list of parsed entries.

    Skips malformed lines silently. Returns [] if the file does not exist.
    """
    if not path.exists():
        return []
    entries: list[dict] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped:
                try:
                    entries.append(json.loads(stripped))
                except json.JSONDecodeError:
                    continue
    return entries
