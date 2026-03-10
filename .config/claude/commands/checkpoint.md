現在の作業状態を手動で checkpoint として保存してください。

以下の手順で実行:

1. `~/.claude/session-state/edit-counter.json` から現在の編集カウントを取得
2. checkpoint を保存
3. 保存結果をユーザーに報告

実行コマンド:

```bash
python3 -c "
import sys; sys.path.insert(0, '$HOME/.claude/scripts')
from checkpoint_manager import save_checkpoint, _read_counter
counter = _read_counter()
path = save_checkpoint(trigger='manual', edit_count=counter.get('count', 0))
print(f'Checkpoint saved: {path}')
"
```
