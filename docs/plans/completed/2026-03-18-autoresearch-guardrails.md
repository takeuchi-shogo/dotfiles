---
status: active
last_reviewed: 2026-04-23
---

# Autoresearch Guardrails 統合 実装プラン

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** autoresearch 記事 "Your Autoresearch Loop Will Cheat" の3つの知見（ドリフト検出、提案品質トラッキング、単一変更規律）を既存の AutoEvolve インフラに統合する

**Architecture:** session_events.py に proposal verdict イベントを追加し、session-learner.py で accept/reject 比率を集計。improve-policy.md にドリフトガードルールを追加し、`/improve --evolve` ループに単一変更規律と changelog 生成を組み込む。既存のテストパターン（AUTOEVOLVE_DATA_DIR による隔離）を踏襲。

**Tech Stack:** Python 3, Bash, Markdown

---

## ファイル構成

| ファイル | 役割 | 変更種別 |
|---|---|---|
| `.config/claude/scripts/lib/session_events.py` | proposal verdict イベントの emit 関数追加 | Modify |
| `.config/claude/scripts/learner/session-learner.py` | proposal 集計 + accept_rate メトリクス | Modify |
| `.config/claude/references/improve-policy.md` | ドリフトガード + 単一変更ルール追加 | Modify |
| `.config/claude/skills/improve/SKILL.md` | --evolve ループに changelog + drift check 統合 | Modify |
| `tests/scripts/test_session_events.py` | proposal verdict のテスト | Modify |
| `tests/scripts/test_session_learner.py` | accept_rate 集計のテスト | Modify |

---

## Task 1: Proposal Verdict イベント追加 (session_events.py)

`/improve --evolve` ループの各イテレーションで keep/revert の判定結果を記録する。

**Files:**
- Modify: `.config/claude/scripts/lib/session_events.py`
- Test: `tests/scripts/test_session_events.py`

- [ ] **Step 1: テスト作成 — emit_proposal_verdict**

  `tests/scripts/test_session_events.py` の冒頭に `import pytest` を追加（既存の import 群の末尾）。
  同ファイルの `TestSessionEvents` クラスに以下を追加:

  ```python
  def test_emit_proposal_verdict_keep(self):
      from session_events import emit_proposal_verdict
      emit_proposal_verdict(
          skill_name="landing-page-copy",
          hypothesis="見出しに数値を強制",
          verdict="keep",
          metric_before=0.56,
          metric_after=0.72,
          iteration=1,
      )
      temp_path = Path(self.tmpdir) / "current-session.jsonl"
      data = json.loads(temp_path.read_text().strip())
      assert data["category"] == "proposal"
      assert data["verdict"] == "keep"
      assert data["skill_name"] == "landing-page-copy"
      assert data["delta"] == pytest.approx(0.16, abs=0.001)

  def test_emit_proposal_verdict_revert(self):
      from session_events import emit_proposal_verdict
      emit_proposal_verdict(
          skill_name="landing-page-copy",
          hypothesis="ワードカウント制限",
          verdict="revert",
          metric_before=0.85,
          metric_after=0.78,
          iteration=3,
      )
      temp_path = Path(self.tmpdir) / "current-session.jsonl"
      data = json.loads(temp_path.read_text().strip())
      assert data["verdict"] == "revert"
      assert data["delta"] == pytest.approx(-0.07, abs=0.001)
  ```

- [ ] **Step 2: テスト実行 — 失敗確認**

  Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest tests/scripts/test_session_events.py::TestSessionEvents::test_emit_proposal_verdict_keep -v`
  Expected: FAIL — `ImportError: cannot import name 'emit_proposal_verdict'`

- [ ] **Step 3: emit_proposal_verdict 実装**

  `.config/claude/scripts/lib/session_events.py` に追加:

  ```python
  def emit_proposal_verdict(
      skill_name: str,
      hypothesis: str,
      verdict: str,  # "keep" | "revert"
      metric_before: float,
      metric_after: float,
      iteration: int,
      extra: dict | None = None,
  ) -> None:
      """AutoEvolve --evolve ループの提案判定結果を記録する。

      autoresearch パターン: 各イテレーションの keep/revert を追跡し、
      accept rate でエージェントの提案品質を定量化する。
      """
      delta = round(metric_after - metric_before, 4)
      emit_event(
          "proposal",
          {
              "type": "verdict",
              "skill_name": skill_name,
              "hypothesis": hypothesis,
              "verdict": verdict,
              "metric_before": metric_before,
              "metric_after": metric_after,
              "delta": delta,
              "iteration": iteration,
              **(extra or {}),
          },
      )
  ```

- [ ] **Step 4: テスト実行 — 成功確認**

  Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest tests/scripts/test_session_events.py::TestSessionEvents::test_emit_proposal_verdict_keep tests/scripts/test_session_events.py::TestSessionEvents::test_emit_proposal_verdict_revert -v`
  Expected: PASS

- [ ] **Step 5: コミット**

  ```bash
  git add .config/claude/scripts/lib/session_events.py tests/scripts/test_session_events.py
  git commit -m "$(cat <<'EOF'
  ✨ feat(session-events): add emit_proposal_verdict for autoresearch tracking

  Track keep/revert decisions in --evolve loops to quantify proposal quality.
  Inspired by "Your Autoresearch Loop Will Cheat" article findings.
  EOF
  )"
  ```

---

## Task 2: Proposal Accept Rate 集計 (session-learner.py)

セッション終了時に proposal verdict を集計し、accept_rate をメトリクスに追加する。

**Files:**
- Modify: `.config/claude/scripts/learner/session-learner.py`
- Test: `tests/scripts/test_session_learner.py`

- [ ] **Step 6: テスト作成 — proposal 集計**

  `tests/scripts/test_session_learner.py` の冒頭に `import pytest` を追加（既存の import 群の末尾）。
  同ファイルの `TestSessionLearner` クラスに以下を追加。
  **注意**: `session-learner.py` はハイフン付きファイル名のため、既存の `_import_session_learner()` ヘルパーを使用する。

  ```python
  def test_proposal_accept_rate_tracking(self):
      """Proposal verdict events are aggregated into accept_rate metric."""
      from session_events import emit_proposal_verdict
      # 3 keep, 1 revert → accept_rate = 0.75
      for i, v in enumerate(["keep", "keep", "revert", "keep"], 1):
          emit_proposal_verdict("test-skill", f"hyp-{i}", v, 0.5, 0.6 if v == "keep" else 0.4, i)

      sl = _import_session_learner()
      summary = sl.build_session_summary(cwd=self.tmpdir)
      proposals = [e for e in summary["_events"] if e.get("category") == "proposal"]
      assert len(proposals) == 4

  def test_proposal_accept_rate_in_metrics(self):
      """Accept rate appears in session metrics when proposals exist."""
      from session_events import emit_proposal_verdict
      emit_proposal_verdict("s", "h", "keep", 0.5, 0.7, 1)
      emit_proposal_verdict("s", "h", "revert", 0.7, 0.6, 2)

      sl = _import_session_learner()
      summary = sl.build_session_summary(cwd=self.tmpdir)
      pm = sl._compute_proposal_metrics(summary["_events"])
      assert pm["proposal_count"] == 2
      assert pm["accept_rate"] == pytest.approx(0.5)
      assert pm["consecutive_rejects"] == 1
  ```

- [ ] **Step 7: テスト実行 — 失敗確認**

  Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest tests/scripts/test_session_learner.py::TestSessionLearner::test_proposal_accept_rate_tracking -v`
  Expected: FAIL

- [ ] **Step 8: _compute_proposal_metrics 実装**

  `session-learner.py` に関数を追加:

  ```python
  def _compute_proposal_metrics(events: list[dict]) -> dict:
      """Proposal verdict イベントから accept_rate と連続 reject 数を計算する。

      autoresearch 記事の知見: accept_rate がエージェントの提案品質を示す。
      GPT-5.4: 67%, Spark: 17%。連続 reject はドリフトのシグナル。
      """
      proposals = [e for e in events if e.get("category") == "proposal" and e.get("type") == "verdict"]
      if not proposals:
          return {}

      keeps = sum(1 for p in proposals if p.get("verdict") == "keep")
      total = len(proposals)

      # 末尾からの連続 revert 数（ドリフト検出用）
      consecutive_rejects = 0
      for p in reversed(proposals):
          if p.get("verdict") == "revert":
              consecutive_rejects += 1
          else:
              break

      return {
          "proposal_count": total,
          "accept_count": keeps,
          "reject_count": total - keeps,
          "accept_rate": round(keeps / total, 2) if total > 0 else 0.0,
          "consecutive_rejects": consecutive_rejects,
      }
  ```

- [ ] **Step 9: process_session に proposal メトリクス統合**

  `process_session()` 内、`metrics = {...}` の直前に追加:

  ```python
  # Proposal quality tracking (autoresearch pattern)
  proposal_metrics = _compute_proposal_metrics(events)
  if proposal_metrics:
      for p in [e for e in events if e.get("category") == "proposal"]:
          append_to_learnings("proposal-verdicts", {
              k: v for k, v in p.items() if k != "category"
          })
  ```

  `metrics` dict に統合:

  ```python
  metrics = {
      ...existing fields...,
      **proposal_metrics,  # accept_rate, consecutive_rejects etc.
      **cfs_data,
  }
  ```

- [ ] **Step 10: テスト実行 — 成功確認**

  Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest tests/scripts/test_session_learner.py -v -k "proposal"`
  Expected: PASS

- [ ] **Step 11: コミット**

  ```bash
  git add .config/claude/scripts/learner/session-learner.py tests/scripts/test_session_learner.py
  git commit -m "$(cat <<'EOF'
  ✨ feat(session-learner): track proposal accept_rate and consecutive rejects

  Aggregate keep/revert verdicts into session metrics for proposal quality
  monitoring. consecutive_rejects enables drift detection.
  EOF
  )"
  ```

---

## Task 3: ドリフトガードルール (improve-policy.md)

連続 reject 上限、目的メトリクス後退検出、単一変更規律をポリシーに追加。

**Files:**
- Modify: `.config/claude/references/improve-policy.md`

- [ ] **Step 12: improve-policy.md にルール 17-19 を追加**

  `### 安全ルール` セクション末尾（Rule 16 の後）に追加:

  ```markdown
  17. **ドリフトガード: 連続 reject 上限** — `--evolve` ループで 3 イテレーション連続 `revert` が発生した場合、ループを即時停止しユーザーにエスカレーションする。autoresearch 記事: "12時間放置でエージェントが別の問題を解き始めた"。連続 reject = 目的から逸脱のシグナル
  18. **ドリフトガード: 目的メトリクス後退検出** — `--evolve` ループの各イテレーションで、ベースラインスコアからの累積改善を追跡する。3 イテレーション経過後にベースラインを下回っている場合はループを停止し「戦略を再検討」を推奨する
  19. **単一変更規律** — `--evolve` ループの各イテレーションでは SKILL.md への変更を **1箇所のみ** に制限する。仮説を明記し、changelog に記録する。autoresearch 記事: "proposal quality dominates total cost" — 少数の精度の高い変更が多数の探索的変更に勝る
  ```

- [ ] **Step 13: コミット**

  ```bash
  git add .config/claude/references/improve-policy.md
  git commit -m "$(cat <<'EOF'
  📝 docs(improve-policy): add drift guard and single-change discipline rules

  Rules 17-19: consecutive reject limit (3), baseline regression detection,
  and one-change-per-iteration discipline. Based on autoresearch article.
  EOF
  )"
  ```

---

## Task 4: --evolve ループに Drift Check + Changelog 統合 (improve SKILL.md)

`/improve --evolve` の実際のループフローにドリフト検出と changelog 生成を組み込む。

**Files:**
- Modify: `.config/claude/skills/improve/SKILL.md`

- [ ] **Step 14: 早期終了条件を拡張**

  `### 早期終了条件` セクションを以下に置換:

  ```markdown
  ### 早期終了条件

  - 2 イテレーション連続で `auto_reject` → ループ終了
  - **3 イテレーション連続で `revert` → ドリフト検出。ループ停止しユーザーに報告** (Rule 17)
  - **3 イテレーション経過後にベースラインスコアを下回っている → ループ停止** (Rule 18)
  - 全対象スキルが healthy に昇格 → ループ終了
  - `--iterations` 上限に到達 → ループ終了
  ```

- [ ] **Step 15: ループフロー Step 3 (Proposer) に単一変更制約を追加**

  ループフローの Step 3 を以下に修正:

  ```markdown
  3. **Proposer**: `autoevolve-core (phase: improve)` を起動。H（`proposer-context --skill {target}`）+ 失敗トレースを注入。AP-1〜4 チェック。
     - **単一変更規律 (Rule 19)**: Proposer への指示に以下を含める: 「SKILL.md への変更は **1箇所のみ**。仮説を1文で明記すること。」
     - Proposer は `hypothesis` フィールドを返す（例: "見出しに数値を強制するルールを追加"）
  ```

- [ ] **Step 16: ループフロー Step 5 (検証) に verdict 記録を追加**

  ループフローの Step 5 の後に追加:

  ```markdown
  5b. **Verdict 記録**: 検証結果を `emit_proposal_verdict()` で記録。以下を実行:
      ```python
      from session_events import emit_proposal_verdict
      emit_proposal_verdict(
          skill_name=target_skill,
          hypothesis=proposer_hypothesis,
          verdict="keep" if gate_passed else "revert",
          metric_before=baseline_score,
          metric_after=current_score,
          iteration=current_iteration,
      )
      ```
  ```

- [ ] **Step 17: Changelog 生成セクションを追加**

  `### ループ完了後のレポート` の直前に追加:

  ```markdown
  ### Changelog 生成

  各イテレーション完了後、ワークスペースの `changelog.md` を更新する:

  ```markdown
  # Skill Evolution Changelog: {skill-name}

  ## Round {N} ({date})
  - **Hypothesis**: {proposer_hypothesis}
  - **Change**: {変更箇所の概要}
  - **Result**: {KEEP|REVERT} (metric: {before} → {after}, delta: {delta})
  ```

  Changelog は `--evolve` レポートに全文を含める。
  ```

- [ ] **Step 18: ループ完了後レポートに accept_rate を追加**

  `### ループ完了後のレポート` のテーブルに列を追加:

  ```markdown
  | Iter | 対象スキル | 仮説 | Gate 判定 | A/B delta | 累積改善 |
  |---|---|---|---|---|---|
  | 1 | {skill} | {hypothesis} | {verdict} | {delta} | {cumulative} |

  - 実行イテレーション数: N / {max}
  - **Accept Rate: {keeps}/{total} ({rate}%)** — autoresearch 記事基準: 50%以上が健全
  - 早期終了: {yes/no, reason}
  - ドリフト検出: {yes/no}
  ```

- [ ] **Step 19: コミット**

  ```bash
  git add .config/claude/skills/improve/SKILL.md
  git commit -m "$(cat <<'EOF'
  ✨ feat(improve): integrate drift detection and changelog in --evolve loop

  Add consecutive reject detection, baseline regression check, single-change
  discipline, verdict recording, and changelog generation to evolve loop.
  EOF
  )"
  ```

---

## Task 5: 全体テスト + メモリ更新

- [ ] **Step 20: 全テスト実行**

  Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest tests/scripts/ -v`
  Expected: ALL PASS

- [ ] **Step 21: MEMORY.md に autoresearch 統合の知見を追記**

  既存の `## AutoEvolve` セクションに追記:

  ```markdown
  - **autoresearch guardrails (2026-03-18)**: "Your Autoresearch Loop Will Cheat" 記事ベース。3施策: emit_proposal_verdict (accept/reject 追跡), ドリフトガード (3連続reject停止 + ベースライン後退検出), 単一変更規律 (1iter=1change + changelog)。improve-policy Rule 17-19
  ```

- [ ] **Step 22: 最終コミット**

  ```bash
  git add ~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/MEMORY.md
  git commit -m "$(cat <<'EOF'
  📝 docs(memory): record autoresearch guardrails integration
  EOF
  )"
  ```

---

## 検証チェックリスト

1. **後方互換**: proposal event がない既存セッションで session-learner.py が正常動作（`_compute_proposal_metrics` が空 dict を返す）
2. **emit_proposal_verdict**: keep/revert 両方で current-session.jsonl に正しく記録
3. **accept_rate 集計**: proposal-verdicts.jsonl と session-metrics.jsonl に出力
4. **consecutive_rejects**: 末尾からの連続 revert 数が正しく計算
5. **improve-policy.md**: Rule 17-19 が既存ルールと矛盾しない
6. **SKILL.md**: --evolve ループの早期終了条件が拡張されている
7. **全テスト通過**: `python3 -m pytest tests/scripts/ -v`
