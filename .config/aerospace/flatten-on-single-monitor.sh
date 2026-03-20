#!/bin/bash
# When only one monitor remains, flatten all workspace trees
# to fix vertical splits persisting from multi-monitor layout

sleep 0.5
monitor_count=$(aerospace list-monitors 2>/dev/null | wc -l | tr -d ' ')

if [ "$monitor_count" -le 1 ]; then
    aerospace list-workspaces --all 2>/dev/null | while read -r ws; do
        aerospace flatten-workspace-tree --workspace "$ws" 2>/dev/null
    done
fi
