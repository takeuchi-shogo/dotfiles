"""Tests for skill_amender.py."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from skill_amender import assess_health, parse_skill


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


@pytest.fixture
def data_dir_with_executions(tmp_path):
    """スキル実行データを含むデータディレクトリ。"""
    learnings = tmp_path / "learnings"
    learnings.mkdir()

    entries = []
    for i in range(10):
        entries.append(
            json.dumps(
                {
                    "timestamp": f"2026-03-{10 + i:02d}T10:00:00Z",
                    "skill_name": "good-skill",
                    "score": 0.8,
                    "error_count": 0,
                    "gp_violations": 0,
                    "test_passed": True,
                    "project": "test",
                }
            )
        )
    for i in range(10):
        entries.append(
            json.dumps(
                {
                    "timestamp": f"2026-03-{10 + i:02d}T11:00:00Z",
                    "skill_name": "bad-skill",
                    "score": 0.2,
                    "error_count": 3,
                    "gp_violations": 2,
                    "test_passed": False,
                    "project": "test",
                }
            )
        )
    for i in range(5):
        entries.append(
            json.dumps(
                {
                    "timestamp": f"2026-03-{10 + i:02d}T12:00:00Z",
                    "skill_name": "declining-skill",
                    "score": 0.7,
                    "error_count": 0,
                    "gp_violations": 0,
                    "test_passed": True,
                    "project": "test",
                }
            )
        )
    for i in range(5):
        entries.append(
            json.dumps(
                {
                    "timestamp": f"2026-03-{15 + i:02d}T12:00:00Z",
                    "skill_name": "declining-skill",
                    "score": 0.45,
                    "error_count": 1,
                    "gp_violations": 1,
                    "test_passed": True,
                    "project": "test",
                }
            )
        )

    (learnings / "skill-executions.jsonl").write_text("\n".join(entries) + "\n")
    return tmp_path


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


class TestAssessHealth:
    def test_healthy_skill(self, data_dir_with_executions):
        report = assess_health("good-skill", data_dir_with_executions)
        assert report.status == "healthy"
        assert report.avg_score >= 0.6
        assert report.execution_count == 10

    def test_failing_skill(self, data_dir_with_executions):
        report = assess_health("bad-skill", data_dir_with_executions)
        assert report.status == "failing"
        assert report.avg_score < 0.4

    def test_degraded_by_trend(self, data_dir_with_executions):
        report = assess_health("declining-skill", data_dir_with_executions)
        assert report.status == "degraded"
        assert report.trend < -0.1

    def test_unknown_skill(self, data_dir_with_executions):
        report = assess_health("nonexistent-skill", data_dir_with_executions)
        assert report.execution_count == 0
        assert report.status == "healthy"

    def test_insufficient_data(self, tmp_path):
        learnings = tmp_path / "learnings"
        learnings.mkdir()
        entries = [
            json.dumps(
                {
                    "timestamp": "2026-03-14T10:00:00Z",
                    "skill_name": "new-skill",
                    "score": 0.3,
                    "error_count": 1,
                    "project": "test",
                }
            )
        ]
        (learnings / "skill-executions.jsonl").write_text("\n".join(entries) + "\n")
        report = assess_health("new-skill", tmp_path)
        assert report.execution_count == 1
