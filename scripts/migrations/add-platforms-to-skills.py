#!/usr/bin/env python3
"""One-off: add `platforms:` to SKILL.md for the shared skills currently
hardcoded in .bin/symlink.sh (CODEX_SHARED_CLAUDE_SKILLS + CODEX_SHARED_PROJECT_SKILLS).

Usage:
  python3 scripts/migrations/add-platforms-to-skills.py [--dry-run]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Matches the current hardcoded arrays in .bin/symlink.sh.
CLAUDE_SHARED = {
    "senior-backend": ["claude", "codex", "agents"],
    "senior-frontend": ["claude", "codex", "agents"],
    "react-best-practices": ["claude", "codex", "agents"],
    "frontend-design": ["claude", "codex", "agents"],
}
AGENTS_SHARED = {
    "codex-search-first": ["agents", "codex"],
    "codex-verification-before-completion": ["agents", "codex"],
    "dotfiles-config-validation": ["agents", "codex"],
    "codex-checkpoint-resume": ["agents", "codex"],
    "codex-memory-capture": ["agents", "codex"],
    "codex-session-hygiene": ["agents", "codex"],
    "openai-frontend-prompt-workflow": ["agents", "codex"],
    "github-review-workflow": ["agents", "codex"],
    "artifact-workflow": ["agents", "codex"],
}


def _split_frontmatter(text: str) -> tuple[list[str], str] | None:
    if not text.startswith("---\n"):
        return None
    lines = text.splitlines(keepends=True)
    for idx in range(1, len(lines)):
        if lines[idx].rstrip("\r\n") == "---":
            return lines[1:idx], "".join(lines[idx:])
    return None


def _has_top_level_key(lines: list[str], key: str) -> bool:
    prefix = f"{key}:"
    return any(
        line.startswith(prefix) for line in lines if line and not line[0].isspace()
    )


def _insert_after_origin(fm_lines: list[str], new_line: str) -> list[str]:
    for i, line in enumerate(fm_lines):
        if line.startswith("origin:") and (
            i == 0 or not fm_lines[i - 1].startswith(" ")
        ):
            return fm_lines[: i + 1] + [new_line] + fm_lines[i + 1 :]
    return fm_lines + [new_line]


def update(skill_md: Path, platforms: list[str], dry_run: bool) -> str:
    name = skill_md.parent.name
    text = skill_md.read_text(encoding="utf-8")
    split = _split_frontmatter(text)
    if split is None:
        return f"skip (no frontmatter): {name}"
    fm_lines, rest = split
    if _has_top_level_key(fm_lines, "platforms"):
        return f"skip (platforms exists): {name}"
    payload = "[" + ", ".join(platforms) + "]"
    new_line = f"platforms: {payload}\n"
    new_fm = _insert_after_origin(fm_lines, new_line)
    new_text = "---\n" + "".join(new_fm) + rest
    if dry_run:
        return f"would add platforms={payload}: {name}"
    skill_md.write_text(new_text, encoding="utf-8")
    return f"added platforms={payload}: {name}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    targets: list[tuple[Path, list[str]]] = []
    for name, platforms in CLAUDE_SHARED.items():
        targets.append(
            (REPO_ROOT / ".config/claude/skills" / name / "SKILL.md", platforms)
        )
    for name, platforms in AGENTS_SHARED.items():
        targets.append((REPO_ROOT / ".agents/skills" / name / "SKILL.md", platforms))

    missing = [p for p, _ in targets if not p.is_file()]
    if missing:
        for m in missing:
            print(f"[error] missing: {m}", file=sys.stderr)
        return 1

    for path, platforms in targets:
        print(update(path, platforms, args.dry_run))
    return 0


if __name__ == "__main__":
    sys.exit(main())
