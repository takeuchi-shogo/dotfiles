"""Secret redactor for JSONL writes from Claude Code hooks.

Applied to each entry before writing to disk (session_events, trace store).
Patterns derived from the A1 audit (docs/security/2026-04-17-jsonl-secret-audit.md)
and ported from tools/otel-session-analyzer/internal/redactor/redactor.go.

Scope (important): this module only covers JSONL written via hook Python code
paths integrated with redact_obj(). Claude Code itself writes transcripts to
~/.claude/projects/*.jsonl outside this path; those require post-hoc sanitizer
(see docs/specs/2026-04-17-memory-schema-retention.md scope section).

Design:
- redact(s): apply all patterns to a string, return masked string.
- redact_obj(obj): recursively redact strings in dict/list/tuple with cycle +
  depth guards.
- Patterns include skip heuristics to reduce false positives observed in A1.
  Heuristics apply only to the VALUE portion of the match (after the key=/:)
  to avoid trivial bypass by co-locating hint words with real secrets.
"""

from __future__ import annotations

import re
from typing import Any

MASK = "[REDACTED]"
MAX_DEPTH = 100

# Placeholder prefixes: value must START with one to be skipped. Substring
# matching was trivially bypassable by embedding a hint in a real secret.
_PLACEHOLDER_PREFIXES: tuple[str, ...] = (
    "your_",
    "example",
    "placeholder",
    "test_key",
    "dummy",
    "xxxxx",
    "localhost",
)

# Substring hints for project-specific conventions. Only highly-specific tokens
# belong here; generic words (e.g. "example") MUST use prefix matching.
_PLACEHOLDER_SUBSTRINGS: tuple[str, ...] = (
    "_local_",  # hearable_local_password convention
)


def _extract_value(match_text: str) -> str:
    """Return the value portion of a key=value or key: value match.

    For "Bearer foo", returns "foo".
    For "api_key=abc", returns "abc".
    Falls back to match_text if no separator is found.
    """
    m = re.search(r"(?i)(?:Bearer\s+|[=:]\s*['\"]?)(.+)$", match_text)
    if m:
        return m.group(1).rstrip("'\"")
    return match_text


def _value_is_placeholder(value: str) -> bool:
    """Heuristic: is the value itself a placeholder / already-masked token?"""
    if not value:
        return True
    low = value.lower()
    if low.startswith(_PLACEHOLDER_PREFIXES):
        return True
    if any(sub in low for sub in _PLACEHOLDER_SUBSTRINGS):
        return True
    if low.startswith("[redacted") or "redacted]" in low:
        return True
    # Accept *** sentinels but not a single * embedded in a realistic secret.
    if re.search(r"\*{3,}", value):
        return True
    return False


def _skip_if_placeholder(m: re.Match[str]) -> str:
    value = _extract_value(m.group(0))
    if _value_is_placeholder(value):
        return m.group(0)
    return MASK


def _redact_private_key(s: str) -> str:
    # Armored PEM / PGP block with actual base64 payload within 80 chars of header.
    pattern = re.compile(
        r"-----BEGIN [A-Z0-9 ]+?(?:KEY|BLOCK)-----[\s\S]{0,80}?[A-Za-z0-9+/=]{20,}",
        re.MULTILINE,
    )
    return pattern.sub(MASK, s)


def _redact_aws_access_key(s: str) -> str:
    return re.sub(r"AKIA[0-9A-Z]{16}", MASK, s)


def _redact_github_pat(s: str) -> str:
    patterns = [
        re.compile(r"ghp_[A-Za-z0-9]{36}"),
        re.compile(r"github_pat_[A-Za-z0-9_]{82}"),
    ]
    for p in patterns:
        s = p.sub(MASK, s)
    return s


def _redact_sk_token(s: str) -> str:
    # Anthropic / OpenAI style sk- tokens. Word boundary avoids "risk-analysis".
    pattern = re.compile(r"(?<![A-Za-z0-9_])sk-[A-Za-z0-9_\-]{20,}")
    return pattern.sub(MASK, s)


def _redact_stripe(s: str) -> str:
    pattern = re.compile(r"(?:sk|rk|pk)_(?:live|test)_[A-Za-z0-9]{20,}")
    return pattern.sub(MASK, s)


def _redact_slack(s: str) -> str:
    pattern = re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")
    return pattern.sub(MASK, s)


def _redact_google_api_key(s: str) -> str:
    pattern = re.compile(r"AIza[0-9A-Za-z_\-]{35}")
    return pattern.sub(MASK, s)


def _redact_google_oauth(s: str) -> str:
    pattern = re.compile(r"ya29\.[0-9A-Za-z_\-]{20,}")
    return pattern.sub(MASK, s)


def _redact_jwt(s: str) -> str:
    pattern = re.compile(
        r"eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"
    )
    return pattern.sub(MASK, s)


def _redact_db_url(s: str) -> str:
    pattern = re.compile(
        r"(?i)(postgres|postgresql|mysql|mongodb|redis|amqp)://"
        r"[^\s:/@]+:[^\s@/]{4,}@"
    )
    return pattern.sub(lambda m: m.group(1) + "://" + MASK + "@", s)


def _redact_bearer(s: str) -> str:
    pattern = re.compile(r"(?i)Bearer\s+[a-zA-Z0-9_\-.]{10,}")
    return pattern.sub(_skip_if_placeholder, s)


def _redact_api_key_assignment(s: str) -> str:
    # Narrowed key names to avoid csrf_token / next_page_token FPs.
    pattern = re.compile(
        r"(?i)(?:api[_-]?key|api[_-]?secret|access[_-]?token|auth[_-]?token"
        r"|client[_-]?secret)[=:]\s*['\"]?[A-Za-z0-9_\-]{20,}"
    )
    return pattern.sub(_skip_if_placeholder, s)


def _redact_password(s: str) -> str:
    pattern = re.compile(r"(?i)(?:password|passwd|pwd)[=:]\s*['\"]?\S{8,}")
    return pattern.sub(_skip_if_placeholder, s)


_PIPELINE = (
    _redact_private_key,
    _redact_aws_access_key,
    _redact_github_pat,
    _redact_stripe,
    _redact_slack,
    _redact_google_api_key,
    _redact_google_oauth,
    _redact_jwt,
    _redact_db_url,
    _redact_sk_token,
    _redact_bearer,
    _redact_api_key_assignment,
    _redact_password,
)


def redact(s: str) -> str:
    """Apply all redaction patterns to a string."""
    if not isinstance(s, str) or not s:
        return s
    for fn in _PIPELINE:
        s = fn(s)
    return s


def redact_obj(obj: Any, _depth: int = 0, _seen: set[int] | None = None) -> Any:
    """Recursively redact strings inside containers.

    Returns a new object; original is not mutated. Keys in dicts pass through
    (keys are schema fields, not secrets). Depth and cycle guards protect hooks
    from stack overflow / DoS on malformed payloads.
    """
    if _depth > MAX_DEPTH:
        return "[REDACTED:depth]"
    if isinstance(obj, str):
        return redact(obj)
    if isinstance(obj, (dict, list, tuple)):
        seen = set() if _seen is None else _seen
        if id(obj) in seen:
            return "[REDACTED:cycle]"
        seen = seen | {id(obj)}
        if isinstance(obj, dict):
            return {k: redact_obj(v, _depth + 1, seen) for k, v in obj.items()}
        if isinstance(obj, list):
            return [redact_obj(v, _depth + 1, seen) for v in obj]
        return tuple(redact_obj(v, _depth + 1, seen) for v in obj)
    return obj
