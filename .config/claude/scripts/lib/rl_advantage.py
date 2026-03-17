"""RL-inspired advantage estimation for AutoEvolve discrete optimization.

Policy Gradient の数学的フレームワーク（RLOO, GRPO, Importance Sampling,
Clipping, Per-step Attribution）を
ハーネスの離散最適化に適応する pure function ライブラリ。

Usage:
    from rl_advantage import rloo_advantage, grpo_advantage, clip_ratio
"""

from __future__ import annotations

import math


def rloo_advantage(scores: list[float]) -> list[float]:
    """RLOO (Leave-One-Out) advantage を計算する。

    各スコアから「自身を除いた他の全スコアの平均」を引いた値。
    K variant の中で相対的に良い/悪いスコアを識別する。

    Args:
        scores: K variant のスコアリスト (K >= 2)

    Returns:
        各 variant の advantage。len < 2 の場合は空リスト。

    Examples:
        >>> rloo_advantage([1.0, 2.0, 3.0, 4.0])
        [-2.0, -0.6666666667, 0.6666666667, 2.0]
    """
    k = len(scores)
    if k < 2:
        return []

    total = sum(scores)

    # 全スコアが同値の場合
    if all(s == scores[0] for s in scores):
        return [0.0] * k

    advantages = []
    for i in range(k):
        baseline = (total - scores[i]) / (k - 1)
        advantages.append(round(scores[i] - baseline, 10))
    return advantages


def grpo_advantage(scores: list[float]) -> list[float]:
    """GRPO (Group Relative Policy Optimization) advantage を計算する。

    グループ内の z-score 正規化。mean=0, std=1 に正規化される。

    Args:
        scores: K variant のスコアリスト (K >= 2)

    Returns:
        z-score 正規化された advantage。len < 2 の場合は空リスト。
        std=0 の場合は全て 0.0。

    Examples:
        >>> grpo_advantage([1.0, 2.0, 3.0])  # z-scores
        [-1.2247..., 0.0, 1.2247...]
    """
    k = len(scores)
    if k < 2:
        return []

    mean = sum(scores) / k
    variance = sum((s - mean) ** 2 for s in scores) / k
    std = math.sqrt(variance)

    if std == 0:
        return [0.0] * k

    return [round((s - mean) / std, 10) for s in scores]


def normalize_advantages(deltas: list[float]) -> list[float]:
    """Advantage 値を z-score 正規化する。

    Args:
        deltas: 正規化対象の delta リスト

    Returns:
        z-score 正規化されたリスト。
        len < 2 の場合はそのまま返す。std=0 の場合は全て 0.0。
    """
    if len(deltas) < 2:
        return list(deltas)

    mean = sum(deltas) / len(deltas)
    variance = sum((d - mean) ** 2 for d in deltas) / len(deltas)
    std = math.sqrt(variance)

    if std == 0:
        return [0.0] * len(deltas)

    return [round((d - mean) / std, 10) for d in deltas]


def importance_weight(
    ver_cur: str,
    ver_data: str,
    change_count: int = 0,
    decay_rate: float = 0.1,
) -> float:
    """Importance Sampling の重みを計算する。

    設定バージョンが異なる過去データの重みを割り引く。
    同一バージョンなら 1.0、バージョンが異なり変更回数が多いほど
    重みが小さくなる（指数減衰）。

    Args:
        ver_cur: 現在の設定バージョン (config_version)
        ver_data: データ記録時の設定バージョン
        change_count: バージョン間の変更回数
        decay_rate: 減衰率 (0.0 で減衰なし)

    Returns:
        重み (0.0, 1.0] の範囲。同一バージョンは 1.0。
    """
    if ver_cur == ver_data:
        return 1.0

    if change_count <= 0:
        return 1.0

    return round(math.exp(-decay_rate * change_count), 10)


def clip_ratio(after: float, before: float, epsilon: float = 0.2) -> float:
    """変更比率をクリップする。

    PPO スタイルのクリッピング。変更比率 (after/before) を
    [1-epsilon, 1+epsilon] の範囲に制限する。

    Args:
        after: 変更後の値
        before: 変更前の値
        epsilon: クリップ範囲 (デフォルト 0.2 = ±20%)

    Returns:
        クリップされた比率。before=0 の場合は 1.0。
    """
    epsilon = abs(epsilon)

    if before == 0:
        return 1.0

    ratio = after / before
    return round(max(1.0 - epsilon, min(1.0 + epsilon, ratio)), 10)


def step_credit(
    outcome: float,
    invocations: list[dict],
    events: list[dict],
) -> dict[str, float]:
    """Per-step credit assignment: 各スキルの寄与度を計算する。

    セッション outcome をスキルの呼び出し回数に比例して配分する。

    Args:
        outcome: セッション全体の outcome スコア (0.0-1.0)
        invocations: スキル呼び出しイベントのリスト
            各要素は {"skill_name": str, ...} を含む
        events: セッション全体のイベントリスト (未使用、将来の拡張用)

    Returns:
        {skill_name: credit_score} の辞書。空の場合は空辞書。
    """
    if not invocations:
        return {}

    if outcome == 0:
        return {
            inv.get("skill_name", ""): 0.0
            for inv in invocations
            if inv.get("skill_name")
        }

    # スキルごとの呼び出し回数を集計
    skill_counts: dict[str, int] = {}
    for inv in invocations:
        name = inv.get("skill_name", "")
        if name:
            skill_counts[name] = skill_counts.get(name, 0) + 1

    total_invocations = sum(skill_counts.values())
    if total_invocations == 0:
        return {}

    # 呼び出し回数に比例して outcome を配分
    return {
        name: round(outcome * count / total_invocations, 4)
        for name, count in skill_counts.items()
    }
