"""graph.py の integration テスト: LLM/HTTP を mock して E2E ループを検証。"""

from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage

from research_agent import config
from research_agent.graph import build_graph

ARXIV_XML = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Relevant Paper</title>
    <id>http://arxiv.org/abs/1234.5678</id>
    <summary>An abstract.</summary>
  </entry>
</feed>"""


class FakeLLM:
    """make_llm の戻りを差し替える。bind_tools は self を返し、invoke で順に応答。"""

    def __init__(self, responses):
        self._responses = list(responses)

    def bind_tools(self, _tools):
        return self

    def invoke(self, _messages):
        return self._responses.pop(0)


def _tool_call(name, args, call_id):
    return AIMessage(
        content="", tool_calls=[{"name": name, "args": args, "id": call_id}]
    )


def _init(question, save=False, max_iter=6):
    return {
        "messages": [("user", question)],
        "research_question": question,
        "iteration": 0,
        "max_iterations": max_iter,
        "experiences": [],
        "reflections": [],
        "draft_report": None,
        "scores": None,
        "status": "researching",
        "save": save,
    }


def _arxiv_resp():
    resp = MagicMock(text=ARXIV_XML)
    resp.raise_for_status = MagicMock()
    return resp


def test_e2e_research_to_done(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(
        config, "MEMORY_VEC_QUERY", tmp_path / "absent.ts"
    )  # 経験RAG skip

    graph_llm = FakeLLM(
        [
            _tool_call("search", {"query": "rl"}, "c1"),  # research #1
            AIMessage(content="調査完了"),  # research #2（tool なし）
            AIMessage(
                content="# レポート\n発見: http://arxiv.org/abs/1234.5678\n結論。"
            ),
        ]
    )
    judge_llm = FakeLLM(
        [
            AIMessage(
                content='{"quality":0.8,"grounding":0.9,"novelty":0.7,"format":0.8}'
            ),
        ]
    )

    with (
        patch("research_agent.graph.make_llm", return_value=graph_llm),
        patch("research_agent.reflexion.make_llm", return_value=judge_llm),
        patch("research_agent.tools.requests.get", return_value=_arxiv_resp()),
    ):
        result = build_graph().invoke(_init("RL の調査"), {"recursion_limit": 50})

    assert result["status"] == "done"
    assert result["scores"]["overall"] >= config.EXPERIENCE_SCORE_THRESHOLD
    assert "arxiv.org" in result["draft_report"]


def test_max_iterations_enforced(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(config, "MEMORY_VEC_QUERY", tmp_path / "absent.ts")

    # research が毎回 search を呼んでも max_iter で打ち切られ synthesize に進む
    graph_llm = FakeLLM(
        [
            _tool_call("search", {"query": "x"}, "c1"),  # iter 1
            _tool_call("search", {"query": "x"}, "c2"),  # iter 2（= max）
            AIMessage(content="# 打ち切りレポート http://arxiv.org/abs/1234.5678"),
        ]
    )
    judge_llm = FakeLLM(
        [
            AIMessage(
                content='{"quality":0.8,"grounding":0.9,"novelty":0.7,"format":0.8}'
            ),
        ]
    )

    with (
        patch("research_agent.graph.make_llm", return_value=graph_llm),
        patch("research_agent.reflexion.make_llm", return_value=judge_llm),
        patch("research_agent.tools.requests.get", return_value=_arxiv_resp()),
    ):
        result = build_graph().invoke(_init("x", max_iter=2), {"recursion_limit": 50})

    assert result["status"] == "done"
    assert result["iteration"] <= 2
