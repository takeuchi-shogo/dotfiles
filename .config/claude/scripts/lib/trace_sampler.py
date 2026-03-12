"""Trace sampler for manual Open Coding in /improve Step 0.

Reads traces from learnings/*.jsonl, samples them with category balance,
and formats for human review.

Usage:
    from lib.trace_sampler import sample_recent_traces, format_for_review
    traces = sample_recent_traces(n=20)
    print(format_for_review(traces))
"""

from __future__ import annotations

import json
import os
from pathlib import Path

EXCLUDED_FILES = {"review-findings.jsonl", "review-feedback.jsonl"}
CATEGORIES = ("error", "quality", "pattern", "correction")
MESSAGE_TRUNCATE_LEN = 60


def _get_data_dir() -> Path:
    """Return the data directory, respecting AUTOEVOLVE_DATA_DIR for tests."""
    return Path(
        os.environ.get(
            "AUTOEVOLVE_DATA_DIR",
            os.path.join(os.environ.get("HOME", ""), ".claude", "agent-memory"),
        )
    )


def _read_all_traces() -> list[dict]:
    """Read all traces from learnings/*.jsonl, excluding review files."""
    learnings_dir = _get_data_dir() / "learnings"
    if not learnings_dir.exists():
        return []

    traces: list[dict] = []
    for jsonl_file in sorted(learnings_dir.glob("*.jsonl")):
        if jsonl_file.name in EXCLUDED_FILES:
            continue
        try:
            with open(jsonl_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            traces.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except OSError:
            continue
    return traces


def sample_recent_traces(n: int = 20) -> list[dict]:
    """Sample the most recent n traces with category-balanced selection.

    Reads all learnings/*.jsonl (excluding review-findings and review-feedback),
    then samples evenly across categories (error, quality, pattern, correction).
    If a category has fewer items than its quota, the remainder is redistributed.

    Args:
        n: Maximum number of traces to return.

    Returns:
        List of trace dicts, sorted by timestamp descending.
    """
    all_traces = _read_all_traces()
    if not all_traces:
        return []

    # Sort all traces by timestamp descending (most recent first)
    all_traces.sort(key=lambda t: t.get("timestamp", ""), reverse=True)

    # Group by category
    by_category: dict[str, list[dict]] = {}
    for trace in all_traces:
        cat = trace.get("category", "unknown")
        by_category.setdefault(cat, []).append(trace)

    # Balanced sampling: distribute n evenly across present categories
    present_categories = [c for c in CATEGORIES if c in by_category]
    # Also include any unexpected categories
    for cat in by_category:
        if cat not in present_categories:
            present_categories.append(cat)

    if not present_categories:
        return []

    sampled: list[dict] = []
    remaining = n

    # Round-robin allocation
    quota_per_cat = max(1, n // len(present_categories))
    leftover_cats: list[str] = []

    for cat in present_categories:
        available = by_category.get(cat, [])
        take = min(quota_per_cat, len(available), remaining)
        sampled.extend(available[:take])
        remaining -= take
        if len(available) > take:
            leftover_cats.append(cat)

    # Fill remaining quota from categories that still have items
    if remaining > 0 and leftover_cats:
        for cat in leftover_cats:
            if remaining <= 0:
                break
            already_taken = quota_per_cat
            available = by_category.get(cat, [])
            extra = available[already_taken : already_taken + remaining]
            sampled.extend(extra)
            remaining -= len(extra)

    # Sort final result by timestamp descending
    sampled.sort(key=lambda t: t.get("timestamp", ""), reverse=True)
    return sampled


def sample_unclassified_traces() -> list[dict]:
    """Extract traces where failure_mode is empty or missing.

    Used for inductive verification of the failure mode taxonomy.

    Returns:
        List of trace dicts with empty/missing failure_mode.
    """
    all_traces = _read_all_traces()
    return [t for t in all_traces if not t.get("failure_mode", "")]


def _truncate(text: str, max_len: int = MESSAGE_TRUNCATE_LEN) -> str:
    """Truncate text to max_len, appending '...' if truncated."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def format_for_review(traces: list[dict]) -> str:
    """Format traces as a Markdown table for human review.

    Columns: #, timestamp, category, failure_mode, importance, message/rule

    Args:
        traces: List of trace dicts to format.

    Returns:
        Markdown table string.
    """
    header = "| # | timestamp | category | failure_mode | importance | message |"
    separator = "|---|-----------|----------|--------------|------------|---------|"
    lines = [header, separator]

    for i, trace in enumerate(traces, 1):
        ts = trace.get("timestamp", "")
        # Shorten ISO timestamp to datetime portion
        if "T" in ts:
            ts = ts.split("T")[0] + " " + ts.split("T")[1][:8]
        category = trace.get("category", "")
        fm = trace.get("failure_mode", "")
        importance = trace.get("importance", "")
        message = trace.get("message", trace.get("rule", ""))
        message = _truncate(str(message))

        lines.append(f"| {i} | {ts} | {category} | {fm} | {importance} | {message} |")

    return "\n".join(lines)
