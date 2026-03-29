import importlib.util
import json
import os
import tempfile
from pathlib import Path

_MODULE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / ".config"
    / "claude"
    / "scripts"
    / "learner"
    / "cross-domain-mapper.py"
)
_spec = importlib.util.spec_from_file_location("cross_domain_mapper", _MODULE_PATH)
cross_domain_mapper = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cross_domain_mapper)


class TestCrossDomainMapper:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.original_env = os.environ.get("AUTOEVOLVE_DATA_DIR")
        os.environ["AUTOEVOLVE_DATA_DIR"] = self.tmpdir
        (Path(self.tmpdir) / "experiments").mkdir(parents=True)
        (Path(self.tmpdir) / "learnings").mkdir(parents=True)

    def teardown_method(self):
        if self.original_env is None:
            os.environ.pop("AUTOEVOLVE_DATA_DIR", None)
        else:
            os.environ["AUTOEVOLVE_DATA_DIR"] = self.original_env

    def test_classify_memory_addition(self):
        classify_improvement_method = cross_domain_mapper.classify_improvement_method

        entry = {
            "hypothesis": "Add persistent memory for error tracking",
            "causal_hypothesis": "State is lost between sessions",
        }
        assert classify_improvement_method(entry) == "memory_addition"

    def test_classify_checklist(self):
        classify_improvement_method = cross_domain_mapper.classify_improvement_method

        entry = {"hypothesis": "Create a checklist rule for reviews"}
        assert classify_improvement_method(entry) == "checklist_creation"

    def test_classify_guard(self):
        classify_improvement_method = cross_domain_mapper.classify_improvement_method

        entry = {
            "hypothesis": "Add constraint guard for file limit",
        }
        assert classify_improvement_method(entry) == "guard_addition"

    def test_classify_none_for_empty(self):
        classify_improvement_method = cross_domain_mapper.classify_improvement_method

        assert classify_improvement_method({}) is None
        assert classify_improvement_method({"hypothesis": ""}) is None

    def test_classify_no_match(self):
        classify_improvement_method = cross_domain_mapper.classify_improvement_method

        entry = {"hypothesis": "Upgrade Python version to 3.14"}
        assert classify_improvement_method(entry) is None

    def test_scan_meta_patterns_empty(self):
        scan_meta_patterns = cross_domain_mapper.scan_meta_patterns

        result = scan_meta_patterns(Path(self.tmpdir))
        assert result == []

    def test_scan_meta_patterns_detects_transfer(self):
        scan_meta_patterns = cross_domain_mapper.scan_meta_patterns

        registry_path = Path(self.tmpdir) / "experiments" / "experiment-registry.jsonl"
        # checklist_creation が errors で成功
        entries = [
            {
                "id": "exp-001",
                "category": "errors",
                "hypothesis": "Create checklist rule for nil errors",
                "status": "merged",
            },
            # quality ドメインには checklist 系の実験なし
            {
                "id": "exp-002",
                "category": "quality",
                "hypothesis": "Add persistent memory for tracking",
                "status": "merged",
            },
        ]
        with open(registry_path, "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")

        result = scan_meta_patterns(Path(self.tmpdir))
        # checklist_creation が errors で成功、quality で未試行
        checklist_candidates = [
            c for c in result if c["method"] == "checklist_creation"
        ]
        assert len(checklist_candidates) == 1
        assert "quality" in checklist_candidates[0]["not_tried_in"]
        assert "errors" in checklist_candidates[0]["successful_in"]

    def test_scan_meta_patterns_no_candidate_when_all_tried(self):
        scan_meta_patterns = cross_domain_mapper.scan_meta_patterns

        registry_path = Path(self.tmpdir) / "experiments" / "experiment-registry.jsonl"
        # Same method in both domains → no transfer candidate
        entries = [
            {
                "id": "exp-001",
                "category": "errors",
                "hypothesis": "Add guard constraint",
                "status": "merged",
            },
            {
                "id": "exp-002",
                "category": "quality",
                "hypothesis": "Add guard limit for reviews",
                "status": "merged",
            },
        ]
        with open(registry_path, "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")

        result = scan_meta_patterns(Path(self.tmpdir))
        guard_candidates = [c for c in result if c["method"] == "guard_addition"]
        assert len(guard_candidates) == 0

    def test_scan_cross_domain_existing(self):
        """既存の scan_cross_domain 機能が壊れていないことを確認。"""
        scan_cross_domain = cross_domain_mapper.scan_cross_domain

        learnings_dir = Path(self.tmpdir) / "learnings"
        errors_path = learnings_dir / "errors.jsonl"
        entries = [
            {
                "root_cause": "missing nil check",
                "category": "errors",
            },
            {
                "root_cause": "missing nil check",
                "category": "quality",
            },
        ]
        with open(errors_path, "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")

        result = scan_cross_domain(Path(self.tmpdir))
        assert len(result) == 1
        assert result[0]["root_cause"] == "missing nil check"
