---
name: search-first
description: >
  Research-before-coding workflow. Search for existing tools, libraries, and patterns
  before writing custom code. Use when starting a new feature, adding a dependency,
  or before creating a new utility. Do NOT use for known bugs with clear fixes
  or simple typo corrections.
allowed-tools: "Read, Bash, Grep, Glob, Agent"
metadata:
  pattern: pipeline
---

# /search-first — 実装前に検索する

コードを書く前に既存の解決策を探す。CLAUDE.md の「検索してから実装」原則を実行するワークフロー。

## チェックリスト

新しいユーティリティ・機能・依存を追加する前に:

1. **パッケージ検索**: npm/PyPI/go pkg に既存ライブラリがあるか
2. **MCP 確認**: `settings.json` の MCP サーバーが機能を提供していないか
3. **スキル確認**: `~/.claude/skills/` に既存スキルがないか
4. **コードベース確認**: プロジェクト内に類似実装がないか

## 判断基準

| シグナル | アクション |
|---------|-----------|
| 完全一致、メンテ良好 | **Adopt** — そのまま採用 |
| 部分一致 | **Extend** — 採用 + 薄いラッパー |
| 適切なものなし | **Build** — 自作（調査結果を踏まえて） |

## Reference Files

- `references/strategies.md` — 検索戦略の詳細ガイド
