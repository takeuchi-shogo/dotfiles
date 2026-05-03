#!/usr/bin/env bash
# Probation 6 skill の 30 日後使用統計 (2026-06-02 限定 one-shot)
# Probation 開始: 2026-05-03 (commit 8775fd8)
# 評価日: 2026-06-02

set -euo pipefail

TARGET_DATE="20260602"
TODAY="$(date +%Y%m%d)"

[ "$TODAY" != "$TARGET_DATE" ] && exit 0

LOG=/tmp/probation-30day.log
INBOX="$HOME/Documents/Obsidian Vault/Inbox"
REPORT="$INBOX/probation-30day-${TODAY}.md"

{
  echo "# Probation 30-day Re-evaluation"
  echo
  echo "Generated: $(date -Iseconds)"
  echo "Probation start: 2026-05-03"
  echo
  echo "## Usage Counts"
  echo
  python3 <<'PY'
import json
from pathlib import Path
from collections import Counter
from datetime import datetime

CUTOFF = datetime.fromisoformat('2026-05-03').timestamp()
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

probation = ['autonomous', 'graphql-expert', 'buf-protobuf', 'prompt-review', 'difit', 'refactor-session']
print('| skill | calls | recommendation |')
print('|---|---|---|')
for s in probation:
    n = counter.get(s, 0)
    rec = 'RETIRE' if n == 0 else 'KEEP'
    print(f'| {s} | {n} | **{rec}** |')
PY
  echo
  echo "## Action"
  echo
  echo "- RETIRE 候補は \`rm -rf ~/.claude/skills/<name>\` で削除し dotfiles で commit"
  echo "- KEEP は probation 解除"
} > "$REPORT" 2>>"$LOG"

echo "[$(date -Iseconds)] probation report -> $REPORT" >> "$LOG"
