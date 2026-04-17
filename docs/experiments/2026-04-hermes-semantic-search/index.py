#!/usr/bin/env python3
"""Index existing JSONL traces into Qdrant (read-only experiment).

Reads ~/.claude/agent-memory/{learnings,traces,metrics} JSONL, computes Ollama
embeddings (nomic-embed-text), upserts into Qdrant 'hermes' collection.

Redaction is applied before embedding (A2 redactor integration).

Usage: python3 index.py [--limit N] [--batch N]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import requests  # type: ignore[import-untyped]

sys.path.insert(
    0, str(Path.home() / "dotfiles" / ".config" / "claude" / "scripts" / "lib")
)
from redactor import redact  # noqa: E402

OLLAMA_URL = "http://localhost:11434/api/embeddings"
QDRANT_URL = "http://localhost:6333"
COLLECTION = "hermes"
MODEL = "nomic-embed-text"
VECTOR_SIZE = 768  # nomic-embed-text dim


def embed(text: str) -> list[float]:
    r = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": text}, timeout=30)
    r.raise_for_status()
    return r.json()["embedding"]


def ensure_collection() -> None:
    r = requests.get(f"{QDRANT_URL}/collections/{COLLECTION}", timeout=5)
    if r.status_code == 200:
        return
    body = {"vectors": {"size": VECTOR_SIZE, "distance": "Cosine"}}
    r = requests.put(f"{QDRANT_URL}/collections/{COLLECTION}", json=body, timeout=10)
    r.raise_for_status()


def _parse_line(line: str) -> dict | None:
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None


def _process_file(
    p: Path, root: Path, out: list[tuple[str, str, dict]], limit: int
) -> bool:
    """Append entries from file p. Returns True when limit reached."""
    try:
        f = p.open(encoding="utf-8", errors="replace")
    except OSError:
        return False
    with f:
        for i, raw in enumerate(f, 1):
            obj = _parse_line(raw)
            if obj is None:
                continue
            text = redact(json.dumps(obj, ensure_ascii=False))[:8000]
            h = hashlib.sha256(f"{p}:{i}:{text}".encode()).hexdigest()[:32]
            payload = {
                "file": str(p.relative_to(Path.home())),
                "line": i,
                "category": root.name,
                "type_hint": obj.get("type") or obj.get("category", ""),
                "timestamp": obj.get("timestamp", ""),
            }
            out.append((h, text, payload))
            if limit and len(out) >= limit:
                return True
    return False


def iter_entries(limit: int) -> list[tuple[str, str, dict]]:
    """Collect (id, text, payload) for each JSONL line across target dirs."""
    roots = [
        Path.home() / ".claude/agent-memory/learnings",
        Path.home() / ".claude/agent-memory/traces",
        Path.home() / ".claude/agent-memory/metrics",
    ]
    out: list[tuple[str, str, dict]] = []
    for root in roots:
        if not root.exists():
            continue
        for p in sorted(root.rglob("*.jsonl")):
            if _process_file(p, root, out, limit):
                return out
    return out


def upsert_batch(points: list[dict]) -> None:
    r = requests.put(
        f"{QDRANT_URL}/collections/{COLLECTION}/points",
        json={"points": points},
        params={"wait": "true"},
        timeout=60,
    )
    r.raise_for_status()


def _id_int(h: str) -> int:
    # Qdrant accepts int or uuid. Use first 15 hex chars as int for stability.
    return int(h[:15], 16)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=2000, help="Max entries to index")
    ap.add_argument("--batch", type=int, default=32, help="Upsert batch size")
    args = ap.parse_args()

    print(f"[index] target: {args.limit} entries, batch={args.batch}")
    ensure_collection()

    entries = iter_entries(args.limit)
    print(f"[index] collected {len(entries)} entries")

    t0 = time.perf_counter()
    batch: list[dict] = []
    for n, (h, text, payload) in enumerate(entries, 1):
        try:
            vec = embed(text)
        except requests.RequestException as e:
            print(f"[index] embed failed for {h}: {e}", file=sys.stderr)
            continue
        batch.append({"id": _id_int(h), "vector": vec, "payload": payload})
        if len(batch) >= args.batch:
            upsert_batch(batch)
            batch = []
            elapsed = time.perf_counter() - t0
            rate = n / elapsed if elapsed else 0.0
            print(f"[index] {n}/{len(entries)} ({rate:.1f} entries/s)", flush=True)
    if batch:
        upsert_batch(batch)

    dur = time.perf_counter() - t0
    print(f"[index] done: {len(entries)} entries in {dur:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
