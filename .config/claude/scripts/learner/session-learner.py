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

    return {
        "project": project,
        "cwd": cwd or os.getcwd(),
        "total_events": len(events),
        "errors_count": len(errors),
        "quality_issues": len(quality),
        "patterns_found": len(patterns),
        "corrections": len(corrections),
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
        existing = f"# {project} Playbook\n\nProject-specific learnings (auto-accumulated).\n\n"

    new_content = existing.rstrip() + "\n" + "\n".join(entries) + "\n"

    lines = new_content.splitlines()
    if len(lines) > 100:
        header = lines[:4]
        body = lines[4:]
        lines = header + body[-(100 - len(header)) :]
        new_content = "\n".join(lines) + "\n"

    playbook_path.write_text(new_content, encoding="utf-8")
    logger.info("session-learner: updated playbook for %s", project)


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


def process_session(cwd: str | None = None) -> None:
    """セッションデータを処理し、永続ストレージに書き出す。"""
    logger = logging.getLogger("autoevolve")
    summary = build_session_summary(cwd=cwd)

    if summary["total_events"] == 0:
        return

    logger.info(
        "session-learner: processing %d events for %s",
        summary["total_events"],
        summary["project"],
    )

    for error in summary["_errors"]:
        entry = {k: v for k, v in error.items() if k != "category"}
        append_to_learnings("errors", entry)

    for issue in summary["_quality"]:
        entry = {k: v for k, v in issue.items() if k != "category"}
        append_to_learnings("quality", entry)

    for pattern in summary["_patterns"]:
        entry = {k: v for k, v in pattern.items() if k != "category"}
        append_to_learnings("patterns", entry)

    # スキル実行データの集計
    events = summary["_events"]
    quality = summary["_quality"]
    skill_invocations = [
        e
        for e in events
        if e.get("category") == "skill" and e.get("type") == "invocation"
    ]
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

            # Extended fields: related_error_ids (スキルスコープのエラーのみ)
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
                },
            )
            logger.info(
                "session-learner: skill '%s' score=%.2f",
                skill_name,
                score,
            )

    metrics = {
        "project": summary["project"],
        "cwd": summary["cwd"],
        "total_events": summary["total_events"],
        "errors_count": summary["errors_count"],
        "quality_issues": summary["quality_issues"],
        "patterns_found": summary["patterns_found"],
        "corrections": summary["corrections"],
        "high_importance_count": summary["high_importance_count"],
        "avg_importance": summary["avg_importance"],
    }
    append_to_metrics(metrics)

    # Project Playbook: プロジェクト固有の知見を蓄積
    _update_playbook(summary, logger)

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
