"""Tests for redactor.py."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from redactor import MASK, redact, redact_obj


class TestTruePositives:
    def test_private_key_block_with_payload(self):
        s = "-----BEGIN RSA PRIVATE KEY-----\nMIIJRAIBADANBgkqhkiG9w0BAQ"
        assert MASK in redact(s)

    def test_aws_access_key(self):
        assert redact("AKIAIOSFODNN7EXAMPLE") == MASK

    def test_github_pat(self):
        s = "ghp_" + "a" * 36
        assert redact(s) == MASK

    def test_sk_token(self):
        s = "sk-proj-" + "A" * 30
        assert redact(s) == MASK

    def test_sk_token_in_sentence(self):
        s = "OpenAI key: sk-" + "X" * 40 + " expires tomorrow"
        out = redact(s)
        assert MASK in out
        assert "expires tomorrow" in out

    def test_bearer_token_real(self):
        s = "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.payload.sig"
        assert MASK in redact(s)

    def test_api_key_assignment(self):
        s = "OPENAI_API_KEY=sk-abcdef0123456789ABCDEFGHIJKLMNOP"
        assert MASK in redact(s)


class TestFalsePositives:
    def test_private_key_docs_mention(self):
        # Only header, no payload — should NOT be redacted
        s = "Patterns: `-----BEGIN RSA PRIVATE KEY-----` detected"
        # Payload check requires 20+ base64 chars within 40 chars after header
        assert redact(s) == s

    def test_sk_token_in_risk(self):
        s = "tmp/plans/risk-analysis.md is the file"
        assert redact(s) == s

    def test_sk_token_in_task_id(self):
        s = '"toolUseID":"toolu_01task_abc_def_ghi"'
        # No "sk-" so never matches
        assert redact(s) == s

    def test_bearer_masked_value(self):
        s = "Authorization: Bearer ***"
        # _looks_placeholder returns True because of '*'
        # but regex requires {10,} after "Bearer " — "***" is only 3 chars, no match
        assert redact(s) == s

    def test_bearer_star_in_value(self):
        s = "Authorization: Bearer abc*****def123"
        # Contains *, placeholder -> skip
        assert redact(s) == s

    def test_api_key_placeholder(self):
        s = "FATHOM_API_KEY=your_fathom_key_here_placeholder"
        assert redact(s) == s

    def test_password_local_db(self):
        s = "POSTGRES_PASSWORD: hearable_local_password"
        assert redact(s) == s

    def test_password_empty(self):
        s = "password: ''"
        # Too short (<8 chars after) — no match anyway
        assert redact(s) == s


class TestRedactObj:
    def test_str(self):
        assert redact_obj("AKIAIOSFODNN7EXAMPLE") == MASK

    def test_dict(self):
        obj = {"key": "AKIAIOSFODNN7EXAMPLE", "safe": "hello"}
        out = redact_obj(obj)
        assert out == {"key": MASK, "safe": "hello"}

    def test_nested(self):
        obj = {
            "messages": [
                {"role": "user", "content": "my pat is ghp_" + "a" * 36},
                {"role": "assistant", "content": "thanks"},
            ],
            "meta": {"session": "abc"},
        }
        out = redact_obj(obj)
        assert MASK in out["messages"][0]["content"]
        assert out["messages"][1]["content"] == "thanks"
        assert out["meta"]["session"] == "abc"

    def test_non_string_passthrough(self):
        obj = {"count": 42, "flag": True, "ratio": 1.5, "null": None}
        assert redact_obj(obj) == obj

    def test_keys_not_redacted(self):
        # Keys are schema names; even if they resemble patterns, pass through
        obj = {"AKIAIOSFODNN7EXAMPLE": "value"}
        out = redact_obj(obj)
        assert "AKIAIOSFODNN7EXAMPLE" in out
        assert out["AKIAIOSFODNN7EXAMPLE"] == "value"

    def test_does_not_mutate(self):
        original = {"a": "AKIAIOSFODNN7EXAMPLE"}
        snapshot = dict(original)
        redact_obj(original)
        assert original == snapshot


class TestIdempotence:
    def test_redact_twice(self):
        s = "sk-" + "A" * 40
        once = redact(s)
        twice = redact(once)
        assert once == twice == MASK

    def test_masked_value_not_rematched(self):
        # api_key=[REDACTED] should not become api_key=[REDACTED:re-masked]
        s = "api_key=[REDACTED]"
        assert redact(s) == s


class TestNewPatterns:
    def test_slack_bot(self):
        # Split literal to avoid GitHub secret-scanning false positive on fixture.
        prefix = "xo" + "xb"
        s = f"{prefix}-1234567890-1234567890-abcdefghijklmnopqrstuvwx"
        assert redact(s) == MASK

    def test_slack_user(self):
        prefix = "xo" + "xp"
        assert redact(f"{prefix}-1234567890-abcdefghijklmnop") == MASK

    def test_stripe_live(self):
        assert redact("sk_live_" + "A" * 24) == MASK

    def test_stripe_test(self):
        assert redact("rk_test_" + "B" * 30) == MASK

    def test_google_api_key(self):
        assert redact("AIza" + "x" * 35) == MASK

    def test_google_oauth(self):
        assert redact("ya29." + "a" * 30) == MASK

    def test_jwt_bare(self):
        s = (
            "eyJhbGciOiJIUzI1NiJ9."
            "eyJzdWIiOiIxMjM0NTY3ODkw."
            "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        )
        assert MASK in redact(s)

    def test_github_pat_finegrained(self):
        s = "github_pat_" + "A" * 82
        assert redact(s) == MASK

    def test_db_url_with_password(self):
        s = "postgres://user:supersecret@db.example.com:5432/mydb"
        out = redact(s)
        assert MASK in out
        assert "supersecret" not in out
        assert "postgres://" in out
        assert "db.example.com" in out


class TestPlaceholderBypass:
    """C-1 regression: hint word in real secret value should NOT bypass."""

    def test_bearer_with_example_in_token(self):
        # Real-looking bearer token that happens to contain "example"
        s = "Authorization: Bearer realtoken12345example67890abcdefghi"
        assert MASK in redact(s)

    def test_api_key_with_dummy_in_value(self):
        s = "api_key=abc123def456dummy7890ghijklmn"
        assert MASK in redact(s)

    def test_password_with_placeholder_suffix(self):
        s = "password=RealSecret123_placeholder"
        assert MASK in redact(s)

    def test_single_star_does_not_bypass(self):
        # password pattern uses \S{8,} which accepts *
        s = "password=RealSecret*With1Star"
        assert MASK in redact(s)

    def test_triple_star_still_skipped(self):
        # Already-masked values with *** should be left alone
        s = "api_key=***********"
        assert redact(s) == s

    def test_redacted_marker_still_skipped(self):
        s = "api_key=[REDACTED]"
        assert redact(s) == s


class TestDepthAndCycle:
    def test_depth_limit(self):
        obj = "leaf"
        for _ in range(150):
            obj = {"k": obj}
        out = redact_obj(obj)
        # Walk down; eventually see the depth sentinel
        node = out
        for _ in range(120):
            if isinstance(node, str):
                break
            node = node["k"]
        assert node == "[REDACTED:depth]"

    def test_cycle_detected(self):
        a: dict = {}
        a["self"] = a
        out = redact_obj(a)
        assert out["self"] == "[REDACTED:cycle]"

    def test_cycle_in_list(self):
        lst: list = []
        lst.append(lst)
        out = redact_obj(lst)
        assert out[0] == "[REDACTED:cycle]"


class TestTupleAndEdgeTypes:
    def test_tuple_with_secret(self):
        obj = ("safe", "AKIAIOSFODNN7EXAMPLE", 42)
        out = redact_obj(obj)
        assert isinstance(out, tuple)
        assert out == ("safe", MASK, 42)

    def test_none_str_passthrough(self):
        assert redact_obj(None) is None
        assert redact_obj(3.14) == 3.14
        assert redact_obj(True) is True

    def test_redact_direct_non_str(self):
        # redact() accepts non-str: returns as-is (historic contract)
        assert redact("") == ""

    def test_local_heuristic_real_length(self):
        # Long enough for the \S{8,} regex; _local_ hint must skip.
        s = "POSTGRES_PASSWORD=hearable_local_password_abc123"
        assert redact(s) == s

    def test_task_sk_prefix_not_masked(self):
        # "task_sk-..." has "_" right before "sk-" → lookbehind rejects.
        s = "task_sk-" + "A" * 30 + " is not a secret"
        assert redact(s) == s

    def test_pem_gap_within_limit(self):
        # 80 chars of noise between BEGIN and payload → still masked
        s = "-----BEGIN RSA PRIVATE KEY-----" + "x" * 70 + "MIIJRAIBADANBgkqhkiG9w0BAQ"
        assert MASK in redact(s)

    def test_pem_gap_exceeds_limit(self):
        # 150 chars of non-base64 filler (spaces) → payload not reached
        s = "-----BEGIN RSA PRIVATE KEY-----" + " " * 150 + "MIIJRAIBADANBgkqhkiG9w0BAQ"
        assert MASK not in redact(s)

    def test_pgp_block_masked(self):
        s = (
            "-----BEGIN PGP PRIVATE KEY BLOCK-----\n"
            "lQOYBF4aX8kBCADOAAAAAAAAAAAAAAAAAAAAAAA="
        )
        assert MASK in redact(s)


class TestApiKeyNarrowing:
    """I-3: csrf_token / next_page_token should NOT match."""

    def test_csrf_token_not_masked(self):
        s = "csrf_token=abcdefghij1234567890ABCDEFGHI"
        assert redact(s) == s

    def test_next_page_token_not_masked(self):
        s = "next_page_token=pageABCDEFGHIJKLMNOPQR"
        assert redact(s) == s

    def test_access_token_masked(self):
        s = "access_token=abcdefghij1234567890ABCDEFGHIJ"
        assert MASK in redact(s)
