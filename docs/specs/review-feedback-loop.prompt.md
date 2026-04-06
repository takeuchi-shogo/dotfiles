---
title: Review Feedback Loop — レビュー指摘の精度追跡
status: draft
created: 2026-04-07
scope: M
research_source: docs/research/2026-04-07-hitl-asymmetric-evaluation-analysis.md
acceptance_criteria:
  - "AC-01: NEEDS_FIX/BLOCK の指摘ごとに accept/reject/partial を review-findings.jsonl に記録する"
  - "AC-02: カテゴリ別の false positive 率を算出できる（レビューアー × 重要度ラベル）"
  - "AC-03: meta-analyzer の Phase 1a で FP データを分析し、insights に精度レポートを含める"
  - "AC-04: accept_rate < 70% のレビューアーを改善候補として自動検出する"
  - "AC-05: 既存の Review-Fix サイクル（workflow-guide.md）を壊さない"
---

# Review Feedback Loop — Prompt-as-PRD

## Context

現在のレビューシステムは code-reviewer, codex-reviewer 等を並列起動し、指摘を統合して Verdict を出す。
しかし指摘の精度（false positive 率）を追跡する仕組みがなく、レビューアープロンプトの改善が
勘に依存している。

LayerX 澁井氏の HITL 非対称評価分析（2026-04）では、フィードバックループの構築が
評価精度の継続的改善に不可欠であると指摘されている。

既存の基盤:
- `review-findings.jsonl` が review 結果を記録（findings-to-autoevolve.py 経由）
- meta-analyzer が Evaluator 精度測定（タスク 5）を持つが、入力データが不足
- AutoEvolve の Phase 2 (Improve) がプロンプト改善提案を生成可能

## Problem Statement

1. **精度データの欠落**: レビュー指摘に対するユーザーの accept/reject が記録されていない
2. **改善根拠の不在**: どのレビューアーの、どのカテゴリの指摘が不正確かを定量的に判断できない
3. **フィードバック断絶**: Review-Fix サイクルでユーザーが修正した/しなかった情報が AutoEvolve に流れない

## Proposed Solution

Review-Fix サイクルの中で、ユーザーの修正行動を暗黙的に記録し、精度データとして蓄積する。

```
Review → NEEDS_FIX/BLOCK 指摘
  → ユーザーが修正を実施 → accept として記録
  → ユーザーが修正をスキップ → reject として記録
  → ユーザーが部分修正 → partial として記録
  → AutoEvolve Analyze → カテゴリ別 FP 率算出 → プロンプト改善提案
```

## Requirements

### Phase 1: データ収集基盤

| # | 要件 | 詳細 |
|---|------|------|
| R-01 | 指摘への応答記録 | Review-Fix サイクルで修正/スキップされた指摘を review-findings.jsonl に `outcome` フィールドとして追記 |
| R-02 | outcome フィールド定義 | `accept`（修正実施）, `reject`（修正スキップ）, `partial`（部分修正）, `deferred`（後で対応） |
| R-03 | 自動判定ロジック | 再レビュー時の diff を比較し、指摘箇所が変更されていれば `accept`、されていなければ `reject` |
| R-04 | 手動オーバーライド | ユーザーが明示的に「この指摘は誤り」と指定した場合は `reject` に上書き |

### Phase 2: 分析と可視化

| # | 要件 | 詳細 |
|---|------|------|
| R-05 | カテゴリ別 FP 率算出 | レビューアー × 重要度ラベル（MUST/CONSIDER）のマトリックスで false positive 率を算出 |
| R-06 | meta-analyzer 連携 | coverage-matrix.md にレビュー精度カテゴリを追加し、Phase 1a で自動分析 |
| R-07 | 改善候補の自動検出 | accept_rate < 70% のレビューアー × カテゴリを改善候補としてフラグ |
| R-08 | トレンド分析 | 直近 20 セッション vs 前 20 セッションの FP 率比較 |

### Phase 3: 改善サイクル接続

| # | 要件 | 詳細 |
|---|------|------|
| R-09 | AutoEvolve Improve 連携 | FP 率が高いレビューアーのプロンプト改善提案を Phase 2 (Improve) に入力 |
| R-10 | A/B テスト対応 | プロンプト改善後の精度変化を skill-benchmarks.jsonl で追跡 |

## Constraints

- **既存フロー非破壊**: Review-Fix サイクルのユーザー体験を変えない。追加の入力を求めない
- **暗黙的記録**: ユーザーの修正行動から自動推定。明示的なフィードバック UI は Phase 1 では作らない
- **データ最小量**: 有意な FP 率算出には各レビューアー 20 指摘以上が必要。それ以下は `INSUFFICIENT_DATA`
- **プライバシー**: 指摘内容のサマリーのみ記録。コード本体は記録しない

## Out of Scope

- レビューアープロンプトの自動修正（手動修正の入力データ提供のみ）
- リアルタイムの精度ダッシュボード UI
- 外部ツール（Datadog 等）へのメトリクス連携
- ユーザー間の精度データ共有

## Technical Notes

### データフロー

```
/review → verdict + findings
  → Review-Fix サイクル → 修正 diff を比較
  → findings-to-autoevolve.py で outcome フィールド付与
  → review-findings.jsonl に追記
  → meta-analyzer (タスク 5: Evaluator 精度測定) で分析
  → insights に精度レポート
  → AutoEvolve Improve で改善提案
```

### 変更対象ファイル

| ファイル | 変更種別 |
|----------|----------|
| `scripts/learner/findings-to-autoevolve.py` | outcome フィールド追加ロジック（既存 L1 接続ロジックとの責務分離を検討。別スクリプト `outcome-tracker.py` への分離も選択肢） |
| `skills/review/SKILL.md` | Review-Fix サイクルで outcome を記録する手順追加 |
| `agents/meta-analyzer.md` | タスク 5 の入力データに outcome を追加 |
| `skills/improve/references/coverage-matrix.md` | レビュー精度カテゴリ追加 |

### review-findings.jsonl スキーマ拡張

```json
{
  "session_id": "...",
  "reviewer": "code-reviewer",
  "file": "path/to/file.go",
  "line": 42,
  "severity": "MUST",
  "confidence": 92,
  "finding": "NullPointerException の可能性",
  "outcome": "accept",
  "outcome_source": "auto | manual"
}
```

## Open Questions

1. `partial` の判定基準: 指摘箇所が変更されたが指摘内容と異なる修正の場合、`accept` か `partial` か？
2. `deferred` の扱い: セッション跨ぎで後から修正された場合の追跡方法
3. confidence score と outcome の相関分析: 低 confidence の指摘は reject 率が高いはずだが、閾値調整に使えるか？
4. R-03 の diff 比較における偽陽性: 指摘行の移動・リネーム・周辺リファクタリングが accept と誤判定されるリスク。行コンテンツハッシュ比較 vs 行番号比較のどちらを採用するか？

## Prompt

このスペックに基づいて Phase 1（R-01 〜 R-04）を実装してください。

1. `findings-to-autoevolve.py` に outcome フィールドの追加ロジックを実装
2. Review-Fix サイクルの修正 diff を比較して accept/reject を自動判定
3. review-findings.jsonl のスキーマに outcome, outcome_source フィールドを追加
4. 既存の Review-Fix サイクルを壊さないことをテストで確認

Phase 2-3 は Phase 1 のデータ蓄積後に別セッションで実装します。
