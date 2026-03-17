# RL-Inspired Optimization Guide

Policy Gradient の数学的概念を AutoEvolve ハーネスの
離散最適化に適応したフレームワークのガイド。

## RL 概念 → ハーネス対応表

| RL 概念 | ハーネスでの対応 | 実装 |
|---------|----------------|------|
| Policy | スキル設定 (SKILL.md) | `skills/*/SKILL.md` |
| Action | スキル修正提案 | `skill_amender.py` |
| Reward | セッション outcome | `session-learner.py` |
| Trajectory | セッションイベント列 | `current-session.jsonl` |
| Advantage | variant 間の相対評価 | `rl_advantage.py` |
| Importance Sampling | 設定変更後のデータ重み | `importance_weight()` |
| Clipping | 変更比率の制限 | `clip_ratio()` |
| Credit Assignment | スキルごとの寄与度 | `step_credit()` |

## 関数リファレンス

### `rloo_advantage(scores: list[float]) -> list[float]`

Leave-One-Out advantage。各スコアから自身を除く平均を引く。

```python
from rl_advantage import rloo_advantage
# K=4 variant のスコア
adv = rloo_advantage([0.7, 0.8, 0.6, 0.9])
# → [-0.066..., 0.033..., -0.166..., 0.2]
```

### `grpo_advantage(scores: list[float]) -> list[float]`

Group z-score 正規化。mean=0, std=1 に正規化。

```python
from rl_advantage import grpo_advantage
adv = grpo_advantage([0.7, 0.8, 0.6, 0.9])
# z-scores: 各 variant の標準化された位置
```

### `normalize_advantages(deltas: list[float]) -> list[float]`

任意の delta リストを z-score 正規化する汎用関数。

### `importance_weight(ver_cur, ver_data, change_count, decay_rate)`

設定バージョン間の IS 重み。同一バージョン=1.0、
異なるバージョンは `exp(-decay_rate * change_count)` で減衰。

```python
from rl_advantage import importance_weight
# 同一バージョン
w = importance_weight("abc123", "abc123")  # → 1.0
# 1回変更あり
w = importance_weight("abc123", "def456", 1, 0.1)  # → 0.905
```

### `clip_ratio(after, before, epsilon=0.2)`

PPO クリッピング。比率を [1-epsilon, 1+epsilon] に制限。

```python
from rl_advantage import clip_ratio
clip_ratio(1.5, 1.0, 0.2)  # → 1.2 (上限クリップ)
clip_ratio(0.7, 1.0, 0.2)  # → 0.8 (下限クリップ)
clip_ratio(1.1, 1.0, 0.2)  # → 1.1 (範囲内)
```

### `step_credit(outcome, invocations, events)`

Per-step credit assignment。outcome を呼び出し回数比で配分。

```python
from rl_advantage import step_credit
invocations = [
    {"skill_name": "review"},
    {"skill_name": "review"},
    {"skill_name": "test"},
]
credits = step_credit(1.0, invocations, [])
# → {"review": 0.6667, "test": 0.3333}
```

## チューニング指針

### decay_rate (Importance Sampling)

| 値 | 効果 | 推奨場面 |
|----|------|---------|
| 0.0 | 減衰なし（全データ等重み） | 設定変更が稀な場合 |
| 0.1 | 緩やかな減衰（デフォルト） | 通常運用 |
| 0.5 | 急速な減衰 | 設定を頻繁に変える実験期 |

### epsilon (Clipping)

| 値 | 効果 | 推奨場面 |
|----|------|---------|
| 0.1 | 厳格（±10%） | 安定期、保守的な改善 |
| 0.2 | 標準（±20%、デフォルト） | 通常運用 |
| 0.3 | 緩和（±30%） | 探索的な実験期 |

### K (Variant 数)

| K | トレードオフ |
|---|-------------|
| 3 | 最小コスト、ノイズ影響大 |
| 5 | バランス良好（推奨） |
| 7+ | 精度高いが eval コスト大 |

## データフロー

```
Session Events
    ↓
session-learner.py
    ├→ skill-executions.jsonl (config_version, is_weight 付き)
    ├→ skill-credit.jsonl (step_credit 結果)
    └→ session-metrics.jsonl (config_version, is_weight 付き)
    ↓
autoevolve-core (Phase 2: Improve)
    ├→ rl_advantage で advantage 計算
    ├→ importance_weight で過去データの重み調整
    └→ skill_amender.gate_proposal で clip_ratio 検証
    ↓
aggregate_benchmark.py --variants
    └→ K-variant RLOO/GRPO レポート
```
