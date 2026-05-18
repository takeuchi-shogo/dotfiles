#!/usr/bin/env bash
# cmux-worktree-daemon.sh — cmux で workspace 作成時に自動で git worktree を切る daemon
#
# 公式 cmux events.md の Resume 契約に準拠 (--reconnect + --cursor-file):
#   1. events.stream を最後に処理した seq で開始
#   2. --reconnect で再接続を cmux 側に委ねる
#   3. --cursor-file で seq を side effect 成功後に永続化
# Ref: https://github.com/manaflow-ai/cmux/blob/main/docs/events.md
#
# workspace.created event の payload (実機確認 2026-05-19):
#   { name: "workspace.created", source: "workspace.lifecycle",
#     payload: { workspace_id, cwd, title, custom_title, index, tab_count, ... } }
#
# 動作 (smart auto モード, default):
#   1. workspace.created event 受信
#   2. payload.cwd が git repo (main repo, worktree 内ではない) か検査
#   3. payload.title (or custom_title) を sanitize → worktree 名
#   4. 既存 worktree なし & cwd が main repo なら git worktree add 実行
#
# Env:
#   CMUX_CLI                              cmux CLI path (default: 動的解決)
#   CMUX_WORKTREE_DAEMON_DISABLE=1        kill switch (no-op exit)
#   CMUX_WORKTREE_DAEMON_OPT_IN_PREFIX    title prefix で opt-in mode (default: 空 = smart auto)
#   CMUX_WORKTREE_CURSOR_FILE             cursor seq file (default: ~/.cache/cmux/cmux-worktree-cursor.seq)
#   CMUX_WORKTREE_LOG_FILE                log file (default: ~/.cache/cmux/cmux-worktree-daemon.log)
#
# Refs: GitHub Issue #51

set -euo pipefail

CMUX_CLI="${CMUX_CLI:-$(command -v cmux 2>/dev/null || echo /Applications/cmux.app/Contents/Resources/bin/cmux)}"
CURSOR_FILE="${CMUX_WORKTREE_CURSOR_FILE:-$HOME/.cache/cmux/cmux-worktree-cursor.seq}"
LOG_FILE="${CMUX_WORKTREE_LOG_FILE:-$HOME/.cache/cmux/cmux-worktree-daemon.log}"

mkdir -p "$(dirname "$CURSOR_FILE")" "$(dirname "$LOG_FILE")"

log() {
  printf '%s %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*" >>"$LOG_FILE"
}

if [[ "${CMUX_WORKTREE_DAEMON_DISABLE:-}" == "1" ]]; then
  log "DISABLED via CMUX_WORKTREE_DAEMON_DISABLE=1"
  exit 0
fi

# title から worktree 名を sanitize ([^a-zA-Z0-9_+.-] → -, multi - 統合, 前後 trim)
# `.` `..` 等の path-special name は明示的に空文字 reject (path traversal 防止)
sanitize_name() {
  local s
  s=$(printf '%s' "$1" | sed -E 's/[^a-zA-Z0-9_+.-]/-/g; s/-+/-/g; s/^-+|-+$//g')
  case "$s" in
    ""|"."|".."|".git") s="" ;;
  esac
  # 先頭ドット (`.foo` / `..foo`) も reject (dotfile 衝突防止)
  case "$s" in
    .*) s="" ;;
  esac
  printf '%s' "$s"
}

process_event() {
  local event="$1"
  local name workspace_id cwd title prefix repo_root common_dir git_dir name_safe wt_path

  # jq parse 失敗で daemon 全体が `set -e` × subshell で停止しないよう `|| true` で吸収
  name=$(printf '%s' "$event" | jq -r '.name // empty' 2>/dev/null || true)
  [[ "$name" == "workspace.created" ]] || return 0

  workspace_id=$(printf '%s' "$event" | jq -r '.payload.workspace_id // empty' 2>/dev/null || true)
  cwd=$(printf '%s' "$event" | jq -r '.payload.cwd // empty' 2>/dev/null || true)
  title=$(printf '%s' "$event" | jq -r '.payload.custom_title // .payload.title // empty' 2>/dev/null || true)

  if [[ -z "$workspace_id" || -z "$cwd" || -z "$title" ]]; then
    log "skip: missing fields (ws=$workspace_id cwd=$cwd title=$title)"
    return 0
  fi

  # Opt-in mode: prefix が設定されていれば title 先頭一致のみ通過
  prefix="${CMUX_WORKTREE_DAEMON_OPT_IN_PREFIX:-}"
  if [[ -n "$prefix" && "${title#"$prefix"}" == "$title" ]]; then
    log "skip opt-in: '$title' lacks prefix '$prefix' (ws=$workspace_id)"
    return 0
  fi

  # smart auto: cwd が git repo か
  if ! repo_root=$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null); then
    log "skip: cwd not a git repo ($cwd) (ws=$workspace_id)"
    return 0
  fi

  # bare repo は worktree add 不可 + main/worktree 判定が無意味
  if [[ "$(git -C "$cwd" rev-parse --is-bare-repository 2>/dev/null)" == "true" ]]; then
    log "skip: cwd is bare repo ($cwd) (ws=$workspace_id)"
    return 0
  fi

  # cwd が main repo か (worktree 内なら再帰防止で skip)
  # 相対パス/絶対パスの混在を防ぐため `cd && pwd -P` で正規化して比較
  common_dir=$(cd "$cwd" && cd "$(git -C "$cwd" rev-parse --git-common-dir 2>/dev/null)" 2>/dev/null && pwd -P) || common_dir=""
  git_dir=$(cd "$cwd" && cd "$(git -C "$cwd" rev-parse --git-dir 2>/dev/null)" 2>/dev/null && pwd -P) || git_dir=""
  if [[ -z "$common_dir" || -z "$git_dir" || "$git_dir" != "$common_dir" ]]; then
    log "skip: cwd is in a worktree, not main repo ($cwd) (ws=$workspace_id)"
    return 0
  fi

  name_safe=$(sanitize_name "$title")
  if [[ -z "$name_safe" ]]; then
    log "skip: empty sanitized name from title='$title' (ws=$workspace_id)"
    return 0
  fi

  wt_path="$repo_root/.claude/worktrees/$name_safe"

  # 正規登録されている worktree は skip (SIGTERM 中断で残った orphan dir と区別)
  if git -C "$repo_root" worktree list --porcelain 2>/dev/null | grep -qx "worktree $wt_path"; then
    log "skip: worktree exists ($wt_path) (ws=$workspace_id)"
    return 0
  fi

  # orphan directory が残っているなら手動 cleanup を要求 (壊れた worktree の永続化を防止)
  if [[ -e "$wt_path" ]]; then
    log "⚠️ stale path at $wt_path (not a registered worktree) — manual cleanup required (ws=$workspace_id)"
    return 0
  fi

  if git -C "$repo_root" worktree add "$wt_path" -b "worktree-$name_safe" >>"$LOG_FILE" 2>&1; then
    log "✅ worktree created: $wt_path (ws=$workspace_id title='$title')"
  else
    log "❌ worktree add failed: $wt_path (ws=$workspace_id)"
  fi
}

log "cmux-worktree-daemon starting (cmux=$CMUX_CLI cursor=$CURSOR_FILE)"

# 公式 Resume 契約: --reconnect で永続接続、--cursor-file で seq 永続化
"$CMUX_CLI" events \
  --reconnect \
  --cursor-file "$CURSOR_FILE" \
  --category workspace \
  --name workspace.created \
  --no-ack --no-heartbeat \
  2>>"$LOG_FILE" | while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  process_event "$line"
done
