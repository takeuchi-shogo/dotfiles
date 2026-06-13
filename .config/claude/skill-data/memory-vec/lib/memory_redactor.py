"""Phase A wrapper around .config/claude/scripts/lib/redactor.redact().

Permanent location for Phase C (Stop hook reindex). Moved out of the spike
worktree so the reindex script can import it independently.

This module MUST NOT modify redactor.py itself — it only delegates.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import NamedTuple

# Resolve the existing redactor library inside the dotfiles repo.
# ~/.claude/ is a symlink to dotfiles/.config/claude/, so .scripts/lib lives there.
_LIB_DIR = Path.home() / ".claude" / "scripts" / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

from redactor import MASK, redact  # type: ignore  # noqa: E402


class RedactStats(NamedTuple):
    text: str
    bytes_in: int
    bytes_out: int
    redaction_count: int


def redact_for_embedding(text: str) -> str:
    return redact(text)


def redact_with_stats(text: str) -> RedactStats:
    bytes_in = len(text.encode("utf-8"))
    out = redact(text)
    return RedactStats(
        text=out,
        bytes_in=bytes_in,
        bytes_out=len(out.encode("utf-8")),
        redaction_count=out.count(MASK),
    )
