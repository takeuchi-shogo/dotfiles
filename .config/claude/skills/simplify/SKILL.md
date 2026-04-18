---
name: simplify
description: >
  Review changed code for reuse, quality, and efficiency, then fix any issues found.
  並列レビューアーを起動し、重複ロジック・過度なネスト・非効率クエリ・再利用機会を検出。
  コード変更後の品質チェック、または手動で /simplify で起動。
  Triggers: '/simplify', 'simplify', 'コード簡素化', 'DRY チェック', '重複検出', 'reduce complexity'.
  Do NOT use for: アーキテクチャレビュー（use /review）、セキュリティ検証（use security-reviewer agent）。
origin: self
allowed-tools: Read, Edit, Write, Bash, Glob, Grep, Agent
metadata:
  pattern: orchestrator
---

# /simplify — Code Simplification Review

## Trigger

`/simplify` で手動起動、またはコード変更後の品質チェックとして使用。

## Workflow

1. **Scope 特定** — `git diff --name-only` で変更ファイルを取得
2. **並列レビュー起動** — 変更規模に応じてレビューアーを選択
3. **結果統合** — 検出結果をカテゴリ別に整理
4. **修正提案** — ユーザー確認後に修正を適用

## Step 1: Scope 特定

```bash
git diff --name-only HEAD  # unstaged changes
git diff --cached --name-only  # staged changes
```

引数でファイルパスが指定された場合はそれを使用。

## Step 2: 並列レビュー

変更規模に応じてレビューアーを起動:

| 変更規模 | レビューアー |
|---------|-------------|
| 1-3 ファイル | code-simplifier agent のみ |
| 4-10 ファイル | code-simplifier + cross-file-reviewer を並列 |
| 10+ ファイル | 上記 + edge-case-hunter を並列 |

各レビューアーには `references/simplification-rules.md` の検出ルールを注入する。

## Step 3: 検出カテゴリ

`references/simplification-rules.md` に定義された以下のカテゴリで報告:

1. **DRY 違反** — 同一/類似パターンの重複
2. **Nesting** — 過度な条件分岐のネスト
3. **Complexity** — 関数の認知的複雑度
4. **Reuse** — ユーティリティ関数化の候補
5. **Query** — N+1 問題、非効率なデータアクセス

## Step 4: 出力形式

```
## Simplification Report

### 🔴 Must Fix (品質基準違反)
- [file:line] category — description — suggested fix

### 🟡 Should Fix (改善推奨)
- [file:line] category — description — suggested fix

### 🔵 Consider (検討事項)
- [file:line] category — description — rationale

### Summary
- Issues found: N (must: X, should: Y, consider: Z)
```

## Step 5: 修正

- Must Fix は自動修正を提案（ユーザー確認後に適用）
- Should Fix / Consider は報告のみ（`--fix` オプションで自動修正可）

## Anti-Patterns

- 変更していないファイルをレビュー対象にしない（スコープクリープ防止）
- 3行以内の類似コードを DRY 違反として報告しない（過度な抽象化は YAGNI 違反）
- パフォーマンスを理由にした複雑化を提案しない（計測データなしの最適化は禁止）
