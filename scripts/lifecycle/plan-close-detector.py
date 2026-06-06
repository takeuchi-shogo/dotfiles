#!/usr/bin/env python3
"""plan-close-detector — detect active plans that are actually complete.

Scans docs/plans/active/*.md, classifies close candidates into confidence
tiers. Tier1 (allowlisted asserts pass + clean tree / misplaced) is auto-PR
eligible; Tier2/3 are report-only. Default mode is dry-run (no file moves).
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
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


ASSERTS: dict[str, list[str]] = {
    "validate-configs": ["task", "validate-configs"],
    "validate-symlinks": ["task", "validate-symlinks"],
    "plan-close-tests": [
        "uv",
        "run",
        "pytest",
        "scripts/tests/test_plan_close_detector.py",
        "-q",
    ],
}
"""Fixed allowlist mapping an assert key to its argv (run with shell=False).

Plan frontmatter can only reference keys, never arbitrary commands — this is
the prompt-injection boundary: LLM or external text mixed into a plan cannot
smuggle a command into the nightly scanner. Keys absent from this map are
silently ignored, so an unknown or hostile key yields zero valid asserts.
"""


def _csv(field: str) -> list[str]:
    """Strip outer quotes and split a comma-separated frontmatter field."""
    v = field.strip().strip('"').strip("'")
    return [x.strip() for x in v.split(",") if x.strip()]


def artifacts_present(artifacts: str) -> bool:
    """Weak signal: every declared artifact path exists. None or empty is False."""
    paths = _csv(artifacts)
    return bool(paths) and all((REPO_ROOT / p).exists() for p in paths)


def asserts_satisfied(asserts: str) -> bool:
    """Strong signal: every allowlisted assert key exits 0 (shell=False).

    Keys not in ASSERTS are ignored; if no valid assert remains, return False
    (absence of evidence is not evidence of completion).
    """
    keys = [k for k in _csv(asserts) if k in ASSERTS]
    if not keys:
        return False
    for k in keys:
        try:
            rc = subprocess.run(
                ASSERTS[k],
                cwd=REPO_ROOT,
                timeout=120,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
        except (subprocess.SubprocessError, OSError):
            return False
        if rc != 0:
            return False
    return True


STALE_THRESHOLD_DAYS = 30
_CLOSED_LIFECYCLES = {"completed", "archive", "deferred", "done", "paused"}


@dataclass
class Verdict:
    result: str
    tier: int


def classify(
    signals: Signals,
    stale_days: int,
    tree_clean: bool,
    stale_threshold: int = STALE_THRESHOLD_DAYS,
) -> Verdict:
    """Classify a plan into a close-candidate tier.

    Tier1 (auto-PR eligible) requires either a misplaced lifecycle or a strong
    completion signal (allowlisted asserts pass AND a clean working tree). Path
    existence alone is only weak evidence (an in-progress file also exists), so
    it stays Tier2 to structurally prevent closing partially-done plans.
    """
    s = signals
    if s.lifecycle in _CLOSED_LIFECYCLES:
        return Verdict("MISPLACED", 1)
    if s.lifecycle != "active":
        return Verdict("HEALTHY", 0)
    if s.asserts and asserts_satisfied(s.asserts) and tree_clean:
        return Verdict("VERIFIED_DONE", 1)
    if s.artifacts and artifacts_present(s.artifacts):
        return Verdict("ARTIFACTS_PRESENT", 2)
    if (
        not s.asserts
        and not s.artifacts
        and stale_days >= stale_threshold
        and s.checkboxes_total > 0
        and s.checkboxes_done == s.checkboxes_total
    ):
        return Verdict("LIKELY_DONE", 2)
    if stale_days >= stale_threshold:
        return Verdict("STALE", 3)
    return Verdict("HEALTHY", 0)
