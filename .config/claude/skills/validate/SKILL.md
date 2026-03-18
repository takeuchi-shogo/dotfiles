---
name: validate
description: "Product Validation ゲート。spec file の acceptance criteria に照らして実装を検証する。「正しいものを作っているか」を確認。/spike や /epd から呼び出し、または手動で使用。"
allowed-tools: Read, Bash, Glob, Grep, Agent
user-invocable: true
metadata:
  pattern: reviewer
---

# Validate: Product Validation Gate

spec file の acceptance criteria に照らして、実装が「正しいものを作っているか」を検証する。

## Workflow

1. spec file を特定する（引数 or 自動検出）
2. acceptance_criteria を抽出する
3. 各 criterion を1つずつ検証する
4. scope 外の機能が紛れ込んでいないか確認する
5. 検証レポートを出力する

## Spec File Detection

引数で spec ファイルパスが指定されていない場合:

1. `docs/specs/*.prompt.md` を検索
2. 直近の git diff で変更されたファイル名から feature 名を推定
3. 候補が複数ある場合はユーザーに選択を求める

## Validation Process

### acceptance_criteria の検証

各 criterion について:

1. **コード検証**: 該当機能が実装されているか、関連コードを検索
2. **動作検証**: テストがある場合は実行、webapp の場合は webapp-testing/ui-observer で確認
3. **判定**: ✅ Pass / ❌ Fail / ⚠️ Partial

### Scope Check

1. spec の Out of Scope に記載された項目が実装されていないか確認
2. spec の Requirements にない機能が追加されていないか確認
3. スコープ外の変更がある場合は ⚠️ Warning として報告

### Context Validation

1. spec の Context（ユーザー課題）に照らして、実装が課題を解決しているか判断
2. ユーザーの操作フローが自然かを評価

## Output Format

```
## Validation Report

**Spec**: docs/specs/{feature}.prompt.md
**Status**: ✅ PASS / ❌ FAIL / ⚠️ PARTIAL

### Acceptance Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | ...       | ✅     | ...      |
| 2 | ...       | ❌     | ...      |

### Scope Check
- ✅ No scope creep detected
  or
- ⚠️ Scope creep: [description]

### Summary
[1-2 sentences: 全体の判定と次のアクション]
```

## Anti-Patterns

- spec file なしで validation を実行する（必ず spec が必要）
- コードの存在だけで Pass と判定する（動作確認が必要）
- 全 criteria を一括で判定する（1つずつ根拠を示す）

## Skill Assets

- 検証レポートテンプレート: `templates/validation-report.md`
- criteria 抽出ガイド: `references/criteria-extraction.md`
