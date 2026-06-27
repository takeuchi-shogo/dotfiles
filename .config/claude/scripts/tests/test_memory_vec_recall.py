"""Gate logic tests for memory-vec-recall-hook.

The hook runs on every prompt, so the only non-trivial decision — whether a
prompt is a judgment/design/research turn worth a Vault query — must hold.
Coding/routine prompts must NOT fire (else every turn pays a subprocess and
pollutes context).
"""

import importlib.util
from pathlib import Path

_HOOK = Path(__file__).resolve().parents[1] / "runtime" / "memory-vec-recall-hook.py"
_spec = importlib.util.spec_from_file_location("recall_hook", _HOOK)
recall_hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(recall_hook)
is_intent_prompt = recall_hook.is_intent_prompt


def test_judgment_prompts_fire():
    for p in [
        "この obsidian repo を導入すべきか",
        "A と B どっちが良い",
        "memory retrieval をどう設計する",
        "should I adopt this approach",
        "compare these two designs",
        "trade-off を整理して",
        "この技術選定についてセカンドオピニオンが欲しい",
    ]:
        assert is_intent_prompt(p), p


def test_routine_prompts_do_not_fire():
    for p in [
        "fix the typo on line 42",
        "この関数の変数名をリネームして",
        "run the tests",
        "git status を見せて",
        "add a log line here",
        "import を整理して消す",
    ]:
        assert not is_intent_prompt(p), p


def test_empty_is_false():
    assert not is_intent_prompt("")
    assert not is_intent_prompt("   ")


def test_english_boundary_guard():
    # "design" must fire, but it should be a real word, not a substring hit
    # inside an unrelated token.
    assert is_intent_prompt("review the design doc")
    assert not is_intent_prompt("update the redesignation field")
