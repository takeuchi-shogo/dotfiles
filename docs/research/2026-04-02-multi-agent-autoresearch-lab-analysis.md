---
source: "Multi-Agent Autoresearch Lab (burtenshaw/multiautoresearch)"
date: 2026-04-02
status: analyzed
---

## Source Summary

### 主張
ML エージェントインフラは「実行」問題を解決したが、真の課題は「実行後の意思決定」— 何が起きたか、なぜ失敗したか、次に何をすべきか。4つの専門ロールで構成されるマルチエージェントシステムが、自律的な研究ラボとしてこれを解決する。

### 手法
1. **ロールベース4エージェント設計**: researcher(文献探索) / planner(実験キュー管理) / worker(仮説実行) / reporter(観測性) + memory-keeper(永続状態管理)
2. **1仮説1パッチ1実行の規律**: promoted master からリフレッシュ → 1つだけ変更 → 実行 → 勝利時のみ promote
3. **Git worktree によるワーカー隔離**: 各 worker は独立 worktree で code mutation。memory-keeper のみ main checkout に書き込み
4. **Wave ベース並列実行**: 複数 worker が小さなバリアントを並列探索。Wave 単位でバッチ→評価→次バッチ
5. **インフラ as プリミティブ**: HF buckets(キャッシュ) / HF Jobs(実行) / Trackio(観測) / HF Papers(リサーチ)
6. **ラベルベーストレーサビリティ**: campaign/experiment/worker/hypothesis をジョブにタグ付け
7. **Promotion ゲート**: ベースラインメトリクスを超えた場合のみ master を更新
8. **Trackio 観測性**: fleet summary + anomaly 検出 + metric dashboard

### 根拠
- Karpathy の autoresearch ベンチマークでの実証
- zai-org/GLM-4.7 と opencode エージェントがベースラインを超えて改善
- OpenCode の sub-agent integration で prompt 交換を追跡可能

### 前提条件
- ML 実験コンテキスト（計測可能なメトリクスがある）
- GPU アクセス（HF Jobs）
- OpenCode が主フレームワーク（hermes, claude, codex もサポート）

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | ロールベース4エージェント設計 | **Partial** | 専門エージェント群は豊富だが研究ラボ型ロール分担は未定義。/research がresearcher、/dispatch がworker相当。planner/reporter 欠落 |
| 2 | 1仮説1パッチ1実行の規律 | **Gap** | /spike は worktree 隔離するが「1つだけ変更して計測」プロトコル未 codify |
| 3 | Promotion ゲート | **Gap** | Review Gate は品質ゲート。メトリクス改善時のみ promote する定量ゲートは不在 |
| 4 | Wave ベース並列実行 | **Partial** | dispatch + worktree + best-of-n で並列実行可能。Wave ライフサイクル管理は未実装 |
| 5 | HF インフラ | **N/A** | dotfiles ハーネスエンジニアリングが対象。ML 実験インフラは範囲外 |
| 6 | ラベルベーストレーサビリティ | **Partial** | session-trace-store + conventional commit タグあり。実験単位のラベリング体系は未構築 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す知見 | 強化案 |
|---|-------------|---------------|--------|
| A1 | worktree 隔離（CLAUDE.md + dispatch + subagent-delegation-guide） | memory-keeper のみ main checkout に書き込み、worker は worktree 内のみ。書き込み権限の明示的分離 | subagent-delegation-guide に worktree 内エージェントの main checkout Write 禁止ルールを明文化 |
| A2 | 専門エージェント群（20+） | ロール間通信テンプレートが AGENTS.md に定義。引き継ぎプロトコルが明示的 | workflow-guide Agent Routing Table にハンドオフフォーマット追記 |
| A3 | session-trace-store + contrastive-trace-analyzer | Trackio で fleet summary + anomaly 検出 + metric dashboard。マルチエージェント全体の鳥瞰ビュー | session-trace-store に fleet-level summary 出力を追加 |

## Integration Decisions

全項目取り込み（#1-4,6 + A1-A3）。#5(HF インフラ) は N/A でスキップ。

## Plan

| # | タスク | 対象ファイル | 規模 |
|---|--------|-------------|------|
| T1 | 実験規律リファレンス新設（1仮説1パッチ1実行 + Promotion ゲート + Wave ライフサイクル） | `references/experiment-discipline.md` | S |
| T2 | subagent-delegation-guide 強化（worktree Write 禁止 + ラボ型ロール + ハンドオフ） | `references/subagent-delegation-guide.md` | S |
| T3 | workflow-guide Agent Routing Table 拡張（ハンドオフフォーマット） | `references/workflow-guide.md` | S |
| T4 | session-trace-store fleet サマリー拡張 | `scripts/lifecycle/session-trace-store.py` | S |
| T5 | situation-strategy-map にラボ型エントリ追加 | `references/situation-strategy-map.md` | S |

依存: T1 ← T2, T5。T2-T5 は並列可能。
