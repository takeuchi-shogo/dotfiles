---
source: "@gkisokay - Stop building workflows. Build agents that improve themselves."
date: 2026-03-19
status: integrated
---

## Source Summary

### 主張

ワークフローを増やすのではなく、スコアリングとフィードバックループを持つスキルを構築し、
自己改善するエージェントを作るべき。スクリプトとスキルの違いは
「評価・改善・合成が可能な契約を持つかどうか」。

### 手法

1. **Skill contracts** — trigger/input/output/scoring を front matter で定義
2. **4-Layer Stack** — Skills → Orchestration → Scoring → Optimizer
3. **Self-scoring** — 全スキル出力に `Score: [1-10]` + `Reason:` を付与
4. **閾値ベースルーティング** — >=80 HIGH_SIGNAL, >=50 CONTEXTUAL, >=25 WATCHLIST, <25 NOISE
5. **Scoring config 外部化** — 重み・閾値を JSON で管理
6. **Retroactive scoring bootstrap** — 過去出力をバッチスコアリングして初期データ化
7. **Optimizer loop** — 平均スコア低下 → 改善プロンプト → Plan Mode でレビュー
8. **Audit-first approach** — 実装前に全スキルの棚卸し

### 根拠

スコアなしの改善は guesswork。スコアありなら systematic。
フィードバックループが compounding を生む。

### 前提条件

スキルが複数あり繰り返し実行される環境。単発スクリプトの少ないセットアップでは過剰。

## Gap Analysis

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Skill contracts | Already | skills/ に front matter 定義済み。91%リッチ化。SkillNet 5D 評価 |
| 2 | 4-Layer Stack | Already | skills/ + hooks 4層 + scoring-rules.md + AutoEvolve |
| 3 | Self-scoring | Partial | skill-executions.jsonl でシステム側がスコア記録。スキル自己評価なし |
| 4 | 閾値ルーティング | Partial | イベント重要度閾値あり。スキル出力→アクションのルーティングなし |
| 5 | Scoring config 外部化 | Partial | 閾値は markdown 定義。チューニング可能な JSON config なし |
| 6 | Retroactive bootstrap | Gap | 未実装 |
| 7 | Optimizer loop | Already | AutoEvolve Phase 2 (Failing/Degraded 検出→修正案→A/B→ブランチ) |
| 8 | Audit-first | Already | /skill-audit, /audit, search-first |

## Integration Decisions

全4項目を取り込み:

1. **[Partial→統合] Scoring config JSON 外部化** — `scoring-config.json` に閾値・重みを集約
2. **[Partial→統合] スキル自己スコアリング標準化** — skill-writing-principles に self-scoring パターン追加
3. **[Partial→統合] 閾値ベースルーティング** — スキル出力スコアの信号分類を autoevolve-core に追加
4. **[Gap→実装] Retroactive scoring bootstrap** — バッチスコアリングスクリプト作成

## Plan

→ `docs/plans/2026-03-19-compounding-agent-integration.md`
