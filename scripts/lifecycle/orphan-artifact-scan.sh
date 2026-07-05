#!/usr/bin/env bash
# scripts/lifecycle/orphan-artifact-scan.sh — orphan-artifact inventory (read-only)
#
# Usage: orphan-artifact-scan.sh [repo-root]   (default: cwd の git repo)
# Output: stale worktree / merged・gone・stale ブランチのカテゴリ別一覧 + 件数。
#         最終行 "candidates: N" は nightly wrapper が metric として抽出する。
# Exit:   0 = scan 完了 (候補の有無は問わない)、1 = git repo でない (preflight 失敗)。
#
# 2026-06-06 に worktree 26 個 + 孤児ブランチ 19 個を手動掃除した pain の再発防止。
# doctor-stale.sh と同じ inventory, don't mutate パターン: 削除は人間がレビュー後に
# git worktree remove / git branch -d で行う。
#
# シグナル:
#   worktree:  prunable / merged / gone / stale(Nd)  (+ 属性: dirty, locked)
#   branch:    merged / gone / stale(Nd)  (worktree 未接続のローカルブランチのみ)
# dirty は候補判定に使わず属性として表示する (作業中 worktree の誤検出防止。
# dirty かつ stale は built-but-never-shipped の疑い — 削除前に中身の確認が必要)。
#
# ponytail: merged 判定は true merge のみ (squash merge は gone/stale で拾う)。
# gone は remote-tracking ref の prune 後にしか立たない — nightly wrapper 側が
# 実行前に git fetch --prune を best effort でかける。

set -uo pipefail

STALE_DAYS="${ORPHAN_STALE_DAYS:-14}"
NOW="$(date +%s)"

REPO_ROOT="${1:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"
if [[ -z "$REPO_ROOT" || ! -d "$REPO_ROOT" ]]; then
  echo "orphan-artifact-scan: not a git repository (cwd or \$1)" >&2
  exit 1
fi
cd "$REPO_ROOT" || exit 1

# merged 判定の基準 ref (master 優先、なければ origin/master、両方なければ skip)
BASE_REF=""
for ref in master origin/master; do
  if git rev-parse --verify -q "$ref" >/dev/null 2>&1; then
    BASE_REF="$ref"
    break
  fi
done

# bash 3.2 (macOS 標準) 対応: 配列でなく改行区切り文字列で集合を持つ
ATTACHED_BRANCHES=$'\n'
is_attached() { [[ "$ATTACHED_BRANCHES" == *$'\n'"$1"$'\n'* ]]; }

is_merged() { # $1=branch name
  [[ -n "$BASE_REF" ]] || return 1
  # master tip と同一 (固有コミットなし) は「切っただけ」の可能性が高いので除外。
  # master が進めば ancestor 判定に戻り、放置された空ブランチも正しく merged 扱いになる
  local tip base_tip
  tip="$(git rev-parse "refs/heads/$1" 2>/dev/null)"
  base_tip="$(git rev-parse "$BASE_REF" 2>/dev/null)"
  [[ -n "$tip" && "$tip" != "$base_tip" ]] || return 1
  git merge-base --is-ancestor "refs/heads/$1" "$BASE_REF" 2>/dev/null
}

is_gone() { # $1=branch name
  [[ "$(git for-each-ref --format='%(upstream:track)' "refs/heads/$1" 2>/dev/null)" == "[gone]" ]]
}

commit_age_days() { # $1=committish → 経過日数 (取得不能なら空)
  local ct
  ct="$(git log -1 --format=%ct "$1" 2>/dev/null)"
  [[ -n "$ct" ]] && echo $(((NOW - ct) / 86400))
}

echo "=== orphan-artifact inventory (read-only, stale threshold: ${STALE_DAYS}d, base: ${BASE_REF:-none}) ==="
echo ""

# --- 1) linked worktrees ---
wt_total=0
wt_candidates=0
main_path=""

wt_path="" wt_head="" wt_branch="" wt_detached=0 wt_locked=0 wt_prunable=0
reset_block() { wt_path="" wt_head="" wt_branch="" wt_detached=0 wt_locked=0 wt_prunable=0; }

flush_worktree() {
  [[ -n "$wt_path" ]] || return 0
  # porcelain は main worktree を先頭に列挙する — main 自体は掃除対象外
  if [[ -z "$main_path" ]]; then
    main_path="$wt_path"
    [[ -n "$wt_branch" ]] && ATTACHED_BRANCHES="${ATTACHED_BRANCHES}${wt_branch}"$'\n'
    return 0
  fi
  wt_total=$((wt_total + 1))
  [[ -n "$wt_branch" ]] && ATTACHED_BRANCHES="${ATTACHED_BRANCHES}${wt_branch}"$'\n'

  local flags=""
  [[ "$wt_prunable" -eq 1 ]] && flags="prunable"
  if [[ "$wt_detached" -eq 0 && -n "$wt_branch" ]]; then
    is_merged "$wt_branch" && flags="${flags:+$flags, }merged"
    is_gone "$wt_branch" && flags="${flags:+$flags, }gone"
  fi
  local age=""
  [[ -n "$wt_head" ]] && age="$(commit_age_days "$wt_head")"
  if [[ -n "$age" && "$age" -gt "$STALE_DAYS" ]]; then
    flags="${flags:+$flags, }stale(${age}d)"
  fi

  local attrs=""
  if [[ -d "$wt_path" ]] && [[ -n "$(git -C "$wt_path" status --porcelain 2>/dev/null | head -1)" ]]; then
    attrs="dirty"
  fi
  [[ "$wt_locked" -eq 1 ]] && attrs="${attrs:+$attrs, }locked"

  if [[ -n "$flags" ]]; then
    wt_candidates=$((wt_candidates + 1))
    local label="${wt_path#"$main_path"/}"
    printf "  candidate: %s [%s]" "$label" "$flags"
    [[ -n "$attrs" ]] && printf " (%s)" "$attrs"
    [[ -n "$wt_branch" ]] && printf " branch=%s" "$wt_branch"
    printf "\n"
  fi
}

# scan 失敗を「0 件 = クリーン」と誤読させない: git 失敗は明示エラーで exit 1
# (wrapper が status fail として記録する)
WT_LIST="$(git worktree list --porcelain 2>&1)" || {
  echo "orphan-artifact-scan: git worktree list failed: ${WT_LIST}" >&2
  exit 1
}

echo "[worktrees]"
while IFS= read -r line; do
  case "$line" in
    "worktree "*) wt_path="${line#worktree }" ;;
    "HEAD "*)     wt_head="${line#HEAD }" ;;
    "branch "*)   wt_branch="${line#branch refs/heads/}" ;;
    detached)     wt_detached=1 ;;
    locked*)      wt_locked=1 ;;
    prunable*)    wt_prunable=1 ;;
    "")           flush_worktree; reset_block ;;
  esac
done <<< "$WT_LIST"
flush_worktree
[[ "$wt_candidates" -eq 0 ]] && echo "  candidate: none"
echo "  linked worktrees: ${wt_total}, candidates: ${wt_candidates}"
echo ""

# --- 2) orphan branches (worktree 未接続のローカルブランチ) ---
br_total=0
br_candidates=0

BR_LIST="$(git for-each-ref refs/heads --format='%(refname:short)|%(upstream:track)|%(committerdate:unix)' 2>&1)" || {
  echo "orphan-artifact-scan: git for-each-ref failed: ${BR_LIST}" >&2
  exit 1
}

echo "[orphan branches]"
while IFS='|' read -r br track cdate; do
  [[ -n "$br" ]] || continue
  is_attached "$br" && continue
  br_total=$((br_total + 1))

  local_flags=""
  is_merged "$br" && local_flags="merged"
  [[ "$track" == "[gone]" ]] && local_flags="${local_flags:+$local_flags, }gone"
  if [[ -n "$cdate" ]]; then
    age=$(((NOW - cdate) / 86400))
    [[ "$age" -gt "$STALE_DAYS" ]] && local_flags="${local_flags:+$local_flags, }stale(${age}d)"
  fi

  if [[ -n "$local_flags" ]]; then
    br_candidates=$((br_candidates + 1))
    printf "  candidate: %s [%s]\n" "$br" "$local_flags"
  fi
done <<< "$BR_LIST"
[[ "$br_candidates" -eq 0 ]] && echo "  candidate: none"
echo "  unattached branches: ${br_total}, candidates: ${br_candidates}"
echo ""

# --- summary ---
total=$((wt_candidates + br_candidates))
echo "=== summary ==="
echo "  worktree candidates: ${wt_candidates}"
echo "  branch candidates:   ${br_candidates}"
if [[ "$total" -gt 0 ]]; then
  echo "  NOTE: nothing was deleted. Review and remove manually:"
  echo "        git worktree remove <path> / git branch -d <branch>"
fi
echo "candidates: ${total}"

exit 0
