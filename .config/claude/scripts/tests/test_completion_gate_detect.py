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


def test_pyproject_without_pytest_is_not_a_pytest_project(tmp_path, monkeypatch):
    """Regression: a uv tool-only pyproject (kwdp) failed every Stop.

    The gate ran pytest there and hit 'No module named pytest'.
    """
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndependencies = []\n\n[tool.uv]\npackage = false\n'
    )
    mod = _load()
    monkeypatch.setattr(mod.shutil, "which", lambda _: None)
    monkeypatch.chdir(tmp_path)
    assert mod._detect_test_command() is None


def test_pyproject_with_pytest_config_runs_pytest(tmp_path, monkeypatch):
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\n\n[tool.pytest.ini_options]\ntestpaths = ["tests"]\n'
    )
    mod = _load()
    monkeypatch.setattr(mod.shutil, "which", lambda _: None)
    monkeypatch.chdir(tmp_path)
    assert mod._detect_test_command() == "python3 -m pytest --tb=short -q"


def test_pytest_ini_runs_pytest(tmp_path, monkeypatch):
    (tmp_path / "pytest.ini").write_text("[pytest]\n")
    mod = _load()
    monkeypatch.setattr(mod.shutil, "which", lambda _: None)
    monkeypatch.chdir(tmp_path)
    assert mod._detect_test_command() == "python3 -m pytest --tb=short -q"


def test_setup_cfg_pytest_section_runs_pytest(tmp_path, monkeypatch):
    (tmp_path / "pyproject.toml").write_text(
        '[build-system]\nrequires = ["setuptools"]\n'
    )
    (tmp_path / "setup.cfg").write_text("[tool:pytest]\ntestpaths = tests\n")
    mod = _load()
    monkeypatch.setattr(mod.shutil, "which", lambda _: None)
    monkeypatch.chdir(tmp_path)
    assert mod._detect_test_command() == "python3 -m pytest --tb=short -q"


def test_root_conftest_alone_runs_pytest(tmp_path, monkeypatch):
    (tmp_path / "conftest.py").write_text("")
    mod = _load()
    monkeypatch.setattr(mod.shutil, "which", lambda _: None)
    monkeypatch.chdir(tmp_path)
    assert mod._detect_test_command() == "python3 -m pytest --tb=short -q"
