#!/usr/bin/env python3
"""Review tier classifier — deterministic tier selection for code-review depth.

Input:  JSON on stdin:
    {
        "diff_stat": {"insertions": N, "deletions": N},
        "files": ["path/to/file", ...],
        "risk_class": "High" | "Medium" | "Low"
    }

Output: JSON on stdout:
    {
        "tier": "light" | "standard" | "deep",
        "reason": "<human-readable decision rationale>",
        "signals": {
            "total_lines": N,
            "risk_class": "...",
            "dependency_change": bool,
            "all_docs_or_tests": bool
        }
    }

Design notes
------------
This script handles ONLY deterministic signals: line counts, file
extensions, and well-known dependency filenames.  It does NOT classify
risk_class itself.

The single source of truth for risk categorisation is:
    skills/review/references/reviewer-routing.md

The calling agent (main agent / hook) must resolve risk_class using that
table and pass the result here.  Mixing the two concerns (risk lookup +
tiering arithmetic) into one script would create a hidden dependency on
the routing table and make independent testing harder.

Tier selection order (first match wins):
    1. deep    — risk_class == "High"  OR  total_lines > 200  OR
                 any dependency file changed
    2. light   — risk_class == "Low"  AND  total_lines <= 10  AND
                 len(files) >= 1  AND  ALL files are docs-only or test-only
    3. standard — everything else

Fail-safe: any parse error / missing field / unexpected risk_class value
returns "standard" with a fail-safe reason.  "standard" is the safe
middle ground: "light" risks under-reviewing, "deep" causes unnecessary
friction.
"""

from __future__ import annotations

import fnmatch
import json
import os
import sys
import traceback
from pathlib import PurePosixPath

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_VALID_RISK_CLASSES = frozenset({"High", "Medium", "Low"})

# Exact basenames that indicate a dependency/lock file change.
_DEPENDENCY_BASENAMES = frozenset(
    {
        "go.mod",
        "go.sum",
        "package.json",
        "package-lock.json",
        "Cargo.toml",
        "Cargo.lock",
        "pyproject.toml",
        "uv.lock",
        "poetry.lock",
    }
)

# ---------------------------------------------------------------------------
# Core classification helpers
# ---------------------------------------------------------------------------


def _is_dependency_file(path: str) -> bool:
    """Return True if *path* names a known dependency or lock file."""
    basename = os.path.basename(path)
    if basename in _DEPENDENCY_BASENAMES:
        return True
    # Catch any other *.lock files (e.g. composer.lock, yarn.lock).
    if basename.endswith(".lock"):
        return True
    return False


def _is_docs_only(path: str) -> bool:
    """Return True if *path* is documentation (Markdown extension)."""
    return path.endswith(".md")


def _is_test_only(path: str) -> bool:
    """Return True if *path* is a test file by name or location."""
    basename = os.path.basename(path)
    # Filename patterns: *_test.*, *.test.*, *.spec.*
    if (
        fnmatch.fnmatch(basename, "*_test.*")
        or fnmatch.fnmatch(basename, "*.test.*")
        or fnmatch.fnmatch(basename, "*.spec.*")
    ):
        return True
    # Path segments: /test/ or /tests/
    parts = PurePosixPath(path.replace("\\", "/")).parts
    if "test" in parts or "tests" in parts:
        return True
    return False


def _is_docs_or_test(path: str) -> bool:
    return _is_docs_only(path) or _is_test_only(path)


# ---------------------------------------------------------------------------
# Public classification function (importable for tests)
# ---------------------------------------------------------------------------


def classify(
    diff_stat: dict,
    files: list[str],
    risk_class: str,
) -> tuple[str, str, dict]:
    """Classify a diff into a review tier.

    Parameters
    ----------
    diff_stat:
        Mapping with integer keys "insertions" and "deletions".
    files:
        List of changed file paths (strings).
    risk_class:
        Pre-classified risk level: "High", "Medium", or "Low".

    Returns
    -------
    (tier, reason, signals)
        tier    — "light" | "standard" | "deep"
        reason  — human-readable rationale
        signals — dict of computed boolean/numeric signals
    """
    insertions = int(diff_stat.get("insertions", 0))
    deletions = int(diff_stat.get("deletions", 0))
    total_lines = insertions + deletions

    dependency_change = any(_is_dependency_file(f) for f in files)
    all_docs_or_tests = bool(files) and all(_is_docs_or_test(f) for f in files)

    signals: dict = {
        "total_lines": total_lines,
        "risk_class": risk_class,
        "dependency_change": dependency_change,
        "all_docs_or_tests": all_docs_or_tests,
    }

    # --- Tier 1: deep ---
    if risk_class == "High":
        return "deep", "risk_class is High", signals
    if total_lines > 200:
        return "deep", f"total_lines {total_lines} > 200", signals
    if dependency_change:
        dep_names = [os.path.basename(f) for f in files if _is_dependency_file(f)]
        return "deep", f"dependency file(s) changed: {dep_names}", signals

    # --- Tier 2: light ---
    if risk_class == "Low" and total_lines <= 10 and bool(files) and all_docs_or_tests:
        return "light", "Low risk, ≤10 lines, all docs/tests", signals

    # --- Tier 3: standard ---
    return "standard", "no deep/light conditions matched", signals


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------


def _emit(tier: str, reason: str, signals: dict) -> None:
    json.dump({"tier": tier, "reason": reason, "signals": signals}, sys.stdout)


def _fail_safe(reason: str) -> None:
    """Emit standard tier with a fail-safe explanation."""
    _emit(
        "standard",
        f"fail-safe (standard): {reason}",
        {
            "total_lines": 0,
            "risk_class": "unknown",
            "dependency_change": False,
            "all_docs_or_tests": False,
        },
    )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, ValueError) as exc:
        _fail_safe(f"stdin is not valid JSON ({exc})")
        return

    if not isinstance(data, dict):
        _fail_safe("stdin JSON is not an object")
        return

    # --- Validate risk_class ---
    risk_class = data.get("risk_class")
    if risk_class not in _VALID_RISK_CLASSES:
        _fail_safe(f"risk_class {risk_class!r} is not one of High/Medium/Low")
        return

    # --- Validate files ---
    files = data.get("files")
    if not isinstance(files, list):
        _fail_safe("files is missing or not a list")
        return

    # --- Validate diff_stat ---
    diff_stat = data.get("diff_stat")
    if not isinstance(diff_stat, dict):
        _fail_safe("diff_stat is missing or not an object")
        return
    try:
        int(diff_stat.get("insertions", 0))
        int(diff_stat.get("deletions", 0))
    except (TypeError, ValueError) as exc:
        _fail_safe(f"diff_stat contains non-numeric values ({exc})")
        return

    try:
        tier, reason, signals = classify(diff_stat, files, risk_class)
    except Exception as exc:  # noqa: BLE001
        traceback.print_exc(file=sys.stderr)
        _fail_safe(f"classify() raised {exc}")
        return

    _emit(tier, reason, signals)


if __name__ == "__main__":
    main()
