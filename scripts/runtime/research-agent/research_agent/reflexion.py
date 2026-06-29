"""Reflexion（§12.5.2）: レポートの多軸自己評価 + 失敗時の自然言語 reflection 生成。

重み更新なし。Evaluator（LLM-as-judge）と Self-Reflection Generator を提供し、
graph 側の reflect ノードが retry loop（research へ戻す）を駆動する。
"""

import json
import re

from langchain_core.messages import HumanMessage, SystemMessage

from .llm import make_llm

_JUDGE_SYS = """あなたは調査レポートの厳格な評価者。次の4軸を各 0.0-1.0 で採点し、
JSON オブジェクトだけを返す（前後に説明文を付けない）:
- quality: 明快さ・深さ・構成
- grounding: 主張が引用（実在ソース）に裏付けられているか（捏造引用は低評価）
- novelty: 単なる要約を超えた洞察があるか
- format: 必要な要素（導入・本論・結論・引用）が揃っているか
例: {"quality": 0.8, "grounding": 0.9, "novelty": 0.6, "format": 0.7}"""

_REFLECT_SYS = """あなたは自分の調査を振り返るエージェント。今回のレポートが
評価基準に届かなかった原因を1-2文で具体的に述べ、次の試行で取るべき改善を
1文で示す。日本語で、箇条書きにせず短く。"""


def _text(resp) -> str:
    """AIMessage.content を文字列へ（Anthropic は str か block list を返す）。"""
    c = resp.content
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return " ".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in c)
    return str(c)


def _clamp(v) -> float:
    try:
        return max(0.0, min(1.0, float(v)))
    except (TypeError, ValueError):
        return 0.0


def _extract_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return {}
    try:
        obj = json.loads(m.group(0))
    except (json.JSONDecodeError, ValueError):
        return {}
    return obj if isinstance(obj, dict) else {}


def evaluate(question: str, report: str) -> dict:
    """4軸スコア + overall（grounding 最重視の加重平均）を返す。"""
    llm = make_llm(temperature=0.0)
    resp = llm.invoke(
        [
            SystemMessage(content=_JUDGE_SYS),
            HumanMessage(content=f"質問:\n{question}\n\nレポート:\n{report}"),
        ]
    )
    raw = _extract_json(_text(resp))
    s = {k: _clamp(raw.get(k)) for k in ("quality", "grounding", "novelty", "format")}
    s["overall"] = round(
        0.40 * s["grounding"]
        + 0.30 * s["quality"]
        + 0.15 * s["novelty"]
        + 0.15 * s["format"],
        4,
    )
    return s


def reflect(question: str, report: str, scores: dict) -> str:
    """低評価の原因と次の改善を自然言語 reflection として返す。"""
    llm = make_llm(temperature=0.3)
    resp = llm.invoke(
        [
            SystemMessage(content=_REFLECT_SYS),
            HumanMessage(
                content=(
                    f"質問:\n{question}\n\nスコア:{scores}\n\n"
                    f"レポート（抜粋）:\n{report[:1500]}"
                )
            ),
        ]
    )
    return _text(resp).strip()
