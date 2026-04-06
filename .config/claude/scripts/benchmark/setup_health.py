"""Setup Health Benchmark — 6次元のベンチマークスコアを計算する。

autocontext 知見の「統合ベンチマーク」を実装。
experiment_tracker.py と同じ JSONL 読み取りパターンを使用。

Usage:
    python setup_health.py
    python setup_health.py --json
"""

import argparse
import json
import os
import sys
from pathlib import Path


def _get_data_dir() -> Path:
    """データディレクトリを遅延評価で返す。"""
    return Path(
        os.environ.get(
            "AUTOEVOLVE_DATA_DIR",
            os.path.join(os.environ.get("HOME", ""), ".claude", "agent-memory"),
        )
    )


def _read_jsonl(path: Path) -> list[dict]:
    """JSONL ファイルを読み込む。存在しなければ空リスト。"""
    if not path.exists():
        return []
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def _count_recent(entries: list[dict], days: int = 7) -> int:
    """直近 N 日のエントリ数を返す。"""
    from datetime import datetime, timezone, timedelta

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    return sum(1 for e in entries if e.get("timestamp", "") >= cutoff)


def compute_error_rate() -> dict:
    """Error Rate: 直近7日のエラー数 / セッション数。"""
    data_dir = _get_data_dir()
    errors = _read_jsonl(data_dir / "learnings" / "errors.jsonl")
    metrics = _read_jsonl(data_dir / "metrics" / "session-metrics.jsonl")
    recent_errors = _count_recent(errors)
    recent_sessions = _count_recent(metrics)
    if recent_sessions == 0:
        return {"score": 0.0, "status": "no_data"}
    rate = recent_errors / recent_sessions
    # 低いほど良い: 0 errors = 1.0, 5+ errors/session = 0.0
    score = max(0.0, min(1.0, 1.0 - rate / 5.0))
    return {
        "score": round(score, 2),
        "errors": recent_errors,
        "sessions": recent_sessions,
        "rate": round(rate, 2),
    }


def compute_recovery_rate() -> dict:
    """Recovery Rate: セッション中のエラー回復率。"""
    data_dir = _get_data_dir()
    metrics = _read_jsonl(data_dir / "metrics" / "session-metrics.jsonl")
    if not metrics:
        return {"score": 0.0, "status": "no_data"}
    recent = [
        m
        for m in metrics
        if m.get("recovery_count", 0) > 0 or m.get("errors_count", 0) > 0
    ]
    if not recent:
        return {"score": 1.0, "recovered": 0, "total_errors": 0}
    total_errors = sum(m.get("errors_count", 0) for m in recent)
    recovered = sum(m.get("recovery_count", 0) for m in recent)
    if total_errors == 0:
        return {"score": 1.0, "recovered": 0, "total_errors": 0}
    score = min(1.0, recovered / total_errors)
    return {
        "score": round(score, 2),
        "recovered": recovered,
        "total_errors": total_errors,
    }


def compute_quality_score() -> dict:
    """Quality Score: 品質違反の頻度（低いほど良い）。"""
    data_dir = _get_data_dir()
    quality = _read_jsonl(data_dir / "learnings" / "quality.jsonl")
    recent = _count_recent(quality)
    # 0 violations = 1.0, 20+ = 0.0
    score = max(0.0, min(1.0, 1.0 - recent / 20.0))
    return {
        "score": round(score, 2),
        "recent_violations": recent,
    }


def compute_skill_health() -> dict:
    """Skill Health: スキル実行の平均スコア。"""
    data_dir = _get_data_dir()
    executions = _read_jsonl(data_dir / "learnings" / "skill-executions.jsonl")
    if not executions:
        return {"score": 0.0, "status": "no_data"}
    scores = [
        e.get("score", 0.5)
        for e in executions
        if isinstance(e.get("score"), (int, float))
    ]
    if not scores:
        return {"score": 0.0, "status": "no_data"}
    avg = sum(scores) / len(scores)
    return {
        "score": round(avg, 2),
        "total_executions": len(scores),
    }


def compute_improvement_velocity() -> dict:
    """Improvement Velocity: CQS トレンド。"""
    scripts_dir = Path(__file__).resolve().parent.parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from experiment_tracker import compute_cqs

    cqs_result = compute_cqs()
    if cqs_result["status"] == "insufficient_data":
        return {"score": 0.0, "status": "insufficient_data"}
    cqs = cqs_result["cqs"]
    # CQS を 0-1 スケールに正規化: -50..+50 → 0..1
    score = max(0.0, min(1.0, (cqs + 50) / 100))
    return {
        "score": round(score, 2),
        "cqs": cqs,
    }


def compute_review_acceptance() -> dict:
    """Review Acceptance: レビュー指摘の受入率。"""
    data_dir = _get_data_dir()
    feedback = _read_jsonl(data_dir / "learnings" / "review-feedback.jsonl")
    if not feedback:
        return {"score": 0.0, "status": "no_data"}
    accepted = sum(1 for f in feedback if f.get("outcome") in ("accepted", "accept"))
    total = len(feedback)
    score = accepted / total if total > 0 else 0.0
    return {
        "score": round(score, 2),
        "accepted": accepted,
        "total": total,
    }


def _cutoff_iso(days: int) -> str:
    from datetime import datetime, timedelta, timezone

    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


def compute_telemetry_completeness() -> dict:
    """必須 telemetry type のうち直近 7 日に観測された種類の割合。

    6D 本体ではない補助指標。telemetry パイプラインの健���性を示す。
    """
    data_dir = _get_data_dir()
    telemetry = _read_jsonl(data_dir / "learnings" / "telemetry.jsonl")
    recent = [e for e in telemetry if e.get("timestamp", "") >= _cutoff_iso(7)]
    expected_types = {
        "mcp_tool_usage",
        "subagent_complete",
        "rationalization_detected",
        "friction_event",
    }
    observed = {e.get("type", "") for e in recent} & expected_types
    completeness = len(observed) / len(expected_types) if expected_types else 0.0
    return {
        "score": round(completeness, 2),
        "observed": sorted(observed),
        "expected": sorted(expected_types),
        "missing": sorted(expected_types - observed),
    }


def compute_friction_visibility() -> dict:
    """直近 30 日�� friction event 検出数。0 なら検出��盤が未稼働。"""
    data_dir = _get_data_dir()
    friction = _read_jsonl(data_dir / "learnings" / "friction-events.jsonl")
    recent = [e for e in friction if e.get("timestamp", "") >= _cutoff_iso(30)]
    from collections import Counter

    class_counts = Counter(e.get("friction_class", "") for e in recent)
    total = len(recent)
    score = min(1.0, total / 10.0)  # 10+ events = 1.0
    return {
        "score": round(score, 2),
        "total_events": total,
        "by_class": dict(class_counts.most_common(5)),
    }


def compute_tier_alignment() -> dict:
    """skill-tier-shadow の aligned 率。"""
    data_dir = _get_data_dir()
    shadow = _read_jsonl(data_dir / "metrics" / "skill-tier-shadow.jsonl")
    if not shadow:
        return {"score": 0.0, "status": "no_data"}
    aligned = sum(1 for s in shadow if s.get("shadow_status") == "aligned")
    total = len(shadow)
    score = aligned / total if total else 0.0
    return {
        "score": round(score, 2),
        "aligned": aligned,
        "total": total,
    }


def compute_all() -> dict:
    """全6次元のベンチマークを計算する。"""
    dimensions = {
        "error_rate": compute_error_rate(),
        "recovery_rate": compute_recovery_rate(),
        "quality_score": compute_quality_score(),
        "skill_health": compute_skill_health(),
        "improvement_velocity": compute_improvement_velocity(),
        "review_acceptance": compute_review_acceptance(),
    }
    scores = [d["score"] for d in dimensions.values()]
    overall = sum(scores) / len(scores) if scores else 0.0
    # 補助指標 — 6D overall には含めない (dashboard 表示用)
    supporting = {
        "telemetry_completeness": compute_telemetry_completeness(),
        "friction_visibility": compute_friction_visibility(),
        "tier_alignment": compute_tier_alignment(),
    }

    return {
        "overall": round(overall, 2),
        "dimensions": dimensions,
        "supporting_indicators": supporting,
    }


def format_report(result: dict) -> str:
    """人間向けのレポートを生成する。"""
    lines = [
        "# Setup Health Report",
        "",
        f"Overall: {result['overall']:.2f}",
        "",
    ]
    for name, data in result["dimensions"].items():
        label = name.replace("_", " ").title()
        score = data["score"]
        bar_filled = int(score * 10)
        bar = "#" * bar_filled + "." * (10 - bar_filled)
        lines.append(f"  {label:.<25} [{bar}] {score:.2f}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Setup Health Benchmark")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    args = parser.parse_args()

    result = compute_all()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_report(result))


if __name__ == "__main__":
    main()
