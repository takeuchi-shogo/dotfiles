#!/usr/bin/env bash
# learned 昇格 pending の件数だけを通知する。レポート本体は作らない(死蔵防止)。
set -euo pipefail
LOG=/tmp/learned-nudge.log
CORE="$HOME/.claude/scripts/learner/extract-promotion-candidates.py"

if [[ ! -f "$CORE" ]]; then
  # core 不在は best-effort 通知の範囲外(インフラ破損)。exit 1 で上位に知らせる。
  echo "[$(date -Iseconds)] core missing: $CORE" >> "$LOG"
  exit 1
fi

# core の出力を明示捕捉し、失敗を握り潰さない(空 stdin で下流 json.load がクラッシュするのを防ぐ)。
if ! RAW="$(python3 "$CORE" 2>>"$LOG")"; then
  echo "[$(date -Iseconds)] core failed: extract-promotion-candidates.py" >> "$LOG"
  exit 1
fi

SUMMARY="$(printf '%s' "$RAW" | python3 -c '
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
  # macOS 通知(失敗は無視・best-effort)。$SUMMARY は argv 経由で AppleScript の
  # 文字列値として渡し、構文層への注入(detail/scope のモデル生成テキスト由来)を防ぐ。
  osascript - "$SUMMARY" <<'APPLESCRIPT' 2>/dev/null || true
on run argv
  display notification (item 1 of argv) with title "learned 昇格"
end run
APPLESCRIPT
fi
exit 0
