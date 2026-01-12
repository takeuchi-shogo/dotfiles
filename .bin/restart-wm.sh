#!/bin/bash
# Restart window manager services (sketchybar & aerospace)

set -e

echo "🔄 Restarting window manager services..."

# Stop sketchybar
echo "  Stopping sketchybar..."
pkill -9 sketchybar 2>/dev/null || true
sleep 1

# Stop AeroSpace
echo "  Stopping AeroSpace..."
pkill -9 AeroSpace 2>/dev/null || true
sleep 1

# Start sketchybar
echo "  Starting sketchybar..."
brew services start sketchybar >/dev/null 2>&1 || sketchybar &
sleep 1

# Start AeroSpace
echo "  Starting AeroSpace..."
open -a AeroSpace
sleep 1

# Verify
echo ""
echo "✅ Status:"
pgrep -l sketchybar && echo "   sketchybar: running" || echo "   sketchybar: not running"
pgrep -l AeroSpace && echo "   AeroSpace: running" || echo "   AeroSpace: not running"

echo ""
echo "🎉 Done!"
