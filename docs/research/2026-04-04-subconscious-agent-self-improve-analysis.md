---
source: "I Gave My Hermes + OpenClaw Agents a Subconscious, and Now They Self-Improve 24/7 | Full Guide"
date: 2026-04-04
status: integrated
---

## Source Summary

### 主張
エージェントに「サブコンシャス（潜在意識）」レイヤーを追加し、Ideation → Debate → Synthesis の自己改善ループを永続ステートで回すことで、ランごとに複利的に改善するシステムを構築できる。

### 手法
1. **自己改善ループ**: Trigger → Runner → Ideation → Debate/Critique → Synthesis → Artifacts → Approval Gate → フィードバック
2. **永続ステート**: JSON/JSONL/markdown で勝った方向性・却下パス・次の改善を保持
3. **3フェーズ推論**: アイデア生成 → 強いモデルで批判・防御 → 1つの推奨に合成
4. **モデルルーター**: フェーズごとに最適モデル（安い=発想、強い=判断）
5. **ガードレール/ガバナンス**: エビデンスファースト、明示的ステート、承認ゲート
6. **アーティファクト永続化**: ideas/, debate/, winning-concept.md, improvement-backlog.md
7. **改善バックログ**: 次ランで磨くべき点を永続化
8. **設定の外部化**: モデル割り当て・ディベートラウンド数・フリーズ条件等を設定で管理

### 根拠
- ほとんどのエージェントシステムは推測ベースで改善し、ドリフトする
- サブコンシャスループでランタイムドリフトと配信出力のミスアライメントを自動検出・修正した実例あり
- 永続化が「ファジーな記憶」と「構造化された学習」の違いを生む

### 前提条件
- 定期実行されるワークフロー、複数モデルへのアクセス、永続ファイルシステム

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Ideation → Debate → Synthesis 3フェーズ推論 | **Partial** | AutoEvolve は Analyze → Improve → Garden の3フェーズ。Codex Deep Analysis が批判役だが、**複数候補の生成・対決**はしていない |
| 2 | 改善バックログの永続化 | **Partial** | `rejected-patterns.jsonl` や `lessons-learned.md` はあるが、「次ランで具体的に何を磨くべきか」を1ファイルで明示する仕組みがない |
| 3 | per-run アーティファクト構造 (ideas/, debate/, winning-concept.md) | **Gap** | `insights/analysis-YYYY-MM-DD.md` は出力するが、ラン内の思考過程を構造化保存していない |
| 4 | 設定の外部化 | **N/A** | `improve-policy.md` が既にこの役割を果たしている |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|-------------|---------------|--------|
| A | AutoEvolve ループ (autoevolve-core + /improve) | 推測ベースの改善 | Already (強化不要) — evidence_chain + confidence で排除済み |
| B | モデルルーター (codex-delegation, gemini-delegation) | フェーズごとのモデル分離 | Already (強化不要) — Sonnet/Codex/Gemini 分離済み |
| C | ガードレール/ガバナンス (governance-map, improve-policy) | 承認ゲート必須 | Already (強化不要) — 5層ガバナンス完備 |
| D | 永続ステート (agent-memory/, traces/, jsonl) | 次ランの入力に前回結果を注入 | Already (強化可能) — 前回の「勝った方向性」を次ランに明示注入する仕組みがない |
| E | スケジューラ (cron + /improve) | トリガーソース | Already (強化不要) — cron + オンデマンド両対応 |

## Integration Decisions

全項目を取り込み:

1. **[Partial → 取込]** AutoEvolve に Ideation-Debate パターンを追加
2. **[Partial → 取込]** improvement-backlog.md の導入
3. **[Gap → 取込]** per-run アーティファクト構造
4. **[Already強化 → 取込]** ラン間状態引き継ぎ（winning direction injection）

## Plan

### T1: Ideation-Debate パターン (autoevolve-core.md Phase 2)

Phase 2 (Improve) の改善候補生成を拡張:
- 現行: 分析結果 → 直接提案生成
- 変更後: 分析結果 → **3つの改善方向性を候補生成** → Codex に「ROI 最大はどれか」判定 → 勝者を Phase 2.5 (Adversarial Gate) に送る
- 既存の Adversarial Gate はそのまま活用

### T2: improvement-backlog.md (autoevolve-core.md Phase 5)

Phase 5 (Report) に追加:
- `~/.claude/agent-memory/improvement-backlog.md` を更新
- 内容: 次ラン優先テーマ、却下された方向性と理由、データ不足で保留中のテーマ
- `rejected-patterns.jsonl` とは別（backlog=前向き、rejected=後ろ向き）

### T3: per-run アーティファクト構造 (autoevolve-core.md Phase 1 + Phase 5)

- Phase 1 で `~/.claude/agent-memory/runs/YYYY-MM-DD/` を作成
- Phase 5 で書き出し:
  - `candidates.md` — 3候補の方向性
  - `debate-log.md` — Codex 判定理由
  - `winning-direction.md` — 選ばれた方向性と根拠
  - `run-summary.json` — メトリクス

### T4: ラン間状態注入 (autoevolve-core.md Phase 1)

Phase 1 (Collect) に追加:
- `improvement-backlog.md` を読み込み
- 前回 `runs/` の `winning-direction.md` を読み込み
- Phase 2 の入力コンテキストに注入

### 依存関係

T3 → T1 → T2 → T4

### 規模

M（主に autoevolve-core.md + improve/SKILL.md の2ファイル）
