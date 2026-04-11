---
source: "Environment-Driven Reinforcement Learning (Baseten Blog)"
date: 2026-04-08
status: analyzed
---

## Source Summary

**主張**: Orchestrator-Driven RL は既存プロダクトへの統合コストが膨大。Environment-Driven RL は本番システムをユーザーと同じ IF で操作し、推論プロキシでトレースを記録することで最小工数で RL を実現する。Cursor Composer 2 が5時間サイクルでリアルタイム RL モデル更新を実現。

**手法**:
1. Recording Proxy — 推論サーバー前にプロキシでトレース記録
2. Environment-as-User — オーケストレーターが本番をユーザーと同じ方法で操作
3. Replay Mechanism — チェックポイント/クローンで状態再現
4. Trace-based Reward Shaping — トレースからシグナル導出（サンドボックス不要）
5. Continual Learning Loop — 本番トレース→報酬→学習→重み更新のリアルタイムループ

**根拠**: Cursor Composer 2（5時間サイクル更新）、Baseten 顧客実績

**前提条件**: プロダクションがユーザー IF 経由で操作可能、replay mechanism が利用可能、トレースから報酬シグナルが導出可能

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Recording Proxy | Already | session-trace-store.py (Stop hook) + session_events.py (PostToolUse) でトレース記録済み |
| 2 | Environment-as-User | Partial | hook がエージェント行動をラップし環境越しに観測する構図は存在するが、パターンとして明文化されていない |
| 3 | Replay Mechanism | Already | checkpoint_manager.py (PostToolUse hook) で自動チェックポイント。max 5件ローテート |
| 4 | Trace-based Reward Shaping | Already | rl_advantage.py に RLOO/GRPO/IS/PPO 関数群、compute_skill_score() でルールベーススコア |
| 5 | Continual Learning Loop | Already | AutoEvolve (Observe→Learn→Evolve)。session-learner.py + autoevolve-runner.sh |
| 6 | RL Math Framework | Already | rl_advantage.py に包括的な RL 数学基盤 |
| 7 | Friction Events | Already | stagnation-detector.py + friction-events.jsonl。consumer (PR2) 待ち |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | session-trace-store.py | Recording Proxy はリアルタイム記録。現状は事後バッチ | PostToolUse の既存リアルタイム記録をストリーミング形式に拡張 | 強化可能 |
| S2 | checkpoint_manager.py | Replay = 同条件で再実行。現状は復帰目的のみ | A/B 比較実験用途に拡張。AutoEvolve の改善案検証に活用 | 強化可能 |
| S3 | rl_advantage.py | Consumer（reward → selection ループ）が未接続 | AutoEvolve の keep/revert 判定に rl_advantage 関数を接続 | 強化可能 |
| S4 | AutoEvolve ループ | 5時間自動サイクル vs 手動 /improve | cron ベースの自動実行サイクル導入 | 強化可能 |
| S5 | RL math framework | 学習器不在で分析補助層 | prompt/hook 選択ループへの接続を実装 | 強化可能 |

### Codex 批評による修正

- S3, S5: 当初 Already (強化不要) と判定していたが、Codex の指摘で修正。「advantage 推定があっても weight update 不能なら continual learning には直結しない。学習器不在なら補助分析層に留まる」
- 前提の乖離: 記事は weight update が可能な ML パイプライン向け。当セットアップは config/skill update のみ。RL 的フレームワークの適用は有効だが、「自己改善ループ」の意味が本質的に異なる

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 2 | Environment-as-User パターンの明文化 | 採用 | references/ に RL ↔ ハーネス対応表を追加。前提差異も記録 |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | Recording Proxy ストリーミング化 | 採用 | PostToolUse の既存記録を拡張 |
| S2 | Checkpoint → Replay 拡張 | 採用 | A/B 比較実験への活用 |
| S3 | RL → AutoEvolve 接続 | 採用 | 最優先。rl_advantage.py を AutoEvolve に接続 |
| S4 | AutoEvolve 自動化度向上 | 採用 | cron 自動実行サイクル |
| S5 | RL framework → selection loop | 採用 | S3 と統合して実装 |

## Plan

→ `docs/plans/2026-04-08-environment-driven-rl-integration.md` 参照
