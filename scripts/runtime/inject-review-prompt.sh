#!/usr/bin/env bash
# inject-review-prompt.sh — cmux PR Review Agent の Setup pane から
# Claude pane に `@REVIEW_TASK.md` を自動投入する。
# Claude pane の command が `${state}.claude_surface` に自身の surface_ref を
# 書き出し、本スクリプトはそれを polling して直接 send する。
# cmux の surface 名は terminal title escape で動的に書き換わるため、
# name match 方式 (旧実装) では Claude 起動完了後に検出不能だった。

set -uo pipefail

readonly POLL_TIMEOUT_SEC=60
readonly REPL_READY_SEC=10
readonly PROMPT='@REVIEW_TASK.md'
readonly LOG_DIR="${HOME}/Library/Logs/pr-reviewer"
readonly LOG_FILE="${LOG_DIR}/poll.log"

mkdir -p "$LOG_DIR"
log() { printf '%s [inject:%s] %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$$" "$*" >> "$LOG_FILE"; }

# cmux 経由起動の必須前提。/tmp や "manual" への fallback は symlink hijack /
# cross-session 衝突の attack surface を残すため明示的にエラーで止める。
# TMPDIR が user-owned (mode 0700, 通常 /var/folders/.../T) であることを
# 検証することで、attacker が同名ファイルを事前準備する経路を塞ぐ。
: "${TMPDIR:?TMPDIR must be set (run via cmux)}"
: "${CMUX_WORKSPACE_ID:?CMUX_WORKSPACE_ID must be set (run via cmux)}"
[[ -O "$TMPDIR" && -d "$TMPDIR" && ! -L "$TMPDIR" ]] || { log "ABORT: TMPDIR not user-owned non-symlink dir: $TMPDIR"; exit 1; }

state_file="${TMPDIR%/}/cmux-pr-review-${CMUX_WORKSPACE_ID}.dir"
claude_ref_file="${state_file}.claude_surface"

# Claude pane が自身の surface_ref を書き出すのを待つ
surface_ref=""
for _ in $(seq 1 "$POLL_TIMEOUT_SEC"); do
  if [[ -s "$claude_ref_file" ]]; then
    surface_ref=$(< "$claude_ref_file")
    [[ -n "$surface_ref" ]] && break
  fi
  sleep 1
done

if [[ -z "$surface_ref" ]]; then
  log "skip: $claude_ref_file not populated after ${POLL_TIMEOUT_SEC}s"
  exit 0
fi

# whitelist: cmux send へ意図しない値 (別 pane への message injection 含む) を
# 渡さないよう、`surface:<digits>` 形式に限定する
if ! [[ "$surface_ref" =~ ^surface:[0-9]+$ ]]; then
  log "ABORT: invalid surface_ref format: $(printf '%q' "$surface_ref")"
  rm -f "$claude_ref_file"
  exit 1
fi

# surface_ref 取得 ≠ claude REPL ready。REPL 起動 (token check + UI) を少し待つ
sleep "$REPL_READY_SEC"

# cmux send の \n は terminal の Enter として送られる (cmux send --help 参照).
# prompt と Enter を別 call で送ると claude REPL の paste/bracketed-paste 経路で
# \r が「改行文字」として消化され、確定にならないケースがある。
# 1 call で "${PROMPT}\n" を送ることで「ペースト + 即確定」を一連で処理させる。
if cmux send --surface "$surface_ref" "${PROMPT}\n" 2>>"$LOG_FILE"; then
  log "sent prompt+Enter to $surface_ref"
else
  log "ERROR: cmux send failed for $surface_ref"
fi

# stale state を残さない (次回起動前に symlink hijack の窓を狭める)
rm -f "$claude_ref_file"
