import json
import tempfile
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / ".config" / "claude" / "scripts"))


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
        append_to_learnings("errors", {"message": "test error", "command": "npm run build"})
        learnings_path = Path(self.tmpdir) / "learnings" / "errors.jsonl"
        assert learnings_path.exists()
        data = json.loads(learnings_path.read_text().strip())
        assert data["message"] == "test error"
        assert "timestamp" in data

    def test_append_to_metrics(self):
        from session_events import append_to_metrics
        append_to_metrics({
            "project": "dotfiles",
            "errors_count": 2,
            "quality_issues": 1,
            "files_changed": 3,
        })
        metrics_path = Path(self.tmpdir) / "metrics" / "session-metrics.jsonl"
        assert metrics_path.exists()
        data = json.loads(metrics_path.read_text().strip())
        assert data["project"] == "dotfiles"
        assert "timestamp" in data
