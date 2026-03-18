# Worktree-Based Tasking

並列 task や長時間 task を安全に分離するときの playbook。

## When To Use

- 別 branch の作業を同時に進める
- Claude と Codex を別 task で並列に走らせる
- 破壊的ではないが生成物や formatter が衝突しやすい
- 実験的変更を main workspace と切り離したい
- 代替案を複数試し、promising なものだけ foreground に戻したい

## Standard Steps

1. ベース branch を確認する
2. `git worktree add ../<repo>-<task> -b <branch>` で専用 worktree を作る
3. Local を foreground、worktree を background の試行環境として役割分担する
4. その worktree で session を開始し、plan を作る
5. promising な試行だけ foreground に昇格し、task 完了後は branch を整理して不要な worktree を片付ける

## Example

```bash
git worktree add ../dotfiles-codex-mcp -b chore/codex-mcp-hardening
cd ../dotfiles-codex-mcp
task validate-configs
```

## Rules

- 1 task 1 worktree 1 session を基本にする
- plan と checkpoint は worktree ごとに管理する
- 同じファイル群を複数の live session で共有しない
- symlink や home 側へ影響する変更は、main workspace に戻る前に validation を通す
- main workspace は現在の判断と統合に使い、長時間の代替案や invasive な試行は worktree に寄せる
- 複数案を試すときは stash より worktree を優先し、attempt ごとの context を分離する

## Permission Notes

global settings で以下の git コマンドは allow から外れているため、実行時に承認ダイアログが表示される:

- `git checkout` — ブランチ切替は worktree 運用では不要。必要な場合は承認して実行する
- `git stash` — worktree で分離するため stash は基本不要。WIP 退避が必要なら承認して実行する
- `git remote` — `git remote -v` 等の確認も承認制。読み取り専用だが包括的な allow を避けている
- `git worktree add/remove` — 読み取り（`list`）のみ自動許可。作成・削除は承認制

## Minimum Validation

- `task validate-configs`
- `task validate-symlinks`
- 必要なら `task symlink`

## Cleanup

```bash
git worktree list
git worktree remove ../dotfiles-codex-mcp
```

worktree を remove する前に、未コミット変更がないことを確認する。
