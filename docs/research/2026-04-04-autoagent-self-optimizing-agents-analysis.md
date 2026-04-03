---
source: "AutoAgent: first open source library for self-optimizing agents (kevinrgu/autoagent)"
date: 2026-04-04
status: integrated
---

## Source Summary

**主張**: メタエージェントがタスクエージェントのハーネスを自律改善でき、手動チューニングを凌駕する。

**手法**:
- Meta/Task Agent Split — 自己改善ではなく別エージェントが改善する分離アーキテクチャ
- Trace-driven improvement — スコアだけでなく推論トレースを分析して改善
- Model empathy / Same-model pairing — メタとタスクで同モデルを使うと最も効果的
- Anti-overfitting reflection — "このタスクが消えても価値ある改善か？" で汎化テスト
- Emergent behaviors: spot checking, forced verification loops, writing tests, progressive disclosure, orchestration logic

**根拠**: SpreadsheetBench 96.5%（#1）、TerminalBench 55.1%（#1）。24h+自律最適化で全手動エンジニアリングを上回った。

**前提条件**: evals基盤 + 大量サンドボックス並列 + 24h+計算リソース

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Meta/Task Agent Split | Already | AutoEvolve が meta/task 分離を実現 |
| 2 | Trace-driven improvement | Already | session-trace-store.py + keyword grep |
| 3 | Model empathy / Same-model pairing | Partial | Cross-Model Insight Registry あり。モデル別ハーネス分岐なし |
| 4 | Anti-overfitting reflection | Partial | Adversarial Gate で KISS/YAGNI チェックあり。汎化テスト明示なし |
| 5 | Spot checking | Gap | 改善提案の検証は常にフルセッション前提 |
| 6 | Forced verification loops | Already | completion-gate + verification-before-completion |
| 7 | Writing tests for improvements | Partial | /autocover あり。改善提案に対するテスト自動生成なし |
| 8 | Progressive disclosure | Already | CLAUDE.md → references/ → rules/ 3層設計 |
| 9 | Orchestration logic | Already | /dispatch + cmux Worker + Agent routing |
| 10 | Meta-agent quality | Already | Adversarial Gate (Codex) |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|-------------|---------------|--------|
| 2 | session-trace-store.py | スコアのみでは改善率激減 | スコア×トレース紐付け強化 |
| 10 | Adversarial Gate | Codex は meta-agent として弱い | cross-model-insights に知見追記 |

## Integration Decisions

全項目取り込み:

- **#3** Model empathy → cross-model-insights.md に追記
- **#4** 汎化テスト → phase4-adversarial-gate.md に 6th 観点として追加
- **#5** Spot checking → improve-policy.md に部分検証戦略セクション追加
- **#7** テスト可能性 → proposals-report.md にテスト戦略要件追加
- **#2強化** スコア×トレース紐付け → data-collection.md に原則追加
- **#10強化** Codex meta-agent 弱点 → cross-model-insights.md に追記

## Changes Made

| ファイル | 変更内容 |
|---------|---------|
| `references/cross-model-insights.md` | Model Empathy セクション追加（same-model pairing + Codex meta-agent 弱点） |
| `skills/improve/instructions/phase4-adversarial-gate.md` | 第6観点「汎化テスト」追加 |
| `references/improve-policy.md` | Spot Checking セクション追加（影響範囲別検証テーブル） |
| `skills/improve/instructions/data-collection.md` | トレース×スコア紐付け原則追加 |
| `skills/improve/instructions/proposals-report.md` | 改善提案テスト可能性要件追加 |
