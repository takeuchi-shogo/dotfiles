#!/usr/bin/env python3
"""plan-close-detector — detect active plans that are actually complete.

Scans docs/plans/active/*.md, classifies close candidates into confidence
tiers. Tier1 (allowlisted asserts pass + clean tree / misplaced) is auto-PR
eligible; Tier2/3 are report-only. Default mode is dry-run (no file moves).
"""

from __future__ import annotations

import importlib.util
import re
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_DIR = REPO_ROOT / "docs" / "plans" / "active"

# Reuse the frontmatter parser from doc-status-audit.py (DRY — no third parser).
_audit_path = Path(__file__).resolve().parent / "doc-status-audit.py"
_spec = importlib.util.spec_from_file_location("doc_status_audit", _audit_path)
_audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_audit)
parse_frontmatter = _audit.parse_frontmatter

_CHECKBOX_DONE = re.compile(r"^\s*[-*] \[x\]", re.IGNORECASE | re.MULTILINE)
_CHECKBOX_TODO = re.compile(r"^\s*[-*] \[ \]", re.MULTILINE)


@dataclass
class Signals:
    path: Path
    lifecycle: str | None  # frontmatter lifecycle:、無ければ status: で後方互換
    artifacts: str | None  # 成果物パス列挙 (弱い証拠)
    asserts: str | None  # allowlist enum キー列挙 (強い証拠)
    checkboxes_total: int
    checkboxes_done: int


def extract_signals(path: Path) -> Signals:
    text = path.read_text(encoding="utf-8", errors="ignore")
    fields, _ = parse_frontmatter(text)
    fields = fields or {}
    done = len(_CHECKBOX_DONE.findall(text))
    todo = len(_CHECKBOX_TODO.findall(text))
    return Signals(
        path=path,
        lifecycle=fields.get("lifecycle") or fields.get("status"),
        artifacts=fields.get("artifacts"),
        asserts=fields.get("asserts"),
        checkboxes_total=done + todo,
        checkboxes_done=done,
    )
