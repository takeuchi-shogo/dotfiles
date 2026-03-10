---
name: codex-search-first
description: Research-before-editing workflow for Codex. Use when starting a new feature, adding a dependency, introducing a new script or utility, configuring MCP, or before creating a new abstraction in an unfamiliar area.
---

# Codex Search First

新しいコードや設定を書く前に、既存の script、task、skill、MCP、ドキュメントで解決できないかを先に確認する。

## Workflow

1. 追加しようとしているものを 1 文で定義する。
2. repo 内を `rg` / `rg --files` で調べる。
3. `Taskfile.yml`、`README.md`、最寄りの `AGENTS.md`、`.mcp.json`、`.agents/skills/` を確認する。
4. 既存の解決策があれば `adopt`、少し足りなければ `extend`、何もなければ `build` を選ぶ。
5. 非自明な場合だけ外部 docs や MCP を使う。

## Local Checklist

- 近い名前の task / script / config がないか
- 既存 skill で再利用できないか
- MCP で済むか
- tool 固有 README に既に運用ルールがないか
- 既存構造に 1 ファイル足すだけで済まないか

## Decision Rules

- 同じ問題を既に解いている file があるなら、まずそこに寄せる。
- 依存追加より既存 task / script 再利用を優先する。
- project-local skill があれば、global skill より先に使う。
- 新規 utility は、既存の command 組み合わせで代替できないことを確認してから作る。

## Anti-Patterns

- 既存 task を見ずに新しい script を増やす
- `.mcp.json` や `mcp_servers` を見ずに外部情報取得を自作する
- 同名・類似責務の file があるのに別名で増やす
