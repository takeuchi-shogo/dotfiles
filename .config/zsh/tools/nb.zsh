# =============================================================================
# nb cli - Terminal Note Management
# =============================================================================

# nb が存在する場合のみ設定
if (( $+commands[nb] )); then
  # Neovim をエディタに設定
  export EDITOR="${EDITOR:-nvim}"
  export NB_DEFAULT_EXTENSION="md"

  # エイリアス
  alias n="nb"
  alias nn="nb new"
  alias ns="nb search"
  alias nl="nb list"
  alias ne="nb edit"
  alias nd="nb delete"
  alias nsh="nb show"

  # nb の補完を有効化
  eval "$(nb completions zsh)"
fi
