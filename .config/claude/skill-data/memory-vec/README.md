# memory-vec runtime

agent-memory + Obsidian Vault 記事を埋め込みインデックス化し、意味検索でオンデマンド参照するためのランタイム。

- `reindex.ts` — `index.db` をフル再構築（DROP→CREATE→全 md を redact→embed）。stop-hook が `index.db` の mtime < ソース md の mtime のとき background 起動する。
- `query.ts` — クエリを embed して KNN 検索。`recall` skill / SessionStart hint hook が呼ぶ。
- `lib/memory_redactor.py` — embed 前に秘匿情報を redact（`.config/claude/scripts/lib/redactor.py` と重複の疑いあり。統合は別タスク）。

呼び出し元は `~/.claude/scripts/runtime/memory-vec-{stop,hint}-hook.py`（`node <path>` を直接実行。`pnpm run` は経由しない）。

## デプロイ（nix home-manager）

ソース（`*.ts` / `package.json` / `pnpm-lock.yaml` / `lib/memory_redactor.py`）は dotfiles git 管理下にあり、`nix/home/default.nix` の `outLink`（mkOutOfStoreSymlink）で個別ファイル symlink される。`node_modules/` と `index.db` は生成物（gitignore）で、このディレクトリ内にローカル実体として共存する。

## 新規 PC セットアップ

1. `task nix:switch` — ソース 5 ファイルが `~/.claude/skill-data/memory-vec/` に symlink される。
2. `cd ~/.claude/skill-data/memory-vec && pnpm install` — `node_modules/`（gitignore）を再現。
3. 初回 reindex は stop-hook が自動起動する（または `pnpm run reindex` で手動）。

## 一回限りの移行注意（このリポジトリを既に未管理運用していたマシンのみ）

ソースが未バージョン管理（実ファイル）だったマシンでは、初回 `nix:switch` の**前に**既存実体を削除すること（home-manager が既存実ファイルと symlink で衝突するため）:

```bash
cd ~/.claude/skill-data/memory-vec
rm reindex.ts query.ts package.json pnpm-lock.yaml lib/memory_redactor.py
# node_modules/ と index.db は残す（生成物）
task nix:switch   # ~/dotfiles で実行
```

新規 PC では実体が存在しないため、この削除は不要。
