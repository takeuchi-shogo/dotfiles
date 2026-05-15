#!/usr/bin/env bash
# Weekly friction-events digest (manual execution; no LaunchAgent).
#
# Reads ~/.claude/agent-memory/learnings/friction-events.jsonl, aggregates the
# last 7 days, and writes a human-readable markdown digest to Obsidian Inbox.
#
# Design notes:
# - Visualization only. No autofix, no skill mutation. (/improve retired 2026-05-03)
# - Style mirrors skill-usage-weekly.sh (Inbox output, idempotent).
# - Manual trigger: run from terminal. Not cron'd because:
#   1) macOS LaunchAgent skips StartCalendarInterval during sleep (would need
#      catch-up window like skill-usage-weekly).
#   2) Event volume is currently too low (7 events) to justify automation.
#   3) If volume grows, copy com.claude.daily-health-check.plist as template.

set -euo pipefail

LOG=/tmp/friction-weekly-digest.log
INBOX="$HOME/Documents/Obsidian Vault/00-Inbox"
TODAY="$(date +%Y%m%d)"
REPORT="$INBOX/friction-weekly-${TODAY}.md"
SOURCE="$HOME/.claude/agent-memory/learnings/friction-events.jsonl"

# Idempotent: same-day report exists -> skip
if [ -f "$REPORT" ]; then
  echo "[$(date -Iseconds)] same-day report exists, skip" >> "$LOG"
  exit 0
fi

# Source missing -> log + exit (not an error)
if [ ! -f "$SOURCE" ]; then
  echo "[$(date -Iseconds)] source missing: $SOURCE" >> "$LOG"
  exit 0
fi

mkdir -p "$INBOX" 2>/dev/null || { echo "[$(date -Iseconds)] mkdir Inbox failed" >> "$LOG"; exit 1; }

{
  echo "# Friction Weekly Digest"
  echo
  echo "Generated: $(date -Iseconds)"
  echo "Source: \`~/.claude/agent-memory/learnings/friction-events.jsonl\`"
  echo "Window: last 7 days"
  echo
  python3 - <<'PY'
import json
import time
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone

CUTOFF_DAYS = 7
NOW = time.time()
CUTOFF = NOW - CUTOFF_DAYS * 86400

source = Path.home() / ".claude/agent-memory/learnings/friction-events.jsonl"

events_in_window = []
parse_errors = 0
total_lines = 0
with source.open() as f:
    for line in f:
        total_lines += 1
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            parse_errors += 1
            continue
        ts = d.get("timestamp")
        if isinstance(ts, str):
            try:
                ts_epoch = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
            except ValueError:
                parse_errors += 1
                continue
        else:
            continue
        if ts_epoch >= CUTOFF:
            events_in_window.append(d)

# Summary
print("## Summary")
print()
print(f"- Total events (file): {total_lines}")
print(f"- Events in last {CUTOFF_DAYS}d: {len(events_in_window)}")
print(f"- Parse errors: {parse_errors}")
print()

if not events_in_window:
    print("_No friction events recorded in the last 7 days._")
    print()
    print("## Notes")
    print()
    print("- Zero events can mean (a) genuinely smooth week, or (b) hooks not")
    print("  firing. Spot-check `webfetch-truncation-detector.py` etc. occasionally.")
    raise SystemExit(0)

# Breakdown by friction_class
class_counter = Counter(e.get("friction_class", "unknown") for e in events_in_window)
severity_counter = Counter(e.get("severity", "unknown") for e in events_in_window)

print("## By severity")
print()
print("| severity | count |")
print("|---|---|")
for sev, n in severity_counter.most_common():
    print(f"| {sev} | {n} |")
print()

print("## By friction_class (top 10)")
print()
print("| class | count |")
print("|---|---|")
for cls, n in class_counter.most_common(10):
    print(f"| {cls} | {n} |")
print()

# Sample evidence per top class (max 5 classes, max 2 samples each)
samples_by_class = defaultdict(list)
for e in events_in_window:
    cls = e.get("friction_class", "unknown")
    if len(samples_by_class[cls]) < 2:
        samples_by_class[cls].append(e)

print("## Sample evidence (top 5 classes)")
print()
for cls, _ in class_counter.most_common(5):
    print(f"### {cls}")
    print()
    for sample in samples_by_class[cls]:
        ts = sample.get("timestamp", "?")
        sev = sample.get("severity", "?")
        evidence = sample.get("evidence", {})
        evidence_str = json.dumps(evidence, ensure_ascii=False, sort_keys=True)
        if len(evidence_str) > 240:
            evidence_str = evidence_str[:237] + "..."
        print(f"- `{ts}` [{sev}] {evidence_str}")
    print()

# Watch list: any class with >= 3 warnings
watch = [
    (cls, n)
    for cls, n in class_counter.items()
    if sum(
        1
        for e in events_in_window
        if e.get("friction_class") == cls and e.get("severity") == "warning"
    )
    >= 3
]
print("## Watch list (>=3 warnings in window)")
print()
if not watch:
    print("_None._")
else:
    for cls, n in watch:
        print(f"- **{cls}** — {n} events")
print()

print("## Next steps")
print()
print("- Read the watch list above. If a class recurs week after week,")
print("  consider a hook fix or a skill update — but **do not auto-edit skills**.")
print("- This digest is a signal, not an action. Treat as journal, not pipeline.")
PY
} > "$REPORT" 2>>"$LOG"

echo "[$(date -Iseconds)] friction digest -> $REPORT" >> "$LOG"
echo "$REPORT"
