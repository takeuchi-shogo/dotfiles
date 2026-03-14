"""Tests for skill_amender.py."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from skill_amender import parse_skill


@pytest.fixture
def sample_skill(tmp_path):
    """標準的な SKILL.md を作成する。"""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        "---\n"
        "name: my-skill\n"
        'description: "A test skill for unit testing."\n'
        'allowed-tools: "Read, Bash"\n'
        "---\n"
        "\n"
        "# My Skill\n"
        "\n"
        "## Step 1\n"
        "Do something.\n"
        "\n"
        "## Step 2\n"
        "Do another thing.\n"
    )
    return skill_file


class TestParseSkill:
    def test_parses_name(self, sample_skill):
        manifest = parse_skill(sample_skill)
        assert manifest.name == "my-skill"

    def test_parses_description(self, sample_skill):
        manifest = parse_skill(sample_skill)
        assert manifest.description == "A test skill for unit testing."

    def test_parses_body(self, sample_skill):
        manifest = parse_skill(sample_skill)
        assert "# My Skill" in manifest.body
        assert "## Step 1" in manifest.body

    def test_parses_raw_frontmatter(self, sample_skill):
        manifest = parse_skill(sample_skill)
        assert manifest.raw_frontmatter["allowed-tools"] == "Read, Bash"

    def test_stores_path(self, sample_skill):
        manifest = parse_skill(sample_skill)
        assert manifest.path == sample_skill

    def test_missing_frontmatter(self, tmp_path):
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("# No Frontmatter\n\nJust body.\n")
        manifest = parse_skill(skill_file)
        assert manifest.name == ""
        assert manifest.description == ""
        assert "# No Frontmatter" in manifest.body

    def test_quoted_and_unquoted_values(self, tmp_path):
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(
            "---\n"
            "name: unquoted-name\n"
            "description: unquoted description here\n"
            "---\n"
            "\nBody\n"
        )
        manifest = parse_skill(skill_file)
        assert manifest.name == "unquoted-name"
        assert manifest.description == "unquoted description here"

    def test_multiline_description(self, tmp_path):
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(
            "---\nname: multi\ndescription: >\n  Line one\n  line two\n---\n\nBody\n"
        )
        manifest = parse_skill(skill_file)
        assert "Line one" in manifest.description
        assert "line two" in manifest.description

    def test_content_hash(self, sample_skill):
        manifest = parse_skill(sample_skill)
        assert len(manifest.content_hash) == 8
        assert manifest.content_hash.isalnum()
