#!/usr/bin/env python3
"""SessionStart hook audit — measure stdout/stderr/latency per hook.

Reads `hooks.SessionStart` from `~/.claude/settings.json`, runs each command
once with empty stdin, and reports:
  - stdout / stderr byte sizes
  - wall-clock latency (perf_counter)
  - volatile heuristic: absolute timestamps (`YYYY-MM-DDTHH:MM`) or
    `<num>h ago` patterns that break prompt cache prefix

Targets (per absorb plan T2):
  - stdout per hook < 200 bytes  (only stdout flows into prompt cache)
  - total latency       < 3 sec

Usage:
  python3 sessionstart-audit.py
"""

from __future__ import annotations

import json
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

STDOUT_TARGET_BYTES = 200
TOTAL_LATENCY_TARGET_SEC = 3.0
PREVIEW_CHARS = 120

VOLATILE_PATTERNS = [
    (re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}"), "absolute timestamp"),
    (re.compile(r"\d+(?:\.\d+)?h ago"), "relative hour"),
    (re.compile(r"\d+\.\d+s\b"), "subsecond duration"),
]


def _detect_volatile(text: str) -> list[str]:
    return [label for pat, label in VOLATILE_PATTERNS if pat.search(text)]


def _truncate(text: str, n: int = PREVIEW_CHARS) -> str:
    text = text.replace("\n", " ⏎ ").strip()
    return text if len(text) <= n else text[:n] + "…"


def _run_hook(command: str) -> dict:
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            ["sh", "-c", command],
            input="",
            capture_output=True,
            text=True,
            timeout=30,
        )
        stdout, stderr, rc = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired:
        stdout, stderr, rc = "", "TIMEOUT (>30s)", -1
    latency = time.perf_counter() - start
    return {
        "command": command,
        "stdout_bytes": len(stdout.encode("utf-8")),
        "stderr_bytes": len(stderr.encode("utf-8")),
        "latency_sec": round(latency, 3),
        "stdout_preview": _truncate(stdout),
        "stderr_preview": _truncate(stderr),
        "stdout_volatile": _detect_volatile(stdout),
        "stderr_volatile": _detect_volatile(stderr),
        "returncode": rc,
    }


def _short_label(command: str) -> str:
    parts = shlex.split(command)
    for p in parts:
        if "/" in p and (p.endswith(".py") or p.endswith(".js")):
            return Path(p).name
        if p.startswith("date"):
            return "timestamp-write"
    return parts[0] if parts else command[:40]


def _print_report(results: list[dict]) -> None:
    total_latency = sum(r["latency_sec"] for r in results)
    over_target = [r for r in results if r["stdout_bytes"] > STDOUT_TARGET_BYTES]

    print("=" * 80)
    print("SessionStart Hook Audit")
    print("=" * 80)
    header = f"{'hook':<30} {'stdout':>8} {'stderr':>8} {'latency':>9}  flags"
    print(header)
    print("-" * 80)
    for r in results:
        label = _short_label(r["command"])
        flags = []
        if r["stdout_bytes"] > STDOUT_TARGET_BYTES:
            flags.append(f"OVER{STDOUT_TARGET_BYTES}B")
        if r["stdout_volatile"]:
            flags.append("VOLATILE-OUT")
        if r["stderr_volatile"]:
            flags.append("VOLATILE-ERR")
        if r["returncode"] != 0:
            flags.append(f"RC={r['returncode']}")
        print(
            f"{label:<30} "
            f"{r['stdout_bytes']:>7}B "
            f"{r['stderr_bytes']:>7}B "
            f"{r['latency_sec']:>7}s  "
            f"{','.join(flags) if flags else 'ok'}"
        )
    print("-" * 80)
    print(f"total latency: {total_latency:.3f}s (target < {TOTAL_LATENCY_TARGET_SEC}s)")
    print(
        f"hooks over stdout target ({STDOUT_TARGET_BYTES}B): "
        f"{len(over_target)} / {len(results)}"
    )

    if over_target:
        print("\nVerbose details for hooks exceeding stdout target:")
        for r in over_target:
            label = _short_label(r["command"])
            print(f"\n  [{label}] stdout preview:")
            print(f"    {r['stdout_preview']}")
            if r["stdout_volatile"]:
                print(f"    volatile: {', '.join(r['stdout_volatile'])}")


def main() -> int:
    settings_path = Path.home() / ".claude" / "settings.json"
    if not settings_path.exists():
        print(f"ERROR: {settings_path} not found", file=sys.stderr)
        return 2

    try:
        settings = json.loads(settings_path.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: malformed {settings_path}: {e}", file=sys.stderr)
        return 2
    hook_groups = settings.get("hooks", {}).get("SessionStart", [])
    commands = [
        h["command"]
        for grp in hook_groups
        for h in grp.get("hooks", [])
        if h.get("type") == "command" and h.get("command")
    ]

    if not commands:
        print("No SessionStart hooks found", file=sys.stderr)
        return 1

    results = [_run_hook(cmd) for cmd in commands]
    _print_report(results)

    total_latency = sum(r["latency_sec"] for r in results)
    over_target = [r for r in results if r["stdout_bytes"] > STDOUT_TARGET_BYTES]

    if over_target or total_latency > TOTAL_LATENCY_TARGET_SEC:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
