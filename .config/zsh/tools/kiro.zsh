# kiro shell integration
if [[ "$TERM_PROGRAM" == "kiro" ]]; then
  . "$(kiro --locate-shell-integration-path zsh)"
fi
