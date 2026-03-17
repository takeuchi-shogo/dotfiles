---
source: https://rlhfbook.com/c/06-policy-gradients
date: 2026-03-18
status: analyzed
---

# Policy Gradients for RLHF — ハーネス最適化への応用分析

## Source Summary

RLHF の計算基盤である policy gradient 手法の包括的解説。REINFORCE, RLOO, PPO, GRPO, GSPO, CISPO の各アルゴリズムを数学的に定式化し、実装詳細（loss 集約、MDP vs Bandit フレーミング、非同期学習アーキテクチャ）を網羅。

### 主張

- RL policy gradient がLLM最適化の計算基盤
- アルゴリズム選択より入力データ品質が最大の決定要因
- 現代の RLHF は古典 RL から大きく乖離（sequence-level reward、γ=1.0、frozen reference model）

### 核心手法

| アルゴリズム | 特徴 | 計算コスト |
|-------------|------|-----------|
| REINFORCE | 最もシンプル。MC 推定。高分散 | 低 |
| RLOO | K-1 の他サンプルをベースラインに。value network 不要 | 中 |
| PPO | importance sampling + clipping で安定化。value network 必要 | 高 |
| GRPO | グループ正規化。value network 不要。メモリ効率良 | 中 |
| GSPO | sequence-level IS ratio。長文・スパースモデル向け | 中 |
| CISPO | clipped IS weight + stop-gradient。非対称 clipping 可能 | 中 |

### RL概念 → ハーネス概念マッピング

| RL | ハーネス |
|----|---------|
| Policy π_θ | 設定全体（CLAUDE.md, skills, agents, hooks, rules） |
| Action | スキル選択、エージェントルーティング、改善提案 |
| Reward R | importance score, skill health score, review 結果 |
| Episode | セッション |
| Advantage A | A/B delta（改善前後の差分） |
| Trust Region | 安全制約（max 3 files, 連続 reject 制限） |
| Value Function V(s) | ベースラインの期待値 |

## Gap Analysis

| # | 手法 | 判定 | 現状 / 差分 |
|---|------|------|------------|
| 1 | 報酬シグナル | **Already** | importance (0.0-1.0), skill health, review confidence |
| 2 | 基本 Advantage | **Already** | A/B delta (+2pp 閾値) |
| 3 | Trust Region 制約 | **Already** | max 3 files, 3連続 reject → 停止 |
| 4 | On-policy データ | **Already** | session-learner がリアルタイム収集 |
| 5 | Outcome 分類 | **Already** | recovery / failure / clean_success |
| 6 | GRPO グループ正規化 | **Partial** | A/B は K=2。K>>2 の正規化なし |
| 7 | Advantage 正規化 | **Partial** | raw delta 使用。z-score 正規化なし |
| 8 | Clipping 関数 | **Partial** | 安全ルールあるが ratio-based 定式化なし |
| 9 | Loss 集約戦略 | **Partial** | per-event vs per-session の明示的選択なし |
| 10 | RLOO ベースライン | **Gap** | K-1 leave-one-out なし |
| 11 | Value Function V(s) | **Gap** | 期待 outcome 予測モデルなし |
| 12 | Importance Sampling | **Gap** | 陳腐データの分布シフト補正なし |
| 13 | Per-step Attribution | **Gap** | スキル別 outcome 帰属なし |
| 14 | Actor-Learner 分離 | **N/A** | 分散 GPU 概念は不適用 |
| 15 | γ 割引率 | **N/A** | ニューラルネット学習ではない |
| 16 | KL ダイバージェンス | **N/A** | ポリシーが確率分布ではない |

## Integration Decisions

全 Gap/Partial 項目を取り込む（ユーザー選択: 全部）:

1. **[Gap] RLOO ベースライン** — skill-audit で K≥4 variants 評価
2. **[Gap] Importance Sampling** — config_version による陳腐データ重み減衰
3. **[Gap] Per-step Attribution** — セッション内スキル別 outcome 帰属
4. **[Partial] GRPO グループ正規化** — group mean/std 正規化
5. **[Partial] Advantage 正規化** — raw delta → z-score
6. **[Partial] Clipping 定式化** — ratio-based clipping 統一

## Plan

→ `docs/plans/2026-03-18-rl-optimization-framework.md` 参照
