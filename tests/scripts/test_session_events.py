import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parent.parent.parent
        / ".config"
        / "claude"
        / "scripts"
        / "lib"
    ),
)


class TestSessionEvents:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.original_env = os.environ.get("AUTOEVOLVE_DATA_DIR")
        os.environ["AUTOEVOLVE_DATA_DIR"] = self.tmpdir

    def teardown_method(self):
        if self.original_env is None:
            os.environ.pop("AUTOEVOLVE_DATA_DIR", None)
        else:
            os.environ["AUTOEVOLVE_DATA_DIR"] = self.original_env

    def test_emit_event_creates_temp_file(self):
        from session_events import emit_event

        emit_event("error", {"message": "TypeError: x is not a function"})
        temp_path = Path(self.tmpdir) / "current-session.jsonl"
        assert temp_path.exists()
        line = temp_path.read_text().strip()
        data = json.loads(line)
        assert data["category"] == "error"
        assert "timestamp" in data

    def test_emit_multiple_events(self):
        from session_events import emit_event

        emit_event("error", {"message": "err1"})
        emit_event("quality", {"rule": "GP-004"})
        temp_path = Path(self.tmpdir) / "current-session.jsonl"
        lines = temp_path.read_text().strip().split("\n")
        assert len(lines) == 2

    def test_flush_session_returns_events_and_cleans_up(self):
        from session_events import emit_event, flush_session

        emit_event("error", {"message": "err1"})
        emit_event("quality", {"rule": "GP-004"})
        events = flush_session()
        assert len(events) == 2
        assert events[0]["category"] == "error"
        temp_path = Path(self.tmpdir) / "current-session.jsonl"
        assert not temp_path.exists()

    def test_flush_empty_session(self):
        from session_events import flush_session

        events = flush_session()
        assert events == []

    def test_append_to_learnings(self):
        from session_events import append_to_learnings

        append_to_learnings(
            "errors", {"message": "test error", "command": "npm run build"}
        )
        learnings_path = Path(self.tmpdir) / "learnings" / "errors.jsonl"
        assert learnings_path.exists()
        data = json.loads(learnings_path.read_text().strip())
        assert data["message"] == "test error"
        assert "timestamp" in data

    def test_append_to_metrics(self):
        from session_events import append_to_metrics

        append_to_metrics(
            {
                "project": "dotfiles",
                "errors_count": 2,
                "quality_issues": 1,
                "files_changed": 3,
            }
        )
        metrics_path = Path(self.tmpdir) / "metrics" / "session-metrics.jsonl"
        assert metrics_path.exists()
        data = json.loads(metrics_path.read_text().strip())
        assert data["project"] == "dotfiles"
        assert "timestamp" in data

    def test_emit_proposal_verdict_keep(self):
        from session_events import emit_proposal_verdict

        emit_proposal_verdict(
            skill_name="landing-page-copy",
            hypothesis="見出しに数値を強制",
            verdict="keep",
            metric_before=0.56,
            metric_after=0.72,
            iteration=1,
        )
        temp_path = Path(self.tmpdir) / "current-session.jsonl"
        data = json.loads(temp_path.read_text().strip())
        assert data["category"] == "proposal"
        assert data["verdict"] == "keep"
        assert data["skill_name"] == "landing-page-copy"
        assert data["delta"] == pytest.approx(0.16, abs=0.001)

    def test_emit_proposal_verdict_revert(self):
        from session_events import emit_proposal_verdict

        emit_proposal_verdict(
            skill_name="landing-page-copy",
            hypothesis="ワードカウント制限",
            verdict="revert",
            metric_before=0.85,
            metric_after=0.78,
            iteration=3,
        )
        temp_path = Path(self.tmpdir) / "current-session.jsonl"
        data = json.loads(temp_path.read_text().strip())
        assert data["verdict"] == "revert"
        assert data["delta"] == pytest.approx(-0.07, abs=0.001)

    def test_emit_review_scores(self):
        from session_events import emit_review_scores

        emit_review_scores(
            reviewer="code-reviewer",
            scores={
                "correctness": "4/5",
                "security": "5/5",
                "maintainability": "3/5",
                "performance": "4/5",
                "consistency": "4/5",
            },
            metadata={"weakest": "maintainability"},
        )
        scores_path = Path(self.tmpdir) / "learnings" / "review-scores.jsonl"
        assert scores_path.exists()
        data = json.loads(scores_path.read_text().strip())
        assert data["reviewer"] == "code-reviewer"
        assert data["scores"]["correctness"] == "4/5"
        assert data["weakest"] == "maintainability"
        assert "timestamp" in data
