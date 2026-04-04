# Temporal Decay Policy

> Source: context-and-impact リポジトリの Temporal Decay 知見に基づく

## 概要

コンテキスト（メモリファイル、ドキュメント）の鮮度を定量的に評価するポリシー。
エージェントが複数ソースを参照する際、古い情報に過度に依存しないための判断基準を提供する。

## 数式

```
freshness_score = exp(-0.1 * days_since_update)
```

- `days_since_update` = 現在日 - ファイルの最終更新日（日数）

## 閾値テーブル

| 状態   | スコア範囲  | 目安日数   | アクション                               |
| ------ | ----------- | ---------- | ---------------------------------------- |
| Fresh  | >= 0.50     | ~7日以内   | そのまま使用                             |
| Aging  | 0.05 - 0.49 | 7-30日     | 内容を確認してから使用                   |
| Stale  | < 0.05      | 30日超     | 更新 or 削除を検討                       |

## 計算例

10日前に更新されたファイル:

```
freshness_score = exp(-0.1 * 10) = exp(-1.0) = 0.368 → Aging
```

アクション: 内容が現状と一致するか確認してから使用する。

## 適用先

1. **`/check-health` スキル**: メモリファイルの鮮度チェックに使用。Stale なファイルを警告として報告する
2. **エージェントのコンテキスト収集**: 複数ソースからコンテキストを集める際の重み付け。freshness_score が低いソースは信頼度を下げる

## 重要度加重 (Importance Weighting)

メモリの重要度に応じて鮮度スコアを調整する:

```
effective_score = freshness_score * importance_weight
```

### 重要度テーブル

| メモリ type  | importance_weight | 理由                           |
| ------------ | ----------------- | ------------------------------ |
| feedback     | 1.0               | ユーザー修正は最重要           |
| user         | 0.8               | プロファイルは中長期安定       |
| project      | 0.6               | プロジェクト状況は変動大       |
| reference    | 0.5               | 外部リソースは検証コスト高     |

### 適用例

feedback メモリ (5日前更新):

```
effective_score = exp(-0.1 * 5) * 1.0 = 0.607 → Fresh
```

reference メモリ (5日前更新):

```
effective_score = exp(-0.1 * 5) * 0.5 = 0.303 → Aging（確認推奨）
```

### 消費先

1. `scripts/learner/memory-eviction.py` — メモリ淘汰候補のスコアリングに使用
2. `scripts/learner/staleness-detector.py --memory` — メモリ鮮度レポートの重み付けに使用

## 注意事項

- このポリシーは自動化スクリプトではなく、エージェントが判断する際の **ガイドライン** である
- 頻繁に更新されないが普遍的な内容（設計原則等）は、スコアが低くても有効な場合がある。機械的に適用せず文脈を考慮すること
- feedback タイプは重要度最高のため、eviction 対象外として保護される
