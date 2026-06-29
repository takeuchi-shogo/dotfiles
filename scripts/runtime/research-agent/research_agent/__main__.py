"""CLI: python -m research_agent "研究質問" [--save] [--max-iter N]

ANTHROPIC_API_KEY は環境変数（local .env 等）で渡す。
"""

import argparse
import sys
import uuid

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver

from . import config
from .graph import build_graph

_RECURSION_LIMIT = 50  # research⇄tools + reflection loop の step 余裕


def _initial_state(question: str, max_iter: int, save: bool) -> dict:
    return {
        "messages": [HumanMessage(content=question)],
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="research_agent")
    parser.add_argument("question", help="研究質問")
    parser.add_argument(
        "--save", action="store_true", help="成功軌跡を経験として永続化（Tier 3）"
    )
    parser.add_argument("--max-iter", type=int, default=config.MAX_ITERATIONS)
    args = parser.parse_args(argv)

    config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with SqliteSaver.from_conn_string(str(config.CHECKPOINT_DB)) as cp:
        graph = build_graph(checkpointer=cp)
        cfg = {
            "configurable": {"thread_id": uuid.uuid4().hex},
            "recursion_limit": _RECURSION_LIMIT,
        }
        result = graph.invoke(
            _initial_state(args.question, args.max_iter, args.save), cfg
        )

    print(result.get("draft_report") or "(no report)")
    print(f"\n--- scores: {result.get('scores')}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
