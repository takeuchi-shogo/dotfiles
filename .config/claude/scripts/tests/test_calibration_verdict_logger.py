"""Tests for calibration-verdict-logger.py."""

import sys
from importlib import import_module
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "learner"))

logger = import_module("calibration-verdict-logger")


@pytest.fixture(autouse=True)
def isolate_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOEVOLVE_DATA_DIR", str(tmp_path))
    return tmp_path


def _fields(key, auto, verdict, scope="cc", corrected=None):
    return {
        "key": key,
        "scope": scope,
        "auto": auto,
        "verdict": verdict,
        "corrected": corrected,
        "note": "",
        "report": "2026-06-06",
    }


class TestLogValidation:
    def test_missing_key_raises(self):
        with pytest.raises(ValueError, match="key"):
            logger.log_verdict(_fields("", "mechanical", "agree"))

    def test_bad_auto_raises(self):
        with pytest.raises(ValueError, match="auto"):
            logger.log_verdict(_fields("k1", "bogus", "agree"))

    def test_bad_verdict_raises(self):
        with pytest.raises(ValueError, match="verdict"):
            logger.log_verdict(_fields("k1", "mechanical", "maybe"))

    def test_bad_corrected_raises(self):
        with pytest.raises(ValueError, match="corrected"):
            logger.log_verdict(
                _fields("k1", "mechanical", "disagree", corrected="bogus")
            )

    def test_agree_with_conflicting_corrected_raises(self):
        with pytest.raises(ValueError, match="矛盾"):
            logger.log_verdict(
                _fields("k1", "mechanical", "agree", corrected="advisory")
            )

    def test_valid_log_writes_entry(self, isolate_data_dir):
        entry = logger.log_verdict(_fields("k1", "mechanical", "agree"))
        assert entry["key"] == "k1"
        ledger = isolate_data_dir / "learnings" / "triage-calibration.jsonl"
        assert ledger.exists()
        assert ledger.read_text().strip().count("\n") == 0  # 1 line


class TestStats:
    def test_empty_stats(self):
        stats = logger.compute_stats([])
        assert stats["total_verdicts"] == 0
        assert stats["agreement_rate"] is None

    def test_agreement_rate_and_allowlist(self):
        logger.log_verdict(_fields("k1", "mechanical", "agree", scope="cc-bash"))
        logger.log_verdict(_fields("k2", "mechanical", "disagree", scope="review-gate"))
        logger.log_verdict(_fields("k3", "advisory", "agree", scope="absorb"))
        stats = logger.compute_stats(logger.read_jsonl(logger._ledger_path()))
        assert stats["total_verdicts"] == 3
        assert stats["agreement_rate"] == round(2 / 3, 3)
        # mechanical: k1 agree, k2 disagree -> allowlist only k1/cc-bash
        assert stats["mechanical_confirmed"]["count"] == 1
        assert stats["mechanical_confirmed"]["scopes"] == ["cc-bash"]
        assert stats["per_class"]["mechanical"]["agreement_rate"] == 0.5

    def test_latest_verdict_wins_on_rejudge(self):
        # 同一 key を再裁定 -> 最新 (disagree) が採用される
        logger.log_verdict(_fields("k1", "mechanical", "agree"))
        logger.log_verdict(
            _fields("k1", "mechanical", "disagree", corrected="advisory")
        )
        stats = logger.compute_stats(logger.read_jsonl(logger._ledger_path()))
        assert stats["total_verdicts"] == 1
        assert stats["agreement_rate"] == 0.0
        assert stats["mechanical_confirmed"]["count"] == 0
