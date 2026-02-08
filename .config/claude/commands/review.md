---
allowed-tools: Bash(git diff *), Bash(git log *), Bash(git status *)
description: Review recent code changes for quality and security
---

# Smart Code Review

Review code changes: $ARGUMENTS

## Current Repository State

- Git status: !`git status --porcelain`
- Current branch: !`git branch --show-current`
- Staged changes: !`git diff --cached --stat`
- Unstaged changes: !`git diff --stat`

## What This Command Does

1. 引数なし: unstaged + staged の変更をレビュー
2. ブランチ名指定: 現在のブランチとの diff をレビュー（例: `/review main`）
3. コミットハッシュ指定: 特定コミットの変更をレビュー
4. `git diff` で変更内容を取得し、以下のチェックリストで評価

## Review Checklist

### Critical (必ず確認)
- セキュリティ脆弱性（XSS, SQL Injection, コマンドインジェクション等）
- 機密情報のハードコード（API キー、パスワード、トークン）
- データ損失のリスク（破壊的操作、バックアップなし）

### Warning (重要)
- エラーハンドリングの不足
- パフォーマンスの問題（N+1クエリ、不要なループ等）
- 型安全性の問題
- テストカバレッジの不足

### Suggestion (改善提案)
- コードの可読性
- 命名規則の一貫性
- DRY 原則の違反
- ドキュメントの不足

## Output Format

各指摘を優先度別に分類して表示:

```
🔴 Critical: [説明]
  ファイル:行番号 — 具体的な問題と修正案

🟡 Warning: [説明]
  ファイル:行番号 — 具体的な問題と修正案

🔵 Suggestion: [説明]
  ファイル:行番号 — 改善提案
```

問題がなければ "LGTM" と表示。
