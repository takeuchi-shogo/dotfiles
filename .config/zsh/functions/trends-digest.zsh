# trends-digest.zsh — その日最初の interactive shell で AI トレンド digest を表示する。
# 1日1回ガード: ~/.cache/tech-researcher/digest-shown-YYYY-MM-DD (空 stamp)。
# stamp ヒット時は即 return し起動オーバーヘッドを ~1ms に抑える。ledger 不在なら何もしない。
# python 失敗時も stamp は書く (シェル起動ごとの再試行 nag を防ぐ)。ただし WARN は 1 回見せる。
# 設計: docs/superpowers/specs/2026-06-10-knowledge-intake-pipeline-design.md §6.2
_trends_digest_on_first_open() {
  [[ -o interactive ]] || return 0
  local cache_dir="$HOME/.cache/tech-researcher"
  local today stamp ledger
  today="$(date +%Y-%m-%d)"
  stamp="$cache_dir/digest-shown-$today"
  [[ -f "$stamp" ]] && return 0
  ledger="$cache_dir/adoption-ledger.jsonl"
  [[ -f "$ledger" ]] || return 0
  mkdir -p "$cache_dir"
  if ! python3 "$HOME/dotfiles/scripts/runtime/tech-researcher/trends_select.py" \
      "$ledger" --days 3 --top 5; then
    print -u2 "[trends-digest] WARN: trends_select.py failed (今日は再表示しません)"
  fi
  rm -f "$cache_dir"/digest-shown-*(N)
  : > "$stamp"
}
_trends_digest_on_first_open
