#!/usr/bin/env python3
"""Tool Scope Enforcer — warn when tools exceed skill/blueprint scope.

Checks if the current tool is within the allowed set for the active
skill or blueprint context. Advisory only (exit 0) in interactive mode.

Stripe Minions pattern: each task type gets only the tools it needs.

Triggered by: PreToolUse (all tools)
Output: stderr warning if tool is out of scope
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import load_hook_input, run_hook

# Default allowed tools (superset — used when no scope is defined)
DEFAULT_TOOLS = frozenset(
    {
        "Read",
        "Write",
        "Edit",
        "Bash",
        "Glob",
        "Grep",
        "Agent",
        "WebFetch",
        "WebSearch",
    }
)

# Cooldown to avoid spam (seconds per tool warning)
_COOLDOWN_SEC = 300
_COOLDOWN_DIR = os.path.join(
    os.environ.get("TMPDIR", "/tmp"),
    "claude-tool-scope",
)


def _recently_warned(tool_name: str) -> bool:
    """Check if we warned about this tool recently."""
    os.makedirs(_COOLDOWN_DIR, exist_ok=True)
    marker = os.path.join(_COOLDOWN_DIR, f"{tool_name}.warned")
    try:
        if os.path.exists(marker):
            age = time.time() - os.path.getmtime(marker)
            if age < _COOLDOWN_SEC:
                return True
        Path(marker).touch()
    except OSError as e:
        print(f"[tool-scope-enforcer] cooldown check warning: {e}", file=sys.stderr)
    return False


def _load_skill_scope() -> frozenset[str] | None:
    """Try to detect the active skill's allowed-tools from environment."""
    # Claude Code sets CLAUDE_SKILL when a skill is active
    skill_name = os.environ.get("CLAUDE_SKILL", "")
    if not skill_name:
        return None

    # Search for the skill's SKILL.md
    skills_dir = Path(__file__).resolve().parent.parent.parent / "skills"
    skill_file = skills_dir / skill_name / "SKILL.md"
    if not skill_file.exists():
        return None

    try:
        content = skill_file.read_text()
        for line in content.split("\n"):
            if line.startswith("allowed-tools:"):
                tools_str = line.split(":", 1)[1].strip()
                return frozenset(t.strip() for t in tools_str.split(","))
    except OSError as e:
        print(f"[tool-scope-enforcer] skill read error: {e}", file=sys.stderr)
    return None


def _enforce(data: dict) -> None:
    tool_name = data.get("tool_name", "")

    # Skip internal/system tools
    if tool_name in ("", "TodoWrite", "TodoRead"):
        return

    # Normalize MCP tool names: mcp__server__tool -> mcp
    base_tool = tool_name.split("__")[0] if "__" in tool_name else tool_name

    scope = _load_skill_scope()
    if scope is None:
        # No skill context — no enforcement
        return

    # Check if tool is in scope
    if tool_name in scope or base_tool in scope:
        return

    # MCP tools: check if "mcp" is in scope (wildcard)
    if tool_name.startswith("mcp__") and "mcp" in scope:
        return

    # Out of scope — warn (don't block)
    if not _recently_warned(tool_name):
        skill = os.environ.get("CLAUDE_SKILL", "")
        msg = f"[Tool Scope] `{tool_name}` はスキル '{skill}' の allowed-tools 外です"
        print(msg, file=sys.stderr)


def main() -> None:
    data = load_hook_input()
    if not data:
        return
    _enforce(data)


if __name__ == "__main__":
    run_hook("tool-scope-enforcer", main, fail_closed=False)
