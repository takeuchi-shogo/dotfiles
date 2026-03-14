"""Tips 汎化モジュール — エンティティ抽象化で learnings の再利用性を高める。

論文 arXiv:2603.10600 の Subtask Description Generalization に基づく。
- Entity abstraction: ユーザーパス、ハッシュ、バージョン等を汎化
- 目的: 類似パターンの発見率向上
"""

import re

_GENERALIZATIONS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"/Users/\w+/"), "{user_home}/"),
    (re.compile(r"/home/\w+/"), "{user_home}/"),
    (re.compile(r"\b[a-f0-9]{7,40}\b"), "{hash}"),
    # IP must come before version — otherwise 192.168.1 matches as {version}
    (
        re.compile(r"\b(?:192\.168|10\.\d+|172\.(?:1[6-9]|2\d|3[01]))\.\d+\.\d+\b"),
        "{ip}",
    ),
    (re.compile(r"\b\d+\.\d+\.\d+(?:-[\w.]+)?\b"), "{version}"),
    (re.compile(r"\bport\s+\d+", re.I), "port {port}"),
    (re.compile(r":\d{4,5}\b"), ":{port}"),
]


def generalize_text(text: str) -> str:
    """テキスト内のエンティティを汎化プレースホルダに置換する。"""
    for pattern, replacement in _GENERALIZATIONS:
        text = pattern.sub(replacement, text)
    return text


def generalize_entry(entry: dict) -> dict:
    """JSONL エントリの message/detail フィールドを汎化し、generalized_* を追加する。"""
    result = dict(entry)
    for field in ("message", "detail"):
        value = entry.get(field)
        if value and isinstance(value, str):
            result[f"generalized_{field}"] = generalize_text(value)
    return result
