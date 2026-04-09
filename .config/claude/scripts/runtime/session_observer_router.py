#!/usr/bin/env python3
"""Event router — date-partitioned JSONL writer.

Receives categorized events and writes them to:
  {base_dir}/{yyyy-mm-dd}/{category}.jsonl

Each line is a self-contained JSON object with a common envelope.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TextIO

# Canonical categories
CATEGORIES = frozenset(
    {
        "user",
        "thinking",
        "responses",
        "tools",
        "skills",
        "agents",
        "mcp",
        "hooks",
        "tokens",
        "system",
        "debug",
    }
)


def make_event(
    cat: str,
    evt: str,
    sid: str = "",
    **fields: Any,
) -> dict[str, Any]:
    """Build a common-envelope event dict."""
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "sid": sid,
        "cat": cat,
        "evt": evt,
        **fields,
    }


class EventRouter:
    """Routes events to date-partitioned JSONL files."""

    def __init__(self, base_dir: Path) -> None:
        self._base = base_dir
        self._handles: dict[str, TextIO] = {}

    def route(self, event: dict[str, Any]) -> None:
        """Write event to the appropriate file."""
        cat = event.get("cat", "debug")
        date_str = _today()
        path = self._base / date_str / f"{cat}.jsonl"
        fh = self._open(path)
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")
        fh.flush()

    def close(self) -> None:
        for fh in self._handles.values():
            fh.close()
        self._handles.clear()

    def _open(self, path: Path) -> TextIO:
        key = str(path)
        if key in self._handles:
            return self._handles[key]
        path.parent.mkdir(parents=True, exist_ok=True)
        fh = open(path, "a", encoding="utf-8")
        self._handles[key] = fh
        return fh


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")
