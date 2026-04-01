#!/usr/bin/env python3
"""Store raw session trace data to filesystem for selective access.

Triggered by: hooks.Stop (after session-learner.py)
Input: stdin passthrough
Output: stdout passthrough

Meta-Harness (Lee+ 2026): Summarization degrades performance (50.0→34.9).
Raw traces via FS selective access (grep) is the key to effective optimization.
AutoEvolve Proposer reads these traces with keyword grep, not summaries.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

TRACES_DIR = Path.home() / ".claude" / "agent-memory" / "traces"
MAX_AGE_DAYS = 90
MAX_TOTAL_BYTES = 500 * 1024 * 1024  # 500 MB


def _get_session_id() -> str:
    """Generate a short session identifier."""
    sid = os.environ.get("CLAUDE_SESSION_ID", "")
    if sid:
        return sid[:12]
    # Fallback: PID-based
    return f"pid-{os.getpid()}"


def _store_trace(data: str) -> None:
    """Parse and store session trace as JSONL."""
    logger = logging.getLogger("autoevolve")

    TRACES_DIR.mkdir(parents=True, exist_ok=True)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    session_id = _get_session_id()
    trace_path = TRACES_DIR / f"{today}_{session_id}.jsonl"

    # Parse input — expect JSON with session data
    try:
        payload = json.loads(data) if data.strip() else {}
    except json.JSONDecodeError:
        # Not JSON — store as raw text entry
        payload = {"raw_text": data[:10000]} if data.strip() else {}

    if not payload:
        return

    # Build trace entry with tool_strategy / context separation (Glean Trace Learning)
    cwd = os.getcwd()

    # Extract tool_strategy from payload if tool_calls present
    tool_calls = payload.get("tool_calls", []) if isinstance(payload, dict) else []
    tools_used = []
    if isinstance(tool_calls, list):
        tools_used = [tc.get("tool", "") for tc in tool_calls if isinstance(tc, dict)]

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "tool_strategy": {
            "tools_used": tools_used,
            "sequence_pattern": "",  # populated by contrastive-trace-analyzer
            "parallel_tools": [],
        },
        "context": {
            "cwd": cwd,
            "project": Path(cwd).name,
            "task_type": payload.get("task_type", "")
            if isinstance(payload, dict)
            else "",
        },
        "outcome": payload.get("outcome", "unknown")
        if isinstance(payload, dict)
        else "unknown",
    }

    # Extract known fields, fallback to storing entire payload
    if isinstance(payload, dict):
        for key in ("tool_calls", "errors", "tasks", "messages", "summary"):
            if key in payload:
                entry[key] = payload[key]
        if not any(
            k in payload
            for k in ("tool_calls", "errors", "tasks", "messages", "summary")
        ):
            entry["data"] = payload
    else:
        entry["data"] = payload

    # Append as JSONL (one line per entry, grep-friendly)
    with open(trace_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")

    logger.info("session-trace-store: saved trace to %s", trace_path.name)


def _cleanup_old_traces() -> None:
    """Remove traces older than MAX_AGE_DAYS and enforce size limit."""
    logger = logging.getLogger("autoevolve")

    if not TRACES_DIR.exists():
        return

    now = datetime.now(timezone.utc)
    total_size = 0
    files_by_mtime: list[tuple[float, Path]] = []

    for f in TRACES_DIR.iterdir():
        if not f.is_file() or f.suffix != ".jsonl":
            continue

        try:
            stat = f.stat()
        except OSError:
            continue

        age_days = (now.timestamp() - stat.st_mtime) / 86400

        if age_days > MAX_AGE_DAYS:
            f.unlink(missing_ok=True)
            logger.info("session-trace-store: deleted old trace %s", f.name)
            continue

        total_size += stat.st_size
        files_by_mtime.append((stat.st_mtime, f))

    # Enforce size limit — remove oldest first
    if total_size > MAX_TOTAL_BYTES:
        files_by_mtime.sort()  # oldest first
        for mtime, f in files_by_mtime:
            if total_size <= MAX_TOTAL_BYTES:
                break
            try:
                size = f.stat().st_size
            except OSError:
                continue
            f.unlink(missing_ok=True)
            total_size -= size
            logger.info("session-trace-store: deleted %s (size limit)", f.name)


def main() -> None:
    data = sys.stdin.read()
    try:
        _store_trace(data)
        _cleanup_old_traces()
    except Exception as e:
        logging.getLogger("autoevolve").error("session-trace-store error: %s", e)
    sys.stdout.write(data)


if __name__ == "__main__":
    main()
