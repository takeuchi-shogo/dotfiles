# PATH settings
export PATH="/opt/homebrew/bin:$PATH"

# Nix home-manager per-user profile. Phase B1 Step 2:
# brew 先頭順序を保持したまま末尾に追加。Phase B2 で順序再設計。
if [ -d "/etc/profiles/per-user/$USER/bin" ]; then
  export PATH="$PATH:/etc/profiles/per-user/$USER/bin"
fi
# home-manager session vars (NH_FLAKE 等). programs.zsh.enable=false のため手動 source。
if [ -f "/etc/profiles/per-user/$USER/etc/profile.d/hm-session-vars.sh" ]; then
  . "/etc/profiles/per-user/$USER/etc/profile.d/hm-session-vars.sh"
fi
if [ -d "/run/current-system/sw/bin" ]; then
  export PATH="$PATH:/run/current-system/sw/bin"
fi
export PATH="/usr/local/opt/php@8.0/bin:$PATH"
export PATH="/usr/local/opt/php@8.0/sbin:$PATH"
export PATH="$PATH:$GOPATH/bin"
export PATH="$HOME/.local/bin:$PATH"
export PATH="/Applications/WezTerm.app/Contents/MacOS:$PATH"

# Added by Windsurf
export PATH="/Users/takeuchishougo/.codeium/windsurf/bin:$PATH"

# Added by Antigravity
export PATH="/Users/takeuchishougo/.antigravity/antigravity/bin:$PATH"

# pyenv
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
