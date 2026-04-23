---
status: reference
last_reviewed: 2026-04-23
---

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
| Margin Loss | A/B 比較の度合い | `margin_advantage()` |
| K-wise Ranking | K>=3 の順序付き比較 | `plackett_luce_ranking()` |
| Process RM | ステップ品質重み付け | `step_credit(step_quality=...)` |

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

### `margin_advantage(score_a, score_b) -> float`

マージン付き advantage。A/B 比較で「どちらが良いか」だけでなく
「どれくらい良いか」の度合いを返す。Llama 2 の margin loss に着想。

```python
from rl_advantage import margin_advantage
margin_advantage(0.9, 0.6)  # → 0.3 (A が大幅に優位)
margin_advantage(0.51, 0.49)  # → 0.02 (僅差)
```

### `plackett_luce_ranking(scores: list[float]) -> list[float]`

K>=3 の variant を Plackett-Luce モデルで順序付きランキング。
softmax 確率を返す（合計 1.0）。K=2 で Bradley-Terry に帰着。

```python
from rl_advantage import plackett_luce_ranking
probs = plackett_luce_ranking([0.6, 0.9, 0.7, 0.8])
# → [0.098, 0.394, 0.146, 0.361]  # 0.9 が最高確率
```

### `step_credit(outcome, invocations, events, step_quality=None)`

Per-step credit assignment。outcome を呼び出し回数比で配分。
`step_quality` 指定時は PRM 的にステップの正しさで重み付けする。

```python
from rl_advantage import step_credit
invocations = [
    {"skill_name": "review"},
    {"skill_name": "review"},
    {"skill_name": "test"},
]
# 従来動作（回数比のみ）
credits = step_credit(1.0, invocations, [])
# → {"review": 0.6667, "test": 0.3333}

# PRM 的品質重み付け
quality = {"review": 1.0, "test": 0.2}
credits = step_credit(1.0, invocations, [], step_quality=quality)
# → review の寄与が品質で増幅される
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

## ORM/PRM 使い分け

タスク種別に応じてスコアリング戦略を切り替える。

| タスク種別 | スコアリング | step_quality | 理由 |
|-----------|------------|-------------|------|
| 推論系（デバッグ、設計、レビュー） | PRM 的 | 各ステップの正しさで重み付け | 中間推論の正しさが最終結果に影響 |
| 結果系（生成、変換、フォーマット） | ORM 的 | None（呼び出し回数のみ） | 最終出力のみが重要 |
| 混合（実装 + テスト） | PRM 的 | テスト結果で重み調整 | テスト通過が品質の強い信号 |

判定基準: セッション内で「途中経過の質」が最終結果に影響するなら PRM、
「結果だけ見ればいい」なら ORM。迷ったら ORM（従来動作）。

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
