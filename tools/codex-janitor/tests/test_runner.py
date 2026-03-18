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


if __name__ == "__main__":
    unittest.main()
