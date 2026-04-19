#!/usr/bin/env python3
"""Add `origin:` field to SKILL.md frontmatter across .config/claude/skills/.

origin classification:
  - external: listed in skills-lock.json
  - self:     everything else (locally authored)

Usage:
  python3 scripts/migrations/add-origin-to-skills.py [--dry-run] [--skills-dir PATH]

Exit codes:
  0  success (all skills processed, including no-op)
  1  malformed frontmatter or I/O error
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SKILLS_DIR = REPO_ROOT / ".config" / "claude" / "skills"
DEFAULT_LOCKFILE = REPO_ROOT / "skills-lock.json"


def load_external_names(lockfile: Path) -> set[str]:
    if not lockfile.is_file():
        print(f"[warn] lockfile not found: {lockfile}", file=sys.stderr)
        return set()
    data = json.loads(lockfile.read_text(encoding="utf-8"))
    skills = data.get("skills") or {}
    return set(skills.keys())


def split_frontmatter(text: str) -> tuple[list[str], str] | None:
    """Split YAML frontmatter from body. Returns (fm_lines, body) or None if absent."""
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return None
    lines = text.splitlines(keepends=True)
    if not lines or not lines[0].rstrip("\r\n") == "---":
        return None
    for idx in range(1, len(lines)):
        if lines[idx].rstrip("\r\n") == "---":
            return lines[1:idx], "".join(lines[idx:])
    return None


def has_origin(fm_lines: list[str]) -> bool:
    for line in fm_lines:
        stripped = line.lstrip()
        if stripped.startswith("origin:"):
            # ensure it's at top-level (no leading space)
            if not line.startswith((" ", "\t")):
                return True
    return False


def _is_top_level_key(line: str) -> bool:
    if not line or line[0] in (" ", "\t"):
        return False
    return ":" in line


def _end_of_description_block(fm_lines: list[str], start: int) -> int:
    """Return the index of the first line that is NOT part of the description block."""
    j = start + 1
    while j < len(fm_lines):
        line = fm_lines[j]
        if line.strip() == "":
            j += 1
            continue
        if _is_top_level_key(line):
            break
        j += 1
    return j


def _find_insert_position(fm_lines: list[str]) -> int:
    """Placement: after description block if present, else after name, else at end."""
    name_idx = -1
    for i, line in enumerate(fm_lines):
        if not _is_top_level_key(line):
            continue
        key = line.split(":", 1)[0]
        if key == "description":
            return _end_of_description_block(fm_lines, i)
        if key == "name" and name_idx < 0:
            name_idx = i
    if name_idx >= 0:
        return name_idx + 1
    return len(fm_lines)


def insert_origin(fm_lines: list[str], origin: str) -> list[str]:
    """Insert `origin: <origin>` at the top level of the frontmatter."""
    insert_at = _find_insert_position(fm_lines)
    new_line = f"origin: {origin}\n"
    return fm_lines[:insert_at] + [new_line] + fm_lines[insert_at:]


def process_skill(skill_md: Path, external_names: set[str], dry_run: bool) -> str:
    skill_name = skill_md.parent.name
    origin = "external" if skill_name in external_names else "self"
    text = skill_md.read_text(encoding="utf-8")
    parts = split_frontmatter(text)
    if parts is None:
        return f"skip (no frontmatter): {skill_name}"
    fm_lines, rest = parts
    if has_origin(fm_lines):
        return f"skip (origin exists): {skill_name}"
    new_fm = insert_origin(fm_lines, origin)
    new_text = "---\n" + "".join(new_fm) + rest
    if dry_run:
        return f"would add origin={origin}: {skill_name}"
    skill_md.write_text(new_text, encoding="utf-8")
    return f"added origin={origin}: {skill_name}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="preview changes only")
    parser.add_argument("--skills-dir", type=Path, default=DEFAULT_SKILLS_DIR)
    parser.add_argument("--lockfile", type=Path, default=DEFAULT_LOCKFILE)
    args = parser.parse_args()

    if not args.skills_dir.is_dir():
        print(f"[error] skills dir not found: {args.skills_dir}", file=sys.stderr)
        return 1

    external = load_external_names(args.lockfile)
    print(f"[info] external skills in lockfile: {len(external)}")

    skill_mds = sorted(args.skills_dir.glob("*/SKILL.md"))
    print(f"[info] SKILL.md files under {args.skills_dir}: {len(skill_mds)}")
    if not skill_mds:
        return 0

    added = skipped = 0
    for md in skill_mds:
        msg = process_skill(md, external, args.dry_run)
        print(msg)
        if msg.startswith(("added", "would add")):
            added += 1
        else:
            skipped += 1

    verb = "would add" if args.dry_run else "added"
    print(f"\n[done] {verb}: {added}, skipped: {skipped}, total: {len(skill_mds)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
