# arc-debug: Arc をリモートデバッグポート付きで再起動し、agent-browser から
# 普段のログイン状態のまま操作できるようにする。
#
# 提供 function:
#   arc-debug        - Arc を --remote-debugging-port 付きで再起動
#   arc-debug off    - Arc を通常起動に戻す (ポートを閉じる)
#
# 接続: agent-browser --session arc --cdp 9222 tab new <url>
# ポートが開いている間は、このマシンの任意のプロセスがログイン済み Arc を操作できる。
# デバッグが終わったら arc-debug off で閉じる。
# Arc は起動済みだと起動フラグを無視するため、付け外しには必ず再起動が要る。
# Claude Code からも呼ぶ (settings.json の ask で毎回承認)。中の osascript / open は
# Bash(osascript *) / Bash(open *) deny の意図的な例外 (references/deny-rules-catalog.md の ASK 節)。

_arc_debug_port() { print -r -- "${ARC_DEBUG_PORT:-9222}"; }

_arc_listening() {
  lsof -nP -iTCP:"$(_arc_debug_port)" -sTCP:LISTEN 2>/dev/null | grep -q '^Arc'
}

_arc_quit() {
  pgrep -x Arc >/dev/null || return 0
  osascript -e 'quit app "Arc"' || return 1
  local i
  for i in {1..30}; do
    pgrep -x Arc >/dev/null || return 0
    sleep 1
  done
  print -u2 "arc-debug: Arc が 30 秒以内に終了しなかった (保存ダイアログが出ていないか確認)"
  return 1
}

arc-debug() {
  local port
  port="$(_arc_debug_port)"

  if [[ "$1" == "off" ]]; then
    _arc_quit || return 1
    open -a Arc
    print "arc-debug: Arc を通常起動に戻した"
    return 0
  fi

  if _arc_listening; then
    print "arc-debug: Arc は既に :$port で待ち受けている"
    return 0
  fi

  _arc_quit || return 1
  open -a Arc --args --remote-debugging-port="$port"

  local i
  for i in {1..30}; do
    if _arc_listening; then
      print "arc-debug: :$port で待ち受け開始。agent-browser --session arc --cdp $port tab new <url>"
      return 0
    fi
    sleep 1
  done
  print -u2 "arc-debug: Arc は起動したが :$port が開かない (Arc 側がフラグを無視している可能性)"
  return 1
}
