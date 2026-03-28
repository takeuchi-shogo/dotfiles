"""Skill amendment engine — SKILL.md parsing, health assessment,
and proposal generation.

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

            if len(value) >= 2 and (
                (value.startswith('"') and value.endswith('"'))
                or (value.startswith("'") and value.endswith("'"))
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

    1-10 スケール閾値 (compute_skill_score / retroactive_scorer と統一):
      Healthy:  avg >= 6.0
      Degraded: avg 4.0-6.0 OR trend <= -1.0
      Failing:  avg < 4.0 OR 直近5回中4回以上 score < 4.0
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
    scores = [e.get("score", 5.0) for e in skill_runs]
    avg_score = sum(scores) / len(scores)

    mid = len(scores) // 2
    if mid > 0:
        first_half = sum(scores[:mid]) / mid
        second_half = sum(scores[mid:]) / (len(scores) - mid)
        trend = round(second_half - first_half, 3)
    else:
        trend = 0.0

    recent_5 = scores[-5:] if len(scores) >= 5 else scores
    low_count = sum(1 for s in recent_5 if s < 4.0)
    mostly_failing = len(recent_5) >= 5 and low_count >= 4

    failure_patterns: list[dict] = []
    for run in skill_runs:
        if run.get("score", 5.0) < 4.0:
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
        skill_benchmarks.sort(key=lambda b: b.get("timestamp", ""))
        latest = skill_benchmarks[-1]
        benchmark_delta = latest.get("delta")

    if avg_score < 4.0 or mostly_failing:
        status: Literal["healthy", "degraded", "failing"] = "failing"
    elif avg_score < 6.0 or trend <= -1.0:
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


MIN_EXECUTIONS_FOR_PROPOSAL = 5


@dataclass
class AmendmentProposal:
    """修正提案。"""

    skill_name: str
    amendment_type: Literal[
        "narrow_description",
        "expand_description",
        "edit_instruction",
        "update_tool_ref",
        "deprecate",
    ]
    reason: str
    diff_summary: str
    evidence: dict = field(default_factory=dict)


@dataclass
class GateResult:
    """セミオートゲートの判定結果。"""

    verdict: Literal["auto_accept", "auto_reject", "pending_review"]
    ab_delta: float | None = None
    score_delta: float | None = None
    reason: str = ""


def classify_failure_pattern(report: SkillHealthReport) -> str | None:
    """健全性レポートから修正タイプを分類する。healthy なら None。

    Phase 1 では edit_instruction と deprecate のみ実装。
    narrow_description, expand_description, update_tool_ref は
    将来の failure pattern 分析で追加予定。
    """
    if report.status == "healthy":
        return None
    if report.benchmark_delta is not None and report.benchmark_delta < 0:
        return "deprecate"
    return "edit_instruction"


def generate_proposal(
    manifest: SkillManifest,
    report: SkillHealthReport,
) -> AmendmentProposal | None:
    """修正提案を生成する。データ不足や healthy なら None。

    improve-policy.md Rule 6: 実行5回以上が改善提案の最低条件
    """
    if report.status == "healthy":
        return None
    if report.execution_count < MIN_EXECUTIONS_FOR_PROPOSAL:
        return None

    amendment_type = classify_failure_pattern(report)
    if amendment_type is None:
        return None

    reasons = []
    if report.avg_score < 0.4:
        reasons.append(f"平均スコア {report.avg_score:.2f} (Failing 閾値 0.4 未満)")
    elif report.avg_score < 0.6:
        reasons.append(f"平均スコア {report.avg_score:.2f} (Degraded)")
    if report.trend <= -0.1:
        reasons.append(f"トレンド {report.trend:+.2f} (低下中)")
    if report.benchmark_delta is not None and report.benchmark_delta < 0:
        reasons.append(f"A/B delta {report.benchmark_delta:+.1f}pp (ベースライン以下)")

    diff_summaries = {
        "deprecate": "description に [DEPRECATED] を付与",
        "narrow_description": "description のトリガー条件を絞り込む",
        "expand_description": "description にキーワードを追加",
        "edit_instruction": "失敗パターンに基づくステップ修正",
        "update_tool_ref": "ツール参照の更新",
    }

    return AmendmentProposal(
        skill_name=report.skill_name,
        amendment_type=amendment_type,
        reason="; ".join(reasons),
        diff_summary=diff_summaries.get(amendment_type, ""),
        evidence={
            "avg_score": report.avg_score,
            "trend": report.trend,
            "execution_count": report.execution_count,
            "benchmark_delta": report.benchmark_delta,
            "failure_patterns": report.failure_patterns,
        },
    )


# --- セミオートゲート（EvoSkill 統合）--- #

_HIGH_IMPACT_PATTERNS = re.compile(r"(skills/.*/SKILL\.md|agents/.*\.md)")

GATE_ACCEPT_THRESHOLD_PP = 2.0
GATE_REJECT_THRESHOLD_PP = -2.0


CLIP_EPSILON = 0.2


def _apply_clip_check(
    result: GateResult,
    report: SkillHealthReport,
) -> GateResult:
    """GateResult 返却前に clip_ratio で変更比率を検証する。

    スコアトレンドの変動が ±epsilon を超える場合、
    reason に CLIP WARNING を追記して注意喚起する。
    """
    from rl_advantage import clip_ratio

    if report.execution_count < 2:
        return result

    # avg_score を「現在」、avg_score - trend を「以前」として比率を計算
    before = report.avg_score - report.trend
    if before <= 0:
        return result

    clipped = clip_ratio(report.avg_score, before, CLIP_EPSILON)
    raw_ratio = report.avg_score / before

    if abs(raw_ratio - clipped) > 1e-9:
        clip_msg = (
            f" [CLIP WARNING: ratio {raw_ratio:.2f}"
            f" clipped to {clipped:.2f},"
            f" epsilon={CLIP_EPSILON}]"
        )
        return GateResult(
            verdict=result.verdict,
            ab_delta=result.ab_delta,
            score_delta=result.score_delta,
            reason=result.reason + clip_msg,
        )

    return result


def gate_proposal(
    proposal: AmendmentProposal,
    report: SkillHealthReport,
    benchmark_delta: float | None = None,
) -> GateResult:
    """セミオートゲート: A/B delta に基づきスキル改善提案を判定。

    +2pp 以上  → auto_accept（ただし高影響ファイルは pending_review に格下げ）
    -2pp 以下  → auto_reject
    間 or 未測定 → pending_review
    """
    if benchmark_delta is None:
        return GateResult(
            verdict="pending_review",
            ab_delta=None,
            score_delta=report.trend,
            reason="A/B テスト未実施",
        )

    if benchmark_delta <= GATE_REJECT_THRESHOLD_PP:
        return GateResult(
            verdict="auto_reject",
            ab_delta=benchmark_delta,
            score_delta=report.trend,
            reason=(
                f"A/B delta {benchmark_delta:+.1f}pp"
                f" — 閾値 {GATE_REJECT_THRESHOLD_PP}pp 以下"
            ),
        )

    if benchmark_delta >= GATE_ACCEPT_THRESHOLD_PP:
        if proposal.amendment_type in (
            "edit_instruction",
            "deprecate",
        ):
            return GateResult(
                verdict="pending_review",
                ab_delta=benchmark_delta,
                score_delta=report.trend,
                reason=(
                    f"A/B delta {benchmark_delta:+.1f}pp"
                    " — 高影響変更のため人間レビュー必須"
                ),
            )
        return GateResult(
            verdict="auto_accept",
            ab_delta=benchmark_delta,
            score_delta=report.trend,
            reason=(
                f"A/B delta {benchmark_delta:+.1f}pp"
                f" — 閾値 {GATE_ACCEPT_THRESHOLD_PP}pp 以上"
            ),
        )

    result = GateResult(
        verdict="pending_review",
        ab_delta=benchmark_delta,
        score_delta=report.trend,
        reason=(f"A/B delta {benchmark_delta:+.1f}pp — 閾値内、人間レビュー推奨"),
    )
    return _apply_clip_check(result, report)
