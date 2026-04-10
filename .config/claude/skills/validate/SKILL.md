---
name: validate
description: "Product Validation ゲート。spec file の acceptance criteria に照らして実装を検証する。「正しいものを作っているか」を確認。/spike や /epd から呼び出し、または手動で使用。Triggers: '仕様通り？', 'validate', '検証して', 'spec に合ってる？', 'acceptance criteria'. Do NOT use for: コード品質レビュー（use /review）、テスト実行（use test-engineer agent）、セキュリティ検証（use security-reviewer agent）。"
allowed-tools: Read, Bash, Glob, Grep, Agent
user-invocable: true
metadata:
  pattern: reviewer
  version: 1.0.0
  category: quality
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

### UX Score Gate（UI 変更がある場合のみ）

以下のいずれかに該当する場合、ui-observer を Agent tool で起動して UX スコアを取得する:

1. spec に `ux_criteria` セクション、または「UI/UX」を含む acceptance criterion がある
2. 変更ファイルに `.tsx` / `.jsx` / `.vue` / `.svelte` / `.css` / `.html` が含まれる
3. ユーザーが明示的に UX 検証を要求

起動方法:

```
Agent(
  subagent_type: "ui-observer",
  prompt: "{feature_name} の UX Score Gate モードで実行してください。baseline は /tmp/ui-baseline/{feature}/、閾値は 7.0。UX Score Delta セクションを返してください。"
)
```

判定ルール:

- **overall >= 7.0**: ✅ Pass
- **overall < 7.0**: ❌ Fail（違反カテゴリを criterion の Evidence 列に記載）
- **カテゴリ別に 1つでも < 5.0**: ⚠️ Partial（局所的な重大問題あり）

### Feedback Loop（閉ループ）

UX Score Gate の結果は、次 iteration の spec プロンプトに注入できる形式で出力する:

```markdown
## Feedback for Next Iteration

**UX Score**: 6.4 / 10 (threshold: 7.0) ❌
**Failing Categories**: Flow (5), Error State (6)
**Priority Fixes**:
1. submit ボタン押下後のフィードバック追加
2. バリデーションエラー表示の文言改善

次の `/rpi` or `/epd` 呼び出しでこの Feedback を spec プロンプトに含めること。
```

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

| # | ❌ Don't | ✅ Do Instead |
|---|---------|--------------|
| 1 | spec file なしで validation を実行する | 必ず spec を特定してから検証する |
| 2 | コードの存在だけで Pass と判定する | 動作確認（テスト実行や実際の操作）で検証する |
| 3 | 全 criteria を一括で判定する | 1つずつ根拠を示して判定する |

## Skill Assets

- 検証レポートテンプレート: `templates/validation-report.md`
- criteria 抽出ガイド: `references/criteria-extraction.md`
