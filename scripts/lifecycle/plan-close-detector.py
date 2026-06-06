#!/usr/bin/env python3
"""plan-close-detector — detect active plans that are actually complete.

Scans docs/plans/active/*.md, classifies close candidates into confidence
tiers. Tier1 (allowlisted asserts pass + clean tree / misplaced) is auto-PR
eligible; Tier2/3 are report-only. Default mode is dry-run (no file moves).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_DIR = REPO_ROOT / "docs" / "plans" / "active"

# Reuse the frontmatter parser from doc-status-audit.py (DRY — no third parser).
_audit_path = Path(__file__).resolve().parent / "doc-status-audit.py"
if not _audit_path.exists():
    raise ImportError(f"doc-status-audit.py not found: {_audit_path}")
_spec = importlib.util.spec_from_file_location("doc_status_audit", _audit_path)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Cannot load spec from {_audit_path}")
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


def _within_repo(p: str) -> Path | None:
    """Resolve p under REPO_ROOT, returning None if it escapes the repo.

    artifacts come from plan frontmatter, which the threat model treats as
    untrusted; a `../` traversal must never let an out-of-repo path count as a
    present artifact (and, once apply lands, become a move target).
    """
    resolved = (REPO_ROOT / p).resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError:
        return None
    return resolved


def artifacts_present(artifacts: str) -> bool:
    """Weak signal: every declared artifact path exists. None or empty is False."""
    paths = _csv(artifacts)
    if not paths:
        return False
    resolved = [_within_repo(p) for p in paths]
    return all(r is not None and r.exists() for r in resolved)


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
    if s.lifecycle is not None and s.lifecycle != "active":
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


def git_stale_days(path: Path) -> int:
    """Days since the last commit touching path; falls back to mtime if untracked."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", str(path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout.strip()
    except (subprocess.SubprocessError, OSError):
        out = ""
    if out:
        last = datetime.fromisoformat(out)
        return (datetime.now(timezone.utc) - last).days
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        return (datetime.now(timezone.utc) - mtime).days
    except OSError:
        return 0


def tree_clean_for(artifacts: str | None) -> bool:
    """True if the declared artifact paths have no uncommitted changes.

    When no artifacts are declared the tree condition is neutral (True) and
    Tier1 is gated by asserts instead. If git cannot be queried, return False
    as a fail-safe so an undeterminable state never gets promoted to Tier1.
    """
    paths = _csv(artifacts) if artifacts else []
    if not paths:
        return True
    try:
        rc = subprocess.run(
            ["git", "diff", "--quiet", "--", *paths], cwd=REPO_ROOT, timeout=30
        ).returncode
        rc2 = subprocess.run(
            ["git", "diff", "--cached", "--quiet", "--", *paths],
            cwd=REPO_ROOT,
            timeout=30,
        ).returncode
        return rc == 0 and rc2 == 0
    except (subprocess.SubprocessError, OSError):
        return False


def scan(active_dir: Path = ACTIVE_DIR) -> list[dict]:
    rows = []
    for f in sorted(active_dir.glob("*.md")):
        sig = extract_signals(f)
        stale = git_stale_days(f)
        verdict = classify(sig, stale, tree_clean=tree_clean_for(sig.artifacts))
        if verdict.tier == 0:
            continue
        rows.append(
            {
                "file": str(f.relative_to(REPO_ROOT)),
                "result": verdict.result,
                "tier": verdict.tier,
                "lifecycle": sig.lifecycle,
                "artifacts": sig.artifacts,
                "asserts": sig.asserts,
                "checkboxes": f"{sig.checkboxes_done}/{sig.checkboxes_total}",
                "stale_days": stale,
            }
        )
    return rows


def render_report(rows: list[dict], today: str) -> str:
    lines = [f"# Plan close-candidate report — {today}", ""]
    for tier in (1, 2, 3):
        group = [r for r in rows if r["tier"] == tier]
        label = {
            1: "Tier1 (auto-PR 対象)",
            2: "Tier2 (報告のみ)",
            3: "Tier3 (stale のみ)",
        }[tier]
        lines.append(f"## {label} — {len(group)} 件")
        for r in group:
            lines.append(
                f"- `{r['file']}` — {r['result']} "
                f"(lifecycle={r['lifecycle']}, checkbox={r['checkboxes']}, "
                f"stale={r['stale_days']}d)"
            )
        lines.append("")
    return "\n".join(lines)


_LIFECYCLE_TO_DIR = {
    "completed": "completed",
    "archive": "completed",
    "done": "completed",
    "deferred": "paused",
    "paused": "paused",
}


def plan_moves() -> list[dict]:
    """Pure planner: return the move plan for Tier1 candidates (no git side effects).

    Kept side-effect-free so the move targets can be unit-tested without
    touching the index or working tree.
    """
    moves = []
    for f in sorted(ACTIVE_DIR.glob("*.md")):
        sig = extract_signals(f)
        verdict = classify(
            sig, git_stale_days(f), tree_clean=tree_clean_for(sig.artifacts)
        )
        if verdict.tier != 1:
            continue
        if verdict.result == "MISPLACED":
            dest_dir = _LIFECYCLE_TO_DIR.get(sig.lifecycle or "", "completed")
            new_lifecycle = sig.lifecycle
        else:
            dest_dir, new_lifecycle = "completed", "completed"
        moves.append(
            {
                "from": str(f.relative_to(REPO_ROOT)),
                "to": f"docs/plans/{dest_dir}/{f.name}",
                "result": verdict.result,
                "new_lifecycle": new_lifecycle,
                "rationale": (
                    f"{verdict.result}: lifecycle={sig.lifecycle}, "
                    f"asserts={sig.asserts}"
                ),
            }
        )
    return moves


def apply_via_pr() -> int:
    """Safety-layered auto-apply: preflight, then move on a branch and open a PR.

    This never commits or moves on the current branch directly: a human merge
    of the PR is the final gate. The actual PR creation stays disabled until
    the 30-day calibration milestone proves a Tier1 human-agree rate >= 0.9.
    """
    unstaged = subprocess.run(["git", "diff", "--quiet"], cwd=REPO_ROOT).returncode
    staged = subprocess.run(
        ["git", "diff", "--cached", "--quiet"], cwd=REPO_ROOT
    ).returncode
    if unstaged != 0 or staged != 0:
        raise SystemExit(
            "[plan-close] working tree dirty (staged or unstaged); abort (preflight)"
        )
    moves = plan_moves()
    if not moves:
        print("[plan-close] no Tier1 candidates")
        return 0
    raise SystemExit(
        "apply_via_pr: PR 化手順は pr-review-*.sh パターンで実装する (calibration 後)"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--apply-tier1",
        action="store_true",
        help="Tier1 候補を PR 提案として生成 (calibration 後のみ、直接 move しない)",
    )
    ap.add_argument("--out", default=str(REPO_ROOT / "docs" / "plan-close"))
    args = ap.parse_args()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rows = scan()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{today}-close-report.md").write_text(
        render_report(rows, today), encoding="utf-8"
    )
    with (out_dir / "candidates.jsonl").open("a", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps({**r, "scanned": today}, ensure_ascii=False) + "\n")
    if args.apply_tier1:
        return apply_via_pr()
    print(f"scanned: {len(rows)} candidates → {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
