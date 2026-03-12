import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parent.parent.parent / ".config" / "claude" / "scripts"
    ),
)


def _make_trace(
    category: str,
    message: str = "test message",
    failure_mode: str = "FM-001",
    importance: float = 0.5,
    ts_offset_hours: int = 0,
) -> dict:
    """Helper to create a trace entry."""
    ts = datetime.now(timezone.utc) - timedelta(hours=ts_offset_hours)
    return {
        "timestamp": ts.isoformat(),
        "category": category,
        "message": message,
        "importance": importance,
        "failure_mode": failure_mode,
        "confidence": 0.8,
        "scored_by": "rule",
        "promotion_status": "pending",
    }


class TestTraceSampler:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.original_env = os.environ.get("AUTOEVOLVE_DATA_DIR")
        os.environ["AUTOEVOLVE_DATA_DIR"] = self.tmpdir
        self.learnings_dir = Path(self.tmpdir) / "learnings"
        self.learnings_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if self.original_env is None:
            os.environ.pop("AUTOEVOLVE_DATA_DIR", None)
        else:
            os.environ["AUTOEVOLVE_DATA_DIR"] = self.original_env

    def _write_jsonl(self, filename: str, traces: list[dict]) -> None:
        path = self.learnings_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            for t in traces:
                f.write(json.dumps(t, ensure_ascii=False) + "\n")

    # --- sample_recent_traces ---

    def test_sample_recent_traces_returns_n_items(self):
        from lib.trace_sampler import sample_recent_traces

        traces = [_make_trace("error", f"msg-{i}") for i in range(30)]
        self._write_jsonl("errors.jsonl", traces)

        result = sample_recent_traces(n=20)
        assert len(result) == 20

    def test_sample_recent_traces_diverse_categories(self):
        from lib.trace_sampler import sample_recent_traces

        errors = [_make_trace("error", f"err-{i}") for i in range(15)]
        qualities = [_make_trace("quality", f"qual-{i}") for i in range(15)]
        self._write_jsonl("errors.jsonl", errors)
        self._write_jsonl("quality-issues.jsonl", qualities)

        result = sample_recent_traces(n=20)
        categories = {t["category"] for t in result}
        assert "error" in categories
        assert "quality" in categories

    def test_sample_recent_traces_empty(self):
        from lib.trace_sampler import sample_recent_traces

        result = sample_recent_traces()
        assert result == []

    def test_sample_recent_traces_excludes_review_files(self):
        """review-findings.jsonl and review-feedback.jsonl must be excluded."""
        from lib.trace_sampler import sample_recent_traces

        errors = [_make_trace("error", f"err-{i}") for i in range(5)]
        findings = [_make_trace("quality", f"finding-{i}") for i in range(10)]
        feedback = [_make_trace("quality", f"feedback-{i}") for i in range(10)]
        self._write_jsonl("errors.jsonl", errors)
        self._write_jsonl("review-findings.jsonl", findings)
        self._write_jsonl("review-feedback.jsonl", feedback)

        result = sample_recent_traces(n=20)
        messages = [t.get("message", "") for t in result]
        assert all("finding" not in m for m in messages)
        assert all("feedback" not in m for m in messages)
        assert len(result) == 5

    def test_sample_recent_traces_n_less_than_categories(self):
        """n < number of categories should return at most n items."""
        from lib.trace_sampler import sample_recent_traces

        for cat in ("error", "quality", "pattern", "correction"):
            self._write_jsonl(f"{cat}.jsonl", [_make_trace(cat, f"msg-{cat}")])

        result = sample_recent_traces(n=1)
        assert len(result) <= 1

    # --- sample_unclassified_traces ---

    def test_sample_unclassified_returns_empty_fm(self):
        from lib.trace_sampler import sample_unclassified_traces

        classified = [_make_trace("error", "classified", failure_mode="FM-001")]
        unclassified_empty = [
            _make_trace("error", "unclassified-empty", failure_mode="")
        ]
        unclassified_missing = [
            {
                "timestamp": "2026-01-01T00:00:00Z",
                "category": "pattern",
                "message": "no-fm",
            }
        ]
        self._write_jsonl("errors.jsonl", classified + unclassified_empty)
        self._write_jsonl("patterns.jsonl", unclassified_missing)

        result = sample_unclassified_traces()
        assert len(result) == 2
        messages = {t["message"] for t in result}
        assert "unclassified-empty" in messages
        assert "no-fm" in messages
        assert "classified" not in messages

    # --- format_for_review ---

    def test_format_for_review(self):
        from lib.trace_sampler import format_for_review

        traces = [
            _make_trace(
                "error", "Short message", failure_mode="FM-001", importance=0.9
            ),
            _make_trace("quality", "A" * 100, failure_mode="FM-002", importance=0.6),
        ]
        output = format_for_review(traces)

        assert "| # |" in output
        assert "| timestamp |" in output
        assert "| category |" in output
        assert "| failure_mode |" in output
        assert "| importance |" in output
        assert "Short message" in output
        assert "error" in output
        assert "quality" in output
        assert "FM-001" in output
        # Long message should be truncated
        assert "A" * 100 not in output
        assert "A" * 57 + "..." in output

    def test_format_for_review_empty(self):
        from lib.trace_sampler import format_for_review

        output = format_for_review([])
        assert "| # |" in output
