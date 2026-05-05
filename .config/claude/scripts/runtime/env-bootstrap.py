#!/usr/bin/env python3
"""Environment bootstrap — inject system snapshot at session start.

Triggered by: hooks.SessionStart
Input: stdin passthrough
Output: stdout with [Environment Snapshot] block (additionalContext)

Meta-Harness (Lee+ 2026): TerminalBench-2 best harness's core was
"environment bootstrap" — a system snapshot before the agent loop starts.
Eliminates 3-5 exploratory turns.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Leading version-like token, e.g. "v25.9.0" -> "25.9.0", "java 14 2020" -> "14".
# `{0,2}` covers single-integer versions (Java 14) and full semver alike.
_VERSION_TOKEN_RE = re.compile(r"\d+(?:\.\d+){0,2}")


def _run(cmd: list[str], timeout: int = 5) -> str:
    """Run a command and return stdout, or empty string on failure."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


def _short_version(raw: str) -> str:
    """Extract the leading semver-like token; fall back to the first line."""
    first_line = raw.split("\n", 1)[0]
    m = _VERSION_TOKEN_RE.search(first_line)
    return m.group(0) if m else first_line


def _detect_runtimes() -> dict[str, str]:
    """Detect available language runtimes and their versions in parallel."""
    checks = [
        ("node", ["node", "--version"]),
        ("python", ["python3", "--version"]),
        ("go", ["go", "version"]),
        ("rustc", ["rustc", "--version"]),
        ("ruby", ["ruby", "--version"]),
        ("java", ["java", "--version"]),
    ]
    available = [(name, cmd) for name, cmd in checks if shutil.which(cmd[0])]
    if not available:
        return {}
    runtimes: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=len(available)) as ex:
        futures = {name: ex.submit(_run, cmd) for name, cmd in available}
        for name, fut in futures.items():
            raw = fut.result()
            if raw:
                runtimes[name] = _short_version(raw)
    return runtimes


def _detect_package_managers() -> list[str]:
    """Detect available package managers."""
    managers = []
    for pm in ("npm", "pnpm", "yarn", "pip", "cargo", "go", "brew", "apt"):
        if shutil.which(pm):
            managers.append(pm)
    return managers


def _detect_project_markers(cwd: str) -> list[str]:
    """Detect project type markers in current directory."""
    markers = []
    marker_files = [
        "package.json",
        "go.mod",
        "Cargo.toml",
        "pyproject.toml",
        "requirements.txt",
        "Gemfile",
        "pom.xml",
        "build.gradle",
        "Makefile",
        "Taskfile.yml",
        "docker-compose.yml",
        "Dockerfile",
        ".github/workflows",
        "CLAUDE.md",
    ]
    for m in marker_files:
        if (Path(cwd) / m).exists():
            markers.append(m)
    return markers


def build_snapshot() -> str:
    """Build the environment snapshot string."""
    cwd = os.getcwd()
    lines = ["[Environment Snapshot]"]

    # OS
    os_info = _run(["uname", "-sr"])
    if os_info:
        lines.append(f"OS: {os_info}")

    # Runtimes
    runtimes = _detect_runtimes()
    if runtimes:
        rt_str = ", ".join(f"{k}: {v}" for k, v in runtimes.items())
        lines.append(f"Runtimes: {rt_str}")

    # Package managers
    pms = _detect_package_managers()
    if pms:
        lines.append(f"Package managers: {', '.join(pms)}")

    # Project markers
    markers = _detect_project_markers(cwd)
    if markers:
        lines.append(f"Project markers: {', '.join(markers)}")

    lines.append("[/Environment Snapshot]")
    return "\n".join(lines)


def main() -> None:
    data = sys.stdin.read()
    try:
        snapshot = build_snapshot()
        sys.stdout.write(snapshot + "\n")
    except Exception:
        # Silent failure — don't block session start
        pass
    sys.stdout.write(data)


if __name__ == "__main__":
    main()
