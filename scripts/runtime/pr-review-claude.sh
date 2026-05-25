#!/usr/bin/env bash
# pr-review-claude.sh — cmux PR Review Agent の Claude pane エントリポイント。
# cmux.json の inline command は約 1024 byte で切れる (paste buffer 制限) ため
# 処理本体を本スクリプトに切り出す。Claude pane の "command" は本スクリプト 1 行を呼ぶだけ。

set -euo pipefail

: "${TMPDIR:?TMPDIR must be set (run via cmux)}"
: "${CMUX_WORKSPACE_ID:?CMUX_WORKSPACE_ID must be set (run via cmux)}"
[[ -O "$TMPDIR" && -d "$TMPDIR" && ! -L "$TMPDIR" ]] || {
  echo "ABORT: TMPDIR not user-owned non-symlink dir: $TMPDIR" >&2
  exec "${SHELL:-/bin/zsh}" -l
}

state="${TMPDIR%/}/cmux-pr-review-${CMUX_WORKSPACE_ID}.dir"
echo "Waiting for PR setup (timeout 15 min)..."

# 15 分 (= 4500 × 0.2 秒). PR 番号入力 (人間時間) + prepare-pr-review.sh
# (gh API + worktree clone + checkout) で数分かかるため余裕を持たせる。
elapsed=0
while [ ! -s "$state" ]; do
  sleep 0.2
  elapsed=$((elapsed + 1))
  if [ $elapsed -ge 4500 ]; then
    echo "ERROR: PR review setup timed out after 15 min" >&2
    exec "${SHELL:-/bin/zsh}" -l
  fi
done

dir=$(cat "$state")
cd "$dir"

# inject-review-prompt.sh は ${state}.claude_surface を polling して
# cmux send 先を決める。terminal title 書き換えで surface 名が動的に変わるため
# 名前 match ではなく自身の surface_ref を直接渡す。
cmux identify 2>/dev/null \
  | jq -r '.caller.surface_ref // empty' \
  > "${state}.claude_surface" 2>/dev/null \
  || true

echo ""
echo "================================================"
echo "Worktree: $dir"
echo "Next: type '@REVIEW_TASK.md' and press Enter"
echo "================================================"
echo ""

exec env CLAUDE_SKIP_TEST_GATE=1 claude \
  --permission-mode auto \
  --add-dir "$HOME/Documents/Obsidian Vault" \
  --mcp-config "$dir/.mcp.json"
