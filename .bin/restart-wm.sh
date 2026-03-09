#!/bin/bash
# Restart window manager services (AeroSpace)
# Note: Ice はログイン項目として管理（手動再起動不要）
# Note: SketchyBar 設定は .config/sketchybar/ に保持（Ice に移行済み）

set -e

echo "🔄 Restarting window manager services..."

# Stop AeroSpace
echo "  Stopping AeroSpace..."
pkill -9 AeroSpace 2>/dev/null || true
sleep 1

# Start AeroSpace
echo "  Starting AeroSpace..."
open -a AeroSpace
sleep 1

# Verify
echo ""
echo "✅ Status:"
pgrep -l AeroSpace && echo "   AeroSpace: running" || echo "   AeroSpace: not running"
pgrep -l Ice && echo "   Ice: running" || echo "   Ice: not running (login item)"

echo ""
echo "🎉 Done!"
