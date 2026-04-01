#!/usr/bin/env python3
"""Contrastive trace analyzer — compare success/failure traces to extract strategies.

Glean "Trace Learning for Self-Improving Agents":
- Pair success/failure traces by task_type
- Identify divergence points (tool choice, sequence, params)
- Output situation-strategy-map candidates (human approval required)

Called by: /improve Step -0.5 (before Open Coding)
Output: stdout (strategy candidates or "no data" message)
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

LEARNINGS_DIR = Path.home() / ".claude" / "agent-memory" / "learnings"

# Consensus threshold: only learn from task_types with 3+ traces
MIN_TRACES_FOR_LEARNING = 3

# Timestamp proximity for cross-referencing errors with strategy-outcomes (seconds)
TIMESTAMP_PROXIMITY_SEC = 300  # 5 minutes


def load_strategy_outcomes() -> list[dict]:
    """Load strategy-outcomes.jsonl entries."""
    path = LEARNINGS_DIR / "strategy-outcomes.jsonl"
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


def load_errors() -> list[dict]:
    """Load errors.jsonl entries with parsed timestamps."""
    path = LEARNINGS_DIR / "errors.jsonl"
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


def analyze() -> list[dict]:
    """Run contrastive analysis across all task_types."""
    outcomes = load_strategy_outcomes()
    errors = load_errors()

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


def main() -> None:
    try:
        candidates = analyze()
        print(format_output(candidates))
    except Exception as e:
        print(f"## Contrastive Trace Analysis\n\nエラーが発生しました: {e}\n")


if __name__ == "__main__":
    main()
