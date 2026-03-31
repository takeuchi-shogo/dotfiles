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
import shutil
import subprocess
import sys
from pathlib import Path


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


def _detect_runtimes() -> dict[str, str]:
    """Detect available language runtimes and their versions."""
    runtimes: dict[str, str] = {}
    checks = [
        ("node", ["node", "--version"]),
        ("python", ["python3", "--version"]),
        ("go", ["go", "version"]),
        ("rustc", ["rustc", "--version"]),
        ("ruby", ["ruby", "--version"]),
        ("java", ["java", "--version"]),
    ]
    for name, cmd in checks:
        if shutil.which(cmd[0]):
            ver = _run(cmd)
            if ver:
                runtimes[name] = ver.split("\n")[0]
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


def _get_top_level_dirs(cwd: str, limit: int = 15) -> list[str]:
    """List top-level directory entries."""
    try:
        entries = sorted(os.listdir(cwd))
        return entries[:limit]
    except OSError:
        return []


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

    # Top-level structure
    top = _get_top_level_dirs(cwd)
    if top:
        lines.append(f"Top-level: {', '.join(top)}")

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
