# ghq-fzf: ghq list → (roots) → fzf でリポジトリ/サブルートを fuzzy 選択
#
# 依存:
#   - ghq         (必須)  https://github.com/x-motemen/ghq
#   - fzf         (必須)
#   - k1LoW/roots (任意)  あれば monorepo の sub-root も列挙。無ければフォールバック
#
# Bind: Ctrl+G
ghq-fzf() {
  local fzf_opts=(--height 40% --reverse --preview 'ls -la {} 2>/dev/null | head -50')
  local selected
  if command -v roots >/dev/null 2>&1; then
    selected=$(ghq list --full-path | roots | fzf "${fzf_opts[@]}")
  else
    selected=$(ghq list --full-path | fzf "${fzf_opts[@]}")
  fi
  if [[ -n "$selected" ]]; then
    BUFFER="cd ${(q)selected}"
    zle accept-line
  else
    zle reset-prompt
  fi
}
zle -N ghq-fzf
bindkey '^g' ghq-fzf
