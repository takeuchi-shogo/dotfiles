#!/usr/bin/env python3
"""Split eval tuples into train/holdout sets using stratified sampling.

Stratification key: (failure_mode, language) pair — "behavioral tag".
Ensures each FM x language cell has representative tuples in both splits.

Usage:
    python3 split_holdout.py [--input reviewer-eval-tuples.json]
                             [--holdout-ratio 0.3]
                             [--seed 42]
                             [--output-dir .]
                             [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SplitConfig:
    """Parameters governing a train/holdout split."""

    source_name: str
    seed: int
    holdout_ratio: float


def load_tuples(input_path: Path) -> tuple[str, list[dict]]:
    """Load tuples from JSON; return (description, tuples)."""
    with input_path.open(encoding="utf-8") as f:
        data = json.load(f)
    description = data.get("description", "")
    return description, data.get("tuples", [])


def stratified_split(
    tuples: list[dict],
    holdout_ratio: float,
    seed: int,
) -> tuple[list[dict], list[dict]]:
    """Split tuples into train/holdout using stratified sampling.

    Stratification key: (failure_mode, language).
    - Groups with 1 tuple go entirely to train.
    - Groups with 2+ tuples: ceil(n * holdout_ratio) items go to holdout.
    """
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for t in tuples:
        key = (t.get("failure_mode", ""), t.get("language", ""))
        groups[key].append(t)

    train: list[dict] = []
    holdout: list[dict] = []

    rng = random.Random(seed)

    for key in sorted(groups.keys()):
        group = groups[key]
        if len(group) == 1:
            train.extend(group)
            continue
        shuffled = list(group)
        rng.shuffle(shuffled)
        n_holdout = math.ceil(len(shuffled) * holdout_ratio)
        holdout.extend(shuffled[:n_holdout])
        train.extend(shuffled[n_holdout:])

    return train, holdout


def build_stratification_table(
    tuples: list[dict],
    train: list[dict],
    holdout: list[dict],
) -> list[tuple[str, str, int, int, int]]:
    """Return rows: (fm, language, total, train_count, holdout_count)."""
    fm_lang_total: dict[tuple[str, str], int] = defaultdict(int)
    fm_lang_train: dict[tuple[str, str], int] = defaultdict(int)
    fm_lang_holdout: dict[tuple[str, str], int] = defaultdict(int)

    for t in tuples:
        key = (t.get("failure_mode", ""), t.get("language", ""))
        fm_lang_total[key] += 1
    for t in train:
        key = (t.get("failure_mode", ""), t.get("language", ""))
        fm_lang_train[key] += 1
    for t in holdout:
        key = (t.get("failure_mode", ""), t.get("language", ""))
        fm_lang_holdout[key] += 1

    rows = []
    for key in sorted(fm_lang_total.keys()):
        fm, lang = key
        rows.append(
            (fm, lang, fm_lang_total[key], fm_lang_train[key], fm_lang_holdout[key])
        )
    return rows


def print_stratification_table(
    rows: list[tuple[str, str, int, int, int]],
    total: int,
    n_train: int,
    n_holdout: int,
) -> None:
    """Print stratification table to stdout."""
    if not rows:
        print("\nStratification Table: (empty)")
        return
    fm_w = max(len("FM"), max(len(r[0]) for r in rows))
    lang_w = max(len("Language"), max(len(r[1]) for r in rows))

    header = (
        f"| {'FM':<{fm_w}} | {'Language':<{lang_w}} "
        f"| {'Total':>5} | {'Train':>5} | {'Holdout':>7} |"
    )
    sep = (
        f"| {'-' * fm_w} | {'-' * lang_w} "
        f"| {'-----':>5} | {'-----':>5} | {'-------':>7} |"
    )

    print("\nStratification Table:")
    print(header)
    print(sep)
    for fm, lang, tot, tr, ho in rows:
        print(f"| {fm:<{fm_w}} | {lang:<{lang_w}} | {tot:>5} | {tr:>5} | {ho:>7} |")
    print(f"\nSummary: {total} total → {n_train} train / {n_holdout} holdout")


def write_split(
    path: Path, split_name: str, tuples: list[dict], cfg: SplitConfig
) -> None:
    """Write a split JSON file with the standard schema."""
    data = {
        "description": (
            f"{split_name.capitalize()} split from {cfg.source_name} "
            f"(seed={cfg.seed}, holdout_ratio={cfg.holdout_ratio})"
        ),
        "source": cfg.source_name,
        "split": split_name,
        "tuples": tuples,
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _parse_args() -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Split eval tuples into train/holdout sets"
    )
    parser.add_argument(
        "--input",
        default=str(script_dir / "reviewer-eval-tuples.json"),
        help="Path to tuples JSON (default: reviewer-eval-tuples.json next to script)",
    )
    parser.add_argument(
        "--holdout-ratio",
        type=float,
        default=0.3,
        help="Fraction of tuples per stratum to allocate to holdout (default: 0.3)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for output files (default: same as input file)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show split statistics without writing files",
    )
    args = parser.parse_args()
    if not (0.0 < args.holdout_ratio < 1.0):
        parser.error("--holdout-ratio must be between 0.0 and 1.0 (exclusive)")
    return args


def _run(args: argparse.Namespace) -> None:
    input_path = Path(args.input).resolve()
    output_dir = (
        Path(args.output_dir).resolve() if args.output_dir else input_path.parent
    )

    _, tuples = load_tuples(input_path)
    source_name = input_path.name
    print(f"Loaded {len(tuples)} tuples from {source_name}")

    train, holdout = stratified_split(tuples, args.holdout_ratio, args.seed)
    cfg = SplitConfig(
        source_name=source_name,
        seed=args.seed,
        holdout_ratio=args.holdout_ratio,
    )

    # Retreat condition: insufficient holdout data
    if len(holdout) < 5:
        print(
            f"WARNING: holdout set has only {len(holdout)} tuples (< 5). "
            "Insufficient data for holdout evaluation — no files written."
        )
        return

    rows = build_stratification_table(tuples, train, holdout)
    print_stratification_table(rows, len(tuples), len(train), len(holdout))

    if args.dry_run:
        print("\n[dry-run] No files written.")
        return

    train_path = output_dir / "reviewer-eval-train.json"
    holdout_path = output_dir / "reviewer-eval-holdout.json"

    output_dir.mkdir(parents=True, exist_ok=True)
    write_split(train_path, "train", train, cfg)
    write_split(holdout_path, "holdout", holdout, cfg)

    print(f"Train:   {train_path}")
    print(f"Holdout: {holdout_path}")


def main() -> None:
    _run(_parse_args())


if __name__ == "__main__":
    main()
