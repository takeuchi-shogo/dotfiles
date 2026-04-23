#!/usr/bin/env python3
"""
Doc status audit: scan docs/research/, docs/plans/, .config/claude/references/
for missing `status: active | reference | archive` frontmatter, and optionally
auto-infer and write the status.

Usage:
  python3 scripts/lifecycle/doc-status-audit.py --dry-run
  python3 scripts/lifecycle/doc-status-audit.py --fix
  python3 scripts/lifecycle/doc-status-audit.py --fix --dir docs/research

Algorithm:
  1. For each target .md file:
     - Parse existing frontmatter (if any)
     - If `status` already set, skip
  2. Infer status:
     a. Path contains /archive/ or /done/ -> archive
     b. Referenced from MEMORY.md/CLAUDE.md/_index.md -> active
     c. Age > 90 days + referenced -> reference
     d. Age > 90 days + not referenced -> archive
     e. Age <= 90 days -> active (fallback)
  3. Output report (stdout); if --fix, write frontmatter.

Output:
  - Stdout: per-file status table
  - JSONL: ~/.claude/logs/doc-status-audit-{date}.jsonl
"""

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DIRS = [
    REPO_ROOT / "docs" / "research",
    REPO_ROOT / "docs" / "plans",
    REPO_ROOT / ".config" / "claude" / "references",
]
AGE_THRESHOLD_DAYS = 90

REFERENCE_ROOTS = [
    REPO_ROOT / ".config" / "claude" / "CLAUDE.md",
    REPO_ROOT / "CLAUDE.md",
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / ".codex" / "AGENTS.md",
    REPO_ROOT / "docs" / "research" / "_index.md",
]

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_REF_PATTERN_CACHE: dict[str, re.Pattern] = {}


def parse_frontmatter(text: str) -> tuple[dict[str, str] | None, int]:
    """Return (fields, end_offset) for YAML frontmatter, or (None, 0) if absent.

    Only parses simple key: value lines (no nested structures)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, 0
    fields: dict[str, str] = {}
    for line in m.group(1).splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields, m.end()


def collect_memory_roots() -> list[Path]:
    """Include project MEMORY.md files for reference counting."""
    roots = list(REFERENCE_ROOTS)
    claude_projects = Path.home() / ".claude" / "projects"
    if claude_projects.exists():
        roots += list(claude_projects.glob("*/memory/MEMORY.md"))
    # Also add sibling _index.md files (plans/_index.md once created)
    for d in DEFAULT_DIRS:
        idx = d / "_index.md"
        if idx.exists():
            roots.append(idx)
    return [p for p in roots if p.exists()]


def is_referenced(target: Path, roots: list[Path]) -> bool:
    stem = target.stem
    if len(stem) < 4:
        return False
    pattern = _REF_PATTERN_CACHE.get(stem)
    if pattern is None:
        pattern = re.compile(r"\b" + re.escape(stem) + r"\b")
        _REF_PATTERN_CACHE[stem] = pattern
    for root in roots:
        try:
            if pattern.search(root.read_text(errors="ignore")):
                return True
        except (IOError, OSError, UnicodeDecodeError):
            continue
    return False


def infer_status(path: Path, mtime: datetime, roots: list[Path]) -> str:
    parts = {p.name for p in path.parents}
    if "archive" in parts or "done" in parts:
        return "archive"
    # references/ 配下は骨子・長期参照の性質なので reference を優先
    # (ただし _index や MEMORY から参照されていて最近更新なら active に昇格)
    in_references = "references" in parts and ".config" in {
        p.name for p in path.parents
    }
    age_days = (datetime.now() - mtime).days
    referenced = is_referenced(path, roots)
    if in_references:
        # MEMORY/CLAUDE.md から参照 + 30日以内の更新 → active
        if referenced and age_days <= 30:
            return "active"
        return "reference"
    if referenced and age_days <= AGE_THRESHOLD_DAYS:
        return "active"
    if referenced:
        return "reference"
    if age_days > AGE_THRESHOLD_DAYS:
        return "archive"
    return "active"


def write_frontmatter(path: Path, status: str, today: str) -> None:
    text = path.read_text(encoding="utf-8")
    fields, end = parse_frontmatter(text)
    if fields is None:
        new_fm = f"---\nstatus: {status}\nlast_reviewed: {today}\n---\n\n"
        path.write_text(new_fm + text, encoding="utf-8")
        return
    if "status" in fields:
        return
    # Inject status + last_reviewed into existing frontmatter
    before = text[:end]
    after = text[end:]
    # Remove trailing --- from `before`, append new fields, re-close
    fm_body = before.rstrip().rstrip("-").rstrip()
    new_fm = fm_body + f"\nstatus: {status}\nlast_reviewed: {today}\n---\n"
    path.write_text(new_fm + after, encoding="utf-8")


def scan(
    dirs: list[Path],
    fix: bool,
    roots: list[Path],
) -> list[dict]:
    today = date.today().isoformat()
    results: list[dict] = []
    for d in dirs:
        if not d.exists():
            continue
        for f in sorted(d.rglob("*.md")):
            if f.is_symlink():
                continue
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
            except OSError:
                continue
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            fields, _ = parse_frontmatter(text)
            has_status = bool(fields and fields.get("status"))
            inferred = None if has_status else infer_status(f, mtime, roots)
            action = "skip" if has_status else ("apply" if fix else "propose")
            if action == "apply" and inferred:
                write_frontmatter(f, inferred, today)
            results.append(
                {
                    "file": str(f.relative_to(REPO_ROOT)),
                    "current_status": (fields or {}).get("status"),
                    "inferred_status": inferred,
                    "action": action,
                    "age_days": (datetime.now() - mtime).days,
                }
            )
    return results


def print_summary(results: list[dict]) -> None:
    total = len(results)
    skipped = sum(1 for r in results if r["action"] == "skip")
    applied = sum(1 for r in results if r["action"] == "apply")
    proposed = sum(1 for r in results if r["action"] == "propose")

    by_status: dict[str, int] = {}
    for r in results:
        s = r["inferred_status"] or r["current_status"] or "unknown"
        by_status[s] = by_status.get(s, 0) + 1

    print(
        f"[doc-status-audit] scanned={total} skip={skipped} "
        f"apply={applied} propose={proposed}"
    )
    print("[doc-status-audit] status distribution:")
    for k in ("active", "reference", "archive", "unknown"):
        if k in by_status:
            print(f"  {k:<10} {by_status[k]}")
    if proposed > 0:
        print("\n[doc-status-audit] proposed changes (use --fix to apply):")
        for r in results:
            if r["action"] == "propose":
                print(
                    f"  {r['inferred_status']:<10} {r['file']} (age={r['age_days']}d)"
                )


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--fix", action="store_true", help="apply inferred status")
    p.add_argument("--dry-run", action="store_true", help="report only (default)")
    p.add_argument(
        "--dir", type=Path, action="append", help="override scan directories"
    )
    args = p.parse_args()

    dirs = args.dir if args.dir else DEFAULT_DIRS
    dirs = [d if d.is_absolute() else (REPO_ROOT / d) for d in dirs]

    roots = collect_memory_roots()
    results = scan(dirs, args.fix, roots)

    log_path = (
        Path.home() / ".claude" / "logs" / f"doc-status-audit-{date.today()}.jsonl"
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    print_summary(results)
    print(f"[doc-status-audit] log={log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
