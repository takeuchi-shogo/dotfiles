#!/usr/bin/env python3
"""File-pattern-based agent suggestion — proactive routing on Edit/Write.

Triggered by: hooks.PreToolUse (Edit|Write)
Input: JSON with tool_input on stdin (contains file_path)
Output: JSON with additionalContext suggestion on stdout

Based on "Codified Context" paper (Vasilopoulos, 2026):
"Trigger tables that route tasks to the appropriate specialist agent
based on observable signals — primarily which files are being modified."

This is advisory only — suggests agents, never blocks edits.
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import output_context  # noqa: E402

# File pattern → agent suggestion mapping
# (regex_pattern, agent_name, description)
FILE_AGENT_ROUTES: list[tuple[str, str, str]] = [
    (r"\.(tsx|jsx)$", "frontend-developer", "React コンポーネント"),
    (r"\.(css|scss|less)$", "frontend-developer", "スタイルシート"),
    (r"\.go$", "golang-pro", "Go コード"),
    (r"go\.(mod|sum)$", "golang-pro", "Go 依存関係"),
    (r"\.rs$", "backend-architect", "Rust コード"),
    (r"\.ts$", "typescript-pro", "TypeScript コード"),
    (r"\.config/claude/agents/", "document-factory", "エージェント定義"),
    (r"\.config/claude/scripts/", "build-fixer", "Hook スクリプト"),
    (r"\.config/claude/references/", "doc-gardener", "リファレンス"),
    (r"\.proto$", "backend-architect", "Protocol Buffers"),
    (r"(test_|_test\.|\.test\.|\.spec\.)", "test-engineer", "テストファイル"),
]

_COOLDOWN_FILE = "/tmp/claude-file-pattern-router-last.json"
_COOLDOWN_SECONDS = 120


def _load_project_overrides() -> list[tuple[str, str, str]]:
    """Load project-specific file-pattern routes if available."""
    override_path = Path.cwd() / ".claude" / "file-pattern-routes.json"
    if not override_path.exists():
        return []
    try:
        with open(override_path) as f:
            data = json.load(f)
        return [(r["pattern"], r["agent"], r.get("description", "")) for r in data]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        sys.stderr.write(f"[file-pattern-router] override parse error: {exc}\n")
        return []


def _check_cooldown(agent: str) -> bool:
    """Return True if suggestion should be suppressed (cooldown active)."""
    try:
        with open(_COOLDOWN_FILE) as f:
            last = json.load(f)
        if last.get("agent") == agent:
            elapsed = time.time() - last.get("time", 0)
            if elapsed < _COOLDOWN_SECONDS:
                return True
    except FileNotFoundError:
        # First run — no cooldown file yet, expected
        return False
    except (json.JSONDecodeError, OSError) as exc:
        sys.stderr.write(f"[file-pattern-router] cooldown read error: {exc}\n")
    return False


def _set_cooldown(agent: str) -> None:
    """Record the last suggestion for cooldown tracking."""
    try:
        with open(_COOLDOWN_FILE, "w") as f:
            json.dump({"agent": agent, "time": time.time()}, f)
    except OSError as exc:
        sys.stderr.write(f"[file-pattern-router] cooldown write error: {exc}\n")


def main() -> None:
    raw = sys.stdin.read()
    if not raw.strip():
        return

    data = json.loads(raw)
    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")

    if not file_path:
        return

    file_path_str = str(file_path)
    routes = _load_project_overrides() + FILE_AGENT_ROUTES

    for pattern, agent, description in routes:
        if re.search(pattern, file_path_str):
            if _check_cooldown(agent):
                return

            _set_cooldown(agent)
            filename = Path(file_path_str).name
            output_context(
                "PreToolUse",
                (
                    f"[File-Pattern Router] {description} ({filename}) の編集を検出。"
                    f"専門エージェント `{agent}` の使用を検討してください。"
                ),
            )
            return


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write(f"[file-pattern-router] unexpected error: {exc}\n")
