#!/bin/bash
# When only one monitor remains, windows that lived on the removed monitor
# (e.g. Arc) keep their off-screen frame even though AeroSpace thinks they're
# visible, so `workspace X` "does nothing". Switching through every non-empty
# workspace makes AeroSpace hide and re-show each one, which re-applies the
# frames without touching the tree. (flatten-workspace-tree and a
# floating->tiling round trip used to do this, but they wiped joins and
# reordered windows every time a monitor was unplugged.)

log="$HOME/Library/Logs/aerospace-monitor-change.log"
exec >>"$log" 2>&1
echo "$(date '+%F %T') focused monitor changed"

sleep 0.5
monitor_count=$(aerospace list-monitors | wc -l | tr -d ' ')
echo "monitors: $monitor_count"
[ "$monitor_count" -le 1 ] || exit 0

original=$(aerospace list-workspaces --focused)
aerospace list-workspaces --monitor all --empty no | while read -r ws; do
    aerospace workspace "$ws"
done
aerospace workspace "$original"
echo "re-applied frames, back to workspace $original"
