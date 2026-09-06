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
