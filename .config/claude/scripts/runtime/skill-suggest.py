#!/usr/bin/env python3
"""Suggest relevant skills based on edited file types.

PostToolUse hook. Implements "environment state drives skill
activation" from Slate's Skill Chaining article.
Suggests only — never auto-activates.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import load_hook_input, run_hook  # noqa: E402

# File extension → suggested skills mapping
SKILL_MAP: dict[str, list[str]] = {
    # Frontend
    ".tsx": ["/frontend-design:frontend-design"],
    ".jsx": ["/frontend-design:frontend-design"],
    ".css": ["/frontend-design:frontend-design"],
    ".scss": ["/frontend-design:frontend-design"],
    ".html": ["/frontend-design:frontend-design"],
    ".svelte": ["/frontend-design:frontend-design"],
    ".vue": ["/frontend-design:frontend-design"],
    # Skill/agent definitions
    "SKILL.md": ["/skill-creator:skill-creator"],
    # Harness config
    "settings.json": ["/update-config"],
}

# Paths that trigger specific suggestions
PATH_MAP: dict[str, list[str]] = {
    ".config/claude/agents/": ["/skill-creator:skill-creator"],
    ".config/claude/skills/": ["/skill-creator:skill-creator"],
    ".config/claude/scripts/": ["/update-config"],
    "docs/specs/": ["/spec"],
}

# Cooldown: don't suggest the same skill twice in a session
SEEN_FILE = "/tmp/claude-skill-suggest-seen.json"


def load_seen() -> set[str]:
    try:
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_seen(seen: set[str]) -> None:
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def get_suggestions(file_path: str) -> list[str]:
    suggestions: list[str] = []

    # Check test file patterns first (more specific)
    for suffix, skills in SKILL_MAP.items():
        if file_path.endswith(suffix):
            suggestions.extend(skills)

    # If no test pattern matched, check by extension
    if not suggestions:
        _, ext = os.path.splitext(file_path)
        if ext in SKILL_MAP:
            suggestions.extend(SKILL_MAP[ext])

    # Check path patterns
    for path_pattern, skills in PATH_MAP.items():
        if path_pattern in file_path:
            suggestions.extend(skills)

    return list(dict.fromkeys(suggestions))  # dedupe preserving order


def main() -> None:
    data = load_hook_input()
    file_path = data.get("tool_input", {}).get("file_path", "") or ""

    if not file_path:
        return

    suggestions = get_suggestions(file_path)
    if not suggestions:
        return

    # Filter out already-suggested skills this session
    seen = load_seen()
    new_suggestions = [s for s in suggestions if s not in seen]
    if not new_suggestions:
        return

    # Mark as seen
    seen.update(new_suggestions)
    save_seen(seen)

    # Output as additional context (non-blocking)
    skills_str = ", ".join(new_suggestions)
    print(
        f"[Skill Suggest] {os.path.basename(file_path)} の変更を検出。"
        f"関連スキル: {skills_str}"
    )


if __name__ == "__main__":
    run_hook("skill-suggest", main)
