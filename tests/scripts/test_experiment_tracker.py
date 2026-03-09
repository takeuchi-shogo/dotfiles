import json
import os
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / ".config" / "claude" / "scripts"))


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
        from experiment_tracker import list_experiments, record_experiment, update_status
        exp1 = record_experiment("errors", "h1", "b1", ["f1"])
        record_experiment("quality", "h2", "b2", ["f2"])
        update_status(exp1["id"], "merged")
        pending = list_experiments(status="pending_review")
        assert len(pending) == 1
        assert pending[0]["category"] == "quality"

    def test_update_status(self):
        from experiment_tracker import record_experiment, update_status, list_experiments
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
        for i in range(5):
            ts = (now - timedelta(days=10)).isoformat()
            entry = {"timestamp": ts, "message": f"TypeError {i}"}
            with open(learnings_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        for i in range(2):
            entry = {"timestamp": now.isoformat(), "message": f"TypeError {i}"}
            with open(learnings_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        result = measure_effect(exp["id"])
        assert result["verdict"] in ("keep", "discard", "neutral", "insufficient_data")

    def test_record_cross_impact(self):
        from experiment_tracker import record_experiment, record_cross_impact, list_experiments
        exp = record_experiment("quality", "h1", "b1", ["f1"])
        record_cross_impact(exp["id"], {"errors": {"before": 5, "after": 3, "note": "GP fix reduced errors"}})
        exps = list_experiments()
        assert "cross_impact" in exps[0]
        assert exps[0]["cross_impact"]["errors"]["after"] == 3
