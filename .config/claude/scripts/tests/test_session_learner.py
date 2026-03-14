#!/usr/bin/env python3
"""Tests for session-learner.py scored output."""

import json
import os
import sys
import tempfile
import unittest
from importlib import import_module
from pathlib import Path

_scripts_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_scripts_dir))
sys.path.insert(0, str(_scripts_dir / "lib"))
sys.path.insert(0, str(_scripts_dir / "learner"))


class TestSessionLearnerScoring(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        os.environ["AUTOEVOLVE_DATA_DIR"] = self.tmpdir

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmpdir, ignore_errors=True)
        os.environ.pop("AUTOEVOLVE_DATA_DIR", None)

    def test_learnings_include_scores(self):
        from session_events import emit_event

        learner = import_module("session-learner")

        emit_event("error", {"message": "Permission denied", "command": "npm test"})
        learner.process_session(cwd=self.tmpdir)

        errors_path = Path(self.tmpdir) / "learnings" / "errors.jsonl"
        self.assertTrue(errors_path.exists())

        with open(errors_path) as f:
            entry = json.loads(f.readline())

        self.assertIn("importance", entry)
        self.assertIn("confidence", entry)
        self.assertIn("scored_by", entry)
        self.assertIn("promotion_status", entry)
        self.assertGreaterEqual(entry["importance"], 0.8)

    def test_metrics_include_score_summary(self):
        from session_events import emit_event

        learner = import_module("session-learner")

        emit_event("error", {"message": "OOM killed", "command": "build"})
        emit_event("quality", {"rule": "GP-001", "file": "x.ts", "detail": "violation"})
        emit_event("error", {"message": "warning: unused var", "command": "lint"})
        learner.process_session(cwd=self.tmpdir)

        metrics_path = Path(self.tmpdir) / "metrics" / "session-metrics.jsonl"
        with open(metrics_path) as f:
            entry = json.loads(f.readline())

        self.assertIn("high_importance_count", entry)
        self.assertIn("avg_importance", entry)
        self.assertGreaterEqual(entry["high_importance_count"], 1)
        self.assertGreater(entry["avg_importance"], 0)

    def test_skill_execution_includes_extended_fields(self):
        from session_events import emit_event, emit_skill_event, emit_skill_step

        learner = import_module("session-learner")

        emit_skill_event("invocation", {"skill_name": "test-skill"})
        emit_skill_step("test-skill", step=1, outcome="success")
        emit_skill_step(
            "test-skill",
            step=2,
            outcome="failed",
            data={"error_ref": "2026-03-14T10:00:00Z", "tool_name": "Bash"},
        )
        emit_event("error", {"message": "TypeError: x is undefined"})
        learner.process_session(cwd=self.tmpdir)

        skill_path = Path(self.tmpdir) / "learnings" / "skill-executions.jsonl"
        self.assertTrue(skill_path.exists())

        with open(skill_path) as f:
            entry = json.loads(f.readline())

        self.assertEqual(entry["skill_name"], "test-skill")
        self.assertIn("version", entry)
        self.assertIn("step_failures", entry)
        self.assertEqual(entry["step_failures"], [2])
        self.assertIn("related_error_ids", entry)
        self.assertIn("related_tools", entry)
        self.assertIn("Bash", entry["related_tools"])


if __name__ == "__main__":
    unittest.main()
