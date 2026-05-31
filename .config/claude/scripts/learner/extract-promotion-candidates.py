#!/usr/bin/env python3
"""learned pending を昇格候補として抽出する純粋ロジック。

入力: learnings/patterns.jsonl (type==learned) + learnings/promoted-ledger.jsonl
出力: stdout に JSON {"count": N, "candidates": [...]}
副作用なし(読み取り専用)。冪等キーは generalized_detail(無ければ detail)の SHA1。
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

# scope → 推奨昇格先(初期推奨。最終配置は skill 内で Claude が提案しユーザーが承認)
SCOPE_ARTIFACT_MAP = {
    "cc-bash": "CLAUDE.md rule / references",
    "cc": "CLAUDE.md rule / references",
    "review-gate": "agents/code-reviewer.md",
    "zero-width": "policy script / security-reviewer",
    "absorb": "skills/absorb / references",
    "triage": "skills/absorb / references",
    "skills": "該当 skill",
    "skill-creation": "skills/skill-creator",
}


def candidate_key(rec: dict) -> str:
    basis = rec.get("generalized_detail") or rec.get("detail") or ""
    return hashlib.sha1(basis.encode("utf-8")).hexdigest()


def recommend_target(scope: str | None) -> str:
    return SCOPE_ARTIFACT_MAP.get(
        scope or "", "(手動判断: Claude が候補内容を読んで提案)"
    )


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # tolerant parse: 壊れた行はスキップ
    return out


def extract(patterns_path: Path, ledger_path: Path) -> list[dict]:
    processed = {e.get("key") for e in _read_jsonl(ledger_path) if e.get("key")}
    seen: set[str] = set()
    candidates: list[dict] = []
    for rec in _read_jsonl(patterns_path):
        if rec.get("type") != "learned":
            continue
        key = candidate_key(rec)
        if key in processed or key in seen:
            continue
        seen.add(key)
        candidates.append(
            {
                "key": key,
                "scope": rec.get("scope"),
                "detail": rec.get("generalized_detail") or rec.get("detail") or "",
                "recommended_target": recommend_target(rec.get("scope")),
                "importance": rec.get("importance", 0.5),
            }
        )
    candidates.sort(key=lambda c: -(c.get("importance") or 0.0))
    return candidates


def main() -> int:
    learnings = Path.home() / ".claude" / "agent-memory" / "learnings"
    cands = extract(learnings / "patterns.jsonl", learnings / "promoted-ledger.jsonl")
    print(
        json.dumps(
            {"count": len(cands), "candidates": cands}, ensure_ascii=False, indent=2
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
