#!/usr/bin/env python3
"""AutoEvolve session learner — flushes session events to persistent storage.

Triggered by: hooks.Stop / hooks.SessionEnd
Input: stdin passthrough
Output: stdout passthrough
"""

from __future__ import annotations

import hashlib
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from session_events import (
    append_to_learnings,
    append_to_metrics,
    compute_skill_score,
    flush_session,
)


def build_session_summary(cwd: str | None = None) -> dict:
    """セッションイベントを集約してサマリーを構築する。"""
    events = flush_session()

    errors = [e for e in events if e.get("category") == "error"]
    quality = [e for e in events if e.get("category") == "quality"]
    patterns = [e for e in events if e.get("category") == "pattern"]
    corrections = [e for e in events if e.get("category") == "correction"]

    project = Path(cwd).name if cwd else "unknown"

    # Score summary
    all_importance = [e.get("importance", 0.5) for e in events]
    high_count = sum(1 for i in all_importance if i >= 0.8)
    avg_importance = (
        sum(all_importance) / len(all_importance) if all_importance else 0.0
    )

    # Outcome classification (arXiv:2603.10600 Multi-Outcome Learning)
    if errors and corrections:
        outcome = "recovery"
    elif errors:
        outcome = "failure"
    else:
        outcome = "clean_success"

    return {
        "project": project,
        "cwd": cwd or os.getcwd(),
        "total_events": len(events),
        "errors_count": len(errors),
        "quality_issues": len(quality),
        "patterns_found": len(patterns),
        "corrections": len(corrections),
        "outcome": outcome,
        "high_importance_count": high_count,
        "avg_importance": round(avg_importance, 2),
        "_events": events,
        "_errors": errors,
        "_quality": quality,
        "_patterns": patterns,
        "_corrections": corrections,
    }


def _update_playbook(summary: dict, logger: logging.Logger) -> None:
    """プロジェクト固有の Playbook を更新する。"""
    from datetime import datetime, timezone

    from storage import get_data_dir

    project = summary.get("project", "unknown")
    if project == "unknown" or summary["total_events"] < 2:
        return

    playbooks_dir = get_data_dir() / "playbooks"
    playbooks_dir.mkdir(parents=True, exist_ok=True)
    playbook_path = playbooks_dir / f"{project}.md"

    entries: list[str] = []
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for error in summary["_errors"][:3]:
        data = error.get("data", {})
        msg = data.get("message", data.get("error", ""))
        if msg:
            fix = data.get("fix", "")
            entry = f"- [{ts}] Error: {msg[:120]}"
            if fix:
                entry += f" -> Fix: {fix[:80]}"
            entries.append(entry)

    for issue in summary["_quality"][:3]:
        data = issue.get("data", {})
        rule = data.get("rule", "")
        file = data.get("file", "")
        if rule:
            name = Path(file).name if file else "unknown"
            entries.append(f"- [{ts}] {rule} violation in {name}")

    for pattern in summary["_patterns"][:2]:
        data = pattern.get("data", {})
        desc = data.get("description", data.get("pattern", ""))
        if desc:
            entries.append(f"- [{ts}] Pattern: {desc[:120]}")

    if not entries:
        return

    existing = ""
    if playbook_path.exists():
        existing = playbook_path.read_text(encoding="utf-8")
    if not existing:
        header_body = "Project-specific learnings (auto-accumulated)."
        existing = f"# {project} Playbook\n\n{header_body}\n\n"

    new_content = existing.rstrip() + "\n" + "\n".join(entries) + "\n"

    lines = new_content.splitlines()
    if len(lines) > 100:
        header = lines[:4]
        body = lines[4:]
        lines = header + body[-(100 - len(header)) :]
        new_content = "\n".join(lines) + "\n"

    playbook_path.write_text(new_content, encoding="utf-8")
    logger.info("session-learner: updated playbook for %s", project)


def _classify_approach(events: list[dict]) -> str:
    """セッションイベントからアプローチ分類を推論する (EvoX Task B)。

    Returns: refinement / structural / exploratory /
             codex-deep / gemini-research
    """
    skill_names = {
        e.get("skill_name", "") for e in events if e.get("category") == "skill"
    }
    if skill_names & {"codex-debugger", "codex-reviewer"}:
        return "codex-deep"
    if "gemini-explore" in skill_names:
        return "gemini-research"

    # exploratory: 検索系イベントが多い
    search_tools = {"Read", "Grep", "Glob", "WebSearch"}
    search_count = sum(1 for e in events if e.get("tool_name") in search_tools)
    if events and search_count > len(events) * 0.5:
        return "exploratory"

    # structural: 3+ ファイルへの言及
    files_mentioned = {
        e.get("file", e.get("path", ""))
        for e in events
        if e.get("file") or e.get("path")
    }
    if len(files_mentioned) >= 3:
        return "structural"

    return "refinement"


def _classify_task_type(summary: dict) -> str:
    """セッションのタスクタイプを推論する (EvoX Task B)。

    Returns: "debug" | "implement" | "refactor" | "investigate"
    """
    if summary["errors_count"] > 0 and summary["corrections"] > 0:
        return "debug"
    if summary["quality_issues"] > summary["errors_count"]:
        return "refactor"
    if summary["total_events"] < 5 and summary["errors_count"] == 0:
        return "investigate"
    return "implement"


def _detect_repeated_topics(summary: dict, logger: logging.Logger) -> None:
    """Detect topics that appear repeatedly across sessions.

    Scans recent learnings for recurring file-path + error-pattern combinations.
    If a topic appears in 3+ sessions, emits a codification suggestion.
    Based on Codified Context paper G4: "If you explained it twice, write it down."
    """
    import json
    from collections import Counter

    from storage import get_data_dir

    errors_path = get_data_dir() / "learnings" / "errors.jsonl"
    if not errors_path.exists():
        return

    topic_counter: Counter[str] = Counter()
    try:
        lines = errors_path.read_text(encoding="utf-8").splitlines()
        for line in lines[-50:]:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                data = entry.get("data", {})
                file_path = data.get("file", data.get("path", ""))
                error_type = data.get("type", data.get("error_type", ""))
                if file_path:
                    parts = Path(file_path).parts
                    topic = (
                        "/".join(parts[:3])
                        if len(parts) >= 3
                        else str(Path(file_path).parent)
                    )
                    if error_type:
                        topic = f"{topic}:{error_type}"
                    topic_counter[topic] += 1
            except (json.JSONDecodeError, KeyError):
                continue
    except OSError:
        return

    for topic, count in topic_counter.items():
        if count >= 3:
            from session_events import emit_repeated_topic

            file_patterns = [topic.split(":")[0]]
            emit_repeated_topic(topic, file_patterns, count)
            logger.info(
                "session-learner: repeated topic detected: %s (%d occurrences)",
                topic,
                count,
            )


def _compute_skill_version(skill_name: str) -> str:
    """SKILL.md の内容ハッシュ先頭8文字を返す。見つからなければ空文字。"""
    skills_dir = Path.home() / ".claude" / "skills"
    skill_file = skills_dir / skill_name / "SKILL.md"
    if not skill_file.exists():
        return ""
    try:
        content = skill_file.read_text(encoding="utf-8")
        return hashlib.sha256(content.encode()).hexdigest()[:8]
    except OSError:
        return ""


def _detect_critical_failure_step(events: list[dict]) -> dict | None:
    """Identify the Critical Failure Step (CFS) in a session trajectory.

    The CFS is the first high-importance error after which no recovery occurs.
    Inspired by AgentRx (Microsoft Research): "the first unrecoverable error."

    Returns a dict with cfs_index, failure_mode, message, cascade_length,
    or None if no CFS is found.
    """
    CFS_IMPORTANCE_THRESHOLD = 0.7
    for i, event in enumerate(events):
        if event.get("category") != "error":
            continue
        if event.get("importance", 0) < CFS_IMPORTANCE_THRESHOLD:
            continue
        # Check if any subsequent event indicates recovery
        subsequent = events[i + 1 :]
        has_recovery = any(
            e.get("category") == "correction"
            or (
                e.get("category") == "error"
                and e.get("importance", 0) < CFS_IMPORTANCE_THRESHOLD
                and e.get("failure_mode") == event.get("failure_mode")
            )
            for e in subsequent
        )
        if not has_recovery:
            return {
                "cfs_index": i,
                "failure_mode": event.get("failure_mode", ""),
                "message": event.get("message", ""),
                "importance": event.get("importance", 0),
                "cascade_length": len(subsequent),
                "total_events": len(events),
            }
    return None


def _compute_proposal_metrics(events: list[dict]) -> dict:
    """Proposal verdict イベントから accept_rate と連続 reject 数を計算する。

    autoresearch 記事の知見: accept_rate がエージェントの提案品質を示す。
    GPT-5.4: 67%, Spark: 17%。連続 reject はドリフトのシグナル。
    """
    proposals = [
        e
        for e in events
        if e.get("category") == "proposal" and e.get("type") == "verdict"
    ]
    if not proposals:
        return {}

    keeps = sum(1 for p in proposals if p.get("verdict") == "keep")
    total = len(proposals)

    # 末尾からの連続 revert 数（ドリフト検出用）
    consecutive_rejects = 0
    for p in reversed(proposals):
        if p.get("verdict") == "revert":
            consecutive_rejects += 1
        else:
            break

    return {
        "proposal_count": total,
        "accept_count": keeps,
        "reject_count": total - keeps,
        "accept_rate": round(keeps / total, 2) if total > 0 else 0.0,
        "consecutive_rejects": consecutive_rejects,
    }


def _read_last_jsonl_entry(path: Path) -> dict:
    """JSONL ファイルの最後のエントリを返す。空/不在なら空辞書。"""
    import json as _json

    if not path.exists():
        return {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        for line in reversed(lines):
            line = line.strip()
            if line:
                return _json.loads(line)
    except (OSError, _json.JSONDecodeError) as exc:
        logging.getLogger("autoevolve").debug(
            "_read_last_jsonl_entry failed for %s: %s", path, exc
        )
    return {}


# outcome → score マッピング
_OUTCOME_SCORES: dict[str, float] = {
    "clean_success": 1.0,
    "recovery": 0.6,
    "failure": 0.2,
}


def process_session(cwd: str | None = None) -> None:
    """セッションデータを処理し、永続ストレージに書き出す。"""
    from session_events import compute_config_version

    logger = logging.getLogger("autoevolve")
    summary = build_session_summary(cwd=cwd)

    if summary["total_events"] == 0:
        return

    # RL: config_version を計算
    config_version = compute_config_version()

    from tip_generalizer import generalize_entry

    logger.info(
        "session-learner: processing %d events for %s",
        summary["total_events"],
        summary["project"],
    )

    for error in summary["_errors"]:
        entry = {k: v for k, v in error.items() if k != "category"}
        entry = generalize_entry(entry)
        append_to_learnings("errors", entry)

    for issue in summary["_quality"]:
        entry = {k: v for k, v in issue.items() if k != "category"}
        entry = generalize_entry(entry)
        append_to_learnings("quality", entry)

    for pattern in summary["_patterns"]:
        entry = {k: v for k, v in pattern.items() if k != "category"}
        entry = generalize_entry(entry)
        append_to_learnings("patterns", entry)

    # Recovery Tips: error→correction ペアを recovery-tips.jsonl に保存
    # (arXiv:2603.10600 Contextual Learning Generator — Recovery Tips)
    if summary["_errors"] and summary["_corrections"]:
        from tip_generalizer import generalize_text

        for error in summary["_errors"]:
            err_msg = error.get("message", "")
            if not err_msg:
                continue
            # 対応する correction を探す（時系列で最も近いもの）
            err_ts = error.get("timestamp", "")
            best_correction = None
            for corr in summary["_corrections"]:
                corr_ts = corr.get("timestamp", "")
                if corr_ts >= err_ts:
                    best_correction = corr
                    break
            if not best_correction:
                best_correction = summary["_corrections"][-1]

            recovery_action = best_correction.get("message", "") or best_correction.get(
                "fix", ""
            )
            append_to_learnings(
                "recovery-tips",
                {
                    "error_pattern": generalize_text(err_msg),
                    "failure_mode": error.get("failure_mode", ""),
                    "recovery_action": recovery_action,
                    "trigger_condition": error.get("command", "")[:200],
                    "importance": max(error.get("importance", 0.5), 0.7),
                },
            )

    # スキル実行データの集計
    from rl_advantage import importance_weight, step_credit

    events = summary["_events"]
    quality = summary["_quality"]
    skill_invocations = [
        e
        for e in events
        if e.get("category") == "skill" and e.get("type") == "invocation"
    ]

    # RL: 前回セッションの config_version を取得して IS weight 計算
    from storage import get_data_dir

    prev_entry = _read_last_jsonl_entry(
        get_data_dir() / "metrics" / "session-metrics.jsonl"
    )
    prev_cv = prev_entry.get("config_version", config_version)
    change_count = 0 if prev_cv == config_version else 1
    is_weight = importance_weight(config_version, prev_cv, change_count)

    if skill_invocations:
        # セッション全体の集計値（ループ外で一度だけ計算）
        error_count = len(summary["_errors"])
        gp_violations = sum(1 for e in quality if e.get("rule", "").startswith("GP-"))
        review_criticals = sum(
            1 for e in quality if e.get("review_severity") in ("critical", "important")
        )
        test_passed = not any(e.get("test_passed") is False for e in events)

        for inv in skill_invocations:
            skill_name = inv.get("skill_name", "")
            if not skill_name:
                continue
            score = compute_skill_score(events, skill_name)

            # Extended fields: step_failures
            step_outcomes = [
                e
                for e in events
                if e.get("category") == "skill"
                and e.get("type") == "step_outcome"
                and e.get("skill_name") == skill_name
            ]
            step_failures = sorted(
                {
                    e["step"]
                    for e in step_outcomes
                    if e.get("outcome") == "failed" and "step" in e
                }
            )

            # Extended fields: related_error_ids
            error_refs_from_steps = {
                e.get("error_ref") for e in step_outcomes if e.get("error_ref")
            }
            related_error_ids = sorted(error_refs_from_steps)

            # Extended fields: related_tools
            related_tools = sorted(
                {e.get("tool_name", "") for e in step_outcomes if e.get("tool_name")}
            )

            # Extended fields: version (SKILL.md content hash)
            version = _compute_skill_version(skill_name)

            append_to_learnings(
                "skill-executions",
                {
                    "skill_name": skill_name,
                    "score": score,
                    "error_count": error_count,
                    "gp_violations": gp_violations,
                    "review_criticals": review_criticals,
                    "test_passed": test_passed,
                    "project": summary["project"],
                    "version": version,
                    "step_failures": step_failures,
                    "related_error_ids": related_error_ids,
                    "related_tools": related_tools,
                    "config_version": config_version,
                    "is_weight": is_weight,
                },
            )
            logger.info(
                "session-learner: skill '%s' score=%.2f",
                skill_name,
                score,
            )

        # RL: Per-step credit assignment → skill-credit.jsonl
        outcome_score = _OUTCOME_SCORES.get(summary["outcome"], 0.2)
        credits = step_credit(outcome_score, skill_invocations, events)
        for sname, credit in credits.items():
            append_to_learnings(
                "skill-credit",
                {
                    "skill_name": sname,
                    "credit": credit,
                    "outcome": summary["outcome"],
                    "outcome_score": outcome_score,
                    "config_version": config_version,
                    "is_weight": is_weight,
                },
            )

    # Critical Failure Step (CFS) detection — AgentRx-inspired
    cfs = _detect_critical_failure_step(events)
    cfs_data = {}
    if cfs:
        append_to_learnings("critical-failure-steps", cfs)
        logger.info(
            "session-learner: CFS at index %d (FM=%s): %s",
            cfs["cfs_index"],
            cfs["failure_mode"],
            cfs["message"][:80],
        )
        cfs_data = {
            "cfs_index": cfs["cfs_index"],
            "cfs_failure_mode": cfs["failure_mode"],
            "cfs_cascade_length": cfs["cascade_length"],
        }

    # Proposal quality tracking (autoresearch pattern)
    proposal_metrics = _compute_proposal_metrics(events)
    if proposal_metrics:
        for p in [e for e in events if e.get("category") == "proposal"]:
            append_to_learnings(
                "proposal-verdicts",
                {k: v for k, v in p.items() if k != "category"},
            )

    metrics = {
        "project": summary["project"],
        "cwd": summary["cwd"],
        "total_events": summary["total_events"],
        "errors_count": summary["errors_count"],
        "quality_issues": summary["quality_issues"],
        "patterns_found": summary["patterns_found"],
        "corrections": summary["corrections"],
        "outcome": summary["outcome"],
        "high_importance_count": summary["high_importance_count"],
        "avg_importance": summary["avg_importance"],
        "config_version": config_version,
        "is_weight": is_weight,
        **proposal_metrics,
        **cfs_data,
    }
    append_to_metrics(metrics)

    # Project Playbook: プロジェクト固有の知見を蓄積
    _update_playbook(summary, logger)

    # Repeated topic detection (Codified Context G4)
    _detect_repeated_topics(summary, logger)

    # Strategy Outcomes Database (EvoX Task B)
    approach = _classify_approach(events)
    task_type = _classify_task_type(summary)
    append_to_learnings(
        "strategy-outcomes",
        {
            "project": summary["project"],
            "task_type": task_type,
            "approach": approach,
            "context": {
                "error_count": summary["errors_count"],
                "quality_issues": summary["quality_issues"],
                "total_events": summary["total_events"],
            },
            "outcome": summary["outcome"],
            "improvement_delta": 0.0,
            "notes": "",
        },
    )
    logger.info(
        "session-learner: strategy outcome: %s/%s -> %s",
        task_type,
        approach,
        summary["outcome"],
    )

    # Stagnation state cleanup (EvoX Task A)
    stagnation_state = (
        Path.home() / ".claude" / "agent-memory" / "stagnation-state.json"
    )
    stagnation_state.unlink(missing_ok=True)

    logger.info(
        "session-learner: flushed %d errors, %d quality, %d patterns",
        summary["errors_count"],
        summary["quality_issues"],
        summary["patterns_found"],
    )


def main() -> None:
    logger = logging.getLogger("autoevolve")
    data = sys.stdin.read()
    try:
        process_session(cwd=os.getcwd())
    except Exception as e:
        logger.error("session-learner error: %s", e)
    sys.stdout.write(data)


if __name__ == "__main__":
    main()
