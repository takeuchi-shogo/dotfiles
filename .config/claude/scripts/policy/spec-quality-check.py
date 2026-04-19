#!/usr/bin/env python3
"""Spec quality check — detects ambiguity and missing sections in spec files.

Triggered by: hooks.PostToolUse (Write)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext advisory on stdout

Advisory only — never blocks.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import (
    load_hook_input,
    output_passthrough,
    output_context,
    run_hook,
    get_emitter,
)

emit = get_emitter()

_QUALITATIVE_RE = re.compile(
    r"(?:高速|安全|使いやすい|適切に?|十分に?|効率的|柔軟|fast|safe|easy|appropriate|sufficient|efficient|flexible)"
    r"(?![\s\S]{0,30}(?:\d|ms|秒|%|件|回|byte))"
)

_REQUIRED_SECTIONS = [
    ("## Context", "## コンテキスト"),
    ("## Requirements", "## 要件"),
    ("## Out of Scope", "## スコープ外"),
]

_ACCEPTANCE_CRITERIA_KEY = "acceptance_criteria:"

_AMBIGUOUS_CRITERIA = re.compile(
    r"うまく動く|正しく処理|適切に処理|問題なく|works correctly|handles properly"
)

# Scenario section detection — empirical-prompt-tuning T3.
# Advisory: median が未記載だと baseline が組めない (mizchi/empirical-prompt-tuning)
_SCENARIOS_SECTION_RE = re.compile(r"^##\s+Scenarios\s*$", re.MULTILINE)
_SCENARIO_MEDIAN_RE = re.compile(r"^###\s+median\s*$", re.MULTILINE | re.IGNORECASE)


def _check_scenarios(content: str) -> list[str]:
    """Advisory: Scenarios + median を確認 (empirical-prompt-tuning T3)."""
    findings: list[str] = []
    if not _SCENARIOS_SECTION_RE.search(content):
        findings.append(
            "⚠️ 推奨セクション '## Scenarios' が見つかりません"
            "（median/edge_cases/holdout_scenarios で baseline を構成してください）"
        )
        return findings
    if not _SCENARIO_MEDIAN_RE.search(content):
        findings.append(
            "⚠️ '### median' シナリオが未記載です"
            "（baseline に最低 1 つの中央値シナリオが必要）"
        )
    return findings


def _check_qualitative(content: str) -> list[str]:
    findings = []
    for m in _QUALITATIVE_RE.finditer(content):
        findings.append(
            f"⚠️ 定性表現 '{m.group()}' に定量基準がありません"
            "（数値・単位を追加してください）"
        )
    return findings


def _check_required_sections(content: str) -> list[str]:
    findings = []
    for primary, alt in _REQUIRED_SECTIONS:
        if primary not in content and alt not in content:
            findings.append(f"⚠️ 必須セクション '{primary}' が見つかりません")
    if _ACCEPTANCE_CRITERIA_KEY not in content:
        findings.append(
            f"⚠️ 必須セクション '{_ACCEPTANCE_CRITERIA_KEY}' が見つかりません"
        )
    return findings


def _check_ambiguous_criteria(content: str) -> list[str]:
    frontmatter = ""
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            frontmatter = content[3:end]

    findings = []
    for m in _AMBIGUOUS_CRITERIA.finditer(frontmatter):
        findings.append(
            f"⚠️ acceptance criteria '{m.group()}' が曖昧です"
            "（検証可能な形に書き直してください）"
        )
    return findings


def main() -> None:
    data = load_hook_input()
    if not data:
        return

    tool_name = data.get("tool_name", "")
    if tool_name != "Write":
        output_passthrough(data)
        return

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not (
        "docs/specs" in file_path.replace("\\", "/")
        and file_path.endswith(".prompt.md")
    ):
        output_passthrough(data)
        return

    content = tool_input.get("content", "")
    if not content:
        output_passthrough(data)
        return

    findings: list[str] = []
    findings.extend(_check_qualitative(content))
    findings.extend(_check_required_sections(content))
    findings.extend(_check_ambiguous_criteria(content))
    findings.extend(_check_scenarios(content))

    if not findings:
        output_passthrough(data)
        return

    emit("spec_quality", {"file": file_path, "finding_count": len(findings)})

    msg = "[spec-quality-check] Spec 品質の改善点:\n" + "\n".join(findings)
    output_context("PostToolUse", msg)


if __name__ == "__main__":
    run_hook("spec-quality-check", main, fail_closed=False)
