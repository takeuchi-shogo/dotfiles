import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parent.parent.parent / ".config" / "claude" / "scripts"
    ),
)


class TestEvaluatorMetrics:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.original_env = os.environ.get("AUTOEVOLVE_DATA_DIR")
        os.environ["AUTOEVOLVE_DATA_DIR"] = self.tmpdir

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if self.original_env is None:
            os.environ.pop("AUTOEVOLVE_DATA_DIR", None)
        else:
            os.environ["AUTOEVOLVE_DATA_DIR"] = self.original_env

    def _write_jsonl(self, filename: str, entries: list[dict]) -> None:
        """Helper to write JSONL entries under learnings/."""
        path = Path(self.tmpdir) / "learnings" / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def test_compute_reviewer_accuracy(self):
        from lib.evaluator_metrics import compute_reviewer_accuracy

        findings = [
            {"id": "f1", "reviewer": "code-reviewer", "failure_mode": "FM-001"},
            {"id": "f2", "reviewer": "code-reviewer", "failure_mode": "FM-002"},
            {"id": "f3", "reviewer": "security-reviewer", "failure_mode": "FM-003"},
            {"id": "f4", "reviewer": "security-reviewer", "failure_mode": "FM-001"},
        ]
        feedback = [
            {"finding_id": "f1", "outcome": "accepted"},
            {"finding_id": "f2", "outcome": "ignored"},
            {"finding_id": "f3", "outcome": "accepted"},
            {"finding_id": "f4", "outcome": "accepted"},
        ]
        self._write_jsonl("review-findings.jsonl", findings)
        self._write_jsonl("review-feedback.jsonl", feedback)

        result = compute_reviewer_accuracy()

        assert "code-reviewer" in result
        assert result["code-reviewer"]["total"] == 2
        assert result["code-reviewer"]["accepted"] == 1
        assert result["code-reviewer"]["ignored"] == 1
        assert result["code-reviewer"]["accept_rate"] == 0.5

        assert "security-reviewer" in result
        assert result["security-reviewer"]["total"] == 2
        assert result["security-reviewer"]["accepted"] == 2
        assert result["security-reviewer"]["ignored"] == 0
        assert result["security-reviewer"]["accept_rate"] == 1.0

    def test_compute_fm_accuracy(self):
        from lib.evaluator_metrics import compute_fm_accuracy

        findings = [
            {"id": "f1", "reviewer": "code-reviewer", "failure_mode": "FM-001"},
            {"id": "f2", "reviewer": "code-reviewer", "failure_mode": "FM-001"},
            {"id": "f3", "reviewer": "code-reviewer", "failure_mode": "FM-002"},
            {"id": "f4", "reviewer": "code-reviewer", "failure_mode": "FM-002"},
            {"id": "f5", "reviewer": "code-reviewer", "failure_mode": ""},
        ]
        feedback = [
            {"finding_id": "f1", "outcome": "accepted"},
            {"finding_id": "f2", "outcome": "accepted"},
            {"finding_id": "f3", "outcome": "ignored"},
            {"finding_id": "f4", "outcome": "ignored"},
            {"finding_id": "f5", "outcome": "accepted"},
        ]
        self._write_jsonl("review-findings.jsonl", findings)
        self._write_jsonl("review-feedback.jsonl", feedback)

        result = compute_fm_accuracy()

        assert "FM-001" in result
        assert result["FM-001"]["total"] == 2
        assert result["FM-001"]["accepted"] == 2
        assert result["FM-001"]["accept_rate"] == 1.0

        assert "FM-002" in result
        assert result["FM-002"]["total"] == 2
        assert result["FM-002"]["ignored"] == 2
        assert result["FM-002"]["accept_rate"] == 0.0

        # Empty FM should be skipped
        assert "" not in result

    def test_compute_hook_effectiveness(self):
        from lib.evaluator_metrics import compute_hook_effectiveness

        learnings = [
            {"failure_mode": "FM-001", "category": "error", "message": "err1"},
            {"failure_mode": "FM-001", "category": "error", "message": "err2"},
            {"failure_mode": "FM-001", "category": "error", "message": "err3"},
            {"failure_mode": "FM-002", "category": "quality", "message": "q1"},
        ]
        self._write_jsonl("errors.jsonl", learnings)

        result = compute_hook_effectiveness()

        assert "FM-001" in result
        assert result["FM-001"]["count"] == 3
        assert result["FM-001"]["recurring"] is True

        assert "FM-002" in result
        assert result["FM-002"]["count"] == 1
        assert result["FM-002"]["recurring"] is False

    def test_compute_hook_effectiveness_boundary(self):
        """count=2 should NOT be recurring (threshold is 3)."""
        from lib.evaluator_metrics import compute_hook_effectiveness

        learnings = [
            {"failure_mode": "FM-003", "category": "error", "message": "a"},
            {"failure_mode": "FM-003", "category": "error", "message": "b"},
        ]
        self._write_jsonl("errors.jsonl", learnings)

        result = compute_hook_effectiveness()
        assert result["FM-003"]["count"] == 2
        assert result["FM-003"]["recurring"] is False

    def test_empty_data(self):
        from lib.evaluator_metrics import (
            compute_fm_accuracy,
            compute_hook_effectiveness,
            compute_reviewer_accuracy,
        )

        assert compute_reviewer_accuracy() == {}
        assert compute_fm_accuracy() == {}
        assert compute_hook_effectiveness() == {}

    def test_format_evaluator_report(self):
        from lib.evaluator_metrics import format_evaluator_report

        reviewer_acc = {
            "code-reviewer": {
                "total": 10,
                "accepted": 8,
                "ignored": 2,
                "accept_rate": 0.8,
            },
        }
        fm_acc = {
            "FM-001": {
                "total": 5,
                "accepted": 4,
                "ignored": 1,
                "accept_rate": 0.8,
            },
        }
        hook_eff = {
            "FM-001": {"count": 3, "recurring": True},
            "FM-002": {"count": 1, "recurring": False},
        }

        report = format_evaluator_report(reviewer_acc, fm_acc, hook_eff)

        # Section headers
        assert "Reviewer Accuracy" in report
        assert "Failure Mode Accuracy" in report
        assert "Hook Effectiveness" in report

        # Content
        assert "code-reviewer" in report
        assert "80.0%" in report
        assert "FM-001" in report
        assert "FM-002" in report
        assert "recurring" in report.lower()
