# pyenv (lazy load)
# 初回呼び出し時に初期化することで起動を高速化
pyenv() {
  unfunction pyenv
  eval "$(command pyenv init - zsh)"
  pyenv "$@"
}
