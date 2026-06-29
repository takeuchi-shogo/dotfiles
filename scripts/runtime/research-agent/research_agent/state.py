"""LangGraph を流れる State スキーマ。"""

from typing import Annotated, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class ResearchState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]  # reducer 必須（履歴消失防止）
    research_question: str
    iteration: int
    max_iterations: int
    experiences: list[str]  # 起動時に1回だけ注入する few-shot（経験RAG）
    reflections: list[str]  # episodic、直近 REFLECTION_WINDOW 件（Reflexion）
    draft_report: str | None
    scores: dict | None  # reflect の多軸自己評価
    status: Literal["researching", "synthesizing", "reflecting", "done", "error"]
    save: bool  # --save（Tier 3: 経験の永続化を許可するか）
