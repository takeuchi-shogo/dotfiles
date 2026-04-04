---
source: https://github.com/neosigmaai/auto-harness
date: 2026-04-04
status: integrated
---

## Source Summary

**主張**: エージェントのボトルネックはコード生成ではなく検証・回帰検出・eval維持。自己改善ループで品質を継続向上できる（Tau3: 0.56→0.78, +40%）。

**手法**:
1. Failure Mining — 本番トレースから失敗パターンを自動抽出
2. Root Cause Clustering — 症状ではなく根本原因でグルーピング
3. Living Eval Cases — クラスタから再利用可能なevalケースを自動生成
4. Regression Gate — 修正済み失敗が永続テストケースに。バックスライド不可
5. Autonomous Harness Changes — テスト環境で自律的にハーネス変更→検証→採用
6. Sub-agents + Recursive Summarization — 冗長トレースのコンテキスト管理
7. PROGRAM.md — 人間の指示でループを操舵
8. workspace/learnings.md — 永続学習ログ

**根拠**: Tau3ベンチで0.56→0.78。クラスタリングで過適合防止、regression gateで gains compound。

**前提条件**: ベンチマーク可能なタスクセット、構造化された失敗トレース、自動実行環境

## Gap Analysis

### Gap / Partial

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Root Cause Clustering | Partial | failure-taxonomy.md が静的FM定義。動的クラスタリングなし |
| 2 | Regression Gate | Gap | eval は手動作成。修正済み失敗→eval自動追加→バックスライド防止のフローなし |
| 3 | Living Eval Cases | Gap | reviewer-eval-tuples.json は手動。失敗クラスタからの自動生成パイプラインなし |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|-------------|--------------|--------|
| 1 | Failure Mining: session-learner.py | 強化不要 | — |
| 2 | Autonomous Harness: /improve ADVERSARIAL GATE | 強化可能 | 定量的回帰検出ゲート追加 |
| 3 | PROGRAM.md: CLAUDE.md + references/ | 強化不要 | — |
| 4 | Sub-agents: agent delegation | 強化不要 | — |
| 5 | learnings.md: learnings/*.jsonl | 強化不要 | — |

## Integration Decisions

全 Gap/Partial + 強化可能項目を取り込む。

## Plan

| # | タスク | ファイル | 規模 |
|---|--------|---------|------|
| T1 | failure-clusterer.py | scripts/learner/failure-clusterer.py | M |
| T2 | eval-generator.py | scripts/learner/eval-generator.py | M |
| T3 | Regression Gate | scripts/eval/regression-gate.py + phase4 強化 | M |
| T4 | Hook 接続 | settings.json | S |
