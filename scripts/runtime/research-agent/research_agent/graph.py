"""LangGraph 本体: retrieve_experience → research ⇄ tools → synthesize → reflect。

教科書 §25.3 Listing 25.3-25.4 を雛形に、経験RAG（retrieve_experience）と
Reflexion（reflect → reflection → research の retry loop）を加えた自己進化グラフ。
"""

import re

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from . import config, experience, reflexion
from .llm import make_llm
from .reflexion import text
from .state import ResearchState
from .tools import fetch, save_report, search

_GROUNDING_FLOOR = 0.6

_BASE_SYS = """あなたは arXiv 文献調査エージェント。研究質問に答える調査レポートを作る。
利用可能ツール: search（arXiv 検索）, fetch（arxiv.org の本文取得）。
進め方: search で関連論文を探し、fetch で重要なものを読み、十分集まったら調査を終える
（これ以上ツールを呼ばない）。引用は必ず tool 結果に実在する arxiv.org の URL に基づき、
捏造しない。最大 {max_iter} 反復。"""

_SYNTH = """ここまでの調査結果を統合し、研究質問に答える構造化レポートを書け。
構成: 導入 / 主要な発見（各点に arxiv.org の引用 URL を併記）/ 結論。
質問: {q}"""

_APPROACH_SYS = """この調査で有効だった手順（検索クエリ・主要ソース・統合方針）を、
次回似た質問で参照できるよう3-5行で要約せよ。日本語、箇条書き可。"""


def _build_system_prompt(state: ResearchState) -> str:
    parts = [_BASE_SYS.format(max_iter=state["max_iterations"])]
    exp = experience.format_for_prompt(state["experiences"])
    if exp:
        parts.append(exp)
    if state["reflections"]:
        parts.append(
            "これまでの reflection（同じ失敗を繰り返さないこと）:\n"
            + "\n".join("- " + r for r in state["reflections"])
        )
    return "\n\n".join(parts)


def retrieve_experience_node(state: ResearchState) -> dict:
    return {"experiences": experience.retrieve(state["research_question"])}


def research_node(state: ResearchState) -> dict:
    llm = make_llm(0.0).bind_tools([search, fetch])
    msgs = [SystemMessage(content=_build_system_prompt(state)), *state["messages"]]
    resp = llm.invoke(msgs)
    return {
        "messages": [resp],
        "iteration": state["iteration"] + 1,
        "status": "researching",
    }


def should_continue(state: ResearchState) -> str:
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools"  # tool_calls は必ず tools で応答（tool_use/result の整合）
    return "synthesize"


def after_tools(state: ResearchState) -> str:
    # iteration 上限は tools 後に判定（ぶら下がり tool_use を残さない）
    if state["iteration"] >= state["max_iterations"]:
        return "synthesize"
    return "research"


def synthesize_node(state: ResearchState) -> dict:
    llm = make_llm(0.0)
    prompt = _SYNTH.format(q=state["research_question"])
    resp = llm.invoke([*state["messages"], HumanMessage(content=prompt)])
    return {"draft_report": text(resp), "status": "synthesizing"}


def reflect_node(state: ResearchState) -> dict:
    scores = reflexion.evaluate(state["research_question"], state["draft_report"] or "")
    return {"scores": scores, "status": "reflecting"}


def after_reflect(state: ResearchState) -> str:
    s = state["scores"] or {}
    passed = (
        s.get("overall", 0) >= config.EXPERIENCE_SCORE_THRESHOLD
        and s.get("grounding", 0) >= _GROUNDING_FLOOR
    )
    if passed or state["iteration"] >= state["max_iterations"]:
        return "finalize"
    return "reflection"


def reflection_node(state: ResearchState) -> dict:
    r = reflexion.reflect(
        state["research_question"], state["draft_report"] or "", state["scores"] or {}
    )
    reflections = (state["reflections"] + [r])[-config.REFLECTION_WINDOW :]
    nudge = (
        f"前回のレポートは基準未達。reflection: {r}\nこれを踏まえ追加調査して改善せよ。"
    )
    return {"reflections": reflections, "messages": [HumanMessage(content=nudge)]}


def _extract_sources(messages: list) -> list[dict]:
    urls: set[str] = set()
    for m in messages:
        text = m.content if isinstance(m.content, str) else str(m.content)
        for u in re.findall(r"https?://arxiv\.org/\S+", text):
            urls.add(u.rstrip(".,)"))
    return [{"url": u, "grounding": "cited in trajectory"} for u in sorted(urls)]


def _summarize_approach(state: ResearchState) -> str:
    llm = make_llm(0.0)
    resp = llm.invoke(
        [
            SystemMessage(content=_APPROACH_SYS),
            HumanMessage(
                content=f"質問:\n{state['research_question']}\n\n"
                f"レポート:\n{(state['draft_report'] or '')[:1500]}"
            ),
        ]
    )
    return text(resp).strip()


def _maybe_persist(state: ResearchState) -> None:
    s = state["scores"] or {}
    ok = (
        s.get("overall", 0) >= config.EXPERIENCE_SCORE_THRESHOLD
        and s.get("grounding", 0) >= _GROUNDING_FLOOR
    )
    if not (state["save"] and ok):
        return
    traj = experience.SuccessTrajectory(
        question=state["research_question"],
        approach=_summarize_approach(state),
        score=s["overall"],
        model=config.MODEL,
        reflections=state["reflections"],
        sources=_extract_sources(state["messages"]),
    )
    experience.persist(traj)


def finalize_node(state: ResearchState) -> dict:
    report = state["draft_report"] or ""
    path = save_report.invoke({"title": state["research_question"], "content": report})
    _maybe_persist(state)  # Tier 3: --save かつ score 合格時のみ exemplar 昇格
    return {"status": "done", "messages": [AIMessage(content=f"レポート保存: {path}")]}


def build_graph(checkpointer=None):
    b = StateGraph(ResearchState)
    b.add_node("retrieve_experience", retrieve_experience_node)
    b.add_node("research", research_node)
    b.add_node("tools", ToolNode([search, fetch]))
    b.add_node("synthesize", synthesize_node)
    b.add_node("reflect", reflect_node)
    b.add_node("reflection", reflection_node)
    b.add_node("finalize", finalize_node)

    b.add_edge(START, "retrieve_experience")
    b.add_edge("retrieve_experience", "research")
    b.add_conditional_edges(
        "research",
        should_continue,
        {"tools": "tools", "synthesize": "synthesize"},
    )
    b.add_conditional_edges(
        "tools",
        after_tools,
        {"research": "research", "synthesize": "synthesize"},
    )
    b.add_edge("synthesize", "reflect")
    b.add_conditional_edges(
        "reflect",
        after_reflect,
        {"finalize": "finalize", "reflection": "reflection"},
    )
    b.add_edge("reflection", "research")
    b.add_edge("finalize", END)
    return b.compile(checkpointer=checkpointer)
