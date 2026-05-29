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

# ---- 動作オプション (env var) ----
# PR_REVIEW_AUTHOR=<login>  指定 author のみ対象 (空文字なら全 author)
# PR_REVIEW_DRY_RUN=1       cmux invoke せず log だけ出す
# PR_REVIEW_FORCE=1         host gate を bypass (検証用)
readonly AUTHOR_FILTER="${PR_REVIEW_AUTHOR:-}"
readonly DRY_RUN="${PR_REVIEW_DRY_RUN:-0}"
readonly WORKTREE_WAIT_MAX_SEC=10  # invoke 後 worktree dir が現れるのを待つ最大秒数

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
  local vault_dir="$vault/PR_REVIEW_AGENT/V1.1"
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

# 特定 PR の worktree dir が現れるまで poll で待つ (0.5s * 20 = 10s 上限)。
# cmux new-workspace は async で prepare-pr-review.sh を実行するため、
# 固定 sleep より状態確認の方が堅牢 (環境依存の遅延に追従)。
# timeout しても poll script は止めず、次の iteration の count_active に委ねる。
wait_for_worktree() {
  local pr_num=$1
  local wt="$WORKTREE_DIR/pr-${pr_num}"
  local i max=$((WORKTREE_WAIT_MAX_SEC * 2))
  for ((i = 0; i < max; i++)); do
    [[ -d "$wt" ]] && return 0
    sleep 0.5
  done
  log "warn pr-${pr_num}: worktree did not appear within ${WORKTREE_WAIT_MAX_SEC}s (count_active may undercount)"
  return 1
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
  --limit 30 2>>"$LOG_FILE") || {
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

  # Author allowlist (PR_REVIEW_AUTHOR が set されていれば一致する author のみ)
  if [[ -n "$AUTHOR_FILTER" && "$pr_author" != "$AUTHOR_FILTER" ]]; then
    log "skip pr-${pr_num}: author filter (${pr_author} != ${AUTHOR_FILTER})"
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

  if [[ "$DRY_RUN" == "1" ]]; then
    log "DRY_RUN: would invoke cmux for pr-${pr_num} (author: @${pr_author}): ${pr_title}"
    continue  # marker は書かない (再 poll 可能に保つ)
  fi

  log "invoke cmux for pr-${pr_num} (author: @${pr_author}): ${pr_title}"

  if env CMUX_PR_NUMBER="$pr_num" cmux new-workspace --command "PR Review Agent" >> "$LOG_FILE" 2>&1; then
    touch "$marker"
    log "ok pr-${pr_num}: marker written"
    # cmux new-workspace は async。次の iteration で count_active が同期するよう
    # prepare-pr-review.sh が worktree dir を作るまで poll で待つ。
    wait_for_worktree "$pr_num" || true
  else
    log "ERROR pr-${pr_num}: cmux new-workspace failed (exit $?)"
    # marker は作らない → 次回 polling で再試行可能
  fi
done

exit 0
