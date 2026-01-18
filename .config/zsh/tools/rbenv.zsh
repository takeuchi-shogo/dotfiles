# rbenv (lazy load)
# 初回呼び出し時に初期化することで起動を高速化
rbenv() {
  unfunction rbenv
  eval "$(command rbenv init - zsh)"
  rbenv "$@"
}
