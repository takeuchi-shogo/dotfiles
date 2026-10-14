#!/usr/bin/env python3
"""AgentShield false-positive / dedup filter + reproduction staging.

Runs `npx ecc-agentshield scan` (or reads --from-json) and applies a Logos-inspired
pipeline stage:

  1. product context   — scan target is agent config (~/.claude), not arbitrary app code
  2. split scans       — AgentShield owns internal file walk; this wrapper is one stage
  3. dedup + FP filter — duplicate fingerprints + known false positives
  4. reproduction      — semi-automated checklist attached per remaining finding
  5. feedback loop     — suppressed/deduped counts returned for next nightly report

Sources (read):
  https://blog.cybozu.io/entry/logos-overview
  https://blog.cybozu.io/entry/logos-harness-horos
Caveat: Cybozu Horos is product SAST/DAST + PSIRT triage. This wrapper only
mirrors the stage shape for AgentShield agent-config scans — not a port of Horos.

Usage:
    python3 agentshield-filter.py [--path PATH] [--fix] [--format FORMAT]
    python3 agentshield-filter.py --from-json FILE [--format json]
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Iterable

# --- False positive suppression rules ---

# settings.json deny section (lines 59-84) contains keywords that
# AgentShield misidentifies as vulnerabilities
DENY_SECTION_RANGE = (59, 84)

# Keywords that appear in deny rules — when found in settings.json
# within the deny section, they are protections, not vulnerabilities
DENY_KEYWORDS = {
    "--no-verify",
    "rm -rf",
    "sudo",
    "curl",
    "wget",
    "ssh",
    "scp",
    "nc",
    "ncat",
    "netcat",
    "~/.ssh/",
    "~/.aws/",
    "chmod 777",
    "git push --force",
    "git reset --hard",
    "git clean -f",
    "git checkout --",
}

# Documentation files that reference dangerous patterns to say "don't do X"
DOC_FP_PATTERNS = {
    ("CLAUDE.md", "--no-verify"),
    ("commands/security-scan.md", "--no-verify"),
}

# Version check commands are not "interpreter access"
VERSION_CHECK_EVIDENCE = {
    "Bash(node --version)",
    "Bash(python3 --version)",
    "Bash(go version)",
    "Bash(git --version)",
    "Bash(rustc --version)",
    "Bash(cargo --version)",
}

# Normal English text misidentified as encoded payloads
BENIGN_TEXT_PATTERNS = {
    "backwards compatibility",
    "backwards compatible",
}

PIPELINE_STAGES = (
    "product_context",
    "split_scans",
    "dedup_false_positive",
    "reproduction_check",
    "feedback_loop",
)

REPRO_SEVERITIES = frozenset({"critical", "high", "medium"})


def is_false_positive(finding: dict) -> tuple[bool, str]:
    """Check if a finding is a known false positive. Returns (is_fp, reason)."""
    file = finding.get("file", "")
    line = finding.get("line", 0)
    evidence = finding.get("evidence", "")

    # 1. Deny section in settings.json
    if (
        file == "settings.json"
        and DENY_SECTION_RANGE[0] <= line <= DENY_SECTION_RANGE[1]
    ):
        return True, "deny ルール内のキーワード"

    # 2. Documentation referencing dangerous patterns
    for doc_file, doc_evidence in DOC_FP_PATTERNS:
        if file == doc_file and evidence == doc_evidence:
            return True, f"{doc_file} 内の禁止規則の説明"

    # 3. Version check commands
    if evidence in VERSION_CHECK_EVIDENCE:
        return True, "バージョン確認コマンド（interpreter access ではない）"

    # 4. Benign text misidentified as encoded payloads
    if any(pattern in evidence.lower() for pattern in BENIGN_TEXT_PATTERNS):
        return True, "通常テキストの誤検出"

    return False, ""


def finding_fingerprint(finding: dict) -> str:
    """Stable dedup key: title + file + line + evidence."""
    title = str(finding.get("title", "")).strip().lower()
    file = str(finding.get("file", "")).strip()
    line = finding.get("line", "")
    evidence = str(finding.get("evidence", "")).strip()
    return f"{title}|{file}|{line}|{evidence}"


def dedup_findings(findings: Iterable[dict]) -> tuple[list[dict], list[dict]]:
    """Keep first occurrence; return (unique, duplicates)."""
    seen: set[str] = set()
    unique: list[dict] = []
    duplicates: list[dict] = []
    for finding in findings:
        key = finding_fingerprint(finding)
        if key in seen:
            duplicates.append(finding)
            continue
        seen.add(key)
        unique.append(finding)
    return unique, duplicates


def attach_reproduction_stage(findings: list[dict]) -> list[dict]:
    """Attach semi-automated reproduction checklist fields.

    Modeled on Logos/Horos: before human triage, ask whether the issue
    already reported / actually reproducible. This does NOT execute exploits;
    it only stages checklist metadata for operators or follow-up agents.
    """
    enriched: list[dict] = []
    for finding in findings:
        item = dict(finding)
        severity = str(item.get("severity", "")).lower()
        needs = severity in REPRO_SEVERITIES
        item["reproduction"] = {
            "status": "pending" if needs else "not_required",
            "semi_automated": needs,
            "checklist": (
                [
                    "Confirm finding is not a duplicate of a prior nightly report",
                    "Reproduce via the cited file:line / evidence without changing secrets",
                    "Record pass/fail + one-line proof in the nightly report feedback section",
                ]
                if needs
                else ["Low/info: no reproduction stage required"]
            ),
        }
        enriched.append(item)
    return enriched


def filter_pipeline(findings: list[dict]) -> dict:
    """Run FP filter → dedup → reproduction staging. Pure (no I/O)."""
    suppressed: list[tuple[dict, str]] = []
    kept: list[dict] = []
    for finding in findings:
        fp, reason = is_false_positive(finding)
        if fp:
            suppressed.append((finding, reason))
        else:
            kept.append(finding)

    unique, duplicates = dedup_findings(kept)
    staged = attach_reproduction_stage(unique)
    return {
        "findings": staged,
        "suppressed": suppressed,
        "deduped": duplicates,
        "stages": list(PIPELINE_STAGES),
    }


def recalculate_score(findings: list[dict]) -> dict:
    """Recalculate grade based on filtered findings."""
    severity_weights = {"critical": 20, "high": 10, "medium": 3, "low": 1, "info": 0}
    total_penalty = sum(severity_weights.get(f["severity"], 0) for f in findings)
    score = max(0, 100 - total_penalty)

    if score >= 90:
        grade = "A"
    elif score >= 70:
        grade = "B"
    elif score >= 50:
        grade = "C"
    elif score >= 30:
        grade = "D"
    else:
        grade = "F"

    by_category: dict[str, int] = {}
    for f in findings:
        cat = f.get("category", "unknown")
        by_category.setdefault(cat, 0)
        by_category[cat] += severity_weights.get(f["severity"], 0)

    return {
        "grade": grade,
        "numericScore": score,
        "penalty": total_penalty,
        "byCategory": by_category,
    }


def print_terminal_report(
    data: dict,
    filtered: list[dict],
    suppressed: list[tuple[dict, str]],
    deduped: list[dict],
    score: dict,
) -> None:
    """Print human-readable filtered report."""
    print("\n  AgentShield Filtered Report\n")
    print(f"  Grade: {score['grade']} ({score['numericScore']}/100)")
    raw = data["summary"]["totalFindings"]
    sup = len(suppressed)
    ded = len(deduped)
    flt = len(filtered)
    print(
        f"  Raw: {raw} → Filtered: {flt} "
        f"(suppressed {sup} FPs, deduped {ded})\n"
    )
    pending_repro = sum(
        1
        for f in filtered
        if (f.get("reproduction") or {}).get("status") == "pending"
    )
    print(f"  Reproduction pending: {pending_repro}\n")

    severity_order = ["critical", "high", "medium", "low", "info"]
    icons = {"critical": "●", "high": "●", "medium": "●", "low": "●", "info": "○"}

    for sev in severity_order:
        sev_findings = [f for f in filtered if f["severity"] == sev]
        for f in sev_findings:
            icon = icons.get(sev, "○")
            loc = f"{f['file']}:{f.get('line', '?')}" if f.get("line") else f["file"]
            print(f"  {icon} {sev.upper()}  {f['title']}")
            print(f"    {loc}")
            if f.get("evidence"):
                print(f"    Evidence: {f['evidence']}")
            repro = f.get("reproduction") or {}
            if repro.get("status") == "pending":
                print("    Reproduction: pending (semi-automated checklist)")
            print()

    if suppressed:
        print(f"  --- Suppressed ({len(suppressed)} false positives) ---")
        reasons: dict[str, int] = {}
        for _, reason in suppressed:
            reasons[reason] = reasons.get(reason, 0) + 1
        for reason, count in reasons.items():
            print(f"    {count}x {reason}")
        print()

    if deduped:
        print(f"  --- Deduped ({len(deduped)} duplicates) ---")
        print(f"    {len(deduped)}x duplicate fingerprint")
        print()


def _split_from_json_arg(args: list[str]) -> tuple[list[str], str | None]:
    """Extract --from-json PATH; return (remaining_args, path_or_none)."""
    remaining: list[str] = []
    from_json: str | None = None
    i = 0
    while i < len(args):
        if args[i] == "--from-json" and i + 1 < len(args):
            from_json = args[i + 1]
            i += 2
            continue
        if args[i].startswith("--from-json="):
            from_json = args[i].split("=", 1)[1]
            i += 1
            continue
        remaining.append(args[i])
        i += 1
    return remaining, from_json


def load_scan_data(args: list[str]) -> tuple[dict, list[str]]:
    """Load AgentShield JSON either from --from-json or by running npx."""
    passthrough, from_json = _split_from_json_arg(args)
    if from_json:
        with open(from_json, encoding="utf-8") as fh:
            return json.load(fh), passthrough

    cmd = ["npx", "ecc-agentshield", "scan", "--format", "json"] + passthrough
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout or result.stderr
    if not output.strip():
        print("AgentShield produced no output", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(output), passthrough
    except json.JSONDecodeError:
        print(f"Failed to parse AgentShield output:\n{output[:500]}", file=sys.stderr)
        sys.exit(2)


def build_json_output(
    data: dict,
    filtered: list[dict],
    suppressed: list[tuple[dict, str]],
    deduped: list[dict],
    score: dict,
) -> dict:
    pending_repro = [
        f for f in filtered if (f.get("reproduction") or {}).get("status") == "pending"
    ]
    return {
        "timestamp": data.get("timestamp"),
        "targetPath": data.get("targetPath"),
        "pipeline": {
            "stages": list(PIPELINE_STAGES),
            "productContext": "agent-config (~/.claude CLAUDE.md/hooks/skills/settings)",
            "modeledOn": "Cybozu Logos/Horos stage shape (not a Horos port)",
        },
        "findings": filtered,
        "suppressed": len(suppressed),
        "deduped": len(deduped),
        "reproductionPending": len(pending_repro),
        "score": score,
        "summary": {
            "totalFindings": len(filtered),
            "critical": sum(1 for f in filtered if f["severity"] == "critical"),
            "high": sum(1 for f in filtered if f["severity"] == "high"),
            "medium": sum(1 for f in filtered if f["severity"] == "medium"),
            "low": sum(1 for f in filtered if f["severity"] == "low"),
            "info": sum(1 for f in filtered if f["severity"] == "info"),
            "filesScanned": data.get("summary", {}).get("filesScanned", 0),
            "autoFixable": sum(1 for f in filtered if f.get("fix", {}).get("auto")),
        },
        "raw": {
            "totalFindings": data["summary"]["totalFindings"],
            "grade": data["score"]["grade"],
            "score": data["score"]["numericScore"],
        },
        "feedback": {
            "suppressedReasons": _reason_histogram(suppressed),
            "dedupedCount": len(deduped),
            "reproductionChecklistRemaining": len(pending_repro),
        },
    }


def _reason_histogram(suppressed: list[tuple[dict, str]]) -> dict[str, int]:
    reasons: dict[str, int] = {}
    for _, reason in suppressed:
        reasons[reason] = reasons.get(reason, 0) + 1
    return reasons


def main() -> None:
    args = sys.argv[1:]
    data, passthrough = load_scan_data(args)
    findings = data.get("findings", [])
    pipeline = filter_pipeline(findings)
    filtered = pipeline["findings"]
    suppressed = pipeline["suppressed"]
    deduped = pipeline["deduped"]
    score = recalculate_score(filtered)

    wants_json = "--format" in passthrough and "json" in passthrough
    if wants_json:
        print(
            json.dumps(
                build_json_output(data, filtered, suppressed, deduped, score),
                indent=2,
            )
        )
    else:
        print_terminal_report(data, filtered, suppressed, deduped, score)

    critical_count = sum(1 for f in filtered if f["severity"] == "critical")
    sys.exit(1 if critical_count > 0 else 0)


if __name__ == "__main__":
    main()
