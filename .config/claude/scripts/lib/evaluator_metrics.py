"""Evaluator accuracy measurement library for AutoEvolve.

Computes TPR/TNR metrics by cross-referencing review-findings.jsonl
and review-feedback.jsonl, and measures hook effectiveness by tracking
failure mode recurrence in learnings.
"""

from __future__ import annotations


from lib.storage import get_data_dir, read_jsonl

RECURRING_THRESHOLD = 3


def _load_findings() -> list[dict]:
    """Load review findings from learnings/review-findings.jsonl."""
    return read_jsonl(get_data_dir() / "learnings" / "review-findings.jsonl")


def _load_feedback() -> list[dict]:
    """Load review feedback from learnings/review-feedback.jsonl."""
    return read_jsonl(get_data_dir() / "learnings" / "review-feedback.jsonl")


def _build_feedback_map(feedback: list[dict]) -> dict[str, str]:
    """Build a mapping from finding_id to outcome."""
    return {
        entry["finding_id"]: entry["outcome"]
        for entry in feedback
        if "finding_id" in entry and "outcome" in entry
    }


def _compute_accuracy_by(key_field: str) -> dict[str, dict]:
    """Compute per-group accept rate by cross-referencing findings and feedback.

    Groups findings by the given key_field (e.g. "reviewer" or "failure_mode"),
    then computes accept/ignore counts and rate for each group.

    Entries with empty key_field values are skipped.
    Returns an empty dict if no data is available.
    """
    findings = _load_findings()
    feedback = _load_feedback()
    if not findings or not feedback:
        return {}

    feedback_map = _build_feedback_map(feedback)
    groups: dict[str, dict] = {}

    for finding in findings:
        finding_id = finding.get("id", "")
        key = finding.get(key_field, "")
        if not finding_id or not key or finding_id not in feedback_map:
            continue

        if key not in groups:
            groups[key] = {"total": 0, "accepted": 0, "ignored": 0}

        outcome = feedback_map[finding_id]
        groups[key]["total"] += 1
        if outcome == "accepted":
            groups[key]["accepted"] += 1
        elif outcome == "ignored":
            groups[key]["ignored"] += 1

    for stats in groups.values():
        total = stats["total"]
        stats["accept_rate"] = round(stats["accepted"] / total, 4) if total > 0 else 0.0

    return groups


def compute_reviewer_accuracy() -> dict[str, dict]:
    """Compute per-reviewer accept rate by cross-referencing findings and feedback.

    Returns a dict keyed by reviewer name:
        {"code-reviewer": {"total": N, "accepted": N, "ignored": N, "accept_rate": 0.X}, ...}
    """
    return _compute_accuracy_by("reviewer")


def compute_fm_accuracy() -> dict[str, dict]:
    """Compute per-failure-mode accept rate.

    Same as compute_reviewer_accuracy but grouped by failure_mode.
    Entries with empty failure_mode are skipped.
    """
    return _compute_accuracy_by("failure_mode")


def compute_hook_effectiveness() -> dict[str, dict]:
    """Compute hook effectiveness by tracking failure mode recurrence.

    Reads all JSONL files under learnings/ (excluding review-findings.jsonl
    and review-feedback.jsonl), counts occurrences per failure_mode, and
    flags any FM with RECURRING_THRESHOLD+ occurrences as recurring.

    Returns:
        {"FM-001": {"count": N, "recurring": bool}, ...}

    Returns an empty dict if no data is available.
    """
    learnings_dir = get_data_dir() / "learnings"
    if not learnings_dir.exists():
        return {}

    exclude = {"review-findings.jsonl", "review-feedback.jsonl"}
    fm_counts: dict[str, int] = {}

    for jsonl_file in sorted(learnings_dir.glob("*.jsonl")):
        if jsonl_file.name in exclude:
            continue
        for entry in read_jsonl(jsonl_file):
            fm = entry.get("failure_mode", "")
            if fm:
                fm_counts[fm] = fm_counts.get(fm, 0) + 1

    return {
        fm: {"count": count, "recurring": count >= RECURRING_THRESHOLD}
        for fm, count in fm_counts.items()
    }


def format_evaluator_report(
    reviewer_acc: dict[str, dict],
    fm_acc: dict[str, dict],
    hook_eff: dict[str, dict],
) -> str:
    """Generate a Markdown report from evaluator metrics.

    Args:
        reviewer_acc: Output of compute_reviewer_accuracy()
        fm_acc: Output of compute_fm_accuracy()
        hook_eff: Output of compute_hook_effectiveness()

    Returns:
        A Markdown-formatted string with three sections.
    """
    lines: list[str] = []

    # Section 1: Reviewer Accuracy
    # Note: "Total" counts only findings with matched feedback entries.
    lines.append("## Reviewer Accuracy\n")
    if reviewer_acc:
        lines.append("| Reviewer | Total | Accepted | Ignored | Accept Rate |")
        lines.append("|----------|-------|----------|---------|-------------|")
        for reviewer, stats in sorted(reviewer_acc.items()):
            rate = f"{stats['accept_rate'] * 100:.1f}%"
            lines.append(
                f"| {reviewer} | {stats['total']} | {stats['accepted']} "
                f"| {stats['ignored']} | {rate} |"
            )
    else:
        lines.append("No reviewer data available.")
    lines.append("")

    # Section 2: Failure Mode Accuracy
    lines.append("## Failure Mode Accuracy\n")
    if fm_acc:
        lines.append("| Failure Mode | Total | Accepted | Ignored | Accept Rate |")
        lines.append("|--------------|-------|----------|---------|-------------|")
        for fm, stats in sorted(fm_acc.items()):
            rate = f"{stats['accept_rate'] * 100:.1f}%"
            lines.append(
                f"| {fm} | {stats['total']} | {stats['accepted']} "
                f"| {stats['ignored']} | {rate} |"
            )
    else:
        lines.append("No failure mode data available.")
    lines.append("")

    # Section 3: Hook Effectiveness
    lines.append("## Hook Effectiveness\n")
    if hook_eff:
        lines.append("| Failure Mode | Count | Recurring |")
        lines.append("|--------------|-------|-----------|")
        for fm, stats in sorted(hook_eff.items()):
            recurring_label = "Yes (recurring)" if stats["recurring"] else "No"
            lines.append(f"| {fm} | {stats['count']} | {recurring_label} |")
    else:
        lines.append("No hook effectiveness data available.")
    lines.append("")

    return "\n".join(lines)
