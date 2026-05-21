#!/usr/bin/env bash
# finish-pr-review.sh — Obsidian 保存確認 → worktree --force remove → cmux workspace close
# Claude 側の Bash tool は cd 状態を引き継がないため、1 つの script で全完了処理を行う。

set -uo pipefail

target="${1:-}"
if [[ -z "$target" ]]; then
  echo "usage: finish-pr-review.sh <obsidian-target-path>" >&2
  exit 64
fi

if [[ ! -s "$target" ]]; then
  echo "ERROR: Obsidian copy missing or empty: $target" >&2
  exit 1
fi

wt_path="$PWD"
review_repo="$HOME/projects/knowledge-work/knowledgework-review"

# worktree が消えても valid な dir に居続ける
cd "$HOME"

if git -C "$review_repo" worktree remove --force "$wt_path" 2>/dev/null; then
  echo "worktree removed: $wt_path"
else
  echo "warn: worktree remove failed (not a worktree?): $wt_path" >&2
fi

# cmux は UUID handle を reject するため identify で short ref を取得
ws_ref=$(cmux identify 2>/dev/null | jq -r '.caller.workspace_ref // empty' 2>/dev/null)
if [[ -n "$ws_ref" ]]; then
  cmux close-workspace --workspace "$ws_ref" || echo "warn: cmux close-workspace failed for $ws_ref" >&2
fi
