import importlib.util
from pathlib import Path

SPEC = Path(__file__).resolve().parent.parent / "runtime" / "memory-vec-stop-hook.py"


def _load():
    spec = importlib.util.spec_from_file_location("mv_stop", SPEC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_scan_dirs_includes_vault_article_folders(monkeypatch, tmp_path):
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(tmp_path / "vault"))
    mod = _load()
    dirs = mod.scan_dirs()
    names = [Path(d).name for d in dirs]
    assert "05-Literature" in names
    assert "09-TechTrends" in names
    assert any("memory" in str(d) for d in dirs)


def test_scan_dirs_defaults_to_home_vault_without_env(monkeypatch):
    monkeypatch.delenv("OBSIDIAN_VAULT_PATH", raising=False)
    mod = _load()
    dirs = mod.scan_dirs()
    assert len(dirs) == 4
    assert any(str(d).endswith("Obsidian Vault/05-Literature") for d in dirs)
    assert any(str(d).endswith(".cache/research-agent/experience") for d in dirs)
