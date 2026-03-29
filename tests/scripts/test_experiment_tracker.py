import json
import os
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path


sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parent.parent.parent / ".config" / "claude" / "scripts"
    ),
)


class TestExperimentTracker:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.original_env = os.environ.get("AUTOEVOLVE_DATA_DIR")
        os.environ["AUTOEVOLVE_DATA_DIR"] = self.tmpdir
        (Path(self.tmpdir) / "experiments").mkdir(parents=True)
        (Path(self.tmpdir) / "learnings").mkdir(parents=True)

    def teardown_method(self):
        if self.original_env is None:
            os.environ.pop("AUTOEVOLVE_DATA_DIR", None)
        else:
            os.environ["AUTOEVOLVE_DATA_DIR"] = self.original_env

    def test_record_experiment(self):
        from experiment_tracker import record_experiment

        exp = record_experiment(
            category="errors",
            hypothesis="Fix TypeError guide reduces recurrence",
            branch="autoevolve/errors-2026-03-10",
            files_changed=["references/error-fix-guides.md"],
        )
        assert exp["category"] == "errors"
        assert exp["status"] == "pending_review"
        assert exp["id"].startswith("exp-")
        registry = Path(self.tmpdir) / "experiments" / "experiment-registry.jsonl"
        assert registry.exists()
        data = json.loads(registry.read_text().strip())
        assert data["id"] == exp["id"]

    def test_list_experiments(self):
        from experiment_tracker import list_experiments, record_experiment

        record_experiment("errors", "h1", "b1", ["f1"])
        record_experiment("quality", "h2", "b2", ["f2"])
        exps = list_experiments()
        assert len(exps) == 2

    def test_list_experiments_by_status(self):
        from experiment_tracker import (
            list_experiments,
            record_experiment,
            update_status,
        )

        exp1 = record_experiment("errors", "h1", "b1", ["f1"])
        record_experiment("quality", "h2", "b2", ["f2"])
        update_status(exp1["id"], "merged")
        pending = list_experiments(status="pending_review")
        assert len(pending) == 1
        assert pending[0]["category"] == "quality"

    def test_update_status(self):
        from experiment_tracker import (
            record_experiment,
            update_status,
            list_experiments,
        )

        exp = record_experiment("errors", "h1", "b1", ["f1"])
        update_status(exp["id"], "merged")
        exps = list_experiments()
        assert exps[0]["status"] == "merged"

    def test_measure_effect_no_data(self):
        from experiment_tracker import measure_effect, record_experiment, update_status

        exp = record_experiment("errors", "h1", "b1", ["f1"])
        update_status(exp["id"], "merged")
        result = measure_effect(exp["id"])
        assert result["verdict"] == "insufficient_data"

    def test_measure_effect_with_data(self):
        from experiment_tracker import measure_effect, record_experiment, update_status

        exp = record_experiment("errors", "h1", "b1", ["f1"])
        update_status(exp["id"], "merged")
        learnings_path = Path(self.tmpdir) / "learnings" / "errors.jsonl"
        now = datetime.now(timezone.utc)
        # 5 errors within 7-day window before merge (days=3 is inside the window)
        for i in range(5):
            ts = (now - timedelta(days=3)).isoformat()
            entry = {"timestamp": ts, "message": f"TypeError {i}"}
            with open(learnings_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        # 2 errors after merge
        for i in range(2):
            entry = {"timestamp": now.isoformat(), "message": f"TypeError {i}"}
            with open(learnings_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        result = measure_effect(exp["id"])
        assert result["verdict"] == "keep"
        assert result["before_count"] == 5
        assert result["after_count"] == 2

    def test_compute_cqs_insufficient_data(self):
        from experiment_tracker import compute_cqs, record_experiment, update_status

        # 5件未満 → insufficient_data
        for i in range(3):
            exp = record_experiment("errors", f"h{i}", f"b{i}", [f"f{i}"])
            update_status(exp["id"], "merged")
        result = compute_cqs()
        assert result["status"] == "insufficient_data"
        assert result["total_experiments"] == 3

    def test_compute_cqs_with_data(self):
        from experiment_tracker import compute_cqs, record_experiment, update_status

        now = datetime.now(timezone.utc)
        learnings_path = Path(self.tmpdir) / "learnings" / "errors.jsonl"
        # 5件の merged 実験を作成（全て keep になるようデータを用意）
        for i in range(5):
            exp = record_experiment("errors", f"h{i}", f"b{i}", [f"f{i}"])
            update_status(exp["id"], "merged")
            # before: 10件, after: 5件 → -50% → keep
            for j in range(10):
                ts = (now - timedelta(days=3)).isoformat()
                entry = {"timestamp": ts, "message": f"err-{i}-{j}"}
                with open(learnings_path, "a") as f:
                    f.write(json.dumps(entry) + "\n")
            for j in range(5):
                entry = {"timestamp": now.isoformat(), "message": f"err-{i}-{j}"}
                with open(learnings_path, "a") as f:
                    f.write(json.dumps(entry) + "\n")
        result = compute_cqs()
        assert result["status"] == "ok"
        assert result["total_experiments"] == 5
        assert result["breakdown"]["keep"] == 5
        assert result["cqs"] > 0

    def test_record_cross_impact(self):
        from experiment_tracker import (
            record_experiment,
            record_cross_impact,
            list_experiments,
        )

        exp = record_experiment("quality", "h1", "b1", ["f1"])
        record_cross_impact(
            exp["id"],
            {"errors": {"before": 5, "after": 3, "note": "GP fix reduced errors"}},
        )
        exps = list_experiments()
        assert "cross_impact" in exps[0]
        assert exps[0]["cross_impact"]["errors"]["after"] == 3

    def test_record_experiment_with_transfer(self):
        from experiment_tracker import record_experiment

        exp = record_experiment(
            category="quality",
            hypothesis="Apply error-fix pattern from errors domain",
            branch="autoevolve/quality-transfer",
            files_changed=["references/golden-principles.md"],
            source_domain="errors",
            transfer_efficacy=0.75,
        )
        assert exp["source_domain"] == "errors"
        assert exp["transfer_efficacy"] == 0.75

    def test_list_experiments_transfers_only(self):
        from experiment_tracker import list_experiments, record_experiment

        record_experiment("errors", "h1", "b1", ["f1"])
        record_experiment(
            "quality",
            "h2",
            "b2",
            ["f2"],
            source_domain="errors",
            transfer_efficacy=0.8,
        )
        all_exps = list_experiments()
        assert len(all_exps) == 2
        transfers = list_experiments(transfers_only=True)
        assert len(transfers) == 1
        assert transfers[0]["source_domain"] == "errors"

    def test_transfer_report(self):
        from experiment_tracker import record_experiment, transfer_report

        record_experiment(
            "quality",
            "h1",
            "b1",
            ["f1"],
            source_domain="errors",
            transfer_efficacy=0.8,
        )
        record_experiment(
            "quality",
            "h2",
            "b2",
            ["f2"],
            source_domain="errors",
            transfer_efficacy=0.6,
        )
        report = transfer_report()
        assert "errors" in report
        assert "quality" in report
        assert "0.70" in report  # average of 0.8 and 0.6

    def test_transfer_report_no_data(self):
        from experiment_tracker import transfer_report

        report = transfer_report()
        assert "転移データなし" in report

    def test_transfer_efficacy_out_of_range(self):
        import pytest
        from experiment_tracker import record_experiment

        with pytest.raises(ValueError):
            record_experiment("quality", "h", "b", ["f"], transfer_efficacy=1.5)
        with pytest.raises(ValueError):
            record_experiment("quality", "h", "b", ["f"], transfer_efficacy=-0.1)

    # --- Task 1: Causal hypothesis fields ---

    def test_record_with_causal_hypothesis(self):
        from experiment_tracker import record_experiment, list_experiments

        exp = record_experiment(
            category="errors",
            hypothesis="Add guard for nil check",
            branch="autoevolve/errors-causal",
            files_changed=["rules/common/nil-guard.md"],
            causal_hypothesis="nil pointer errors come from unvalidated input",
            forward_plan="Extend guard to all API endpoints",
            overcorrection_risk="strict → too restrictive for internal calls",
            prior_attempts=["exp-2026-03-20-errors-001"],
        )
        assert exp["causal_hypothesis"] == (
            "nil pointer errors come from unvalidated input"
        )
        assert exp["forward_plan"] == "Extend guard to all API endpoints"
        assert exp["overcorrection_risk"] == (
            "strict → too restrictive for internal calls"
        )
        assert exp["prior_attempts"] == ["exp-2026-03-20-errors-001"]

        # Round-trip: load from registry and verify
        exps = list_experiments()
        loaded = exps[0]
        assert loaded["causal_hypothesis"] == exp["causal_hypothesis"]
        assert loaded["prior_attempts"] == exp["prior_attempts"]

    def test_record_without_causal_fields(self):
        from experiment_tracker import record_experiment

        exp = record_experiment("errors", "h1", "b1", ["f1"])
        assert "causal_hypothesis" not in exp
        assert "forward_plan" not in exp

    def test_proposer_context_includes_causal(self):
        from experiment_tracker import (
            record_experiment,
            build_proposer_context,
        )

        record_experiment(
            category="skills",
            hypothesis="Improve review skill",
            branch="autoevolve/skills-review",
            files_changed=["skills/review/SKILL.md"],
            target_skill="review",
            causal_hypothesis="Missing edge case handling",
            overcorrection_risk="Over-checking slows reviews",
        )
        ctx = build_proposer_context("review")
        assert "因果仮説" in ctx
        assert "過修正リスク" in ctx
        assert "Missing edge case" in ctx

    # --- Task 2: Improvement trend ---

    def test_trend_insufficient_data(self):
        from experiment_tracker import compute_improvement_trend

        result = compute_improvement_trend("errors", window=5)
        assert result["trend"] == "insufficient_data"

    def _create_trend_data(self, category, count, before_after_pairs):
        """トレンドテスト用ヘルパー。時間窓が重ならないよう配置。"""
        from experiment_tracker import _registry_path

        registry_path = _registry_path()
        learnings_path = Path(self.tmpdir) / "learnings" / f"{category}.jsonl"
        now = datetime.now(timezone.utc)

        for i in range(count):
            # 各実験を 20 日間隔で配置（窓 ±7 日が重ならない）
            merged_at = now - timedelta(days=(count - i) * 20)
            exp_entry = {
                "id": f"exp-trend-{category}-{i:03d}",
                "category": category,
                "hypothesis": f"h{i}",
                "branch": f"b{i}",
                "files_changed": [f"f{i}"],
                "status": "merged",
                "created_at": merged_at.isoformat(),
                "updated_at": merged_at.isoformat(),
                "merged_at": merged_at.isoformat(),
            }
            with open(registry_path, "a") as f:
                f.write(json.dumps(exp_entry) + "\n")

            bc, ac = before_after_pairs[i]
            for j in range(bc):
                ts = (merged_at - timedelta(days=3)).isoformat()
                with open(learnings_path, "a") as f:
                    f.write(
                        json.dumps({"timestamp": ts, "message": f"{i}-b{j}"}) + "\n"
                    )
            for j in range(ac):
                ts = (merged_at + timedelta(days=1)).isoformat()
                with open(learnings_path, "a") as f:
                    f.write(
                        json.dumps({"timestamp": ts, "message": f"{i}-a{j}"}) + "\n"
                    )

    def test_trend_accelerating(self):
        from experiment_tracker import compute_improvement_trend

        # older 5: before=10, after=8 → -20%
        # recent 5: before=10, after=3 → -70%
        pairs = [(10, 8)] * 5 + [(10, 3)] * 5
        self._create_trend_data("errors", 10, pairs)

        result = compute_improvement_trend("errors", window=5)
        assert result["trend"] == "accelerating"
        assert result["delta"] < -5.0

    def test_trend_saturating(self):
        from experiment_tracker import compute_improvement_trend

        # all 10: before=10, after=7 → -30% (same for all)
        pairs = [(10, 7)] * 10
        self._create_trend_data("quality", 10, pairs)

        result = compute_improvement_trend("quality", window=5)
        assert result["trend"] == "saturating"
        assert abs(result["delta"]) < 5.0

    # --- Task 5: Archive-based exploration ---

    def test_archive_snapshot_success(self):
        from experiment_tracker import (
            archive_snapshot,
            record_experiment,
            update_status,
        )

        exp = record_experiment("errors", "h1", "b1", ["f1"])
        update_status(exp["id"], "merged")

        result = archive_snapshot(exp["id"], "v1-best")
        assert result["exp_id"] == exp["id"]
        assert result["label"] == "v1-best"
        assert result["category"] == "errors"

        # ファイルに保存されていることを確認
        archive_path = Path(self.tmpdir) / "experiments" / "archive" / "snapshots.jsonl"
        assert archive_path.exists()
        first_line = archive_path.read_text().strip().split("\n")[0]
        data = json.loads(first_line)
        assert data["label"] == "v1-best"

    def test_archive_snapshot_not_merged(self):
        from experiment_tracker import archive_snapshot, record_experiment

        exp = record_experiment("errors", "h1", "b1", ["f1"])
        result = archive_snapshot(exp["id"], "v1")
        assert "error" in result

    def test_archive_snapshot_max_limit(self):
        from experiment_tracker import (
            archive_snapshot,
            record_experiment,
            update_status,
        )

        # 25 個アーカイブして最大 20 件に制限されることを確認
        for i in range(25):
            exp = record_experiment("errors", f"h{i}", f"b{i}", [f"f{i}"])
            update_status(exp["id"], "merged")
            archive_snapshot(exp["id"], f"v{i}")

        archive_path = Path(self.tmpdir) / "experiments" / "archive" / "snapshots.jsonl"
        lines = [line for line in archive_path.read_text().strip().split("\n") if line]
        assert len(lines) == 20

    def test_select_parent_variant_empty(self):
        from experiment_tracker import select_parent_variant

        result = select_parent_variant("errors")
        assert result is None

    def test_select_parent_variant_returns_snapshot(self):
        from experiment_tracker import (
            archive_snapshot,
            record_experiment,
            select_parent_variant,
            update_status,
        )

        exp = record_experiment("errors", "h1", "b1", ["f1"])
        update_status(exp["id"], "merged")
        archive_snapshot(exp["id"], "v1")

        result = select_parent_variant("errors")
        assert result is not None
        assert result["category"] == "errors"
        assert result["label"] == "v1"

    def test_select_parent_variant_filters_category(self):
        from experiment_tracker import (
            archive_snapshot,
            record_experiment,
            select_parent_variant,
            update_status,
        )

        exp1 = record_experiment("errors", "h1", "b1", ["f1"])
        update_status(exp1["id"], "merged")
        archive_snapshot(exp1["id"], "errors-v1")

        # quality カテゴリにはアーカイブなし
        result = select_parent_variant("quality")
        assert result is None
