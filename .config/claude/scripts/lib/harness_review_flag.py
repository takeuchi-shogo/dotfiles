#!/usr/bin/env python3
"""Write/check harness review PASS flag.

Used by:
  - /review skill: writes flag after PASS verdict on harness changes
  - completion-gate.py: checks flag existence (via shared constants)

Usage:
  python3 harness_review_flag.py write   # write PASS flag
  python3 harness_review_flag.py check   # exit 0 if flag exists, 1 otherwise
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys

# Single source: completion-gate.py imports these markers and the flag key.
# "claude/settings" scopes to Claude Code settings only and avoids false
# positives on .config/zed/settings.json, .vscode/settings.json etc.
HARNESS_PATH_MARKERS = [
    "scripts/policy/",
    "scripts/runtime/",
    "claude/settings",
    "CLAUDE.md",
    "/agents/",
    "scripts/lib/harness_review_flag.py",
]

# NOTE: Must NOT use tempfile.gettempdir(). This flag is written here (often via
# /review's sandboxed Bash, TMPDIR=/tmp/claude-*) but read by completion-gate.py
# in the unsandboxed Stop hook (macOS default /var/folders/.../T). Those resolve to
# different dirs, so a tempfile-keyed flag is never found and the gate blocks forever
# after a legitimate PASS. Key it to the stable session-state dir so both contexts
# agree.
FLAG_DIR = os.path.join(
    os.environ.get(
        "CLAUDE_SESSION_STATE_DIR",
        os.path.join(os.environ.get("HOME", ""), ".claude", "session-state"),
    ),
    "harness-review",
)


NUL = chr(0)


def _has_marker(path: str) -> bool:
    return any(m in path for m in HARNESS_PATH_MARKERS)


def get_changed_harness_files() -> list[str]:
    """Get uncommitted (tracked) harness file changes. [] if git fails."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "-z", "HEAD"],
            capture_output=True,
            timeout=5,
        )
        if result.returncode != 0:
            return []
        names = result.stdout.decode("utf-8", "surrogateescape").split(NUL)
        return sorted(f for f in names if f and _has_marker(f))
    except (subprocess.TimeoutExpired, OSError):
        return []


def _git(args: list[str], cwd: str | None = None) -> bytes:
    result = subprocess.run(
        ["git", "--literal-pathspecs", *args],
        capture_output=True,
        timeout=30,
        cwd=cwd,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {args[0]} failed: {result.stderr.decode('utf-8', 'replace').strip()}"
        )
    return result.stdout


def fingerprint(files: list[str]) -> str:
    """Content fingerprint of the reviewed harness state. Raises RuntimeError.

    Covers repo, HEAD, the binary-safe tracked diff of `files`, and the content
    of untracked harness files, so any edit after review changes the key.
    """
    try:
        top = _git(["rev-parse", "--show-toplevel"]).decode().strip()
        head = _git(["rev-parse", "HEAD"], top).strip()
        diff = _git(
            [
                "diff",
                "--binary",
                "--no-textconv",
                "--no-ext-diff",
                "--no-renames",
                "HEAD",
                "--",
                *sorted(files),
            ],
            top,
        )
        listing = _git(["ls-files", "-z", "--others", "--exclude-standard"], top)
        untracked = sorted(
            f
            for f in listing.decode("utf-8", "surrogateescape").split(NUL)
            if f and _has_marker(f)
        )
        h = hashlib.sha256()

        def feed(b: bytes) -> None:
            h.update(len(b).to_bytes(8, "big"))
            h.update(b)

        for part in (b"v2", top.encode(), head, diff):
            feed(part)
        for f in untracked:
            full = os.path.join(top, f)
            feed(f.encode("utf-8", "surrogateescape"))
            if os.path.islink(full):
                feed(os.readlink(full).encode("utf-8", "surrogateescape"))
            else:
                with open(full, "rb") as fh:
                    feed(fh.read())
        return h.hexdigest()[:16]
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"harness review fingerprint failed: {exc}") from exc


def flag_path(files: list[str]) -> str:
    """Flag file path keyed by the content fingerprint. Raises RuntimeError."""
    os.makedirs(FLAG_DIR, exist_ok=True)
    return os.path.join(FLAG_DIR, f"pass-{fingerprint(files)}")


def write_flag() -> bool:
    """Write PASS flag for current harness changes. Returns True if written."""
    files = get_changed_harness_files()
    if not files:
        return False
    path = flag_path(files)
    with open(path, "w") as f:
        f.write("PASS")
    return True


def check_flag() -> bool:
    """Check if PASS flag exists for current harness content (False on error)."""
    files = get_changed_harness_files()
    if not files:
        return True  # no harness changes — no flag needed
    try:
        return os.path.exists(flag_path(files))
    except (RuntimeError, OSError):
        return False


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: harness_review_flag.py [write|check]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "write":
        try:
            written = write_flag()
        except (RuntimeError, OSError) as exc:
            print(f"[Harness Review Flag] write failed: {exc}", file=sys.stderr)
            sys.exit(1)
        if written:
            print("[Harness Review Flag] PASS flag written.")
        else:
            print("[Harness Review Flag] No harness changes.")
    elif cmd == "check":
        sys.exit(0 if check_flag() else 1)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
