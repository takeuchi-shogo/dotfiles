#!/usr/bin/env python3
"""AutoEvolve session learner — flushes session events to persistent storage.

Triggered by: hooks.Stop / hooks.SessionEnd
Input: stdin passthrough
Output: stdout passthrough
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from session_events import append_to_learnings, append_to_metrics, flush_session


def build_session_summary(cwd: str | None = None) -> dict:
    """セッションイベントを集約してサマリーを構築する。"""
    events = flush_session()

    errors = [e for e in events if e.get("category") == "error"]
    quality = [e for e in events if e.get("category") == "quality"]
    patterns = [e for e in events if e.get("category") == "pattern"]
    corrections = [e for e in events if e.get("category") == "correction"]

    project = Path(cwd).name if cwd else "unknown"

    return {
        "project": project,
        "cwd": cwd or os.getcwd(),
        "total_events": len(events),
        "errors_count": len(errors),
        "quality_issues": len(quality),
        "patterns_found": len(patterns),
        "corrections": len(corrections),
        "_errors": errors,
        "_quality": quality,
        "_patterns": patterns,
        "_corrections": corrections,
    }


def process_session(cwd: str | None = None) -> None:
    """セッションデータを処理し、永続ストレージに書き出す。"""
    summary = build_session_summary(cwd=cwd)

    if summary["total_events"] == 0:
        return

    for error in summary["_errors"]:
        entry = {k: v for k, v in error.items() if k != "category"}
        append_to_learnings("errors", entry)

    for issue in summary["_quality"]:
        entry = {k: v for k, v in issue.items() if k != "category"}
        append_to_learnings("quality", entry)

    for pattern in summary["_patterns"]:
        entry = {k: v for k, v in pattern.items() if k != "category"}
        append_to_learnings("patterns", entry)

    metrics = {
        "project": summary["project"],
        "cwd": summary["cwd"],
        "total_events": summary["total_events"],
        "errors_count": summary["errors_count"],
        "quality_issues": summary["quality_issues"],
        "patterns_found": summary["patterns_found"],
        "corrections": summary["corrections"],
    }
    append_to_metrics(metrics)


def main() -> None:
    data = sys.stdin.read()
    try:
        process_session(cwd=os.getcwd())
    except Exception as e:
        print(f"[session-learner] error: {e}", file=sys.stderr)
    sys.stdout.write(data)


if __name__ == "__main__":
    main()
