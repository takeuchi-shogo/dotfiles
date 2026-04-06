#!/usr/bin/env python3
"""Advise red-teaming or preflight based on change surface.

PostToolUse hook for Edit|Write. Detects high-risk change patterns
and suggests appropriate agents (edge-case-hunter, silent-failure-hunter,
migration-guard, security-reviewer).

References:
  - references/change-surface-preflight.md
  - references/high-risk-change-patterns.md

Design: advisory only, never blocks. Cooldown per change surface
category to avoid repeated suggestions in the same session.
"""

import json
import os
import re
from dataclasses import dataclass

SEEN_FILE = "/tmp/claude-change-surface-seen.json"


@dataclass
class SurfacePattern:
    category: str
    risk: str  # critical, high, medium
    patterns: list[str]
    advice: str


SURFACES: list[SurfacePattern] = [
    # Critical
    SurfacePattern(
        category="auth",
        risk="critical",
        patterns=[r"auth[/.]", r"middleware/.*auth", r"jwt", r"rbac", r"permission"],
        advice="edge-case-hunter + security-reviewer (認可バイパスリスク)",
    ),
    SurfacePattern(
        category="db_migration",
        risk="critical",
        patterns=[r"migration[/.]", r"migrate", r"\.sql$", r"schema"],
        advice="migration-guard (データ損失・後方互換性リスク)",
    ),
    SurfacePattern(
        category="harness",
        risk="critical",
        patterns=[
            r"scripts/policy/",
            r"scripts/runtime/",
            r"settings\.json",
            r"CLAUDE\.md",
        ],
        advice="harness contract 準拠確認 (docs/agent-harness-contract.md)",
    ),
    SurfacePattern(
        category="crypto",
        risk="critical",
        patterns=[r"crypto", r"sign[^a]", r"hash", r"encrypt", r"decrypt"],
        advice="security-reviewer (暗号処理の脆弱性リスク)",
    ),
    # High
    SurfacePattern(
        category="external_api",
        risk="high",
        patterns=[r"_client\.", r"api/external", r"integration/", r"http_client"],
        advice="edge-case-hunter (タイムアウト・リトライ・エラーハンドリング)",
    ),
    SurfacePattern(
        category="concurrency",
        risk="high",
        patterns=[r"worker", r"goroutine", r"channel", r"mutex", r"sync[./]"],
        advice="edge-case-hunter (デッドロック・race condition)",
    ),
    SurfacePattern(
        category="cache",
        risk="high",
        patterns=[r"cache", r"_cache"],
        advice="edge-case-hunter (一貫性違反・stale data)",
    ),
    # Medium
    SurfacePattern(
        category="config",
        risk="medium",
        patterns=[r"config[/.]", r"\.env", r"environment"],
        advice="silent-failure-hunter (デフォルト値の安全性)",
    ),
    SurfacePattern(
        category="error_handling",
        risk="medium",
        patterns=[r"error[/.]", r"_error", r"panic", r"recover"],
        advice="silent-failure-hunter (エラー握り潰しリスク)",
    ),
    SurfacePattern(
        category="validation",
        risk="medium",
        patterns=[r"valid", r"sanitiz"],
        advice="edge-case-hunter (入力検証の抜け穴)",
    ),
]

RISK_ICONS = {"critical": "!!!", "high": "!!", "medium": "!"}


def load_seen() -> set[str]:
    try:
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_seen(seen: set[str]) -> None:
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def match_surfaces(file_path: str) -> list[SurfacePattern]:
    matched: list[SurfacePattern] = []
    for surface in SURFACES:
        for pattern in surface.patterns:
            if re.search(pattern, file_path, re.IGNORECASE):
                matched.append(surface)
                break
    return matched


def main() -> None:
    tool_input = json.loads(os.environ.get("TOOL_INPUT", "{}"))
    file_path = tool_input.get("file_path", "")

    if not file_path:
        return

    matched = match_surfaces(file_path)
    if not matched:
        return

    seen = load_seen()
    new_matches = [m for m in matched if m.category not in seen]
    if not new_matches:
        return

    seen.update(m.category for m in new_matches)
    save_seen(seen)

    # Build advisory message - only show highest risk
    highest = min(new_matches, key=lambda m: ["critical", "high", "medium"].index(m.risk))
    icon = RISK_ICONS[highest.risk]
    lines = [
        f"[Change Surface {icon}] {os.path.basename(file_path)} — "
        f"{highest.category} ({highest.risk})"
    ]
    for m in new_matches:
        lines.append(f"  推奨: {m.advice}")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
