#!/usr/bin/env python3
"""Memory vector hint SessionStart hook (Phase D, post-review hardened).

Reads cwd/HANDOFF.md (tail 1000 chars), runs semantic top-K against
~/.claude/skill-data/memory-vec/index.db, and prints a [Memory Hint] block
with PATH-ONLY suggestions to stdout. File body is never included.

Always exits 0 with empty output on any failure (must not block session start).

Hardening (post-review):
  - shutil.which("node") to avoid PATH binary hijack
  - log entries are routed through the Phase A redactor (defense-in-depth)
    so traceback / error text containing handoff secrets is masked before
    being persisted to ~/.claude/logs/memory-vec.log
  - subprocess returncode != 0 is now recorded with truncated stderr
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

SKILL_DATA = Path.home() / ".claude" / "skill-data" / "memory-vec"
INDEX_DB = SKILL_DATA / "index.db"
QUERY_SCRIPT = SKILL_DATA / "query.ts"
LOG_FILE = Path.home() / ".claude" / "logs" / "memory-vec.log"
REDACTOR_LIB = SKILL_DATA / "lib"

QUERY_TIMEOUT_SEC = 5.0
QUERY_TAIL_CHARS = 1000
DISTANCE_THRESHOLD = 1.5
TOP_K = 5
STDERR_LOG_CAP = 500


def _resolve_node() -> str | None:
    """Resolve node binary to an absolute path; return None if unavailable."""
    resolved = shutil.which("node")
    return resolved


def _scrub(text: str) -> str:
    """Best-effort redact via Phase A wrapper; truncate on failure."""
    if not text:
        return text
    try:
        if str(REDACTOR_LIB) not in sys.path:
            sys.path.insert(0, str(REDACTOR_LIB))
        from memory_redactor import redact_for_embedding  # type: ignore

        return redact_for_embedding(text)
    except (ImportError, OSError, ValueError) as exc:
        # Redactor unavailable — fall back to length-capped passthrough.
        # Keep the cap tight so any unredacted secret has minimal exposure.
        truncated = text if len(text) <= 200 else f"{text[:200]}... [truncated]"
        return f"[REDACT_UNAVAILABLE: {type(exc).__name__}] {truncated}"


def _log(stage: str, error: BaseException, extra: dict | None = None) -> None:
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        err_text = f"{type(error).__name__}: {error}"
        tb_text = traceback.format_exc()
        entry: dict = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "source": "memory-vec-hint-hook",
            "stage": stage,
            "error": _scrub(err_text),
            "traceback": _scrub(tb_text),
        }
        if extra:
            entry.update({k: _scrub(str(v)) for k, v in extra.items()})
        with LOG_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        # Disk full / permission denied — hook must still exit 0.
        # Cannot escalate further without violating the no-block contract.
        return


def _log_event(stage: str, payload: dict) -> None:
    """Record a non-exception event (e.g. nonzero exit) with scrubbed fields."""
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "source": "memory-vec-hint-hook",
            "stage": stage,
        }
        for k, v in payload.items():
            entry[k] = _scrub(str(v)) if isinstance(v, str) else v
        with LOG_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        return


def _get_cwd() -> Path:
    """Read cwd from hook payload; fallback to os.getcwd()."""
    try:
        raw = sys.stdin.read()
        if raw:
            payload = json.loads(raw)
            cwd = payload.get("cwd")
            if cwd and isinstance(cwd, str):
                p = Path(cwd)
                if p.is_absolute() and p.is_dir():
                    return p
    except (OSError, ValueError, TypeError) as exc:
        _log("payload_parse", exc)
    return Path(os.getcwd())


HANDOFF_CANDIDATES = ("HANDOFF.md", "tmp/HANDOFF.md")


def _read_handoff_tail(cwd: Path) -> str | None:
    for relative in HANDOFF_CANDIDATES:
        handoff = cwd / relative
        if not handoff.is_file():
            continue
        try:
            text = handoff.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            _log("handoff_read", exc)
            continue
        stripped = text.strip()
        if stripped:
            return stripped[-QUERY_TAIL_CHARS:]
    return None


def _run_query(query: str, node_bin: str) -> list[dict] | None:
    if not INDEX_DB.is_file() or not QUERY_SCRIPT.is_file():
        return None
    try:
        result = subprocess.run(
            [
                node_bin,
                "--experimental-strip-types",
                "--no-warnings",
                str(QUERY_SCRIPT),
                query,
            ],
            capture_output=True,
            text=True,
            timeout=QUERY_TIMEOUT_SEC,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        _log("query_subprocess", exc)
        return None

    if result.returncode != 0:
        _log_event(
            "query_nonzero",
            {
                "returncode": result.returncode,
                "stderr": (result.stderr or "")[:STDERR_LOG_CAP],
            },
        )
        return None
    if not result.stdout.strip():
        return None
    try:
        rows = json.loads(result.stdout)
    except ValueError as exc:
        _log("query_parse", exc)
        return None
    if not isinstance(rows, list):
        return None
    return rows


def _format_hint(rows: list[dict]) -> str:
    filtered = [
        r
        for r in rows
        if isinstance(r, dict)
        and isinstance(r.get("distance"), (int, float))
        and r["distance"] < DISTANCE_THRESHOLD
        and isinstance(r.get("path"), str)
    ][:TOP_K]
    if not filtered:
        return ""

    lines = [
        "[Memory Hint] HANDOFF intent から関連 memory (top-{0}):".format(len(filtered))
    ]
    for r in filtered:
        lines.append(f"- {r['path']} (rel: {r['distance']:.2f})")
    lines.append("")
    lines.append(
        "Read tool で必要時に展開してください。本 hint に file 内容は含まれません。"
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    node_bin = _resolve_node()
    if node_bin is None:
        _log_event("node_missing", {"note": "node binary not found in PATH"})
        return 0

    cwd = _get_cwd()
    query = _read_handoff_tail(cwd)
    if query is None:
        return 0

    rows = _run_query(query, node_bin)
    if rows is None:
        return 0

    hint = _format_hint(rows)
    if hint:
        sys.stdout.write(hint)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        _log("unhandled", exc)
        sys.exit(0)
