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

4. checkpoint 保存後、以下のテンプレートに従い HANDOFF.md を生成する

**配置先の決定:**
- worktree 内の場合: worktree ルートに `HANDOFF.md`
- 通常の場合: `tmp/HANDOFF.md`（リポジトリルートの tmp/）

**HANDOFF.md テンプレート:**

変更されたファイル一覧は `git diff --name-only HEAD` と `git status --porcelain` から取得する。

```markdown
# HANDOFF

> Generated: {現在のISO日時}

## Goal

{現在のタスクの目的を1-2文で}

## Progress

- [x] {完了した作業項目}
- [ ] {未完了の作業項目}

## What Worked

- {うまくいったアプローチ・判断}

## What Didn't Work

- {試して失敗したこと・避けるべきこと}（なければ「特になし」）

## Next Steps

1. {次にやるべきこと}
2. {その次にやるべきこと}

## Context Files

{`git diff --name-only HEAD` と `git status --porcelain` の結果から関連ファイルをリスト}
```

5. 生成結果をユーザーに報告（ファイルパスと内容サマリ）
