#!/usr/bin/env python3
"""aggregate.py — Aggregate benchmark results from eval runs.

Usage: python3 aggregate.py <iteration-dir> --skill-name <name>

Scans iteration-dir for eval-* subdirectories and aggregates grading.json
and timing.json data into benchmark.json and benchmark.md summaries.
"""

import argparse
import json
import statistics
import sys
from datetime import date
from pathlib import Path
from typing import Any


def warn(msg: str) -> None:
    """Print a warning message to stderr."""
    print(f"WARNING: {msg}", file=sys.stderr)


def load_json(path: Path) -> dict[str, Any] | None:
    """Load a JSON file, returning None if missing or invalid."""
    if not path.exists():
        warn(f"File not found: {path}")
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        warn(f"Failed to read {path}: {e}")
        return None


def compute_pass_rate(assertion_results: list[dict]) -> float:
    """Compute pass rate from assertion results (0.0 - 1.0)."""
    if not assertion_results:
        return 0.0
    passed = sum(1 for r in assertion_results if r.get("passed", False))
    return passed / len(assertion_results)


def collect_eval_data(
    eval_dir: Path,
) -> dict[str, dict[str, Any]] | None:
    """Collect grading and timing data for a single eval directory.

    Returns a dict with 'with_skill' and 'without_skill' entries,
    or None if essential data is missing.
    """
    grading = load_json(eval_dir / "grading.json")
    if grading is None:
        warn(f"Skipping {eval_dir.name}: no grading.json")
        return None

    result: dict[str, dict[str, Any]] = {}
    for config_name in ("with_skill", "without_skill"):
        config_grading = grading.get(config_name)
        if config_grading is None:
            warn(f"Skipping {eval_dir.name}/{config_name}: missing in grading.json")
            return None

        timing = load_json(eval_dir / config_name / "timing.json")
        duration_ms = timing.get("duration_ms", 0) if timing else 0

        assertion_results = config_grading.get("assertion_results", [])
        pass_rate = compute_pass_rate(assertion_results)
        quality_score = config_grading.get("quality_score", 0)

        # Checklist pass rate (optional, backwards-compatible)
        checklist_pass_rate = config_grading.get("checklist_pass_rate")

        entry: dict[str, Any] = {
            "eval_dir": eval_dir.name,
            "pass_rate": round(pass_rate, 4),
            "quality_score": quality_score,
            "duration_ms": duration_ms,
        }
        if checklist_pass_rate is not None:
            entry["checklist_pass_rate"] = round(checklist_pass_rate, 4)

        # Tool-use metrics — Reward Hacking 対策で Precision of Tool Use を併用
        # Source: mizchi/empirical-prompt-tuning, arXiv:2403.03023
        tool_uses = config_grading.get("tool_uses") or {}
        if isinstance(tool_uses, dict):
            total_count = tool_uses.get("total_count")
            precision = tool_uses.get("precision")
            if isinstance(total_count, int):
                entry["tool_count"] = total_count
            if isinstance(precision, (int, float)):
                entry["tool_precision"] = round(float(precision), 4)

        # Qualitative signals — ambiguity/retry/failure_reason
        # Schema: references/qualitative-signals-spec.md
        # Only populate fields if qualitative_signals is explicitly present
        # (backwards-compatible with legacy grading.json).
        signals = config_grading.get("qualitative_signals")
        if isinstance(signals, dict):
            amb = signals.get("ambiguity") or []
            retry = signals.get("retry") or []
            entry["ambiguity_count"] = len(amb) if isinstance(amb, list) else 0
            entry["retry_count"] = len(retry) if isinstance(retry, list) else 0
            fr = signals.get("failure_reason") or {}
            if isinstance(fr, dict):
                entry["failure_category"] = fr.get("category", "none")

        # Evaluator drift — record grader model version if present
        evaluator_version = config_grading.get("evaluator_model_version")
        if evaluator_version:
            entry["evaluator_model_version"] = evaluator_version

        result[config_name] = entry

    return result


def compute_stddev(values: list[float]) -> float:
    """Compute population standard deviation, returning 0.0 for < 2 values."""
    if len(values) < 2:
        return 0.0
    return statistics.stdev(values)


def aggregate_configuration(
    config_name: str, evals: list[dict[str, Any]]
) -> dict[str, Any]:
    """Aggregate eval data for a single configuration."""
    pass_rates = [e["pass_rate"] for e in evals]
    quality_scores = [e["quality_score"] for e in evals]
    durations = [e["duration_ms"] for e in evals]

    result: dict[str, Any] = {
        "name": config_name,
        "eval_count": len(evals),
        "pass_rate": round(statistics.mean(pass_rates), 4) if pass_rates else 0.0,
        "pass_rate_stddev": round(compute_stddev(pass_rates), 4),
        "mean_quality_score": round(statistics.mean(quality_scores), 2)
        if quality_scores
        else 0.0,
        "mean_duration_ms": round(statistics.mean(durations)) if durations else 0,
        "evals": evals,
    }

    # Aggregate checklist pass rates if any evals have them
    checklist_rates = [
        e["checklist_pass_rate"] for e in evals if "checklist_pass_rate" in e
    ]
    if checklist_rates:
        result["checklist_pass_rate"] = round(statistics.mean(checklist_rates), 4)
        result["checklist_pass_rate_stddev"] = round(compute_stddev(checklist_rates), 4)

    return result


def determine_recommendation(
    with_skill_quality: float, without_skill_quality: float
) -> tuple[str, str]:
    """Determine recommendation based on quality score delta.

    Returns (recommendation, reason) tuple.
    """
    delta = with_skill_quality - without_skill_quality

    if delta < -0.5:
        return (
            "retire",
            f"Skill degrades quality (delta: {delta:+.2f}). "
            "Consider removing or reworking the skill.",
        )
    elif delta > 0.5:
        return (
            "keep",
            f"Skill improves quality (delta: {delta:+.2f}). "
            "The skill is providing measurable value.",
        )
    else:
        return (
            "monitor",
            f"Marginal difference (delta: {delta:+.2f}). "
            "Continue monitoring with more evals before deciding.",
        )


def generate_markdown(benchmark: dict[str, Any]) -> str:
    """Generate a markdown summary from the benchmark data."""
    lines: list[str] = []
    lines.append(f"# Benchmark: {benchmark['skill']}")
    lines.append("")
    lines.append(f"- **Date**: {benchmark['date']}")
    lines.append(f"- **Iteration**: {benchmark['iteration']}")
    lines.append(f"- **Recommendation**: {benchmark['recommendation'].upper()}")
    lines.append(f"- **Reason**: {benchmark['recommendation_reason']}")
    lines.append("")

    # Summary table
    lines.append("## Summary")
    lines.append("")

    # Detect if any config has checklist data
    has_checklist = any("checklist_pass_rate" in c for c in benchmark["configurations"])

    if has_checklist:
        lines.append(
            "| Configuration | Evals | Pass Rate | Checklist | "
            "Quality Score | Duration (ms) |"
        )
        lines.append("|---|---|---|---|---|---|")
    else:
        lines.append(
            "| Configuration | Evals | Pass Rate | Quality Score | Duration (ms) |"
        )
        lines.append("|---|---|---|---|---|")

    for config in benchmark["configurations"]:
        stddev_str = (
            f" ({config['pass_rate_stddev']:.2%} sd)"
            if config["pass_rate_stddev"] > 0
            else ""
        )
        if has_checklist:
            cl_rate = config.get("checklist_pass_rate")
            cl_str = f"{cl_rate:.1%}" if cl_rate is not None else "N/A"
            lines.append(
                f"| {config['name']} "
                f"| {config['eval_count']} "
                f"| {config['pass_rate']:.1%}{stddev_str} "
                f"| {cl_str} "
                f"| {config['mean_quality_score']:.1f} "
                f"| {config['mean_duration_ms']} |"
            )
        else:
            lines.append(
                f"| {config['name']} "
                f"| {config['eval_count']} "
                f"| {config['pass_rate']:.1%}{stddev_str} "
                f"| {config['mean_quality_score']:.1f} "
                f"| {config['mean_duration_ms']} |"
            )

    lines.append("")

    # Per-eval details
    lines.append("## Per-Eval Details")
    lines.append("")

    with_evals = next(
        (c for c in benchmark["configurations"] if c["name"] == "with_skill"),
        None,
    )
    without_evals = next(
        (c for c in benchmark["configurations"] if c["name"] == "without_skill"),
        None,
    )

    if with_evals and without_evals:
        lines.append(
            "| Eval | With Skill (Quality) | Without Skill (Quality) "
            "| Delta | With Skill (ms) | Without Skill (ms) |"
        )
        lines.append("|---|---|---|---|---|---|")

        with_map = {e["eval_dir"]: e for e in with_evals["evals"]}
        without_map = {e["eval_dir"]: e for e in without_evals["evals"]}

        for eval_dir_name in with_map:
            w = with_map[eval_dir_name]
            wo = without_map.get(eval_dir_name)
            if wo is None:
                continue
            delta = w["quality_score"] - wo["quality_score"]
            delta_str = f"{delta:+d}"
            lines.append(
                f"| {eval_dir_name} "
                f"| {w['quality_score']} "
                f"| {wo['quality_score']} "
                f"| {delta_str} "
                f"| {w['duration_ms']} "
                f"| {wo['duration_ms']} |"
            )

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggregate eval benchmark results into a summary."
    )
    parser.add_argument(
        "iteration_dir",
        help="Path to the iteration directory containing eval-* subdirs.",
    )
    parser.add_argument(
        "--skill-name",
        required=True,
        help="Name of the skill being benchmarked.",
    )
    args = parser.parse_args()

    iter_dir = Path(args.iteration_dir)
    if not iter_dir.is_dir():
        print(f"ERROR: Directory not found: {iter_dir}", file=sys.stderr)
        sys.exit(1)

    # Discover eval-* subdirectories
    eval_dirs = sorted(
        [d for d in iter_dir.iterdir() if d.is_dir() and d.name.startswith("eval-")]
    )

    if not eval_dirs:
        print(f"ERROR: No eval-* directories found in {iter_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"=== Aggregating {len(eval_dirs)} evals for skill: {args.skill_name} ===")
    print(f"  Iteration dir: {iter_dir}")
    print()

    # Collect data from each eval
    with_skill_evals: list[dict[str, Any]] = []
    without_skill_evals: list[dict[str, Any]] = []
    skipped = 0

    for eval_dir in eval_dirs:
        data = collect_eval_data(eval_dir)
        if data is None:
            skipped += 1
            continue
        with_skill_evals.append(data["with_skill"])
        without_skill_evals.append(data["without_skill"])
        print(f"  [OK] {eval_dir.name}")

    if not with_skill_evals:
        print("ERROR: No valid eval data found.", file=sys.stderr)
        sys.exit(1)

    if skipped > 0:
        print(f"\n  Skipped {skipped} eval(s) due to missing data.")

    # Aggregate per configuration
    with_config = aggregate_configuration("with_skill", with_skill_evals)
    without_config = aggregate_configuration("without_skill", without_skill_evals)

    # Determine recommendation
    recommendation, reason = determine_recommendation(
        with_config["mean_quality_score"],
        without_config["mean_quality_score"],
    )

    # Extract iteration name from directory
    iteration_name = iter_dir.name

    # Build benchmark.json
    benchmark: dict[str, Any] = {
        "skill": args.skill_name,
        "date": date.today().isoformat(),
        "iteration": iteration_name,
        "configurations": [with_config, without_config],
        "recommendation": recommendation,
        "recommendation_reason": reason,
    }

    # Write benchmark.json
    benchmark_json_path = iter_dir / "benchmark.json"
    with open(benchmark_json_path, "w") as f:
        json.dump(benchmark, f, indent=2, ensure_ascii=False)
    print(f"\n  Wrote: {benchmark_json_path}")

    # Write benchmark.md
    markdown = generate_markdown(benchmark)
    benchmark_md_path = iter_dir / "benchmark.md"
    with open(benchmark_md_path, "w") as f:
        f.write(markdown)
    print(f"  Wrote: {benchmark_md_path}")

    # Print summary
    print()
    print("=== Result ===")
    print(
        f"  With Skill:    quality={with_config['mean_quality_score']:.1f}, "
        f"pass_rate={with_config['pass_rate']:.1%}"
    )
    print(
        f"  Without Skill: quality={without_config['mean_quality_score']:.1f}, "
        f"pass_rate={without_config['pass_rate']:.1%}"
    )
    delta = with_config["mean_quality_score"] - without_config["mean_quality_score"]
    print(f"  Delta:         {delta:+.2f}")
    print(f"  Recommendation: {recommendation.upper()} — {reason}")


if __name__ == "__main__":
    main()
