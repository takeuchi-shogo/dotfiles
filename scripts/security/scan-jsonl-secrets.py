#!/usr/bin/env python3
"""JSONL secret scanner.

Read-only audit of JSONL files for plaintext secrets.
Patterns are ported from tools/otel-session-analyzer/internal/redactor/redactor.go
plus plan-specified additions (sk-*, ghp_*).

Usage:
    scan-jsonl-secrets.py [--root DIR ...] [--output FILE] [--json]

The module exposes PATTERNS so A2 (lib/redactor.py) can reuse the same list.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator


@dataclass(frozen=True)
class Pattern:
    name: str
    severity: str  # high | medium | low
    regex: re.Pattern[str]


PATTERNS: list[Pattern] = [
    Pattern(
        "private_key_block",
        "high",
        re.compile(r"-----BEGIN [A-Z ]+ KEY-----"),
    ),
    Pattern(
        "aws_access_key",
        "high",
        re.compile(r"AKIA[0-9A-Z]{16}"),
    ),
    Pattern(
        "github_pat",
        "high",
        re.compile(r"ghp_[A-Za-z0-9]{36}"),
    ),
    Pattern(
        "sk_token",
        "medium",
        re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),
    ),
    Pattern(
        "bearer_token",
        "medium",
        re.compile(r"(?i)Bearer\s+[a-zA-Z0-9_\-.]{10,}"),
    ),
    Pattern(
        "api_key_assignment",
        "medium",
        re.compile(r"(?i)(api[_-]?key|token|secret)[=:]\s*['\"]?[a-zA-Z0-9_\-]{20,}"),
    ),
    Pattern(
        "password_assignment",
        "low",
        re.compile(r"(?i)(password|passwd|pwd)[=:]\s*['\"]?\S{8,}"),
    ),
]


MASK = "***"


def mask_match(text: str, start: int, end: int) -> str:
    """Return context snippet with the matched value replaced by MASK."""
    ctx_start = max(0, start - 40)
    ctx_end = min(len(text), end + 40)
    masked = text[ctx_start:start] + MASK + text[end:ctx_end]
    return masked.replace("\n", "\\n").replace("\t", " ")


@dataclass
class Hit:
    file: str
    line_no: int
    pattern: str
    severity: str
    snippet: str


def scan_line(line: str) -> Iterator[tuple[Pattern, re.Match[str]]]:
    for pat in PATTERNS:
        for m in pat.regex.finditer(line):
            yield pat, m


def iter_jsonl_files(roots: Iterable[Path]) -> Iterator[Path]:
    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            if root.suffix == ".jsonl":
                yield root
            continue
        for p in root.rglob("*.jsonl"):
            yield p


def scan_file(path: Path) -> tuple[list[Hit], int, int]:
    """Return (hits, lines_scanned, bytes_scanned)."""
    hits: list[Hit] = []
    lines_scanned = 0
    bytes_scanned = 0
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, start=1):
                lines_scanned += 1
                bytes_scanned += len(line)
                for pat, m in scan_line(line):
                    hits.append(
                        Hit(
                            file=str(path),
                            line_no=i,
                            pattern=pat.name,
                            severity=pat.severity,
                            snippet=mask_match(line, m.start(), m.end()),
                        )
                    )
    except OSError as e:
        print(f"warn: cannot read {path}: {e}", file=sys.stderr)
    return hits, lines_scanned, bytes_scanned


def default_roots() -> list[Path]:
    home = Path(os.path.expanduser("~"))
    return [
        home / ".claude/projects",
        home / ".claude/session-state",
        home / ".claude/skill-data",
        home / ".claude/agent-memory",
        Path("/Users/takeuchishougo/dotfiles/.claude/tacit-knowledge"),
    ]


def build_report(
    all_hits: list[Hit],
    files_scanned: int,
    lines_scanned: int,
    bytes_scanned: int,
) -> dict:
    by_pattern: Counter[str] = Counter()
    by_severity: Counter[str] = Counter()
    by_file: Counter[str] = Counter()
    for h in all_hits:
        by_pattern[h.pattern] += 1
        by_severity[h.severity] += 1
        by_file[h.file] += 1
    top_files = by_file.most_common(10)
    samples_by_pattern: dict[str, list[dict]] = defaultdict(list)
    for h in all_hits:
        samples = samples_by_pattern[h.pattern]
        if len(samples) < 3:
            samples.append(
                {
                    "file": h.file,
                    "line": h.line_no,
                    "severity": h.severity,
                    "snippet": h.snippet,
                }
            )
    return {
        "summary": {
            "files_scanned": files_scanned,
            "lines_scanned": lines_scanned,
            "bytes_scanned": bytes_scanned,
            "total_hits": len(all_hits),
            "by_severity": dict(by_severity),
            "by_pattern": dict(by_pattern),
        },
        "top_files": [{"file": f, "hits": n} for f, n in top_files],
        "samples_by_pattern": dict(samples_by_pattern),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit JSONL files for plaintext secrets.")
    ap.add_argument(
        "--root",
        action="append",
        default=None,
        help="Directory to scan (repeatable). Default: common ~/.claude paths.",
    )
    ap.add_argument("--output", help="Write JSON report to this path.")
    ap.add_argument("--json", action="store_true", help="Print JSON report to stdout.")
    ap.add_argument(
        "--limit", type=int, default=0, help="Limit number of files scanned (debug)."
    )
    args = ap.parse_args()

    roots = [Path(r).expanduser() for r in args.root] if args.root else default_roots()

    files_scanned = 0
    lines_scanned = 0
    bytes_scanned = 0
    all_hits: list[Hit] = []

    for path in iter_jsonl_files(roots):
        if args.limit and files_scanned >= args.limit:
            break
        hits, lines, size = scan_file(path)
        files_scanned += 1
        lines_scanned += lines
        bytes_scanned += size
        all_hits.extend(hits)

    report = build_report(all_hits, files_scanned, lines_scanned, bytes_scanned)

    if args.output:
        Path(args.output).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    if args.json or not args.output:
        json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
