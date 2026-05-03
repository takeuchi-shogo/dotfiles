#!/usr/bin/env bash
# 毎週月曜: 過去 30 日で使用 0 回の skill を Inbox に投函

set -euo pipefail

LOG=/tmp/skill-usage-weekly.log
INBOX="$HOME/Documents/Obsidian Vault/Inbox"
TODAY="$(date +%Y%m%d)"
REPORT="$INBOX/skill-usage-weekly-${TODAY}.md"

[ -d "$INBOX" ] || { echo "[$(date -Iseconds)] Inbox not found, skip" >> "$LOG"; exit 0; }

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

print(f'## Summary')
print()
print(f'- Total skills: {len(all_skills)}')
print(f'- Used (≥1 call in 30d): {len(all_skills) - len(unused)}')
print(f'- Unused: {len(unused)}')
print()
print(f'## Unused skills (retire candidates)')
print()
for s in unused:
    print(f'- [ ] {s}')
print()
print(f'## Top 10 by usage')
print()
print('| skill | calls |')
print('|---|---|')
for s, n in counter.most_common(10):
    print(f'| {s} | {n} |')
PY
} > "$REPORT" 2>>"$LOG"

echo "[$(date -Iseconds)] weekly report -> $REPORT" >> "$LOG"
