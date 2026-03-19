#!/usr/bin/env python3
"""File proliferation guard — warns when too many new files are created in a session.

Triggered by: hooks.PostToolUse (Write)
Input: JSON with tool_name, tool_input on stdin
Output: JSON with additionalContext warning on stdout

Inspired by "Don't trust your agents" (0xSero & SarahXC, 2026):
"LLMs love creating new code, rebuilding instead of improving what already
exists. Left unbounded they will make the directory unmanageable very quickly."
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import (
    check_tool,
    get_emitter,
    load_hook_input,
    output_context,
    output_passthrough,
    run_hook,
)

emit = get_emitter()

# --- Constants ---
WARN_THRESHOLD = 10
STATE_FILE = "file-creation-tracker.json"
# Directories where new file creation is expected
ALLOW_PATTERNS = {
    "node_modules/",
    ".git/",
    "dist/",
    "build/",
    "__pycache__/",
    "tmp/",
}


def _state_path() -> Path:
    from storage import get_data_dir

    return get_data_dir() / STATE_FILE


def _load_state() -> dict:
    path = _state_path()
    if not path.exists():
        return {"created_files": [], "warned": False}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"created_files": [], "warned": False}


def _save_state(state: dict) -> None:
    path = _state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")


def _is_allowed_path(file_path: str) -> bool:
    return any(pattern in file_path for pattern in ALLOW_PATTERNS)


def _is_new_file(file_path: str) -> bool:
    return not Path(file_path).exists()


def main() -> None:
    data = load_hook_input()
    if not data:
        return
    if not check_tool(data, "Write"):
        output_passthrough(data)
        return

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path or _is_allowed_path(file_path):
        output_passthrough(data)
        return

    # Check if this is creating a new file (not overwriting existing)
    if not _is_new_file(file_path):
        output_passthrough(data)
        return

    state = _load_state()
    created = state.get("created_files", [])

    # Track the new file
    if file_path not in created:
        created.append(file_path)
        state["created_files"] = created

    count = len(created)

    if count >= WARN_THRESHOLD and not state.get("warned"):
        state["warned"] = True
        _save_state(state)

        recent = created[-5:]
        recent_list = "\n".join(f"  - {f}" for f in recent)

        warning = (
            f"[File Proliferation Guard] 警告: "
            f"このセッションで {count} 個の新規ファイルが作成されました "
            f"(閾値: {WARN_THRESHOLD})。\n"
            f"直近の作成ファイル:\n{recent_list}\n"
            f"エージェントは新規ファイル作成を好みますが、既存ファイルの修正を優先してください。\n"
            f"本当に新規ファイルが必要か確認してください。"
        )

        emit(
            "pattern",
            {
                "type": "file_proliferation",
                "file_count": count,
                "recent_files": recent,
                "message": warning,
            },
        )
        output_context("PostToolUse", warning)
        return

    _save_state(state)
    output_passthrough(data)


if __name__ == "__main__":
    run_hook("file-proliferation-guard", main, fail_closed=False)
