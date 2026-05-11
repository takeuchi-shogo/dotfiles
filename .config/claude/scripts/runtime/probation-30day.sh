#!/usr/bin/env bash
# Probation 6 skill の 30 日後使用統計
# Catch-up window: 2026-06-02 〜 2026-06-08 (PC スリープ対策)
# Done marker で重複実行を防止

set -euo pipefail

WINDOW_START=20260602
WINDOW_END=20260608
STATE_DIR="$HOME/.claude/state/skill-health"
DONE_MARKER="$STATE_DIR/probation-30day.done"
LOG=/tmp/probation-30day.log
INBOX="$HOME/Documents/Obsidian Vault/00-Inbox"
TODAY="$(date +%Y%m%d)"

[ -f "$DONE_MARKER" ] && exit 0
[ "$TODAY" -lt "$WINDOW_START" ] && exit 0

mkdir -p "$STATE_DIR"

if [ "$TODAY" -gt "$WINDOW_END" ]; then
  # Window 過ぎても未実行 → 警告だけ Inbox に出して mark
  if [ -d "$INBOX" ]; then
    cat > "$INBOX/probation-30day-MISSED-${TODAY}.md" <<EOF
# Probation 30-day Re-evaluation: MISSED

PC offline during window 2026-06-02 〜 2026-06-08.
手動で評価してください: \`/skill-audit\` または

\`\`\`bash
bash $HOME/.claude/scripts/runtime/probation-30day.sh --force
\`\`\`
EOF
  fi
  touch "$DONE_MARKER"
  echo "[$(date -Iseconds)] window missed, marked done" >> "$LOG"
  exit 0
fi

mkdir -p "$INBOX" 2>/dev/null || { echo "[$(date -Iseconds)] mkdir Inbox failed, skip" >> "$LOG"; exit 0; }

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

touch "$DONE_MARKER"
echo "[$(date -Iseconds)] probation report -> $REPORT" >> "$LOG"
