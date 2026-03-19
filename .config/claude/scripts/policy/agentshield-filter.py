#!/usr/bin/env python3
"""AgentShield false-positive filter.

Runs `npx ecc-agentshield scan` and filters out known false positives
caused by deny rules, documentation references, and version-check commands.

Usage:
    python3 agentshield-filter.py [--path PATH] [--fix] [--format FORMAT]

Outputs filtered results with recalculated score.
"""

from __future__ import annotations

import json
import subprocess
import sys

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
    ("commands/commit.md", "--no-verify"),
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
    data: dict, filtered: list[dict], suppressed: list[dict], score: dict
) -> None:
    """Print human-readable filtered report."""
    print("\n  AgentShield Filtered Report\n")
    print(f"  Grade: {score['grade']} ({score['numericScore']}/100)")
    raw = data["summary"]["totalFindings"]
    sup = len(suppressed)
    flt = len(filtered)
    print(f"  Raw: {raw} → Filtered: {flt} (suppressed {sup} FPs)\n")

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
            print()

    if suppressed:
        print(f"  --- Suppressed ({len(suppressed)} false positives) ---")
        reasons: dict[str, int] = {}
        for _, reason in suppressed:
            reasons[reason] = reasons.get(reason, 0) + 1
        for reason, count in reasons.items():
            print(f"    {count}x {reason}")
        print()


def main() -> None:
    # Pass through CLI args to agentshield
    args = sys.argv[1:]
    cmd = ["npx", "ecc-agentshield", "scan", "--format", "json"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)

    output = result.stdout or result.stderr
    if not output.strip():
        print("AgentShield produced no output", file=sys.stderr)
        sys.exit(2)

    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        print(f"Failed to parse AgentShield output:\n{output[:500]}", file=sys.stderr)
        sys.exit(2)

    findings = data.get("findings", [])

    filtered = []
    suppressed = []
    for f in findings:
        fp, reason = is_false_positive(f)
        if fp:
            suppressed.append((f, reason))
        else:
            filtered.append(f)

    score = recalculate_score(filtered)

    # Check if JSON output was requested
    wants_json = "--format" in args and "json" in args
    if wants_json:
        output_data = {
            "timestamp": data.get("timestamp"),
            "targetPath": data.get("targetPath"),
            "findings": filtered,
            "suppressed": len(suppressed),
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
        }
        print(json.dumps(output_data, indent=2))
    else:
        print_terminal_report(data, filtered, suppressed, score)

    # Exit with appropriate code
    critical_count = sum(1 for f in filtered if f["severity"] == "critical")
    sys.exit(1 if critical_count > 0 else 0)


if __name__ == "__main__":
    main()
