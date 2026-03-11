#!/usr/bin/env python3
"""Completion Gate — run tests before allowing agent to stop.

Detects project type, runs appropriate test command, and injects failure
info as additionalContext so the agent can self-correct.
Uses a retry counter to prevent infinite loops (max 2 retries).
Ref: Harness Engineering Best Practices 2026 — "Completion Gates (Stop)"

Triggered by: hooks.Stop
Output: JSON with additionalContext on stdout (if tests fail)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

MAX_RETRIES = 2
COUNTER_DIR = os.path.join(tempfile.gettempdir(), "claude-completion-gate")
COUNTER_FILE = os.path.join(COUNTER_DIR, "retries")

# Ralph Loop — active plan detection
PLAN_DIRS = [
    os.path.join(os.getcwd(), "docs", "plans", "active"),
    os.path.join(os.getcwd(), "tmp", "plans"),
]


def _get_retry_count() -> int:
    try:
        with open(COUNTER_FILE) as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def _set_retry_count(n: int) -> None:
    os.makedirs(COUNTER_DIR, exist_ok=True)
    with open(COUNTER_FILE, "w") as f:
        f.write(str(n))


def _reset_retries() -> None:
    try:
        os.remove(COUNTER_FILE)
    except FileNotFoundError:
        pass


def _detect_test_command() -> str | None:
    """Detect the appropriate test command for the current project."""
    cwd = os.getcwd()

    # Node.js — check for test script in package.json
    pkg_json = os.path.join(cwd, "package.json")
    if os.path.exists(pkg_json):
        try:
            with open(pkg_json) as f:
                pkg = json.load(f)
            if "test" in pkg.get("scripts", {}):
                # Detect package manager
                if os.path.exists(os.path.join(cwd, "bun.lockb")):
                    return "bun test"
                if os.path.exists(os.path.join(cwd, "pnpm-lock.yaml")):
                    return "pnpm test"
                return "npm test"
        except Exception:
            pass

    # Go
    if os.path.exists(os.path.join(cwd, "go.mod")):
        return "go test ./..."

    # Python — pytest if pyproject.toml or conftest.py exists
    if os.path.exists(os.path.join(cwd, "pyproject.toml")) or os.path.exists(
        os.path.join(cwd, "conftest.py")
    ):
        return "python3 -m pytest --tb=short -q"

    # Rust
    if os.path.exists(os.path.join(cwd, "Cargo.toml")):
        return "cargo test"

    # bats (shell script tests)
    if os.path.isdir(os.path.join(cwd, "test")) and any(
        f.endswith(".bats") for f in os.listdir(os.path.join(cwd, "test"))
    ):
        return "bats test/"

    return None


def _run_tests(cmd: str) -> tuple[bool, str]:
    """Run tests and return (success, output)."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.getcwd(),
            env={**os.environ, "NO_COLOR": "1", "CI": "1"},
        )
        output = (result.stdout + result.stderr).strip()
        # Limit output to last 30 lines
        lines = output.split("\n")
        if len(lines) > 30:
            output = "\n".join(["...(truncated)"] + lines[-30:])
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "テストがタイムアウトしました (120秒)"
    except Exception:
        # If we can't run tests, don't block
        return True, ""


def _find_incomplete_plan() -> tuple[str, list[str]] | None:
    """Find active plan with unchecked items. Returns (plan_file, pending_items)."""
    import glob

    for plan_dir in PLAN_DIRS:
        if not os.path.isdir(plan_dir):
            continue
        for plan_file in glob.glob(os.path.join(plan_dir, "*.md")):
            try:
                with open(plan_file) as f:
                    lines = f.readlines()
            except OSError:
                continue
            pending = [ln.strip() for ln in lines if ln.strip().startswith("- [ ]")]
            if pending:
                return (os.path.basename(plan_file), pending)
    return None


def main() -> None:
    retries = _get_retry_count()

    # Safety valve: if we've hit max retries, allow stop
    if retries >= MAX_RETRIES:
        _reset_retries()
        print(
            f"[Completion Gate] リトライ上限({MAX_RETRIES}回)に到達。停止を許可します。",
            file=sys.stderr,
        )
        return

    # --- Ralph Loop: check for incomplete active plans ---
    incomplete = _find_incomplete_plan()
    if incomplete:
        plan_name, pending = incomplete
        shown = pending[:5]
        remaining_count = len(pending) - len(shown)

        ctx_parts = [
            f"[Ralph Loop] アクティブプラン '{plan_name}' に未完了ステップがあります:",
            "",
        ]
        ctx_parts.extend(shown)
        if remaining_count > 0:
            ctx_parts.append(f"  ...他 {remaining_count} 件")
        ctx_parts.extend(
            [
                "",
                "タスクを続行してください。完了不要なら、プランを completed/ に移動してから停止してください。",
            ]
        )

        _set_retry_count(retries + 1)
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "Stop",
                    "additionalContext": "\n".join(ctx_parts),
                }
            },
            sys.stdout,
        )
        return

    # --- Test gate ---
    test_cmd = _detect_test_command()
    if not test_cmd:
        _reset_retries()
        return

    success, output = _run_tests(test_cmd)

    if success:
        _reset_retries()
        print(f"[Completion Gate] テスト通過 ({test_cmd})", file=sys.stderr)
        return

    # Tests failed — increment retry counter and report
    _set_retry_count(retries + 1)
    remaining = MAX_RETRIES - retries - 1

    ctx_lines = [
        f"[Completion Gate] テストが失敗しています: `{test_cmd}`",
        f"リトライ残り: {remaining}回 (上限到達で自動停止許可)",
        "",
        "```",
        output,
        "```",
        "",
        "FIX: テストを通過させてから完了してください。",
    ]

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "Stop",
                "additionalContext": "\n".join(ctx_lines),
            }
        },
        sys.stdout,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[completion-gate] error: {e}", file=sys.stderr)
