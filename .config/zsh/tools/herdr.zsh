# herdr (AI エージェント multiplexer) CLI 補完
# clap 生成の #compdef スクリプトは source 時に `compdef _herdr herdr` で自己登録する。
# docker.zsh が先に compinit を走らせるため、ここでは eval するだけでよい。
if command -v herdr &>/dev/null; then
  eval "$(herdr completion zsh)"
fi
