#!/usr/bin/env python3
"""Submodular greedy selection for diverse subset extraction.

Uses Facility Location + lambda-weighted objective to select k items
that maximize coverage while penalizing redundancy.

Usage:
    python3 submodular_selection.py --candidates cands.jsonl --k 5
    python3 submodular_selection.py --candidates cands.jsonl --k 3 --lambda 0.5

Approximation guarantee: (1-1/e) ~ 0.63 for monotone submodular.
"""

from __future__ import annotations

import argparse
import json
import sys

# Re-use vectorizer and similarity from diversity_metrics
sys.path.insert(0, __import__("os").path.dirname(__file__))
from diversity_metrics import (  # noqa: E402
    similarity_matrix,
    tfidf_vectorize,
)


# -------------------------------------------------------------------
# Greedy Submodular Selection
# -------------------------------------------------------------------


def _marginal_coverage(
    sim_matrix: list[list[float]],
    idx: int,
    current_max: list[float],
) -> float:
    """Marginal coverage gain of adding idx to the selected set."""
    gain = 0.0
    for i, row in enumerate(sim_matrix):
        delta = row[idx] - current_max[i]
        if delta > 0:
            gain += delta
    return gain


def greedy_select(
    sim_matrix: list[list[float]],
    k: int,
    lam: float = 0.5,
) -> list[int]:
    """Select k items via greedy submodular maximization.

    Objective per step:
        gain(e|S) = coverage_gain(e|S) - lam * redundancy(e, S)

    Args:
        sim_matrix: n x n pairwise similarity matrix.
        k: Number of items to select.
        lam: Diversity weight. Higher = more diverse. Default 0.5.

    Returns:
        List of selected indices, ordered by selection step.
    """
    n = len(sim_matrix)
    k = min(k, n)
    if k <= 0:
        return []

    selected: list[int] = []
    in_selected = [False] * n
    current_max = [0.0] * n

    for _ in range(k):
        best_idx = -1
        best_gain = -float("inf")

        for idx in range(n):
            if in_selected[idx]:
                continue
            cov = _marginal_coverage(sim_matrix, idx, current_max)
            redundancy = sum(sim_matrix[idx][j] for j in selected)
            gain = cov - lam * redundancy
            if gain > best_gain:
                best_gain = gain
                best_idx = idx

        if best_idx == -1:
            break

        selected.append(best_idx)
        in_selected[best_idx] = True
        for i in range(n):
            current_max[i] = max(
                current_max[i],
                sim_matrix[i][best_idx],
            )

    return selected


# -------------------------------------------------------------------
# Duplicate Detection
# -------------------------------------------------------------------


def find_duplicates(
    sim_matrix: list[list[float]],
    threshold: float = 0.7,
) -> list[tuple[int, int, float]]:
    """Find pairs with cosine similarity above threshold.

    Returns list of (i, j, similarity) tuples.
    """
    n = len(sim_matrix)
    pairs: list[tuple[int, int, float]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if sim_matrix[i][j] > threshold:
                pairs.append((i, j, round(sim_matrix[i][j], 4)))
    return pairs


# -------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------


def _load_candidates(path: str, field: str) -> list[str]:
    """Load candidate texts from JSONL."""
    texts: list[str] = []
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                print(
                    f"Warning: skipping invalid JSON at line {line_num}",
                    file=sys.stderr,
                )
                continue
            text = obj.get(field) or obj.get("text") or obj.get("content") or ""
            if text:
                texts.append(text)
    return texts


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Submodular greedy selection for diversity",
    )
    parser.add_argument("--candidates", required=True, help="JSONL file")
    parser.add_argument("--k", type=int, default=3, help="Items to select")
    parser.add_argument(
        "--lambda",
        dest="lam",
        type=float,
        default=0.5,
        help="Diversity weight (default: 0.5)",
    )
    parser.add_argument("--field", default="text", help="JSON field")
    parser.add_argument(
        "--duplicates",
        action="store_true",
        help="Also report duplicate pairs (cosine > 0.7)",
    )
    parser.add_argument("--output", help="Output JSON file (default: stdout)")
    return parser


def _write_json(data: dict, path: str | None) -> None:
    output = json.dumps(data, indent=2, ensure_ascii=False)
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(output + "\n")
        print(f"Report written to {path}", file=sys.stderr)
    else:
        print(output)


def main() -> None:
    args = _build_parser().parse_args()

    texts = _load_candidates(args.candidates, args.field)
    if len(texts) < 2:
        print("Error: need at least 2 candidates", file=sys.stderr)
        sys.exit(1)

    vectors = tfidf_vectorize(texts)
    sim_mat = similarity_matrix(vectors)
    selected = greedy_select(sim_mat, args.k, args.lam)

    result: dict = {
        "k": args.k,
        "lambda": args.lam,
        "n_candidates": len(texts),
        "selected_indices": selected,
        "selected_texts": [texts[i] for i in selected],
    }
    if args.duplicates:
        dupes = find_duplicates(sim_mat)
        result["duplicates"] = [{"i": i, "j": j, "similarity": s} for i, j, s in dupes]

    _write_json(result, args.output)


if __name__ == "__main__":
    main()
