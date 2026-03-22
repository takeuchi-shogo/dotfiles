# Resource Evaluations

外部知見（記事・論文・ツール等）の初期トリアージ。`/absorb` の前段として5分以内で評価し、統合判断を記録する。

## 評価基準

| 指標 | 観点 | 1 | 3 | 5 |
|------|------|---|---|---|
| **Relevance** | 現在の dotfiles/harness に関係するか | 無関係 | 間接的に有用 | 直接適用可能 |
| **Novelty** | 既存セットアップにない知見か | 既知 | 部分的に新規 | 完全に新規 |
| **Actionability** | 具体的な変更に落とせるか | 概念のみ | 一部実装可能 | すぐ実装可能 |

## スコア解釈

| 合計スコア | 判定 | アクション |
|-----------|------|-----------|
| 12-15 | 高優先 | 即 `/absorb` 実行 |
| 8-11 | 検討 | Gap Analysis 精査後に判断 |
| 4-7 | 低優先 | バックログに記録、後日再評価 |
| 3 | スキップ | `status: skipped` で閉じる |

## ワークフロー

1. リソース発見
2. `_template.md` をコピーして `YYYY-MM-DD-{slug}.md` で作成
3. 5分以内で3指標スコアリング + Gap Analysis テーブル記入
4. 合計8以上 → `/absorb` 実行 → `status: absorbed` に更新
5. `/absorb` 結果は `docs/research/` に詳細レポートとして出力

## 既存リソースとの関係

| 場所 | 役割 |
|------|------|
| `docs/resource-evaluations/` | 初期評価 + 統合判断の記録（本ディレクトリ） |
| `docs/research/` | `/absorb` 実行結果の詳細分析レポート（移行不要） |
| `MEMORY.md` | 統合済みリソースのサマリ索引 |

## カテゴリ

`article` / `paper` / `tool` / `repo` / `video`

## インデックス

> 既存52件（`docs/research/` + MEMORY.md 記載分）は移行不要。新規評価分のみ追記する。

| Date | Resource | Category | Score | Status |
|------|----------|----------|-------|--------|
