"""Tests for completion-gate.py fabricated completion-claim gate.

Regression for the 2026-06-28 incident: a session claimed it wrote and
ls-verified a research doc that was never written (no Write tool_use, file
absent on disk). The gate must block that, while leaving truthful claims and
backed writes alone.
"""

import json
import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "policy"))

gate = import_module("completion-gate")


def _assistant_text(text: str) -> str:
    return json.dumps(
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": text}],
            },
        }
    )


def _write_tool_use(file_path: str) -> str:
    return json.dumps(
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "name": "Write",
                        "input": {"file_path": file_path, "content": "x"},
                    }
                ],
            },
        }
    )


def _transcript(tmp_path: Path, *lines: str) -> Path:
    p = tmp_path / "transcript.jsonl"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def _data(tmp_path: Path, transcript: Path, sid: str = "s1") -> dict:
    gate._CLAIM_GATE_MARKER_DIR = str(tmp_path / "claim-gate")
    return {"transcript_path": str(transcript), "session_id": sid}


def test_blocks_fabricated_write_claim(tmp_path):
    missing = tmp_path / "2026-06-28-never-written.md"
    text = (
        f"ファイルはここに書いた:\n\n`{missing}`\n\n(`ls` で実在確認済み: 6747 バイト)"
    )
    tr = _transcript(tmp_path, _assistant_text("作業開始"), _assistant_text(text))
    result = gate._check_fabricated_claims(_data(tmp_path, tr))
    assert result is not None
    assert result.get("decision") == "block"
    assert str(missing) in result["reason"]


def test_allows_when_file_exists(tmp_path):
    real = tmp_path / "real.md"
    real.write_text("done", encoding="utf-8")
    text = f"分析を `{real}` に書き出した。"
    tr = _transcript(tmp_path, _assistant_text(text))
    assert gate._check_fabricated_claims(_data(tmp_path, tr)) is None


def test_allows_when_write_tool_was_called(tmp_path):
    target = tmp_path / "via-write.md"
    text = f"`{target}` を作成した。"
    tr = _transcript(
        tmp_path,
        _write_tool_use(str(target)),
        _assistant_text(text),
    )
    assert gate._check_fabricated_claims(_data(tmp_path, tr)) is None


def test_ignores_future_tense_intent(tmp_path):
    planned = tmp_path / "will-create.md"
    text = f"次に `{planned}` を作成します。"
    tr = _transcript(tmp_path, _assistant_text(text))
    assert gate._check_fabricated_claims(_data(tmp_path, tr)) is None


def test_ignores_path_without_claim_verb(tmp_path):
    missing = tmp_path / "mentioned.md"
    text = f"参考までに `{missing}` というパス命名が候補です。"
    tr = _transcript(tmp_path, _assistant_text(text))
    assert gate._check_fabricated_claims(_data(tmp_path, tr)) is None


def test_ignores_desiderative_and_conditional_verbs(tmp_path):
    planned = tmp_path / "suggestion.md"
    for phrase in ("作成したほうがいい", "作成したい", "作成したら便利"):
        text = f"このファイルも{phrase}: `{planned}`"
        tr = _transcript(tmp_path, _assistant_text(text))
        assert gate._check_fabricated_claims(_data(tmp_path, tr)) is None, phrase


def test_ignores_backticked_command(tmp_path):
    missing = tmp_path / "x.md"
    text = f"`{missing}` を作成した。確認は `stat {missing}` と `ls -la /tmp/x` で。"
    tr = _transcript(tmp_path, _assistant_text(text))
    result = gate._check_fabricated_claims(_data(tmp_path, tr))
    assert result is not None and result.get("decision") == "block"
    flagged_section = result["reason"].split("対応:")[0]
    assert str(missing) in flagged_section
    assert "stat " not in flagged_section
    assert "ls -la" not in flagged_section


def test_ignores_url(tmp_path):
    text = "ドキュメントは `https://example.com/guide/page.html` に作成した。"
    tr = _transcript(tmp_path, _assistant_text(text))
    assert gate._check_fabricated_claims(_data(tmp_path, tr)) is None


def test_second_block_allows_to_bound_loop(tmp_path):
    missing = tmp_path / "ghost.md"
    text = f"`{missing}` を作成した。"
    tr = _transcript(tmp_path, _assistant_text(text))
    data = _data(tmp_path, tr)
    first = gate._check_fabricated_claims(data)
    assert first.get("decision") == "block"
    assert gate._check_fabricated_claims(data) is None


def test_marker_write_failure_fails_open(tmp_path, monkeypatch):
    missing = tmp_path / "ghost.md"
    text = f"`{missing}` を作成した。"
    tr = _transcript(tmp_path, _assistant_text(text))
    data = _data(tmp_path, tr)

    def _boom(*_a, **_k):
        raise OSError("read-only")

    monkeypatch.setattr(gate.os, "makedirs", _boom)
    assert gate._check_fabricated_claims(data) is None
