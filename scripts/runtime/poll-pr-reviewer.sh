#!/usr/bin/env bash
# poll-pr-reviewer.sh — knowledge-work/knowledgework の review-requested PR を polling し
# cmux PR Review Agent を非対話起動するワーカー。launchd から 10 分間隔で起動する想定。
#
# 動作:
#   1. host gate (work Mac 限定) で early exit
#   2. アクティブ worktree 数を確認 (MAX_PARALLEL=2)
#   3. gh search prs --review-requested=@me で対象 PR 取得
#   4. 各 PR について .processed/pr-<#>.done が無ければ cmux new-workspace を invoke
#   5. invoke 成功で marker 作成 (= 次回以降スキップ)
#
# Refs:
#   - docs/plans/active/2026-05-19-pr-review-agent-plan.md (Phase A)
#   - scripts/runtime/prepare-pr-review.sh (cmux action 内で実行される)
#   - .config/cmux/cmux.json actions.pr-review-agent
#   - docs/playbooks/pr-reviewer-launchd.md (install/uninstall)

set -euo pipefail

# ---- 設定 ----
readonly REPO="knowledge-work/knowledgework"
readonly REVIEW_REPO_DIR="${HOME}/projects/knowledge-work/knowledgework-review"
readonly WORKTREE_DIR="${REVIEW_REPO_DIR}/.claude/worktrees"
readonly PROCESSED_DIR="${REVIEW_REPO_DIR}/.claude/pr-reviews/.processed"
readonly LOG_DIR="${HOME}/Library/Logs/pr-reviewer"
readonly LOG_FILE="${LOG_DIR}/poll.log"
readonly MAX_PARALLEL=2
readonly ALLOWED_HOST="MacBookPro-work"

mkdir -p "$LOG_DIR"
log() { printf '%s [%s] %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$$" "$*" >> "$LOG_FILE"; }

# ---- Host gate (work 環境のみで動作) ----
current_host=$(hostname -s 2>/dev/null || hostname)
if [[ "${PR_REVIEW_FORCE:-0}" != "1" && "$current_host" != "$ALLOWED_HOST" ]]; then
  # silent skip on non-work host (launchd は private Mac にも load されうる前提)
  exit 0
fi

# ---- 前提チェック ----
command -v gh   >/dev/null 2>&1 || { log "ERROR: gh not in PATH"; exit 0; }
command -v cmux >/dev/null 2>&1 || { log "ERROR: cmux not in PATH"; exit 0; }
command -v jq   >/dev/null 2>&1 || { log "ERROR: jq not in PATH"; exit 0; }
[[ -d "$REVIEW_REPO_DIR" ]]     || { log "ERROR: review repo not found: $REVIEW_REPO_DIR"; exit 0; }

mkdir -p "$PROCESSED_DIR"

# ---- 事前 cleanup: Obsidian 保存済 worktree を回収 ----
# Claude セッションが review.md を Obsidian Vault にコピーしたら、その PR の
# worktree は不要 → 自動で git worktree remove して並列枠を空ける。
# uncommitted な変更がある worktree は safe (--force なし) で skip。
cleanup_done_worktrees() {
  local vault="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
  local vault_dir="$vault/AUTO-PR-REVIEW"
  [[ -d "$vault_dir" ]] || return 0
  [[ -d "$WORKTREE_DIR" ]] || return 0

  local wt num obsidian
  for wt in "$WORKTREE_DIR"/pr-*; do
    [[ -d "$wt" ]] || continue
    num=$(basename "$wt" | sed 's/^pr-//')
    [[ "$num" =~ ^[0-9]+$ ]] || continue
    obsidian="$vault_dir/pr-${num}-review.md"
    if [[ -f "$obsidian" ]]; then
      if git -C "$REVIEW_REPO_DIR" worktree remove "$wt" 2>>"$LOG_FILE"; then
        log "cleanup: removed worktree pr-${num} (review in Obsidian)"
      else
        log "cleanup: worktree pr-${num} remove failed (uncommitted? remove manually with --force)"
      fi
    fi
  done
}

cleanup_done_worktrees

# ---- 並列上限チェック ----
# アクティブ worktree = .claude/worktrees/pr-* ディレクトリ数
count_active() {
  if [[ -d "$WORKTREE_DIR" ]]; then
    find "$WORKTREE_DIR" -maxdepth 1 -type d -name 'pr-*' 2>/dev/null | wc -l | tr -d ' '
  else
    echo 0
  fi
}

active=$(count_active)
if (( active >= MAX_PARALLEL )); then
  log "skip cycle: $active active worktree(s) (limit $MAX_PARALLEL)"
  exit 0
fi

# ---- review-requested PR 検索 ----
# gh search prs は GitHub の検索 API を叩く。レート 30 req/min 程度。
# 失敗時は silent skip (次回 polling で再試行)。
prs_json=$(gh search prs \
  --review-requested=@me \
  --state=open \
  --repo "$REPO" \
  --json number,title,author,updatedAt \
  --limit 10 2>>"$LOG_FILE") || {
    log "ERROR: gh search failed (auth? rate limit?)"
    exit 0
  }

pr_count=$(echo "$prs_json" | jq 'length')
log "poll: found $pr_count review-requested PR(s) (active: $active)"

if (( pr_count == 0 )); then
  exit 0
fi

# ---- 各 PR の invoke ----
echo "$prs_json" | jq -c '.[]' | while IFS= read -r pr; do
  pr_num=$(echo "$pr" | jq -r '.number')
  pr_title=$(echo "$pr" | jq -r '.title')
  pr_author=$(echo "$pr" | jq -r '.author.login')
  pr_author_type=$(echo "$pr" | jq -r '.author.type')
  marker="${PROCESSED_DIR}/pr-${pr_num}.done"

  # Bot author (Terraform / Migration / Deploy 自動 PR) はレビュー対象外
  if [[ "$pr_author_type" == "Bot" ]]; then
    log "skip pr-${pr_num}: bot author (${pr_author})"
    continue
  fi

  if [[ -e "$marker" ]]; then
    log "skip pr-${pr_num}: already processed"
    continue
  fi

  # 各 invoke の直前に並列上限を再確認 (前回 invoke で増えうるため)
  active=$(count_active)
  if (( active >= MAX_PARALLEL )); then
    log "stop iteration at pr-${pr_num}: parallel limit reached"
    break
  fi

  log "invoke cmux for pr-${pr_num} (author: @${pr_author}): ${pr_title}"

  if env CMUX_PR_NUMBER="$pr_num" cmux new-workspace --command "PR Review Agent" >> "$LOG_FILE" 2>&1; then
    touch "$marker"
    log "ok pr-${pr_num}: marker written"
  else
    log "ERROR pr-${pr_num}: cmux new-workspace failed (exit $?)"
    # marker は作らない → 次回 polling で再試行可能
  fi
done

exit 0
