#!/usr/bin/env python3
"""Track eval tuple saturation and flag retirement candidates.

A tuple is "saturated" when it has passed N consecutive eval runs.
Saturated tuples stop providing signal — they should be retired or mutated.

Usage:
    python3 eval-staleness.py [--results-dir eval/results]
                              [--tuples reviewer-eval-tuples.json]
                              [--saturation-threshold 5]
                              [--output staleness-report.md]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Regex to extract YYYY-MM-DD prefix from result filenames.
_DATE_PREFIX_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-")


def _extract_date(filename: str) -> str | None:
    """Return ISO date string from filename, or None if not found."""
    m = _DATE_PREFIX_RE.match(filename)
    return m.group(1) if m else None


def _scan_result_files(results_dir: Path) -> list[Path]:
    """Return result JSON files sorted by date prefix (chronological).

    Includes:
      - *-reviewer-eval.json
      - *-regression-eval.json

    Excludes:
      - baseline-eval.json
      - *-summary.md
    """
    patterns = ["*-reviewer-eval.json", "*-regression-eval.json"]
    found: list[Path] = []
    for pat in patterns:
        for p in results_dir.glob(pat):
            # Exclude files without a date prefix (e.g. baseline-eval.json)
            if _extract_date(p.name) is not None:
                found.append(p)

    # Sort by the date prefix string (lexicographic == chronological for ISO dates)
    found.sort(key=lambda p: _extract_date(p.name) or "")
    return found


def _load_results(path: Path) -> list[dict]:
    """Load a result JSON file and return its entries."""
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, list):
        return data
    return []


def _build_history(
    result_files: list[Path],
) -> dict[str, list[tuple[str, bool | None]]]:
    """Build per-tuple pass history from sorted result files.

    Returns:
        { eval_id: [(date, pass_bool), ...] }
        pass_bool is None for dry_run / error entries.
    """
    history: dict[str, list[tuple[str, bool | None]]] = {}
    for path in result_files:
        date = _extract_date(path.name) or "unknown"
        entries = _load_results(path)
        for entry in entries:
            eid = entry.get("eval_id", "")
            if not eid:
                continue
            pass_val: bool | None = entry.get("pass")
            # Normalise: treat None (dry_run) as None (skip), not False
            if pass_val is None:
                pass_val = None
            else:
                pass_val = bool(pass_val)
            history.setdefault(eid, []).append((date, pass_val))
    return history


def _pass_streak(history: list[tuple[str, bool | None]]) -> int:
    """Return the length of the trailing consecutive True streak.

    Entries with pass=None (dry_run/error) are ignored when computing the
    streak but do NOT break it.
    """
    streak = 0
    for _date, pval in reversed(history):
        if pval is None:
            continue
        if pval:
            streak += 1
        else:
            break
    return streak


def _pass_rate(history: list[tuple[str, bool | None]]) -> float:
    """Return overall pass rate across non-None entries."""
    definite = [pval for _, pval in history if pval is not None]
    if not definite:
        return 0.0
    return sum(definite) / len(definite)


def _last_fail_date(history: list[tuple[str, bool | None]]) -> str:
    """Return the most recent date of a failure, or 'never'."""
    for date, pval in reversed(history):
        if pval is False:
            return date
    return "never"


def _last_run_date(history: list[tuple[str, bool | None]]) -> str:
    """Return the most recent date this tuple appeared in any result."""
    if not history:
        return "never"
    return history[-1][0]


def _total_runs(history: list[tuple[str, bool | None]]) -> int:
    """Return count of appearances (including dry_run / error)."""
    return len(history)


def _load_tuples(tuples_path: Path) -> list[dict]:
    """Load eval tuples from JSON; return list of tuple dicts."""
    if not tuples_path.exists():
        return []
    with tuples_path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("tuples", [])


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def _md_row(*cells: str) -> str:
    return "| " + " | ".join(str(c) for c in cells) + " |"


def _pct(rate: float) -> str:
    return f"{rate:.0%}"


def generate_report(
    result_files: list[Path],
    history: dict[str, list[tuple[str, bool | None]]],
    tuples: list[dict],
    threshold: int,
) -> str:
    today = datetime.now().strftime("%Y-%m-%d")

    # Build per-tuple stats
    tuple_meta: dict[str, dict] = {t["id"]: t for t in tuples if "id" in t}

    saturated: list[dict] = []
    active: list[dict] = []
    orphaned: list[dict] = []

    all_seen_ids = set(history.keys())

    for eid, hist in history.items():
        streak = _pass_streak(hist)
        rate = _pass_rate(hist)
        runs = _total_runs(hist)
        meta = tuple_meta.get(eid, {})
        desc = meta.get("description", "")
        last_fail = _last_fail_date(hist)
        last_run = _last_run_date(hist)

        record = {
            "id": eid,
            "description": desc,
            "pass_streak": streak,
            "pass_rate": rate,
            "total_runs": runs,
            "last_run": last_run,
            "last_fail": last_fail,
        }

        if streak >= threshold:
            saturated.append(record)
        else:
            active.append(record)

    for t in tuples:
        eid = t["id"]
        if eid not in all_seen_ids:
            orphaned.append(
                {
                    "id": eid,
                    "description": t.get("description", ""),
                    "failure_mode": t.get("failure_mode", ""),
                }
            )

    # Sort sections for stable output
    saturated.sort(key=lambda r: r["id"])
    active.sort(key=lambda r: r["id"])
    orphaned.sort(key=lambda r: r["id"])

    lines: list[str] = [
        f"# Eval Staleness Report — {today}",
        "",
        f"**Result files scanned**: {len(result_files)}",
        f"**Tuples tracked**: {len(history)}",
        "",
    ]

    # --- Saturated ---
    lines.append("## Saturated (退役候補)")
    lines.append("")
    if saturated:
        lines.append(
            _md_row("ID", "Description", "Pass Streak", "Pass Rate", "Last Fail")
        )
        lines.append(
            _md_row("----", "-------------", "----------", "---------", "---------")
        )
        for r in saturated:
            lines.append(
                _md_row(
                    r["id"],
                    r["description"],
                    str(r["pass_streak"]),
                    _pct(r["pass_rate"]),
                    r["last_fail"],
                )
            )
    else:
        lines.append("_(なし)_")
    lines.append("")

    # --- Active ---
    lines.append("## Active (有効)")
    lines.append("")
    if active:
        lines.append(
            _md_row("ID", "Description", "Pass Streak", "Pass Rate", "Last Run")
        )
        lines.append(
            _md_row("----", "-------------", "----------", "---------", "--------")
        )
        for r in active:
            lines.append(
                _md_row(
                    r["id"],
                    r["description"],
                    str(r["pass_streak"]),
                    _pct(r["pass_rate"]),
                    r["last_run"],
                )
            )
    else:
        lines.append("_(なし)_")
    lines.append("")

    # --- Orphaned ---
    lines.append("## Orphaned (未実行)")
    lines.append("")
    if orphaned:
        lines.append(_md_row("ID", "Description", "Failure Mode"))
        lines.append(_md_row("----", "-------------", "------------"))
        for r in orphaned:
            lines.append(_md_row(r["id"], r["description"], r["failure_mode"]))
    else:
        lines.append("_(なし)_")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_arg_parser(script_dir: Path) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Track eval tuple saturation and flag retirement candidates."
    )
    parser.add_argument(
        "--results-dir",
        default=str(script_dir / "results"),
        help="Path to results directory (default: results/ next to script)",
    )
    parser.add_argument(
        "--tuples",
        default=str(script_dir / "reviewer-eval-tuples.json"),
        help="Path to tuples JSON for orphan detection",
    )
    parser.add_argument(
        "--saturation-threshold",
        type=int,
        default=5,
        help="Consecutive pass count to mark a tuple as saturated (default: 5)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path for report (default: stdout)",
    )
    return parser


def _write_report(report: str, output: str | None) -> None:
    if output:
        out_path = Path(output)
        out_path.write_text(report, encoding="utf-8")
        print(f"Report written to {out_path}")
    else:
        print(report, end="")


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    args = _build_arg_parser(script_dir).parse_args()

    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"No result files found (directory does not exist: {results_dir})")
        sys.exit(0)

    result_files = _scan_result_files(results_dir)
    if not result_files:
        print("No result files found")
        sys.exit(0)

    history = _build_history(result_files)
    tuples = _load_tuples(Path(args.tuples))
    report = generate_report(result_files, history, tuples, args.saturation_threshold)
    _write_report(report, args.output)


if __name__ == "__main__":
    main()
