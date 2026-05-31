#!/usr/bin/env bash
# learned 昇格 pending の件数だけを通知する。レポート本体は作らない(死蔵防止)。
set -euo pipefail
LOG=/tmp/learned-nudge.log
CORE="$HOME/.claude/scripts/learner/extract-promotion-candidates.py"

if [[ ! -f "$CORE" ]]; then
  echo "[$(date -Iseconds)] core missing: $CORE" >> "$LOG"
  exit 0
fi

SUMMARY="$(python3 "$CORE" 2>>"$LOG" | python3 -c '
import json, sys
d = json.load(sys.stdin)
n = d["count"]
if n == 0:
    print("")  # 0件なら通知しない(ノイズ防止)
else:
    scopes = {}
    for c in d["candidates"][:50]:
        s = c.get("scope") or "?"
        scopes[s] = scopes.get(s, 0) + 1
    top = ", ".join(f"{k}({v})" for k, v in sorted(scopes.items(), key=lambda x: -x[1])[:3])
    print(f"learned 昇格 pending {n} 件。top scope: {top}。/promote-learnings で処理を。")
')"

if [[ -n "$SUMMARY" ]]; then
  echo "[$(date -Iseconds)] $SUMMARY" >> "$LOG"
  # macOS 通知(失敗は無視・best-effort)
  osascript -e "display notification \"$SUMMARY\" with title \"learned 昇格\"" 2>/dev/null || true
fi
exit 0
