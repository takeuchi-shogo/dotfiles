from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
RUNNER = REPO_ROOT / "tools" / "codex-janitor" / "runner.py"
WORKFLOW = REPO_ROOT / "tools" / "codex-janitor" / "workflows" / "refactor-loop.toml"

sys.path.insert(0, str(REPO_ROOT / "tools" / "codex-janitor"))
import runner  # noqa: E402


class RunnerTests(unittest.TestCase):
    def make_repo(self) -> Path:
        repo_root = Path(tempfile.mkdtemp())
        subprocess.run(
            ["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"], cwd=repo_root, check=True
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_root,
            check=True,
        )
        (repo_root / "README.md").write_text("ok\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=repo_root, check=True)
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
        return repo_root

    def make_fake_codex(self, root: Path) -> Path:
        script_path = root / "fake_codex.py"
        script_path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "import json",
                    "import os",
                    "import sys",
                    "from pathlib import Path",
                    "",
                    "def parse_output_path(argv: list[str]) -> Path:",
                    "    index = argv.index('-o')",
                    "    return Path(argv[index + 1])",
                    "",
                    "def write_session(sessions_dir: Path, session_id: str) -> None:",
                    "    session_path = sessions_dir / '2026' / '03' / '19' / f'rollout-{session_id}.jsonl'",  # noqa: E501
                    "    session_path.parent.mkdir(parents=True, exist_ok=True)",
                    "    payload = {'type': 'session_meta', 'payload': {'id': session_id}}",  # noqa: E501
                    "    session_path.write_text(json.dumps(payload) + '\\n', encoding='utf-8')",  # noqa: E501
                    "",
                    "def bump_counter() -> None:",
                    "    counter = Path('STAGE_COUNTER.txt')",
                    "    current = int(counter.read_text()) if counter.exists() else 0",  # noqa: E501
                    "    counter.write_text(str(current + 1))",
                    "",
                    "def main() -> int:",
                    "    argv = sys.argv[1:]",
                    "    sessions_dir = Path(os.environ['CODEX_JANITOR_TEST_SESSIONS_DIR'])",  # noqa: E501
                    "    output_path = parse_output_path(argv)",
                    "    prompt = argv[-1]",
                    "    session_id = 'session-123'",
                    "    if argv[:2] == ['exec', 'resume']:",
                    "        print(json.dumps({'type': 'turn.started'}))",
                    "    else:",
                    "        write_session(sessions_dir, session_id)",
                    "        print(json.dumps({'type': 'thread.started', 'thread_id': 'thread-123'}))",  # noqa: E501
                    "    bump_counter()",
                    "    output_path.parent.mkdir(parents=True, exist_ok=True)",
                    "    if 'execplan-improve' in prompt:",
                    "        output_path.write_text('Usefulness score: 2/10 - little left to improve\\n', encoding='utf-8')",  # noqa: E501
                    "    elif 'review-recent-work' in prompt:",
                    "        output_path.write_text('skip\\n', encoding='utf-8')",
                    "    else:",
                    "        output_path.write_text('ok\\n', encoding='utf-8')",
                    "    return 0",
                    "",
                    "if __name__ == '__main__':",
                    "    raise SystemExit(main())",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        script_path.chmod(0o755)
        return script_path

    def test_dry_run_expands_stages(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--workflow",
                str(WORKFLOW),
                "--improvements",
                "2",
                "--reviews",
                "1",
                "--dry-run",
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0)
        self.assertIn("01. find-best-refactor", completed.stdout)
        self.assertIn("02. execplan-improve-1", completed.stdout)
        self.assertIn("05. review-recent-work", completed.stdout)

    def test_runner_discovers_session_and_stops_on_low_usefulness(self) -> None:
        repo_root = self.make_repo()
        temp_root = Path(tempfile.mkdtemp())
        sessions_dir = temp_root / "sessions"
        fake_codex = self.make_fake_codex(temp_root)
        output_root = temp_root / "runs"
        env = dict(os.environ)
        env["CODEX_JANITOR_TEST_SESSIONS_DIR"] = str(sessions_dir)

        completed = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--workflow",
                str(WORKFLOW),
                "--target-dir",
                str(repo_root),
                "--output-root",
                str(output_root),
                "--sessions-dir",
                str(sessions_dir),
                "--codex-bin",
                str(fake_codex),
                "--improvements",
                "1",
                "--reviews",
                "1",
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )

        self.assertEqual(completed.returncode, 0)
        manifest_path = Path(completed.stdout.strip())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["session_id"], "session-123")
        self.assertEqual(
            manifest["stop_reason"],
            "stopped:execplan-improve:usefulness_below_threshold:2",
        )
        self.assertEqual(len(manifest["stages"]), 2)
        first_stage = manifest["stages"][0]
        self.assertIn("decision", first_stage)
        self.assertIn("evidence", first_stage)
        self.assertEqual(first_stage["decision"]["verdict"], "proceed")

    def test_runner_fails_on_dirty_repo(self) -> None:
        repo_root = self.make_repo()
        (repo_root / "README.md").write_text("dirty\n", encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--workflow",
                str(WORKFLOW),
                "--target-dir",
                str(repo_root),
                "--dry-run",
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0)

        completed = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--workflow",
                str(WORKFLOW),
                "--target-dir",
                str(repo_root),
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 1)
        self.assertIn("pre-existing changes", completed.stderr)


class StopRuleUnitTests(unittest.TestCase):
    """Pure-function tests for decide_stop_reason new branches."""

    def _stage(self) -> runner.ExpandedStage:
        return runner.ExpandedStage(
            label="test",
            prompt="prompt",
            stop_on_skip=True,
            stop_on_low_usefulness=True,
        )

    def test_no_op_diff_returns_stop(self) -> None:
        result = runner.decide_stop_reason(
            self._stage(),
            last_message="ok",
            usefulness_score=None,
            usefulness_threshold=3,
            no_op_diff_enabled=True,
            diff_changed=False,
        )
        self.assertEqual(result, "no_op_diff")

    def test_no_op_diff_disabled_does_not_trigger(self) -> None:
        result = runner.decide_stop_reason(
            self._stage(),
            last_message="ok",
            usefulness_score=None,
            usefulness_threshold=3,
            no_op_diff_enabled=False,
            diff_changed=False,
        )
        self.assertIsNone(result)

    def test_validation_failed_returns_stop(self) -> None:
        result = runner.decide_stop_reason(
            self._stage(),
            last_message="ok",
            usefulness_score=None,
            usefulness_threshold=3,
            validation_failed=True,
            validation_summary="non-zero exit (1): test failed at line 42",
        )
        self.assertIsNotNone(result)
        assert result is not None
        self.assertTrue(result.startswith("validation_failed"))

    def test_time_budget_exceeded_returns_stop(self) -> None:
        result = runner.decide_stop_reason(
            self._stage(),
            last_message="ok",
            usefulness_score=None,
            usefulness_threshold=3,
            elapsed_seconds=1900.0,
            time_budget_seconds=1800.0,
        )
        self.assertIsNotNone(result)
        assert result is not None
        self.assertTrue(result.startswith("time_budget_exceeded"))

    def test_destructive_low_confidence_returns_stop(self) -> None:
        result = runner.decide_stop_reason(
            self._stage(),
            last_message="ok",
            usefulness_score=4,
            usefulness_threshold=3,
            destructive_enabled=True,
            destructive_stat={"insertions": 10, "deletions": 80},
            destructive_deletion_threshold=50,
            destructive_total_threshold=100,
            destructive_usefulness_floor=5,
        )
        self.assertIsNotNone(result)
        assert result is not None
        self.assertTrue(result.startswith("destructive_without_evidence"))

    def test_destructive_high_confidence_does_not_trigger(self) -> None:
        result = runner.decide_stop_reason(
            self._stage(),
            last_message="ok",
            usefulness_score=9,
            usefulness_threshold=3,
            destructive_enabled=True,
            destructive_stat={"insertions": 10, "deletions": 80},
            destructive_deletion_threshold=50,
            destructive_total_threshold=100,
            destructive_usefulness_floor=5,
        )
        self.assertIsNone(result)

    def test_existing_skip_branch_still_works(self) -> None:
        result = runner.decide_stop_reason(
            self._stage(),
            last_message="skip",
            usefulness_score=None,
            usefulness_threshold=3,
        )
        self.assertEqual(result, "assistant_returned_skip")

    def test_existing_usefulness_branch_still_works(self) -> None:
        result = runner.decide_stop_reason(
            self._stage(),
            last_message="ok",
            usefulness_score=2,
            usefulness_threshold=3,
        )
        self.assertEqual(result, "usefulness_below_threshold:2")


class SnapshotAndDiffTests(unittest.TestCase):
    def _make_repo_with_file(self, name: str, content: str) -> Path:
        repo_root = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_root,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_root,
            check=True,
        )
        (repo_root / name).write_text(content, encoding="utf-8")
        subprocess.run(["git", "add", name], cwd=repo_root, check=True)
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=repo_root,
            check=True,
            capture_output=True,
        )
        return repo_root

    def test_capture_head_sha_returns_sha(self) -> None:
        repo = self._make_repo_with_file("a.txt", "hello\n")
        sha = runner.capture_head_sha(repo)
        self.assertIsNotNone(sha)
        assert sha is not None
        self.assertEqual(len(sha), 40)

    def test_compute_snapshot_with_no_changes(self) -> None:
        repo = self._make_repo_with_file("a.txt", "hello\n")
        snap = runner.compute_snapshot(repo)
        self.assertIn("commit", snap)
        self.assertEqual(snap["files_sha256"], {})

    def test_compute_snapshot_with_explicit_files(self) -> None:
        repo = self._make_repo_with_file("a.txt", "hello\n")
        snap = runner.compute_snapshot(repo, files=["a.txt"])
        self.assertIn("a.txt", snap["files_sha256"])
        self.assertEqual(len(snap["files_sha256"]["a.txt"]), 64)

    def test_detect_snapshot_drift_commit_changed(self) -> None:
        start = {"commit": "abc123", "files_sha256": {}}
        current = {"commit": "def456", "files_sha256": {}}
        drift = runner.detect_snapshot_drift(start, current)
        self.assertIsNotNone(drift)
        assert drift is not None
        self.assertTrue(drift.startswith("commit_changed"))

    def test_detect_snapshot_drift_file_changed(self) -> None:
        start = {"commit": "abc", "files_sha256": {"a.txt": "deadbeef" * 8}}
        current = {"commit": "abc", "files_sha256": {"a.txt": "cafebabe" * 8}}
        drift = runner.detect_snapshot_drift(start, current)
        self.assertIsNotNone(drift)
        assert drift is not None
        self.assertTrue(drift.startswith("file_changed:a.txt"))

    def test_detect_snapshot_drift_none(self) -> None:
        start = {"commit": "abc", "files_sha256": {}}
        current = {"commit": "abc", "files_sha256": {}}
        self.assertIsNone(runner.detect_snapshot_drift(start, current))

    def test_analyze_destructive_change_detects_deletions(self) -> None:
        repo = self._make_repo_with_file(
            "code.py", "\n".join([f"line {i}" for i in range(80)]) + "\n"
        )
        head_before = runner.capture_head_sha(repo)
        # Delete most of the file
        (repo / "code.py").write_text("line 0\n", encoding="utf-8")
        stat = runner.analyze_destructive_change(repo, head_before)
        self.assertGreater(stat["deletions"], 50)

    def test_analyze_destructive_change_handles_no_diff(self) -> None:
        repo = self._make_repo_with_file("a.txt", "hi\n")
        head_before = runner.capture_head_sha(repo)
        stat = runner.analyze_destructive_change(repo, head_before)
        self.assertEqual(stat["insertions"], 0)
        self.assertEqual(stat["deletions"], 0)


class WorkflowLoadingTests(unittest.TestCase):
    def test_default_stop_rules_when_section_missing(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        ) as fh:
            fh.write(
                """
name = "minimal"
description = ""
[prompt]
default = "do thing"
[counts]
[stopping]
usefulness_threshold = 3
[[stages]]
label = "stage1"
prompt = "{initial_prompt}"
"""
            )
            tmp = Path(fh.name)
        wf = runner.load_workflow(tmp)
        self.assertFalse(wf.stop_rules.no_op_diff_enabled)
        self.assertFalse(wf.stop_rules.snapshot_drift_enabled)
        self.assertFalse(wf.stop_rules.destructive_enabled)

    def test_load_stop_rules_section(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        ) as fh:
            fh.write(
                """
name = "with-rules"
description = ""
[prompt]
default = "go"
[counts]
[stopping]
usefulness_threshold = 4
[stop_rules.no_op_diff]
enabled = true
[stop_rules.time_budget]
enabled = true
seconds = 60
[stop_rules.snapshot_drift]
enabled = true
apply_labels = ["implement", "apply"]
[stop_rules.destructive_without_evidence]
enabled = true
deletion_threshold = 30
[[stages]]
label = "x"
prompt = "{initial_prompt}"
"""
            )
            tmp = Path(fh.name)
        wf = runner.load_workflow(tmp)
        self.assertTrue(wf.stop_rules.no_op_diff_enabled)
        self.assertTrue(wf.stop_rules.time_budget_enabled)
        self.assertEqual(wf.stop_rules.time_budget_seconds, 60.0)
        self.assertTrue(wf.stop_rules.snapshot_drift_enabled)
        self.assertEqual(
            wf.stop_rules.snapshot_drift_apply_labels, ("implement", "apply")
        )
        self.assertTrue(wf.stop_rules.destructive_enabled)
        self.assertEqual(wf.stop_rules.destructive_deletion_threshold, 30)


if __name__ == "__main__":
    unittest.main()
