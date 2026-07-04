#!/usr/bin/env python3
"""Memory vector recall UserPromptSubmit hook.

Mechanizes the CLAUDE.md `<important if="...judgment/decision/research...">` rule:
when the prompt looks like a judgment / design / research turn, run a semantic
top-K against the vault+wiki slices of ~/.claude/skill-data/memory-vec/index.db
and print a PATH-ONLY [Knowledge Recall] block. File body is never included —
the agent expands with Read on demand (pointer push, body pull).

Why gate on prompt intent, not distance: the index corpus is topically
homogeneous (all AI/agent/dotfiles), so cosine distance cannot separate
"needs Vault knowledge" from routine coding (off-topic floor ~1.17 overlaps
on-topic top ~1.12). The signal is in the prompt intent. Distance is demoted
to a loose garbage filter only.

Runs on EVERY prompt, so the gate (`is_intent_prompt`) is pure regex with no
subprocess — non-matching turns cost ~0 and cannot fail. The query.ts
subprocess fires only on a gate match. Always exits 0 (must never block a
prompt). Mirrors memory-vec-hint-hook.py hardening.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

SKILL_DATA = Path.home() / ".claude" / "skill-data" / "memory-vec"
INDEX_DB = SKILL_DATA / "index.db"
QUERY_SCRIPT = SKILL_DATA / "query.ts"
LOG_FILE = Path.home() / ".claude" / "logs" / "memory-vec.log"
REDACTOR_LIB = SKILL_DATA / "lib"

QUERY_TIMEOUT_SEC = 8.0
QUERY_MAX_CHARS = 2000
DISTANCE_THRESHOLD = 1.3
TOP_K = 3
STDERR_LOG_CAP = 500

# Intent gate. Japanese terms are matched as plain substrings (\b misbehaves on
# Japanese — see memory). English terms get a leading ASCII boundary guard so
# "decide" does not fire inside "undecided". Mirrors the CLAUDE.md judgment
# /decision/research condition that this hook makes deterministic.
_JP_TERMS = (
    "どっち",
    "どちら",
    "比較",
    "トレードオフ",
    "採用",
    "導入",
    "選定",
    "選ぶ",
    "判断",
    "決め",
    "決断",
    "設計",
    "方針",
    "検討",
    "評価",
    "レビュー",
    "移行",
    "べきか",
    "すべき",
    "メリット",
    "デメリット",
    "良い方法",
    "どうする",
    "技術選定",
    "セカンドオピニオン",
    "意見",
)
_EN_TERMS = (
    "should i",
    "trade-off",
    "tradeoff",
    "compare",
    "comparison",
    "decide",
    "decision",
    "evaluate",
    "which is better",
    "adopt",
    "pros and cons",
    "second opinion",
)
_JP_PATTERN = re.compile("|".join(re.escape(t) for t in _JP_TERMS))
_EN_PATTERN = re.compile("|".join(f"(?<![a-z0-9]){re.escape(t)}" for t in _EN_TERMS))


def is_intent_prompt(prompt: str) -> bool:
    """True when the prompt reads as a judgment/design/research turn."""
    if not prompt or not prompt.strip():
        return False
    lowered = prompt.lower()
    return bool(_JP_PATTERN.search(prompt) or _EN_PATTERN.search(lowered))


def _resolve_node() -> str | None:
    return shutil.which("node")


def _scrub(text: str) -> str:
    if not text:
        return text
    try:
        if str(REDACTOR_LIB) not in sys.path:
            sys.path.insert(0, str(REDACTOR_LIB))
        from memory_redactor import redact_for_embedding  # type: ignore

        return redact_for_embedding(text)
    except (ImportError, OSError, ValueError) as exc:
        truncated = text if len(text) <= 200 else f"{text[:200]}... [truncated]"
        return f"[REDACT_UNAVAILABLE: {type(exc).__name__}] {truncated}"


def _log(stage: str, error: BaseException, extra: dict | None = None) -> None:
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        entry: dict = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "source": "memory-vec-recall-hook",
            "stage": stage,
            "error": _scrub(f"{type(error).__name__}: {error}"),
            "traceback": _scrub(traceback.format_exc()),
        }
        if extra:
            entry.update({k: _scrub(str(v)) for k, v in extra.items()})
        with LOG_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        return


def _log_event(stage: str, payload: dict) -> None:
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        entry: dict = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "source": "memory-vec-recall-hook",
            "stage": stage,
        }
        for k, v in payload.items():
            entry[k] = _scrub(str(v)) if isinstance(v, str) else v
        with LOG_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        return


def _read_prompt() -> str | None:
    """Read the prompt from the UserPromptSubmit payload."""
    try:
        raw = sys.stdin.read()
        if not raw:
            return None
        payload = json.loads(raw)
        prompt = payload.get("prompt")
        if isinstance(prompt, str) and prompt.strip():
            return prompt
        _log_event(
            "prompt_unusable",
            {
                "keys": list(payload)
                if isinstance(payload, dict)
                else type(payload).__name__
            },
        )
    except (OSError, ValueError, TypeError) as exc:
        _log("payload_parse", exc)
    return None


def _run_query(query: str, node_bin: str) -> list[dict] | None:
    if not INDEX_DB.is_file() or not QUERY_SCRIPT.is_file():
        _log_event(
            "index_unavailable",
            {"index_db": INDEX_DB.is_file(), "query_script": QUERY_SCRIPT.is_file()},
        )
        return None
    try:
        result = subprocess.run(
            [
                node_bin,
                "--experimental-strip-types",
                "--no-warnings",
                str(QUERY_SCRIPT),
                query[:QUERY_MAX_CHARS],
                "--source",
                "vault,wiki",
            ],
            capture_output=True,
            text=True,
            timeout=QUERY_TIMEOUT_SEC,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        _log("query_subprocess", exc)
        return None

    if result.returncode != 0:
        _log_event(
            "query_nonzero",
            {
                "returncode": result.returncode,
                "stderr": (result.stderr or "")[:STDERR_LOG_CAP],
            },
        )
        return None
    if not result.stdout.strip():
        return None
    try:
        rows = json.loads(result.stdout)
    except ValueError as exc:
        _log("query_parse", exc)
        return None
    return rows if isinstance(rows, list) else None


def _format_hint(rows: list[dict]) -> str:
    filtered = [
        r
        for r in rows
        if isinstance(r, dict)
        and isinstance(r.get("distance"), (int, float))
        and r["distance"] < DISTANCE_THRESHOLD
        and isinstance(r.get("path"), str)
    ][:TOP_K]
    if not filtered:
        return ""

    header = (
        "[Knowledge Recall] この判断に関連しうるノート "
        "(Vault/wiki, top-{0}, ephemeral):"
    )
    lines = [header.format(len(filtered))]
    for r in filtered:
        lines.append(f"- {r['path']} (rel: {r['distance']:.2f})")
    lines.append("")
    lines.append(
        "必要時のみ Read で展開。Vault/wiki は単方向同期のスナップショット — "
        "現行コード/事実と矛盾したら現状を優先。本 hint に file 内容は含まれません。"
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    prompt = _read_prompt()
    if prompt is None or not is_intent_prompt(prompt):
        return 0

    node_bin = _resolve_node()
    if node_bin is None:
        _log_event("node_missing", {"note": "node binary not found in PATH"})
        return 0

    rows = _run_query(prompt, node_bin)
    if rows is None:
        return 0

    hint = _format_hint(rows)
    if hint:
        sys.stdout.write(hint)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        _log("unhandled", exc)
        sys.exit(0)
