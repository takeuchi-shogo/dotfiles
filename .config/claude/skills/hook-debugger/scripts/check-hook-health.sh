#!/usr/bin/env bash
# Hook health check — 登録された hook の状態を一覧表示
set -euo pipefail

SETTINGS_FILES=(
    "$HOME/.claude/settings.json"
    "$HOME/.claude/settings.local.json"
)

echo "=== Hook Registration Status ==="
echo ""

for f in "${SETTINGS_FILES[@]}"; do
    if [[ -f "$f" ]]; then
        echo "📄 $f"
        python3 -c "
import json, sys
with open('$f') as fh:
    data = json.load(fh)
hooks = data.get('hooks', {})
if not hooks:
    print('  (no hooks)')
else:
    for event, entries in hooks.items():
        print(f'  {event}: {len(entries)} hook(s)')
        for e in entries:
            matcher = e.get('matcher', '(all)')
            for h in e.get('hooks', []):
                cmd = h.get('command', h.get('prompt', '(prompt)'))[:60]
                print(f'    - [{matcher}] {cmd}')
" 2>/dev/null || echo "  (parse error)"
        echo ""
    fi
done

echo "=== Script Permission Check ==="
echo ""
find "$HOME/.claude/scripts" -name "*.py" -o -name "*.sh" -o -name "*.js" 2>/dev/null | while read -r script; do
    if [[ -x "$script" ]]; then
        echo "  ✅ $script"
    else
        echo "  ⚠️  $script (not executable)"
    fi
done
