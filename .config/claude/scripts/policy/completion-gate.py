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
import time

MAX_RETRIES = 2

# Graduated completion mode (Stripe Minions pattern)
# "strict" = default, block on test failure
# "graduated" = allow partial completion with handback report
COMPLETION_MODE = os.environ.get("COMPLETION_MODE", "strict")
COUNTER_DIR = os.path.join(tempfile.gettempdir(), "claude-completion-gate")
COUNTER_FILE = os.path.join(COUNTER_DIR, "retries")

# Ralph Loop — active plan detection
# Ref: "Long-Running Claude" — Ralph Loop with success criteria + max iterations
PLAN_DIRS = [
    os.path.join(os.getcwd(), "docs", "plans", "active"),
    os.path.join(os.getcwd(), "tmp", "plans"),
]

# Ralph Loop — success criteria support
# Set COMPLETION_PROMISE to a string the agent must output to signal true completion
COMPLETION_PROMISE = os.environ.get("COMPLETION_PROMISE", "")
# Max iterations before Ralph Loop allows stop (prevents infinite loops)
MAX_RALPH_ITERATIONS = int(os.environ.get("MAX_RALPH_ITERATIONS", "10"))

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
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(
                f"[completion-gate] package.json parse failed: {exc}",
                file=sys.stderr,
            )

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
    except Exception as exc:
        # If we can't run tests, don't block
        print(
            f"[completion-gate] test run failed: {exc}",
            file=sys.stderr,
        )
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


def _has_active_status(lines: list[str]) -> bool:
    """Check if plan has 'status: active' in frontmatter — skip these plans."""
    in_frontmatter = False
    for line in lines:
        stripped = line.strip()
        if stripped == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break  # end of frontmatter
        if in_frontmatter and stripped.startswith("status:"):
            value = stripped.split(":", 1)[1].strip().lower()
            return value == "active"
    return False


def _extract_success_criteria(lines: list[str]) -> str | None:
    """Extract success_criteria from plan frontmatter."""
    in_frontmatter = False
    for line in lines:
        stripped = line.strip()
        if stripped == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter and stripped.startswith("success_criteria:"):
            return stripped.split(":", 1)[1].strip()
    return None


def _find_incomplete_plan() -> tuple[str, list[str], str | None] | None:
    """Find active plan with unchecked items that is relevant to the current session.

    Returns (plan_name, pending_items, success_criteria) or None.
    """
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

            # status: active means another session owns this plan — skip
            if _has_active_status(lines):
                continue

            pending = [ln.strip() for ln in lines if ln.strip().startswith("- [ ]")]
            if pending:
                criteria = _extract_success_criteria(lines)
                return (plan_name, pending, criteria)
    return None


def _check_layer0_verification() -> str | None:
    """Layer 0: Check if tests exist but were never run in this session (advisory).

    Trust Verification Policy: テスト結果 > レビュー合意 > 自己評価。
    テストファイルが存在するのにテストが実行されていない場合に警告。
    Ref: references/trust-verification-policy.md
    """
    test_cmd = _detect_test_command()
    if not test_cmd:
        return None  # no tests to run

    # Check session state for test execution history
    _home = os.environ.get("HOME") or os.path.expanduser("~")
    state_dir = os.environ.get(
        "CLAUDE_SESSION_STATE_DIR",
        os.path.join(_home, ".claude", "session-state"),
    )
    test_history = os.path.join(state_dir, "test-execution.json")
    try:
        with open(test_history) as f:
            history = json.load(f)
        if history.get("last_run_epoch", 0) > 0:
            return None  # tests were run
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"[Layer 0] test history not found: {exc}", file=sys.stderr)

    return (
        "[Layer 0 — Trust Verification] テストコマンドが検出されましたが、"
        "このセッションでテストが実行された記録がありません。"
        f"コマンド: `{test_cmd}` を実行してから完了してください。"
        "テスト結果は LLM の判断より常に優先されます。"
    )


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
                    "### 未コミットの変更ファイル",
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
            "2. working tree に未コミットの変更が残っています。"
            "必要に応じて commit してください",
            "3. PR を作成する場合は `[WIP]` を title に付加してください",
        ]
    )

    return "\n".join(parts)


def _check_test_coverage_for_changes() -> str | None:
    """Check if changed source files have corresponding test files (advisory)."""
    try:
        result = subprocess.run(
            ["git", "--no-optional-locks", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.getcwd(),
        )
        if result.returncode != 0:
            return None
        changed = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(
            f"[completion-gate] test coverage check git diff failed: {exc}",
            file=sys.stderr,
        )
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


# --- Comprehension Check: Design Rationale for M/L changes ---
# Ref: Addy Osmani "Comprehension Debt" + comprehension-debt-policy.md
_CHANGE_SIZE_M = 30  # lines changed threshold for M-size
_RATIONALE_KEYWORDS = {
    "what": ["解決", "目的", "what", "solve", "address", "purpose"],
    "why": [
        "なぜ",
        "アプローチ",
        "選んだ",
        "理由",
        "why",
        "approach",
        "chose",
        "because",
        "代替",
    ],
    "risk": ["リスク", "壊れ", "影響", "risk", "break", "impact", "mitigation"],
}


def _estimate_change_size() -> int:
    """Estimate lines changed from git diff --stat."""
    try:
        result = subprocess.run(
            ["git", "diff", "--stat", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.getcwd(),
        )
        if result.returncode != 0 or not result.stdout.strip():
            return 0
        # Last line: " N files changed, X insertions(+), Y deletions(-)"
        import re

        m = re.search(r"(\d+) insertion", result.stdout)
        ins = int(m.group(1)) if m else 0
        m = re.search(r"(\d+) deletion", result.stdout)
        dels = int(m.group(1)) if m else 0
        return ins + dels
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"[Comprehension Check] git diff error: {exc}", file=sys.stderr)
        return 0


def _find_rationale_text() -> str:
    """Collect text from active plan and recent commit message."""
    parts: list[str] = []
    # Check active plans
    import glob as _glob

    for plan_dir in PLAN_DIRS:
        if not os.path.isdir(plan_dir):
            continue
        for plan_file in _glob.glob(os.path.join(plan_dir, "*.md")):
            try:
                with open(plan_file) as f:
                    parts.append(f.read()[:2000])
            except OSError as exc:
                print(f"[Comprehension Check] plan read error: {exc}", file=sys.stderr)
    # Check latest commit message
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=os.getcwd(),
        )
        if result.returncode == 0:
            parts.append(result.stdout)
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"[Comprehension Check] git log error: {exc}", file=sys.stderr)
    return "\n".join(parts).lower()


def _check_design_rationale() -> str | None:
    """Check if M/L changes have Design Rationale (What/Why/Risk).

    Advisory only — returns a message if rationale is missing, else None.
    """
    change_size = _estimate_change_size()
    if change_size < _CHANGE_SIZE_M:
        return None  # S-size: exempt

    text = _find_rationale_text()
    if not text:
        return (
            f"[Comprehension Check] {change_size}行の変更がありますが、"
            "Design Rationale（What/Why/Risk）が Plan にもコミットにも見つかりません。"
            "理解負債を防ぐため、変更意図を記録してください。"
        )

    missing: list[str] = []
    for dimension, keywords in _RATIONALE_KEYWORDS.items():
        if not any(kw in text for kw in keywords):
            missing.append(dimension)

    if not missing:
        return None

    labels = {
        "what": "What(何を解決)",
        "why": "Why(なぜこのアプローチ)",
        "risk": "Risk(何が壊れうるか)",
    }
    missing_str = ", ".join(labels[d] for d in missing)
    return (
        f"[Comprehension Check] {change_size}行の変更で "
        f"Design Rationale の {missing_str} が不十分です。"
        "Plan またはコミットメッセージに記録を推奨します。"
    )


def _check_progress_log() -> str | None:
    """Check if progress.log was updated during this session.

    Advisory only — returns a message if stale, else None.
    """
    cwd = os.getcwd()
    progress_log = os.path.join(cwd, "progress.log")
    feature_list = os.path.join(cwd, "feature_list.json")

    # Only check if feature_list.json or progress.log exists
    if not os.path.exists(feature_list) and not os.path.exists(progress_log):
        return None

    if not os.path.exists(progress_log):
        return (
            "[Progress Log] feature_list.json が存在しますが "
            "progress.log がありません。"
            "/checkpoint で進捗を記録してください。"
        )

    # Check if progress.log was updated in the last hour
    try:
        mtime = os.path.getmtime(progress_log)
        age_hours = (time.time() - mtime) / 3600
        if age_hours > 1:
            return (
                "[Progress Log] progress.log が "
                f"{age_hours:.1f}時間前から更新されていません。"
                "/checkpoint で進捗を記録してください。"
            )
    except OSError as exc:
        print(
            f"[Completion Gate] progress.log stat error: {exc}",
            file=sys.stderr,
        )

    return None


def _check_session_focus() -> str | None:
    """Warn if multiple features were completed in one session.

    Compares current feature_list.json passes state against
    the session-start snapshot saved by session-load.js.
    Advisory only.
    """
    cwd = os.getcwd()
    feature_path = os.path.join(cwd, "feature_list.json")
    if not os.path.exists(feature_path):
        return None

    snapshot_path = os.path.join(
        os.environ.get(
            "CLAUDE_SESSION_STATE_DIR",
            os.path.join(
                os.environ.get("HOME", ""),
                ".claude",
                "session-state",
            ),
        ),
        "feature-passes-snapshot.json",
    )

    try:
        with open(snapshot_path) as f:
            snapshot = json.load(f)
        with open(feature_path) as f:
            current = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    old_passes = snapshot.get("passes", {})
    newly_passed = []
    for feat in current.get("features", []):
        fid = feat.get("id", "")
        if feat.get("passes") and not old_passes.get(fid, False):
            newly_passed.append(fid)

    if len(newly_passed) >= 2:
        ids = ", ".join(newly_passed)
        return (
            f"[Session Focus] このセッションで {len(newly_passed)} "
            f"機能が完了しました ({ids})。"
            "1セッション1機能を推奨します。"
        )

    return None


_FRONTEND_EXTENSIONS = {".tsx", ".jsx", ".vue", ".svelte", ".css", ".scss", ".less"}

# UI verification marker — set by webapp-testing / Playwright hooks
_UI_VERIFIED_MARKER = os.path.join(
    os.environ.get(
        "CLAUDE_SESSION_STATE_DIR",
        os.path.join(os.environ.get("HOME", ""), ".claude", "session-state"),
    ),
    "ui-verified.marker",
)


def _check_ui_verification() -> str | None:
    """Check if frontend changes were verified via browser (advisory).

    Detects frontend file changes and checks if agent-browser or Playwright
    was used during the session. If not, suggests UI self-verification.
    Ref: Neil Kakkar — "a change isn't done until the agent has verified the UI"
    """
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
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(
            f"[completion-gate] UI verification git diff failed: {exc}",
            file=sys.stderr,
        )
        return None

    if not changed:
        return None

    frontend_changes = [
        f for f in changed if os.path.splitext(f)[1] in _FRONTEND_EXTENSIONS
    ]

    if not frontend_changes:
        return None

    # Check if UI was verified this session
    if os.path.exists(_UI_VERIFIED_MARKER):
        return None

    files_str = ", ".join(f"`{f}`" for f in frontend_changes[:3])
    extra = f" 他{len(frontend_changes) - 3}件" if len(frontend_changes) > 3 else ""
    return (
        f"[UI Verification] フロントエンド変更を検出: {files_str}{extra}。"
        "`/webapp-testing` または Playwright MCP でUI検証を推奨します。"
    )


def _check_knowledge_extraction() -> str | None:
    """Suggest /analyze-tacit-knowledge when session had significant activity.

    Inspired by 724-office compress_async pattern: auto-trigger knowledge
    extraction when session crosses activity threshold.
    Advisory only — does not block stop.
    """
    try:
        with open(EDIT_COUNTER_FILE) as f:
            counter = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    edit_count = counter.get("count", 0)
    if edit_count < 15:
        return None

    # Check if analyze-tacit-knowledge was already run this session
    marker = os.path.join(
        os.path.dirname(EDIT_COUNTER_FILE),
        "tacit-knowledge-ran.marker",
    )
    if os.path.exists(marker):
        return None

    return (
        f"[Knowledge Capture] このセッションで {edit_count} 回の編集がありました。"
        "`/analyze-tacit-knowledge` でセッションの知見を抽出することを推奨します。"
    )


def _check_clean_state() -> str | None:
    """Check if workspace is in a clean state (advisory).

    Warns about uncommitted changes at session end.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.getcwd(),
        )
        if result.returncode != 0:
            return None
        dirty = [ln for ln in result.stdout.strip().splitlines() if ln.strip()]
        if not dirty:
            return None

        count = len(dirty)
        return (
            f"[Clean State] {count} 件の未コミット変更があります。"
            "セッション終了前にコミットを推奨します。"
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(
            f"[Completion Gate] git status error: {exc}",
            file=sys.stderr,
        )
        return None


def main() -> None:
    if os.environ.get("CLAUDE_SKIP_TEST_GATE") == "1":
        return

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
        plan_name, pending, success_criteria = incomplete

        # Ralph Loop iteration limit — prevent infinite loops
        ralph_iteration = retries + 1
        if ralph_iteration > MAX_RALPH_ITERATIONS:
            _reset_retries()
            json.dump(
                {
                    "decision": "allow",
                    "reason": (
                        f"[Ralph Loop] max iterations "
                        f"({MAX_RALPH_ITERATIONS}) 到達。停止を許可。"
                    ),
                },
                sys.stdout,
            )
            return

        shown = pending[:5]
        remaining_count = len(pending) - len(shown)

        ctx_parts = [
            f"[Ralph Loop] アクティブプラン '{plan_name}' に未完了ステップがあります "
            f"(iteration {ralph_iteration}/{MAX_RALPH_ITERATIONS}):",
            "",
        ]
        # Show success criteria if defined in plan frontmatter or env
        effective_criteria = success_criteria or COMPLETION_PROMISE
        if effective_criteria:
            ctx_parts.append(f"  成功基準: {effective_criteria}")
            ctx_parts.append("")
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
        advisories_notests: list[str] = []
        layer0_msg = _check_layer0_verification()
        if layer0_msg:
            advisories_notests.append(layer0_msg)
        review_msg = _check_review_gate()
        if review_msg:
            advisories_notests.append(review_msg)
        rationale_msg = _check_design_rationale()
        if rationale_msg:
            advisories_notests.append(rationale_msg)
        progress_msg = _check_progress_log()
        if progress_msg:
            advisories_notests.append(progress_msg)
        clean_msg = _check_clean_state()
        if clean_msg:
            advisories_notests.append(clean_msg)
        focus_msg = _check_session_focus()
        if focus_msg:
            advisories_notests.append(focus_msg)
        knowledge_msg = _check_knowledge_extraction()
        if knowledge_msg:
            advisories_notests.append(knowledge_msg)
        ui_msg = _check_ui_verification()
        if ui_msg:
            advisories_notests.append(ui_msg)
        if advisories_notests:
            json.dump({"systemMessage": "\n".join(advisories_notests)}, sys.stdout)
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
        # Layer 0 チェックはスキップ — このブランチは直前にテスト実行・成功済み
        review_msg = _check_review_gate()
        if review_msg:
            advisories.append(review_msg)
        coverage_msg = _check_test_coverage_for_changes()
        if coverage_msg:
            advisories.append(coverage_msg)
        rationale_msg = _check_design_rationale()
        if rationale_msg:
            advisories.append(rationale_msg)
        progress_msg = _check_progress_log()
        if progress_msg:
            advisories.append(progress_msg)
        clean_msg = _check_clean_state()
        if clean_msg:
            advisories.append(clean_msg)
        focus_msg = _check_session_focus()
        if focus_msg:
            advisories.append(focus_msg)
        knowledge_msg = _check_knowledge_extraction()
        if knowledge_msg:
            advisories.append(knowledge_msg)
        ui_msg = _check_ui_verification()
        if ui_msg:
            advisories.append(ui_msg)
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
