#!/usr/bin/env bash
# 週次 skill 使用レポート (catch-up: 月-水 まで実行可、その日のレポートあれば skip)

set -euo pipefail

LOG=/tmp/skill-usage-weekly.log
INBOX="$HOME/Documents/Obsidian Vault/Inbox"
TODAY="$(date +%Y%m%d)"
DOW="$(date +%u)"  # 1=Mon, 7=Sun
REPORT="$INBOX/skill-usage-weekly-${TODAY}.md"

# Idempotent: その日のレポートあれば skip (LaunchAgent 多重発火対策)
[ -f "$REPORT" ] && exit 0

# Catch-up window: Mon-Wed のみ。月曜スリープで飛んでも火水で拾う
[ "$DOW" -gt 3 ] && exit 0

# 今週のレポートが既にあれば skip (火水 catch-up が月曜と重複しないように)
if find "$INBOX" -name 'skill-usage-weekly-*.md' -mtime -7 2>/dev/null | grep -q .; then
  echo "[$(date -Iseconds)] this week's report exists, skip" >> "$LOG"
  exit 0
fi

mkdir -p "$INBOX" 2>/dev/null || { echo "[$(date -Iseconds)] mkdir Inbox failed, skip" >> "$LOG"; exit 0; }

{
  echo "# Skill Usage Weekly Report"
  echo
  echo "Generated: $(date -Iseconds)"
  echo "Window: last 30 days"
  echo
  python3 <<'PY'
import json, time
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

CUTOFF = time.time() - 30 * 86400
log_path = Path.home() / '.claude/agent-memory/learnings/skill-executions.jsonl'
counter = Counter()
if log_path.exists():
    with log_path.open() as f:
        for line in f:
            try:
                d = json.loads(line)
                ts = d.get('timestamp')
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts.replace('Z', '+00:00')).timestamp()
                if ts and ts >= CUTOFF:
                    n = d.get('skill_name') or d.get('skill', '')
                    if n: counter[n] += 1
            except (json.JSONDecodeError, ValueError):
                pass

skills_dir = Path.home() / '.claude/skills'
all_skills = sorted([p.name for p in skills_dir.iterdir() if p.is_dir()])
unused = [s for s in all_skills if counter.get(s, 0) == 0]

print('## Summary')
print()
print(f'- Total skills: {len(all_skills)}')
print(f'- Used (≥1 call in 30d): {len(all_skills) - len(unused)}')
print(f'- Unused: {len(unused)}')
print()
print('## Unused skills (retire candidates)')
print()
for s in unused:
    print(f'- [ ] {s}')
print()
print('## Top 10 by usage')
print()
print('| skill | calls |')
print('|---|---|')
for s, n in counter.most_common(10):
    print(f'| {s} | {n} |')
PY
} > "$REPORT" 2>>"$LOG"

echo "[$(date -Iseconds)] weekly report -> $REPORT (DOW=$DOW)" >> "$LOG"
