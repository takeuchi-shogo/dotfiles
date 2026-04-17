#!/usr/bin/env python3
"""Evaluate recall@5 + latency against 10 handcrafted queries.

Loads queries.json, embeds each query, searches Qdrant (k=5), measures latency.

Recall is judged by: does at least one top-5 hit contain keywords from the
expected_hint? (manual-reviewable, since we don't have ground-truth labels).

Usage: python3 eval.py
Outputs: eval-results.json + prints summary; populate report.md manually.
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

import requests  # type: ignore[import-untyped]

OLLAMA_URL = "http://localhost:11434/api/embeddings"
QDRANT_URL = "http://localhost:6333"
COLLECTION = "hermes"
MODEL = "nomic-embed-text"
K = 5


def embed(text: str) -> list[float]:
    r = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": text}, timeout=30)
    r.raise_for_status()
    return r.json()["embedding"]


def search(vector: list[float], k: int = K) -> list[dict]:
    r = requests.post(
        f"{QDRANT_URL}/collections/{COLLECTION}/points/search",
        json={"vector": vector, "limit": k, "with_payload": True},
        timeout=10,
    )
    r.raise_for_status()
    return r.json().get("result", [])


def judge(hits: list[dict], hint: str) -> bool:
    """Heuristic: any hit payload (file/category) contains a hint keyword."""
    keywords = [w for w in hint.lower().split() if len(w) > 3]
    if not keywords:
        return False
    for hit in hits:
        payload = hit.get("payload", {})
        hay = (
            f"{payload.get('file', '')} {payload.get('category', '')} "
            f"{payload.get('type_hint', '')}"
        ).lower()
        if any(k in hay for k in keywords):
            return True
    return False


def main() -> int:
    qpath = Path(__file__).parent / "queries" / "queries.json"
    queries = json.loads(qpath.read_text(encoding="utf-8"))

    results = []
    latencies_ms: list[float] = []
    hits_count = 0

    for q in queries:
        t0 = time.perf_counter()
        vec = embed(q["query"])
        hits = search(vec, k=K)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        latencies_ms.append(elapsed_ms)

        ok = judge(hits, q.get("expected_hint", ""))
        if ok:
            hits_count += 1

        results.append(
            {
                "id": q["id"],
                "query": q["query"],
                "latency_ms": round(elapsed_ms, 1),
                "match": ok,
                "top_files": [h.get("payload", {}).get("file", "") for h in hits[:5]],
            }
        )
        print(f"[{q['id']}] {elapsed_ms:.0f}ms match={ok} — {q['query'][:60]}")

    recall_at_5 = hits_count / len(queries) if queries else 0.0
    p50 = statistics.median(latencies_ms) if latencies_ms else 0.0
    p95 = (
        statistics.quantiles(latencies_ms, n=20)[18]
        if len(latencies_ms) >= 20
        else max(latencies_ms, default=0.0)
    )

    summary = {
        "queries": len(queries),
        "recall_at_5": round(recall_at_5, 2),
        "latency_p50_ms": round(p50, 1),
        "latency_p95_ms": round(p95, 1),
        "results": results,
    }

    out = Path(__file__).parent / "eval-results.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== Summary ===")
    print(f"Recall@5: {recall_at_5:.2f}")
    print(f"Latency  p50: {p50:.1f}ms / p95: {p95:.1f}ms")
    print(f"Results written to {out}")

    # Retreat check
    if recall_at_5 < 0.5:
        print("RETREAT: recall@5 < 0.5")
    if p50 > 500:
        print("RETREAT: latency p50 > 500ms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
