"""imozuru fetch.py の安全策（URL scheme・subprocess timeout）の単体テスト。"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]
FETCH_PY = SCRIPTS / "fetch.py"
sys.path.insert(0, str(SCRIPTS))

import fetch  # noqa: E402


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "ftp://example.com/a.pdf",
        "javascript:alert(1)",
        "data:text/plain,hi",
        "/relative/path",
        "example.com/no-scheme",
    ],
)
def test_ensure_http_url_rejects_non_http(url: str) -> None:
    with pytest.raises(ValueError, match="unsupported URL scheme"):
        fetch.ensure_http_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/paper.pdf",
        "http://example.com/a",
        "HTTPS://Example.COM/X",
    ],
)
def test_ensure_http_url_allows_http_https(url: str) -> None:
    fetch.ensure_http_url(url)


def test_download_rejects_file_scheme_before_open() -> None:
    with patch.object(fetch, "_OPENER") as opener:
        with pytest.raises(ValueError, match="unsupported URL scheme"):
            fetch.download("file:///tmp/secret.pdf")
        opener.open.assert_not_called()


def test_run_subprocess_passes_timeout() -> None:
    completed = subprocess.CompletedProcess(["true"], 0, stdout=b"", stderr=b"")
    with patch("subprocess.run", return_value=completed) as mocked:
        result = fetch.run_subprocess(["true"], timeout=7)
        assert result.returncode == 0
        assert mocked.call_args.kwargs["timeout"] == 7


def test_run_subprocess_handles_timeout_expired() -> None:
    with patch(
        "subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd=["sleep", "99"], timeout=1),
    ):
        result = fetch.run_subprocess(
            ["sleep", "99"],
            timeout=1,
            capture_output=True,
            encoding="utf-8",
        )
    assert result.returncode == 124
    assert result.stdout == ""
    assert "timeout" in result.stderr


def test_run_subprocess_decodes_timeout_stdout_bytes() -> None:
    """TimeoutExpired.stdout が bytes のとき、text mode では str に直す。"""
    with patch(
        "subprocess.run",
        side_effect=subprocess.TimeoutExpired(
            cmd=["cmd"],
            timeout=1,
            output=b"partial-\xe3\x81\x82",
            stderr=b"err",
        ),
    ):
        result = fetch.run_subprocess(
            ["cmd"],
            timeout=1,
            capture_output=True,
            encoding="utf-8",
        )
    assert result.returncode == 124
    assert isinstance(result.stdout, str)
    assert "partial-" in result.stdout
    assert isinstance(result.stderr, str)
    assert result.stderr == "err"


def test_fetch_source_fails_on_bad_scheme(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    sources = tmp_path / "sources"
    sources.mkdir()
    with patch.object(fetch, "_OPENER") as opener:
        code = fetch.fetch_source(sources, "bad", "file:///etc/passwd", sources)
        opener.open.assert_not_called()
    assert code == 1
    out = capsys.readouterr().out
    assert out.startswith("FAIL\tbad\t")
    assert "unsupported URL scheme" in out
    assert "file" in out
    assert list(sources.iterdir()) == []


def test_all_subprocess_run_calls_go_through_run_subprocess() -> None:
    """AST: subprocess.run の直接呼び出しは run_subprocess 内だけ。"""
    tree = ast.parse(FETCH_PY.read_text(encoding="utf-8"))
    direct: list[tuple[int, str]] = []

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack: list[str] = []

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        def visit_Call(self, node: ast.Call) -> None:
            func = node.func
            is_run = (
                isinstance(func, ast.Attribute)
                and func.attr == "run"
                and isinstance(func.value, ast.Name)
                and func.value.id == "subprocess"
            )
            if is_run:
                owner = self.stack[-1] if self.stack else "<module>"
                if owner != "run_subprocess":
                    direct.append((node.lineno, owner))
            self.generic_visit(node)

    Visitor().visit(tree)
    assert direct == [], f"subprocess.run outside run_subprocess: {direct}"


def test_run_subprocess_is_used_in_source() -> None:
    src = FETCH_PY.read_text(encoding="utf-8")
    assert "def run_subprocess(" in src
    assert src.count("run_subprocess(") >= 5
