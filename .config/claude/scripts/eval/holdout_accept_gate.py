#!/usr/bin/env python3
"""Held-out strict accept gate for SkillOpt-style edits (arXiv:2605.23904).

Pure-logic verdict engine — no LLM calls. Takes baseline/candidate eval
result files (train + holdout splits) and decides whether a candidate
edit is accepted, using three guards in order:

1. Overfitting guard: train improved but holdout did not.
2. Strict holdout improvement: holdout pass_rate must strictly improve
   (ties are rejected — "strict" accept gate).
3. Metric diversity (Rule 23): a secondary metric must not regress on
   holdout, even when pass_rate improves.

Rejected edits are recorded (idempotently) in a JSONL buffer so the
caller can build momentum tracking of edits that keep failing the gate.

Usage:
    python3 holdout_accept_gate.py \\
        --baseline-train baseline-train.json \\
        --baseline-holdout baseline-holdout.json \\
        --candidate-train candidate-train.json \\
        --candidate-holdout candidate-holdout.json \\
        --secondary-metric finding_precision:higher \\
        --edit-id e123 --lane review-gate \\
        [--rejected-buffer PATH] [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


class GateInputError(Exception):
    """Invalid or malformed eval input — caller should exit with code 2."""


@dataclass
class SecondaryMetricSpec:
    """A secondary metric name plus the direction that counts as "better"."""

    name: str
    direction: str  # "higher" or "lower"


@dataclass
class EvalSplits:
    """The four eval-result splits driving one gate decision."""

    baseline_train: list[dict]
    baseline_holdout: list[dict]
    candidate_train: list[dict]
    candidate_holdout: list[dict]


@dataclass
class RejectionRecord:
    """One rejected-edit entry destined for the momentum buffer."""

    lane: str
    edit_id: str
    reason: str
    holdout_delta: float


def load_eval_file(path: Path) -> list[dict]:
    """Load an eval-result JSON file; return its `results` list."""
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise GateInputError(f"failed to load {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise GateInputError(
            f"{path}: top-level JSON must be an object, got {type(data).__name__}"
        )
    results = data.get("results", [])
    if not isinstance(results, list):
        raise GateInputError(
            f"{path}: 'results' must be a list, got {type(results).__name__}"
        )
    return results


def parse_secondary_metric_spec(spec: str) -> SecondaryMetricSpec:
    """Parse "NAME[:higher|:lower]" (default direction: higher)."""
    name, sep, direction = spec.partition(":")
    if not sep:
        return SecondaryMetricSpec(name=name, direction="higher")
    direction = direction.lower()
    if direction not in ("higher", "lower"):
        raise GateInputError(f"invalid direction in --secondary-metric: {spec!r}")
    return SecondaryMetricSpec(name=name, direction=direction)


def pass_rate(results: list[dict]) -> float:
    """Fraction of results with pass == True."""
    return sum(1 for r in results if r.get("pass")) / len(results)


def secondary_mean(results: list[dict], metric_name: str) -> float:
    """Average of metrics[metric_name] across results."""
    return sum(r["metrics"][metric_name] for r in results) / len(results)


def _check_nonempty(label: str, results: list[dict]) -> None:
    if not results:
        raise GateInputError(f"empty results: {label}")


def _check_records_well_formed(label: str, results: list[dict]) -> None:
    """Validate each record: dict shape, str `id`, bool `pass`, dict `metrics`."""
    for idx, r in enumerate(results):
        if not isinstance(r, dict):
            raise GateInputError(f"{label}: result[{idx}] is not an object: {r!r}")
        if not isinstance(r.get("id"), str):
            raise GateInputError(
                f"{label}: result[{idx}] has non-string 'id': {r.get('id')!r}"
            )
        if not isinstance(r.get("pass"), bool):
            raise GateInputError(
                f"{label}: case {r.get('id')!r} has non-bool 'pass': {r.get('pass')!r}"
            )
        if "metrics" in r and not isinstance(r["metrics"], dict):
            raise GateInputError(
                f"{label}: case {r.get('id')!r} has non-dict 'metrics': "
                f"{r['metrics']!r}"
            )


def _check_id_sets(label: str, baseline: list[dict], candidate: list[dict]) -> None:
    """Compare id *multisets* — a duplicated id on one side must not slip through."""
    baseline_counts = Counter(r.get("id") for r in baseline)
    candidate_counts = Counter(r.get("id") for r in candidate)
    if baseline_counts == candidate_counts:
        return
    all_ids = sorted(
        baseline_counts.keys() | candidate_counts.keys(), key=lambda i: str(i)
    )
    mismatches = [
        f"{i!r}(baseline={baseline_counts[i]}, candidate={candidate_counts[i]})"
        for i in all_ids
        if baseline_counts[i] != candidate_counts[i]
    ]
    raise GateInputError(
        f"{label}: baseline/candidate id multisets differ: {mismatches}"
    )


def _check_metric_present(label: str, results: list[dict], metric_name: str) -> None:
    for r in results:
        metrics = r.get("metrics") or {}
        if metric_name not in metrics:
            raise GateInputError(
                f"{label}: case {r.get('id')!r} missing metric {metric_name!r}"
            )
        value = metrics[metric_name]
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise GateInputError(
                f"{label}: case {r.get('id')!r} metric {metric_name!r} "
                f"is not a finite number: {value!r}"
            )


def evaluate_gate(
    splits: EvalSplits,
    secondary_metric: SecondaryMetricSpec,
    edit_id: str,
    lane: str,
) -> dict:
    """Run the held-out strict accept gate and return the verdict dict.

    Raises GateInputError for malformed input (empty results, mismatched
    id sets, missing secondary metric) — these are Fail Fast boundary
    errors, not accept/reject decisions.
    """
    baseline_train = splits.baseline_train
    baseline_holdout = splits.baseline_holdout
    candidate_train = splits.candidate_train
    candidate_holdout = splits.candidate_holdout

    labeled = (
        ("baseline-train", baseline_train),
        ("baseline-holdout", baseline_holdout),
        ("candidate-train", candidate_train),
        ("candidate-holdout", candidate_holdout),
    )
    for label, results in labeled:
        _check_nonempty(label, results)
    for label, results in labeled:
        _check_records_well_formed(label, results)

    _check_id_sets("train", baseline_train, candidate_train)
    _check_id_sets("holdout", baseline_holdout, candidate_holdout)

    for label, results in labeled:
        _check_metric_present(label, results, secondary_metric.name)

    baseline_train_pr = pass_rate(baseline_train)
    baseline_holdout_pr = pass_rate(baseline_holdout)
    candidate_train_pr = pass_rate(candidate_train)
    candidate_holdout_pr = pass_rate(candidate_holdout)

    train_delta = candidate_train_pr - baseline_train_pr
    holdout_delta = candidate_holdout_pr - baseline_holdout_pr

    baseline_secondary = secondary_mean(baseline_holdout, secondary_metric.name)
    candidate_secondary = secondary_mean(candidate_holdout, secondary_metric.name)
    secondary_delta = candidate_secondary - baseline_secondary

    deltas = {
        "train_pass_rate": train_delta,
        "holdout_pass_rate": holdout_delta,
        "holdout_secondary": secondary_delta,
    }
    baseline_summary = {
        "train_pass_rate": baseline_train_pr,
        "holdout_pass_rate": baseline_holdout_pr,
    }
    candidate_summary = {
        "train_pass_rate": candidate_train_pr,
        "holdout_pass_rate": candidate_holdout_pr,
    }

    def _verdict(verdict: str, reason: str) -> dict:
        return {
            "verdict": verdict,
            "reason": reason,
            "edit_id": edit_id,
            "lane": lane,
            "deltas": deltas,
            "baseline": baseline_summary,
            "candidate": candidate_summary,
        }

    if train_delta > 0 and holdout_delta <= 0:
        return _verdict("reject", "overfitting: train improved but holdout did not")

    if holdout_delta <= 0:
        return _verdict(
            "reject", "holdout pass_rate did not strictly improve (tie rejected)"
        )

    if secondary_metric.direction == "higher":
        secondary_regressed = candidate_secondary < baseline_secondary
    else:
        secondary_regressed = candidate_secondary > baseline_secondary
    if secondary_regressed:
        return _verdict("reject", "secondary metric regressed")

    return _verdict(
        "accept",
        "holdout pass_rate improved without overfitting or secondary regression",
    )


def rejected_buffer_key(lane: str, edit_id: str) -> str:
    return hashlib.sha1(f"{lane}:{edit_id}".encode("utf-8")).hexdigest()


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    for lineno, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as exc:
            print(
                f"{path}:{lineno}: skipping malformed JSON line: {exc}",
                file=sys.stderr,
            )
            continue  # tolerant parse: 壊れた行はスキップ
    return out


def record_rejection(buffer_path: Path, rejection: RejectionRecord) -> bool:
    """Append a rejection record to the buffer JSONL, idempotent by key.

    Returns True if a new record was written, False if the key was
    already present (no duplicate append on re-run).
    """
    key = rejected_buffer_key(rejection.lane, rejection.edit_id)
    existing_keys = {e.get("key") for e in _read_jsonl(buffer_path)}
    if key in existing_keys:
        return False
    buffer_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "key": key,
        "lane": rejection.lane,
        "edit_id": rejection.edit_id,
        "reason": rejection.reason,
        "holdout_delta": rejection.holdout_delta,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    with buffer_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return True


def _parse_args() -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Held-out strict accept gate for SkillOpt-style edits"
    )
    parser.add_argument(
        "--baseline-train",
        required=True,
        help="Path to baseline eval-result JSON (train split)",
    )
    parser.add_argument(
        "--baseline-holdout",
        required=True,
        help="Path to baseline eval-result JSON (holdout split)",
    )
    parser.add_argument(
        "--candidate-train",
        required=True,
        help="Path to candidate eval-result JSON (train split)",
    )
    parser.add_argument(
        "--candidate-holdout",
        required=True,
        help="Path to candidate eval-result JSON (holdout split)",
    )
    parser.add_argument(
        "--secondary-metric",
        required=True,
        help="Metric name, optionally suffixed :higher or :lower (default: higher)",
    )
    parser.add_argument(
        "--edit-id", required=True, help="Identifier of the candidate edit"
    )
    parser.add_argument(
        "--lane",
        required=True,
        help="Lane name the edit belongs to (used in the rejection buffer key)",
    )
    parser.add_argument(
        "--rejected-buffer",
        default=str(script_dir / "results" / "rejected-edits.jsonl"),
        help="JSONL buffer for rejected edits (default: results/rejected-edits.jsonl)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write to the rejected-edit buffer",
    )
    return parser.parse_args()


def _run(args: argparse.Namespace) -> int:
    try:
        baseline_train = load_eval_file(Path(args.baseline_train))
        baseline_holdout = load_eval_file(Path(args.baseline_holdout))
        candidate_train = load_eval_file(Path(args.candidate_train))
        candidate_holdout = load_eval_file(Path(args.candidate_holdout))
        secondary_metric = parse_secondary_metric_spec(args.secondary_metric)

        splits = EvalSplits(
            baseline_train=baseline_train,
            baseline_holdout=baseline_holdout,
            candidate_train=candidate_train,
            candidate_holdout=candidate_holdout,
        )
        verdict = evaluate_gate(splits, secondary_metric, args.edit_id, args.lane)
    except GateInputError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2

    if verdict["verdict"] == "reject" and not args.dry_run:
        record_rejection(
            Path(args.rejected_buffer),
            RejectionRecord(
                lane=args.lane,
                edit_id=args.edit_id,
                reason=verdict["reason"],
                holdout_delta=verdict["deltas"]["holdout_pass_rate"],
            ),
        )

    print(json.dumps(verdict, ensure_ascii=False, indent=2))
    return 0 if verdict["verdict"] == "accept" else 1


def main() -> int:
    return _run(_parse_args())


if __name__ == "__main__":
    sys.exit(main())
