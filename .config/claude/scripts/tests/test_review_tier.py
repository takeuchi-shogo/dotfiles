"""Tests for review-tier.py — deterministic review tier classifier."""

import json
import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "policy"))

tier_mod = import_module("review-tier")
classify = tier_mod.classify


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_main(payload: object) -> dict:
    """Run main() with *payload* on stdin, return parsed stdout JSON."""
    import io

    monkeypatched_stdin = io.StringIO(json.dumps(payload))
    old_stdin = sys.stdin
    captured_stdout = io.StringIO()
    old_stdout = sys.stdout
    try:
        sys.stdin = monkeypatched_stdin
        sys.stdout = captured_stdout
        tier_mod.main()
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout
    return json.loads(captured_stdout.getvalue())


def _make_input(
    insertions: int = 5,
    deletions: int = 0,
    files: list[str] | None = None,
    risk_class: str = "Low",
) -> dict:
    if files is None:
        files = ["README.md"]
    return {
        "diff_stat": {"insertions": insertions, "deletions": deletions},
        "files": files,
        "risk_class": risk_class,
    }


# ---------------------------------------------------------------------------
# classify() — light path
# ---------------------------------------------------------------------------


class TestClassifyLight:
    def test_low_risk_docs_only(self):
        tier, reason, signals = classify(
            {"insertions": 3, "deletions": 2},
            ["docs/README.md", "CHANGELOG.md"],
            "Low",
        )
        assert tier == "light"
        assert signals["all_docs_or_tests"] is True
        assert signals["dependency_change"] is False

    def test_low_risk_test_files_filename_pattern(self):
        tier, _, _ = classify(
            {"insertions": 5, "deletions": 0},
            ["pkg/foo_test.go", "pkg/bar_test.go"],
            "Low",
        )
        assert tier == "light"

    def test_low_risk_test_files_spec_pattern(self):
        tier, _, _ = classify(
            {"insertions": 4, "deletions": 1},
            ["src/component.spec.ts"],
            "Low",
        )
        assert tier == "light"

    def test_low_risk_test_dir_segment(self):
        tier, _, _ = classify(
            {"insertions": 2, "deletions": 2},
            ["tests/unit/helper.py"],
            "Low",
        )
        assert tier == "light"

    def test_low_risk_mixed_docs_and_tests(self):
        tier, _, _ = classify(
            {"insertions": 3, "deletions": 0},
            ["README.md", "tests/test_foo.py"],
            "Low",
        )
        assert tier == "light"

    def test_exactly_10_lines_is_light(self):
        tier, _, _ = classify(
            {"insertions": 7, "deletions": 3},
            ["README.md"],
            "Low",
        )
        assert tier == "light"
        assert tier != "standard"


# ---------------------------------------------------------------------------
# classify() — light guard failures → standard
# ---------------------------------------------------------------------------


class TestClassifyLightGuardsMissed:
    def test_low_risk_11_lines_is_standard(self):
        """Guard: Low + ≤10 lines required. 11 lines → standard."""
        tier, _, signals = classify(
            {"insertions": 8, "deletions": 3},
            ["README.md"],
            "Low",
        )
        assert tier == "standard"
        assert signals["total_lines"] == 11

    def test_low_risk_10_lines_but_py_file_mixed(self):
        """Guard: all files must be docs/tests. .py present → standard."""
        tier, _, signals = classify(
            {"insertions": 5, "deletions": 2},
            ["README.md", "main.py"],
            "Low",
        )
        assert tier == "standard"
        assert signals["all_docs_or_tests"] is False

    def test_medium_risk_docs_only_is_standard(self):
        """Guard: risk_class must be Low. Medium → standard (not light)."""
        tier, _, _ = classify(
            {"insertions": 3, "deletions": 0},
            ["README.md"],
            "Medium",
        )
        assert tier == "standard"


# ---------------------------------------------------------------------------
# classify() — deep path
# ---------------------------------------------------------------------------


class TestClassifyDeep:
    def test_high_risk_class(self):
        tier, reason, _ = classify(
            {"insertions": 1, "deletions": 0},
            ["main.go"],
            "High",
        )
        assert tier == "deep"
        assert "High" in reason

    def test_201_lines(self):
        tier, reason, signals = classify(
            {"insertions": 150, "deletions": 51},
            ["main.go"],
            "Low",
        )
        assert tier == "deep"
        assert signals["total_lines"] == 201
        assert "201" in reason

    def test_exactly_200_lines_is_not_deep(self):
        """200 lines does NOT trigger deep (threshold is strictly > 200)."""
        tier, _, _ = classify(
            {"insertions": 100, "deletions": 100},
            ["main.go"],
            "Medium",
        )
        assert tier == "standard"

    def test_go_mod_triggers_deep(self):
        tier, reason, signals = classify(
            {"insertions": 2, "deletions": 1},
            ["go.mod"],
            "Low",
        )
        assert tier == "deep"
        assert signals["dependency_change"] is True
        assert "go.mod" in reason

    def test_package_json_triggers_deep(self):
        tier, _, _ = classify(
            {"insertions": 1, "deletions": 0},
            ["package.json"],
            "Low",
        )
        assert tier == "deep"

    def test_package_lock_json_triggers_deep(self):
        """package-lock.json does not end with .lock — must be in the basename set."""
        tier, _, signals = classify(
            {"insertions": 1, "deletions": 0},
            ["package-lock.json"],
            "Low",
        )
        assert tier == "deep"
        assert signals["dependency_change"] is True

    def test_cargo_toml_triggers_deep(self):
        tier, _, _ = classify(
            {"insertions": 3, "deletions": 0},
            ["Cargo.toml"],
            "Low",
        )
        assert tier == "deep"

    def test_arbitrary_lock_file_triggers_deep(self):
        """Any *.lock file — not just the named ones — should trigger deep."""
        tier, _, _ = classify(
            {"insertions": 2, "deletions": 0},
            ["composer.lock"],
            "Low",
        )
        assert tier == "deep"

    def test_dep_file_mixed_with_others(self):
        """go.sum among regular files still triggers deep."""
        tier, _, _ = classify(
            {"insertions": 5, "deletions": 0},
            ["main.go", "go.sum", "README.md"],
            "Low",
        )
        assert tier == "deep"


# ---------------------------------------------------------------------------
# classify() — standard path
# ---------------------------------------------------------------------------


class TestClassifyStandard:
    def test_medium_risk_small_change(self):
        tier, _, _ = classify(
            {"insertions": 10, "deletions": 0},
            ["main.go"],
            "Medium",
        )
        assert tier == "standard"

    def test_low_risk_large_change(self):
        tier, _, _ = classify(
            {"insertions": 50, "deletions": 20},
            ["main.go"],
            "Low",
        )
        assert tier == "standard"


# ---------------------------------------------------------------------------
# main() — invalid input → standard (fail-safe)
# ---------------------------------------------------------------------------


class TestMainFailSafe:
    def test_invalid_json_stdin(self):
        import io

        old = sys.stdin
        captured = io.StringIO()
        old_out = sys.stdout
        try:
            sys.stdin = io.StringIO("{not valid json")
            sys.stdout = captured
            tier_mod.main()
        finally:
            sys.stdin = old
            sys.stdout = old_out
        out = json.loads(captured.getvalue())
        assert out["tier"] == "standard"
        assert "fail-safe" in out["reason"]

    def test_json_not_object(self):
        out = _run_main([1, 2, 3])
        assert out["tier"] == "standard"
        assert "fail-safe" in out["reason"]

    def test_invalid_risk_class(self):
        payload = _make_input(risk_class="Critical")
        out = _run_main(payload)
        assert out["tier"] == "standard"
        assert "fail-safe" in out["reason"]

    def test_files_not_a_list(self):
        payload = {
            "diff_stat": {"insertions": 5, "deletions": 0},
            "files": "not-a-list",
            "risk_class": "Low",
        }
        out = _run_main(payload)
        assert out["tier"] == "standard"
        assert "fail-safe" in out["reason"]

    def test_diff_stat_missing(self):
        payload = {
            "files": ["README.md"],
            "risk_class": "Low",
        }
        out = _run_main(payload)
        assert out["tier"] == "standard"
        assert "fail-safe" in out["reason"]

    def test_diff_stat_non_numeric(self):
        payload = {
            "diff_stat": {"insertions": "abc", "deletions": 0},
            "files": ["README.md"],
            "risk_class": "Low",
        }
        out = _run_main(payload)
        assert out["tier"] == "standard"
        assert "fail-safe" in out["reason"]


# ---------------------------------------------------------------------------
# main() — happy-path round-trips
# ---------------------------------------------------------------------------


class TestMainRoundTrip:
    def test_light_round_trip(self):
        payload = _make_input(
            insertions=3, deletions=1, files=["README.md"], risk_class="Low"
        )
        out = _run_main(payload)
        assert out["tier"] == "light"
        assert out["signals"]["total_lines"] == 4
        assert out["signals"]["risk_class"] == "Low"

    def test_deep_high_risk_round_trip(self):
        payload = _make_input(
            insertions=1, deletions=0, files=["main.go"], risk_class="High"
        )
        out = _run_main(payload)
        assert out["tier"] == "deep"

    def test_standard_round_trip(self):
        payload = _make_input(
            insertions=20, deletions=5, files=["handler.go"], risk_class="Medium"
        )
        out = _run_main(payload)
        assert out["tier"] == "standard"

    def test_output_has_required_keys(self):
        out = _run_main(_make_input())
        assert "tier" in out
        assert "reason" in out
        assert "signals" in out
        for key in (
            "total_lines",
            "risk_class",
            "dependency_change",
            "all_docs_or_tests",
        ):
            assert key in out["signals"], f"signals missing key: {key}"
