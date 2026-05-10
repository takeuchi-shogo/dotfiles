#!/usr/bin/env bash
# Skill pruning evaluation reminder (Track A 8 件 + Track B 5 件)
# Plan: docs/plans/2026-05-08-skill-pruning-evaluation-plan.md
# Catch-up window: 2026-06-07 〜 2026-06-13 (PC スリープ対策)
# Done marker で重複実行を防止

set -euo pipefail

WINDOW_START=20260607
WINDOW_END=20260613
STATE_DIR="$HOME/.claude/state/skill-health"
DONE_MARKER="$STATE_DIR/skill-pruning-eval.done"
LOG=/tmp/skill-pruning-eval.log
INBOX="$HOME/Documents/Obsidian Vault/00-Inbox"
TODAY="$(date +%Y%m%d)"

[ -f "$DONE_MARKER" ] && exit 0
[ "$TODAY" -lt "$WINDOW_START" ] && exit 0

mkdir -p "$STATE_DIR"

if [ "$TODAY" -gt "$WINDOW_END" ]; then
  if [ -d "$INBOX" ]; then
    cat > "$INBOX/skill-pruning-eval-MISSED-${TODAY}.md" <<EOF
# Skill Pruning Evaluation: MISSED

PC offline during window 2026-06-07 〜 2026-06-13.
Plan: docs/plans/2026-05-08-skill-pruning-evaluation-plan.md
手動で評価してください:

\`\`\`bash
bash $HOME/.claude/scripts/runtime/skill-pruning-eval-reminder.sh --force
\`\`\`
EOF
  fi
  touch "$DONE_MARKER"
  echo "[$(date -Iseconds)] window missed, marked done" >> "$LOG"
  exit 0
fi

mkdir -p "$INBOX" 2>/dev/null || { echo "[$(date -Iseconds)] mkdir Inbox failed, skip" >> "$LOG"; exit 0; }

REPORT="$INBOX/skill-pruning-eval-${TODAY}.md"

{
  echo "# Skill Pruning Evaluation (30-day)"
  echo
  echo "Generated: $(date -Iseconds)"
  echo "Plan: docs/plans/2026-05-08-skill-pruning-evaluation-plan.md"
  echo "Evaluation period: 2026-05-08 〜 2026-06-07"
  echo
  echo "## Track A — Dormant Skill Retire Decision"
  echo
  python3 <<'PY'
import json
from pathlib import Path
from collections import Counter
from datetime import datetime

CUTOFF = datetime.fromisoformat('2026-05-08').timestamp()
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

track_a = [
    'ai-workflow-audit', 'autocover', 'refactor-session', 'setup-background-agents',
    'recall', 'analyze-tacit-knowledge', 'prompt-review', 'developer-onboarding',
]
print('| skill | calls | recommendation |')
print('|---|---|---|')
for s in track_a:
    n = counter.get(s, 0)
    rec = 'RETIRE' if n == 0 else 'KEEP'
    print(f'| {s} | {n} | **{rec}** |')
PY
  echo
  echo "## Track B — Large Skill Split Progress (情報のみ、retire 対象外)"
  echo
  for skill in ast-grep-practice review playwright-test skill-audit; do
    p="$HOME/.claude/skills/$skill/SKILL.md"
    if [ -f "$p" ]; then
      lines=$(wc -l < "$p" | tr -d ' ')
      status="(< 500 ✓)"
      [ "$lines" -ge 500 ] && status="(>= 500, 分割未完)"
      echo "- $skill: $lines lines $status"
    fi
  done
  echo
  echo "## Action"
  echo
  echo "- RETIRE 候補は \`mv ~/.claude/skills/<name> ~/.claude/skills/_archived/\` で退避"
  echo "- KEEP は probation 解除、plan の Track A 行を削除"
  echo "- Track B 未完なら次サイクルで分割継続"
} > "$REPORT" 2>>"$LOG"

touch "$DONE_MARKER"
echo "[$(date -Iseconds)] skill-pruning-eval report -> $REPORT" >> "$LOG"

# Notify via cmux if available
NOTIFY="$(dirname "$0")/cmux-notify.sh"
[ -x "$NOTIFY" ] && "$NOTIFY" "Skill Pruning Eval" "30-day evaluation report ready" hero || true
