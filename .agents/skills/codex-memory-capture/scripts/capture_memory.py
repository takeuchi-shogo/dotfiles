#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def load_entries(path: Path) -> list[dict]:
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def key_for(entry: dict) -> tuple[str, str, str]:
    return (
        entry.get("category", "").strip().lower(),
        entry.get("pattern", "").strip(),
        entry.get("action", "").strip(),
    )


def write_summary(entries: list[dict], summary_path: Path) -> None:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for entry in entries[-30:]:
        grouped[entry["category"]].append(entry)

    lines = ["# Dotfiles Codex Memory", ""]
    for category in sorted(grouped):
        lines.append(f"## {category}")
        for entry in grouped[category][-10:]:
            lines.append(f"- Pattern: {entry['pattern']}")
            lines.append(f"  Action: {entry['action']}")
            if entry.get("evidence"):
                lines.append(f"  Evidence: {entry['evidence']}")
        lines.append("")

    summary_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", required=True)
    parser.add_argument("--pattern", required=True)
    parser.add_argument("--action", required=True)
    parser.add_argument("--evidence", default="")
    parser.add_argument("--memory-dir", default=os.path.expanduser("~/.codex/memories"))
    args = parser.parse_args()

    memory_dir = Path(args.memory_dir)
    memory_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = memory_dir / "dotfiles-learnings.jsonl"
    summary_path = memory_dir / "dotfiles-memory.md"

    entries = load_entries(jsonl_path)
    new_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "category": args.category.strip().lower(),
        "pattern": args.pattern.strip(),
        "action": args.action.strip(),
        "evidence": args.evidence.strip(),
    }

    existing_keys = {key_for(entry) for entry in entries}
    if key_for(new_entry) not in existing_keys:
        with jsonl_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(new_entry, ensure_ascii=False) + "\n")
        entries.append(new_entry)

    write_summary(entries, summary_path)
    print(summary_path)
    print(jsonl_path)


if __name__ == "__main__":
    main()
