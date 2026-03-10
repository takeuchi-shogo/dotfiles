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
    json.dump({
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": context,
        }
    }, sys.stdout)


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

def run_hook(hook_name: str, main_func: Callable) -> None:
    """Wrap hook main() with error handling."""
    try:
        main_func()
    except Exception as e:
        print(f"[{hook_name}] error: {e}", file=sys.stderr)
        json.dump({}, sys.stdout)
