#!/usr/bin/env python3
"""Cost-aware evolution gate (T5, Autogenesis).

Tracks cumulative API cost per AutoEvolve cycle in `cycle-cost.json`
and emits gate decisions when budget thresholds are crossed.

Gemini 指摘 "$1 問題に $10 API 費" 対策。autoresearch の Convergence-Aware
Budgeting と同系統の考え方を cost 軸に適用する。

Artifacts:
    ~/.claude/agent-memory/runs/YYYY-MM-DD/cycle-cost.json

Schema (per-entry list):
    {
      "cycle_id": "YYYY-MM-DD[-HHMM]",
      "model": "opus-4.7 | sonnet-4.6 | gpt-5.4 | gemini-2.x | ...",
      "input_tokens": int,
      "output_tokens": int,
      "cost_usd": float,
      "cumulative_usd": float,
      "timestamp": "ISO8601 UTC"
    }

Commands:
    init <run_dir>          — create empty cycle-cost.json with header
    add <run_dir> <json>    — append an entry from stdin JSON
    check <run_dir>         — evaluate against budget, return gate verdict
    status <run_dir>        — human-readable summary

Budget thresholds (adjustable via env):
    CYCLE_COST_WARN_USD   default 5.0
    CYCLE_COST_STOP_USD   default 10.0
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

WARN_USD = float(os.environ.get("CYCLE_COST_WARN_USD", "5.0"))
STOP_USD = float(os.environ.get("CYCLE_COST_STOP_USD", "10.0"))


def _cost_file(run_dir: Path) -> Path:
    return run_dir / "cycle-cost.json"


def _read_entries(run_dir: Path) -> list[dict]:
    path = _cost_file(run_dir)
    if not path.exists():
        return []
    try:
        with open(path) as f:
            data = json.load(f)
        return data.get("entries", []) if isinstance(data, dict) else []
    except (json.JSONDecodeError, OSError):
        return []


def _write_entries(run_dir: Path, entries: list[dict]) -> None:
    path = _cost_file(run_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    cycle_id = run_dir.name
    cumulative = entries[-1]["cumulative_usd"] if entries else 0.0
    payload = {
        "cycle_id": cycle_id,
        "cumulative_usd": round(cumulative, 4),
        "entry_count": len(entries),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "entries": entries,
    }
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def _verdict(cumulative: float) -> tuple[str, str]:
    """Return (verdict, message). verdict ∈ {ok, warn, stop}."""
    if cumulative >= STOP_USD:
        return (
            "stop",
            f"[cost-gate] STOP: cumulative ${cumulative:.2f} >= ${STOP_USD:.2f}. "
            f"AutoEvolve サイクルを停止します。ユーザー override なしに継続禁止。",
        )
    if cumulative >= WARN_USD:
        return (
            "warn",
            f"[cost-gate] WARN: cumulative ${cumulative:.2f} >= ${WARN_USD:.2f}. "
            f"コスト逆転リスク (Gemini 指摘) を確認してください。",
        )
    return ("ok", f"[cost-gate] OK: cumulative ${cumulative:.2f} < ${WARN_USD:.2f}")


def cmd_init(run_dir: Path) -> int:
    if _cost_file(run_dir).exists():
        print(f"cycle-cost.json already exists at {run_dir}", file=sys.stderr)
        return 0
    _write_entries(run_dir, [])
    print(f"Initialized {_cost_file(run_dir)}")
    return 0


def cmd_add(run_dir: Path, payload: dict) -> int:
    required = ("model", "input_tokens", "output_tokens", "cost_usd")
    missing = [k for k in required if k not in payload]
    if missing:
        print(f"Missing required fields: {missing}", file=sys.stderr)
        return 2

    entries = _read_entries(run_dir)
    prev_total = entries[-1]["cumulative_usd"] if entries else 0.0
    try:
        cost = float(payload["cost_usd"])
    except (TypeError, ValueError):
        print("cost_usd must be numeric", file=sys.stderr)
        return 2
    cumulative = round(prev_total + cost, 4)

    entry = {
        "cycle_id": run_dir.name,
        "model": str(payload["model"]),
        "input_tokens": int(payload["input_tokens"]),
        "output_tokens": int(payload["output_tokens"]),
        "cost_usd": round(cost, 4),
        "cumulative_usd": cumulative,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    entries.append(entry)
    _write_entries(run_dir, entries)

    verdict, msg = _verdict(cumulative)
    print(
        json.dumps({"verdict": verdict, "cumulative_usd": cumulative, "message": msg})
    )
    return 1 if verdict == "stop" else 0


def cmd_check(run_dir: Path) -> int:
    entries = _read_entries(run_dir)
    cumulative = entries[-1]["cumulative_usd"] if entries else 0.0
    verdict, msg = _verdict(cumulative)
    print(
        json.dumps({"verdict": verdict, "cumulative_usd": cumulative, "message": msg})
    )
    return 1 if verdict == "stop" else 0


def cmd_status(run_dir: Path) -> int:
    entries = _read_entries(run_dir)
    if not entries:
        print(f"No cost entries in {run_dir}")
        return 0
    cumulative = entries[-1]["cumulative_usd"]
    print(f"Cycle: {run_dir.name}")
    print(f"Entries: {len(entries)}")
    print(f"Cumulative: ${cumulative:.4f} (warn ${WARN_USD} / stop ${STOP_USD})")
    verdict, msg = _verdict(cumulative)
    print(msg)
    # Per-model breakdown
    by_model: dict[str, float] = {}
    for e in entries:
        by_model[e["model"]] = by_model.get(e["model"], 0.0) + e["cost_usd"]
    print("By model:")
    for model, total in sorted(by_model.items(), key=lambda x: -x[1]):
        print(f"  {model}: ${total:.4f}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="AutoEvolve cost-aware gate")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("init", "check", "status"):
        p = sub.add_parser(name)
        p.add_argument("run_dir", type=Path)
    p_add = sub.add_parser("add")
    p_add.add_argument("run_dir", type=Path)
    p_add.add_argument("--json", help="Entry as JSON string (else stdin)")
    args = parser.parse_args()

    run_dir: Path = args.run_dir

    if args.cmd == "init":
        return cmd_init(run_dir)
    if args.cmd == "check":
        return cmd_check(run_dir)
    if args.cmd == "status":
        return cmd_status(run_dir)
    if args.cmd == "add":
        raw = args.json if args.json else sys.stdin.read()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}", file=sys.stderr)
            return 2
        return cmd_add(run_dir, payload)
    return 2


if __name__ == "__main__":
    sys.exit(main())
