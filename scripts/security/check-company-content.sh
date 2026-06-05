#!/bin/bash
# check-company-content.sh — public dotfiles に会社関連文言が commit されるのを防ぐ pre-commit guard
#
# 背景: dotfiles は PUBLIC リポジトリ。会社固有のファイル・文言は ~/dotfiles-private で
# 管理する (overlay symlink 方式、dotfiles-private/install.sh 参照)。
# 2026-06-04 に会社文言入り commit を push 寸前で取り消したインシデントの再発防止。
set -euo pipefail

# self-match 防止のためパターンを文字列連結で組み立てる
pattern="knowledge[-]?""work"

# staged diff の追加行のみ検査 (既存行・削除行・ファイルヘッダは対象外)
hits=$(git diff --cached --unified=0 | grep -E '^\+' | grep -vE '^\+\+\+' | grep -iE "$pattern" || true)

if [ -n "$hits" ]; then
  echo "❌ [company-content-guard] 会社関連の文言が staged diff に含まれています:" >&2
  echo "$hits" | head -10 >&2
  echo "" >&2
  echo "   dotfiles は PUBLIC リポジトリです。会社関連の内容は ~/dotfiles-private に置き、" >&2
  echo "   install.sh の overlay symlink で運用してください。" >&2
  exit 1
fi
