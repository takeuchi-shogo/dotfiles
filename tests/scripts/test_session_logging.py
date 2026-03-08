import json
import logging
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / ".config" / "claude" / "scripts"))


class TestSessionLogging:

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        os.environ["AUTOEVOLVE_DATA_DIR"] = self.tmpdir
        # Reset logger handlers to force re-init with new data dir
        logger = logging.getLogger("autoevolve")
        logger.handlers.clear()

    def teardown_method(self):
        os.environ.pop("AUTOEVOLVE_DATA_DIR", None)
        logger = logging.getLogger("autoevolve")
        logger.handlers.clear()

    def test_log_file_created_on_emit(self):
        from session_events import emit_event
        emit_event("error", {"message": "test"})
        log_path = Path(self.tmpdir) / "logs" / "autoevolve.log"
        assert log_path.exists()
        content = log_path.read_text()
        assert "emit" in content.lower()

    def test_log_captures_flush(self):
        from session_events import emit_event, flush_session
        emit_event("error", {"message": "test"})
        flush_session()
        log_path = Path(self.tmpdir) / "logs" / "autoevolve.log"
        content = log_path.read_text()
        assert "flush" in content.lower()

    def test_log_captures_error(self):
        """emit_event should not crash even if data dir is broken."""
        from session_events import emit_event
        # Use a path that can't be written (file instead of directory)
        bad_path = Path(self.tmpdir) / "current-session.jsonl"
        bad_path.mkdir(parents=True, exist_ok=True)  # Make it a directory so write fails
        # This should log error but not crash
        emit_event("error", {"message": "test"})
        # The function should have completed without raising

    def test_corrupt_jsonl_logged_as_warning(self):
        from session_events import emit_event, flush_session
        # Write valid event then corrupt line
        emit_event("error", {"message": "valid"})
        temp_path = Path(self.tmpdir) / "current-session.jsonl"
        with open(temp_path, "a") as f:
            f.write("this is not json\n")
        events = flush_session()
        assert len(events) == 1  # Only the valid one
        log_path = Path(self.tmpdir) / "logs" / "autoevolve.log"
        content = log_path.read_text()
        assert "warn" in content.lower() or "skip" in content.lower()
