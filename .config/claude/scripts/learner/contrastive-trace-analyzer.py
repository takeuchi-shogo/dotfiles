#!/usr/bin/env python3
"""Contrastive trace analyzer — compare success/failure traces to extract strategies.

Glean "Trace Learning for Self-Improving Agents":
- Pair success/failure traces by task_type
- Identify divergence points (tool choice, sequence, params)
- Output situation-strategy-map candidates (human approval required)

Called by: /improve Step -0.5 (before Open Coding)
Output: stdout (strategy candidates or "no data" message)

Usage:
  # Default mode (analyze all available traces):
  python contrastive-trace-analyzer.py

  # Version-diff mode (compare two time periods):
  python contrastive-trace-analyzer.py --version-diff 2026-01-01 2026-04-01

  # With custom traces directory:
  python contrastive-trace-analyzer.py --traces-dir /path/to/learnings
  python contrastive-trace-analyzer.py \
      --version-diff 2026-01-01 2026-04-01 --traces-dir /path/to/learnings

Version-diff semantics:
  period_1 (old): entries with timestamp < v1 (represents "before" harness state)
  period_2 (new): entries with timestamp >= v1 AND timestamp < v2
  Patterns: [v2 new] appeared in new, [v1 only] resolved, [both] persistent
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

LEARNINGS_DIR = Path.home() / ".claude" / "agent-memory" / "learnings"

# Consensus threshold: only learn from task_types with 3+ traces
MIN_TRACES_FOR_LEARNING = 3

# Timestamp proximity for cross-referencing errors with strategy-outcomes (seconds)
TIMESTAMP_PROXIMITY_SEC = 300  # 5 minutes


def load_strategy_outcomes(traces_dir: Path | None = None) -> list[dict]:
    """Load strategy-outcomes.jsonl entries."""
    base = traces_dir if traces_dir is not None else LEARNINGS_DIR
    path = base / "strategy-outcomes.jsonl"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    entries = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def load_errors(traces_dir: Path | None = None) -> list[dict]:
    """Load errors.jsonl entries with parsed timestamps."""
    base = traces_dir if traces_dir is not None else LEARNINGS_DIR
    path = base / "errors.jsonl"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    entries = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
            entries.append(entry)
        except json.JSONDecodeError:
            continue
    return entries


def parse_timestamp(ts_str: str) -> datetime | None:
    """Parse ISO-8601 timestamp string."""
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def cross_reference_errors(
    outcomes: list[dict], errors: list[dict]
) -> dict[str, list[dict]]:
    """Cross-reference strategy-outcomes with errors by timestamp proximity.

    Returns dict mapping task_type to list of enriched outcome entries
    with 'has_nearby_errors' and 'nearby_errors' fields.
    """
    by_type: dict[str, list[dict]] = defaultdict(list)

    for outcome in outcomes:
        task_type = outcome.get("task_type", "")
        if not task_type:
            continue

        outcome_ts = parse_timestamp(outcome.get("timestamp", ""))
        enriched = {**outcome, "has_nearby_errors": False, "nearby_errors": []}

        if outcome_ts:
            for err in errors:
                err_ts = parse_timestamp(err.get("timestamp", ""))
                if (
                    err_ts
                    and abs((outcome_ts - err_ts).total_seconds())
                    < TIMESTAMP_PROXIMITY_SEC
                ):
                    enriched["has_nearby_errors"] = True
                    enriched["nearby_errors"].append(err)

        by_type[task_type].append(enriched)

    return by_type


def analyze_task_type(task_type: str, entries: list[dict]) -> list[dict]:
    """Analyze a single task_type for contrastive patterns.

    Returns list of strategy candidates.
    """
    if len(entries) < MIN_TRACES_FOR_LEARNING:
        return []

    # Use outcome field first, fall back to nearby_errors heuristic
    success = [
        e
        for e in entries
        if e.get("outcome") in ("clean_success", "recovery")
        and not e.get("has_nearby_errors")
    ]
    failure = [
        e
        for e in entries
        if e.get("outcome") == "failure" or e.get("has_nearby_errors")
    ]

    if not failure:
        return []  # No failures to contrast against

    candidates = []

    # Extract error patterns from failure sessions
    error_patterns: dict[str, int] = defaultdict(int)
    for entry in failure:
        for err in entry.get("nearby_errors", []):
            msg = err.get("message", "")
            cmd = err.get("command", "")
            pattern = err.get("failure_pattern", "")
            key = pattern or msg[:80] or cmd[:80]
            if key:
                error_patterns[key] += 1

    # Generate candidates from recurring error patterns
    for pattern, count in error_patterns.items():
        if count >= 2:  # Pattern seen in 2+ failure sessions
            candidates.append(
                {
                    "situation": f"{task_type} タスクで '{pattern}' エラーが発生",
                    "strategy": (
                        f"同一 task_type の成功セッション"
                        f" ({len(success)} 件) のアプローチを参照"
                    ),
                    "evidence": (
                        f"failure {len(failure)}"
                        f" / success {len(success)}"
                        f" / total {len(entries)}"
                    ),
                    "error_pattern": pattern,
                    "task_type": task_type,
                }
            )

    return candidates


def analyze(traces_dir: Path | None = None) -> list[dict]:
    """Run contrastive analysis across all task_types."""
    outcomes = load_strategy_outcomes(traces_dir)
    errors = load_errors(traces_dir)

    if not outcomes:
        return []

    by_type = cross_reference_errors(outcomes, errors)

    all_candidates = []
    for task_type, entries in by_type.items():
        candidates = analyze_task_type(task_type, entries)
        all_candidates.extend(candidates)

    return all_candidates


def format_output(candidates: list[dict]) -> str:
    """Format candidates as markdown for human review."""
    if not candidates:
        return (
            "## Contrastive Trace Analysis\n\n"
            "分析対象なし"
            "（失敗トレースが不足、または合意閾値未達）。\n"
        )

    lines = [
        "## Contrastive Trace Analysis",
        "",
        f"**候補数**: {len(candidates)}",
        "",
        "以下は situation-strategy-map への追加候補です（人間の承認が必要）:",
        "",
        "| 状況 | 推奨戦略 | エビデンス |",
        "|------|----------|-----------|",
    ]
    for c in candidates:
        lines.append(f"| {c['situation']} | {c['strategy']} | {c['evidence']} |")

    lines.append("")
    return "\n".join(lines)


def _parse_date_boundary(date_str: str) -> datetime:
    """Parse YYYY-MM-DD date string as UTC-aware datetime (start of day)."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.replace(tzinfo=timezone.utc)


def filter_by_date_range(
    entries: list[dict], start: str | None, end: str | None
) -> list[dict]:
    """Filter entries by timestamp range [start, end).

    Args:
        entries: List of dicts with a 'timestamp' field.
        start: ISO date string YYYY-MM-DD (inclusive lower bound), or None for no limit.
        end: ISO date string YYYY-MM-DD (exclusive upper bound), or None for no limit.

    Returns:
        Filtered list of entries whose timestamp falls within [start, end).
    """
    start_dt = _parse_date_boundary(start) if start else None
    end_dt = _parse_date_boundary(end) if end else None

    result = []
    for entry in entries:
        ts = parse_timestamp(entry.get("timestamp", ""))
        if ts is None:
            continue
        # Normalize to UTC-aware for comparison
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        if start_dt is not None and ts < start_dt:
            continue
        if end_dt is not None and ts >= end_dt:
            continue
        result.append(entry)
    return result


def _run_analysis_on_entries(outcomes: list[dict], errors: list[dict]) -> list[dict]:
    """Run cross_reference_errors + analyze_task_type on a given set of entries."""
    if not outcomes:
        return []
    by_type = cross_reference_errors(outcomes, errors)
    candidates = []
    for task_type, entries in by_type.items():
        candidates.extend(analyze_task_type(task_type, entries))
    return candidates


def format_version_diff_output(
    v1_candidates: list[dict],
    v2_candidates: list[dict],
    v1: str,
    v2: str,
) -> str:
    """Format diff report between two time periods.

    Classifies patterns as:
      [v2 new]  — appeared in period_2 (v1..v2) but not period_1 (..v1)
      [v1 only] — present in period_1 only (resolved in new period)
      [both]    — persistent issues across both periods
    """
    v1_keys = {c["error_pattern"] for c in v1_candidates}
    v2_keys = {c["error_pattern"] for c in v2_candidates}

    v2_new = [c for c in v2_candidates if c["error_pattern"] not in v1_keys]
    v1_only = [c for c in v1_candidates if c["error_pattern"] not in v2_keys]
    both = [c for c in v2_candidates if c["error_pattern"] in v1_keys]

    lines = [
        "## Contrastive Trace Analysis — Version Diff",
        "",
        f"**比較期間**: period_1 = ~{v1} / period_2 = {v1}~{v2}",
        f"**period_1 候補数**: {len(v1_candidates)} | "
        f"**period_2 候補数**: {len(v2_candidates)}",
        "",
    ]

    def _append_section(title: str, tag: str, items: list[dict]) -> None:
        lines.append(f"### {title} ({len(items)} 件)")
        if not items:
            lines.append("_なし_")
            lines.append("")
            return
        lines.append("")
        lines.append("| タグ | 状況 | エビデンス |")
        lines.append("|-----|------|-----------|")
        for c in items:
            lines.append(f"| {tag} | {c['situation']} | {c['evidence']} |")
        lines.append("")

    _append_section("新規パターン (period_2 のみ)", "[v2 new]", v2_new)
    _append_section("解消パターン (period_1 のみ)", "[v1 only]", v1_only)
    _append_section("継続パターン (両期間)", "[both]", both)

    return "\n".join(lines)


def version_diff(v1: str, v2: str, traces_dir: Path) -> str:
    """Compare strategy candidates between two time periods.

    period_1 (old): entries with timestamp < v1
    period_2 (new): entries with timestamp >= v1 AND timestamp < v2

    Args:
        v1: Start of new period / end of old period (YYYY-MM-DD).
        v2: End of new period (YYYY-MM-DD, exclusive).
        traces_dir: Directory containing strategy-outcomes.jsonl and errors.jsonl.

    Returns:
        Formatted markdown diff report.
    """
    all_outcomes = load_strategy_outcomes(traces_dir)
    all_errors = load_errors(traces_dir)

    p1_outcomes = filter_by_date_range(all_outcomes, None, v1)
    p1_errors = filter_by_date_range(all_errors, None, v1)

    p2_outcomes = filter_by_date_range(all_outcomes, v1, v2)
    p2_errors = filter_by_date_range(all_errors, v1, v2)

    if not p1_outcomes and not p2_outcomes:
        return (
            "## Contrastive Trace Analysis — Version Diff\n\n"
            f"データ不足: period_1 ({len(p1_outcomes)} 件) / "
            f"period_2 ({len(p2_outcomes)} 件)。"
            "分析を実行できません。\n"
        )

    v1_candidates = _run_analysis_on_entries(p1_outcomes, p1_errors)
    v2_candidates = _run_analysis_on_entries(p2_outcomes, p2_errors)

    if not v1_candidates and not v2_candidates:
        return (
            "## Contrastive Trace Analysis — Version Diff\n\n"
            "両期間ともに候補なし（失敗トレース不足または合意閾値未達）。\n"
        )

    return format_version_diff_output(v1_candidates, v2_candidates, v1, v2)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Contrastive trace analyzer for strategy candidate extraction.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version-diff",
        nargs=2,
        metavar=("V1", "V2"),
        help=(
            "Compare two time periods. "
            "V1/V2 are YYYY-MM-DD dates. "
            "period_1 = before V1, period_2 = V1..V2."
        ),
    )
    parser.add_argument(
        "--traces-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help=(
            "Directory containing strategy-outcomes.jsonl and errors.jsonl. "
            f"Default: {LEARNINGS_DIR}"
        ),
    )
    return parser


def main() -> None:
    parser = _build_arg_parser()
    args = parser.parse_args()

    traces_dir: Path | None = args.traces_dir
    if traces_dir is not None:
        traces_dir = traces_dir.expanduser().resolve()

    try:
        if args.version_diff:
            v1, v2 = args.version_diff
            effective_dir = traces_dir if traces_dir is not None else LEARNINGS_DIR
            print(version_diff(v1, v2, effective_dir))
        else:
            candidates = analyze(traces_dir)
            print(format_output(candidates))
    except Exception as e:
        print(f"## Contrastive Trace Analysis\n\nエラーが発生しました: {e}\n")


if __name__ == "__main__":
    main()
