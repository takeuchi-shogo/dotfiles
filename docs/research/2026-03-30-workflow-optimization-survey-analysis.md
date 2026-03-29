---
source: "From Static Templates to Dynamic Runtime Graphs: A Survey of Workflow Optimization for LLM Agents (Yue et al., arXiv:2603.22386)"
date: 2026-03-30
status: integrated
---

## Source Summary

IBM Research + RPI によるサーベイ論文。LLM エージェントのワークフローを **Agentic Computation Graph (ACG)** として統一的に形式化し、77 本の文献を分類。Template（再利用設計）/ Realized Graph（実行時構造）/ Execution Trace（実行ログ）の 3 層を区別し、Static（事前固定）vs Dynamic（実行時決定）の軸で最適化手法を整理。

### 主要フレームワーク

- **GDT (Graph Determination Time)**: offline / pre-execution / in-execution
- **GPM (Graph Plasticity Mode)**: none / select / generate / edit
- **最適化レベル**: node-level（プロンプト等）/ graph-level（トポロジ等）/ joint
- **Quality-Cost トレードオフ**: max E[R(τ;x) - λC(τ)]
- **Feedback 4 分類**: metric/score, verifier, preference/ranking, trace-derived textual

### 設計トレードオフ（Section 7）

1. **When static is enough**: 3 条件同時成立（制約された演算子空間 + 信頼できる評価 + 反復デプロイ）
2. **Select vs Generate vs Edit**: タスク異質性の度合いで最小 plasticity を選ぶ
3. **Graph > Prompt**: 失敗原因が構造的（ノード欠落/情報パス誤り）なら prompt 修正では解決しない
4. **Verifier 配置**: cheap + semantically meaningful な箇所に戦略配置。全ステップは非効率

### Evaluation Protocol（Table 5）

タスク正解率だけでなくグラフ構造メトリクス（node count, depth, width, communication volume, structural variance）も報告すべきと提唱。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | ACG 形式化 (V,E,Φ,Σ,A) | N/A | 学術的形式化。実装ハーネスには過剰 |
| 2 | Template/Realized Graph/Trace 3 層語彙 | N/A | 概念的に 3 層だが形式的語彙導入の実益薄 |
| 3 | GDT×GPM 分類軸 | Partial | S/M/L スケールはあるが 2 軸での明示的判断基準なし |
| 4 | "When static is enough" 3 条件 | Gap | workflow-guide.md に判定基準なし |
| 5 | Select vs Generate vs Edit 選択 | Partial | 委譲パターンはあるが plasticity 段階での判断基準未明示 |
| 6 | Graph > Prompt 診断 | Gap | failure-taxonomy.md に FM はあるが構造 vs node 修正の分岐なし |
| 7 | Structure-Aware 評価 | Gap | グラフ構造メトリクス未計測 |
| 8 | Minimum Reporting Protocol | Partial | JSONL トレースはあるが 10 次元レポート未対応 |
| 9 | Structural Variance 計測 | Gap | 同タスクタイプでの realized graph 変動度未計測 |
| 10 | Robustness Testing | N/A | 開発ハーネスであり評価環境ではない |

### Already 項目の強化分析

| # | 既存の仕組み | 強化案 | 判定 |
|---|-------------|--------|------|
| A1 | workflow-guide.md タスクスケール | §7.1 の 3 条件チェックリスト追記 | 強化可能 |
| A2 | subagent-delegation-guide 5 パターン | plasticity スペクトラム判定フロー追記 | 強化可能 |
| A3 | failure-taxonomy drift/residual 2 チャネル | Graph vs Prompt 修正診断追記 | 強化可能 |
| A4 | completion-gate + hook verifiers | Verifier 配置ヒューリスティック追記 | 強化可能 |
| A5 | AutoEvolve feedback pipeline | 強化不要 — improve-policy.md にガード機構あり | 強化不要 |
| A6 | Quality-Cost (structured-test-time-scaling) | 強化不要 — Tu 2026 統合で十分カバー | 強化不要 |
| A7 | Feedback 4 種 | 強化不要 — 4 種実装 + reviewer-capability-scores | 強化不要 |

## Integration Decisions

全項目選択。以下を統合:
- T1: workflow-guide.md に "When static is enough" 3 条件 + plasticity 判定
- T2: subagent-delegation-guide.md に plasticity spectrum 判定基準
- T3: failure-taxonomy.md に Graph vs Prompt 修正診断
- T4: trust-verification-policy.md に Verifier 配置ヒューリスティック

### 将来タスク（今回スキップ）

- Structure-Aware 評価スクリプト（グラフ構造メトリクス計測）
- Minimum Reporting Protocol の JSONL スキーマ拡張
- Structural Variance 計測パイプライン

## Plan

| タスク | ファイル | 変更内容 |
|--------|---------|---------|
| T1 | `references/workflow-guide.md` | §7.1 "When static is enough" 3 条件 + plasticity spectrum |
| T2 | `references/subagent-delegation-guide.md` | GPM 4 段階の判定基準テーブル |
| T3 | `references/failure-taxonomy.md` | 構造 vs node 修正の診断フローチャート |
| T4 | `references/trust-verification-policy.md` | Verifier Placement Heuristic |
