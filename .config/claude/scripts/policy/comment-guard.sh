#!/usr/bin/env bash
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

# comment-guard.sh — Edit/Write/MultiEdit で新規コードコメントが純増したら deny する PreToolUse hook。
#
# 目的: 低価値コメント (作業経過・自明・意図) の乱造を予防する。コメントはデフォルト禁止とし、
#       書くなら「そうしないと何が起きるか (ハザード・制約)」の Tier 1 だけを意識的 override で書く。
#       経緯・意図は git commit message に置く。設計: docs/plans/2026-06-06-comment-guard-hook-design.md
#
# 設計上の必然 (鈍いまま): hook は Tier を判定しない。pragma 以外のコメント純増を一律 deny する。
#                          Tier 判定を hook に持ち込むと determinism boundary を壊すため。
# fail-open: 判定不能・対象外・スクリプト自体のエラーはすべて exit 0 (=allow)。
# 無効化: COMMENT_GUARD=off (セッションキルスイッチ) または marker touch (30 分有効) で override。
#
# Adapted from MH4GF/claude-code user-scope/hooks/comment-guard.sh (MIT License, Copyright (c) 2026 MH4GF).
# 変更点: rust (.rs) を c-family に追加 / deny メッセージを Tier 哲学に差し替え / marker 運用を dotfiles 向けに記述。

input=$(cat)

[[ "${COMMENT_GUARD:-}" == "off" ]] && exit 0

tool_name=$(jq -r '.tool_name // empty' <<<"$input" 2>/dev/null) || exit 0
case "$tool_name" in
  Edit|Write|MultiEdit) ;;
  *) exit 0 ;;
esac

file_path=$(jq -r '.tool_input.file_path // empty' <<<"$input" 2>/dev/null) || exit 0
[ -n "$file_path" ] || exit 0

ext=$(printf '%s' "$file_path" | tr '[:upper:]' '[:lower:]')
ext="${ext##*.}"
case "$ext" in
  ts|tsx|js|jsx|mjs|cjs|go|rs) family=c ;;
  json)                        family=json ;;
  yaml|yml|py)                 family=hash ;;
  sql)                         family=sql ;;
  *) exit 0 ;;
esac

case "$family" in
  hash) awk_fam=hash ;;
  sql)  awk_fam=sql ;;
  *)    awk_fam=c ;;
esac

count_comments() {
  printf '%s\n' "$1" | awk -v fam="$awk_fam" '
  {
    line = $0
    sub(/^[ \t]+/, "", line)
    if (fam == "hash") {
      if (line ~ /^#!/) next
      if (line ~ /#[ \t]*(noqa|type:|pylint:|pragma:|yamllint|nosec|fmt:|mypy:)/) next
      gsub(/"[^"]*"/, "", line)
      gsub(/\047[^\047]*\047/, "", line)
      if (line ~ /(^|[ \t])#/) c++
    } else if (fam == "sql") {
      if (line ~ /^#!/) next
      gsub(/"[^"]*"/, "", line)
      gsub(/\047[^\047]*\047/, "", line)
      gsub(/`[^`]*`/, "", line)
      if (line ~ /--/ || line ~ /\/\*/) c++
    } else {
      if (line ~ /^#!/) next
      if (line ~ /\/\/go:/) next
      if (line ~ /(\/\/|\/\*)[ \t]*(eslint-|@ts-|@flow|biome-ignore|prettier-ignore|oxlint-|deno-lint-|c8 ignore|v8 ignore|istanbul ignore|nolint)/) next
      gsub(/"[^"]*"/, "", line)
      gsub(/\047[^\047]*\047/, "", line)
      gsub(/`[^`]*`/, "", line)
      if (line ~ /\/\// || line ~ /\/\*/) c++
    }
  }
  END { print c+0 }
  ' 2>/dev/null
}

# 1 edit の (old,new) からコメント行数の増分を算出。
# マルチライン文字列ガードに該当したら判定をスキップし 0 を返す。
contribution() {
  local old=$1 new=$2 bt cold cnew
  if [ "$family" = c ]; then
    bt=$(printf '%s' "$new" | tr -cd '`' | wc -c | tr -d ' ')
    [ -n "$bt" ] && [ $((bt % 2)) -ne 0 ] && { echo 0; return; }
  elif [ "$family" = hash ]; then
    printf '%s\n' "$new" | grep -qE ':[[:space:]]*[|>][+-]?[0-9]?[[:space:]]*$' && { echo 0; return; }
  fi
  cold=$(count_comments "$old"); cold=${cold:-0}
  cnew=$(count_comments "$new"); cnew=${cnew:-0}
  echo $((cnew - cold))
}

total=0
case "$tool_name" in
  Edit)
    old=$(jq -r '.tool_input.old_string // ""' <<<"$input" 2>/dev/null)
    new=$(jq -r '.tool_input.new_string // ""' <<<"$input" 2>/dev/null)
    c=$(contribution "$old" "$new"); total=$((total + ${c:-0}))
    ;;
  Write)
    [ -f "$file_path" ] || exit 0
    old=$(cat "$file_path" 2>/dev/null) || exit 0
    new=$(jq -r '.tool_input.content // ""' <<<"$input" 2>/dev/null)
    c=$(contribution "$old" "$new"); total=$((total + ${c:-0}))
    ;;
  MultiEdit)
    n=$(jq '.tool_input.edits | length' <<<"$input" 2>/dev/null)
    [ -n "$n" ] || exit 0
    i=0
    while [ "$i" -lt "$n" ] 2>/dev/null; do
      old=$(jq -r ".tool_input.edits[$i].old_string // \"\"" <<<"$input" 2>/dev/null)
      new=$(jq -r ".tool_input.edits[$i].new_string // \"\"" <<<"$input" 2>/dev/null)
      c=$(contribution "$old" "$new"); total=$((total + ${c:-0}))
      i=$((i + 1))
    done
    ;;
esac

[ "${total:-0}" -gt 0 ] 2>/dev/null || exit 0

# deny 候補。marker (.claude/tmp/.comment-guard-allow) が 30 分以内に touch されていれば許可する。
# marker は私が Bash で明示 touch する or ユーザーが手動 touch する (tool call として可視・監査可能)。
cwd=$(jq -r '.cwd // empty' <<<"$input" 2>/dev/null)
if [ -n "$cwd" ]; then
  marker="$cwd/.claude/tmp/.comment-guard-allow"
  if [ -f "$marker" ] && [ -n "$(find "$marker" -mmin -30 2>/dev/null)" ]; then
    exit 0
  fi
fi

printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"新規コードコメントの追加はブロックされています。経緯・意図は git commit message に書いてください。コードに残すなら「そうしないと何が起きるか (ハザード・制約)」を書く Tier 1 コメントに限り、その場合はユーザーに確認のうえ override (COMMENT_GUARD=off または .claude/tmp/.comment-guard-allow を touch) してください。"}}'
exit 0
