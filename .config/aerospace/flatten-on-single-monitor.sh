#!/bin/bash
# When only one monitor remains, flatten all workspace trees
# to fix vertical splits persisting from multi-monitor layout.
# Also re-tile every tiled window: windows that lived on the removed monitor
# (e.g. Arc) keep their off-screen frame even though AeroSpace thinks they're
# visible, so `workspace X` "does nothing". A floating->tiling round trip
# forces AeroSpace to re-apply the frame.

sleep 0.5
monitor_count=$(aerospace list-monitors 2>/dev/null | wc -l | tr -d ' ')

if [ "$monitor_count" -le 1 ]; then
    aerospace list-workspaces --all 2>/dev/null | while read -r ws; do
        aerospace flatten-workspace-tree --workspace "$ws" 2>/dev/null
    done
    aerospace list-windows --all --format '%{window-id} %{window-layout}' 2>/dev/null |
        while read -r id layout; do
            [ "$layout" = floating ] && continue
            aerospace layout floating --window-id "$id" 2>/dev/null
            aerospace layout tiling --window-id "$id" 2>/dev/null
        done
fi
