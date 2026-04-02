---
name: spike
description: >
  プロトタイプファースト開発。worktree で隔離し、最小実装 → Product Validation まで行う。
  Triggers: '試してみたい', 'プロトタイプ', 'POC', 'proof of concept', 'まず動かしてみる',
  'spike', '実験', 'feasibility', 'これって可能？', 'quick test'.
  Do NOT use when spec is clear and ready for production — use /rpi or /epd instead.
  テスト・lint 不要。
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, EnterWorktree
user-invocable: true
metadata:
  pattern: pipeline
  version: 1.0.0
  category: workflow
---

# Spike: Prototype-First Development

アイデアを素早くプロトタイプ化し、Product Validation（acceptance criteria 照合）まで行う。
テスト・lint は不要。目的は「正しいものを作っているか」の検証。

## Workflow

```
/spike {idea or feature name}
  1. Spec Check    → docs/specs/ に spec があるか確認
  2. Spec Create   → なければ /spec を実行して生成
  3. Isolate       → worktree で隔離環境を作成
  4. Implement     → 最小実装（動くことが最優先）
  5. Validate      → /validate で acceptance criteria を照合
  6. Report        → 結果をまとめて報告
  7. Record        → Abandon の場合は失敗記録を保存
```

## Step 1-2: Spec Check / Create

1. `docs/specs/{feature}.prompt.md` を検索
2. 存在しなければ、spec スキルを呼び出して生成する
3. spec の Prompt セクションを実装の入力として使用する

## Step 3: Isolate

worktree を使用してメインブランチから隔離する:

1. EnterWorktree ツールで `spike/{feature}` ブランチを作成
2. または Agent ツールの `isolation: "worktree"` を使用

## Step 4: Implement

### ベースライン選定原則 (Meta-Harness Tip)

意図的に「苦戦するベースライン」から始める:

- **シンプルに始める**: few-shot プロンプティング等の最小構成をベースラインにする
- **discriminative な評価セット**: 改善のシグナルが検出できる程度に小さく、かつ差が出る問題を選ぶ
- **ベースラインが完璧なら spike 不要**: ベースラインが acceptance criteria を満たすなら、そのまま `/rpi` に進む

> 根拠: Meta-Harness (Lee+ 2026) — "Start with a baseline that struggles. Keep the search set small enough for roughly ~50 full evaluations per run"

### 実装ルール

- **動くことが最優先**: コード品質は二の次
- **テスト不要**: spike のコードは捨てる前提
- **lint 不要**: フォーマットは気にしない
- **最小限**: spec の Requirements を満たす最小コード
- **ハードコード可**: 設定値等は直書きでOK

## Step 5: Validate

validate スキルを呼び出して acceptance criteria を検証する。

## Step 6: Report

以下のフォーマットで結果を報告:

```
## Spike Report: {feature}

**Spec**: docs/specs/{feature}.prompt.md
**Branch**: spike/{feature}
**Validation**: ✅ PASS / ❌ FAIL / ⚠️ PARTIAL

### Findings
- 実装で分かったこと
- 想定と違ったこと
- 技術的な課題や制約

### Recommendation
- ✅ Proceed: 正式実装に進む（/rpi を使用）
- 🔄 Pivot: アプローチを変更して再 spike
- ❌ Abandon: この機能は見送り
```

## After Spike

- **Proceed**: worktree のコードは参考として残す。正式実装は `/rpi` で新たに行う
- **Pivot**: spec を更新して再度 `/spike`
- **Abandon**: 失敗の学習を記録してから worktree を削除

### Negative Results の記録（Abandon 時は必須）

失敗した実験でも学びは資産。以下のテンプレートで `docs/spikes/{feature}-abandoned.md` に記録する:

```markdown
# Spike: {feature} — Abandoned

**Date**: YYYY-MM-DD
**Spec**: docs/specs/{feature}.prompt.md
**Branch**: spike/{feature}（削除済み）

## What We Tried
- 試したアプローチの概要

## Why It Didn't Work
- 失敗の根本原因（技術的制約、パフォーマンス、ユーザビリティ等）

## What We Learned
- 今後に活かせる知見
- 避けるべきアプローチ

## Alternatives Considered
- 検討したが試さなかった代替案（次回の参考に）
```

spec の status を `abandoned` に更新し、worktree を削除する。

## Anti-Patterns

| # | ❌ Don't | ✅ Do Instead |
|---|---------|--------------|
| 1 | spike のコードをそのまま本番に持ち込む | `/rpi` で正式実装する |
| 2 | テストやリファクタリングに時間をかける | spike は検証が目的。動けば十分 |
| 3 | spec なしで spike する | 先に `/spec` で何を検証するか明確にする |
| 4 | 長時間の spike を行う | 30分以内の作業量に収める |

## Reference Files

- `templates/spike-scaffold.md` — spike 開始時にコピーして使うテンプレート

## Skill Assets

- スパイクレポートテンプレート: `templates/spike-report.md`
- スキャフォールドテンプレート: `templates/spike-scaffold.md` (既存)
