#!/usr/bin/env bash
set -euo pipefail

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Clipboard to Scrap
# @raycast.mode fullOutput

# Optional parameters:
# @raycast.icon 📝
# @raycast.packageName Claude
# @raycast.argument1 { "type": "text", "placeholder": "追加指示 (任意)", "optional": true }

# Documentation:
# @raycast.description クリップボードの調査メモを匿名化した Markdown スクラップへ整形し、結果をクリップボードに戻す
# @raycast.author takeuchi-shogo
# @raycast.authorURL https://github.com/takeuchi-shogo

# Raycast は login shell を通さない。mise shims は claude の SessionEnd hook が node を要求するため。
export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:/opt/homebrew/bin:$PATH"
export LANG="${LANG:-ja_JP.UTF-8}"
# USER が無いと claude が資格情報を見つけられず "Not logged in" で落ちる (実測)。
export USER="${USER:-$(id -un)}"

input=$(pbpaste)
if [[ -z "${input//[[:space:]]/}" ]]; then
  echo "クリップボードが空です。整形したいテキストをコピーしてから実行してください。" >&2
  exit 1
fi

prompt="入力テキストは調査中に取ったメモやログの断片です。再利用できる技術スクラップに整形してください。

- 社内固有の識別子 (プロダクト名・企業名・内部サービス名・ホスト名) は「対象アプリケーション」「対象環境」等の一般名に置き換える
- 公開技術の名称・公式ドキュメントの URL・引用はそのまま残す
- 見出しは \`# <技術名>\` から始め、概要・背景・手順/コマンド・補足の順で構成する
- 補足は \`> [!NOTE]\` で示す
- 出力は Markdown 本文のみ。前置きや講評は書かない"

if [[ -n "${1:-}" ]]; then
  prompt+="

追加指示: $1"
fi

result=$(printf '%s' "$input" | claude -p --model sonnet "$prompt")

printf '%s\n' "$result"
[[ -n "${NO_PBCOPY:-}" ]] || printf '%s' "$result" | pbcopy
