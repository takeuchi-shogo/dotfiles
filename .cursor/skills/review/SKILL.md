---
name: review
description: コード変更のレビューを実行する。品質・セキュリティ・複雑度をチェックし、severity 付きで報告する。コード変更後に使用。
---

# Code Review Skill

## When to Use

- コード変更後のレビュー
- PR 作成前の品質確認
- リファクタリング後の検証

## Workflow

1. `git diff` で変更を取得（unstaged + staged）
2. 変更規模を判定:
   - **S** (1-30行): 簡易チェック（品質のみ）
   - **M** (31-100行): 品質 + セキュリティ
   - **L** (101行+): 全軸レビュー + reviewer サブエージェントに委譲
3. 変更ファイルの元のコードを読み、差分のコンテキストを理解する
4. チェック項目:
   - **品質**: 複雑度増加、命名規約、DRY 違反、エラーハンドリング
   - **セキュリティ**: 入力検証、秘密情報、注入攻撃パターン
   - **テスト**: 変更に対応するテストの有無、カバレッジ
5. 発見事項を severity 付きで報告:
   - 🔴 **Critical**: 修正必須（セキュリティ、データ損失リスク）
   - 🟡 **Warning**: 修正推奨（品質劣化、複雑度増加）
   - 🔵 **Info**: 改善提案（命名、構造）

## Output Format

```
## Review Report

### Summary
- Files changed: N
- Lines added/removed: +X/-Y
- Severity: N critical, N warning, N info

### Findings
#### 🔴 Critical
- [file:line] Description

#### 🟡 Warning
- [file:line] Description

#### 🔵 Info
- [file:line] Description
```
