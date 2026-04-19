"""Parse `platforms:` from SKILL.md frontmatter and emit sharing lists.

The `platforms:` field in a SKILL.md frontmatter is a YAML sequence that lists
the agents this skill should be shared with:

    platforms: [claude, codex, agents, cursor]

Defaults when the field is absent:
  - skills under `.config/claude/skills/`  -> [claude]
  - skills under `.agents/skills/`          -> [agents]

Usage:
  python3 -m scripts.lib.skill_platforms --source claude --needs codex
  python3 scripts/lib/skill_platforms.py --source claude --needs codex

Output: one skill name per line (sorted), suitable for bash `$(…)` use.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_SKILLS_DIR = REPO_ROOT / ".config" / "claude" / "skills"
AGENTS_SKILLS_DIR = REPO_ROOT / ".agents" / "skills"

SOURCE_DIRS = {
    "claude": CLAUDE_SKILLS_DIR,
    "agents": AGENTS_SKILLS_DIR,
}

DEFAULT_PLATFORMS = {
    "claude": ["claude"],
    "agents": ["agents"],
}

_PLATFORMS_LINE = re.compile(r"^platforms:\s*(.+?)\s*$", re.IGNORECASE)


def _extract_frontmatter(text: str) -> str | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else None


def _parse_inline_sequence(raw: str) -> list[str]:
    """Parse `[claude, codex]` style inline YAML list. Strips quotes/whitespace."""
    if not (raw.startswith("[") and raw.endswith("]")):
        return []
    inner = raw[1:-1].strip()
    if not inner:
        return []
    return [item.strip().strip("'\"") for item in inner.split(",") if item.strip()]


def _parse_block_sequence(lines: list[str], start: int) -> list[str]:
    """Parse YAML block list immediately following `platforms:` line."""
    items: list[str] = []
    for line in lines[start + 1 :]:
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip().strip("'\""))
            continue
        if stripped == "" or stripped.startswith("#"):
            continue
        break
    return items


def read_platforms(skill_md: Path, default: list[str]) -> list[str]:
    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError:
        return list(default)
    fm = _extract_frontmatter(text)
    if fm is None:
        return list(default)
    lines = fm.splitlines()
    for i, line in enumerate(lines):
        match = _PLATFORMS_LINE.match(line)
        if not match:
            continue
        rest = match.group(1)
        if rest.startswith("["):
            return _parse_inline_sequence(rest) or list(default)
        if rest == "":
            return _parse_block_sequence(lines, i) or list(default)
    return list(default)


def list_skills_needing(source: str, needs: str) -> list[str]:
    base = SOURCE_DIRS.get(source)
    if base is None or not base.is_dir():
        return []
    default = DEFAULT_PLATFORMS[source]
    results: list[str] = []
    for skill_dir in sorted(base.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        platforms = read_platforms(skill_md, default)
        if needs in platforms:
            results.append(skill_dir.name)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=list(SOURCE_DIRS), required=True)
    parser.add_argument(
        "--needs",
        required=True,
        help="platform keyword to filter by (e.g. codex, agents, cursor)",
    )
    args = parser.parse_args()

    for name in list_skills_needing(args.source, args.needs):
        print(name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
