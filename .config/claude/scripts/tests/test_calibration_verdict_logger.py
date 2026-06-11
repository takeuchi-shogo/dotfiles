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


def _fields(key, auto, verdict, scope="cc", corrected=None, source=None):
    fields = {
        "key": key,
        "scope": scope,
        "auto": auto,
        "verdict": verdict,
        "corrected": corrected,
        "note": "",
        "report": "2026-06-06",
    }
    if source is not None:
        fields["source"] = source
    return fields


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

    def test_default_source_is_auto_triage(self):
        entry = logger.log_verdict(_fields("k1", "mechanical", "agree"))
        assert entry["source"] == "auto-triage"

    def test_promote_classes_accepted(self):
        entry = logger.log_verdict(_fields("k1", "adopted", "agree", source="promote"))
        assert entry["auto"] == "adopted"
        assert entry["source"] == "promote"

    def test_bad_source_raises(self):
        with pytest.raises(ValueError, match="source"):
            logger.log_verdict(_fields("k1", "mechanical", "agree", source="bogus"))

    def test_cross_source_class_rejected(self):
        with pytest.raises(ValueError, match="auto"):
            logger.log_verdict(_fields("k1", "adopted", "agree"))
        with pytest.raises(ValueError, match="auto"):
            logger.log_verdict(_fields("k1", "mechanical", "agree", source="promote"))


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

    def test_per_source_separation(self):
        logger.log_verdict(_fields("k1", "mechanical", "agree"))
        logger.log_verdict(_fields("k2", "adopted", "disagree", source="promote"))
        logger.log_verdict(_fields("k3", "rejected", "agree", source="promote"))
        stats = logger.compute_stats(logger.read_jsonl(logger._ledger_path()))
        assert stats["per_source"]["auto-triage"]["n"] == 1
        assert stats["per_source"]["auto-triage"]["agreement_rate"] == 1.0
        assert stats["per_source"]["promote"]["n"] == 2
        assert stats["per_source"]["promote"]["agreement_rate"] == 0.5
        assert stats["per_class"]["adopted"]["n"] == 1
        assert stats["per_class"]["rejected"]["n"] == 1

    def test_promote_source_never_pollutes_allowlist(self):
        entries = [
            {
                "key": "k1",
                "scope": "cc-bash",
                "auto": "mechanical",
                "verdict": "agree",
                "source": "promote",
                "ts": "2026-06-11T09:00:00",
            },
            {
                "key": "k2",
                "scope": "review-gate",
                "auto": "mechanical",
                "verdict": "agree",
                "ts": "2026-06-11T09:01:00",
            },
        ]
        stats = logger.compute_stats(entries)
        assert stats["mechanical_confirmed"]["count"] == 1
        assert stats["mechanical_confirmed"]["scopes"] == ["review-gate"]

    def test_sourceless_legacy_entries_counted_as_auto_triage(self):
        entries = [
            {
                "key": "legacy",
                "scope": "cc-bash",
                "auto": "mechanical",
                "verdict": "agree",
                "ts": "2026-06-01T09:00:00",
            }
        ]
        stats = logger.compute_stats(entries)
        assert stats["per_source"]["auto-triage"]["n"] == 1
        assert stats["mechanical_confirmed"]["count"] == 1

    def test_last_windows_trend_but_not_allowlist(self):
        # PR #61 review 🟡: --last はトレンド統計のみ窓化、allowlist は全期間維持
        entries = [
            {
                "key": "old",
                "scope": "cc-bash",
                "auto": "mechanical",
                "verdict": "agree",
                "ts": "2026-06-01T09:00:00",
            },
            {
                "key": "mid",
                "scope": "review-gate",
                "auto": "advisory",
                "verdict": "disagree",
                "ts": "2026-06-02T09:00:00",
            },
            {
                "key": "new",
                "scope": "absorb",
                "auto": "mechanical",
                "verdict": "agree",
                "ts": "2026-06-03T09:00:00",
            },
        ]
        stats = logger.compute_stats(entries, last=1)
        # トレンド: 最新 1 件 (new, agree) のみ
        assert stats["window"] == 1
        assert stats["total_verdicts"] == 1
        assert stats["agreement_rate"] == 1.0
        # allowlist: 全期間の mechanical+agree (old, new) — mid は advisory で除外
        assert stats["mechanical_confirmed"]["count"] == 2
        assert stats["mechanical_confirmed"]["scopes"] == ["absorb", "cc-bash"]
