#!/usr/bin/env bash
# pr-review-setup.sh — cmux PR Review Agent の Setup pane エントリポイント。
# cmux.json の inline command は約 1024 byte で切れる (paste buffer 制限) ため
# 処理本体を本スクリプトに切り出す。Setup pane の "command" は本スクリプト 1 行を呼ぶだけ。

set -euo pipefail

: "${TMPDIR:?TMPDIR must be set (run via cmux)}"
: "${CMUX_WORKSPACE_ID:?CMUX_WORKSPACE_ID must be set (run via cmux)}"
[[ -O "$TMPDIR" && -d "$TMPDIR" && ! -L "$TMPDIR" ]] || {
  echo "ABORT: TMPDIR not user-owned non-symlink dir: $TMPDIR" >&2
  exec "${SHELL:-/bin/zsh}" -l
}

state="${TMPDIR%/}/cmux-pr-review-${CMUX_WORKSPACE_ID}.dir"
rm -f "$state" "${state}.claude_surface"

printf '\033[1;33mPR Review Agent — knowledge-work/knowledgework\033[0m\n'

if [[ -n "${CMUX_PR_NUMBER:-}" ]]; then
  pr_num="$CMUX_PR_NUMBER"
  echo "Auto: PR #$pr_num (from CMUX_PR_NUMBER)"
else
  # stty raw mode + 500ms inter-key timeout で「数字入れて待てば自動確定」する。
  # Enter / Backspace / Ctrl+C もサポート。
  # 非 tty 環境 (SSH 経由・自動化等) では raw mode が使えず無限ループするため早めに弾く。
  [[ -t 0 ]] || { echo "ERROR: PR number prompt requires interactive tty" >&2; exec "${SHELL:-/bin/zsh}" -l; }
  printf 'Enter PR number (auto-confirm after 0.5s pause): '
  stty_orig=$(stty -g </dev/tty)
  trap 'stty "$stty_orig" </dev/tty 2>/dev/null' EXIT INT TERM
  stty -icanon -echo time 5 min 0 </dev/tty
  pr_num=""
  while :; do
    ch=$(dd bs=1 count=1 2>/dev/null </dev/tty || true)
    if [[ -z "$ch" ]]; then
      [[ -n "$pr_num" ]] && break
      continue
    fi
    case "$ch" in
      [0-9])
        pr_num+="$ch"
        printf '%s' "$ch" >/dev/tty
        ;;
      $'\n'|$'\r')
        [[ -n "$pr_num" ]] && break
        ;;
      $'\x7f'|$'\b')
        if [[ -n "$pr_num" ]]; then
          pr_num="${pr_num%?}"
          printf '\b \b' >/dev/tty
        fi
        ;;
      $'\x03')
        printf '\n' >/dev/tty
        stty "$stty_orig" </dev/tty
        exit 130
        ;;
    esac
  done
  stty "$stty_orig" </dev/tty
  trap - EXIT INT TERM
  printf '\n' >/dev/tty
fi

if ! [[ "$pr_num" =~ ^[0-9]+$ ]]; then
  echo "ERROR: invalid PR number: $pr_num" >&2
  exec "${SHELL:-/bin/zsh}" -l
fi

~/dotfiles/scripts/runtime/prepare-pr-review.sh "$pr_num" || {
  echo "ERROR: prepare-pr-review.sh failed" >&2
  exec "${SHELL:-/bin/zsh}" -l
}

worktree="$HOME/projects/knowledge-work/knowledgework-review/.claude/worktrees/pr-${pr_num}"
printf '%s\n' "$worktree" > "$state"
cd "$worktree"

nohup ~/dotfiles/scripts/runtime/inject-review-prompt.sh >/dev/null 2>&1 &
disown

echo ""
echo "--- Worktree ready. Claude pane will start automatically. ---"
exec "${SHELL:-/bin/zsh}" -l
