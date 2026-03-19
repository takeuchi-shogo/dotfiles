#!/usr/bin/env python3
"""Completion Gate — run tests before allowing agent to stop.

Detects project type, runs appropriate test command, and injects failure
info as additionalContext so the agent can self-correct.
Uses a retry counter to prevent infinite loops (max 2 retries).

Features:
  - Selective test running: run related tests first, then full suite (Stripe Minions)
  - Graduated completion: partial handback with structured report (Stripe Minions)
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

# Graduated completion mode (Stripe Minions pattern)
# "strict" = default, block on test failure
# "graduated" = allow partial completion with handback report
COMPLETION_MODE = os.environ.get("COMPLETION_MODE", "strict")
COUNTER_DIR = os.path.join(tempfile.gettempdir(), "claude-completion-gate")
COUNTER_FILE = os.path.join(COUNTER_DIR, "retries")

# Ralph Loop — active plan detection
PLAN_DIRS = [
    os.path.join(os.getcwd(), "docs", "plans", "active"),
    os.path.join(os.getcwd(), "tmp", "plans"),
]

# Review Gate — edit count threshold for review reminder
REVIEW_EDIT_THRESHOLD = 10
EDIT_COUNTER_FILE = os.path.join(
    os.environ.get(
        "CLAUDE_SESSION_STATE_DIR",
        os.path.join(os.environ.get("HOME", ""), ".claude", "session-state"),
    ),
    "edit-counter.json",
)


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


SNAPSHOT_FILE = os.path.join(
    os.environ.get(
        "CLAUDE_SESSION_STATE_DIR",
        os.path.join(os.environ.get("HOME", ""), ".claude", "session-state"),
    ),
    "active-plans-snapshot.json",
)


def _load_plan_snapshot() -> dict:
    """Load the session-start snapshot of active plans."""
    try:
        with open(SNAPSHOT_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _is_session_relevant(plan_name: str, plan_path: str, snapshot: dict) -> bool:
    """Check if a plan was created or modified during the current session."""
    if not snapshot or "plans" not in snapshot:
        # No snapshot = no session-load ran
        # Treat all plans as relevant (backward compat)
        return True

    known = snapshot.get("plans", {})
    if plan_name not in known:
        # Plan was created after session start
        return True

    try:
        current_mtime = os.path.getmtime(plan_path)
        snapshot_mtime = known[plan_name].get("mtime", 0)
        # Modified since session start (tolerance: 1 second)
        if current_mtime > snapshot_mtime / 1000 + 1:
            return True
    except OSError:
        return True

    return False


def _find_incomplete_plan() -> tuple[str, list[str]] | None:
    """Find active plan with unchecked items that is relevant to the current session."""
    import glob

    snapshot = _load_plan_snapshot()

    for plan_dir in PLAN_DIRS:
        if not os.path.isdir(plan_dir):
            continue
        for plan_file in glob.glob(os.path.join(plan_dir, "*.md")):
            plan_name = os.path.basename(plan_file)

            if not _is_session_relevant(plan_name, plan_file, snapshot):
                continue

            try:
                with open(plan_file) as f:
                    lines = f.readlines()
            except OSError:
                continue
            pending = [ln.strip() for ln in lines if ln.strip().startswith("- [ ]")]
            if pending:
                return (plan_name, pending)
    return None


def _check_review_gate() -> str | None:
    """Check if session had significant edits without review.

    Reads edit-counter.json (managed by suggest-compact.js).
    Returns a reminder message if edits exceed threshold, else None.
    This is advisory only — does not block stop.
    """
    try:
        with open(EDIT_COUNTER_FILE) as f:
            counter = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    edit_count = counter.get("count", 0)
    if edit_count < REVIEW_EDIT_THRESHOLD:
        return None

    return (
        f"[Review Gate] このセッションで {edit_count} 回の編集がありました。"
        "`/review` でコードレビューを実行することを推奨します。"
    )


# Test file naming conventions per language
_TEST_FILE_MAPPINGS = {
    ".ts": [".test.ts", ".spec.ts"],
    ".tsx": [".test.tsx", ".spec.tsx"],
    ".js": [".test.js", ".spec.js"],
    ".jsx": [".test.jsx", ".spec.jsx"],
    ".go": ["_test.go"],
    ".py": ["test_{name}.py", "{name}_test.py"],
    ".rs": [],  # Rust uses inline #[cfg(test)]
}


def _try_selective_tests() -> tuple[bool, str, str] | None:
    """Try running only tests related to changed files (fast feedback).

    Returns (success, output, cmd) or None if selective tests aren't available.
    """
    try:
        # Import test_selector from sibling lib/ directory
        lib_dir = os.path.join(os.path.dirname(__file__), "..", "lib")
        if lib_dir not in sys.path:
            sys.path.insert(0, lib_dir)
        from test_selector import select_tests

        selective_cmd, _full_cmd = select_tests(project_root=os.getcwd())
        if selective_cmd is None:
            return None

        print(
            f"[Completion Gate] 選択的テスト実行: {selective_cmd}",
            file=sys.stderr,
        )
        success, output = _run_tests(selective_cmd)
        return (success, output, selective_cmd)
    except ImportError:
        print("[Completion Gate] test_selector not available", file=sys.stderr)
        return None
    except Exception as exc:
        print(f"[Completion Gate] selective test error: {exc}", file=sys.stderr)
        return None


def _generate_handback_report() -> str:
    """Generate a structured handback report for graduated completion.

    Collects: completed tasks, failed tests, and recommended actions.
    """
    parts = [
        "[Graduated Completion] ハンドバックレポート",
        "",
        "## Status: Partial",
        "",
    ]

    # Collect recent test failure info
    test_cmd = _detect_test_command()
    if test_cmd:
        success, output = _run_tests(test_cmd)
        if not success:
            parts.extend(
                [
                    "### 失敗テスト",
                    f"コマンド: `{test_cmd}`",
                    "```",
                    output,
                    "```",
                    "",
                ]
            )
        else:
            parts.extend(["### テスト: 全通過", ""])

    # Collect changed files as "completed work"
    try:
        result = subprocess.run(
            ["git", "diff", "--stat", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.getcwd(),
        )
        if result.returncode == 0 and result.stdout.strip():
            parts.extend(
                [
                    "### 変更済みファイル",
                    "```",
                    result.stdout.strip(),
                    "```",
                    "",
                ]
            )
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"[Completion Gate] git diff failed: {exc}", file=sys.stderr)

    parts.extend(
        [
            "### 推奨アクション",
            "1. 失敗テストを確認し、手動で修正を検討してください",
            "2. 変更済みコードは commit 済みです（作業喪失防止）",
            "3. PR を作成する場合は `[WIP]` を title に付加してください",
        ]
    )

    return "\n".join(parts)


def _check_test_coverage_for_changes() -> str | None:
    """Check if changed source files have corresponding test files (advisory)."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.getcwd(),
        )
        if result.returncode != 0:
            return None
        changed = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except Exception:
        return None

    if not changed:
        return None

    uncovered: list[str] = []
    cwd = os.getcwd()

    for filepath in changed:
        base, ext = os.path.splitext(filepath)
        name = os.path.basename(base)

        # Skip test files, configs, docs themselves
        if any(
            filepath.endswith(s)
            for s in (
                "_test.go",
                ".test.ts",
                ".test.tsx",
                ".test.js",
                ".test.jsx",
                ".spec.ts",
                ".spec.tsx",
                ".spec.js",
                ".spec.jsx",
            )
        ) or name.startswith("test_"):
            continue
        if ext in (".md", ".json", ".yaml", ".yml", ".toml", ".lock", ".css", ".html"):
            continue

        suffixes = _TEST_FILE_MAPPINGS.get(ext)
        if suffixes is None:
            continue

        # Check if any test file exists
        has_test = False
        dirpath = os.path.dirname(filepath)

        for suffix in suffixes:
            if "{name}" in suffix:
                test_name = suffix.replace("{name}", name)
            else:
                test_name = name + suffix

            # Check same directory
            if os.path.exists(os.path.join(cwd, dirpath, test_name)):
                has_test = True
                break

            # Check __tests__ subdirectory
            tests_dir = os.path.join(cwd, dirpath, "__tests__")
            if os.path.exists(os.path.join(tests_dir, test_name)):
                has_test = True
                break

        if not has_test:
            uncovered.append(filepath)

    if not uncovered:
        return None

    files_str = ", ".join(f"`{f}`" for f in uncovered[:5])
    extra = f" 他{len(uncovered) - 5}件" if len(uncovered) > 5 else ""
    return (
        f"[Test Coverage] テストファイルが見つからない変更: {files_str}{extra}。"
        "対応するテストの追加を検討してください。"
    )


def main() -> None:
    retries = _get_retry_count()

    # Safety valve: if we've hit max retries, allow stop (or handback)
    if retries >= MAX_RETRIES:
        _reset_retries()
        if COMPLETION_MODE == "graduated":
            report = _generate_handback_report()
            print(
                "[Completion Gate] リトライ上限到達 — graduated mode: "
                "ハンドバックレポートを生成します。",
                file=sys.stderr,
            )
            json.dump({"systemMessage": report}, sys.stdout)
        else:
            print(
                "[Completion Gate] リトライ上限"
                f"({MAX_RETRIES}回)に到達。停止を許可します。",
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
                "タスクを続行してください。完了不要なら、"
                "プランを completed/ に移動してから停止してください。",
            ]
        )

        _set_retry_count(retries + 1)
        json.dump(
            {"decision": "block", "reason": "\n".join(ctx_parts)},
            sys.stdout,
        )
        return

    # --- Test gate ---
    test_cmd = _detect_test_command()
    if not test_cmd:
        _reset_retries()
        # Advisory: suggest review if many edits (no tests to run)
        review_msg = _check_review_gate()
        if review_msg:
            json.dump({"systemMessage": review_msg}, sys.stdout)
        return

    # Step 1: Try selective tests first (fast feedback)
    selective = _try_selective_tests()
    if selective is not None:
        sel_success, sel_output, sel_cmd = selective
        if not sel_success:
            # Selective tests failed — skip full suite, report immediately
            _set_retry_count(retries + 1)
            remaining = MAX_RETRIES - retries - 1
            ctx_lines = [
                f"[Completion Gate] 関連テストが失敗: `{sel_cmd}`",
                f"リトライ残り: {remaining}回",
                "",
                "```",
                sel_output,
                "```",
                "",
                "FIX: 関連テストを通過させてから完了してください。",
            ]
            json.dump(
                {"decision": "block", "reason": "\n".join(ctx_lines)},
                sys.stdout,
            )
            return
        print(
            f"[Completion Gate] 関連テスト通過 ({sel_cmd})",
            file=sys.stderr,
        )

    # Step 2: Run full test suite
    success, output = _run_tests(test_cmd)

    if success:
        _reset_retries()
        print(f"[Completion Gate] テスト通過 ({test_cmd})", file=sys.stderr)
        # Advisory messages (non-blocking)
        advisories: list[str] = []
        review_msg = _check_review_gate()
        if review_msg:
            advisories.append(review_msg)
        coverage_msg = _check_test_coverage_for_changes()
        if coverage_msg:
            advisories.append(coverage_msg)
        if advisories:
            json.dump({"systemMessage": "\n".join(advisories)}, sys.stdout)
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
        {"decision": "block", "reason": "\n".join(ctx_lines)},
        sys.stdout,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[completion-gate] error: {e}", file=sys.stderr)
