#!/usr/bin/env python3
"""TDD Guard hook (PreToolUse/Edit|Write).

When TDD_MODE=1, warns if editing an implementation file
that has no corresponding test file.
Advisory only — warns but does not block.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import load_hook_input, output_context, run_hook

# Implementation file extensions and their test file patterns
_TEST_PATTERNS: dict[str, list[str]] = {
    ".go": ["{stem}_test.go"],
    ".ts": ["{stem}.test.ts", "{stem}.spec.ts"],
    ".tsx": ["{stem}.test.tsx", "{stem}.spec.tsx"],
    ".py": ["{stem}_test.py", "test_{stem}.py"],
}

# Substrings that identify test files (skip checking these)
_TEST_MARKERS = (
    "test_",
    "_test.",
    ".test.",
    ".spec.",
    "__tests__",
    "testdata",
)


def _is_test_file(file_path: str) -> bool:
    return any(m in file_path for m in _TEST_MARKERS)


def _find_test(file_path: str) -> bool:
    """Check if a corresponding test file exists."""
    p = Path(file_path)
    ext = p.suffix
    if ext not in _TEST_PATTERNS:
        return True  # Not a target extension

    stem = p.stem
    search_dirs = [p.parent, p.parent / "__tests__"]

    for tmpl in _TEST_PATTERNS[ext]:
        test_name = tmpl.format(stem=stem)
        for d in search_dirs:
            if (d / test_name).exists():
                return True
    return False


def _check_tdd(data: dict) -> None:
    if os.environ.get("TDD_MODE") != "1":
        return

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Edit", "Write"):
        return

    file_path = (
        data.get("tool_input", {}).get("file_path")
        or data.get("tool_input", {}).get("path")
        or ""
    )
    if not file_path:
        return

    if _is_test_file(file_path):
        return

    ext = Path(file_path).suffix
    if ext not in _TEST_PATTERNS:
        return

    if not _find_test(file_path):
        basename = Path(file_path).name
        patterns = ", ".join(_TEST_PATTERNS[ext])
        output_context(
            "PreToolUse",
            f"[TDD Guard] `{basename}` に対応するテストファイルが"
            f"見つかりません。\n"
            f"TDD モードが有効です。先にテストを作成してください。\n"
            f"対応テスト候補: {patterns}",
        )


def main() -> None:
    data = load_hook_input()
    if not data:
        return
    _check_tdd(data)


if __name__ == "__main__":
    run_hook("tdd-guard", main, fail_closed=False)
