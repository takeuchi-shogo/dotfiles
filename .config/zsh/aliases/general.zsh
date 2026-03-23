# General aliases

# eza (ls 上位互換)
if command -v eza &>/dev/null; then
  alias ls='eza --icons --git'
  alias ll='eza -la --icons --git'
  alias la='eza -a --icons --git'
  alias lt='eza --tree --icons --git -L 2'
else
  alias ll='ls -la'
  alias la='ls -a'
fi

# bat (cat 上位互換)
if command -v bat &>/dev/null; then
  alias cat='bat --paging=never'
fi

# dust (du 上位互換)
if command -v dust &>/dev/null; then
  alias du='dust'
fi

alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias mkdir='mkdir -p'
alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'
