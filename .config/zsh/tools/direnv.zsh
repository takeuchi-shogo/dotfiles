# =============================================================================
# direnv - Directory-specific Environment Variables
# =============================================================================

if (( $+commands[direnv] )); then
  eval "$(direnv hook zsh)"
fi
