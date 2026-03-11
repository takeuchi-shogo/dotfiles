#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def run_git(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def build_checkpoint(args: argparse.Namespace) -> str:
    timestamp = datetime.now(timezone.utc).isoformat()
    branch = run_git(["branch", "--show-current"])
    status = run_git(["status", "--short"])
    lines = [
        "# Codex Checkpoint",
        "",
        f"- Timestamp: {timestamp}",
        f"- Goal: {args.goal}",
    ]
    if branch:
        lines.append(f"- Branch: {branch}")
    lines.extend(
        [
            "",
            "## Summary",
            args.summary,
            "",
            "## Next Step",
            args.next_step,
        ]
    )

    if args.file:
        lines.extend(["", "## Focus Files"])
        lines.extend([f"- {file_path}" for file_path in args.file])

    if args.command:
        lines.extend(["", "## Pending Commands"])
        lines.extend([f"- `{command}`" for command in args.command])

    if args.risk:
        lines.extend(["", "## Open Risks"])
        lines.extend([f"- {risk}" for risk in args.risk])

    if status:
        lines.extend(["", "## Git Status", "```", status, "```"])

    resume_prompt = (
        "Read tmp/codex-state/latest-checkpoint.md, confirm current git status, "
        "and continue from the recorded Next Step."
    )
    lines.extend(["", "## Resume Prompt", resume_prompt, ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--goal", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--next-step", required=True, dest="next_step")
    parser.add_argument("--file", action="append", default=[])
    parser.add_argument("--command", action="append", default=[])
    parser.add_argument("--risk", action="append", default=[])
    parser.add_argument("--state-dir", default="tmp/codex-state")
    args = parser.parse_args()

    state_dir = Path(args.state_dir)
    checkpoints_dir = state_dir / "checkpoints"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)

    content = build_checkpoint(args)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    latest_path = state_dir / "latest-checkpoint.md"
    archive_path = checkpoints_dir / f"{timestamp}-checkpoint.md"

    latest_path.write_text(content, encoding="utf-8")
    archive_path.write_text(content, encoding="utf-8")
    print(latest_path)
    print(archive_path)


if __name__ == "__main__":
    main()
