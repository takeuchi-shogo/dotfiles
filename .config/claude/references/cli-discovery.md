---
status: reference
last_reviewed: 2026-04-23
---

# CLI Discovery Policy

## 発見順序

1. **CLI `--help`**: 新しいツールを使う前に必ず `--help` を確認する
2. **Skills**: Claude Code スキルで対応できるか確認する (`/skill-name`)
3. **MCP**: 専用 MCP server が存在するか確認する

## 理由

Progressive Disclosure 設計: 詳細は必要になったときだけ露出する。
CLI は最も軽量で副作用のない探索手段。

## 例

```bash
# Good: まず help を見る
gh --help
gh pr --help

# Good: サブコマンド発見後に実行
gh pr list --state open
```
