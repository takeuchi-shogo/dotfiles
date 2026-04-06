---
source: "https://arxiv.org/abs/2604.02988"
date: 2026-04-07
status: integrated
---

## Source Summary

**主張**: マルチエージェント Deep Research システムのプロンプトを「学習可能なパラメータ」として扱い、self-play + 自動最適化（TextGrad / GEPA）で専門家の手作成プロンプトと同等以上の性能を達成できる。

**手法**:
- 4エージェント構成（Orchestrator / Reader / Aggregator / Writer）で Deep Research を実行
- TextGrad: テキスト勾配降下でプロンプトを反復最適化（実行トレース→損失→勾配→更新）
- GEPA: 遺伝的パレート最適化。複数候補を並行保持し、パレートフロンティアで淘汰
- ルーブリック評価 + 実行トレースのフィードバックループ（タスク固有評価信号が鍵）
- メタプロンプトのカスタマイズ（オプティマイザ自体のプロンプトを調整）

**根拠**: ScholarQA-CS (GPT-4.1-mini) で最小限プロンプト→GEPA最適化 +0.192（0.513→0.705）。専門家プロンプト超え。GEPA がTextGrad を +0.051 上回る。OpenAI 汎用オプティマイザは実行トレース未活用で劣悪（0.583）。

**前提条件**: 反復的計画・検索・統合タスク。評価ルーブリックが定義可能。コスト $50/ラウンド。単一ドメイン（CS）・小規模（テスト50件）での検証のみ。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | 4エージェント DR アーキテクチャ | Already | `/research` が 5段パイプラインを実装 |
| 2 | TextGrad (テキスト勾配降下) | Gap | AutoEvolve は 1-shot 提案→精錬。勾配ベース反復最適化なし |
| 3 | GEPA (遺伝的パレート最適化) | Partial | Ideation-Debate + best-of-n あり。population-based 探索なし |
| 4 | ルーブリック評価 + 実行トレース | Already | session-trace-store + adversarial gate |
| 5 | メタプロンプトのカスタマイズ | Partial | Phase 4 gate プロンプトは固定 |
| 6 | Self-play 多様探索 | Gap | greedy 単一候補精錬のみ |
| 7 | 引用管理パイプライン | N/A | DR 固有。ハーネスには不要 |

### Already 項目の強化分析

| # | 既存の仕組み | 論文が示す弱点 | 強化案 |
|---|-------------|---------------|--------|
| 1 | `/research` 5段パイプライン | Aggregator の品質基準が未定義 | 重複排除・矛盾検出・エビデンス強度フィルタ追加 |
| 4 | session-trace-store + adversarial gate | 汎用スコアではタスク固有の品質差異を検出できない | カテゴリ別ルーブリック生成を Phase 2 に追加 |

## Integration Decisions

全項目取り込み:

- **#1強化** → `/research` SKILL.md の Aggregate ステップに品質基準テーブル追加
- **#2+6** TextGrad + Self-play → `evolve-mode.md` に `--pareto` モード追加（3バリアント並行生成・パレート淘汰）
- **#3** GEPA → 同上。パレートフロンティア選択 + 確率的親選択を実装
- **#4強化** → `improve-policy.md` に Rule 44（タスクカテゴリ別ルーブリック評価）追加
- **#5** → `phase4-adversarial-gate.md` にメタプロンプト自己改善セクション追加

## Changes Made

| ファイル | 変更内容 |
|---------|---------|
| `skills/research/SKILL.md` | Step 4 Aggregate に品質基準テーブル追加（重複排除・矛盾検出・エビデンス強度・カバレッジ確認） |
| `references/improve-policy.md` | Rule 44 追加: タスクカテゴリ別ルーブリック評価（汎用→カテゴリ固有の評価信号） |
| `skills/improve/instructions/evolve-mode.md` | `--pareto` モード追加: 3バリアント並行生成・パレートフロンティア淘汰・確率的親選択 |
| `skills/improve/instructions/phase4-adversarial-gate.md` | メタプロンプト自己改善セクション追加: Gate プロンプト自体の改善トリガー・制約・履歴管理 |
