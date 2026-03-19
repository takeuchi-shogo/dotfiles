---
source: "autocontext: The Recursive Self-Improving Loop (greyhaven-ai/autocontext)"
date: 2026-03-19
status: integrated
---

## Source Summary

**主張**: エージェントのコンテキストウィンドウは金魚の脳。run をまたいだ知識蓄積がなく、毎回同じ失敗を繰り返す。autocontext はこの欠落したフィードバックループを提供する閉ループ最適化システム。

**手法**:
- マルチエージェントパイプライン（Competitor→Translator→Analyst→Coach→Architect→Curator、Orchestrator が統括）
- Playbook — 世代を超えて成長する生きたナレッジベース
- Elo ベースの進歩ゲーティング（Tournament matches でスコアが改善しなければロールバック）
- Multi-dimensional rubrics による LLM Judge 評価（次元ごとに独立スコア→最弱次元を狙い撃ち）
- 4層フォールバックパーサー（marker-delimited JSON → raw JSON → regex → structured retry）
- Frontier-to-Local 蒸留（MLX on Apple Silicon でローカルモデルを学習）
- ドメイン非依存シナリオフレームワーク（Game scenarios + Agent tasks）
- Natural language task creation（自然言語→仕様→ルブリック→実行ループを自動生成）
- MCP サーバー統合（autoctx mcp-serve）

**根拠**: grid_ctf シナリオで 2 世代 33 lessons 蓄積、5,870 chars の playbook。Adversarial validation テスト通過（hallucination テストで fabricated claims が全次元 0 点）。

**前提条件**: 繰り返し実行可能なタスク、評価関数（objective or LLM judge）が定義可能、Apple Silicon（MLX 蒸留の場合）。

## Gap Analysis

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Elo ベース進歩ゲーティング | Already | CQS 実装済み（experiment_tracker.py:compute_cqs）。前回プラン Task 1 完了 |
| 2 | ロールバック付き自動復元 | **Gap** | discard 記録はあるが merged 変更の auto-revert なし。前回プランになかった新知見 |
| 3 | 次元別レビュールブリック | **Partial** | benchmark-dimensions.md（システム全体）は実装済み。reviewer 出力への次元スコア追加は前回プラン Task 2 で設計済みだが未実装 |
| 4 | 4層フォールバックパーサー | N/A | hook 出力は構造化済み。LLM テキストの JSON パース場面なし |
| 5 | Playbook 抽象 | Already | session-learner playbook + L0-L4 蒸留パイプライン |
| 6 | Frontier→Local 蒸留 | N/A | ドキュメント蒸留は Task 4 で実装済み。MLX モデル蒸留は射程外 |
| 7 | Tournament 型並列戦略比較 | **Gap** | A/B delta はあるが K-variant 同時比較なし。前回プランになかった新知見 |
| 8 | ドメイン非依存シナリオ | N/A | 開発ワークフロー特化。汎用シナリオフレームワークは射程外 |
| 9 | NL タスク生成 | Already | /spec + /spike が該当 |
| 10 | Orchestrator パターン | Already | autoevolve-core 3フェーズ + /epd + /autonomous |

## Integration Decisions

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| A | 次元別レビュースコア（前回 Task 2） | 採用 | reviewer 出力の定量化で弱点特定が可能に。設計済みで実装コスト低減 |
| B | ロールバック付き改善ゲート | 採用 | merged 後の改悪を自動防止。experiment_tracker 拡張で低コスト |
| C | Tournament 型並列スパイク | 採用 | 最適戦略の選定精度向上。worktree 活用で既存インフラ上に構築可能 |

## Plan

→ `docs/plans/active/2026-03-19-autocontext-v2-integration.md` に詳細プラン
