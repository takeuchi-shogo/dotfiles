#!/usr/bin/env python3
"""Tests for checkpoint_recover.py."""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestCheckpointRecover(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.state_dir = Path(self.tmpdir) / "session-state"
        self.state_dir.mkdir(parents=True)
        os.environ["CLAUDE_SESSION_STATE_DIR"] = str(self.state_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        os.environ.pop("CLAUDE_SESSION_STATE_DIR", None)

    def test_no_checkpoint_no_output(self):
        from checkpoint_recover import check_recovery
        result = check_recovery(self.state_dir)
        self.assertIsNone(result)

    def test_normal_exit_no_recovery(self):
        from checkpoint_recover import check_recovery
        now = datetime.now(timezone.utc)
        cp = {"timestamp": now.isoformat(), "trigger": "manual", "working_on": "test"}
        (self.state_dir / "last-checkpoint.json").write_text(json.dumps(cp))
        ss = {"timestamp": (now + timedelta(seconds=10)).isoformat()}
        (self.state_dir / "last-session.json").write_text(json.dumps(ss))

        result = check_recovery(self.state_dir)
        self.assertIsNone(result)

    def test_abnormal_exit_triggers_recovery(self):
        from checkpoint_recover import check_recovery
        now = datetime.now(timezone.utc)
        cp = {
            "timestamp": now.isoformat(),
            "trigger": "auto:edit_threshold",
            "working_on": "auth rollout",
            "focus": ["src/auth.ts"],
            "branch": "feat/auth",
            "git_status": "M src/auth.ts",
            "edit_count": 20,
        }
        (self.state_dir / "last-checkpoint.json").write_text(json.dumps(cp))

        result = check_recovery(self.state_dir)
        self.assertIsNotNone(result)
        self.assertIn("auth rollout", result)
        self.assertIn("feat/auth", result)

    def test_old_checkpoint_ignored(self):
        from checkpoint_recover import check_recovery
        old = datetime.now(timezone.utc) - timedelta(hours=25)
        cp = {"timestamp": old.isoformat(), "trigger": "manual", "working_on": "old"}
        (self.state_dir / "last-checkpoint.json").write_text(json.dumps(cp))

        result = check_recovery(self.state_dir)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
