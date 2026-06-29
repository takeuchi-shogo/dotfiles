"""tools.py の unit テスト: arXiv パース / fetch の SSRF ガード / save_report。"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from research_agent import config, tools

ARXIV_XML = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Test Paper</title>
    <id>http://arxiv.org/abs/1234.5678</id>
    <summary>An example abstract.</summary>
  </entry>
</feed>"""


def test_search_parses_arxiv_xml():
    resp = MagicMock(text=ARXIV_XML)
    resp.raise_for_status = MagicMock()
    with patch("research_agent.tools.requests.get", return_value=resp):
        results = tools.search.invoke({"query": "test", "max_results": 5})
    assert len(results) == 1
    assert results[0]["title"] == "Test Paper"
    assert results[0]["url"] == "http://arxiv.org/abs/1234.5678"
    assert results[0]["abstract"] == "An example abstract."


def test_fetch_rejects_non_arxiv_host():
    assert tools.fetch.invoke({"url": "http://evil.example.com/x"}).startswith("ERROR")


def test_fetch_rejects_ip_literals_and_localhost():
    # 数値 IP（短縮形含む）と localhost は allowlist 厳密一致で即拒否
    for url in ("http://2130706433/x", "http://127.0.0.1/x", "http://localhost/x"):
        assert tools.fetch.invoke({"url": url}).startswith("ERROR")


def test_is_allowed_url_pins_resolved_ip():
    # arxiv.org でも解決 IP が private なら拒否（DNS rebinding 対策）
    with patch("research_agent.tools._host_resolves_to_public", return_value=False):
        assert not tools._is_allowed_url("https://arxiv.org/abs/1")
    with patch("research_agent.tools._host_resolves_to_public", return_value=True):
        assert tools._is_allowed_url("https://arxiv.org/abs/1")


def test_strip_html_removes_script():
    assert tools._strip_html("<p>hello <b>world</b></p>") == "hello world"
    assert "alert" not in tools._strip_html("<script>alert(1)</script>visible")


def test_save_report_writes(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "REPORTS_DIR", tmp_path / "reports")
    path = tools.save_report.invoke({"title": "My Report", "content": "# body"})
    assert Path(path).read_text(encoding="utf-8") == "# body"
