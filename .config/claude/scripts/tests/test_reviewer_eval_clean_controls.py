"""Tests for known-clean control tuples in reviewer-eval-tuples.json.

前提: eval/reviewer-eval-tuples.json に case_kind="clean" の対照タプルがある。
検証項目: ID が一意、clean は expected_findings == 0、split_holdout が
train / holdout の両方に clean を 1 件以上配置する。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent.parent / "eval"
sys.path.insert(0, str(EVAL_DIR))

from split_holdout import stratified_split  # noqa: E402

TUPLES_FILE = EVAL_DIR / "reviewer-eval-tuples.json"
TUPLES = json.loads(TUPLES_FILE.read_text(encoding="utf-8"))["tuples"]
CLEAN = [t for t in TUPLES if t.get("case_kind") == "clean"]


def test_ids_are_unique():
    ids = [t["id"] for t in TUPLES]
    assert len(ids) == len(set(ids))


def test_clean_controls_expect_no_findings():
    assert len(CLEAN) >= 6
    for t in CLEAN:
        assert t["expected_findings"] == 0, t["id"]
        assert t["failure_mode"] == "NONE", t["id"]


def test_defect_tuples_are_not_marked_clean():
    assert all(t.get("failure_mode") != "NONE" for t in TUPLES if t not in CLEAN)


def test_split_puts_clean_control_in_both_splits():
    train, holdout = stratified_split(TUPLES, holdout_ratio=0.3, seed=42)
    assert any(t.get("case_kind") == "clean" for t in train)
    assert any(t.get("case_kind") == "clean" for t in holdout)
