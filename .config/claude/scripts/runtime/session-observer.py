#!/usr/bin/env python3
"""Claude Code Session Observer.

セッションの transcript JSONL + debug log をリアルタイムで監視し、
カテゴリ別・日付別の構造化 JSONL に記録する。

Usage:
  python3 session-observer.py --latest
  python3 session-observer.py --latest --debug-log ~/claude-debug.log
  python3 session-observer.py --latest --filter thinking
  python3 session-observer.py --latest --replay
  python3 session-observer.py --latest --compact
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import session_observer_fmt as fmt
import session_observer_parse as parse
from session_observer_router import EventRouter

PROJECTS_DIR = Path.home() / ".claude" / "projects"
OBSERVE_DIR = Path.home() / ".claude" / "agent-memory" / "logs" / "observe"


@dataclass(frozen=True)
class TailConfig:
    """Immutable config passed through the tail pipeline."""

    sid: str
    filters: set[str]
    compact: bool
    router: EventRouter


# --- session resolution ---


def find_latest_session() -> Path | None:
    """Find the most recently modified .jsonl transcript."""
    if not PROJECTS_DIR.exists():
        return None
    candidates = [
        (j.stat().st_mtime, j)
        for j in PROJECTS_DIR.rglob("*.jsonl")
        if "memory" not in j.parts and "logs" not in j.parts
    ]
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


def resolve_transcript(target: str) -> Path | None:
    """Resolve session ID or path to a transcript file."""
    p = Path(target)
    if p.exists() and p.suffix == ".jsonl":
        return p
    for jsonl in PROJECTS_DIR.rglob(f"{target}.jsonl"):
        return jsonl
    return None


# --- JSON parsing ---


def _try_parse_json(line: str) -> dict | None:
    stripped = line.strip()
    if not stripped:
        return None
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        print("[observer] skipping malformed line", file=sys.stderr)
        return None


# --- event display + routing ---


def _process_events(events: list[dict], cfg: TailConfig) -> None:
    for ev in events:
        cfg.router.route(ev)
    _display(events, cfg)


def _display(events: list[dict], cfg: TailConfig) -> None:
    for ev in events:
        cat = ev.get("cat", "")
        if "all" not in cfg.filters and cat not in cfg.filters:
            continue
        line = fmt.format_event(ev, cfg.compact)
        if line:
            print(line, flush=True)


# --- tail / replay ---


def run_tail(
    transcript: Path,
    debug_log: Path | None,
    cfg: TailConfig,
) -> None:
    """Tail transcript (+ optional debug log) in real-time."""
    if not cfg.compact:
        _print_header(transcript, cfg)

    tf = open(transcript, "r", encoding="utf-8")
    tf.seek(0, 2)
    df = None
    if debug_log:
        df = open(debug_log, "r", encoding="utf-8")
        df.seek(0, 2)

    try:
        while True:
            got = _tail_once(tf, df, cfg)
            if not got:
                time.sleep(0.3)
    except KeyboardInterrupt:
        if not cfg.compact:
            print(f"\n{fmt.C.DIM}Observer stopped.{fmt.C.RESET}")
    finally:
        tf.close()
        if df:
            df.close()
        cfg.router.close()


def _tail_once(tf, df, cfg: TailConfig) -> bool:
    got = False

    line = tf.readline()
    entry = _try_parse_json(line) if line else None
    if entry:
        got = True
        events = parse.parse_entry(entry, cfg.sid)
        _process_events(events, cfg)

    if df:
        dline = df.readline()
        if dline and dline.strip():
            got = True
            ev = parse.parse_debug_line(dline, cfg.sid)
            if ev:
                _process_events([ev], cfg)

    return got


def run_replay(transcript: Path, cfg: TailConfig) -> None:
    """Replay an entire session transcript."""
    try:
        with open(transcript, "r", encoding="utf-8") as f:
            for line in f:
                entry = _try_parse_json(line)
                if not entry:
                    continue
                events = parse.parse_entry(entry, cfg.sid)
                _process_events(events, cfg)
    finally:
        cfg.router.close()


def _print_header(transcript: Path, cfg: TailConfig) -> None:
    joined = ", ".join(sorted(cfg.filters))
    print(f"{fmt.C.BOLD}🔍 Observing: {transcript.name}{fmt.C.RESET}")
    print(f"{fmt.C.DIM}   Filters: {joined}{fmt.C.RESET}")
    print(f"{fmt.C.DIM}   Output:  {OBSERVE_DIR}{fmt.C.RESET}")
    print(f"{fmt.C.DIM}{'─' * 60}{fmt.C.RESET}")


# --- CLI ---


def main() -> None:
    p = argparse.ArgumentParser(description="Claude Code Session Observer")
    p.add_argument("target", nargs="?", help="Session ID or .jsonl")
    p.add_argument("--latest", action="store_true")
    p.add_argument("--debug-log", type=str, help="debug-file path")
    p.add_argument("--filter", type=str, default="all")
    p.add_argument("--compact", action="store_true")
    p.add_argument("--replay", action="store_true")

    args = p.parse_args()

    path = _resolve_path(args, p)
    filters = set(args.filter.split(","))
    router = EventRouter(OBSERVE_DIR)
    cfg = TailConfig(
        sid=path.stem,
        filters=filters,
        compact=args.compact,
        router=router,
    )

    debug_path = _resolve_debug(args.debug_log)

    if args.replay:
        run_replay(path, cfg)
    else:
        run_tail(path, debug_path, cfg)


def _resolve_path(args, parser) -> Path:
    if args.latest:
        path = find_latest_session()
    elif args.target:
        path = resolve_transcript(args.target)
    else:
        parser.print_help()
        sys.exit(1)

    if not path:
        print("Session not found.", file=sys.stderr)
        sys.exit(1)
    return path


def _resolve_debug(debug_log: str | None) -> Path | None:
    if not debug_log:
        return None
    p = Path(debug_log)
    if not p.exists():
        print(f"Debug log not found: {p}", file=sys.stderr)
        return None
    return p


if __name__ == "__main__":
    main()
