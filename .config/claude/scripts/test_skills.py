#!/usr/bin/env python3
"""スキル構造・参照整合性の自動テスト。

Usage:
    python3 .config/claude/scripts/test_skills.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"

# Skills that contain example file paths in documentation (not real references)
REF_CHECK_SKIP = {"skill-creator"}

# YAML frontmatter の簡易パーサー（PyYAML 不要）
KEBAB_CASE_RE = re.compile(r"^[a-z][a-z0-9-]*$")
# Only < is forbidden — > is valid YAML folded scalar syntax
XML_BRACKET_RE = re.compile(r"<")


def parse_frontmatter(content: str) -> tuple[dict[str, str], list[str]]:
    """Parse YAML frontmatter without PyYAML. Returns (fields, errors)."""
    errors: list[str] = []
    fields: dict[str, str] = {}

    delimiter_count = content.count("---")
    if delimiter_count < 2:
        errors.append(f"frontmatter delimiters: expected 2, got {delimiter_count}")
        return fields, errors

    parts = content.split("---", 2)
    fm_text = parts[1]

    if XML_BRACKET_RE.search(fm_text):
        errors.append("XML angle brackets (<>) found in frontmatter")

    # Parse key-value pairs (handles multi-line > and | blocks)
    current_key = None
    current_value_lines: list[str] = []

    for line in fm_text.strip().split("\n"):
        kv_match = re.match(r"^(\w[\w-]*):\s*(.*)", line)
        if kv_match and not line.startswith(" "):
            if current_key:
                fields[current_key] = " ".join(current_value_lines).strip()
            current_key = kv_match.group(1)
            val = kv_match.group(2).strip()
            if val in (">", "|", ">-", "|-"):
                current_value_lines = []
            else:
                current_value_lines = [val.strip('"').strip("'")]
        elif current_key and line.startswith("  "):
            current_value_lines.append(line.strip())
        # else: continuation or blank line

    if current_key:
        fields[current_key] = " ".join(current_value_lines).strip()

    return fields, errors


def test_frontmatter(skill_path: Path) -> list[str]:
    """YAML frontmatter の構造テスト。"""
    errors: list[str] = []
    content = (skill_path / "SKILL.md").read_text(encoding="utf-8")

    fields, parse_errors = parse_frontmatter(content)
    errors.extend(parse_errors)

    if parse_errors:
        return errors  # Can't validate further if parsing failed

    # name: kebab-case
    name = fields.get("name", "")
    if not name:
        errors.append("name field is missing")
    elif not KEBAB_CASE_RE.match(name):
        errors.append(f"name '{name}' is not kebab-case")

    # description: required, <= 1024 chars
    desc = fields.get("description", "")
    if not desc:
        errors.append("description is empty")
    elif len(desc) > 1024:
        errors.append(f"description too long: {len(desc)} > 1024 chars")

    return errors


def _strip_fenced_blocks(text: str) -> str:
    """Remove fenced code blocks to avoid matching example references."""
    return re.sub(r"```[\s\S]*?```", "", text)


def test_references(skill_path: Path) -> list[str]:
    """SKILL.md 内のファイル参照が実在するか検証。"""
    errors: list[str] = []
    content = (skill_path / "SKILL.md").read_text(encoding="utf-8")
    cleaned = _strip_fenced_blocks(content)

    # references/ と scripts/ への参照を検出
    # Also strip lines that are clearly examples (contain "Example" or "例")
    lines = [
        line for line in cleaned.split("\n")
        if not re.search(r"(?:Example|例|When to include|Benefits)", line, re.IGNORECASE)
    ]
    cleaned = "\n".join(lines)
    refs = re.findall(r"`((?:references|scripts|assets)/[^`]+)`", cleaned)
    for ref in refs:
        ref_path = skill_path / ref
        if not ref_path.exists():
            errors.append(f"referenced file not found: {ref}")

    return errors


def main() -> None:
    exit_code = 0
    passed = 0
    failed = 0

    skills = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())

    for skill_path in skills:
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            continue

        errors: list[str] = []
        errors.extend(test_frontmatter(skill_path))
        if skill_path.name not in REF_CHECK_SKIP:
            errors.extend(test_references(skill_path))

        if errors:
            exit_code = 1
            failed += 1
            print(f"\n❌ {skill_path.name}:")
            for e in errors:
                print(f"  - {e}")
        else:
            passed += 1
            print(f"✅ {skill_path.name}")

    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")

    sys.exit(exit_code)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[test_skills] error: {e}", file=sys.stderr)
        sys.exit(2)
