import importlib.util
import json
import sys
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "hag",
    Path(__file__).resolve().parents[2]
    / ".config/claude/scripts/eval/holdout_accept_gate.py",
)
hag = importlib.util.module_from_spec(_SPEC)
sys.modules["hag"] = hag
_SPEC.loader.exec_module(hag)


def _results(specs):
    """specs: list of (id, pass, secondary_value) -> results list with metric 'm'."""
    return [{"id": i, "pass": p, "metrics": {"m": m}} for i, p, m in specs]


def _splits(baseline_train, baseline_holdout, candidate_train, candidate_holdout):
    return hag.EvalSplits(
        baseline_train=baseline_train,
        baseline_holdout=baseline_holdout,
        candidate_train=candidate_train,
        candidate_holdout=candidate_holdout,
    )


def _metric(name="m", direction="higher"):
    return hag.SecondaryMetricSpec(name=name, direction=direction)


def test_strict_improve_accepts():
    baseline_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    baseline_holdout = _results([("h1", True, 0.5), ("h2", False, 0.5)])
    candidate_train = _results([("t1", True, 0.5), ("t2", True, 0.5)])
    candidate_holdout = _results([("h1", True, 0.5), ("h2", True, 0.5)])

    verdict = hag.evaluate_gate(
        _splits(baseline_train, baseline_holdout, candidate_train, candidate_holdout),
        _metric(),
        "e1",
        "lane-a",
    )

    assert verdict["verdict"] == "accept"
    assert verdict["deltas"]["holdout_pass_rate"] == pytest.approx(0.5)


def test_holdout_tie_rejects():
    # train flat, holdout ties -> rule 3 (strict improvement) fires
    baseline_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    baseline_holdout = _results([("h1", True, 0.5), ("h2", False, 0.5)])
    candidate_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    candidate_holdout = _results([("h1", True, 0.5), ("h2", False, 0.5)])

    verdict = hag.evaluate_gate(
        _splits(baseline_train, baseline_holdout, candidate_train, candidate_holdout),
        _metric(),
        "e2",
        "lane-a",
    )

    assert verdict["verdict"] == "reject"
    assert "tie" in verdict["reason"]
    assert verdict["deltas"]["holdout_pass_rate"] == pytest.approx(0.0)


def test_empty_results_errors():
    baseline_train = []
    baseline_holdout = _results([("h1", True, 0.5)])
    candidate_train = _results([("t1", True, 0.5)])
    candidate_holdout = _results([("h1", True, 0.5)])

    with pytest.raises(hag.GateInputError, match="empty results"):
        hag.evaluate_gate(
            _splits(
                baseline_train, baseline_holdout, candidate_train, candidate_holdout
            ),
            _metric(),
            "e3",
            "lane-a",
        )


def test_overfitting_train_up_holdout_down_rejects():
    baseline_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    baseline_holdout = _results([("h1", True, 0.5), ("h2", True, 0.5)])
    candidate_train = _results([("t1", True, 0.5), ("t2", True, 0.5)])
    candidate_holdout = _results([("h1", True, 0.5), ("h2", False, 0.5)])

    verdict = hag.evaluate_gate(
        _splits(baseline_train, baseline_holdout, candidate_train, candidate_holdout),
        _metric(),
        "e4",
        "lane-a",
    )

    assert verdict["verdict"] == "reject"
    assert "overfitting" in verdict["reason"]


def test_secondary_metric_regression_rejects_despite_pass_rate_gain():
    baseline_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    baseline_holdout = _results([("h1", True, 0.8), ("h2", False, 0.8)])
    candidate_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    # holdout pass_rate improves (0.5 -> 1.0) but secondary metric drops (0.8 -> 0.3)
    candidate_holdout = _results([("h1", True, 0.3), ("h2", True, 0.3)])

    verdict = hag.evaluate_gate(
        _splits(baseline_train, baseline_holdout, candidate_train, candidate_holdout),
        _metric(direction="higher"),
        "e5",
        "lane-a",
    )

    assert verdict["verdict"] == "reject"
    assert verdict["reason"] == "secondary metric regressed"


def test_secondary_metric_lower_direction_flips_comparison():
    baseline_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    baseline_holdout = _results([("h1", True, 0.3), ("h2", False, 0.3)])
    candidate_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    # holdout pass_rate improves; secondary metric rises (0.3 -> 0.8), which is a
    # regression when "lower" is better -> must reject.
    candidate_holdout = _results([("h1", True, 0.8), ("h2", True, 0.8)])

    verdict = hag.evaluate_gate(
        _splits(baseline_train, baseline_holdout, candidate_train, candidate_holdout),
        _metric(direction="lower"),
        "e6",
        "lane-a",
    )
    assert verdict["verdict"] == "reject"
    assert verdict["reason"] == "secondary metric regressed"

    # Same data but declared "higher" is better -> should accept instead.
    verdict_higher = hag.evaluate_gate(
        _splits(baseline_train, baseline_holdout, candidate_train, candidate_holdout),
        _metric(direction="higher"),
        "e6",
        "lane-a",
    )
    assert verdict_higher["verdict"] == "accept"


def test_id_set_mismatch_errors():
    baseline_train = _results([("t1", True, 0.5)])
    baseline_holdout = _results([("h1", True, 0.5)])
    candidate_train = _results([("t1", True, 0.5)])
    candidate_holdout = _results([("h2", True, 0.5)])  # different id from baseline

    with pytest.raises(hag.GateInputError, match="id multisets differ"):
        hag.evaluate_gate(
            _splits(
                baseline_train, baseline_holdout, candidate_train, candidate_holdout
            ),
            _metric(),
            "e7",
            "lane-a",
        )


def test_missing_secondary_metric_errors():
    baseline_train = [{"id": "t1", "pass": True, "metrics": {"m": 0.5}}]
    baseline_holdout = [{"id": "h1", "pass": True, "metrics": {"m": 0.5}}]
    candidate_train = [{"id": "t1", "pass": True, "metrics": {"m": 0.5}}]
    # missing the "m" metric entirely
    candidate_holdout = [{"id": "h1", "pass": True, "metrics": {}}]

    with pytest.raises(hag.GateInputError, match="missing metric"):
        hag.evaluate_gate(
            _splits(
                baseline_train, baseline_holdout, candidate_train, candidate_holdout
            ),
            _metric(),
            "e8",
            "lane-a",
        )


def test_rejected_buffer_idempotent_on_repeat_reject(tmp_path):
    buffer_path = tmp_path / "rejected-edits.jsonl"
    rejection = hag.RejectionRecord(
        lane="lane-a", edit_id="e9", reason="holdout tie", holdout_delta=0.0
    )

    wrote_first = hag.record_rejection(buffer_path, rejection)
    wrote_second = hag.record_rejection(buffer_path, rejection)

    assert wrote_first is True
    assert wrote_second is False
    lines = buffer_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["lane"] == "lane-a"
    assert entry["edit_id"] == "e9"
    assert entry["key"] == hag.rejected_buffer_key("lane-a", "e9")


def test_rejected_buffer_not_written_on_accept(tmp_path):
    buffer_path = tmp_path / "rejected-edits.jsonl"
    baseline_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    baseline_holdout = _results([("h1", True, 0.5), ("h2", False, 0.5)])
    candidate_train = _results([("t1", True, 0.5), ("t2", True, 0.5)])
    candidate_holdout = _results([("h1", True, 0.5), ("h2", True, 0.5)])

    verdict = hag.evaluate_gate(
        _splits(baseline_train, baseline_holdout, candidate_train, candidate_holdout),
        _metric(),
        "e10",
        "lane-a",
    )
    assert verdict["verdict"] == "accept"
    # Simulate CLI behavior: only record on reject.
    if verdict["verdict"] == "reject":
        hag.record_rejection(
            buffer_path,
            hag.RejectionRecord(
                lane="lane-a",
                edit_id="e10",
                reason=verdict["reason"],
                holdout_delta=verdict["deltas"]["holdout_pass_rate"],
            ),
        )
    assert not buffer_path.exists()


def test_rejected_buffer_not_written_in_dry_run(tmp_path, monkeypatch, capsys):
    baseline_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    baseline_holdout = _results([("h1", True, 0.5), ("h2", False, 0.5)])
    candidate_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    candidate_holdout = _results([("h1", True, 0.5), ("h2", False, 0.5)])

    baseline_train_path = tmp_path / "baseline-train.json"
    baseline_holdout_path = tmp_path / "baseline-holdout.json"
    candidate_train_path = tmp_path / "candidate-train.json"
    candidate_holdout_path = tmp_path / "candidate-holdout.json"
    for path, results in (
        (baseline_train_path, baseline_train),
        (baseline_holdout_path, baseline_holdout),
        (candidate_train_path, candidate_train),
        (candidate_holdout_path, candidate_holdout),
    ):
        path.write_text(json.dumps({"results": results}), encoding="utf-8")

    buffer_path = tmp_path / "rejected-edits.jsonl"
    argv = [
        "holdout_accept_gate.py",
        "--baseline-train",
        str(baseline_train_path),
        "--baseline-holdout",
        str(baseline_holdout_path),
        "--candidate-train",
        str(candidate_train_path),
        "--candidate-holdout",
        str(candidate_holdout_path),
        "--secondary-metric",
        "m",
        "--edit-id",
        "e11",
        "--lane",
        "lane-a",
        "--rejected-buffer",
        str(buffer_path),
        "--dry-run",
    ]
    monkeypatch.setattr("sys.argv", argv)
    exit_code = hag.main()

    assert exit_code == 1  # reject (holdout tie)
    assert not buffer_path.exists()


def test_cli_reject_writes_buffer_via_main(tmp_path, monkeypatch):
    baseline_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    baseline_holdout = _results([("h1", True, 0.5), ("h2", False, 0.5)])
    candidate_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    candidate_holdout = _results([("h1", True, 0.5), ("h2", False, 0.5)])

    baseline_train_path = tmp_path / "baseline-train.json"
    baseline_holdout_path = tmp_path / "baseline-holdout.json"
    candidate_train_path = tmp_path / "candidate-train.json"
    candidate_holdout_path = tmp_path / "candidate-holdout.json"
    for path, results in (
        (baseline_train_path, baseline_train),
        (baseline_holdout_path, baseline_holdout),
        (candidate_train_path, candidate_train),
        (candidate_holdout_path, candidate_holdout),
    ):
        path.write_text(json.dumps({"results": results}), encoding="utf-8")

    buffer_path = tmp_path / "rejected-edits.jsonl"
    argv = [
        "holdout_accept_gate.py",
        "--baseline-train",
        str(baseline_train_path),
        "--baseline-holdout",
        str(baseline_holdout_path),
        "--candidate-train",
        str(candidate_train_path),
        "--candidate-holdout",
        str(candidate_holdout_path),
        "--secondary-metric",
        "m",
        "--edit-id",
        "e12",
        "--lane",
        "lane-a",
        "--rejected-buffer",
        str(buffer_path),
    ]
    monkeypatch.setattr("sys.argv", argv)
    exit_code = hag.main()

    assert exit_code == 1
    assert buffer_path.exists()
    lines = buffer_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1


def test_duplicate_id_pass_rate_forgery_errors():
    baseline_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    baseline_holdout = _results([("h1", True, 0.5), ("h2", False, 0.5)])
    candidate_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    candidate_holdout = _results(
        [("h1", True, 0.5), ("h1", True, 0.5), ("h1", True, 0.5), ("h2", False, 0.5)]
    )

    with pytest.raises(hag.GateInputError, match="id multisets differ"):
        hag.evaluate_gate(
            _splits(
                baseline_train, baseline_holdout, candidate_train, candidate_holdout
            ),
            _metric(),
            "e13",
            "lane-a",
        )


def test_top_level_list_errors(tmp_path):
    path = tmp_path / "results.json"
    path.write_text(json.dumps([{"id": "h1", "pass": True}]), encoding="utf-8")

    with pytest.raises(hag.GateInputError, match="top-level JSON must be an object"):
        hag.load_eval_file(path)


def test_pass_as_string_errors():
    baseline_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    baseline_holdout = _results([("h1", True, 0.5), ("h2", False, 0.5)])
    candidate_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    candidate_holdout = [
        {"id": "h1", "pass": "false", "metrics": {"m": 0.5}},
        {"id": "h2", "pass": False, "metrics": {"m": 0.5}},
    ]

    with pytest.raises(hag.GateInputError, match="non-bool 'pass'"):
        hag.evaluate_gate(
            _splits(
                baseline_train, baseline_holdout, candidate_train, candidate_holdout
            ),
            _metric(),
            "e14",
            "lane-a",
        )


def test_metrics_null_errors():
    baseline_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    baseline_holdout = _results([("h1", True, 0.5), ("h2", False, 0.5)])
    candidate_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    candidate_holdout = [
        {"id": "h1", "pass": True, "metrics": None},
        {"id": "h2", "pass": False, "metrics": {"m": 0.5}},
    ]

    with pytest.raises(hag.GateInputError, match="non-dict 'metrics'"):
        hag.evaluate_gate(
            _splits(
                baseline_train, baseline_holdout, candidate_train, candidate_holdout
            ),
            _metric(),
            "e15",
            "lane-a",
        )


def test_secondary_metric_value_as_string_errors():
    baseline_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    baseline_holdout = _results([("h1", True, 0.5), ("h2", False, 0.5)])
    candidate_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    candidate_holdout = [
        {"id": "h1", "pass": True, "metrics": {"m": "0.85"}},
        {"id": "h2", "pass": True, "metrics": {"m": 0.5}},
    ]

    with pytest.raises(hag.GateInputError, match="is not a finite number"):
        hag.evaluate_gate(
            _splits(
                baseline_train, baseline_holdout, candidate_train, candidate_holdout
            ),
            _metric(),
            "e16",
            "lane-a",
        )


def test_secondary_metric_nan_errors():
    baseline_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    baseline_holdout = _results([("h1", True, 0.5), ("h2", False, 0.5)])
    candidate_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    candidate_holdout = [
        {"id": "h1", "pass": True, "metrics": {"m": float("nan")}},
        {"id": "h2", "pass": True, "metrics": {"m": 0.5}},
    ]

    with pytest.raises(hag.GateInputError, match="is not a finite number"):
        hag.evaluate_gate(
            _splits(
                baseline_train, baseline_holdout, candidate_train, candidate_holdout
            ),
            _metric(),
            "e17",
            "lane-a",
        )


def test_non_string_id_errors():
    baseline_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    baseline_holdout = _results([("h1", True, 0.5), ("h2", False, 0.5)])
    candidate_train = _results([("t1", True, 0.5), ("t2", False, 0.5)])
    candidate_holdout = [
        {"id": True, "pass": True, "metrics": {"m": 0.5}},
        {"id": "h2", "pass": True, "metrics": {"m": 0.5}},
    ]

    with pytest.raises(hag.GateInputError, match="non-string 'id'"):
        hag.evaluate_gate(
            _splits(
                baseline_train, baseline_holdout, candidate_train, candidate_holdout
            ),
            _metric(),
            "e18",
            "lane-a",
        )


def test_parse_secondary_metric_spec_invalid_direction_errors():
    with pytest.raises(hag.GateInputError, match="invalid direction"):
        hag.parse_secondary_metric_spec("m:sideways")
