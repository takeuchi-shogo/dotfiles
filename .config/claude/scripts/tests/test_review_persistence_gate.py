"""review-persistence-gate: /review 後に Run Metrics 未記録なら Stop を block する。

前提: transcript は assistant の Skill(review) tool_use (timestamp は Z 表記)、
metrics は +00:00 表記。AUTOEVOLVE_DATA_DIR は tmp。
"""

import json
import os
import subprocess
import sys
from pathlib import Path

GATE = Path(__file__).resolve().parent.parent / "policy" / "review-persistence-gate.py"
T_REVIEW = "2026-10-17T10:00:00.000Z"


def _skill_line(skill, ts):
    return json.dumps(
        {
            "type": "assistant",
            "timestamp": ts,
            "message": {
                "content": [
                    {"type": "tool_use", "name": "Skill", "input": {"skill": skill}}
                ]
            },
        }
    )


def _run(tmp_path, transcript_lines, metrics_ts=None, active=False, raw=None):
    tr = tmp_path / "t.jsonl"
    tr.write_text(raw if raw is not None else "\n".join(transcript_lines) + "\n")
    if metrics_ts:
        d = tmp_path / "data" / "learnings"
        d.mkdir(parents=True)
        (d / "review-metrics.jsonl").write_text(
            "".join(
                json.dumps({"timestamp": t, "run_id": "rv-1"}) + "\n"
                for t in metrics_ts
            )
        )
    payload = {
        "transcript_path": str(tr),
        "stop_hook_active": active,
        "session_id": "s1",
    }
    return subprocess.run(
        [sys.executable, str(GATE)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "AUTOEVOLVE_DATA_DIR": str(tmp_path / "data"),
            "CLAUDE_SESSION_STATE_DIR": str(tmp_path / "state"),
        },
    )


def test_blocks_only_once_per_review_invocation(tmp_path):
    """前提: review 後の metrics が無いまま、同じ /review 起動について 2 回 Stop する。
    検証: 1 回目は block、2 回目は (stop_hook_active でなくても) 通す。
    """
    lines = [_skill_line("review", T_REVIEW)]
    first = _run(tmp_path, lines)
    second = _run(tmp_path, lines)
    assert json.loads(first.stdout)["decision"] == "block"
    assert second.returncode == 0 and second.stdout == ""


def test_blocks_when_review_ran_without_later_metrics(tmp_path):
    """検証: review 後の metrics が無い (古い記録のみ) なら decision=block。"""
    r = _run(tmp_path, [_skill_line("review", T_REVIEW)], ["2026-10-17T09:00:00+00:00"])
    assert json.loads(r.stdout)["decision"] == "block"


def test_blocks_when_metrics_file_absent(tmp_path):
    """検証: metrics ファイル自体が無くても block。"""
    r = _run(tmp_path, [_skill_line("review", T_REVIEW)])
    assert json.loads(r.stdout)["decision"] == "block"


def test_allows_when_later_metrics_exist(tmp_path):
    """検証: review 後 (+00:00 表記) の metrics があれば何も出力しない。"""
    r = _run(tmp_path, [_skill_line("review", T_REVIEW)], ["2026-10-17T10:05:00+00:00"])
    assert r.returncode == 0 and r.stdout == ""


def test_allows_when_stop_hook_active(tmp_path):
    """検証: stop_hook_active=true は loop 防止のため無条件 allow。"""
    r = _run(tmp_path, [_skill_line("review", T_REVIEW)], active=True)
    assert r.returncode == 0 and r.stdout == ""


def test_allows_when_no_review_invocation(tmp_path):
    """検証: review 以外の Skill のみなら allow。"""
    r = _run(tmp_path, [_skill_line("commit", T_REVIEW)])
    assert r.returncode == 0 and r.stdout == ""


def test_allows_on_corrupt_transcript(tmp_path):
    """検証: 壊れた transcript は allow (stdout 空、exit 0)。"""
    r = _run(tmp_path, [], raw="not json\n{broken\n")
    assert r.returncode == 0 and r.stdout == ""


def test_allows_when_transcript_missing(tmp_path):
    """検証: transcript_path が存在しなくても allow し stderr に 1 行残す。"""
    r = subprocess.run(
        [sys.executable, str(GATE)],
        input=json.dumps({"transcript_path": str(tmp_path / "nope")}),
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0 and r.stdout == "" and r.stderr.strip()


def test_separate_invocations_in_the_same_second_each_block(tmp_path):
    """前提: 同じ秒の別時刻 (.001 と .999) に /review を起動した 2 つの transcript。
    検証: マーカーを共有せず、後者の /review も 1 回 block される。
    """
    first = _run(tmp_path, [_skill_line("review", "2026-10-17T10:00:00.001Z")])
    second = _run(tmp_path, [_skill_line("review", "2026-10-17T10:00:00.999Z")])
    assert json.loads(first.stdout)["decision"] == "block"
    assert json.loads(second.stdout)["decision"] == "block"
