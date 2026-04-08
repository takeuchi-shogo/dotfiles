#!/usr/bin/env python3
"""Diff coverage gate — checks if changed source files have test files.

Triggered by: hooks.Stop
Input: none (reads git diff)
Output: JSON with systemMessage advisory on stdout

Advisory only — never blocks.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import run_hook, get_emitter

emit = get_emitter()

# Language-specific test file patterns
_TEST_PATTERNS: dict[str, list[str]] = {
    ".go": ["{stem}_test.go"],
    ".ts": [
        "{stem}.test.ts",
        "{stem}.spec.ts",
        "__tests__/{stem}.ts",
        "__tests__/{stem}.test.ts",
    ],
    ".tsx": [
        "{stem}.test.tsx",
        "{stem}.spec.tsx",
        "__tests__/{stem}.tsx",
        "__tests__/{stem}.test.tsx",
    ],
    ".js": [
        "{stem}.test.js",
        "{stem}.spec.js",
        "__tests__/{stem}.js",
    ],
    ".jsx": [
        "{stem}.test.jsx",
        "{stem}.spec.jsx",
        "__tests__/{stem}.jsx",
    ],
    ".py": [
        "test_{stem}.py",
        "{stem}_test.py",
        "tests/test_{stem}.py",
    ],
}

_SKIP_DIRS = {
    "node_modules",
    "vendor",
    ".git",
    "dist",
    "build",
    "__pycache__",
    ".next",
    "target",
}

_TEST_FILE_PATTERNS = {
    "_test.go",
    ".test.",
    ".spec.",
    "test_",
    "__tests__",
}


def _is_test_file(path: str) -> bool:
    return any(p in path for p in _TEST_FILE_PATTERNS)


def _is_skippable(path: str) -> bool:
    parts = Path(path).parts
    return any(d in _SKIP_DIRS for d in parts)


def _get_changed_files() -> list[str]:
    """Get source files changed in the working tree."""
    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        )
        # Also include staged changes
        staged = subprocess.check_output(
            ["git", "diff", "--name-only", "--cached"],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        )
        files = set(out.strip().splitlines())
        files.update(staged.strip().splitlines())
        return sorted(f for f in files if f)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return []


def _find_test_file(
    source_path: str,
    repo_root: str,
) -> str | None:
    """Find a test file for the given source file."""
    p = Path(source_path)
    ext = p.suffix
    patterns = _TEST_PATTERNS.get(ext)
    if not patterns:
        return None

    stem = p.stem
    parent = p.parent

    for pattern in patterns:
        test_name = pattern.format(stem=stem)
        # Check in same directory
        candidate = parent / test_name
        full = os.path.join(repo_root, str(candidate))
        if os.path.isfile(full):
            return str(candidate)
        # Check in repo root (for patterns with tests/ prefix)
        if "/" in test_name:
            root_candidate = os.path.join(
                repo_root,
                str(parent),
                test_name,
            )
            if os.path.isfile(root_candidate):
                return str(Path(parent) / test_name)

    return None


def main() -> None:
    repo_root = ""
    try:
        repo_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return

    changed = _get_changed_files()
    if not changed:
        return

    uncovered: list[str] = []
    for f in changed:
        if _is_skippable(f) or _is_test_file(f):
            continue
        ext = Path(f).suffix
        if ext not in _TEST_PATTERNS:
            continue
        test = _find_test_file(f, repo_root)
        if test is None:
            uncovered.append(f)

    if not uncovered:
        return

    emit(
        "diff_coverage",
        {"uncovered_count": len(uncovered), "files": uncovered},
    )

    lines = [
        "[diff-coverage] テストファイルが見つからない変更:",
    ]
    for f in uncovered[:8]:
        lines.append(f"  ⚠️ {f}")
    if len(uncovered) > 8:
        lines.append(f"  ... 他 {len(uncovered) - 8} 件")
    lines.append("💡 変更したファイルに対応するテストの追加を検討してください")

    json.dump(
        {"systemMessage": "\n".join(lines)},
        sys.stdout,
    )


if __name__ == "__main__":
    run_hook("diff-coverage-gate", main, fail_closed=False)
