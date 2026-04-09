#!/usr/bin/env python3
"""Diversity metrics for text collections — stdlib-only TF-IDF + cosine similarity.

Usage:
    python3 diversity_metrics.py --input texts.jsonl [--output report.json]

Input JSONL: each line {"text": "..."} or {"content": "..."}
Output: JSON report with similarity matrix and diversity metrics.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from typing import Callable

# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------


def tokenize(text: str) -> list[str]:
    """Unicode-aware word tokenizer. Optimized for English.

    CJK text is tokenized at character boundaries (no morphological analysis).
    For meaningful Japanese similarity, consider a morphological tokenizer.
    """
    return re.findall(r"\w+", text.lower())


# ---------------------------------------------------------------------------
# TF-IDF Vectorizer (stdlib-only)
# ---------------------------------------------------------------------------

SparseVector = dict[str, float]
Vectorizer = Callable[[list[str]], list[SparseVector]]


def tfidf_vectorize(texts: list[str]) -> list[SparseVector]:
    """Compute TF-IDF sparse vectors from raw texts."""
    tokenized = [tokenize(t) for t in texts]
    n = len(tokenized)
    if n == 0:
        return []

    # Document frequency
    df: Counter[str] = Counter()
    for doc in tokenized:
        df.update(set(doc))

    vectors: list[SparseVector] = []
    for doc in tokenized:
        if not doc:
            vectors.append({})
            continue
        tf = Counter(doc)
        total = len(doc)
        vector: SparseVector = {}
        for term, count in tf.items():
            tf_val = count / total
            idf_val = math.log(n / (df[term] + 1)) + 1  # smoothed IDF
            vector[term] = tf_val * idf_val
        vectors.append(vector)
    return vectors


# ---------------------------------------------------------------------------
# Cosine Similarity
# ---------------------------------------------------------------------------


def cosine_similarity(v1: SparseVector, v2: SparseVector) -> float:
    """Cosine similarity between two sparse vectors."""
    common = set(v1) & set(v2)
    if not common:
        return 0.0
    dot = sum(v1[k] * v2[k] for k in common)
    norm1 = math.sqrt(sum(v * v for v in v1.values()))
    norm2 = math.sqrt(sum(v * v for v in v2.values()))
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return min(1.0, dot / (norm1 * norm2))


def similarity_matrix(vectors: list[SparseVector]) -> list[list[float]]:
    """Compute pairwise cosine similarity matrix. O(n^2)."""
    n = len(vectors)
    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        matrix[i][i] = 1.0
        for j in range(i + 1, n):
            sim = cosine_similarity(vectors[i], vectors[j])
            matrix[i][j] = sim
            matrix[j][i] = sim
    return matrix


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def compute_metrics(matrix: list[list[float]]) -> dict:
    """Compute diversity metrics from a similarity matrix."""
    n = len(matrix)
    if n < 2:
        return {
            "n_items": n,
            "n_pairs": 0,
            "avg_pairwise_similarity": 0.0,
            "max_similarity": 0.0,
            "min_similarity": 0.0,
            "coverage_score": 1.0,
        }

    pairs: list[float] = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append(matrix[i][j])

    avg = sum(pairs) / len(pairs)
    return {
        "n_items": n,
        "n_pairs": len(pairs),
        "avg_pairwise_similarity": round(avg, 4),
        "max_similarity": round(max(pairs), 4),
        "min_similarity": round(min(pairs), 4),
        "coverage_score": round(1.0 - avg, 4),
    }


# ---------------------------------------------------------------------------
# High-level API
# ---------------------------------------------------------------------------


def analyze_texts(
    texts: list[str],
    vectorize: Vectorizer = tfidf_vectorize,
) -> dict:
    """Run full diversity analysis on a list of texts.

    Returns dict with 'metrics', 'similarity_matrix', and 'high_similarity_pairs'.
    """
    vectors = vectorize(texts)
    matrix = similarity_matrix(vectors)
    metrics = compute_metrics(matrix)

    # Flag high-similarity pairs (cosine > 0.7)
    high_pairs: list[dict] = []
    n = len(matrix)
    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i][j] > 0.7:
                high_pairs.append(
                    {
                        "i": i,
                        "j": j,
                        "similarity": round(matrix[i][j], 4),
                    }
                )

    return {
        "metrics": metrics,
        "similarity_matrix": [[round(v, 4) for v in row] for row in matrix],
        "high_similarity_pairs": high_pairs,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _load_jsonl(path: str, field: str) -> list[str]:
    """Load texts from JSONL file."""
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Diversity metrics for text collections"
    )
    parser.add_argument("--input", required=True, help="Path to JSONL file")
    parser.add_argument("--output", help="Path to output JSON file (default: stdout)")
    parser.add_argument(
        "--field", default="text", help="JSON field name for text (default: text)"
    )
    args = parser.parse_args()

    texts = _load_jsonl(args.input, args.field)
    if not texts:
        print("Error: no texts found in input file", file=sys.stderr)
        sys.exit(1)

    result = analyze_texts(texts)

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output + "\n")
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
