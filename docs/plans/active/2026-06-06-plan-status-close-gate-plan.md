---
topic: plan-status-close-gate
status: active
scope: L
owner: takeuchi-shogo
created: 2026-06-06
artifacts: "scripts/lifecycle/plan-close-detector.py, scripts/tests/test_plan_close_detector.py, scripts/runtime/nightly/run-plan-close-scan.sh"
asserts: "plan-close-tests"
success_criteria: "nightly が docs/plans/active/ を走査し『lifecycle=active だが完了』候補を Tier 別に検出して docs/plan-close/ にレポート出力。Tier1(allowlisted assert 成功 + clean tree / 誤配置) のみ自動 PR 提案を生成 (直接 move/commit はしない)。calibration ledger で人間裁定の agree 率を記録し、agree≥0.9 + 安全層充足を auto-apply の開放条件とする"
---

# Plan Status Close-Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `status: active` のまま放置され「死蔵」と誤判定される完了済み plan を機械検出し、確信度 Tier 別に報告／自動クローズ提案する仕組みを作る。

**Architecture:** 既存 `doc-status-audit.py` の `parse_frontmatter` を再利用した独立検出器 `plan-close-detector.py` を新設。完了シグナルを Tier に分類 — **Tier1 = allowlisted assert 成功 + clean tree、または誤配置** (→自動 PR 提案), **Tier2 = 成果物パス存在のみ / checkbox 全 done** (→報告のみ), **Tier3 = stale のみ** (→報告のみ)。nightly で dry-run scan を回し、`docs/plan-close/candidates.jsonl` を pending source of truth とする。人間が Tier1 PR を裁定した**後**に `calibration-verdict-logger.py` で agree/disagree を記録。agree 率が閾値を超え、かつ安全層 (clean tree / open PR guard / allowlist / fail-loud) を満たすまで auto-apply は開放しない (learned 昇格ループの Wave gating と同型)。

**Tech Stack:** Python 3.13 (標準ライブラリのみ), bash, launchd, pytest。

---

## 設計上の教訓 (本セッション 2026-06-06 で実証)

1. **checkbox は完了の証拠にならない** — nix-migration は checkbox 0 のまま実装完了・稼働中だった。→ checkbox は Tier2 (報告のみ) の補助シグナルに格下げ。
2. **「書いた」≠「配線した」で死蔵する** — `run-learned-promote.sh` はスクリプト実体があるのに launchd 未登録で一度も実行されなかった。→ Task 5 で `launchd-install.sh` の `TASKS` 配列への登録を**必須ステップ**にし、登録漏れを検証する。
3. **自動化は calibration 前に開放しない** — learned 昇格ループは無人 PR 化 (Wave3) を calibration (mechanical 0/139) の後に YAGNI 撤退した。→ auto-apply は Task 6 で実装するが、calibration で agree≥0.9 を実測するまでデフォルト無効。
4. **「存在」≠「完了」の罠は再帰する (Codex Gate #1 で露呈)** — 初版は「成果物パス実在」を Tier1 の完了証拠に据えたが、これは教訓1と同じ罠 (途中実装でもファイルは存在する =「作成済み」であって「完了・配線・検証済み」ではない)。→ **Tier1 は allowlisted assert の成功を必須**とし、パス存在のみは Tier2 (`ARTIFACTS_PRESENT`, 報告のみ) に降格。
5. **plan 本文をコード実行面にしない (Codex Gate #4)** — 初版の `verification: "! 任意コマンド"` (`shell=True`) は、LLM/外部記事由来の文言が混ざる plan frontmatter の任意コマンドを nightly が実行する prompt injection 経路だった。→ `! command` 形式を廃止し、detector 内の固定 allowlist map から `shell=False` で起動する `asserts:` enum に置換。

> **Codex Spec/Plan Gate (2026-06-06, Verdict: REVISE) 反映済み**: 上記 4-5 に加え、(#2) quote stripping 仕様化 / (#3) `status` → `lifecycle:` 名前空間分離で doc-status-audit 語彙衝突を回避 / (#5) calibration-verdict-logger は pending queue でなく裁定記録器として正しく使用 / (#6) launchd TASKS 書式修正 / auto-apply に `run-learned-promote.sh` 安全層を縮小移植。Codex 出力: `/tmp/cmux-results/w-1780728643-codex.md`。

## 撤退条件 (reversible-decisions)

- **auto-apply 開放の撤退**: nightly 30 日分の calibration で Tier1 の human-agree 率 < 0.9 なら、Tier1 を「報告のみ」に降格し auto-PR を恒久無効化する (`references/reversible-decisions.md` に記録)。
- **検出器ごと撤退**: 3 ヶ月運用して close 候補の検出が月 0 件、かつ既存 active plan の誤配置も解消済みなら、本検出器を退役し `docs/decommission-log.md` に記録する (Build to Delete)。

## File Structure

- `scripts/lifecycle/plan-close-detector.py` (Create) — 検出器本体。`docs/plans/active/*.md` を走査し Tier 分類した候補を JSONL + md で出力。`--apply-tier1` で Tier1 を安全層付き PR 提案として生成 (直接 move/commit はしない)。
- `scripts/tests/test_plan_close_detector.py` (Create) — pytest。Tier 分類・asserts/artifacts 照合・誤配置検出・dry-run 不変性をカバー。
- `scripts/runtime/nightly/run-plan-close-scan.sh` (Create) — nightly runner。検出器を dry-run で起動しレポート生成、calibration ledger に候補を emit。
- `scripts/runtime/nightly/launchd-install.sh` (Modify) — `TASKS` 配列に `plan-close-scan` を追加。
- `PLANS.md` (Modify) — frontmatter 規約に `lifecycle:`/`artifacts:`/`asserts:` 欄を追加 (予防レーン)。
- `docs/plan-close/` (Create dir) — レポート出力先 (`<DATE>-close-report.md`, `candidates.jsonl`)。`.gitkeep` + `README.md`。
- `docs/plans/active/2026-06-06-plan-status-close-gate-plan.md` (この plan 自身, dogfood: `lifecycle:`/`artifacts:`/`asserts:` 欄を保有)。

---

### Task 0: 予防レーン — PLANS.md / doc-status-schema.md に `artifacts:`/`asserts:`/`lifecycle:` 欄を規約化

**Files:**
- Modify: `PLANS.md` (frontmatter テンプレート節)
- Modify: `.config/claude/references/doc-status-schema.md` (status 語彙衝突の回避を明記)

**設計 (Codex Gate #1/#3/#4 反映):**
- 完了証拠は2分割する。`artifacts:` (成果物パス = 弱い証拠 → Tier2) と `asserts:` (allowlist enum = 強い証拠 → Tier1)。
- `status:` は doc-status-audit.py が `active/reference/archive` で使う語彙と衝突するため、plan の生存状態は **`lifecycle:`** で持つ (`active/completed/deferred/paused/pending`)。既存 plan の `status:` は移行期間中 detector が後方互換で読む (Task 3 で両対応)。
- 任意 shell コマンド形式は**置かない**。`asserts:` は detector 内の固定 allowlist map のキーのみ。

- [ ] **Step 1: PLANS.md の frontmatter テンプレートに規約を追記**

`PLANS.md` のテンプレート節に以下を追加:

```markdown
### frontmatter 完了判定欄 (推奨)

plan-close-detector が走査して close 候補を機械判定するための欄。simple `key: value` parser 互換 (1行・カンマ区切り、detector が outer quote を strip する)。

- `lifecycle: active` — plan の生存状態 (active/completed/deferred/paused/pending)。`status:` とは別名前空間 (status は doc-status-audit の active/reference/archive 用)。
- `artifacts: "path/a.py, path/b.sh"` — 成果物パス列挙。全実在で **Tier2 (ARTIFACTS_PRESENT, 報告のみ)**。「作成済み」の弱い証拠であり、これだけでは自動クローズしない。
- `asserts: "validate-configs, plan-close-tests"` — detector の固定 allowlist (`ASSERTS` map) のキー列挙。全 assert が exit 0 かつ working tree clean で **Tier1 (VERIFIED_DONE, 自動 PR 提案)**。任意コマンドは書けない (allowlist 外のキーは無視)。

何も書かない plan は stale + checkbox の Tier2/3 報告のみ対象。
```

- [ ] **Step 2: doc-status-schema.md に語彙分離を明記 (Codex Gate #3)**

`.config/claude/references/doc-status-schema.md` に追記: 「`docs/plans/` の plan は `lifecycle:` (active/completed/deferred/paused/pending) を生存状態に使う。doc-status-audit が扱う `status:` (active/reference/archive) とは別概念で、両ツールは disjoint な責務 (doc-status-audit=reference docs の status 推定 / plan-close-detector=plans の lifecycle クローズ判定)。」

- [ ] **Step 3: コミット**

```bash
git add PLANS.md .config/claude/references/doc-status-schema.md
git commit -m "📝 docs(plans): 完了判定欄 (lifecycle/artifacts/asserts) を規約化 + status語彙分離"
```

---

### Task 1: 検出器の骨格 — frontmatter + 完了シグナル抽出

**Files:**
- Create: `scripts/lifecycle/plan-close-detector.py`
- Test: `scripts/tests/test_plan_close_detector.py`

- [ ] **Step 1: 失敗するテストを書く (シグナル抽出)**

`scripts/tests/test_plan_close_detector.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lifecycle"))
import importlib

pcd = importlib.import_module("plan-close-detector")


def _write(tmp_path, name, body):
    f = tmp_path / name
    f.write_text(body, encoding="utf-8")
    return f


def test_extract_signals_reads_lifecycle_artifacts_asserts(tmp_path):
    f = _write(
        tmp_path,
        "p.md",
        "---\nlifecycle: active\nartifacts: \"a.py, b.sh\"\nasserts: \"plan-close-tests\"\n---\n\n- [x] done\n- [ ] todo\n",
    )
    sig = pcd.extract_signals(f)
    assert sig.lifecycle == "active"
    assert sig.artifacts == '"a.py, b.sh"'
    assert sig.asserts == '"plan-close-tests"'
    assert sig.checkboxes_total == 2
    assert sig.checkboxes_done == 1


def test_extract_signals_falls_back_to_status(tmp_path):
    # 既存 plan は status: のみ。lifecycle 欠落時は status を後方互換で読む。
    f = _write(tmp_path, "old.md", "---\nstatus: completed\n---\n# old\n")
    assert pcd.extract_signals(f).lifecycle == "completed"
```

- [ ] **Step 2: テストが失敗することを確認**

Run: `python3 -m pytest scripts/tests/test_plan_close_detector.py::test_extract_signals_reads_lifecycle_artifacts_asserts -v`
Expected: FAIL (`ModuleNotFoundError` or `AttributeError: extract_signals`)

- [ ] **Step 3: 最小実装 — extract_signals**

`scripts/lifecycle/plan-close-detector.py`:

```python
#!/usr/bin/env python3
"""plan-close-detector — detect active plans that are actually complete.

Scans docs/plans/active/*.md, classifies close candidates into confidence
tiers. Tier1 (allowlisted asserts pass + clean tree / misplaced) is auto-PR eligible;
Tier2/3 are report-only. Default mode is dry-run (no file moves).
"""
from __future__ import annotations

import importlib.util
import re
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_DIR = REPO_ROOT / "docs" / "plans" / "active"

# Reuse the frontmatter parser from doc-status-audit.py (DRY — no third parser).
_audit_path = Path(__file__).resolve().parent / "doc-status-audit.py"
_spec = importlib.util.spec_from_file_location("doc_status_audit", _audit_path)
_audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_audit)
parse_frontmatter = _audit.parse_frontmatter

_CHECKBOX_DONE = re.compile(r"^\s*[-*] \[x\]", re.IGNORECASE | re.MULTILINE)
_CHECKBOX_TODO = re.compile(r"^\s*[-*] \[ \]", re.MULTILINE)


@dataclass
class Signals:
    path: Path
    lifecycle: str | None  # frontmatter lifecycle:、無ければ status: で後方互換
    artifacts: str | None  # 成果物パス列挙 (弱い証拠)
    asserts: str | None    # allowlist enum キー列挙 (強い証拠)
    checkboxes_total: int
    checkboxes_done: int


def extract_signals(path: Path) -> Signals:
    text = path.read_text(encoding="utf-8", errors="ignore")
    fields, _ = parse_frontmatter(text)
    fields = fields or {}
    done = len(_CHECKBOX_DONE.findall(text))
    todo = len(_CHECKBOX_TODO.findall(text))
    return Signals(
        path=path,
        lifecycle=fields.get("lifecycle") or fields.get("status"),
        artifacts=fields.get("artifacts"),
        asserts=fields.get("asserts"),
        checkboxes_total=done + todo,
        checkboxes_done=done,
    )
```

- [ ] **Step 4: テストが通ることを確認**

Run: `python3 -m pytest scripts/tests/test_plan_close_detector.py::test_extract_signals_reads_lifecycle_artifacts_asserts -v`
Expected: PASS

- [ ] **Step 5: コミット**

```bash
git add scripts/lifecycle/plan-close-detector.py scripts/tests/test_plan_close_detector.py
git commit -m "✨ feat(lifecycle): plan-close-detector シグナル抽出 (frontmatter+checkbox)"
```

---

### Task 2: 照合ロジック — `artifacts_present` (弱) + `asserts_satisfied` (強・allowlist)

**Files:**
- Modify: `scripts/lifecycle/plan-close-detector.py`
- Test: `scripts/tests/test_plan_close_detector.py`

**設計 (Codex Gate #2/#4):** quote stripping を明示。任意コマンド実行を排し、`ASSERTS` 固定 allowlist の `shell=False` 起動のみ。

- [ ] **Step 1: 失敗するテストを書く (パス存在 / allowlist assert / quote strip / 非allowlist拒否)**

`test_plan_close_detector.py` に追記:

```python
def test_artifacts_present_all_exist(tmp_path, monkeypatch):
    (tmp_path / "a.py").write_text("x")
    (tmp_path / "b.sh").write_text("y")
    monkeypatch.setattr(pcd, "REPO_ROOT", tmp_path)
    assert pcd.artifacts_present('"a.py, b.sh"') is True  # outer quote を strip


def test_artifacts_present_missing_one(tmp_path, monkeypatch):
    (tmp_path / "a.py").write_text("x")
    monkeypatch.setattr(pcd, "REPO_ROOT", tmp_path)
    assert pcd.artifacts_present("a.py, b.sh") is False


def test_asserts_satisfied_allowlisted(monkeypatch):
    # ALLOWLIST のキーを exit 0 で返すコマンドに差し替え
    monkeypatch.setattr(pcd, "ASSERTS", {"ok": ["true"], "ng": ["false"]})
    assert pcd.asserts_satisfied("ok") is True
    assert pcd.asserts_satisfied("ok, ng") is False


def test_asserts_satisfied_rejects_non_allowlisted(monkeypatch):
    monkeypatch.setattr(pcd, "ASSERTS", {"ok": ["true"]})
    # allowlist 外のキーは無視され、有効 assert ゼロ → False (証拠なし)
    assert pcd.asserts_satisfied("rm -rf /") is False
    assert pcd.asserts_satisfied("! task validate-configs") is False
```

- [ ] **Step 2: テストが失敗することを確認**

Run: `python3 -m pytest scripts/tests/test_plan_close_detector.py -k "artifacts or asserts" -v`
Expected: FAIL (`AttributeError`)

- [ ] **Step 3: 実装 — quote strip + artifacts_present + ASSERTS allowlist + asserts_satisfied**

`plan-close-detector.py` に追記:

```python
import subprocess

# Fixed allowlist: assert key → argv (shell=False で起動). plan frontmatter からは
# キーのみ参照可能で、任意コマンドは実行できない (Codex Gate #4: prompt injection 遮断).
ASSERTS: dict[str, list[str]] = {
    "validate-configs": ["task", "validate-configs"],
    "validate-symlinks": ["task", "validate-symlinks"],
    "plan-close-tests": ["python3", "-m", "pytest",
                         "scripts/tests/test_plan_close_detector.py", "-q"],
}


def _csv(field: str) -> list[str]:
    """Strip outer quotes (Codex Gate #2) and split a comma-separated field."""
    v = field.strip().strip('"').strip("'")
    return [x.strip() for x in v.split(",") if x.strip()]


def artifacts_present(artifacts: str) -> bool:
    """Weak signal: all declared artifact paths exist. None/empty → False."""
    paths = _csv(artifacts)
    return bool(paths) and all((REPO_ROOT / p).exists() for p in paths)


def asserts_satisfied(asserts: str) -> bool:
    """Strong signal: every allowlisted assert key exits 0 (shell=False).

    Keys not in ASSERTS are ignored. If no valid assert remains → False."""
    keys = [k for k in _csv(asserts) if k in ASSERTS]
    if not keys:
        return False
    for k in keys:
        try:
            rc = subprocess.run(
                ASSERTS[k], cwd=REPO_ROOT, timeout=120,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            ).returncode
        except (subprocess.SubprocessError, OSError):
            return False
        if rc != 0:
            return False
    return True
```

- [ ] **Step 4: テストが通ることを確認**

Run: `python3 -m pytest scripts/tests/test_plan_close_detector.py -k "artifacts or asserts" -v`
Expected: PASS (4 passed)

- [ ] **Step 5: コミット**

```bash
git add scripts/lifecycle/plan-close-detector.py scripts/tests/test_plan_close_detector.py
git commit -m "✨ feat(lifecycle): artifacts_present + asserts_satisfied (allowlist, shell=False)"
```

---

### Task 3: Tier 分類

**Files:**
- Modify: `scripts/lifecycle/plan-close-detector.py`
- Test: `scripts/tests/test_plan_close_detector.py`

分類規則 (`classify(signals, stale_days, tree_clean, stale_threshold=30)`)。`tree_clean` は対象 plan の成果物に未コミット変更が無いか (scan が `git diff --quiet` で算出して渡す):

| 結果 | 条件 | Tier | 自動 PR |
|---|---|---|---|
| `MISPLACED` | lifecycle ∈ {completed, archive, deferred, done, paused} かつ active/ に存在 | 1 | ○ |
| `VERIFIED_DONE` | lifecycle=active かつ **asserts 充足** かつ **tree_clean** | 1 | ○ |
| `ARTIFACTS_PRESENT` | lifecycle=active かつ artifacts 全実在 (パスのみ=弱証拠) | 2 | × |
| `LIKELY_DONE` | lifecycle=active, asserts/artifacts 無, stale≥閾値, checkbox 総数>0 かつ 全 done | 2 | × |
| `STALE` | lifecycle=active, stale≥閾値, 上記いずれにも該当せず | 3 | × |
| `HEALTHY` | それ以外 | — | × |

> **Codex Gate #1**: パス存在のみは「作成済み」の弱証拠 → 必ず Tier2 (報告のみ)。Tier1 (自動 PR) は allowlisted assert の exit 0 + clean tree を要求し、途中実装の誤クローズを構造的に防ぐ。

- [ ] **Step 1: 失敗するテストを書く**

```python
def test_classify_misplaced():
    s = pcd.Signals(path=Path("docs/plans/active/x.md"), lifecycle="completed",
                    artifacts=None, asserts=None, checkboxes_total=0, checkboxes_done=0)
    v = pcd.classify(s, stale_days=5, tree_clean=True)
    assert v.result == "MISPLACED" and v.tier == 1


def test_classify_verified_done_requires_assert_and_clean_tree(monkeypatch):
    monkeypatch.setattr(pcd, "ASSERTS", {"ok": ["true"]})
    s = pcd.Signals(path=Path("x.md"), lifecycle="active", artifacts=None,
                    asserts="ok", checkboxes_total=3, checkboxes_done=0)
    assert pcd.classify(s, stale_days=1, tree_clean=True).result == "VERIFIED_DONE"
    # dirty tree → Tier1 不可 (HEALTHY に落ちる)
    assert pcd.classify(s, stale_days=1, tree_clean=False).result == "HEALTHY"


def test_classify_artifacts_present_is_tier2(monkeypatch, tmp_path):
    (tmp_path / "a.py").write_text("x")
    monkeypatch.setattr(pcd, "REPO_ROOT", tmp_path)
    s = pcd.Signals(path=Path("x.md"), lifecycle="active", artifacts="a.py",
                    asserts=None, checkboxes_total=3, checkboxes_done=0)
    v = pcd.classify(s, stale_days=1, tree_clean=True)
    assert v.result == "ARTIFACTS_PRESENT" and v.tier == 2


def test_classify_likely_done_is_tier2():
    s = pcd.Signals(path=Path("x.md"), lifecycle="active", artifacts=None,
                    asserts=None, checkboxes_total=4, checkboxes_done=4)
    v = pcd.classify(s, stale_days=40, tree_clean=True)
    assert v.result == "LIKELY_DONE" and v.tier == 2


def test_classify_healthy_recent():
    s = pcd.Signals(path=Path("x.md"), lifecycle="active", artifacts=None,
                    asserts=None, checkboxes_total=4, checkboxes_done=1)
    assert pcd.classify(s, stale_days=3, tree_clean=True).result == "HEALTHY"
```

- [ ] **Step 2: テストが失敗することを確認**

Run: `python3 -m pytest scripts/tests/test_plan_close_detector.py -k classify -v`
Expected: FAIL (`AttributeError: classify`)

- [ ] **Step 3: 実装 — classify**

`plan-close-detector.py` に追記:

```python
STALE_THRESHOLD_DAYS = 30
_CLOSED_LIFECYCLES = {"completed", "archive", "deferred", "done", "paused"}


@dataclass
class Verdict:
    result: str
    tier: int  # 0 = none


def classify(signals: Signals, stale_days: int, tree_clean: bool,
             stale_threshold: int = STALE_THRESHOLD_DAYS) -> Verdict:
    s = signals
    if s.lifecycle in _CLOSED_LIFECYCLES:
        return Verdict("MISPLACED", 1)
    if s.lifecycle != "active":
        return Verdict("HEALTHY", 0)
    # Tier1: 強証拠 (allowlisted assert 成功) かつ working tree clean のみ
    if s.asserts and asserts_satisfied(s.asserts) and tree_clean:
        return Verdict("VERIFIED_DONE", 1)
    # Tier2: 弱証拠 (成果物パス存在) — 報告のみ
    if s.artifacts and artifacts_present(s.artifacts):
        return Verdict("ARTIFACTS_PRESENT", 2)
    if (not s.asserts and not s.artifacts and stale_days >= stale_threshold
            and s.checkboxes_total > 0 and s.checkboxes_done == s.checkboxes_total):
        return Verdict("LIKELY_DONE", 2)
    if stale_days >= stale_threshold:
        return Verdict("STALE", 3)
    return Verdict("HEALTHY", 0)
```

- [ ] **Step 4: テストが通ることを確認**

Run: `python3 -m pytest scripts/tests/test_plan_close_detector.py -k classify -v`
Expected: PASS (5 passed)

- [ ] **Step 5: コミット**

```bash
git add scripts/lifecycle/plan-close-detector.py scripts/tests/test_plan_close_detector.py
git commit -m "✨ feat(lifecycle): Tier 分類 (Tier1=assert+clean tree, パス存在は Tier2 降格)"
```

---

### Task 4: scan エントリポイント + git stale + レポート出力

**Files:**
- Modify: `scripts/lifecycle/plan-close-detector.py`
- Test: `scripts/tests/test_plan_close_detector.py`
- Create: `docs/plan-close/.gitkeep`, `docs/plan-close/README.md`

- [ ] **Step 1: git stale 日数ヘルパのテストを書く**

```python
def test_git_stale_days_handles_untracked(tmp_path, monkeypatch):
    monkeypatch.setattr(pcd, "REPO_ROOT", tmp_path)
    f = tmp_path / "x.md"
    f.write_text("---\nstatus: active\n---\n")
    # untracked file: git log returns empty → fall back to mtime (0 days)
    assert pcd.git_stale_days(f) >= 0
```

- [ ] **Step 2: テストが失敗することを確認**

Run: `python3 -m pytest scripts/tests/test_plan_close_detector.py -k stale -v`
Expected: FAIL (`AttributeError: git_stale_days`)

- [ ] **Step 3: 実装 — git_stale_days + scan + render_report + main**

`plan-close-detector.py` に追記:

```python
import argparse
import json
from datetime import datetime, timezone


def git_stale_days(path: Path) -> int:
    """Days since last commit touching path; falls back to mtime if untracked."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", str(path)],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
        ).stdout.strip()
    except (subprocess.SubprocessError, OSError):
        out = ""
    if out:
        last = datetime.fromisoformat(out)
        return (datetime.now(timezone.utc) - last).days
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        return (datetime.now(timezone.utc) - mtime).days
    except OSError:
        return 0


def tree_clean_for(artifacts: str | None) -> bool:
    """True if declared artifact paths have no uncommitted changes (Codex Gate)."""
    paths = _csv(artifacts) if artifacts else []
    if not paths:
        return True  # 成果物宣言が無ければ tree 条件は中立 (Tier1 は asserts 側で律速)
    try:
        rc = subprocess.run(["git", "diff", "--quiet", "--", *paths],
                            cwd=REPO_ROOT, timeout=30).returncode
        rc2 = subprocess.run(["git", "diff", "--cached", "--quiet", "--", *paths],
                             cwd=REPO_ROOT, timeout=30).returncode
        return rc == 0 and rc2 == 0
    except (subprocess.SubprocessError, OSError):
        return False  # 判定不能なら clean とみなさない (fail-safe: Tier1 に上げない)


def scan(active_dir: Path = ACTIVE_DIR) -> list[dict]:
    rows = []
    for f in sorted(active_dir.glob("*.md")):
        sig = extract_signals(f)
        stale = git_stale_days(f)
        verdict = classify(sig, stale, tree_clean=tree_clean_for(sig.artifacts))
        if verdict.tier == 0:
            continue
        rows.append({
            "file": str(f.relative_to(REPO_ROOT)),
            "result": verdict.result,
            "tier": verdict.tier,
            "lifecycle": sig.lifecycle,
            "artifacts": sig.artifacts,
            "asserts": sig.asserts,
            "checkboxes": f"{sig.checkboxes_done}/{sig.checkboxes_total}",
            "stale_days": stale,
        })
    return rows


def render_report(rows: list[dict], today: str) -> str:
    lines = [f"# Plan close-candidate report — {today}", ""]
    for tier in (1, 2, 3):
        group = [r for r in rows if r["tier"] == tier]
        label = {1: "Tier1 (auto-PR 対象)", 2: "Tier2 (報告のみ)",
                 3: "Tier3 (stale のみ)"}[tier]
        lines.append(f"## {label} — {len(group)} 件")
        for r in group:
            lines.append(f"- `{r['file']}` — {r['result']} "
                         f"(lifecycle={r['lifecycle']}, checkbox={r['checkboxes']}, "
                         f"stale={r['stale_days']}d)")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply-tier1", action="store_true",
                    help="Tier1 候補を安全層付き PR 提案として生成 (calibration 後のみ、直接 move しない)")
    ap.add_argument("--out", default=str(REPO_ROOT / "docs" / "plan-close"))
    args = ap.parse_args()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rows = scan()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{today}-close-report.md").write_text(
        render_report(rows, today), encoding="utf-8")
    with (out_dir / "candidates.jsonl").open("a", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps({**r, "scanned": today}, ensure_ascii=False) + "\n")
    if args.apply_tier1:
        # Gated: implemented in Task 6, no-op until calibration opens it.
        raise SystemExit("--apply-tier1 is gated; see Task 5/6 calibration milestone")
    print(f"scanned: {len(rows)} candidates → {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: テストが通ることを確認 + 全テスト**

Run: `python3 -m pytest scripts/tests/test_plan_close_detector.py -v`
Expected: PASS (全件)

- [ ] **Step 5: docs/plan-close/ を作成**

```bash
mkdir -p docs/plan-close
printf '# plan-close レポート出力先\n\nplan-close-detector の dry-run scan 出力 (`<DATE>-close-report.md`, `candidates.jsonl`)。\nTier1 候補のみ将来 auto-PR 対象。Tier2/3 は人間がクローズ判断する。\n' > docs/plan-close/README.md
touch docs/plan-close/.gitkeep
```

- [ ] **Step 6: 実 active/ に対して dry-run 実行 (dogfood)**

Run: `python3 scripts/lifecycle/plan-close-detector.py`
Expected: `docs/plan-close/<today>-close-report.md` 生成。誤配置 (skill-guide-absorb=completed が active/) が MISPLACED (Tier1) に出ること、本 plan は asserts(plan-close-tests) 未通過のため VERIFIED_DONE にはならず ARTIFACTS_PRESENT(Tier2) 止まりであることを目視確認。

- [ ] **Step 7: コミット**

```bash
git add scripts/lifecycle/plan-close-detector.py scripts/tests/test_plan_close_detector.py docs/plan-close/
git commit -m "✨ feat(lifecycle): scan エントリポイント + git stale + レポート出力"
```

---

### Task 5: nightly 配線 + calibration ledger (教訓2・3)

**Files:**
- Create: `scripts/runtime/nightly/run-plan-close-scan.sh`
- Modify: `scripts/runtime/nightly/launchd-install.sh` (`TASKS` 配列)
- 再利用: `scripts/learner/calibration-verdict-logger.py` (auto-triage で構築済み)

- [ ] **Step 1: nightly runner を作成**

`scripts/runtime/nightly/run-plan-close-scan.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
REPO="${DOTFILES_DIR:-$HOME/dotfiles}"
cd "$REPO"
LOG="$HOME/.claude/agent-memory/logs/plan-close-scan.log"
mkdir -p "$(dirname "$LOG")"
echo "[$(date -u +%FT%TZ)] plan-close-scan start" >>"$LOG"
# dry-run のみ (auto-apply は calibration milestone まで開放しない)
python3 scripts/lifecycle/plan-close-detector.py >>"$LOG" 2>&1
echo "[$(date -u +%FT%TZ)] plan-close-scan done" >>"$LOG"
```

```bash
chmod +x scripts/runtime/nightly/run-plan-close-scan.sh
```

- [ ] **Step 2: launchd の TASKS 配列に登録 (教訓2: 配線漏れ防止)**

`scripts/runtime/nightly/launchd-install.sh` の `TASKS` 配列 (現状 8 件) に追加。**書式は `task|hour|minute|script` (Codex Gate #6 で確認済み — 初版の `task|script|hour|minute` は誤り)**:

```bash
  "plan-close-scan|0|50|run-plan-close-scan.sh"   # 毎日 00:50
```

(保存前に `launchd-install.sh:13` 付近の既存エントリ書式を Read して目視照合すること。)

- [ ] **Step 3: 配線を検証 (教訓2)**

```bash
bash scripts/runtime/nightly/launchd-install.sh
launchctl list | grep plan-close-scan
```

Expected: `com.user.nightly.plan-close-scan` が一覧に出る (last exit = 0 or -)。出なければ TASKS 書式ミス → 修正。

- [ ] **Step 4: pending source of truth と calibration の役割分担 (Codex Gate #5)**

`calibration-verdict-logger.py` は「裁定記録器」であって pending queue ではない。したがって:
- **pending source of truth は `docs/plan-close/candidates.jsonl`** (scan が append、Tier1 候補を含む)。runner はここに書くだけで、logger は呼ばない。
- **人間が Tier1 PR をレビューして agree/disagree を出した後**にのみ `calibration-verdict-logger.py` で裁定を記録する (auto-triage と同じ使い方。`--help` と auto-triage runner の呼び出し例を grep して引数を確定)。
- これにより「自動が pending を作る」と「人間が裁定を記録する」が分離され、logger を pending emit に誤用しない。

- [ ] **Step 5: コミット**

```bash
git add scripts/runtime/nightly/run-plan-close-scan.sh scripts/runtime/nightly/launchd-install.sh
git commit -m "🔧 chore(nightly): plan-close-scan を launchd 配線 + calibration ledger 連携"
```

---

### Task 6: auto-apply (Tier1) — **calibration milestone まで gated**

**前提ゲート (教訓3):** Task 5 の nightly を最低 30 日運用し、`calibration-verdict-logger` の Tier1 human-agree 率 ≥ 0.9 を実測してから本 Task に着手する。未達なら撤退条件に従い Tier1 を報告のみに降格 (本 Task を破棄)。

**Files:**
- Modify: `scripts/lifecycle/plan-close-detector.py` (`--apply-tier1` の no-op を実装に置換)
- Test: `scripts/tests/test_plan_close_detector.py`

**安全層 (Codex Gate: `run-learned-promote.sh` から縮小移植)。auto-apply は直接 move/commit せず、必ず PR 提案に固定する:**
1. **preflight (fail-loud)**: global working tree が clean でなければ即 abort (途中作業に割り込まない)。
2. **open PR guard**: 既存の plan-close PR (ブランチ `plan-close/<date>` or ラベル) があれば新規作成しない。
3. **allowlist stage**: 移動対象は Tier1 候補 (MISPLACED/VERIFIED_DONE) のみ。Tier2/3 は絶対に触らない。
4. **dry-run diff 出力**: PR body に move 計画と各候補の根拠 (lifecycle/asserts 結果/stale) を必ず含める。
5. **PR 経由のみ**: 専用ブランチで git mv + frontmatter 書換 → push → PR。master へ直接 commit/move しない (人間 merge が最後の砦)。

- [ ] **Step 1: 失敗するテストを書く (move 計画生成。実 git 操作は dry_run で抑止)**

```python
def test_plan_moves_misplaced_to_correct_dir(tmp_path, monkeypatch):
    active = tmp_path / "docs/plans/active"
    active.mkdir(parents=True)
    (active / "x.md").write_text("---\nlifecycle: deferred\n---\n# x\n")
    monkeypatch.setattr(pcd, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(pcd, "ACTIVE_DIR", active)
    moves = pcd.plan_moves()  # 計画のみ、git 操作なし
    assert any(m["to"].endswith("paused/x.md") and m["result"] == "MISPLACED"
               for m in moves)
```

- [ ] **Step 2: テストが失敗することを確認**

Run: `python3 -m pytest scripts/tests/test_plan_close_detector.py -k moves -v`
Expected: FAIL (`AttributeError: plan_moves`)

- [ ] **Step 3: 実装 — plan_moves (純粋計画) + apply_via_pr (副作用は PR のみ)**

```python
_LIFECYCLE_TO_DIR = {"completed": "completed", "archive": "completed",
                     "done": "completed", "deferred": "paused", "paused": "paused"}


def plan_moves() -> list[dict]:
    """Pure planner: Tier1 候補の move 計画を返す (git 操作なし、テスト可能)."""
    moves = []
    for f in sorted(ACTIVE_DIR.glob("*.md")):
        sig = extract_signals(f)
        verdict = classify(sig, git_stale_days(f), tree_clean=tree_clean_for(sig.artifacts))
        if verdict.tier != 1:
            continue
        if verdict.result == "MISPLACED":
            dest_dir = _LIFECYCLE_TO_DIR.get(sig.lifecycle or "", "completed")
            new_lifecycle = sig.lifecycle
        else:  # VERIFIED_DONE
            dest_dir, new_lifecycle = "completed", "completed"
        moves.append({
            "from": str(f.relative_to(REPO_ROOT)),
            "to": f"docs/plans/{dest_dir}/{f.name}",
            "result": verdict.result,
            "new_lifecycle": new_lifecycle,
            "rationale": f"{verdict.result}: lifecycle={sig.lifecycle}, asserts={sig.asserts}",
        })
    return moves


def apply_via_pr() -> int:
    """安全層付き auto-apply: preflight → 専用ブランチで move → PR 提案。直接 commit しない."""
    # 1. preflight: global tree clean (fail-loud)
    if subprocess.run(["git", "diff", "--quiet"], cwd=REPO_ROOT).returncode != 0:
        raise SystemExit("[plan-close] working tree dirty; abort (preflight)")
    moves = plan_moves()
    if not moves:
        print("[plan-close] no Tier1 candidates")
        return 0
    # 2. open PR guard / 3. branch (実装時に pr-review-*.sh の既存パターンを参照)
    #    branch=plan-close/<date>、既存 open PR があれば skip。
    # 4-5. branch 上で git mv + write_frontmatter → push → gh pr create。
    #    PR body に moves (rationale 込み) を埋め込む。詳細手順は実装時に
    #    scripts/runtime/pr-review-*.sh を Read して合わせる。
    raise SystemExit("apply_via_pr: PR 化手順は pr-review-*.sh パターンで実装する (calibration 後)")
```

`main()` の `--apply-tier1` 分岐を `apply_via_pr()` 呼び出しに置換する。

- [ ] **Step 4: テストが通ることを確認**

Run: `python3 -m pytest scripts/tests/test_plan_close_detector.py -v`
Expected: PASS (全件)

- [ ] **Step 5: コミット**

```bash
git add scripts/lifecycle/plan-close-detector.py scripts/tests/test_plan_close_detector.py
git commit -m "✨ feat(lifecycle): Tier1 auto-apply を安全層付き PR 提案に限定 (直接move禁止)"
```

---

## Self-Review

- **Spec coverage**: 予防 (Task 0 verification 規約) / 検出 (Task 1-4) / 棚卸し (Task 4 Step 6 dogfood scan) / 自動 PR (Task 6, gated) / 配線 (Task 5) / calibration (Task 5 Step 4) — ユーザー選択「両方フル + 自動 PR」を全てカバー。
- **教訓の反映**: checkbox 格下げ (Task 3 で Tier2 限定) / launchd 登録必須 (Task 5 Step 2-3) / calibration gate (Task 6 前提) — 3 件とも task 化済み。
- **型整合**: `Signals`(lifecycle/artifacts/asserts) / `Verdict` dataclass、`extract_signals`/`artifacts_present`/`asserts_satisfied`/`classify`(tree_clean 引数)/`scan`/`tree_clean_for`/`git_stale_days`/`plan_moves`/`apply_via_pr` のシグネチャは全 task で一貫。
- **既知の未確定点 (実装時に確定)**: Task 5 Step 4 の `calibration-verdict-logger.py` インターフェースは `--help` で確定する (現時点で内部未読のため疑似コードにせず手順で明示)。Task 6 の PR 化は既存 `pr-review-*.sh` パターンに合わせる。
