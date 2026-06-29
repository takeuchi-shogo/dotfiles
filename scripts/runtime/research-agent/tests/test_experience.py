"""経験RAG（experience.py）の unit テスト: persist フォーマット / retrieve / degrade。

実 memory-vec を叩く「2回目に効く」フル統合は本番 index を汚すため、README の
手動検証手順で確認する（ここでは subprocess を mock してロジックを検証）。
"""

import json
from unittest.mock import MagicMock, patch

from research_agent import config, experience


def test_persist_writes_frontmatter(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "EXPERIENCE_DIR", tmp_path / "exp")
    monkeypatch.setattr(experience, "_reindex", lambda: None)
    traj = experience.SuccessTrajectory(
        question="RL とは",
        approach="search → read → synth",
        score=0.85,
        model="claude-sonnet-4-6",
        reflections=["公開日を確認する"],
        sources=[{"url": "http://arxiv.org/abs/1", "grounding": "abstract"}],
    )
    path = experience.persist(traj)
    text = path.read_text(encoding="utf-8")
    assert "question: RL とは" in text
    assert "score: 0.85" in text
    assert "model: claude-sonnet-4-6" in text
    assert "http://arxiv.org/abs/1" in text
    assert "## Approach (what worked)" in text
    assert path.parent == tmp_path / "exp"


def test_retrieve_parses_query_json(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "EXPERIENCE_DIR", tmp_path)
    exp_file = tmp_path / "e1.md"
    exp_file.write_text("過去の調査メモ", encoding="utf-8")
    query_stub = tmp_path / "query.ts"
    query_stub.write_text("// stub", encoding="utf-8")
    monkeypatch.setattr(config, "MEMORY_VEC_QUERY", query_stub)
    fake = MagicMock(
        returncode=0,
        stdout=json.dumps(
            [
                {
                    "path": str(exp_file),
                    "name": "e1.md",
                    "distance": 0.5,
                    "source": "research-experience",
                }
            ]
        ),
    )
    with patch("research_agent.experience.subprocess.run", return_value=fake):
        out = experience.retrieve("調査")
    assert out == ["過去の調査メモ"]


def test_retrieve_rejects_path_outside_experience_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "EXPERIENCE_DIR", tmp_path / "exp")
    (tmp_path / "exp").mkdir()
    outside = tmp_path / "secret.md"
    outside.write_text("/etc/passwd 相当", encoding="utf-8")
    query_stub = tmp_path / "query.ts"
    query_stub.write_text("// stub", encoding="utf-8")
    monkeypatch.setattr(config, "MEMORY_VEC_QUERY", query_stub)
    fake = MagicMock(returncode=0, stdout=json.dumps([{"path": str(outside)}]))
    with patch("research_agent.experience.subprocess.run", return_value=fake):
        assert experience.retrieve("調査") == []


def test_retrieve_degrades_when_query_absent(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "MEMORY_VEC_QUERY", tmp_path / "absent.ts")
    assert experience.retrieve("x") == []


def test_format_for_prompt():
    assert experience.format_for_prompt([]) == ""
    out = experience.format_for_prompt(["手順A", "手順B"])
    assert "手順A" in out
    assert "手順B" in out
