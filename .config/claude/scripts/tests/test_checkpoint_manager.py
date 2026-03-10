#!/usr/bin/env python3
"""Tests for checkpoint_manager.py."""
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestShouldCheckpoint(unittest.TestCase):

    def test_edit_threshold_triggers(self):
        from checkpoint_manager import should_checkpoint
        counter = {"count": 16, "lastReset": time.time() * 1000, "recentEdits": []}
        result = should_checkpoint(counter, last_checkpoint_time=0)
        self.assertEqual(result, "auto:edit_threshold")

    def test_below_threshold_no_trigger(self):
        from checkpoint_manager import should_checkpoint
        counter = {"count": 5, "lastReset": time.time() * 1000, "recentEdits": []}
        result = should_checkpoint(counter, last_checkpoint_time=time.time())
        self.assertFalse(result)

    def test_time_threshold_triggers(self):
        from checkpoint_manager import should_checkpoint
        counter = {"count": 3, "lastReset": time.time() * 1000, "recentEdits": []}
        old_time = time.time() - 1900
        result = should_checkpoint(counter, last_checkpoint_time=old_time)
        self.assertEqual(result, "auto:time_threshold")

    def test_cooldown_prevents_trigger(self):
        from checkpoint_manager import should_checkpoint
        counter = {"count": 20, "lastReset": time.time() * 1000, "recentEdits": []}
        recent_time = time.time() - 60
        result = should_checkpoint(counter, last_checkpoint_time=recent_time)
        self.assertFalse(result)

    def test_context_threshold_triggers(self):
        from checkpoint_manager import should_checkpoint
        counter = {"count": 3, "lastReset": time.time() * 1000, "recentEdits": []}
        result = should_checkpoint(counter, last_checkpoint_time=0, context_pct=65)
        self.assertEqual(result, "auto:context_threshold")


class TestSaveCheckpoint(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.state_dir = Path(self.tmpdir) / "session-state"
        os.environ["CLAUDE_SESSION_STATE_DIR"] = str(self.state_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        os.environ.pop("CLAUDE_SESSION_STATE_DIR", None)

    def test_creates_checkpoint_file(self):
        from checkpoint_manager import save_checkpoint
        save_checkpoint(trigger="manual", state_dir=self.state_dir, edit_count=10)
        files = list((self.state_dir / "checkpoints").glob("checkpoint-*.json"))
        self.assertEqual(len(files), 1)
        data = json.loads(files[0].read_text())
        self.assertEqual(data["trigger"], "manual")
        self.assertEqual(data["edit_count"], 10)

    def test_updates_last_checkpoint_pointer(self):
        from checkpoint_manager import save_checkpoint
        save_checkpoint(trigger="manual", state_dir=self.state_dir)
        pointer = self.state_dir / "last-checkpoint.json"
        self.assertTrue(pointer.exists())
        data = json.loads(pointer.read_text())
        self.assertEqual(data["trigger"], "manual")

    def test_keeps_max_5_checkpoints(self):
        from checkpoint_manager import save_checkpoint
        for i in range(7):
            save_checkpoint(trigger="auto:edit_threshold", state_dir=self.state_dir, edit_count=i)
            time.sleep(0.02)
        files = list((self.state_dir / "checkpoints").glob("checkpoint-*.json"))
        self.assertLessEqual(len(files), 5)

    def test_checkpoint_contains_required_fields(self):
        from checkpoint_manager import save_checkpoint
        save_checkpoint(
            trigger="auto:time_threshold",
            state_dir=self.state_dir,
            edit_count=5,
            context_pct=45,
            focus_files=["src/auth.ts"],
            active_profile="debugging",
        )
        pointer = self.state_dir / "last-checkpoint.json"
        data = json.loads(pointer.read_text())
        for field in ["timestamp", "trigger", "working_on", "focus", "branch",
                       "git_status", "edit_count", "context_usage_pct", "active_profile"]:
            self.assertIn(field, data, f"Missing field: {field}")
        self.assertEqual(data["active_profile"], "debugging")


if __name__ == "__main__":
    unittest.main()
