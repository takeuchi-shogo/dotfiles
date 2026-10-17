#!/usr/bin/env python3
"""Review persistence gate — /review 後に Run Metrics が未記録なら 1 回 block する。

Triggered by: hooks.Stop
Input: stdin JSON (transcript_path, stop_hook_active)
Output: {"decision": "block", "reason": ...} on stdout, or nothing.

最後の Skill(review) 呼び出し以降に review-metrics.jsonl の追記が無ければ block。
metrics の session_id は pid fallback で突合できないため timestamp で突合する。
入力欠落・破損・I/O エラーは全て allow (セッションを詰まらせない)。
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from storage import get_data_dir

REASON = (
    "/review を実行しましたが review-metrics.jsonl に"
    " Run Metrics が記録されていません。"
    "skills/review/SKILL.md の Run Metrics 記録 (emit_review_metrics) を実行し、"
    "指摘があれば Step 6 (Findings Persistence) も行ってください。"
    "この /review について block するのは 1 回だけです。"
)
MARKER_DIR = (
    Path(
        os.environ.get(
            "CLAUDE_SESSION_STATE_DIR",
            os.path.join(os.environ.get("HOME", ""), ".claude", "session-state"),
        )
    )
    / "review-persistence"
)


def _parse_ts(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else None


def _last_review_invocation(transcript: Path) -> datetime | None:
    last = None
    for line in transcript.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if not isinstance(entry, dict) or entry.get("type") != "assistant":
            continue
        content = (entry.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if (
                isinstance(block, dict)
                and block.get("type") == "tool_use"
                and block.get("name") == "Skill"
                and (block.get("input") or {}).get("skill") == "review"
            ):
                ts = _parse_ts(entry.get("timestamp"))
                if ts:
                    last = ts
    return last


def _has_metrics_since(since: datetime) -> bool:
    path = get_data_dir() / "learnings" / "review-metrics.jsonl"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return False
    for line in lines:
        try:
            ts = _parse_ts(json.loads(line).get("timestamp"))
        except (ValueError, AttributeError):
            continue
        if ts and ts >= since:
            return True
    return False


def main() -> None:
    try:
        data = json.load(sys.stdin)
        if data.get("stop_hook_active"):
            return
        since = _last_review_invocation(Path(data["transcript_path"]))
        if since is None or _has_metrics_since(since):
            return
        session = str(data.get("session_id") or "unknown").replace("/", "_")
        marker = MARKER_DIR / f"{session}-{int(since.timestamp() * 1_000_000)}"
        MARKER_DIR.mkdir(parents=True, exist_ok=True)
        try:
            open(marker, "x").close()
        except FileExistsError:
            return
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(f"[review-persistence-gate] skipped: {exc}", file=sys.stderr)
        return
    json.dump({"decision": "block", "reason": REASON}, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
