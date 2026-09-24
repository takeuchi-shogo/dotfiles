#!/usr/bin/env python3
"""emit_benchmark.py — Emit benchmark results to AutoEvolve learnings.

Usage: python3 emit_benchmark.py <benchmark.json>

Reads a benchmark.json (output of aggregate.py) and appends structured
learning entries to skill-benchmarks.jsonl for AutoEvolve tracking.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def find_config(configurations: list[dict], name: str) -> dict:
    """Find a configuration by name, returning empty dict if not found."""
    for config in configurations:
        if config.get("name") == name:
            return config
    return {}


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 emit_benchmark.py <benchmark.json>", file=sys.stderr)
        sys.exit(1)

    benchmark_path = Path(sys.argv[1])
    if not benchmark_path.exists():
        print(f"ERROR: File not found: {benchmark_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(benchmark_path) as f:
            benchmark = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"ERROR: Failed to read {benchmark_path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Import append_to_learnings from shared library
    sys.path.insert(0, str(Path.home() / ".claude" / "scripts" / "lib"))
    from session_events import append_to_learnings

    # Extract data from benchmark.json
    skill_name = benchmark.get("skill", "unknown")
    recommendation = benchmark.get("recommendation", "monitor")
    recommendation_reason = benchmark.get("recommendation_reason", "")
    configurations = benchmark.get("configurations", [])

    with_skill = find_config(configurations, "with_skill")
    without_skill = find_config(configurations, "without_skill")

    quality_with = with_skill.get("mean_quality_score", 0.0)
    quality_baseline = without_skill.get("mean_quality_score", 0.0)
    delta = round(quality_with - quality_baseline, 2)

    # T4 (Autogenesis): task_category + model_tier for ceiling detection
    # Read from benchmark.json if present, else use safe defaults.
    task_category = benchmark.get("task_category", "generation")
    if task_category not in ("retrieval", "generation", "gate"):
        task_category = "generation"
    model_tier = benchmark.get("model_tier", "strong")
    if model_tier not in ("weak", "strong"):
        model_tier = "strong"

    learning_entry = {
        "type": "skill_benchmark",
        "skill": skill_name,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "recommendation": recommendation,
        "recommendation_reason": recommendation_reason,
        "quality_with_skill": quality_with,
        "quality_baseline": quality_baseline,
        "delta": delta,
        "pass_rate_with_skill": with_skill.get("pass_rate", 0.0),
        "pass_rate_baseline": without_skill.get("pass_rate", 0.0),
        "task_category": task_category,
        "model_tier": model_tier,
    }

    append_to_learnings("skill-benchmarks", learning_entry)

    print(
        f"Emitted benchmark for '{skill_name}': "
        f"recommendation={recommendation}, delta={delta:+.2f}"
    )


if __name__ == "__main__":
    main()
