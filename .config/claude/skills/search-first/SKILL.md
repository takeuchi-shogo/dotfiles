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

チェックリストで見つけた候補を以下の品質シグナルで評価し、Adopt / Extend / Build を決定する。

### 品質シグナル（全候補に適用）

| シグナル | Go（Adopt 可） | Caution（要検討） |
|---------|----------------|-------------------|
| メンテナンス | 直近3ヶ月以内にリリース | 1年以上更新なし |
| 依存数 | 少ない（<10） | 依存ツリーが深い（>50） |
| ライセンス | MIT / Apache 2.0 / BSD | GPL（伝播注意）/ SSPL |
| 型定義（TS） | 同梱 or @types あり | 型なし |
| テスト / CI | CI バッジあり、カバレッジ公開 | テストなし |

### 判定フロー

1. **Adopt** — 要件に完全一致 AND 品質シグナルが全て Go → そのまま採用
2. **Extend** — 要件に部分一致 OR Caution が1-2個だが許容可能 → 採用 + 薄いラッパーで不足を補う
3. **Build** — 候補なし OR Caution が3個以上 → 自作（調査で得た設計知見を活用）

## Reference Files

- `references/strategies.md` — 検索戦略の詳細ガイド
