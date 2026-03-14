"""Skill amendment engine — SKILL.md parsing, health assessment, and proposal generation.

autoevolve-core の Phase 2 から呼び出される。
SKILL.md の解析、スキル健全性の判定、修正提案の生成を行う。
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path



@dataclass
class SkillManifest:
    """SKILL.md の構造化表現。"""

    name: str
    description: str
    body: str
    path: Path
    raw_frontmatter: dict = field(default_factory=dict)
    content_hash: str = ""


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """--- で囲まれたフロントマターを解析し、(frontmatter_dict, body) を返す。

    Handles:
    - key: value (simple)
    - key: "quoted value" or key: 'quoted value'
    - key: > (folded scalar, multiline with 2-space indent continuation)
    - Missing frontmatter (no --- delimiters)
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
    if not match:
        return {}, text

    fm_text = match.group(1)
    body = match.group(2)
    result: dict[str, str] = {}

    current_key: str | None = None
    multiline_value: list[str] = []

    for line in fm_text.split("\n"):
        kv = re.match(r"^(\S[^:]*?):\s*(.*)", line)
        if kv:
            if current_key and multiline_value:
                result[current_key] = " ".join(multiline_value).strip()
                multiline_value = []

            key = kv.group(1).strip()
            value = kv.group(2).strip()

            if value in (">", "|"):
                current_key = key
                multiline_value = []
                continue

            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]

            result[key] = value
            current_key = None
        elif current_key and line.startswith("  "):
            multiline_value.append(line.strip())

    if current_key and multiline_value:
        result[current_key] = " ".join(multiline_value).strip()

    return result, body


def parse_skill(path: Path) -> SkillManifest:
    """SKILL.md を解析して SkillManifest を返す。"""
    text = path.read_text(encoding="utf-8")
    fm, body = _parse_frontmatter(text)
    content_hash = hashlib.sha256(text.encode()).hexdigest()[:8]

    return SkillManifest(
        name=fm.get("name", ""),
        description=fm.get("description", ""),
        body=body,
        path=path,
        raw_frontmatter={
            k: v for k, v in fm.items() if k not in ("name", "description")
        },
        content_hash=content_hash,
    )
