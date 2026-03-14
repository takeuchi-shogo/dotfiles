"""Skill amendment engine — SKILL.md parsing, health assessment, and proposal generation.

autoevolve-core の Phase 2 から呼び出される。
SKILL.md の解析、スキル健全性の判定、修正提案の生成を行う。
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from storage import get_data_dir, read_jsonl


@dataclass
class SkillManifest:
    """SKILL.md の構造化表現。"""

    name: str
    description: str
    body: str
    path: Path
    raw_frontmatter: dict = field(default_factory=dict)
    content_hash: str = ""


@dataclass
class SkillHealthReport:
    """スキルの健全性レポート。"""

    skill_name: str
    status: Literal["healthy", "degraded", "failing"]
    avg_score: float
    trend: float
    execution_count: int
    failure_patterns: list[dict] = field(default_factory=list)
    benchmark_delta: float | None = None


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """--- で囲まれたフロントマターを解析し、(frontmatter_dict, body) を返す。

    Handles:
    - key: value (simple)
    - key: "quoted value" or key: 'quoted value'
    - key: > (folded scalar, multiline with 2-space indent continuation)
    - Missing frontmatter (no --- delimiters)
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
    if not match:
        return {}, text

    fm_text = match.group(1)
    body = match.group(2)
    result: dict[str, str] = {}

    current_key: str | None = None
    multiline_value: list[str] = []

    for line in fm_text.split("\n"):
        kv = re.match(r"^(\S[^:]*?):\s*(.*)", line)
        if kv:
            if current_key and multiline_value:
                result[current_key] = " ".join(multiline_value).strip()
                multiline_value = []

            key = kv.group(1).strip()
            value = kv.group(2).strip()

            if value in (">", "|"):
                current_key = key
                multiline_value = []
                continue

            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]

            result[key] = value
            current_key = None
        elif current_key and line.startswith("  "):
            multiline_value.append(line.strip())

    if current_key and multiline_value:
        result[current_key] = " ".join(multiline_value).strip()

    return result, body


def parse_skill(path: Path) -> SkillManifest:
    """SKILL.md を解析して SkillManifest を返す。"""
    text = path.read_text(encoding="utf-8")
    fm, body = _parse_frontmatter(text)
    content_hash = hashlib.sha256(text.encode()).hexdigest()[:8]

    return SkillManifest(
        name=fm.get("name", ""),
        description=fm.get("description", ""),
        body=body,
        path=path,
        raw_frontmatter={
            k: v for k, v in fm.items() if k not in ("name", "description")
        },
        content_hash=content_hash,
    )


def assess_health(skill_name: str, data_dir: Path | None = None) -> SkillHealthReport:
    """skill-executions.jsonl からスキルの健全性を判定する。

    閾値 (autoevolve-core.md L60-70 準拠):
      Healthy:  avg >= 0.6
      Degraded: avg 0.4-0.6 OR trend <= -0.1
      Failing:  avg < 0.4 OR 直近5回中4回以上 score < 0.4
    """
    if data_dir is None:
        data_dir = get_data_dir()

    executions = read_jsonl(data_dir / "learnings" / "skill-executions.jsonl")
    skill_runs = [e for e in executions if e.get("skill_name") == skill_name]

    if not skill_runs:
        return SkillHealthReport(
            skill_name=skill_name,
            status="healthy",
            avg_score=0.0,
            trend=0.0,
            execution_count=0,
        )

    skill_runs.sort(key=lambda e: e.get("timestamp", ""))
    scores = [e.get("score", 0.5) for e in skill_runs]
    avg_score = sum(scores) / len(scores)

    mid = len(scores) // 2
    if mid > 0:
        first_half = sum(scores[:mid]) / mid
        second_half = sum(scores[mid:]) / (len(scores) - mid)
        trend = round(second_half - first_half, 3)
    else:
        trend = 0.0

    recent_5 = scores[-5:] if len(scores) >= 5 else scores
    low_count = sum(1 for s in recent_5 if s < 0.4)
    mostly_failing = len(recent_5) >= 5 and low_count >= 4

    failure_patterns: list[dict] = []
    for run in skill_runs:
        if run.get("score", 1.0) < 0.4:
            pattern: dict = {}
            if run.get("error_count", 0) > 0:
                pattern["error_count"] = run["error_count"]
            if run.get("gp_violations", 0) > 0:
                pattern["gp_violations"] = run["gp_violations"]
            if run.get("test_passed") is False:
                pattern["test_failed"] = True
            if pattern:
                failure_patterns.append(pattern)

    benchmarks = read_jsonl(data_dir / "learnings" / "skill-benchmarks.jsonl")
    skill_benchmarks = [b for b in benchmarks if b.get("skill") == skill_name]
    benchmark_delta = None
    if skill_benchmarks:
        latest = skill_benchmarks[-1]
        benchmark_delta = latest.get("delta")

    if avg_score < 0.4 or mostly_failing:
        status: Literal["healthy", "degraded", "failing"] = "failing"
    elif avg_score < 0.6 or trend <= -0.1:
        status = "degraded"
    else:
        status = "healthy"

    return SkillHealthReport(
        skill_name=skill_name,
        status=status,
        avg_score=round(avg_score, 3),
        trend=trend,
        execution_count=len(skill_runs),
        failure_patterns=failure_patterns,
        benchmark_delta=benchmark_delta,
    )
