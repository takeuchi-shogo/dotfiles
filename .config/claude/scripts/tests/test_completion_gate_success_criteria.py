import importlib.util
from pathlib import Path

SPEC = Path(__file__).resolve().parent.parent / "policy" / "completion-gate.py"

# PLANS.md Required Sections の形式
SCALAR = """---
success_criteria: "task validate-configs が pass する"
artifacts: "a.py"
---

# Plan
"""

# resume-anchor-contract.md の形式
YAML_LIST = """---
success_criteria:
  - "broken link が解消される"
  - "gate が frontmatter を読める"
status: active
---

# Plan
"""

NO_KEY = """---
title: plan
---

# Plan
"""


def _load():
    spec = importlib.util.spec_from_file_location("completion_gate", SPEC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _extract(text):
    return _load()._extract_success_criteria(text.splitlines(keepends=True))


def test_scalar_form_is_read():
    assert _extract(SCALAR) == '"task validate-configs が pass する"'


def test_yaml_list_form_is_read():
    """Regression: the list form used to yield '' and silently fall back to
    COMPLETION_PROMISE, discarding the plan's own criteria."""
    got = _extract(YAML_LIST)
    assert got is not None and got != ""
    assert "broken link が解消される" in got
    assert "gate が frontmatter を読める" in got


def test_missing_key_returns_none():
    assert _extract(NO_KEY) is None


LIST_WITH_COMMENTS = """---
success_criteria:
  # 最低限これが通れば完了
  - "a が通る"

  - "b が通る"
status: active
---
"""

EMPTY_FLOW_LIST = """---
success_criteria: []
---
"""

NESTED_KEY_ONLY = """---
plan:
  success_criteria: "これは別マッピングの値"
---
"""

FOLDED_SCALAR = """---
success_criteria: >
  a が通り、
  b も通る
status: active
---
"""

LITERAL_SCALAR = """---
success_criteria: |
  a が通る
  b が通る
---
"""


def test_comments_and_blank_lines_inside_list_are_skipped():
    got = _extract(LIST_WITH_COMMENTS)
    assert got == "a が通る / b が通る"


def test_explicit_empty_collection_is_none():
    assert _extract(EMPTY_FLOW_LIST) is None


def test_indented_key_under_another_mapping_is_ignored():
    assert _extract(NESTED_KEY_ONLY) is None


def test_folded_block_scalar_is_joined():
    assert _extract(FOLDED_SCALAR) == "a が通り、 b も通る"


def test_literal_block_scalar_is_joined():
    assert _extract(LITERAL_SCALAR) == "a が通る b が通る"


def _fmt(plan_name, criteria, fallback):
    return _load()._format_criteria_lines(plan_name, criteria, fallback)


def test_plan_criteria_is_labelled_as_coming_from_frontmatter():
    """
    前提: plan frontmatter に success_criteria が書かれている。
    事前: 汎用 fallback (COMPLETION_PROMISE) も同時に設定されている。
    検証: plan 側が優先され、出所が "plan frontmatter" と明示されること。
          fallback 文字列は出力に現れないこと。
    """
    out = _fmt("p.md", "task validate-configs が pass する", "generic fallback")
    assert "成功基準 (plan frontmatter): task validate-configs が pass する" in out[0]
    assert not any("generic fallback" in line for line in out)


def test_fallback_is_labelled_and_warns_which_plan_lacks_criteria():
    """
    前提: plan に success_criteria が無い (None)。
    事前: 汎用 fallback は設定済み。
    検証: fallback を使ったことを明示し、criteria を欠いた plan 名を警告に含めること。
          無言で plan 由来のように見せないこと (暗黙フォールバック禁止)。
    """
    out = _fmt("orphan-plan.md", None, "generic fallback")
    joined = "\n".join(out)
    assert "汎用 fallback" in joined
    assert "orphan-plan.md" in joined
    assert "⚠" in joined
    assert "成功基準 (plan frontmatter)" not in joined


def test_missing_criteria_and_missing_fallback_is_still_reported():
    """
    前提: plan に success_criteria が無く、汎用 fallback も未設定 (どちらも None)。
    事前: Ralph Loop は未完了ステップを検出して回っている。
    検証: 黙って空を返さず、完了条件が未定義である旨を警告として返すこと。
    """
    out = _fmt("bare.md", None, None)
    joined = "\n".join(out)
    assert "bare.md" in joined
    assert "未定義" in joined
    assert out != []


def test_extracted_criteria_flows_into_the_rendered_block():
    """
    前提: YAML list 形式の success_criteria を持つ plan テキスト。
    事前: _extract_success_criteria がそれを結合して返す。
    検証: 抽出結果がそのまま描画ブロックに載り、fallback 経路に落ちないこと
          (抽出器と描画器の接続を回帰検出する)。
    """
    criteria = _extract(YAML_LIST)
    out = _fmt("p.md", criteria, "generic fallback")
    assert "broken link が解消される" in out[0]
    assert "⚠" not in "\n".join(out)
