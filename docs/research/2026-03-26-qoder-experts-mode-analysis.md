---
source: "How Qoder builds Harness Engineering into Experts Mode (Qoder Blog, 2026-03)"
date: 2026-03-26
status: integrated
---

## Source Summary

**主張**: 単一エージェント・ハーネスには5つの構造的限界（コンテキスト零和・役割切替オーバーヘッド・長鎖ドリフト・機能正確性検証の欠如・ターミナル実行リスク）があり、マルチエージェント "Experts Mode" で解決できる。67%品質向上、2/3コスト。

**手法（8つ）**:
1. Leader/Expert 分離 — 調整役は実装しない
2. DAG 駆動の非同期並列 — 依存をDAGで管理、独立タスクは並列
3. Star Topology — 中央集権、P2P拒否（矛盾検出不能・状態追跡の指数増加）
4. Expert = 独立ハーネス — ツールセット・コンテキスト注入・実行制約が役割別
5. Cross-model scheduling — タスク種別→最適モデル割当
6. Functional correctness verification — Browser E2E + QA change-aware + Code Review semantic diff
7. Self-evolution — タスクレベルスキル抽出→メモリ蓄積→自動リコール
8. Terminal execution safety — OS別ASTパーサー + 3層リスクチェック + サンドボックス

**根拠**: Stripe (1,300+ agent PR/week)、Ramp (30% agent PR)、Coinbase (150h→15h)、OpenAI (1M LOC, 0 hand-written) の実績。

**前提条件**: マルチエージェント基盤（チーム管理、非同期実行、ツール制限）が利用可能であること。

## Gap Analysis

### Gap / Partial

| # | 手法 | 判定 | 現状 | 統合対象 |
|---|------|------|------|----------|
| 1 | Leader/Expert 分離 | **Partial** | `/review`, triage-router で暗黙的に実現。agent 定義に「実装禁止」の明示契約がない | Yes |
| 2 | DAG 駆動の非同期並列 | **Partial** | workflow-guide.md に依存列付き Unit of Work。worktree 並列あり。自動 DAG executor なし | Yes |
| 4 | Expert = 独立ハーネス | **Partial** | 31 agent に異なるツール制限。per-agent token budget / reasoning effort / context injection profile 未定義 | Yes |
| 6 | 機能正確性検証 | **Partial** | E2E(webapp-testing) + QA(autocover) + Review(cross-file-reviewer) 個別存在。統合 oracle なし | Yes |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点/知見 | 強化案 | 統合対象 |
|---|-------------|-------------------|--------|----------|
| 3 | Star Topology | **強化不要** — 完全一致 | — | No |
| 5 | Cross-model scheduling | **強化可能** — Qoder は Expert 単位でモデル固定。現状 agent 定義に default model 未指定のものが多い | agent 定義に model フィールド明示 | Yes |
| 7 | Self-evolution | **強化可能** — Qoder は各 Expert が独立してスキル抽出。現状は autoevolve-core が一元管理 | reviewer-capability-scores.md にフィードバックループ追加 | Yes |
| 8 | Terminal safety | **強化可能** — コマンドネスト内サブコマンド抽出が regex ベースでは不完全 | agency-safety-framework.md に改善候補として記録 | Yes |

## Integration Decisions

全7項目を統合。優先順位:
1. T1: subagent-delegation-guide.md に Leader/Expert 契約パターン追加
2. T2: agent-execution-profiles.md 新規（per-agent 実行プロファイル）
3. T3: reviewer-capability-scores.md にフィードバックループ節追加
4. T4: agency-safety-framework.md にコマンドネスト検出の改善候補記録
5. T5: workflow-guide.md に Correctness Oracle 節追加
6. T6: subagent-delegation-guide.md に DAG 自動化の設計指針追加
7. T7: agent 定義の model フィールド監査・補完

## Plan

→ `docs/plans/2026-03-26-qoder-experts-mode-integration.md` 参照
