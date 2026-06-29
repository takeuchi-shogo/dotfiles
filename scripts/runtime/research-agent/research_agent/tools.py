"""ツール: arXiv 検索 / 安全な fetch / レポート保存。

fetch の SSRF 防御（codex BLOCK #1 反映）:
- 主防御 = arxiv.org allowlist（host 厳密一致）。LLM が任意 URL を取れない。host が
  数値 IP（`2130706433` 等の短縮形含む）でも allowlist 厳密一致で即拒否されるため、
  sources.py の inet_aton 短縮形パースは不要（allowlist 前提で簡略化）。
- defense-in-depth = fetch-time に解決 IP を private/loopback/link-local denylist で
  再チェック（DNS rebinding 対策）。
- redirect 不追従 / Content-Type 限定 / サイズ上限 / timeout。
"""

import ipaddress
import re
import socket
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import urlsplit

import requests
from langchain_core.tools import tool

from . import config

_ATOM = "{http://www.w3.org/2005/Atom}"


def _host_resolves_to_public(host: str) -> bool:
    """host の解決 IP が全て public（private/loopback/link-local 等でない）か。"""
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0])
        except ValueError:
            return False
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_unspecified
            or ip.is_multicast
        ):
            return False
    return True


def _is_allowed_url(url: str) -> bool:
    """https + host が arxiv.org allowlist + public IP 解決、を全て満たすか。

    https のみ許可（平文 http は MITM で本文を改竄されるため拒否）。
    """
    parts = urlsplit(url)
    if parts.scheme != "https":
        return False
    host = (parts.hostname or "").lower()
    if host not in config.ALLOWED_FETCH_HOSTS:
        return False
    return _host_resolves_to_public(host)


def _strip_html(html: str) -> str:
    """簡易 HTML→text。script/style を除去しタグを落として空白を畳む。"""
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


@tool
def search(query: str, max_results: int = 8) -> list[dict]:
    """arXiv を検索し、論文の {title, url, abstract} のリストを返す。"""
    resp = requests.get(
        config.ARXIV_API,
        params={
            "search_query": f"all:{query}",
            "max_results": max_results,
            "sortBy": "relevance",
        },
        timeout=config.FETCH_TIMEOUT,
    )
    resp.raise_for_status()
    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError as e:
        return [
            {"title": "ERROR", "url": "", "abstract": f"arXiv XML parse error: {e}"}
        ]
    out: list[dict] = []
    for entry in root.findall(f"{_ATOM}entry"):
        url = (
            (entry.findtext(f"{_ATOM}id") or "")
            .strip()
            .replace("http://", "https://", 1)
        )
        out.append(
            {
                "title": (entry.findtext(f"{_ATOM}title") or "").strip(),
                "url": url,
                "abstract": (entry.findtext(f"{_ATOM}summary") or "").strip(),
            }
        )
    return out


@tool
def fetch(url: str) -> str:
    """指定 URL（arxiv.org のみ許可）の本文をクリーンテキストで返す。"""
    if not _is_allowed_url(url):
        return f"ERROR: URL not allowed (arxiv.org のみ取得可): {url}"
    resp = requests.get(
        url, timeout=config.FETCH_TIMEOUT, allow_redirects=False, stream=True
    )
    if resp.status_code != 200:
        return f"ERROR: HTTP {resp.status_code} for {url}"
    ctype = resp.headers.get("Content-Type", "").split(";")[0].strip().lower()
    if ctype and not any(
        ctype.startswith(t) for t in config.FETCH_ALLOWED_CONTENT_TYPES
    ):
        return f"ERROR: disallowed Content-Type {ctype} for {url}"
    chunks: list[bytes] = []
    total = 0
    for chunk in resp.iter_content(8192):
        chunks.append(chunk)
        total += len(chunk)
        if total >= config.FETCH_MAX_BYTES:
            break
    text = b"".join(chunks).decode("utf-8", errors="replace")
    return _strip_html(text)


@tool
def save_report(title: str, content: str) -> str:
    """調査レポートを reports ディレクトリに保存し、パスを返す（Tier 1）。"""
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:50] or "report"
    date_s = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = config.REPORTS_DIR / f"{date_s}-{slug}.md"
    path.write_text(content, encoding="utf-8")
    return str(path)


TOOLS = [search, fetch, save_report]
