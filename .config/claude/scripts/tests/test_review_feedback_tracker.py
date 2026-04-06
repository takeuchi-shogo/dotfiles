"""Tests for review-feedback-tracker.py hook."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "policy"))

from importlib import import_module

tracker = import_module("review-feedback-tracker")


@pytest.fixture(autouse=True)
def isolate_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOEVOLVE_DATA_DIR", str(tmp_path))
    import logging

    logging.getLogger("autoevolve").handlers.clear()
    return tmp_path


class TestIsGitCommit:
    def test_simple_commit(self):
        assert tracker._is_git_commit("git commit -m 'test'")

    def test_commit_with_path(self):
        assert tracker._is_git_commit("git commit -m \"$(cat <<'EOF'\ntest\nEOF\n)\"")

    def test_not_commit(self):
        assert not tracker._is_git_commit("git status")
        assert not tracker._is_git_commit("git diff")
        assert not tracker._is_git_commit("git log --oneline")


class TestParseDiffChangedLines:
    def test_single_file_change(self):
        diff = """\
diff --git a/api.go b/api.go
--- a/api.go
+++ b/api.go
@@ -40,0 +41,3 @@
+func newHandler() {
+    // fixed
+}
"""
        result = tracker._parse_diff_changed_lines(diff)
        assert "api.go" in result
        assert result["api.go"] == {41, 42, 43}

    def test_multiple_files(self):
        diff = """\
diff --git a/a.ts b/a.ts
--- a/a.ts
+++ b/a.ts
@@ -10,0 +11,1 @@
+const x = 1;
diff --git a/b.ts b/b.ts
--- a/b.ts
+++ b/b.ts
@@ -5,0 +6,2 @@
+const y = 2;
+const z = 3;
"""
        result = tracker._parse_diff_changed_lines(diff)
        assert result["a.ts"] == {11}
        assert result["b.ts"] == {6, 7}

    def test_empty_diff(self):
        assert tracker._parse_diff_changed_lines("") == {}


class TestMatchFindingToDiff:
    def test_exact_match(self):
        finding = {"file": "api.go", "line": 42}
        changed = {"api.go": {41, 42, 43}}
        assert tracker._match_finding_to_diff(finding, changed) == "accept"

    def test_proximity_match(self):
        finding = {"file": "api.go", "line": 45}
        changed = {"api.go": {42}}
        assert tracker._match_finding_to_diff(finding, changed) == "accept"

    def test_no_match_line_far(self):
        """ファイルは変更されたが行が proximity 外 → partial."""
        finding = {"file": "api.go", "line": 100}
        changed = {"api.go": {42}}
        assert tracker._match_finding_to_diff(finding, changed) == "partial"

    def test_file_not_in_diff(self):
        finding = {"file": "other.go", "line": 42}
        changed = {"api.go": {42}}
        assert tracker._match_finding_to_diff(finding, changed) == "reject"

    def test_line_zero_accepts_any_change_in_file(self):
        finding = {"file": "api.go", "line": 0}
        changed = {"api.go": {100}}
        assert tracker._match_finding_to_diff(finding, changed) == "accept"

    def test_suffix_matching(self):
        finding = {"file": "src/api.go", "line": 42}
        changed = {"api.go": {42}}
        assert tracker._match_finding_to_diff(finding, changed) == "accept"

    def test_partial_file_changed_but_line_far(self):
        """ファイルは変更あり、指摘行は proximity(±5) の範囲外 → partial."""
        finding = {"file": "api.go", "line": 200}
        changed = {"api.go": {10, 11, 12}}
        assert tracker._match_finding_to_diff(finding, changed) == "partial"
