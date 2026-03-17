#!/usr/bin/env python3
"""Aggregate reviewer eval results and generate comparison reports.

Usage:
    python3 aggregate_benchmark.py --single results/baseline.json
    python3 aggregate_benchmark.py \
        --baseline results/baseline.json \
        --current results/current.json
    python3 aggregate_benchmark.py \
        --variants v1.json v2.json v3.json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from rl_advantage import grpo_advantage, rloo_advantage


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


def compute_rloo_metrics(
    variant_results: list[list[dict]],
) -> dict:
    """K variant の結果から RLOO advantage を計算する。

    Args:
        variant_results: K 個の result リスト

    Returns:
        各 variant の metrics + RLOO advantage を含む辞書。
    """
    metrics_list = [compute_metrics(vr) for vr in variant_results]
    f1_scores = [m["f1"] for m in metrics_list]
    advantages = rloo_advantage(f1_scores)

    return {
        "method": "rloo",
        "variants": [
            {
                "index": i,
                **metrics_list[i],
                "advantage": advantages[i] if advantages else 0.0,
            }
            for i in range(len(metrics_list))
        ],
        "best_variant": (
            max(range(len(f1_scores)), key=lambda i: f1_scores[i])
            if f1_scores
            else None
        ),
    }


def compute_grpo_metrics(
    variant_results: list[list[dict]],
) -> dict:
    """K variant の結果から GRPO advantage を計算する。

    Args:
        variant_results: K 個の result リスト

    Returns:
        各 variant の metrics + GRPO advantage を含む辞書。
    """
    metrics_list = [compute_metrics(vr) for vr in variant_results]
    f1_scores = [m["f1"] for m in metrics_list]
    advantages = grpo_advantage(f1_scores)

    return {
        "method": "grpo",
        "variants": [
            {
                "index": i,
                **metrics_list[i],
                "advantage": advantages[i] if advantages else 0.0,
            }
            for i in range(len(metrics_list))
        ],
        "best_variant": (
            max(range(len(f1_scores)), key=lambda i: f1_scores[i])
            if f1_scores
            else None
        ),
    }


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

    b, c = baseline_m, current_m
    lines = [
        "# Reviewer Benchmark: Before/After Comparison",
        "",
        "## Overall Metrics",
        "",
        "| Metric | Baseline | Current | Delta |",
        "|--------|----------|---------|-------|",
        (
            f"| Recall | {b['recall']:.1%}"
            f" | {c['recall']:.1%}"
            f" | {delta(c['recall'], b['recall'])} |"
        ),
        (
            f"| Precision | {b['precision']:.1%}"
            f" | {c['precision']:.1%}"
            f" | {delta(c['precision'], b['precision'])} |"
        ),
        (f"| F1 | {b['f1']:.1%} | {c['f1']:.1%} | {delta(c['f1'], b['f1'])} |"),
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

    recall_d = c["recall"] - b["recall"]
    precision_d = c["precision"] - b["precision"]
    f1_d = c["f1"] - b["f1"]

    recall_str = delta(c["recall"], b["recall"])
    prec_str = delta(c["precision"], b["precision"])
    f1_str = delta(c["f1"], b["f1"])

    recall_pass = "PASS" if recall_d >= 0.10 else "FAIL"
    prec_pass = "PASS" if precision_d >= -0.05 else "FAIL"
    f1_pass = "PASS" if f1_d >= 0.05 else "FAIL"

    lines.extend(
        [
            "",
            "## Success Criteria",
            "",
            f"- Recall +10pt: {recall_pass} ({recall_str})",
            f"- Precision -5pt max: {prec_pass} ({prec_str})",
            f"- F1 +5pt: {f1_pass} ({f1_str})",
        ]
    )
    return "\n".join(lines)


def format_variants_report(
    rloo: dict,
    grpo: dict,
) -> str:
    """K-variant ベンチマーク結果のマークダウンレポート。"""
    lines = [
        "# K-Variant Benchmark Report",
        "",
        "## RLOO Advantage",
        "",
        "| Variant | F1 | Advantage |",
        "|---------|-----|-----------|",
    ]
    for v in rloo["variants"]:
        lines.append(f"| V{v['index']} | {v['f1']:.1%} | {v['advantage']:+.4f} |")
    if rloo["best_variant"] is not None:
        lines.append(f"\nBest variant (RLOO): V{rloo['best_variant']}")

    lines.extend(
        [
            "",
            "## GRPO Advantage",
            "",
            "| Variant | F1 | Advantage |",
            "|---------|-----|-----------|",
        ]
    )
    for v in grpo["variants"]:
        lines.append(f"| V{v['index']} | {v['f1']:.1%} | {v['advantage']:+.4f} |")
    if grpo["best_variant"] is not None:
        lines.append(f"\nBest variant (GRPO): V{grpo['best_variant']}")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate benchmark results")
    parser.add_argument(
        "--single",
        help="Single result JSON for standalone report",
    )
    parser.add_argument(
        "--baseline",
        help="Baseline result JSON for comparison",
    )
    parser.add_argument(
        "--current",
        help="Current result JSON for comparison",
    )
    parser.add_argument(
        "--variants",
        nargs="+",
        help="K>=3 variant result JSONs for RLOO/GRPO analysis",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path (default: stdout)",
    )
    args = parser.parse_args()

    if args.variants:
        if len(args.variants) < 3:
            parser.error("--variants requires at least 3 files")
            return
        variant_results = []
        for vpath in args.variants:
            with open(vpath) as f:
                variant_results.append(json.load(f))
        rloo = compute_rloo_metrics(variant_results)
        grpo = compute_grpo_metrics(variant_results)
        report = format_variants_report(rloo, grpo)
    elif args.single:
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
        parser.error("Provide --single, --baseline+--current, or --variants")
        return

    if args.output:
        Path(args.output).write_text(report + "\n")
        print(f"Report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
