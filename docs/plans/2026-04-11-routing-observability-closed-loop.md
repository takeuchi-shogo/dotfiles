---
status: active
last_reviewed: 2026-04-23
---

# Routing & Capability Observability — Closed Loop

**Date**: 2026-04-11
**Owner**: harness maintainer
**Status**: proposed (not started)
**Size**: L (Wave 1 は M 相当、Wave 2-3 は spike 前提)
**Origin**: Codex critique during `/absorb` of "Mixture of Experts Explained" (2026-04-11)

## TL;DR

既存ハーネスの Router (CLAUDE.md agent_delegation + triage-router), capability weighting (reviewer-capability-scores.md), routing 学習 (autoevolve + race-outcomes) は **参照先は存在するが実測で閉ループしていない**。Codex の `/absorb` 批評で発覚。ルーティングの「判断が妥当だったか」を直接測定するメトリクスが存在せず、改善サイクルが駆動できていない。

## Context

### Codex の原文指摘 (2026-04-11 の MoE /absorb Phase 2.5 より)

> 「`exists` と言っている中に「参照先はあるが、実測で閉ループしていない」ものが混じっている点です。特に capability weighting と routing 学習は、その典型に見えます」
>
> 調査の末尾で Codex は `.config/claude/references/observability-signals.md` + `scripts/learner/skill-tier-shadow.py` + `scripts/learner/qa-tuning-analyzer.py` + `reviewer-capability-scores.md` を読み、「設計メモ段階に留まり、実測 → 改善のフィードバックループが切れている」と判断。

### 現状の閉ループ有無マトリクス

| コンポーネント | 設計 | 計測 | フィードバック | 閉ループ? |
|---------------|-----|------|-------------|---------|
| Reviewer Capability Scores | ✅ | 🟡 (手動更新) | 🟡 (update-policy のみ) | ❌ |
| Routing Decision (agent_delegation) | ✅ | ❌ (ログなし) | ❌ | ❌ |
| race-outcomes.jsonl | ✅ | ✅ | 🟡 (集計なし) | 🟡 |
| skill-executions.jsonl (skill-audit Tier) | ✅ | ✅ | ✅ (skill-audit で活用) | ✅ |
| review-findings.jsonl (accept/reject 追跡) | ✅ | ✅ | ✅ (AutoEvolve) | ✅ |
| agent-invocations histogram | ❌ (今回 MoE absorb で追加検討) | ❌ | ❌ | ❌ |

**パターン**: skill-level では閉ループが成立 (skill-audit, review-feedback-tracker) しているが、**agent-level と routing-level で閉ループが欠落**している。

## Acceptance Criteria

- [ ] **AC-1**: `agent-invocations.jsonl` が記録され、過去 30 日のエージェント呼び出し分布を `skill-audit` が参照できる (MoE absorb で追加した Dominant tier が実データで動作する)
- [ ] **AC-2**: Routing decision log (「どのタスクで誰を呼んだか、結果の quality はどうだったか」) が `routing-decisions.jsonl` に記録される
- [ ] **AC-3**: `reviewer-capability-scores.md` のスコアが手動更新から **race-outcomes + review-findings の集計による半自動更新** に移行する
- [ ] **AC-4**: `/improve` サイクルで routing 精度の時系列変化を確認できる (「先週比 routing 正解率 +5%」等)
- [ ] **AC-5**: 1 週間実運用した後、Codex に再度批評してもらい「閉ループしている」と認めさせる (AC-gate の独立検証)

## Wave 1 — Measurement layer (M 規模)

まず**計測する**。改善は後。

### Tasks

1. **`agent-invocations.jsonl` の追加** (S)
   - PostToolUse hook で Agent ツール呼び出しを記録
   - フィールド: `timestamp, agent_type, model, parent_task, token_in, token_out, duration_ms, exit_status`
   - 書き込み先: `~/.claude/agent-memory/learnings/agent-invocations.jsonl`
   - 既存の `session-events.py` に emit_agent_invocation 関数を追加

2. **`routing-decisions.jsonl` の追加** (S)
   - triage-router.md の意思決定を structured log に書き出す
   - フィールド: `timestamp, task_summary, candidates[], chosen, reason, outcome_quality_score (nullable, 後で埋める)`
   - outcome_quality_score は実装で空、Wave 2 で埋める

3. **skill-audit への agent-invocations 集計追加** (S)
   - Dominant tier 判定を skill-executions だけでなく agent-invocations にも拡張
   - Over-Use (Expert Collapse) セクションで agent-level と skill-level の両方を表示

**Wave 1 Exit Criteria**: AC-1 達成 + `routing-decisions.jsonl` が 7 日分溜まる

## Wave 2 — Quality attribution (spike)

測ったデータを使って「routing 判断が正しかったか」を評価する。

### Tasks

4. **Outcome quality scoring** (spike, M)
   - routing-decisions.jsonl の各行に後から `outcome_quality_score` を付与
   - スコア源: (a) /review verdict (PASS=1.0, NEEDS_FIX=0.5, BLOCK=0.0), (b) review-findings の accept 率, (c) ユーザーの explicit feedback
   - 集計スクリプト: `scripts/learner/routing-quality-attribution.py`

5. **Counterfactual routing eval** (spike, L)
   - 「もし別のエージェントを選んでいたらどうなっていたか」を過去ログから推定
   - 同じタスクに対する複数エージェントの race 結果 (race-outcomes) を使って pseudo-ground truth を構築
   - この成果物は probabilistic で、ユーザーレビューを前提とする (自動決定しない)

**Wave 2 Exit Criteria**: AC-2 + AC-3 達成、routing 精度指標が定義される

## Wave 3 — Closed loop (改善連結)

測って評価したら、それを改善に使う。

### Tasks

6. **`reviewer-capability-scores.md` 半自動更新** (M)
   - `scripts/learner/capability-score-updater.py` が race-outcomes + review-findings を読み、月次でスコア差分を提案
   - ユーザーが approve/reject する PR を自動生成 (GitHub Actions)
   - 完全自動ではなく「提案 → 人間 approve → merge」のワークフロー (autoevolve の既存パターンに従う)

7. **`/improve` サイクルへの routing 指標追加** (S)
   - autoevolve-core.md の Analyze フェーズで routing 精度を時系列で確認
   - improve-policy.md に "routing-accuracy" カテゴリ追加

8. **Codex 再批評 (AC-5 gate)** (S)
   - 1 週間実運用後、Codex に同じ質問を再送: 「今度は閉ループしていると言えるか?」
   - 「No」なら Wave 3 は追加タスクが必要 — この plan を更新

**Wave 3 Exit Criteria**: AC-4 + AC-5 達成

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| JSONL の書き込みがホットパスでレイテンシを引き起こす | append-only + async write (既存 session-events パターン) |
| counterfactual eval が probabilistic で ground truth にならない | Wave 2 は spike 扱い。結果に `confidence` フィールドを付与 |
| capability scores の自動更新が暴走 | approval ゲート必須、1 サイクル最大 3 ファイルルール (AutoEvolve と同じ制約) |
| 閉ループが「測っているだけで改善に繋がらない」 | AC-5 で Codex 再批評を強制 (独立検証) |

## Reversibility

- Wave 1 は純追加 (ログ書き込みのみ)。ロールバックは hook 削除 + jsonl 削除で完了
- Wave 2 は spike なので、結果が出なかったら plan 自体を破棄
- Wave 3 は approval 必須なので、破壊的変更は起こらない

## Out of Scope

- MoA /absorb で追加した候補 H (Intent-Based Gating 動的 Tier 分類) はこの plan の対象外。別 plan で扱う
- LLM 内部の auxiliary loss や gradient-level 改善は対象外 (ハーネスレベルではない)
- routing 決定の完全自動化 (approval を外す) は対象外。人間判断を残す

## References

- Codex critique: 本 plan の起点
- `.config/claude/references/reviewer-capability-scores.md` — 現状のスコアテーブル
- `.config/claude/references/model-expertise-map.md` — Cross-MoA 原則 (2026-04-11 追加)
- `.config/claude/references/observability-signals.md` — 計測シグナル一覧
- `.config/claude/agents/autoevolve-core.md` — 改善サイクル
- `docs/research/2026-04-11-moe-article-analysis.md` — MoE 記事分析の Codex 部分批評
- Better Harness (eval hill-climbing) パターン — `docs/plans/2026-04-09-skill-eval-improvement-plan.md` と連動
