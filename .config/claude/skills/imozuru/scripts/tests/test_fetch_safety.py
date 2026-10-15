"""imozuru fetch.py の安全策（URL scheme・subprocess timeout・OCR 打ち切り）の単体テスト。"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]
FETCH_PY = SCRIPTS / "fetch.py"
sys.path.insert(0, str(SCRIPTS))

import fetch  # noqa: E402

SUBPROCESS_BANNED_ATTRS = frozenset(
    {"run", "Popen", "check_output", "call", "check_call"}
)
OS_BANNED_ATTRS = frozenset({"system", "popen"})


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


def test_fetch_source_fails_on_bad_scheme(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
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


def test_ocr_pdf_marks_page_cap_truncation(tmp_path: Path) -> None:
    """pdftoppm が上限ページ数を返したら打ち切りを先頭に書き、理由を返す。"""
    pdf = tmp_path / "long.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    tmp = tmp_path / ".long-ocr"

    def fake_run(cmd, **kwargs):
        if cmd[0] == "pdftoppm":
            tmp.mkdir(exist_ok=True)
            for i in range(1, fetch.OCR_MAX_PAGES + 1):
                (tmp / f"p-{i}.png").write_bytes(b"img")
            assert "-l" in cmd
            assert str(fetch.OCR_MAX_PAGES) in cmd
            return subprocess.CompletedProcess(cmd, 0)
        if cmd[0] == "tesseract":
            return subprocess.CompletedProcess(cmd, 0, stdout="page text\n", stderr="")
        raise AssertionError(cmd)

    with (
        patch.object(fetch, "missing", return_value=[]),
        patch.object(fetch, "run_subprocess", side_effect=fake_run),
    ):
        text, reason = fetch.ocr_pdf(pdf)

    assert reason == f"ページ上限 {fetch.OCR_MAX_PAGES}"
    assert text.startswith("（OCR 打ち切り:")
    assert "部分結果" in text.splitlines()[0]
    assert pdf.with_suffix(".txt").read_text(encoding="utf-8").startswith(
        "（OCR 打ち切り:"
    )


def test_ocr_pdf_marks_time_cap_truncation(tmp_path: Path) -> None:
    pdf = tmp_path / "slow.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    tmp = tmp_path / ".slow-ocr"
    ticks = {"n": 0}

    def fake_monotonic() -> float:
        # pdftoppm 後のループ1回目で総時間上限を超える
        ticks["n"] += 1
        return 0.0 if ticks["n"] < 2 else float(fetch.OCR_TOTAL_TIMEOUT + 1)

    def fake_run(cmd, **kwargs):
        if cmd[0] == "pdftoppm":
            tmp.mkdir(exist_ok=True)
            (tmp / "p-1.png").write_bytes(b"img")
            (tmp / "p-2.png").write_bytes(b"img")
            return subprocess.CompletedProcess(cmd, 0)
        raise AssertionError(f"tesseract should not run after time cap: {cmd}")

    with (
        patch.object(fetch, "missing", return_value=[]),
        patch.object(fetch, "run_subprocess", side_effect=fake_run),
        patch.object(fetch.time, "monotonic", side_effect=fake_monotonic),
    ):
        text, reason = fetch.ocr_pdf(pdf)

    assert reason == "総時間上限"
    assert "OCR 打ち切り" in text.splitlines()[0]


def test_fetch_source_fails_when_ocr_truncated(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sources = tmp_path / "sources"
    sources.mkdir()
    pdf_bytes = b"%PDF-1.4 truncated-doc"

    def fake_download(url: str):
        return pdf_bytes, "application/pdf"

    with (
        patch.object(fetch, "download", side_effect=fake_download),
        patch.object(fetch, "pdf_to_text", return_value="x"),
        patch.object(
            fetch, "ocr_pdf", return_value=("（OCR 打ち切り: ページ上限 40）\n\nbody", "ページ上限 40")
        ),
    ):
        code = fetch.fetch_source(
            sources, "paper", "https://example.com/a.pdf", sources
        )

    assert code == 1
    out = capsys.readouterr().out
    assert out.startswith("FAIL\tpaper\t")
    assert "OCR 打ち切り" in out
    assert "ページ上限 40" in out
    assert "部分結果" in out
    assert list(sources.iterdir()) == []


def test_no_direct_process_spawn_outside_run_subprocess() -> None:
    """AST: subprocess/os のプロセス起動は run_subprocess 経由のみ。"""
    tree = ast.parse(FETCH_PY.read_text(encoding="utf-8"))
    findings: list[str] = []
    subprocess_aliases: set[str] = {"subprocess"}
    os_aliases: set[str] = {"os"}
    # from subprocess import run as r → r is banned
    imported_banned: dict[str, str] = {}

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

        def visit_Import(self, node: ast.Import) -> None:
            for alias in node.names:
                if alias.name == "subprocess":
                    subprocess_aliases.add(alias.asname or "subprocess")
                if alias.name == "os":
                    os_aliases.add(alias.asname or "os")

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
            if node.module == "subprocess":
                for alias in node.names:
                    if alias.name in SUBPROCESS_BANNED_ATTRS:
                        imported_banned[alias.asname or alias.name] = (
                            f"subprocess.{alias.name}"
                        )
            if node.module == "os":
                for alias in node.names:
                    if alias.name in OS_BANNED_ATTRS:
                        imported_banned[alias.asname or alias.name] = f"os.{alias.name}"

        def visit_Call(self, node: ast.Call) -> None:
            owner = self.stack[-1] if self.stack else "<module>"
            func = node.func
            label = None
            if isinstance(func, ast.Name) and func.id in imported_banned:
                label = imported_banned[func.id]
            elif isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                if (
                    func.value.id in subprocess_aliases
                    and func.attr in SUBPROCESS_BANNED_ATTRS
                ):
                    label = f"subprocess.{func.attr}"
                elif func.value.id in os_aliases and func.attr in OS_BANNED_ATTRS:
                    label = f"os.{func.attr}"
            # run_subprocess 内の subprocess.run のみ許可
            allowed = owner == "run_subprocess" and label == "subprocess.run"
            if label and not allowed:
                findings.append(f"L{node.lineno}:{owner}:{label}")
            self.generic_visit(node)

    Visitor().visit(tree)
    assert findings == [], f"banned process spawn: {findings}"
