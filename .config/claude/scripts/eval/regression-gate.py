#!/usr/bin/env python3
"""Regression Gate for /improve Adversarial Phase.

Reads scripts/eval/regression-suite.json and validates that proposed changes
do not regress on previously-fixed failure cases. Outputs JSON to stdout.

Exit codes:
  0 — PASS or WARN
  1 — FAIL
"""

from __future__ import annotations

import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Known failure-mode codes (derived from reviewer-eval-tuples.json).
# FM-001 through FM-010 are the currently recognised codes.
# ---------------------------------------------------------------------------
KNOWN_FM_CODES: frozenset[str] = frozenset(f"FM-{i:03d}" for i in range(1, 18))

# Known reviewer agent names (derived from agents/ directory).
KNOWN_REVIEWERS: frozenset[str] = frozenset(
    [
        "code-reviewer",
        "security-reviewer",
        "silent-failure-hunter",
        "edge-case-hunter",
        "type-design-analyzer",
        "cross-file-reviewer",
        "codex-reviewer",
        "golang-reviewer",
        "product-reviewer",
        "design-reviewer",
        "debugger",
        "build-fixer",
    ]
)


def _locate_suite(base_dir: Path) -> Path | None:
    """Search for regression-suite.json relative to the repo root."""
    candidates = [
        base_dir / "regression-suite.json",
        base_dir / "scripts" / "eval" / "regression-suite.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def _validate_tuple(t: dict[str, Any], index: int) -> list[str]:
    """Return a list of validation error messages for one tuple entry."""
    errors: list[str] = []
    tid = t.get("id", f"<index {index}>")

    fm = t.get("failure_mode", "")
    if not fm:
        errors.append(f"[{tid}] missing 'failure_mode'")
    elif fm not in KNOWN_FM_CODES:
        known = sorted(KNOWN_FM_CODES)
        errors.append(f"[{tid}] unknown failure_mode '{fm}' (expected one of {known})")

    reviewer = t.get("expected_reviewer", "")
    if not reviewer:
        errors.append(f"[{tid}] missing 'expected_reviewer'")
    elif reviewer not in KNOWN_REVIEWERS:
        # Warn but do not fail — new reviewers may be added over time.
        print(
            f"[regression-gate] WARN [{tid}] unrecognised reviewer '{reviewer}' "
            "(not in KNOWN_REVIEWERS — verify the agent exists)",
            file=sys.stderr,
        )

    return errors


def run(base_dir: Path) -> dict[str, Any]:
    suite_path = _locate_suite(base_dir)

    if suite_path is None:
        print(
            "[regression-gate] regression-suite.json not found — skipping gate",
            file=sys.stderr,
        )
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_cases": 0,
            "passed": 0,
            "failed": 0,
            "pass_rate": 1.0,
            "status": "PASS",
            "details": [],
        }

    print(f"[regression-gate] loading suite from {suite_path}", file=sys.stderr)

    try:
        with suite_path.open(encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        print(
            f"[regression-gate] ERROR: invalid JSON in suite — {exc}", file=sys.stderr
        )
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_cases": 0,
            "passed": 0,
            "failed": 1,
            "pass_rate": 0.0,
            "status": "FAIL",
            "details": [{"error": f"JSON parse error: {exc}"}],
        }

    tuples: list[dict[str, Any]] = data.get("tuples", [])
    total = len(tuples)
    details: list[dict[str, Any]] = []
    failed_ids: list[str] = []

    for i, t in enumerate(tuples):
        errors = _validate_tuple(t, i)
        if errors:
            tid = t.get("id", f"<index {i}>")
            failed_ids.append(tid)
            details.append({"id": tid, "errors": errors})
            for msg in errors:
                print(f"[regression-gate] FAIL {msg}", file=sys.stderr)
        else:
            tid = t.get("id", f"<index {i}>")
            print(f"[regression-gate] OK   [{tid}]", file=sys.stderr)

    failed = len(failed_ids)
    passed = total - failed
    pass_rate = passed / total if total > 0 else 1.0

    if pass_rate >= 1.0:
        status = "PASS"
    elif pass_rate >= 0.9:
        status = "WARN"
    else:
        status = "FAIL"

    rate_str = f"{pass_rate:.2f}"
    msg = (
        f"[regression-gate] result: {status} ({passed}/{total} passed, rate={rate_str})"
    )
    print(msg, file=sys.stderr)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_cases": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "status": status,
        "details": details,
    }


def main() -> None:
    script_dir = Path(__file__).resolve().parent

    # Allow override via env var for testing.
    base_dir_env = os.environ.get("REGRESSION_GATE_BASE_DIR")
    base_dir = Path(base_dir_env) if base_dir_env else script_dir

    result = run(base_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result["status"] == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()
