#!/usr/bin/env python3
"""Promote pending patterns in patterns.jsonl.

Daily batch classifier for the promotion pipeline:
  - learned / rejected entries older than 7 days -> promoted
  - doom_loop entries with same hash appearing 5+ times -> dismissed
  - entries newer than 7 days -> remain pending

Promoted entries are summarized into:
  ~/.claude/agent-memory/insights/promoted-{date}.md

Usage:
  python3 scripts/runtime/promote-patterns.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

PATTERNS_PATH = (
    Path.home() / ".claude" / "agent-memory" / "learnings" / "patterns.jsonl"
)
INSIGHTS_DIR = Path.home() / ".claude" / "agent-memory" / "insights"
PENDING_AGE_DAYS = 7
DOOM_LOOP_DISMISS_THRESHOLD = 5


def parse_timestamp(ts_str: str) -> datetime | None:
    """Parse ISO-8601 timestamp, returning None on failure."""
    if not ts_str:
        return None
    try:
        # Handle both +00:00 and Z suffixes
        cleaned = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(cleaned)
    except (ValueError, TypeError):
        return None


def load_entries(path: Path) -> list[dict]:
    """Load all JSONL entries, skipping malformed lines."""
    entries = []
    if not path.exists():
        return entries
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"WARN: skipping malformed line {line_num}", file=sys.stderr)
    return entries


def count_doom_loop_hashes(entries: list[dict]) -> Counter:
    """Count occurrences of each hash across all doom_loop entries."""
    counter: Counter = Counter()
    for entry in entries:
        if entry.get("type") == "doom_loop" and "hash" in entry:
            counter[entry["hash"]] += 1
    return counter


def classify_entries(
    entries: list[dict],
    now: datetime,
    doom_hash_counts: Counter,
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """Classify entries into promoted, dismissed, still-pending, and unchanged.

    Returns:
        (promoted, dismissed, still_pending, unchanged)
    """
    promoted = []
    dismissed = []
    still_pending = []
    unchanged = []

    cutoff = now - timedelta(days=PENDING_AGE_DAYS)

    for entry in entries:
        status = entry.get("promotion_status")

        # Already processed or no status field -> unchanged
        if status != "pending":
            unchanged.append(entry)
            continue

        entry_type = entry.get("type", "")
        ts = parse_timestamp(entry.get("timestamp", ""))

        # doom_loop with high-frequency hash -> dismissed
        if entry_type == "doom_loop":
            h = entry.get("hash")
            if (
                h is not None
                and doom_hash_counts.get(h, 0) >= DOOM_LOOP_DISMISS_THRESHOLD
            ):
                entry["promotion_status"] = "dismissed"
                dismissed.append(entry)
                continue

        # learned / rejected older than cutoff -> promoted
        if entry_type in ("learned", "rejected"):
            if ts is not None and ts < cutoff:
                entry["promotion_status"] = "promoted"
                promoted.append(entry)
                continue

        # New entries (within cutoff) or unclassified -> stay pending
        if ts is not None and ts >= cutoff:
            still_pending.append(entry)
        else:
            # Old entries of other types (e.g. skill_security_scan) -> stay pending
            # but if older than cutoff and not learned/rejected, just keep pending
            still_pending.append(entry)

    return promoted, dismissed, still_pending, unchanged


def write_entries(path: Path, entries: list[dict]) -> None:
    """Write entries back to JSONL atomically via temp file."""
    tmp_path = path.with_suffix(".jsonl.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    tmp_path.replace(path)


def generate_summary(promoted: list[dict], date_str: str) -> str:
    """Generate markdown summary of promoted entries."""
    lines = [
        f"# Promoted Patterns - {date_str}",
        "",
        f"Auto-promoted {len(promoted)} patterns from `patterns.jsonl`.",
        "",
    ]

    learned = [e for e in promoted if e.get("type") == "learned"]
    rejected = [e for e in promoted if e.get("type") == "rejected"]

    if learned:
        lines.append("## Learned")
        lines.append("")
        for entry in learned:
            scope = entry.get("scope", "unknown")
            detail = entry.get("generalized_detail") or entry.get("detail", "")
            lines.append(f"- **{scope}**: {detail}")
        lines.append("")

    if rejected:
        lines.append("## Rejected (Anti-Patterns)")
        lines.append("")
        for entry in rejected:
            scope = entry.get("scope", "unknown")
            detail = entry.get("generalized_detail") or entry.get("detail", "")
            lines.append(f"- **{scope}**: {detail}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Promote pending patterns")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without modifying files",
    )
    args = parser.parse_args()

    if not PATTERNS_PATH.exists():
        print(f"patterns.jsonl not found at {PATTERNS_PATH}", file=sys.stderr)
        sys.exit(1)

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")

    entries = load_entries(PATTERNS_PATH)
    if not entries:
        print("No entries in patterns.jsonl")
        return

    doom_hash_counts = count_doom_loop_hashes(entries)
    promoted, dismissed, still_pending, unchanged = classify_entries(
        entries, now, doom_hash_counts
    )

    print(f"Total entries:   {len(entries)}")
    print(f"  Promoted:      {len(promoted)}")
    print(f"  Dismissed:     {len(dismissed)}")
    print(f"  Still pending: {len(still_pending)}")
    print(f"  Unchanged:     {len(unchanged)}")

    if args.dry_run:
        print("\n[DRY RUN] No files modified.")
        if promoted:
            print("\nWould promote:")
            for e in promoted:
                print(f"  - [{e.get('type')}] {e.get('scope', e.get('hash', 'N/A'))}")
        if dismissed:
            print("\nWould dismiss:")
            for e in dismissed:
                h = e.get("hash")
                cnt = doom_hash_counts.get(h, "?")
                print(f"  - [doom_loop] hash={h} (count={cnt})")
        return

    # Entries were modified in-place, so re-serialize the original list
    write_entries(PATTERNS_PATH, entries)

    # Generate and write promoted summary
    if promoted:
        INSIGHTS_DIR.mkdir(parents=True, exist_ok=True)
        summary_path = INSIGHTS_DIR / f"promoted-{date_str}.md"
        # Append if file already exists (multiple runs per day)
        if summary_path.exists():
            with open(summary_path, "a", encoding="utf-8") as f:
                f.write("\n---\n\n")
                f.write(generate_summary(promoted, date_str))
        else:
            summary_path.write_text(
                generate_summary(promoted, date_str), encoding="utf-8"
            )
        print(f"Summary written to {summary_path}")

    print("Done.")


if __name__ == "__main__":
    main()
