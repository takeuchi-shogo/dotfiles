#!/usr/bin/env python3
"""patterns.jsonl daily rotation and deduplication.

Performs two operations:
  1. Archive: Move pending entries older than --days to gzip archive.
  2. Dedup:
     - FM-009 (doom_loop): Collapse entries with the same hash on the same
       calendar day (UTC) to a single entry (keep the last one).
     - FM-012 (exploration_spiral): Collapse entries on the same calendar day
       (UTC) to a single entry (keep the last one).

Usage:
  python3 rotate-patterns.py            # execute rotation
  python3 rotate-patterns.py --dry-run  # preview without writing
  python3 rotate-patterns.py --days 14  # custom age threshold
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path


PATTERNS_FILE = (
    Path.home() / ".claude" / "agent-memory" / "learnings" / "patterns.jsonl"
)
ARCHIVE_FILE = (
    Path.home() / ".claude" / "agent-memory" / "learnings" / "patterns.archive.jsonl.gz"
)
DEFAULT_DAYS = 30


def parse_timestamp(ts_str: str) -> datetime | None:
    """Parse ISO-8601 timestamp string to UTC datetime."""
    if not ts_str:
        return None
    try:
        # Handle both +00:00 and Z suffixes
        ts_str = ts_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def load_entries(path: Path) -> list[dict]:
    """Load JSONL entries, skipping malformed lines."""
    entries = []
    if not path.exists():
        return entries
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                # Preserve malformed lines as-is (wrapped in a marker dict)
                entries.append({"_raw_line": line, "_malformed": True})
    return entries


def entry_to_line(entry: dict) -> str:
    """Serialize an entry back to a JSONL line."""
    if entry.get("_malformed"):
        return entry["_raw_line"]
    return json.dumps(entry, ensure_ascii=False, separators=(",", ":"))


def archive_entries(entries: list[dict], archive_path: Path) -> None:
    """Append entries to gzip archive."""
    if not entries:
        return
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    mode = "ab"  # append binary
    with gzip.open(archive_path, mode) as gz:
        for entry in entries:
            line = entry_to_line(entry) + "\n"
            gz.write(line.encode("utf-8"))


def dedup_doom_loop(entries: list[dict]) -> list[dict]:
    """FM-009: Collapse doom_loop entries with the same hash on the same day.

    Keeps only the last entry per (date, hash) pair.
    """
    # Separate doom_loop entries from others
    doom_entries: list[tuple[int, dict]] = []
    other_indices: set[int] = set()

    for i, entry in enumerate(entries):
        if entry.get("_malformed"):
            other_indices.add(i)
            continue
        fm = entry.get("failure_mode", "")
        entry_type = entry.get("type", "")
        if fm == "FM-009" or entry_type == "doom_loop":
            doom_entries.append((i, entry))
        else:
            other_indices.add(i)

    # Group by (date, hash) -- keep last occurrence
    seen: dict[tuple[str, int | str], int] = {}
    duplicates: set[int] = set()

    for idx, entry in doom_entries:
        ts = parse_timestamp(entry.get("timestamp", ""))
        date_key = ts.strftime("%Y-%m-%d") if ts else "unknown"
        hash_val = entry.get("hash") or entry.get("data", {}).get("hash")
        if hash_val is None or date_key == "unknown":
            # No hash or no timestamp — skip dedup to avoid false grouping
            other_indices.add(idx)
            continue
        key = (date_key, hash_val)

        if key in seen:
            # Previous entry with same key is a duplicate
            duplicates.add(seen[key])
        seen[key] = idx

    # Rebuild: keep entries not in duplicates set
    result = []
    for i, entry in enumerate(entries):
        if i not in duplicates:
            result.append(entry)

    return result


def dedup_exploration_spiral(entries: list[dict]) -> list[dict]:
    """FM-012: Collapse exploration_spiral entries on the same day.

    Keeps only the last entry per date.
    """
    spiral_entries: list[tuple[int, dict]] = []
    other_indices: set[int] = set()

    for i, entry in enumerate(entries):
        if entry.get("_malformed"):
            other_indices.add(i)
            continue
        fm = entry.get("failure_mode", "")
        entry_type = entry.get("type", "")
        if fm == "FM-012" or entry_type == "exploration_spiral":
            spiral_entries.append((i, entry))
        else:
            other_indices.add(i)

    # Group by date -- keep last occurrence
    seen: dict[str, int] = {}
    duplicates: set[int] = set()

    for idx, entry in spiral_entries:
        ts = parse_timestamp(entry.get("timestamp", ""))
        if ts is None:
            # No timestamp — skip dedup to avoid false grouping
            continue
        date_key = ts.strftime("%Y-%m-%d")

        if date_key in seen:
            duplicates.add(seen[date_key])
        seen[date_key] = idx

    result = []
    for i, entry in enumerate(entries):
        if i not in duplicates:
            result.append(entry)

    return result


def rotate(patterns_path: Path, archive_path: Path, days: int, dry_run: bool) -> dict:
    """Run rotation and dedup. Returns stats dict."""
    entries = load_entries(patterns_path)
    total_before = len(entries)

    if total_before == 0:
        return {
            "total_before": 0,
            "total_after": 0,
            "archived": 0,
            "doom_loop_deduped": 0,
            "spiral_deduped": 0,
        }

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)

    # --- Phase 1: Separate old pending entries for archival ---
    to_archive: list[dict] = []
    kept: list[dict] = []

    for entry in entries:
        if entry.get("_malformed"):
            kept.append(entry)
            continue
        status = entry.get("promotion_status", "")
        ts = parse_timestamp(entry.get("timestamp", ""))

        if status == "pending" and ts and ts < cutoff:
            to_archive.append(entry)
        else:
            kept.append(entry)

    archived_count = len(to_archive)

    # --- Phase 2: Dedup doom_loop (FM-009) ---
    before_doom = len(kept)
    kept = dedup_doom_loop(kept)
    doom_deduped = before_doom - len(kept)

    # --- Phase 3: Dedup exploration_spiral (FM-012) ---
    before_spiral = len(kept)
    kept = dedup_exploration_spiral(kept)
    spiral_deduped = before_spiral - len(kept)

    total_after = len(kept)

    stats = {
        "total_before": total_before,
        "total_after": total_after,
        "archived": archived_count,
        "doom_loop_deduped": doom_deduped,
        "spiral_deduped": spiral_deduped,
    }

    if dry_run:
        return stats

    # --- Write results atomically ---
    # Archive old entries
    if to_archive:
        archive_entries(to_archive, archive_path)

    # Write kept entries atomically via temp file
    if kept or archived_count > 0 or doom_deduped > 0 or spiral_deduped > 0:
        fd, tmp_path = tempfile.mkstemp(
            dir=patterns_path.parent,
            prefix=".patterns-rotate-",
            suffix=".jsonl",
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmp_f:
                for entry in kept:
                    tmp_f.write(entry_to_line(entry) + "\n")
            shutil.move(tmp_path, patterns_path)
        except Exception:
            # Cleanup temp file on failure
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rotate and deduplicate patterns.jsonl"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_DAYS,
        help=f"Age threshold in days for archival (default: {DEFAULT_DAYS})",
    )
    parser.add_argument(
        "--patterns-file",
        type=Path,
        default=PATTERNS_FILE,
        help="Path to patterns.jsonl",
    )
    parser.add_argument(
        "--archive-file",
        type=Path,
        default=ARCHIVE_FILE,
        help="Path to archive file",
    )
    args = parser.parse_args()

    if not args.patterns_file.exists():
        print("patterns.jsonl not found — skipping")
        sys.exit(0)

    stats = rotate(
        patterns_path=args.patterns_file,
        archive_path=args.archive_file,
        days=args.days,
        dry_run=args.dry_run,
    )

    mode = "[DRY RUN] " if args.dry_run else ""
    print(f"{mode}patterns.jsonl rotation complete:")
    print(f"  Before:              {stats['total_before']} entries")
    print(f"  Archived (>{args.days}d):   {stats['archived']} entries")
    print(f"  Doom loop deduped:   {stats['doom_loop_deduped']} entries")
    print(f"  Spiral deduped:      {stats['spiral_deduped']} entries")
    print(f"  After:               {stats['total_after']} entries")

    removed = stats["archived"] + stats["doom_loop_deduped"] + stats["spiral_deduped"]
    if removed > 0:
        pct = (removed / stats["total_before"]) * 100
        print(f"  Reduction:           {removed} entries ({pct:.1f}%)")


if __name__ == "__main__":
    main()
