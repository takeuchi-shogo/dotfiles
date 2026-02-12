# =============================================================================
# Zsh Configuration
# =============================================================================

ZSHDIR="$HOME/.config/zsh"

# Load configuration files in order
for dir in core tools functions aliases plugins; do
  if [[ -d "$ZSHDIR/$dir" ]]; then
    for file in "$ZSHDIR/$dir"/*.zsh(N); do
      source "$file"
    done
  fi
done
