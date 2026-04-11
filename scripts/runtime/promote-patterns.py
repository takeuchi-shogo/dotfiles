#!/usr/bin/env python3
"""Promote pending patterns in patterns.jsonl.

Daily batch classifier for the promotion pipeline (evidence-based since 2026-04-11):
  - learned / rejected entries with recurrence evidence -> promoted
    * Primary:  same pattern observed in 2+ distinct scopes (contexts)
    * Fallback: same pattern observed 3+ times within a single scope
  - doom_loop entries with same hash appearing 5+ times -> dismissed
  - pending entries older than 30 days with no recurrence -> dismissed (stale)
  - entries that never recurred -> remain pending until they do or become stale

Rationale (2026-04-11 pepabo failure-learning-loop /absorb):
  The prior "age >= 7 days -> promoted" rule promoted every observation, defeating
  the "実戦で検証されたものだけ残す" (only promote patterns proven by recurrence)
  philosophy. Evidence-based promotion keeps the promoted insights ledger focused
  on patterns that actually repeat in practice.

Promoted entries are summarized into:
  ~/.claude/agent-memory/insights/promoted-{date}.md

Usage:
  python3 scripts/runtime/promote-patterns.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

PATTERNS_PATH = (
    Path.home() / ".claude" / "agent-memory" / "learnings" / "patterns.jsonl"
)
INSIGHTS_DIR = Path.home() / ".claude" / "agent-memory" / "insights"
DOOM_LOOP_DISMISS_THRESHOLD = 5
# Evidence-based promotion thresholds (pepabo 2026-04-11 philosophy shift)
RECURRENCE_MIN_DISTINCT_SCOPES = 2  # Primary: cross-context reproducibility
RECURRENCE_MIN_SAME_SCOPE_COUNT = 3  # Fallback: strong same-context recurrence
# Safety rail to prevent unbounded pending growth
STALE_DISMISS_DAYS = 30


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


def _pattern_key(entry: dict) -> str | None:
    """Stable key for grouping learned/rejected entries for recurrence detection.

    Prefers ``generalized_detail`` (the abstracted form written by the learner)
    over raw ``detail`` so that superficial wording differences cluster under
    the same semantic pattern. Returns ``None`` if no usable text exists; the
    entry is then treated as un-groupable and stays pending until it either
    acquires evidence or becomes stale.
    """
    text = (entry.get("generalized_detail") or entry.get("detail") or "").strip()
    if not text:
        return None
    # Normalize: NFKC (fullwidth/halfwidth, combining marks) + casefold, then
    # first 120 code points. NFKC is important for Japanese (全角→半角) and
    # Unicode combining sequences; casefold handles Turkish ``İ/ı`` edge cases
    # better than ``lower()``. The 120-char cap trades false-positive clustering
    # against false-negative fragmentation (tunable if recurrence rate changes).
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return normalized[:120]


def build_pattern_groups(entries: list[dict]) -> dict[str, dict]:
    """Group learned/rejected entries by pattern key for recurrence evidence.

    Returns a dict mapping pattern_key -> {"scopes": set[str], "count": int}.
    Previously-promoted entries are intentionally included: they still count
    as evidence for a pending entry observing the same pattern (a second
    scope seeing a promoted pattern reinforces cross-context reproducibility).
    """
    groups: dict[str, dict] = {}
    for entry in entries:
        if entry.get("type") not in ("learned", "rejected"):
            continue
        key = _pattern_key(entry)
        if key is None:
            continue
        g = groups.setdefault(key, {"scopes": set(), "count": 0})
        g["scopes"].add(entry.get("scope", ""))
        g["count"] += 1
    return groups


def classify_entries(
    entries: list[dict],
    now: datetime,
    doom_hash_counts: Counter,
    pattern_groups: dict[str, dict],
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """Classify entries into promoted, dismissed, still-pending, and unchanged.

    Promotion is evidence-based (pepabo 2026-04-11 philosophy):
      - Primary:  the same pattern was observed in >= RECURRENCE_MIN_DISTINCT_SCOPES
                  distinct scopes -> promoted (cross-context reproducibility).
      - Fallback: the same pattern was observed >= RECURRENCE_MIN_SAME_SCOPE_COUNT
                  times overall -> promoted (strong single-context recurrence).
      - Stale pending entries (> STALE_DISMISS_DAYS) with no recurrence ->
                  dismissed as noise; they never proved themselves in practice.

    Returns:
        (promoted, dismissed, still_pending, unchanged)
    """
    promoted = []
    dismissed = []
    still_pending = []
    unchanged = []

    stale_cutoff = now - timedelta(days=STALE_DISMISS_DAYS)

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

        # learned / rejected: promote only with recurrence evidence
        if entry_type in ("learned", "rejected"):
            key = _pattern_key(entry)
            group = pattern_groups.get(key) if key else None
            if group is not None:
                distinct_scopes = len(group["scopes"])
                total = group["count"]
                if (
                    distinct_scopes >= RECURRENCE_MIN_DISTINCT_SCOPES
                    or total >= RECURRENCE_MIN_SAME_SCOPE_COUNT
                ):
                    entry["promotion_status"] = "promoted"
                    entry["promotion_evidence"] = {
                        "distinct_scopes": distinct_scopes,
                        "total_occurrences": total,
                    }
                    promoted.append(entry)
                    continue

            # No recurrence yet. Dismiss if stale, otherwise keep waiting for evidence.
            if ts is not None and ts < stale_cutoff:
                entry["promotion_status"] = "dismissed"
                dismissed.append(entry)
                continue

        # Everything else: stay pending (new, insufficient evidence, or other types)
        still_pending.append(entry)

    return promoted, dismissed, still_pending, unchanged


def write_entries(path: Path, entries: list[dict]) -> None:
    """Write entries back to JSONL atomically via temp file.

    Ensures the parent directory exists (``mkdir -p``) before writing so that
    the first invocation on a fresh ``~/.claude/agent-memory/learnings/`` tree
    does not crash. Cleans up the temp file on write failure so a corrupted
    half-written JSONL never survives.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".jsonl.tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        tmp_path.replace(path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


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
    pattern_groups = build_pattern_groups(entries)
    promoted, dismissed, still_pending, unchanged = classify_entries(
        entries, now, doom_hash_counts, pattern_groups
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
                evidence = e.get("promotion_evidence", {})
                scopes = evidence.get("distinct_scopes", "?")
                total = evidence.get("total_occurrences", "?")
                scope = e.get("scope", e.get("hash", "N/A"))
                print(f"  - [{e.get('type')}] {scope} (scopes={scopes}, total={total})")
        if dismissed:
            print("\nWould dismiss:")
            for e in dismissed:
                etype = e.get("type", "?")
                if etype == "doom_loop":
                    h = e.get("hash")
                    cnt = doom_hash_counts.get(h, "?")
                    print(f"  - [doom_loop] hash={h} (count={cnt})")
                else:
                    print(
                        f"  - [{etype}] {e.get('scope', 'N/A')} "
                        f"(stale > {STALE_DISMISS_DAYS}d, no recurrence)"
                    )
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
