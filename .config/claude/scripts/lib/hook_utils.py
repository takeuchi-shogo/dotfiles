#!/usr/bin/env python3
"""Hook utilities — shared patterns across Claude Code hooks."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable


# ============================================================================
# I/O
# ============================================================================


def load_hook_input() -> dict[str, Any]:
    """Load hook input JSON from stdin. Returns {} on failure."""
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return {}


def output_passthrough(data: dict) -> None:
    """Pass through hook input unchanged."""
    json.dump(data, sys.stdout)


def output_context(event_name: str, context: str) -> None:
    """Output hook-specific additionalContext."""
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": event_name,
                "additionalContext": context,
            }
        },
        sys.stdout,
    )


# ============================================================================
# Filtering
# ============================================================================


def check_tool(data: dict, required: str | list[str]) -> bool:
    """Return True if tool_name matches required tool(s)."""
    tool_name = data.get("tool_name", "")
    if isinstance(required, str):
        return tool_name == required
    return tool_name in required


# ============================================================================
# Path Resolution
# ============================================================================


def get_lib_dir() -> Path:
    """Return the scripts/lib/ directory (this file's location)."""
    return Path(__file__).resolve().parent


def get_scripts_dir() -> Path:
    """Return the scripts/ directory."""
    return get_lib_dir().parent


def get_references_dir() -> Path:
    """Return the references/ directory (sibling to scripts/)."""
    return get_scripts_dir().parent / "references"


def resolve_reference(filename: str) -> Path:
    """Resolve a file path within references/."""
    return get_references_dir() / filename


# ============================================================================
# Logging
# ============================================================================

LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB


def rotate_and_append(log_path: str, entry: str) -> None:
    """Append a line to a log file with best-effort rotation.

    Uses os.replace for atomic rename. Concurrent hook executions may
    cause a log entry to be lost during rotation — this is acceptable
    for audit/metrics logs.
    """
    import os

    try:
        if os.path.exists(log_path) and os.path.getsize(log_path) > LOG_MAX_BYTES:
            rotated = log_path + ".1"
            os.replace(log_path, rotated)  # atomic on POSIX
    except OSError as e:
        print(f"[hook_utils] log rotation warning: {e}", file=sys.stderr)

    try:
        with open(log_path, "a") as f:
            f.write(entry if entry.endswith("\n") else entry + "\n")
    except OSError as e:
        print(f"[hook_utils] log write warning: {e}", file=sys.stderr)


# ============================================================================
# Session Events
# ============================================================================


def get_emitter() -> Callable:
    """Import session_events.emit_event or return no-op."""
    try:
        from session_events import emit_event

        return emit_event
    except ImportError:
        return lambda *a, **kw: None


# ============================================================================
# Error Handling
# ============================================================================


def run_hook(hook_name: str, main_func: Callable, *, fail_closed: bool = False) -> None:
    """Wrap hook main() with error handling.

    Args:
        fail_closed: If True (for policy hooks), exit with code 2 on
            unexpected errors instead of passing through. This prevents
            security checks from being silently bypassed.
    """
    try:
        main_func()
    except SystemExit:
        raise  # preserve sys.exit(2) from policy blocks
    except Exception as e:
        print(f"[{hook_name}] error: {e}", file=sys.stderr)
        if fail_closed:
            print(
                f"BLOCKED: [{hook_name}] failed-closed on unexpected error",
                file=sys.stderr,
            )
            sys.exit(2)
        json.dump({}, sys.stdout)
