#!/usr/bin/env python3
"""
Dead-weight scan: detect rarely-referenced files in references/, skills/, agents/.

Algorithm:
  1. List all .md files in target directories
  2. Count references by stem name in CLAUDE.md, MEMORY.md, settings.json,
     and all .md files under skills/, agents/, references/ (cross-reference coverage)
  3. Check last-modified date
  4. Flag as dead-weight if: ref_count == 0 AND last_modified > 30 days ago

Output:
  - JSONL: ~/.claude/logs/dead-weight-{date}.jsonl
  - Stdout: table of flagged files with ref_count and age_days

Integration:
  - AutoEvolve Phase 1 reads this output to generate deletion proposals
  - Proposals go to /improve workflow, never auto-delete
"""

import json
import re
import time
from datetime import date, datetime, timedelta
from pathlib import Path

SCAN_DIRS = [
    Path.home() / ".claude" / "references",
    Path.home() / ".claude" / "skills",
    Path.home() / ".claude" / "agents",
]
DEAD_WEIGHT_AGE_DAYS = 30

# C2: module-level pattern cache to avoid recompiling per file
_REF_PATTERN_CACHE: dict[str, re.Pattern] = {}


def collect_reference_roots() -> list[Path]:
    """Collect all files that may reference other files."""
    # C1: use glob to find MEMORY.md under any project directory
    claude = Path.home() / ".claude"
    roots = [
        claude / "CLAUDE.md",
        claude / "settings.json",
    ]
    # Find MEMORY.md files by glob (supports any project directory)
    projects_dir = claude / "projects"
    if projects_dir.exists():
        roots += list(projects_dir.glob("*/memory/MEMORY.md"))
    roots += list(claude.glob("skills/**/*.md"))
    roots += list(claude.glob("agents/**/*.md"))
    roots += list(claude.glob("references/**/*.md"))
    return [r for r in roots if r.exists()]


def count_references(target: Path, roots: list[Path]) -> int:
    """Count how many root files reference the target file by stem name.

    Returns -1 (sentinel) when the stem is too short to measure reliably.
    """
    # C2: skip stems shorter than 4 chars — too many false positives
    stem = target.stem
    if len(stem) < 4:
        return -1

    pattern = _REF_PATTERN_CACHE.get(stem)
    if pattern is None:
        pattern = re.compile(r"\b" + re.escape(stem) + r"\b")
        _REF_PATTERN_CACHE[stem] = pattern

    count = 0
    for root in roots:
        try:
            content = root.read_text(errors="ignore")
            count += len(pattern.findall(content))
        except (IOError, UnicodeDecodeError, OSError):
            continue
    return count


def scan(roots: list[Path]) -> list[dict]:
    """Scan all target directories and return result records."""
    results = []
    cutoff = datetime.now() - timedelta(days=DEAD_WEIGHT_AGE_DAYS)
    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for f in sorted(scan_dir.rglob("*.md")):
            # C3: skip symlinks to avoid loops
            if f.is_symlink():
                continue
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
            except OSError:
                continue  # skip broken links or permission-denied
            age_days = (datetime.now() - mtime).days
            ref_count = count_references(f, roots)
            # C2: sentinel -1 means not measurable → do not flag as dead
            is_dead = ref_count >= 0 and ref_count == 0 and mtime < cutoff
            results.append(
                {
                    "file": str(f),
                    "stem": f.stem,
                    "ref_count": ref_count,
                    "age_days": age_days,
                    "is_dead_weight": is_dead,
                    "scanned_at": datetime.now().isoformat(),
                }
            )
    return results


def print_table(dead: list[dict]) -> None:
    """Print flagged files as a tabular summary."""
    if not dead:
        print("[dead-weight-scan] No dead-weight files detected.")
        return

    col_file = max(len(r["file"]) for r in dead)
    col_file = min(col_file, 80)  # cap column width
    header = f"{'FILE':<{col_file}}  {'REFS':>5}  {'AGE(d)':>7}"
    print(f"\n[dead-weight-scan] {len(dead)} files flagged:\n")
    print(header)
    print("-" * len(header))
    for r in dead:
        file_str = r["file"]
        if len(file_str) > col_file:
            file_str = "..." + file_str[-(col_file - 3) :]
        print(f"{file_str:<{col_file}}  {r['ref_count']:>5}  {r['age_days']:>7}")
    print()


def main() -> None:
    start = time.monotonic()

    roots = collect_reference_roots()
    results = scan(roots)
    dead = [r for r in results if r["is_dead_weight"]]

    elapsed = time.monotonic() - start

    # Write JSONL log
    log_path = Path.home() / ".claude" / "logs" / f"dead-weight-{date.today()}.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Summary line
    print(
        f"[dead-weight-scan] scanned {len(results)} files in {elapsed:.1f}s"
        f" | flagged={len(dead)} | log={log_path}"
    )

    print_table(dead)


if __name__ == "__main__":
    main()
