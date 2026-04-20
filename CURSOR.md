# Using this repo with Cursor

このリポジトリは Cursor で開くと、`.cursor/rules/global.mdc` が `alwaysApply: true` で自動適用される。Karpathy 4 原則を含む Core Principles は `global.mdc` に統合済みのため、追加インストールは不要。

## In this repository

- リポジトリのルートを Cursor で開く
- `.cursor/rules/global.mdc` が alwaysApply として効いていることを Cursor Settings → Rules で確認する
- 言語別ルール (`go.mdc`, `python.mdc`, `typescript.mdc` 等) は対応するファイルに応じて自動適用される

## Karpathy 4 原則の所在

Karpathy が X で指摘した LLM failure モードに対抗する 4 原則 (Think Before Coding / Simplicity First / Surgical Changes / Goal-Driven Execution) は以下に配置されている:

- **Cursor**: `.cursor/rules/global.mdc` の「Karpathy 4 原則」セクション
- **Claude Code (プロジェクト)**: `CLAUDE.md` の「1-4」節
- **Claude Code (グローバル)**: `~/.claude/CLAUDE.md` の Core Principles (同等概念を含む)
- **Codex**: `AGENTS.md` / `.codex/AGENTS.md` から `CLAUDE.md` を参照

4 原則の本体更新は `CLAUDE.md` と `.cursor/rules/global.mdc` の両方を同期すること。

## Use the same guidelines in another project

- **Cursor 推奨**: `.cursor/rules/global.mdc` を対象プロジェクトの `.cursor/rules/` にコピーまたは merge する
- **他ツール**: root の `CLAUDE.md` をコピー (または既存 instruction に merge)

## Claude Code vs Cursor

- **Claude Code**: `CLAUDE.md` (プロジェクト) + `~/.claude/CLAUDE.md` (グローバル) + `.config/claude/` 以下の skills / rules / agents で構成される
- **Cursor**: `.cursor/rules/*.mdc` のみ読む。`.claude-plugin/` や `CLAUDE.md` はデフォルトでは読まれない

## For contributors

Karpathy 4 原則を修正するときは以下を同期する:

1. `CLAUDE.md` (プロジェクト直下)
2. `.cursor/rules/global.mdc` の「Karpathy 4 原則」セクション
3. `AGENTS.md` / `.codex/AGENTS.md` のポインタが正しい参照を維持しているか確認
