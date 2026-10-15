"""imozuru fetch.py の安全策（URL scheme・subprocess timeout）の単体テスト。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]
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


def test_fetch_source_fails_on_bad_scheme(tmp_path: Path) -> None:
    sources = tmp_path / "sources"
    sources.mkdir()
    code = fetch.fetch_source(sources, "bad", "file:///etc/passwd", sources)
    assert code == 1
