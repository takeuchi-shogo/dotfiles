import json
import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "epc",
    Path(__file__).resolve().parents[2]
    / ".config/claude/scripts/learner/extract-promotion-candidates.py",
)
epc = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(epc)


def _write(path, records):
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
        encoding="utf-8",
    )


def test_extracts_only_learned(tmp_path):
    patterns = tmp_path / "patterns.jsonl"
    ledger = tmp_path / "promoted-ledger.jsonl"
    _write(
        patterns,
        [
            {"type": "learned", "scope": "cc-bash", "generalized_detail": "A"},
            {"type": "doom_loop", "target": "x"},
            {"type": "learned", "scope": "review-gate", "generalized_detail": "B"},
        ],
    )
    ledger.write_text("", encoding="utf-8")
    out = epc.extract(patterns, ledger)
    assert {c["scope"] for c in out} == {"cc-bash", "review-gate"}


def test_dedup_by_generalized_detail(tmp_path):
    patterns = tmp_path / "patterns.jsonl"
    ledger = tmp_path / "promoted-ledger.jsonl"
    _write(
        patterns,
        [
            {"type": "learned", "scope": "s", "generalized_detail": "same insight"},
            {"type": "learned", "scope": "s", "generalized_detail": "same insight"},
        ],
    )
    ledger.write_text("", encoding="utf-8")
    out = epc.extract(patterns, ledger)
    assert len(out) == 1


def test_skips_keys_in_ledger(tmp_path):
    patterns = tmp_path / "patterns.jsonl"
    ledger = tmp_path / "promoted-ledger.jsonl"
    _write(patterns, [{"type": "learned", "scope": "s", "generalized_detail": "done"}])
    key = epc.candidate_key({"generalized_detail": "done"})
    ledger.write_text(
        json.dumps({"key": key, "decision": "adopted"}) + "\n", encoding="utf-8"
    )
    out = epc.extract(patterns, ledger)
    assert out == []


def test_tolerant_parse_skips_broken_lines(tmp_path):
    patterns = tmp_path / "patterns.jsonl"
    ledger = tmp_path / "promoted-ledger.jsonl"
    patterns.write_text(
        '{"type":"learned","scope":"s","generalized_detail":"ok"}\n'
        "{ this is broken json\n",
        encoding="utf-8",
    )
    ledger.write_text("", encoding="utf-8")
    out = epc.extract(patterns, ledger)
    assert len(out) == 1


def test_missing_patterns_file_returns_empty(tmp_path):
    out = epc.extract(tmp_path / "nope.jsonl", tmp_path / "nope2.jsonl")
    assert out == []


def test_falls_back_to_detail_when_no_generalized(tmp_path):
    patterns = tmp_path / "patterns.jsonl"
    ledger = tmp_path / "promoted-ledger.jsonl"
    _write(patterns, [{"type": "learned", "scope": "s", "detail": "only detail"}])
    ledger.write_text("", encoding="utf-8")
    out = epc.extract(patterns, ledger)
    assert out[0]["detail"] == "only detail"


def test_sorted_by_importance_desc(tmp_path):
    patterns = tmp_path / "patterns.jsonl"
    ledger = tmp_path / "promoted-ledger.jsonl"
    _write(
        patterns,
        [
            {
                "type": "learned",
                "scope": "s",
                "generalized_detail": "low",
                "importance": 0.1,
            },
            {
                "type": "learned",
                "scope": "s",
                "generalized_detail": "high",
                "importance": 0.9,
            },
            {
                "type": "learned",
                "scope": "s",
                "generalized_detail": "mid",
                "importance": 0.5,
            },
        ],
    )
    ledger.write_text("", encoding="utf-8")
    out = epc.extract(patterns, ledger)
    assert [c["detail"] for c in out] == ["high", "mid", "low"]


def test_string_importance_does_not_crash_sort(tmp_path):
    patterns = tmp_path / "patterns.jsonl"
    ledger = tmp_path / "promoted-ledger.jsonl"
    _write(
        patterns,
        [
            {
                "type": "learned",
                "scope": "s",
                "generalized_detail": "numeric str",
                "importance": "0.8",
            },
            {
                "type": "learned",
                "scope": "s",
                "generalized_detail": "garbage",
                "importance": "high",
            },
            {
                "type": "learned",
                "scope": "s",
                "generalized_detail": "none",
                "importance": None,
            },
        ],
    )
    ledger.write_text("", encoding="utf-8")
    out = epc.extract(patterns, ledger)
    # "0.8"(=0.8) > "high"/None(=default 0.5) でクラッシュせず数値ソートされる
    assert out[0]["detail"] == "numeric str"
    assert all(isinstance(c["importance"], float) for c in out)
