"""Tests for review-phase-gate.py hook."""

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "policy"))

from importlib import import_module

gate = import_module("review-phase-gate")


def _assistant(text: str) -> str:
    return json.dumps(
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": text}],
            },
        }
    )


def _user(text: str) -> str:
    return json.dumps(
        {
            "type": "user",
            "message": {"role": "user", "content": [{"type": "text", "text": text}]},
        }
    )


def _tool_use(name: str) -> str:
    return json.dumps(
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [{"type": "tool_use", "name": name}],
            },
        }
    )


def _write_transcript(tmp_path: Path, lines: list[str]) -> str:
    p = tmp_path / "transcript.jsonl"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(p)


class TestDecide:
    def test_verdict_heading_allows(self, tmp_path):
        tp = _write_transcript(
            tmp_path,
            [_user("レビューして"), _assistant("## Verdict\n\nBLOCK: 1 件")],
        )
        decision, _ = gate._decide(tp)
        assert decision == "allow"

    def test_verdict_inline_allows(self, tmp_path):
        tp = _write_transcript(
            tmp_path,
            [_assistant("結果は verdict: NEEDS_FIX です")],
        )
        decision, _ = gate._decide(tp)
        assert decision == "allow"

    def test_user_approval_allows(self, tmp_path):
        # Verdict なし + user 承認フレーズあり
        tp = _write_transcript(
            tmp_path,
            [_assistant("指摘を 3 件挙げました"), _user("修正して")],
        )
        decision, _ = gate._decide(tp)
        assert decision == "allow"

    def test_no_verdict_no_approval_asks(self, tmp_path):
        tp = _write_transcript(
            tmp_path,
            [
                _user("レビューして"),
                _assistant("git diff を確認中です"),
                _tool_use("Bash"),
            ],
        )
        decision, _ = gate._decide(tp)
        assert decision == "ask"

    def test_approval_substring_not_overmatched(self, tmp_path):
        # 「修正は不要」は承認フレーズ (修正して) に一致しない
        tp = _write_transcript(
            tmp_path,
            [_assistant("探索中"), _user("修正は不要、調査を続けて")],
        )
        decision, _ = gate._decide(tp)
        assert decision == "ask"

    def test_english_negative_context_not_overmatched(self, tmp_path):
        # "git apply failed" / "not applicable" は承認 ("apply the fix") に一致しない
        tp = _write_transcript(
            tmp_path,
            [
                _assistant("探索中"),
                _user("git apply failed, that is not applicable here. 調査続行"),
            ],
        )
        decision, _ = gate._decide(tp)
        assert decision == "ask"

    def test_verdict_pushed_out_of_window_asks(self, tmp_path):
        # Verdict が直近 _TAIL_ENTRIES より前にあると window 外 → ask
        old_verdict = _assistant("## Verdict\nNEEDS_FIX")
        noise = [_user(f"探索中 {i}") for i in range(gate._TAIL_ENTRIES + 5)]
        tp = _write_transcript(tmp_path, [old_verdict, *noise])
        decision, _ = gate._decide(tp)
        assert decision == "ask"

    def test_verdict_inside_window_allows(self, tmp_path):
        # Verdict が window 内にあれば allow（境界の対）
        noise = [_user(f"探索中 {i}") for i in range(gate._TAIL_ENTRIES - 2)]
        tp = _write_transcript(tmp_path, [*noise, _assistant("## Verdict\nPASS")])
        decision, _ = gate._decide(tp)
        assert decision == "allow"

    def test_content_as_plain_string(self, tmp_path):
        # content が list でなく str 形式でも Verdict 検出が効く
        raw = json.dumps(
            {
                "type": "assistant",
                "message": {"role": "assistant", "content": "## Verdict\nPASS"},
            }
        )
        tp = _write_transcript(tmp_path, [raw])
        decision, _ = gate._decide(tp)
        assert decision == "allow"

    def test_malformed_message_entry_does_not_crash(self, tmp_path):
        # message が dict でない (構造破損) entry を混ぜても crash せず走査継続
        broken = json.dumps({"type": "assistant", "message": "oops"})
        tp = _write_transcript(tmp_path, [broken, _assistant("## Verdict\nPASS")])
        decision, _ = gate._decide(tp)
        assert decision == "allow"


class TestFailSafe:
    def test_missing_transcript_asks(self, tmp_path):
        decision, _ = gate._decide(str(tmp_path / "nope.jsonl"))
        assert decision == "ask"

    def test_corrupt_lines_skipped(self, tmp_path):
        tp = _write_transcript(
            tmp_path,
            ["{ this is not json", _assistant("## Verdict\nPASS")],
        )
        decision, _ = gate._decide(tp)
        assert decision == "allow"  # 破損行は skip して残りを走査

    def test_all_corrupt_asks_with_distinct_reason(self, tmp_path):
        # 全行破損 → ask、かつ「探索中」と区別できる reason を返す
        tp = _write_transcript(tmp_path, ["{ bad", "also } bad", "}{"])
        decision, reason = gate._decide(tp)
        assert decision == "ask"
        assert "corrupt" in reason


class TestMain:
    def test_main_allow_emits_permission(self, tmp_path, monkeypatch, capsys):
        tp = _write_transcript(tmp_path, [_assistant("## Verdict\nPASS")])
        monkeypatch.setattr("sys.stdin", _Stdin(json.dumps({"transcript_path": tp})))
        gate.main()
        out = json.loads(capsys.readouterr().out)
        assert out["hookSpecificOutput"]["permissionDecision"] == "allow"
        assert out["hookSpecificOutput"]["hookEventName"] == "PreToolUse"

    def test_main_no_transcript_path_asks(self, monkeypatch, capsys):
        monkeypatch.setattr("sys.stdin", _Stdin(json.dumps({})))
        gate.main()
        out = json.loads(capsys.readouterr().out)
        assert out["hookSpecificOutput"]["permissionDecision"] == "ask"

    def test_main_empty_stdin_asks(self, monkeypatch, capsys):
        monkeypatch.setattr("sys.stdin", _Stdin(""))
        gate.main()
        out = json.loads(capsys.readouterr().out)
        assert out["hookSpecificOutput"]["permissionDecision"] == "ask"


class _Stdin:
    """Minimal stdin stub for json.load."""

    def __init__(self, payload: str):
        self._payload = payload

    def read(self) -> str:
        return self._payload
