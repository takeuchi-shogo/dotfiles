#!/usr/bin/env python3
"""Plan lifecycle hook — tracks plan status based on git commits.

Triggered by: hooks.PostToolUse (Bash)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext suggestion on stdout

Checks if git commit messages reference active plans and suggests
moving them to completed/ when sufficient progress is detected.
"""
import json
import os
import subprocess
import sys


PLANS_DIR = "docs/plans/active"


def get_repo_root() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def get_active_plans(repo_root: str) -> list[str]:
    active_dir = os.path.join(repo_root, PLANS_DIR)
    if not os.path.isdir(active_dir):
        return []
    return [
        f for f in os.listdir(active_dir)
        if f.endswith(".md") and not f.startswith(".")
    ]


def extract_plan_references(commit_msg: str, plans: list[str]) -> list[str]:
    referenced = []
    msg_lower = commit_msg.lower()
    for plan in plans:
        name_parts = plan.replace(".md", "").split("-", 3)
        if len(name_parts) >= 4:
            topic = name_parts[3]
        else:
            topic = plan.replace(".md", "")

        if topic.lower() in msg_lower:
            referenced.append(plan)

    return referenced


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = data.get("tool_name", "")
    if tool_name != "Bash":
        json.dump(data, sys.stdout)
        return

    command = data.get("tool_input", {}).get("command", "")

    if "git commit" not in command:
        json.dump(data, sys.stdout)
        return

    output = data.get("tool_output", "") or ""
    if (
        "file changed" not in output.lower()
        and "files changed" not in output.lower()
        and "insertion" not in output.lower()
        and "create mode" not in output.lower()
    ):
        json.dump(data, sys.stdout)
        return

    repo_root = get_repo_root()
    if not repo_root:
        json.dump(data, sys.stdout)
        return

    plans = get_active_plans(repo_root)
    if not plans:
        json.dump(data, sys.stdout)
        return

    # Get actual commit message from git log (immune to HEREDOC/quoting)
    try:
        log_result = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            capture_output=True, text=True, cwd=repo_root, timeout=5,
        )
        commit_msg = log_result.stdout.strip() if log_result.returncode == 0 else ""
    except (FileNotFoundError, subprocess.TimeoutExpired):
        commit_msg = ""

    if not commit_msg:
        json.dump(data, sys.stdout)
        return

    referenced = extract_plan_references(commit_msg, plans)
    if referenced:
        plan_list = ", ".join(f"`{p}`" for p in referenced)
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    f"[plan-lifecycle] アクティブ計画 {plan_list} に関連するコミットを検出。\n"
                    "計画が完了した場合は `docs/plans/active/` → `docs/plans/completed/` に移動してください。"
                ),
            }
        }, sys.stdout)
        return

    json.dump(data, sys.stdout)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[plan-lifecycle] error: {e}", file=sys.stderr)
        json.dump({}, sys.stdout)
