#!/usr/bin/env python3
"""WebFetch Truncation Detector — silent truncation 検出 PostToolUse hook.

Claude Code v2.1.126 で WebFetch は内部 Haiku 要約 + 100k chars 上限の観測あり。
trusted_domains 外で出力が極端に短い場合 (要約された可能性) を検出する。

Triggered by: PostToolUse (matcher: WebFetch)
Input: stdin JSON {tool_name, tool_input.{url,prompt}, tool_response or tool_output}
Output: stdout に hook input を passthrough。
        webfetch_truncation_suspect event を friction-events.jsonl に追記。

Threshold:
- 出力長 < SHORT_OUTPUT_THRESHOLD かつ trusted 外 → suspect
- ZeroDivision / 取得失敗等は graceful degradation (passthrough 維持)

Known limitation (false-negative):
本 hook は出力長のみで判定するため、入力 100k chars 上限で truncate されたが
出力 markdown が 8000 chars 以上残っている「微妙な truncation」を見逃す可能性が
ある。HEAD request で content-length を取得して input/output 比率で判定する
拡張は別 plan 候補 (codex-reviewer 指摘 2026-05-06)。現状は「明らかに短い出力」
の検出に留め、hook の網羅性より hook 自身の軽量性を優先する。

詳細: references/web-fetch-policy.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import (  # noqa: E402
    check_tool,
    load_hook_input,
    output_passthrough,
    run_hook,
)

# 出力長の下限。これ未満で trusted 外なら suspect 候補とする。
# 実観測 (Wikipedia 長記事) で WebFetch 出力が 1k〜数 k に落ちる事例があるため、
# 偽陽性回避で 8000 文字を採用 (まともな markdown はこれ以上)。
SHORT_OUTPUT_THRESHOLD = 8000

TRUSTED_DOMAINS_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data" / "trusted-domains.json"
)
ALT_TRUSTED_DOMAINS_PATH = Path.home() / ".claude" / "data" / "trusted-domains.json"


def load_trusted_domains() -> set[str]:
    """trusted_domains を読む。読めなければ空集合 (= fail-safe で全 non-trusted)。

    fail-safe で空集合を返した場合、stderr に警告を出す (友好的な誤検知防止)。
    """
    for path in (TRUSTED_DOMAINS_PATH, ALT_TRUSTED_DOMAINS_PATH):
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return set(data.get("trusted_domains", []))
        except (json.JSONDecodeError, OSError) as exc:
            sys.stderr.write(
                f"[webfetch-truncation-detector] trusted-domains.json read failed at "
                f"{path}: {exc}. Falling back to empty set (all domains non-trusted).\n"
            )
            continue
    sys.stderr.write(
        "[webfetch-truncation-detector] trusted-domains.json not found at expected "
        "paths. Falling back to empty set (all domains non-trusted).\n"
    )
    return set()


def extract_domain(url: str) -> str:
    """URL から hostname を抽出。スキーム欠落でも動作。"""
    try:
        parsed = urlparse(url if "://" in url else f"https://{url}")
        return (parsed.hostname or "").lower()
    except (ValueError, AttributeError):
        return ""


def is_trusted(domain: str, trusted: set[str]) -> bool:
    """domain (または親 domain) が trusted に含まれるか。"""
    if not domain:
        return False
    if domain in trusted:
        return True
    parts = domain.split(".")
    for i in range(1, len(parts) - 1):
        if ".".join(parts[i:]) in trusted:
            return True
    return False


def _coerce_str(val: Any) -> str:
    """文字列に正規化。

    対応する型:
    - str: そのまま返す
    - list: Claude content block 形式 ({"type": "text", "text": "..."}) を抽出して連結
    - dict: 既知の sub-key (content/text/output/body) を試す
    - その他: 空文字列
    """
    if isinstance(val, str):
        return val
    if isinstance(val, list):
        parts: list[str] = []
        for item in val:
            text = _coerce_str(item)
            if text:
                parts.append(text)
        return "\n".join(parts)
    if not isinstance(val, dict):
        return ""
    for sub in ("content", "text", "output", "body"):
        inner = val.get(sub)
        if isinstance(inner, str):
            return inner
    return ""


def get_response_text(data: dict[str, Any]) -> str:
    """tool_response または tool_output から本文を取り出す。型バリエーションを吸収。"""
    for key in ("tool_response", "tool_output"):
        text = _coerce_str(data.get(key))
        if text:
            return text
    return ""


def emit_suspect_event(
    url: str,
    domain: str,
    visible_chars: int,
    trusted: bool,
) -> None:
    """webfetch_truncation_suspect event を friction-events.jsonl に追記する。"""
    try:
        from session_events import append_to_learnings

        append_to_learnings(
            "friction-events",
            {
                "type": "event",
                "friction_class": "webfetch_truncation_suspect",
                "action_surface": "WebFetch",
                "severity": "info",
                "evidence": {
                    "url": url,
                    "domain": domain,
                    "visible_chars": visible_chars,
                    "threshold": SHORT_OUTPUT_THRESHOLD,
                    "trusted_domain": trusted,
                    "policy_ref": "references/web-fetch-policy.md",
                },
            },
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"[webfetch-truncation-detector] event emit failed: {exc}\n")


def is_suspect(visible_chars: int, trusted: bool) -> bool:
    """suspect 判定: 短すぎる出力 + trusted 外 + 空でない。"""
    if trusted:
        return False
    if visible_chars <= 0:
        return False
    return visible_chars < SHORT_OUTPUT_THRESHOLD


def main() -> None:
    data = load_hook_input()
    if not data:
        return

    if not check_tool(data, "WebFetch"):
        output_passthrough(data)
        return

    url = data.get("tool_input", {}).get("url", "") or ""
    domain = extract_domain(url)
    trusted = is_trusted(domain, load_trusted_domains())

    visible_chars = len(get_response_text(data))

    if is_suspect(visible_chars, trusted):
        emit_suspect_event(url, domain, visible_chars, trusted)

    output_passthrough(data)


if __name__ == "__main__":
    run_hook("webfetch-truncation-detector", main)
