# mise
if command -v mise &>/dev/null; then
  eval "$(mise activate zsh)"
  export MISE_AGE_SSH_IDENTITY_FILES="$HOME/.ssh/id_ed25519"
fi
