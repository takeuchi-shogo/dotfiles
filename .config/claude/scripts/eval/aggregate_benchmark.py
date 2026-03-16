#!/usr/bin/env python3
"""Aggregate reviewer eval results and generate Before/After comparison report.

Usage:
    python3 aggregate_benchmark.py --single results/baseline.json
    python3 aggregate_benchmark.py --baseline results/baseline.json --current results/current.json
"""

import argparse
import json
from pathlib import Path


def compute_metrics(results: list[dict]) -> dict:
    """Compute Recall/Precision/F1 from eval results."""
    completed = [r for r in results if r["status"] == "completed"]
    if not completed:
        return {"recall": 0, "precision": 0, "f1": 0, "count": 0}

    detected = sum(1 for r in completed if r.get("pass"))
    total_expected = len(completed)
    total_findings = sum(r.get("findings_count", 0) for r in completed)
    total_correct = sum(
        len(r.get("matched_fms", [])) for r in completed if r.get("pass")
    )

    recall = detected / total_expected if total_expected else 0
    precision = total_correct / total_findings if total_findings else 0
    f1 = 2 * recall * precision / (recall + precision) if (recall + precision) else 0

    return {
        "recall": round(recall, 4),
        "precision": round(precision, 4),
        "f1": round(f1, 4),
        "count": len(completed),
        "detected": detected,
        "total_findings": total_findings,
    }


def compute_per_fm(results: list[dict]) -> dict[str, dict]:
    """Compute per-FM detection rate."""
    completed = [r for r in results if r["status"] == "completed"]
    fm_stats: dict[str, dict] = {}
    for r in completed:
        fm = r["expected_fm"]
        if fm not in fm_stats:
            fm_stats[fm] = {"total": 0, "detected": 0}
        fm_stats[fm]["total"] += 1
        if r.get("pass"):
            fm_stats[fm]["detected"] += 1
    for stats in fm_stats.values():
        stats["rate"] = (
            round(stats["detected"] / stats["total"], 4) if stats["total"] else 0
        )
    return fm_stats


def format_single_report(metrics: dict, per_fm: dict[str, dict]) -> str:
    """Format a single benchmark report."""
    lines = [
        "# Reviewer Benchmark Report",
        "",
        "## Overall Metrics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Recall | {metrics['recall']:.1%} |",
        f"| Precision | {metrics['precision']:.1%} |",
        f"| F1 | {metrics['f1']:.1%} |",
        f"| Cases | {metrics['count']} |",
        "",
        "## Per-FM Detection Rate",
        "",
        "| FM | Total | Detected | Rate |",
        "|----|-------|----------|------|",
    ]
    for fm, stats in sorted(per_fm.items()):
        lines.append(
            f"| {fm} | {stats['total']} | {stats['detected']} | {stats['rate']:.0%} |"
        )
    return "\n".join(lines)


def format_comparison_report(
    baseline_m: dict,
    current_m: dict,
    baseline_fm: dict[str, dict],
    current_fm: dict[str, dict],
) -> str:
    """Format a Before/After comparison report."""

    def delta(cur: float, base: float) -> str:
        d = cur - base
        sign = "+" if d >= 0 else ""
        return f"{sign}{d:.1%}"

    lines = [
        "# Reviewer Benchmark: Before/After Comparison",
        "",
        "## Overall Metrics",
        "",
        "| Metric | Baseline | Current | Delta |",
        "|--------|----------|---------|-------|",
        f"| Recall | {baseline_m['recall']:.1%} | {current_m['recall']:.1%} | {delta(current_m['recall'], baseline_m['recall'])} |",
        f"| Precision | {baseline_m['precision']:.1%} | {current_m['precision']:.1%} | {delta(current_m['precision'], baseline_m['precision'])} |",
        f"| F1 | {baseline_m['f1']:.1%} | {current_m['f1']:.1%} | {delta(current_m['f1'], baseline_m['f1'])} |",
        "",
        "## Per-FM Comparison",
        "",
        "| FM | Baseline Rate | Current Rate | Delta |",
        "|----|---------------|--------------|-------|",
    ]
    all_fms = sorted(set(list(baseline_fm.keys()) + list(current_fm.keys())))
    for fm in all_fms:
        b_rate = baseline_fm.get(fm, {}).get("rate", 0)
        c_rate = current_fm.get(fm, {}).get("rate", 0)
        lines.append(
            f"| {fm} | {b_rate:.0%} | {c_rate:.0%} | {delta(c_rate, b_rate)} |"
        )

    recall_delta = current_m["recall"] - baseline_m["recall"]
    precision_delta = current_m["precision"] - baseline_m["precision"]
    f1_delta = current_m["f1"] - baseline_m["f1"]

    lines.extend(
        [
            "",
            "## Success Criteria",
            "",
            f"- Recall +10pt: {'PASS' if recall_delta >= 0.10 else 'FAIL'} ({delta(current_m['recall'], baseline_m['recall'])})",
            f"- Precision -5pt max: {'PASS' if precision_delta >= -0.05 else 'FAIL'} ({delta(current_m['precision'], baseline_m['precision'])})",
            f"- F1 +5pt: {'PASS' if f1_delta >= 0.05 else 'FAIL'} ({delta(current_m['f1'], baseline_m['f1'])})",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate benchmark results")
    parser.add_argument("--single", help="Single result JSON for standalone report")
    parser.add_argument("--baseline", help="Baseline result JSON for comparison")
    parser.add_argument("--current", help="Current result JSON for comparison")
    parser.add_argument("--output", default=None, help="Output path (default: stdout)")
    args = parser.parse_args()

    if args.single:
        with open(args.single) as f:
            results = json.load(f)
        metrics = compute_metrics(results)
        per_fm = compute_per_fm(results)
        report = format_single_report(metrics, per_fm)
    elif args.baseline and args.current:
        with open(args.baseline) as f:
            baseline = json.load(f)
        with open(args.current) as f:
            current = json.load(f)
        report = format_comparison_report(
            compute_metrics(baseline),
            compute_metrics(current),
            compute_per_fm(baseline),
            compute_per_fm(current),
        )
    else:
        parser.error("Provide --single or both --baseline and --current")
        return

    if args.output:
        Path(args.output).write_text(report + "\n")
        print(f"Report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
