#!/usr/bin/env bash
# prepare-pr-review.sh — knowledge-work/knowledgework 専用 PR レビュー準備スクリプト
#
# 使い方:
#   prepare-pr-review.sh <PR_NUMBER>
#
# 動作:
#   1. ~/projects/knowledge-work/knowledgework-review/ に worktree を切る
#      .claude/worktrees/pr-<NUM>/  (PR ブランチ checkout)
#   2. REVIEW_TASK.md を生成 (テンプレを placeholder 置換)
#   3. 次に何をすればいいかを stdout に出す
#
# 出力ファイル: 後段の claude セッションが <worktree>/.claude/pr-reviews/pr-<NUM>.md を生成する
#
# Refs: dotfiles/templates/pr-review/REVIEW_TASK.md.tpl

set -euo pipefail

# ---- 設定 (knowledge-work 専用にハードコード) ----
readonly REPO_OWNER="knowledge-work"
readonly REPO_NAME="knowledgework"
readonly REVIEW_REPO_DIR="${HOME}/projects/knowledge-work/knowledgework-review"
readonly TEMPLATE_PATH="${HOME}/dotfiles/templates/pr-review/REVIEW_TASK.md.tpl"

# ---- 引数 ----
if [[ $# -ne 1 ]]; then
  echo "usage: prepare-pr-review.sh <PR_NUMBER>" >&2
  exit 64
fi

PR_NUMBER="$1"
if ! [[ "$PR_NUMBER" =~ ^[0-9]+$ ]]; then
  echo "error: PR number must be a positive integer, got: $PR_NUMBER" >&2
  exit 64
fi

# ---- 前提チェック ----
command -v gh >/dev/null || { echo "error: gh not found" >&2; exit 127; }
command -v jq >/dev/null || { echo "error: jq not found" >&2; exit 127; }
[[ -d "$REVIEW_REPO_DIR" ]] || { echo "error: review repo not found: $REVIEW_REPO_DIR" >&2; exit 1; }
[[ -f "$TEMPLATE_PATH" ]] || { echo "error: template not found: $TEMPLATE_PATH" >&2; exit 1; }

cd "$REVIEW_REPO_DIR"

# repo がターゲットと一致するか確認
remote_url=$(git remote get-url origin 2>/dev/null || echo "")
if [[ "$remote_url" != *"${REPO_OWNER}/${REPO_NAME}"* ]]; then
  echo "error: review repo's origin does not match ${REPO_OWNER}/${REPO_NAME}" >&2
  echo "  expected pattern: ${REPO_OWNER}/${REPO_NAME}" >&2
  echo "  actual: $remote_url" >&2
  exit 1
fi

# ---- PR メタ取得 ----
echo "==> Fetching PR #${PR_NUMBER} metadata..."
pr_json=$(gh pr view "$PR_NUMBER" \
  --repo "${REPO_OWNER}/${REPO_NAME}" \
  --json number,title,author,headRefName,baseRefName,url,files,state,isDraft)

pr_state=$(echo "$pr_json" | jq -r '.state')
pr_draft=$(echo "$pr_json" | jq -r '.isDraft')
if [[ "$pr_state" != "OPEN" ]]; then
  echo "warning: PR #${PR_NUMBER} is $pr_state (not OPEN). Continue anyway." >&2
fi
if [[ "$pr_draft" == "true" ]]; then
  echo "warning: PR #${PR_NUMBER} is draft. Continue anyway." >&2
fi

PR_TITLE=$(echo "$pr_json" | jq -r '.title')
PR_AUTHOR=$(echo "$pr_json" | jq -r '.author.login')
PR_BRANCH=$(echo "$pr_json" | jq -r '.headRefName')
BASE_BRANCH=$(echo "$pr_json" | jq -r '.baseRefName')
PR_URL=$(echo "$pr_json" | jq -r '.url')
FILES_CHANGED=$(echo "$pr_json" | jq -r '.files | length')

# ---- worktree 作成 ----
worktree_path="${REVIEW_REPO_DIR}/.claude/worktrees/pr-${PR_NUMBER}"
worktree_branch="pr-review-${PR_NUMBER}"

if [[ -d "$worktree_path" ]]; then
  echo "==> Worktree already exists: $worktree_path"
  echo "    (skipping checkout; re-using existing worktree)"
else
  echo "==> Creating worktree: $worktree_path"
  echo "    branch: $PR_BRANCH (tracked as $worktree_branch)"
  git fetch origin "$PR_BRANCH" --quiet
  mkdir -p "${REVIEW_REPO_DIR}/.claude/worktrees"
  git worktree add -b "$worktree_branch" "$worktree_path" "origin/${PR_BRANCH}"
fi

# ---- REVIEW_TASK.md 生成 ----
mkdir -p "${worktree_path}/.claude/pr-reviews"
review_task_path="${worktree_path}/REVIEW_TASK.md"

# placeholder 置換 (sed -i は macOS/GNU 差があるので mktemp 経由)
tmp_file=$(mktemp)
trap 'rm -f "$tmp_file"' EXIT

# PR_TITLE などは sed delimiter (`#`, `|`, `/`) と衝突しうるので
# python で literal 置換する (regex を介さないので escape 不要)
PR_NUMBER="$PR_NUMBER" \
PR_URL="$PR_URL" \
PR_TITLE="$PR_TITLE" \
PR_AUTHOR="$PR_AUTHOR" \
PR_BRANCH="$PR_BRANCH" \
BASE_BRANCH="$BASE_BRANCH" \
FILES_CHANGED="$FILES_CHANGED" \
python3 -c '
import os, sys
with open(sys.argv[1]) as f:
    text = f.read()
for k in ("PR_NUMBER","PR_URL","PR_TITLE","PR_AUTHOR","PR_BRANCH","BASE_BRANCH","FILES_CHANGED"):
    text = text.replace("{{" + k + "}}", os.environ.get(k, ""))
sys.stdout.write(text)
' "$TEMPLATE_PATH" > "$tmp_file"

mv "$tmp_file" "$review_task_path"
trap - EXIT

# ---- 次の手順を案内 ----
cat <<EOF

✅ Setup complete.

PR #${PR_NUMBER}: ${PR_TITLE}
  Author : @${PR_AUTHOR}
  Branch : ${PR_BRANCH} → ${BASE_BRANCH}
  Files  : ${FILES_CHANGED}
  URL    : ${PR_URL}

Worktree : ${worktree_path}
Task file: ${review_task_path}
Output   : ${worktree_path}/.claude/pr-reviews/pr-${PR_NUMBER}.md

Next steps:
  cd "${worktree_path}"
  claude
  # その後 Claude の中で: @REVIEW_TASK.md を読んでレビュー開始

When done:
  open "${worktree_path}/.claude/pr-reviews/pr-${PR_NUMBER}.md"
  # worktree の片付け:
  cd "${REVIEW_REPO_DIR}"
  git worktree remove "${worktree_path}"
  git branch -D "${worktree_branch}"
EOF
