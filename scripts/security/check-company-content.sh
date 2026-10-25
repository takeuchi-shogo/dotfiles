#!/bin/bash
# check-company-content.sh — public dotfiles に会社関連文言が commit されるのを防ぐ pre-commit guard
#
# 背景: dotfiles は PUBLIC リポジトリ。会社固有のファイル・文言は ~/dotfiles-private で
# 管理する (overlay symlink 方式、dotfiles-private/install.sh 参照)。
# 2026-06-04 に会社文言入り commit を push 寸前で取り消したインシデントの再発防止。
#
# 引数なし: lefthook pre-commit と同じく staged diff (--cached) を検査する。
# 引数あり: そのまま git diff に渡す (CI は origin/master...HEAD)。
set -euo pipefail

# 引数なしは staged。引数ありは git diff の範囲として使う。
if [ "$#" -eq 0 ]; then
  set -- --cached
fi

# self-match 防止のためパターンを文字列連結で組み立てる
pattern="knowledge[-]?""work"

# allowlist: 公開リポジトリ参照 (会社内部文言ではない)
# - anthropics/knowledge-work (GitHub URL パス形式)
# - anthropic-knowledge-work / knowledge-work-plugins (Anthropic 公式 repo 派生ラベル)
allowlist_pattern="anthropics?[/-]knowledge[-]?work|knowledge[-]?work[-]plugins"

# 追加行のみ検査 (既存行・削除行・ファイルヘッダは対象外)。
# git diff の失敗は握りつぶさない。grep の「該当なし」だけを成功扱いにする。
diff_out=$(git diff "$@" --unified=0)
hits=$(printf '%s\n' "$diff_out" | grep -E '^\+' | grep -vE '^\+\+\+' | grep -iE "$pattern" | grep -vE "$allowlist_pattern" || true)

if [ -n "$hits" ]; then
  echo "❌ [company-content-guard] 会社関連の文言が対象 diff に含まれています:" >&2
  echo "   git diff $*" >&2
  echo "$hits" | head -10 >&2
  echo "" >&2
  echo "   dotfiles は PUBLIC リポジトリです。会社関連の内容は ~/dotfiles-private に置き、" >&2
  echo "   install.sh の overlay symlink で運用してください。" >&2
  exit 1
fi
