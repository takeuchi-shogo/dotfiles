---
source: "ASI-Evolve: AI Accelerates AI (arXiv:2603.29640)"
date: 2026-04-06
status: analyzed
---

## Source Summary

**主張**: AI自身の開発を加速する自律型エージェントフレームワーク（ASI-Evolve）が、認知基盤（人間の先行知識注入）と専門分析器（構造化フィードバック蓄積）の2コンポーネントにより、AIスタック全体で人間超えの改善を実現。

**手法**:
- **認知基盤 (Cognition Base)**: 論文から抽出した設計原則をembeddingで索引化し、各探索ラウンドに意味的類似性で注入
- **専門分析器 (Analyzer)**: 生ログ・メトリクス・訓練動態から意思決定指向レポートを蒸留し、再利用可能な洞察として蓄積
- **UCB1/MAP-Elites サンプリング**: 探索/活用バランスをバンディットアルゴリズムで管理
- **多段階評価パイプライン**: 小規模→中規模→大規模と段階的に候補を昇格・棄却
- **構造化データベース**: 各ラウンドで (motivation, program, results, analysis_report, metadata) を保存
- **新規性チェック**: 動機類似性に基づく重複提案フィルタリング

**根拠**:
- アーキテクチャ設計: 105個がDeltaNet超え、+0.97pt（人間改善の3倍）
- データキュレーション: 平均+3.96pt、MMLU+18.64pt
- RLアルゴリズム: GRPO超過10個、AMC32+12.5pt
- 分析器除去 → 長期プラトー（構造化分析が継続的進化に不可欠）
- 認知基盤除去 → コールドスタート遅延（知識注入が初期加速に有効）

**前提条件**: 閉ループの実験→評価→改善サイクルが構築済み、ドメイン知識の構造化が可能

## Gap Analysis

### Gap / Partial

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Embedding索引付き認知基盤 — 先行知識を索引化し各ラウンドで意味的類似性で自動注入 | Gap | references/, wiki/ に知識はあるが semantic search なし。注入は手動 |
| 2 | UCB1/バンディットベース探索戦略 — 探索と活用のバランスを数理的に管理 | Gap | Ideation-Debate は3候補→Codex ROI判定。bandit スコアリングなし |
| 3 | 候補プール管理 — 上位Nの成功パターンをスコア付きプールで維持 | Gap | improvement-backlog.md は優先テーマ保持だが top-K スコア管理ではない |
| 4 | 多段階スケールアップ評価 — 段階的に候補を昇格・棄却する基準 | Partial | Spot Checking は類似だがスケールアップ基準が曖昧 |
| 5 | 適応的計算予算配分 — コンテンツ複雑性に応じた動的リソース割り当て | Partial | モデルルーティングはタスク種別ベース。複雑性ベースではない |

### Already 項目の強化分析

| # | 既存の仕組み | ASI-Evolve が示す弱点 | 強化案 |
|---|---|---|---|
| A | AutoEvolve 閉ループ (runs/) | ラウンドごとのメタデータが不十分 | runs/ に motivation+outcome+analysis の構造化スキーマ追加 |
| B | meta-analyzer (バッチ分析) | per-experiment のリアルタイム蒸留なし | merge/revert 直後の即時効果測定マイクロレポート追加 |
| C | 新規性チェック (AP-1 スキル重複) | 提案レベルの事前類似性フィルタなし | rejected-patterns + 過去提案の motivation テキスト類似性で事前重複検出 |
| E | 知識蒸留パイプライン (L0→L4) | L3/L4 知識の検索可能インデックスなし | 昇格知識を topic-tagged index で管理し AutoEvolve から検索可能に |

### N/A

| 手法 | 理由 |
|---|---|
| 多段階パラメータスケール (20M→1.3B) | ML訓練固有 |
| 静的チェック+デバッグエージェント | hooks + build-fixer で十分 |
| 差分編集モード | Edit ツールが標準 |

## Integration Decisions

全 Gap/Partial 5項目 + Already 強化 4項目 = 9項目を統合。
L規模のため docs/plans/ にプラン保存し、複数セッションで段階的に実装。

## Plan

→ `docs/plans/2026-04-06-asi-evolve-integration.md` 参照
