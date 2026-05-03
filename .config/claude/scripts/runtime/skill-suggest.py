#!/usr/bin/env python3
"""Suggest relevant skills based on edited file types.

PostToolUse hook. Implements "environment state drives skill
activation" from Slate's Skill Chaining article.
Suggests only — never auto-activates.
"""

import json
import os

# File extension → suggested skills mapping
SKILL_MAP: dict[str, list[str]] = {
    # Frontend
    ".tsx": ["/frontend-design", "/web-design-guidelines", "/react-best-practices"],
    ".jsx": ["/frontend-design", "/react-best-practices"],
    ".css": ["/frontend-design", "/web-design-guidelines"],
    ".scss": ["/frontend-design", "/web-design-guidelines"],
    ".html": ["/frontend-design", "/web-design-guidelines"],
    ".svelte": ["/frontend-design"],
    ".vue": ["/frontend-design"],
    # Proto
    ".proto": ["/buf-protobuf"],
    # GraphQL
    ".graphql": ["/graphql-expert"],
    ".gql": ["/graphql-expert"],
    # Test files (detected by name pattern, not extension)
    "_test.go": ["/autocover"],
    ".test.ts": ["/autocover"],
    ".test.tsx": ["/autocover"],
    ".spec.ts": ["/autocover"],
    ".spec.tsx": ["/autocover"],
    # Skill/agent definitions
    "SKILL.md": ["/skill-creator"],
    # Harness config
    "settings.json": ["/update-config"],
}

# Paths that trigger specific suggestions
PATH_MAP: dict[str, list[str]] = {
    ".config/claude/agents/": ["/skill-creator"],
    ".config/claude/skills/": ["/skill-creator"],
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
    tool_input = json.loads(os.environ.get("TOOL_INPUT", "{}"))
    file_path = tool_input.get("file_path", "")

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
    main()
