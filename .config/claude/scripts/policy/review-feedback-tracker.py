#!/usr/bin/env python3
"""Review feedback tracker — PostToolUse(Bash) hook.

git commit を検出したら、pending な review findings と
commit の diff を照合し、指摘対象のファイル:行が変更されていれば
"accepted"、されていなければ "ignored" と判定する。


結果は review-feedback.jsonl に記録される。

サブエージェントのコンテキストを汚染しないよう、Python 内で完結する。
"""

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from session_events import (
    emit_review_feedback,
    read_pending_findings,
)


def _parse_review_scores(text: str) -> dict[str, str] | None:
    """Review Scores ブロックをパースする。

    Returns:
        {"correctness": "4/5", ...} or None if not found
    """
    match = re.search(r"## Review Scores\n((?:[a-z]+: .+\n)+)", text)
    if not match:
        return None
    scores: dict[str, str] = {}
    for line in match.group(1).strip().split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            if key != "weakest":
                scores[key] = val
    return scores if scores else None


def _is_git_commit(command: str) -> bool:
    """コマンドが git commit であるか判定する。"""
    return bool(re.search(r"\bgit\s+commit\b", command))


def _get_committed_diff() -> str:
    """直前のコミットの diff を取得する。"""
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD~1..HEAD", "--unified=0"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout
    except Exception:
        return ""


def _parse_diff_changed_lines(diff_text: str) -> dict[str, set[int]]:
    """diff から変更されたファイルと行番号のマップを返す。

    Returns:
        {"file.go": {42, 43, 44}, "api.ts": {10, 11}}
    """
    changed: dict[str, set[int]] = {}
    current_file = ""

    for line in diff_text.split("\n"):
        if line.startswith("+++ b/"):
            current_file = line[6:]
        elif line.startswith("@@ ") and current_file:
            match = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if match:
                start = int(match.group(1))
                count = int(match.group(2)) if match.group(2) else 1
                if current_file not in changed:
                    changed[current_file] = set()
                for i in range(start, start + count):
                    changed[current_file].add(i)

    return changed


def _match_finding_to_diff(finding: dict, changed_lines: dict[str, set[int]]) -> str:
    """finding が diff の変更範囲に含まれるか判定する。

    Returns: "accepted" | "ignored"
    """
    file_path = finding.get("file", "")
    line = finding.get("line", 0)

    for diff_file, lines in changed_lines.items():
        if diff_file.endswith(file_path) or file_path.endswith(diff_file):
            if line == 0:
                return "accepted"
            proximity = 5
            for changed_line in lines:
                if abs(changed_line - line) <= proximity:
                    return "accepted"

    return "ignored"


def main() -> None:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            json.dump({}, sys.stdout)
            return

        hook_input = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        json.dump({}, sys.stdout)
        return

    command = hook_input.get("tool_input", {}).get("command", "")

    if not _is_git_commit(command):
        json.dump(hook_input, sys.stdout)
        return

    pending = read_pending_findings()
    if not pending:
        json.dump(hook_input, sys.stdout)
        return

    diff_text = _get_committed_diff()
    if not diff_text:
        json.dump(hook_input, sys.stdout)
        return

    changed_lines = _parse_diff_changed_lines(diff_text)

    accepted_count = 0
    ignored_count = 0

    for finding in pending:
        finding_id = finding.get("id", "")
        if not finding_id:
            continue
        outcome = _match_finding_to_diff(finding, changed_lines)
        emit_review_feedback(finding_id, outcome)
        if outcome == "accepted":
            accepted_count += 1
        else:
            ignored_count += 1

    if accepted_count + ignored_count > 0:
        context = (
            f"[Review Feedback] "
            f"{accepted_count + ignored_count} 件のレビュー指摘を追跡: "
            f"{accepted_count} accepted, {ignored_count} ignored"
        )
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": context,
                }
            },
            sys.stdout,
        )
    else:
        json.dump(hook_input, sys.stdout)


if __name__ == "__main__":
    main()
