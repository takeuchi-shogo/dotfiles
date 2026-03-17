import json
import os
import sys
import tempfile
import importlib
from pathlib import Path

scripts_dir = str(
    Path(__file__).resolve().parent.parent.parent / ".config" / "claude" / "scripts"
)
lib_dir = os.path.join(scripts_dir, "lib")
learner_dir = os.path.join(scripts_dir, "learner")
sys.path.insert(0, scripts_dir)
sys.path.insert(0, lib_dir)


def _import_session_learner():
    """ハイフン付きファイル名 session-learner.py をインポートする。"""
    spec = importlib.util.spec_from_file_location(
        "session_learner",
        os.path.join(learner_dir, "session-learner.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestSessionLearner:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        os.environ["AUTOEVOLVE_DATA_DIR"] = self.tmpdir

    def teardown_method(self):
        os.environ.pop("AUTOEVOLVE_DATA_DIR", None)

    def test_build_session_summary_with_events(self):
        from session_events import emit_event

        emit_event("error", {"message": "TypeError", "command": "npm test"})
        emit_event("error", {"message": "ReferenceError", "command": "node app.js"})
        emit_event("quality", {"rule": "GP-004", "file": "src/app.ts"})

        session_learner = _import_session_learner()
        summary = session_learner.build_session_summary(cwd="/tmp/test-project")

        assert summary["errors_count"] == 2
        assert summary["quality_issues"] == 1
        assert summary["project"] == "test-project"

    def test_build_session_summary_empty(self):
        session_learner = _import_session_learner()
        summary = session_learner.build_session_summary(cwd="/tmp/test-project")
        assert summary["errors_count"] == 0
        assert summary["quality_issues"] == 0
        assert summary["total_events"] == 0

    def test_process_flushes_events_to_learnings(self):
        from session_events import emit_event

        emit_event("error", {"message": "TypeError", "command": "npm test"})

        session_learner = _import_session_learner()
        session_learner.process_session(cwd="/tmp/test-project")

        errors_path = Path(self.tmpdir) / "learnings" / "errors.jsonl"
        assert errors_path.exists()

        metrics_path = Path(self.tmpdir) / "metrics" / "session-metrics.jsonl"
        assert metrics_path.exists()

    def test_process_skips_when_no_events(self):
        session_learner = _import_session_learner()
        session_learner.process_session(cwd="/tmp/test-project")

        metrics_path = Path(self.tmpdir) / "metrics" / "session-metrics.jsonl"
        assert not metrics_path.exists()

    def test_session_outcome_clean_success(self):
        session_learner = _import_session_learner()
        summary = session_learner.build_session_summary(cwd="/tmp/test")
        assert summary["outcome"] == "clean_success"

    def test_session_outcome_failure(self):
        from session_events import emit_event

        emit_event("error", {"message": "TypeError", "command": "npm test"})
        session_learner = _import_session_learner()
        summary = session_learner.build_session_summary(cwd="/tmp/test")
        assert summary["outcome"] == "failure"

    def test_session_outcome_recovery(self):
        from session_events import emit_event

        emit_event("error", {"message": "TypeError", "command": "npm test"})
        emit_event("correction", {"message": "Fixed TypeError"})
        session_learner = _import_session_learner()
        summary = session_learner.build_session_summary(cwd="/tmp/test")
        assert summary["outcome"] == "recovery"

    def test_process_adds_generalized_fields(self):
        from session_events import emit_event

        emit_event(
            "error", {"message": "Error in /Users/test/app.ts", "command": "npm test"}
        )
        session_learner = _import_session_learner()
        session_learner.process_session(cwd="/tmp/test")

        errors_path = Path(self.tmpdir) / "learnings" / "errors.jsonl"
        data = json.loads(errors_path.read_text().strip())
        assert "generalized_message" in data
        assert "/Users/test/" not in data["generalized_message"]

    def test_recovery_tips_extracted(self):
        from session_events import emit_event

        emit_event(
            "error", {"message": "TypeError: x is undefined", "command": "npm test"}
        )
        emit_event("correction", {"message": "Fixed by adding null check"})

        session_learner = _import_session_learner()
        session_learner.process_session(cwd="/tmp/test")

        tips_path = Path(self.tmpdir) / "learnings" / "recovery-tips.jsonl"
        assert tips_path.exists()
        data = json.loads(tips_path.read_text().strip())
        assert "TypeError" in data["error_pattern"]
        assert data["recovery_action"] != ""

    def test_no_recovery_tips_without_corrections(self):
        from session_events import emit_event

        emit_event("error", {"message": "TypeError", "command": "npm test"})

        session_learner = _import_session_learner()
        session_learner.process_session(cwd="/tmp/test")

        tips_path = Path(self.tmpdir) / "learnings" / "recovery-tips.jsonl"
        assert not tips_path.exists()

    def test_proposal_accept_rate_tracking(self):
        """Proposal verdict events are aggregated into accept_rate metric."""
        from session_events import emit_proposal_verdict

        # 3 keep, 1 revert → accept_rate = 0.75
        for i, v in enumerate(["keep", "keep", "revert", "keep"], 1):
            emit_proposal_verdict(
                "test-skill", f"hyp-{i}", v, 0.5, 0.6 if v == "keep" else 0.4, i
            )

        sl = _import_session_learner()
        summary = sl.build_session_summary(cwd=self.tmpdir)
        proposals = [e for e in summary["_events"] if e.get("category") == "proposal"]
        assert len(proposals) == 4

    def test_proposal_accept_rate_in_metrics(self):
        """Accept rate appears in session metrics when proposals exist."""
        import pytest
        from session_events import emit_proposal_verdict

        emit_proposal_verdict("s", "h", "keep", 0.5, 0.7, 1)
        emit_proposal_verdict("s", "h", "revert", 0.7, 0.6, 2)

        sl = _import_session_learner()
        summary = sl.build_session_summary(cwd=self.tmpdir)
        pm = sl._compute_proposal_metrics(summary["_events"])
        assert pm["proposal_count"] == 2
        assert pm["accept_rate"] == pytest.approx(0.5)
        assert pm["consecutive_rejects"] == 1
