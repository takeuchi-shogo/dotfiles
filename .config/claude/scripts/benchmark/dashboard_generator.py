#!/usr/bin/env python3
"""Dashboard generator — render improve-history.jsonl as Markdown sparkline table.

Triggered by: /improve Phase 5 REPORT (manual invocation per SKILL.md).
Source:       yamadashy "Claude Code Routines" absorb (2026-04-29) — Task C.

Reads ~/.claude/agent-memory/metrics/improve-history.jsonl, picks the most
recent N entries (default 20), and writes a Markdown table with ASCII
sparklines for three metrics: adoption_rate, cycle_time_hours, eval_tuple_count.

Standard library only. Graceful degradation: if data is missing or partial,
exit 0 with a notice; never abort /improve REPORT.

Build to Delete: when AutoEvolve absorbs dashboard rendering natively, remove
both this script and the SKILL.md invocation line.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

JsonEntry = dict[str, object]
Numeric = float | int

SPARK_CHARS = "▁▂▃▄▅▆▇█"
DEFAULT_HISTORY = (
    Path.home() / ".claude" / "agent-memory" / "metrics" / "improve-history.jsonl"
)
DEFAULT_OUTPUT = Path.home() / ".claude" / "agent-memory" / "runs" / "_dashboard.md"
DEFAULT_WINDOW = 20
TRACKED_METRICS = ("adoption_rate", "cycle_time_hours", "eval_tuple_count")
NO_DATA_NOTICE = (
    "> **データなし**: improve-history.jsonl が未作成 or 空。"
    "/improve を最低 1 回実行してください。"
)
BUILD_TO_DELETE_NOTE = (
    "> Build to Delete: dashboard_generator.py は過渡的スクリプト。"
    "AutoEvolve が dashboard を内包したら削除する。"
)


def _read_jsonl_tail(path: Path, window: int) -> list[JsonEntry]:
    if not path.exists():
        return []
    entries: list[JsonEntry] = []
    with path.open(encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries[-window:]


def _coerce_numeric(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _spark_for(values: list[float | None]) -> str:
    numeric = [v for v in values if v is not None]
    if not numeric:
        return "(no data)"
    if len(numeric) == 1:
        return SPARK_CHARS[len(SPARK_CHARS) // 2]
    lo, hi = min(numeric), max(numeric)
    span = hi - lo
    chars: list[str] = []
    for v in values:
        if v is None:
            chars.append("·")
            continue
        if span == 0:
            idx = len(SPARK_CHARS) // 2
        else:
            idx = int(round((v - lo) / span * (len(SPARK_CHARS) - 1)))
            idx = max(0, min(idx, len(SPARK_CHARS) - 1))
        chars.append(SPARK_CHARS[idx])
    return "".join(chars)


def _summary_for(values: list[float | None]) -> dict[str, object]:
    numeric = [v for v in values if v is not None]
    total = len(values)
    if not numeric:
        return {"min": None, "max": None, "latest": None, "present": 0, "total": total}
    return {
        "min": min(numeric),
        "max": max(numeric),
        "latest": numeric[-1],
        "present": len(numeric),
        "total": total,
    }


def _format_value(v: object) -> str:
    if v is None:
        return "—"
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, float):
        return f"{v:.3g}"
    return str(v)


def _extract_dates(entries: list[JsonEntry]) -> list[str]:
    return [str(e.get("date") or e.get("timestamp") or "?") for e in entries]


def _extract_metric_series(entries: list[JsonEntry], metric: str) -> list[float | None]:
    return [_coerce_numeric(e.get(metric)) for e in entries]


def _render_header(
    entries: list[JsonEntry], history_path: Path, window: int
) -> list[str]:
    lines = [
        "# /improve Dashboard",
        "",
        f"- source: `{history_path}`",
        f"- window: latest {len(entries)} of requested {window}",
    ]
    if entries:
        dates = _extract_dates(entries)
        lines.append(f"- range: {dates[0]} → {dates[-1]}")
    return lines


def _render_metrics_table(entries: list[JsonEntry]) -> list[str]:
    lines = [
        "## Metrics",
        "",
        "| metric | sparkline | latest | min | max | data |",
        "|---|---|---|---|---|---|",
    ]
    for metric in TRACKED_METRICS:
        values = _extract_metric_series(entries, metric)
        spark = _spark_for(values)
        summary = _summary_for(values)
        lines.append(
            "| `{m}` | `{s}` | {lt} | {lo} | {hi} | {p}/{t} |".format(
                m=metric,
                s=spark,
                lt=_format_value(summary["latest"]),
                lo=_format_value(summary["min"]),
                hi=_format_value(summary["max"]),
                p=summary["present"],
                t=summary["total"],
            )
        )
    return lines


def _render_recent_entries(entries: list[JsonEntry]) -> list[str]:
    dates = _extract_dates(entries)
    lines = [
        "## Recent entries",
        "",
        "| date | adoption_rate | cycle_time_hours | eval_tuple_count |",
        "|---|---|---|---|",
    ]
    for entry, date_str in zip(entries[-10:], dates[-10:]):
        lines.append(
            "| {d} | {a} | {c} | {t} |".format(
                d=date_str,
                a=_format_value(entry.get("adoption_rate")),
                c=_format_value(entry.get("cycle_time_hours")),
                t=_format_value(entry.get("eval_tuple_count")),
            )
        )
    return lines


def _render_markdown(entries: list[JsonEntry], history_path: Path, window: int) -> str:
    sections: list[list[str]] = [_render_header(entries, history_path, window)]
    if not entries:
        sections.append(["", NO_DATA_NOTICE])
    else:
        sections.append([""] + _render_metrics_table(entries))
        sections.append([""] + _render_recent_entries(entries))
        sections.append(["", BUILD_TO_DELETE_NOTE])
    body = "\n".join(line for section in sections for line in section)
    return body + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--history",
        type=Path,
        default=DEFAULT_HISTORY,
        help="improve-history.jsonl path",
    )
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT, help="output Markdown path"
    )
    parser.add_argument(
        "--window",
        type=int,
        default=DEFAULT_WINDOW,
        help="how many tail entries to read",
    )
    args = parser.parse_args()

    try:
        entries = _read_jsonl_tail(args.history, args.window)
        markdown = _render_markdown(entries, args.history, args.window)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding="utf-8")
        print(
            f"dashboard_generator: wrote {args.output} ({len(entries)} entries)",
            file=sys.stderr,
        )
    except Exception as exc:  # graceful degradation — never break /improve REPORT
        print(
            f"dashboard_generator: failed ({exc.__class__.__name__}: {exc})",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
