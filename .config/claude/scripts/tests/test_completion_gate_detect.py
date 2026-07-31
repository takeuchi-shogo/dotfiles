import importlib.util
from pathlib import Path

SPEC = Path(__file__).resolve().parent.parent / "policy" / "completion-gate.py"

TASKFILE_WITH_TEST = """version: '3'

tasks:
  build:
    cmds:
      - echo build

  test:
    desc: Run tests
    cmds:
      - echo test
"""

TASKFILE_WITHOUT_TEST = """version: '3'

tasks:
  build:
    cmds:
      - echo build

  validate:
    cmds:
      - echo validate
"""


def _load():
    spec = importlib.util.spec_from_file_location("completion_gate", SPEC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_taskfile_test_target_detected(tmp_path):
    (tmp_path / "Taskfile.yml").write_text(TASKFILE_WITH_TEST)
    assert _load()._has_taskfile_test_target(str(tmp_path)) is True


def test_taskfile_yaml_extension_detected(tmp_path):
    (tmp_path / "Taskfile.yaml").write_text(TASKFILE_WITH_TEST)
    assert _load()._has_taskfile_test_target(str(tmp_path)) is True


def test_taskfile_without_test_target_not_detected(tmp_path):
    (tmp_path / "Taskfile.yml").write_text(TASKFILE_WITHOUT_TEST)
    assert _load()._has_taskfile_test_target(str(tmp_path)) is False


def test_no_taskfile_not_detected(tmp_path):
    assert _load()._has_taskfile_test_target(str(tmp_path)) is False


def test_nested_test_key_not_mistaken_for_target(tmp_path):
    (tmp_path / "Taskfile.yml").write_text(
        "version: '3'\n\ntasks:\n  build:\n    env:\n      test:\n"
    )
    assert _load()._has_taskfile_test_target(str(tmp_path)) is False


def test_detect_test_command_prefers_taskfile(tmp_path, monkeypatch):
    (tmp_path / "Taskfile.yml").write_text(TASKFILE_WITH_TEST)
    (tmp_path / "go.mod").write_text("module example.com/x\n")
    mod = _load()
    monkeypatch.setattr(mod.shutil, "which", lambda _: "/usr/bin/task")
    monkeypatch.chdir(tmp_path)
    assert mod._detect_test_command() == "task test"


def test_detect_test_command_falls_back_when_task_missing(tmp_path, monkeypatch):
    (tmp_path / "Taskfile.yml").write_text(TASKFILE_WITH_TEST)
    (tmp_path / "go.mod").write_text("module example.com/x\n")
    mod = _load()
    monkeypatch.setattr(mod.shutil, "which", lambda _: None)
    monkeypatch.chdir(tmp_path)
    assert mod._detect_test_command() == "go test ./..."


def test_dotfiles_repo_itself_has_a_test_command(monkeypatch):
    """Regression: the repo's own Stop gate must not fall into the no-tests branch."""
    repo_root = Path(__file__).resolve().parents[4]
    mod = _load()
    monkeypatch.setattr(mod.shutil, "which", lambda _: "/usr/bin/task")
    monkeypatch.chdir(repo_root)
    assert mod._detect_test_command() is not None
