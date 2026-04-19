#!/usr/bin/env python3
"""
Reviewer Calibration: track TPR/TNR for codex-reviewer, code-reviewer,
security-reviewer.

Data source:
  - ~/.claude/projects/<project>/*/subagents/agent-*.jsonl
  - ~/.claude/logs/session-*.jsonl
  - Ground truth: human override events (accepted/rejected reviewer verdict)

Metrics:
  - TPR (True Positive Rate): reviewer flagged issue → human confirmed real
  - TNR (True Negative Rate): reviewer passed → no issue found later

Output:
  - JSONL: ~/.claude/logs/reviewer-calibration-{date}.jsonl
  - Rolling 30-day window per reviewer

Algorithm:
  1. Load session logs from last 30 days
  2. Extract review events: {reviewer, verdict, outcome}
  3. Compute TPR = confirmed_blocks / all_blocks
  4. Compute TNR = clean_passes / all_passes
  5. Flag reviewers with TPR < 0.5 or TNR < 0.7 for calibration review
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

# ── Constants ─────────────────────────────────────────────────

WINDOW_DAYS = 30
TPR_WARN_THRESHOLD = 0.5
TNR_WARN_THRESHOLD = 0.7

REVIEWERS = ["codex-reviewer", "code-reviewer", "security-reviewer"]

REVIEWER_FIELDS = ["reviewer", "agent_type", "subagent_type", "tool", "agent"]
VERDICT_FIELDS = ["verdict", "decision", "result", "status"]
OUTCOME_FIELDS = ["outcome", "human_verdict", "user_decision"]

_EMPTY_COUNTS = {"tp": 0, "fp": 0, "tn": 0, "fn": 0, "deferred": 0}


# ── Log loading ───────────────────────────────────────────────


def find_session_logs(log_dir: Path, window_days: int) -> list[Path]:
    """Collect all relevant JSONL log files within the time window."""
    cutoff = datetime.now() - timedelta(days=window_days)
    found: list[Path] = []

    if log_dir.exists():
        for p in sorted(log_dir.glob("session-*.jsonl")):
            if datetime.fromtimestamp(p.stat().st_mtime) >= cutoff:
                found.append(p)

    projects_dir = log_dir.parent / "projects"
    if projects_dir.exists():
        pattern = "*/*/subagents/agent-*.jsonl"
        for p in sorted(projects_dir.glob(pattern)):
            if datetime.fromtimestamp(p.stat().st_mtime) >= cutoff:
                found.append(p)

    return found


def _get_str_field(record: dict, fields: list[str]) -> str | None:
    """Return first non-empty string value matching any of the given fields."""
    for field in fields:
        val = record.get(field)
        if isinstance(val, str) and val:
            return val
    return None


def _extract_reviewer(record: dict) -> str | None:
    """Flexibly extract reviewer name from a log record."""
    val = _get_str_field(record, REVIEWER_FIELDS)
    if val:
        return val
    msg = record.get("message", {})
    if isinstance(msg, dict):
        return _get_str_field(msg, REVIEWER_FIELDS)
    return None


def _extract_verdict(record: dict) -> str | None:
    """Flexibly extract verdict (block/pass) from a log record."""
    val = _get_str_field(record, VERDICT_FIELDS)
    return val.lower() if val else None


def _extract_outcome(record: dict) -> str | None:
    """Flexibly extract outcome from a log record."""
    val = _get_str_field(record, OUTCOME_FIELDS)
    return val.lower() if val else None


def _parse_record(record: dict, log_file: Path, known: set[str]) -> dict | None:
    """Return a normalized review event dict, or None if not a review event."""
    rec_type = record.get("type", "")
    if rec_type == "review_event":
        return record

    reviewer = _extract_reviewer(record)
    verdict = _extract_verdict(record)
    if reviewer and verdict and reviewer in known:
        return {
            "reviewer": reviewer,
            "verdict": verdict,
            "outcome": _extract_outcome(record) or "unknown",
            "_source": str(log_file),
            "_original_type": rec_type,
        }
    return None


def load_review_events(log_files: list[Path]) -> list[dict]:
    """Load review events from all log files."""
    events: list[dict] = []
    known = set(REVIEWERS)

    for log_file in log_files:
        try:
            with log_file.open(encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    event = _parse_record(record, log_file, known)
                    if event is not None:
                        events.append(event)
        except (OSError, PermissionError):
            continue

    return events


# ── Metrics computation ───────────────────────────────────────


def compute_metrics(events: list[dict]) -> dict[str, dict]:
    """Compute TPR/TNR per reviewer.

    Confusion matrix:
      block + confirmed           → TP
      block + rejected            → FP
      block + unknown             → deferred (not counted in TPR)
      pass  + confirmed           → TN (pass was correct)
      pass  + rejected            → FN (pass missed the issue)
      pass  + unknown             → deferred (not counted in TNR)
    """
    stats: dict[str, dict] = defaultdict(
        lambda: {"tp": 0, "fp": 0, "tn": 0, "fn": 0, "deferred": 0}
    )

    for e in events:
        reviewer = e.get("reviewer", "unknown")
        verdict = (e.get("verdict") or "").lower()
        outcome = (e.get("outcome") or "unknown").lower()

        if verdict == "block":
            if outcome == "confirmed":
                stats[reviewer]["tp"] += 1
            elif outcome in ("rejected_by_human", "rejected"):
                stats[reviewer]["fp"] += 1
            elif outcome == "unknown":
                stats[reviewer]["deferred"] += 1
        elif verdict == "pass":
            if outcome == "confirmed":
                stats[reviewer]["tn"] += 1
            elif outcome in ("rejected_by_human", "rejected"):
                stats[reviewer]["fn"] += 1
            elif outcome == "unknown":
                stats[reviewer]["deferred"] += 1

    results: dict[str, dict] = {}
    for reviewer, s in stats.items():
        # deferred is excluded from TPR/TNR denominators
        total_blocks = s["tp"] + s["fp"]
        total_passes = s["tn"] + s["fn"]
        tpr = s["tp"] / total_blocks if total_blocks > 0 else None
        tnr = s["tn"] / total_passes if total_passes > 0 else None
        results[reviewer] = {
            "tpr": tpr,
            "tnr": tnr,
            "counts": dict(s),
            "event_count": total_blocks + total_passes,
            "deferred_count": s["deferred"],
            "tpr_warn": tpr is not None and tpr < TPR_WARN_THRESHOLD,
            "tnr_warn": tnr is not None and tnr < TNR_WARN_THRESHOLD,
        }

    return results


# ── Output helpers ────────────────────────────────────────────


def _fmt(val: float | None) -> str:
    return f"{val:.2f}" if val is not None else "N/A"


def _reviewer_summary_line(reviewer: str, m: dict) -> str:
    """Return a single summary line for one reviewer."""
    tpr_str = _fmt(m["tpr"])
    tnr_str = _fmt(m["tnr"])
    warns: list[str] = []
    if m["tpr_warn"]:
        warns.append(f"TPR={tpr_str}<{TPR_WARN_THRESHOLD} (false alarms)")
    if m["tnr_warn"]:
        warns.append(f"TNR={tnr_str}<{TNR_WARN_THRESHOLD} (missing issues)")
    cnt = m["event_count"]
    deferred = m.get("deferred_count", 0)
    suffix = f" | events={cnt}, deferred={deferred}"
    if warns:
        return f"  [WARN] {reviewer}: {', '.join(warns)}{suffix}"
    return f"  [ok]   {reviewer}: TPR={tpr_str}, TNR={tnr_str}{suffix}"


def print_summary(metrics: dict[str, dict], total_events: int) -> None:
    """Print human-readable calibration summary to stdout."""
    print(f"[reviewer-calibration] window={WINDOW_DAYS}d, events={total_events}")

    if not metrics:
        for reviewer in REVIEWERS:
            print(f"  {reviewer}: TPR=N/A, TNR=N/A (no events)")
        return

    for reviewer in REVIEWERS + sorted(set(metrics) - set(REVIEWERS)):
        if reviewer not in metrics:
            print(f"  {reviewer}: TPR=N/A, TNR=N/A (no events)")
        else:
            print(_reviewer_summary_line(reviewer, metrics[reviewer]))


# ── Output record builder ─────────────────────────────────────


def _reviewer_record(reviewer: str, metrics: dict[str, dict]) -> dict:
    """Build the per-reviewer JSONL sub-record."""
    m = metrics.get(reviewer)
    if m is None:
        return {
            "tpr": None,
            "tpr_display": "N/A",
            "tnr": None,
            "tnr_display": "N/A",
            "counts": dict(_EMPTY_COUNTS),
            "event_count": 0,
            "deferred_count": 0,
            "tpr_warn": False,
            "tnr_warn": False,
        }
    return {
        "tpr": m["tpr"],
        "tpr_display": _fmt(m["tpr"]),
        "tnr": m["tnr"],
        "tnr_display": _fmt(m["tnr"]),
        "counts": m["counts"],
        "event_count": m["event_count"],
        "deferred_count": m.get("deferred_count", 0),
        "tpr_warn": m["tpr_warn"],
        "tnr_warn": m["tnr_warn"],
    }


def build_output(
    metrics: dict[str, dict], events: list[dict], log_files: list[Path]
) -> dict:
    """Assemble the JSONL output record."""
    reviewers: dict[str, dict] = {r: _reviewer_record(r, metrics) for r in REVIEWERS}
    for reviewer in metrics:
        if reviewer not in reviewers:
            reviewers[reviewer] = _reviewer_record(reviewer, metrics)

    return {
        "date": date.today().isoformat(),
        "window_days": WINDOW_DAYS,
        "event_count": len(events),
        "log_files_scanned": len(log_files),
        "reviewers": reviewers,
        "thresholds": {
            "tpr_warn": TPR_WARN_THRESHOLD,
            "tnr_warn": TNR_WARN_THRESHOLD,
        },
    }


def write_output(output: dict, log_dir: Path) -> Path:
    """Write output record to JSONL and return the path."""
    out_path = log_dir / f"reviewer-calibration-{date.today()}.jsonl"
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"[warn] could not write JSONL: {e}", file=sys.stderr)
    return out_path


# ── Main ──────────────────────────────────────────────────────


def main() -> None:
    log_dir = Path.home() / ".claude" / "logs"
    log_files = find_session_logs(log_dir, WINDOW_DAYS)
    events = load_review_events(log_files)

    if not events:
        print(f"[info] no review events found in last {WINDOW_DAYS} days")

    metrics = compute_metrics(events)
    output = build_output(metrics, events, log_files)
    out_path = write_output(output, log_dir)

    print_summary(metrics, len(events))
    print(f"[reviewer-calibration] output → {out_path}")


if __name__ == "__main__":
    main()
