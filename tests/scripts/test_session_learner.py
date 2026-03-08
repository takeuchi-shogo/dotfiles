import json
import os
import sys
import tempfile
import importlib
from pathlib import Path

scripts_dir = str(Path(__file__).resolve().parent.parent.parent / ".config" / "claude" / "scripts")
sys.path.insert(0, scripts_dir)


def _import_session_learner():
    """ハイフン付きファイル名 session-learner.py をインポートする。"""
    spec = importlib.util.spec_from_file_location(
        "session_learner",
        os.path.join(scripts_dir, "session-learner.py"),
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
