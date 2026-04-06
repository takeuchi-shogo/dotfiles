---
title: Review Feedback Loop — レビュー指摘の精度追跡
status: draft
created: 2026-04-07
updated: 2026-04-07
scope: M
research_source: docs/research/2026-04-07-hitl-asymmetric-evaluation-analysis.md
acceptance_criteria:
  - "AC-01: NEEDS_FIX/BLOCK の指摘ごとに accept/reject/partial を review-findings.jsonl に記録する"
  - "AC-02: /review 後にユーザーへ明示的な accept/reject 確認を行う"
  - "AC-03: 再レビュー時の diff 比較で暗黙的に accept/reject を自動判定する"
  - "AC-04: カテゴリ別の false positive 率を算出できる（レビューアー × 重要度ラベル）"
  - "AC-05: meta-analyzer の Phase 1a で FP データを分析し、insights に精度レポートを含める"
  - "AC-06: accept_rate < 70% のレビューアーを改善候補として自動検出する"
  - "AC-07: AutoEvolve Phase 2 が改善提案を生成し、ユーザー承認ゲートを通過して適用する"
  - "AC-08: 既存の Review-Fix サイクル（workflow-guide.md）を壊さない"
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

## Product Spec

- `/review` 完了後、NEEDS_FIX/BLOCK の指摘一覧が表示される
- ユーザーに「この指摘を受け入れますか？」と確認し、指摘ごとに accept/reject/partial を選択できる
- ユーザーが明示的に回答しなかった指摘は、再レビュー時の diff 比較で自動判定される
- `/improve` 実行時、FP 率が高いレビューアー×カテゴリの改善提案が表示される
- 改善提案はユーザーの承認を経てプロンプトに適用される（自動適用はしない）

## Tech Spec

### データモデル

`review-findings.jsonl` スキーマ拡張:

```json
{
  "session_id": "...",
  "reviewer": "code-reviewer",
  "file": "path/to/file.go",
  "line": 42,
  "severity": "MUST",
  "confidence": 92,
  "finding": "NullPointerException の可能性",
  "outcome": "accept | reject | partial | deferred",
  "outcome_source": "explicit | auto_diff",
  "outcome_timestamp": "2026-04-07T10:30:00Z"
}
```

### データフロー

```
/review → verdict + findings
  ├─ 明示的フロー (Phase 1A):
  │   → findings 表示 → AskUserQuestion で accept/reject 確認
  │   → outcome: explicit として review-findings.jsonl に記録
  │
  └─ 暗黙的フロー (Phase 1B):
      → Review-Fix サイクル → 修正 diff を比較
      → 指摘箇所が変更 → accept (auto_diff)
      → 指摘箇所が未変更 → reject (auto_diff)
      → 部分変更 → partial (auto_diff)

  明示的フロー優先: explicit が記録済みの指摘は auto_diff で上書きしない

  → meta-analyzer (タスク 5: Evaluator 精度測定) で分析
  → insights に精度レポート
  → AutoEvolve Improve で改善提案生成
  → ユーザー承認ゲート → プロンプト適用
```

### 主要な技術判断

- **明示的 + 暗黙的の二重記録**: 明示的回答が最も信頼性が高いが、全指摘への回答はユーザー負荷が大きい。暗黙的 diff 比較を補完として使い、明示的回答を優先する
- **プロンプト自動適用はしない**: FP 率に基づく改善提案は生成するが、適用はユーザー承認ゲートを通す。レビュー品質の劣化リスクを人間が管理する
- **既存 JSONL への追記**: 新規ストレージは作らない。review-findings.jsonl に outcome フィールドを追加するだけ

## Requirements

### Phase 1: データ収集基盤

| # | 要件 | 詳細 |
|---|------|------|
| R-01 | 明示的フィードバック | /review 完了後、NEEDS_FIX/BLOCK の指摘リストを表示し、各指摘に accept/reject/partial を確認 |
| R-02 | 暗黙的フィードバック | 再レビュー時の diff を比較し、指摘箇所が変更されていれば accept、されていなければ reject |
| R-03 | outcome フィールド定義 | `accept`（修正実施/妥当と認めた）, `reject`（誤検知/修正不要）, `partial`（部分修正）, `deferred`（後で対応） |
| R-04 | outcome_source 記録 | `explicit`（ユーザーが明示回答）, `auto_diff`（diff 比較で自動判定） |
| R-05 | 明示的優先ルール | explicit が記録済みの指摘は auto_diff で上書きしない |

### Phase 2: 分析と可視化

| # | 要件 | 詳細 |
|---|------|------|
| R-06 | カテゴリ別 FP 率算出 | レビューアー × 重要度ラベル（MUST/CONSIDER）のマトリックスで false positive 率を算出 |
| R-07 | meta-analyzer 連携 | タスク 5 の入力データに outcome を追加 |
| R-08 | 改善候補の自動検出 | accept_rate < 70% のレビューアー × カテゴリを改善候補としてフラグ |
| R-09 | トレンド分析 | 直近 20 セッション vs 前 20 セッションの FP 率比較 |

### Phase 3: 改善サイクル接続

| # | 要件 | 詳細 |
|---|------|------|
| R-10 | AutoEvolve Improve 連携 | FP 率が高いレビューアーのプロンプト改善提案を Phase 2 (Improve) で自動生成 |
| R-11 | ユーザー承認ゲート | 改善提案をユーザーに提示し、承認を得てからプロンプトに適用する |
| R-12 | A/B テスト対応 | プロンプト改善後の精度変化を skill-benchmarks.jsonl で追跡 |

## Constraints

- **既存フロー非破壊**: Review-Fix サイクルの基本フローを変えない
- **明示的確認は低負荷に**: 一覧表示 + バッチ回答で、1 指摘ずつの逐一確認は避ける
- **データ最小量**: 有意な FP 率算出には各レビューアー 20 指摘以上が必要。それ以下は `INSUFFICIENT_DATA`
- **プライバシー**: 指摘内容のサマリーのみ記録。コード本体は記録しない
- **新規ストレージ不要**: 既存の review-findings.jsonl にフィールド追加のみ

## Extensibility Checkpoint

- 新しい outcome タイプの追加: outcome フィールドの enum に値を追加するだけ。解析ロジックの変更箇所は 1（FP 率算出の分母/分子定義）
- 新しいレビューアーの追加: reviewer フィールドで自動的に集計対象になる。変更箇所 0
- confidence 閾値の動的調整: FP 率データから confidence 閾値を算出するロジックを Phase 3 以降で追加可能

## Out of Scope

- リアルタイムの精度ダッシュボード UI
- 外部ツール（Datadog 等）へのメトリクス連携
- ユーザー間の精度データ共有
- confidence score の自動閾値調整（Phase 3 以降の拡張候補）

## Open Questions

1. **partial の判定基準**: 指摘箇所が変更されたが指摘内容と異なる修正の場合、accept か partial か？
2. **deferred の追跡**: セッション跨ぎで後から修正された場合の追跡方法
3. **diff 比較の偽陽性**: 指摘行の移動・リネーム・周辺リファクタリングが accept と誤判定されるリスク。行コンテンツハッシュ比較 vs 行番号比較のどちらを採用するか？
4. **明示的確認の UX**: 指摘が 10 件以上ある場合、全件確認はユーザー負荷が高い。MUST のみ確認 + CONSIDER は auto_diff に委ねる方式を検討するか？

## Technical Notes

### 変更対象ファイル

| ファイル | 変更種別 |
|----------|----------|
| `scripts/learner/findings-to-autoevolve.py` | outcome フィールド追加ロジック |
| `skills/review/SKILL.md` | Review 完了後の明示的確認フロー追加 |
| `agents/meta-analyzer.md` | タスク 5 の入力データに outcome を追加 |
| `skills/improve/references/coverage-matrix.md` | レビュー精度カテゴリ追加 |

## Prompt

このスペックに基づいて Phase 1（R-01 〜 R-05）を実装してください:

1. `skills/review/SKILL.md` に Review 完了後の明示的フィードバック確認フローを追加
   - NEEDS_FIX/BLOCK 指摘を一覧表示し、accept/reject/partial をバッチで確認
   - 回答結果を review-findings.jsonl に outcome (explicit) として記録
2. `findings-to-autoevolve.py` に暗黙的 diff 比較ロジックを追加
   - 再レビュー時の diff から指摘箇所の変更有無を判定
   - explicit が未記録の指摘のみ auto_diff で outcome を付与
3. review-findings.jsonl のスキーマに outcome, outcome_source, outcome_timestamp を追加
4. 既存の Review-Fix サイクルを壊さないことを確認

Phase 2-3 は Phase 1 のデータ蓄積後に別セッションで実装します。
