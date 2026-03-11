#!/usr/bin/env python3
"""Protect linter/formatter config files from agent modification.

Prevents the anti-pattern where agents bypass lint violations by modifying
linter config instead of fixing code.
Ref: Harness Engineering Best Practices 2026 — "Config Protection"

Triggered by: hooks.PreToolUse (Edit|Write)
Input: JSON with tool_name, tool_input on stdin
Block: exit 2 + reason on stderr
Allow: exit 0
"""
from __future__ import annotations

import json
import os
import sys

# Pure linter/formatter config files — always block
BLOCKED_FILES = {
    ".eslintrc",
    ".eslintrc.js",
    ".eslintrc.cjs",
    ".eslintrc.json",
    ".eslintrc.yml",
    "eslint.config.js",
    "eslint.config.mjs",
    "eslint.config.ts",
    "biome.json",
    "biome.jsonc",
    ".prettierrc",
    ".prettierrc.js",
    ".prettierrc.cjs",
    ".prettierrc.json",
    ".prettierrc.yml",
    "prettier.config.js",
    "prettier.config.mjs",
    ".oxlintrc.json",
    ".swiftlint.yml",
    ".golangci.yml",
    ".golangci.yaml",
    ".markdownlint.json",
    ".markdownlint.yaml",
    ".stylelintrc",
    ".stylelintrc.json",
}

# Mixed-use files — block only if editing linter-related sections
MIXED_FILE_PATTERNS = {
    "pyproject.toml": ["[tool.ruff", "[tool.black", "[tool.isort", "[tool.pylint", "[tool.mypy"],
    "Cargo.toml": ["[lints", "[lints.clippy", "[lints.rust"],
    "tsconfig.json": [],  # allow — tsconfig is mostly project config
}


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")

    if not file_path:
        return

    basename = os.path.basename(file_path)

    # Check pure linter configs
    if basename in BLOCKED_FILES:
        print(
            f"BLOCKED: `{basename}` はリンター/フォーマッター設定ファイルです。\n"
            "コードを修正してください。リンター設定を変更してはいけません。\n"
            "WHY: エージェントが lint 違反をコード修正ではなく設定変更で回避するのを防止するため。",
            file=sys.stderr,
        )
        sys.exit(2)

    # Check mixed-use files — block if editing linter sections
    for filename, patterns in MIXED_FILE_PATTERNS.items():
        if basename == filename and patterns:
            # Check if the edit touches linter-related content
            new_string = tool_input.get("new_string", "") or tool_input.get("content", "")
            old_string = tool_input.get("old_string", "")
            edit_content = f"{old_string}\n{new_string}"

            for pattern in patterns:
                if pattern in edit_content:
                    print(
                        f"BLOCKED: `{basename}` のリンター設定セクション ({pattern}) を変更しようとしています。\n"
                        "コードを修正してください。リンター設定を変更してはいけません。",
                        file=sys.stderr,
                    )
                    sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        # Non-blocking — don't fail the tool use on unexpected errors
        print(f"[protect-linter-config] error: {e}", file=sys.stderr)
