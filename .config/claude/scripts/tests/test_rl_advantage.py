"""Tests for rl_advantage.py — RL-inspired advantage estimation functions."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from rl_advantage import (
    clip_ratio,
    grpo_advantage,
    importance_weight,
    normalize_advantages,
    rloo_advantage,
    step_credit,
)


# --- rloo_advantage ---


class TestRlooAdvantage:
    def test_k4_known_values(self):
        # baseline_i = (sum - score_i) / (K-1)
        # [1,2,3,4]: baselines = [3.0, 2.667, 2.333, 2.0]
        result = rloo_advantage([1.0, 2.0, 3.0, 4.0])
        assert len(result) == 4
        assert result == pytest.approx([-2.0, -2 / 3, 2 / 3, 2.0], abs=1e-8)

    def test_empty(self):
        assert rloo_advantage([]) == []

    def test_single_element(self):
        assert rloo_advantage([5.0]) == []

    def test_two_elements(self):
        result = rloo_advantage([1.0, 3.0])
        assert len(result) == 2
        assert result[0] == pytest.approx(-2.0)
        assert result[1] == pytest.approx(2.0)

    def test_all_same(self):
        result = rloo_advantage([5.0, 5.0, 5.0])
        assert result == [0.0, 0.0, 0.0]

    def test_sum_approximately_zero(self):
        """Advantages should sum to approximately zero."""
        result = rloo_advantage([1.0, 2.0, 3.0, 4.0, 5.0])
        assert sum(result) == pytest.approx(0.0, abs=1e-8)


# --- grpo_advantage ---


class TestGrpoAdvantage:
    def test_z_score_properties(self):
        result = grpo_advantage([1.0, 2.0, 3.0])
        # mean should be ~0
        assert sum(result) / len(result) == pytest.approx(0.0, abs=1e-8)
        # std should be ~1
        variance = sum(r**2 for r in result) / len(result)
        assert math.sqrt(variance) == pytest.approx(1.0, abs=1e-8)

    def test_empty(self):
        assert grpo_advantage([]) == []

    def test_single_element(self):
        assert grpo_advantage([5.0]) == []

    def test_std_zero(self):
        result = grpo_advantage([3.0, 3.0, 3.0])
        assert result == [0.0, 0.0, 0.0]

    def test_two_elements(self):
        result = grpo_advantage([0.0, 2.0])
        assert len(result) == 2
        assert result[0] < 0
        assert result[1] > 0


# --- normalize_advantages ---


class TestNormalizeAdvantages:
    def test_basic_z_score(self):
        result = normalize_advantages([1.0, 2.0, 3.0, 4.0, 5.0])
        assert sum(result) / len(result) == pytest.approx(0.0, abs=1e-8)

    def test_single_element(self):
        assert normalize_advantages([5.0]) == [5.0]

    def test_empty(self):
        assert normalize_advantages([]) == []

    def test_all_same(self):
        result = normalize_advantages([2.0, 2.0, 2.0])
        assert result == [0.0, 0.0, 0.0]


# --- importance_weight ---


class TestImportanceWeight:
    def test_same_version(self):
        assert importance_weight("abc123", "abc123") == 1.0

    def test_decay_zero_gives_one(self):
        assert importance_weight("v1", "v2", change_count=5, decay_rate=0.0) == 1.0

    def test_large_count_approaches_zero(self):
        w = importance_weight("v1", "v2", change_count=100, decay_rate=0.1)
        assert w < 0.001

    def test_negative_count_gives_one(self):
        assert importance_weight("v1", "v2", change_count=-1) == 1.0

    def test_zero_count_gives_one(self):
        assert importance_weight("v1", "v2", change_count=0) == 1.0

    def test_moderate_decay(self):
        w = importance_weight("v1", "v2", change_count=2, decay_rate=0.1)
        expected = math.exp(-0.2)
        assert w == pytest.approx(expected)


# --- clip_ratio ---


class TestClipRatio:
    def test_within_range(self):
        assert clip_ratio(1.1, 1.0, epsilon=0.2) == pytest.approx(1.1)

    def test_upper_clip(self):
        assert clip_ratio(2.0, 1.0, epsilon=0.2) == pytest.approx(1.2)

    def test_lower_clip(self):
        assert clip_ratio(0.5, 1.0, epsilon=0.2) == pytest.approx(0.8)

    def test_before_zero(self):
        assert clip_ratio(5.0, 0.0) == 1.0

    def test_boundary_upper(self):
        assert clip_ratio(1.2, 1.0, epsilon=0.2) == pytest.approx(1.2)

    def test_boundary_lower(self):
        assert clip_ratio(0.8, 1.0, epsilon=0.2) == pytest.approx(0.8)

    def test_negative_epsilon_uses_abs(self):
        assert clip_ratio(2.0, 1.0, epsilon=-0.2) == pytest.approx(1.2)

    def test_exact_ratio(self):
        assert clip_ratio(1.0, 1.0) == pytest.approx(1.0)


# --- step_credit ---


class TestStepCredit:
    def test_single_skill(self):
        invocations = [{"skill_name": "review"}]
        result = step_credit(1.0, invocations, [])
        assert result == {"review": pytest.approx(1.0)}

    def test_two_skills_proportional(self):
        invocations = [
            {"skill_name": "review"},
            {"skill_name": "review"},
            {"skill_name": "test"},
        ]
        result = step_credit(0.9, invocations, [])
        assert result["review"] == pytest.approx(0.6)
        assert result["test"] == pytest.approx(0.3)

    def test_empty_invocations(self):
        assert step_credit(1.0, [], []) == {}

    def test_outcome_zero(self):
        invocations = [{"skill_name": "review"}]
        result = step_credit(0.0, invocations, [])
        assert result == {"review": 0.0}

    def test_no_skill_name(self):
        invocations = [{"other": "data"}]
        result = step_credit(1.0, invocations, [])
        assert result == {}

    def test_credits_sum_to_outcome(self):
        invocations = [
            {"skill_name": "a"},
            {"skill_name": "b"},
            {"skill_name": "c"},
        ]
        result = step_credit(0.6, invocations, [])
        assert sum(result.values()) == pytest.approx(0.6)

    def test_step_quality_weighting(self):
        """PRM 的ステップ品質重み付けのテスト。"""
        invocations = [
            {"skill_name": "review"},
            {"skill_name": "review"},
            {"skill_name": "test"},
        ]
        # review: quality=1.0, test: quality=0.0 → review が全 credit を取る
        quality = {"review": 1.0, "test": 0.0}
        result = step_credit(0.9, invocations, [], step_quality=quality)
        assert result["review"] == pytest.approx(0.9)
        assert result["test"] == pytest.approx(0.0)

    def test_step_quality_balanced(self):
        """品質が同じなら呼び出し回数比で配分。"""
        invocations = [
            {"skill_name": "a"},
            {"skill_name": "a"},
            {"skill_name": "b"},
        ]
        quality = {"a": 0.8, "b": 0.8}
        result = step_credit(0.9, invocations, [], step_quality=quality)
        # 品質同じなので回数比 2:1 で配分
        assert result["a"] == pytest.approx(0.6)
        assert result["b"] == pytest.approx(0.3)

    def test_step_quality_default(self):
        """未知のスキルはデフォルト 0.5 で計算。"""
        invocations = [{"skill_name": "unknown"}]
        quality = {}  # 空
        result = step_credit(1.0, invocations, [], step_quality=quality)
        assert result["unknown"] == pytest.approx(1.0)


# --- margin_advantage ---


class TestMarginAdvantage:
    def test_a_better(self):
        from rl_advantage import margin_advantage

        assert margin_advantage(0.9, 0.6) == pytest.approx(0.3)

    def test_b_better(self):
        from rl_advantage import margin_advantage

        assert margin_advantage(0.4, 0.7) == pytest.approx(-0.3)

    def test_equal(self):
        from rl_advantage import margin_advantage

        assert margin_advantage(0.5, 0.5) == pytest.approx(0.0)


# --- plackett_luce_ranking ---


class TestPlackettLuceRanking:
    def test_sums_to_one(self):
        from rl_advantage import plackett_luce_ranking

        result = plackett_luce_ranking([1.0, 2.0, 3.0, 4.0])
        assert sum(result) == pytest.approx(1.0)

    def test_ordering(self):
        from rl_advantage import plackett_luce_ranking

        result = plackett_luce_ranking([1.0, 3.0, 2.0])
        # highest score gets highest probability
        assert result[1] > result[2] > result[0]

    def test_empty(self):
        from rl_advantage import plackett_luce_ranking

        assert plackett_luce_ranking([]) == []

    def test_single(self):
        from rl_advantage import plackett_luce_ranking

        assert plackett_luce_ranking([5.0]) == []

    def test_two_elements_sums_to_one(self):
        from rl_advantage import plackett_luce_ranking

        result = plackett_luce_ranking([1.0, 2.0])
        assert sum(result) == pytest.approx(1.0)
        assert result[1] > result[0]

    def test_equal_scores(self):
        from rl_advantage import plackett_luce_ranking

        result = plackett_luce_ranking([5.0, 5.0, 5.0])
        assert all(r == pytest.approx(1 / 3) for r in result)
