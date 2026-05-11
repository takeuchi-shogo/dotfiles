---
status: active
last_reviewed: 2026-04-29
---

# Self-Healing Agent Harness Absorb Plan

## Source

- 記事: The Self-Healing Agent Harness (CREAO CTO Peter Pang, 2026-04-29 推定)
- 分析: `docs/research/2026-04-29-self-healing-harness-absorb-analysis.md`
- 前作 absorb: `docs/research/2026-04-14-creao-ai-first-analysis.md` + `docs/plans/2026-04-14-creao-absorb-plan.md`

## Goal

CREAO 記事から **Pruning-First** で 4 件のみ採択。Codex 批評で「吸収しすぎ」を回避済。本 plan は T4-C のみ管理 (T1/T2/T3 は同セッション完了済)。

## 完了済 (同セッション)

- **T1**: `evaluator-calibration-guide.md` に「Outcome over Trajectory」原則を追加 (S, ~13 行)
- **T2**: `absorb/SKILL.md` Phase 2.5 に model-family diversity rationale を追記 (S, ~3 行)
- **T3**: `evaluator-calibration-guide.md` に「再校正条件」セクションを追加 (S, ~14 行)

## 未完了 (本 plan)

### T4-C: regression-suite.json populate + harness 変更時 hook (M)

#### Background

- 既存の `scripts/eval/regression-gate.py` (5.3K) は schema validator のみ。実 cases を実行していない
- `regression-suite.json` は未生成 (find で 0 件)
- `eval-generator.py` (14.7K) で failure-clusterer から regression cases を生成する設計だが wiring 未完
- 2026-04-14 absorb plan で類似の B2 (failure-clusters → /improve 接続) は採択されなかった (注意資源の負債化リスク)
- `improve-policy.md` Rule 32 (Cross-Model 検証) が「skill 改善時に Haiku/Codex smoke test」を既に提供 — T4-C と直交だが補完関係

#### Pruning-First Justification

T4-C は「自動チケット化」を含まない。記事の主張から以下のみ採用:

- ✅ **採用**: harness rule 変更時 (skill/agent/hook 編集) に既知の failure cluster を少数 re-run して regression を検出
- ❌ **棄却**: 100%/24h re-grade、自動 ticket 起票、auto-fix PR 作成、grey rollout

つまり「**変更時の数件 smoke test**」止まり。CREAO の Engineering Pipeline は採用しない。

#### Tasks

##### T4-C-1: regression-suite.json の最小 populate (S)

`scripts/eval/regression-suite.json` を作成。初期サイズは **5-10 件** に限定。

- ソース: `failure-clusterer.py` の出力から TPR/TNR > 0.9 で人間検証済みの failure cases を抽出
- スキーマ: `regression-gate.py` の `_validate_tuple()` に合わせる (`failure_mode` ∈ KNOWN_FM_CODES, `expected_reviewer` ∈ KNOWN_REVIEWERS)
- フィールド: `id`, `failure_mode`, `expected_reviewer`, `input`, `expected_output`, `notes`
- 育成方針: 後追いで増やすが、**上限 30 件**。それ以上は staleness リスク

**Acceptance**:
- `python scripts/eval/regression-gate.py` が PASS で exit 0
- `regression-suite.json` の `tuples` が 5 件以上
- 全 tuple が validation を通る

##### T4-C-2: harness 変更検出ロジック (M)

「harness rule 変更」をどう判定するか。3 候補:

| 候補 | 検出方法 | 利点 | 欠点 |
|-----|---------|------|------|
| A. **PostToolUse hook** | `.claude/skills/*`, `.claude/agents/*`, `.claude/CLAUDE.md` への Edit/Write を検出 | リアルタイム | hook 過剰実行の懸念 |
| B. **commit-msg lefthook** | git diff で対象パスを検出 | バッチで安定 | コミット時のみ |
| C. **手動 (improve-policy Rule 33)** | `/improve` 起動時に harness 変更があれば自動実行 | sleep 中 noise なし | 即時性なし |

**推奨**: **C (手動 + improve-policy Rule 33)**。理由:
- 2026-04-14 で「自動チケット化は注意資源の負債化」と判定済
- `/improve` の Adversarial Phase で自然に発火できる
- 手動 (or sleep 中) なら hook 過剰の懸念なし

**Acceptance**:
- `improve-policy.md` に Rule 33 を追加: 「`/improve` 起動時に直近 N 日の `.claude/{skills,agents,CLAUDE.md}` 変更があれば `regression-gate.py` を発火、FAIL なら改善提案を draft に留める」
- N の初期値は 7 日 (recalibrate 可)

##### T4-C-3: 結果の AutoEvolve への connect (S-M)

`regression-gate.py` の出力 (status, failed_ids) を AutoEvolve に渡す:

- FAIL → 改善提案を draft に留める (PASS なら通常 review へ)
- WARN → 警告のみ、ブロックしない
- 出力先: `.claude/state/regression-gate-history.jsonl` に追記 (改善サイクル内で参照可能に)

**Acceptance**:
- `autoevolve-core` が `regression-gate-history.jsonl` を読んで提案フィルタリングできる
- FAIL ステータスが draft 化に反映される

#### Risks

| リスク | 対策 |
|------|------|
| regression-suite.json の staleness (実 failure と乖離) | 上限 30 件、`eval-staleness.py` で自動 retire 候補検出 |
| harness 変更が小さくても毎回 re-run で時間負担 | 初期 5-10 件に限定、Codex/Haiku で並列実行 |
| 「自動チケット化」への slippery slope | 設計時点で「FAIL → draft」止まり。auto-fix PR は明示的に scope 外 |
| B2 と同じ「dead weight 化」リスク | 30 日後に使用率を測定。発火回数 0 なら撤退 |

#### Dependency Graph

```
T4-C-1 (suite populate)
    ↓
T4-C-2 (improve-policy Rule 33 追加)
    ↓
T4-C-3 (AutoEvolve connect)
```

順序: T4-C-1 → T4-C-2 → T4-C-3。並列化不可。

#### Validation

各タスク完了後:
- `task validate-configs`
- `task validate-symlinks`
- `python scripts/eval/regression-gate.py` (exit 0)
- 30 日後の使用率レビュー (撤退判断)

#### Retreat Conditions

- T4-C-1 で 5 件の suite tuple を populate できない (検証済 failure cases が不足) → **撤退**
- T4-C-2 で improve-policy 既存 Rule との衝突が発見 → **降格** (手動運用のみ、Rule 化棄却)
- 30 日後に発火回数 0 → **撤退** (dead weight)

## References

- `docs/research/2026-04-29-self-healing-harness-absorb-analysis.md` (本 plan の根拠)
- `scripts/eval/regression-gate.py` (実装済 schema validator)
- `references/improve-policy.md` Rule 32 (補完関係の Cross-Model 検証)
- `docs/plans/2026-04-14-creao-absorb-plan.md` (前作 absorb の完了タスク)

## Execution

別セッションで `/rpi docs/plans/active/2026-04-29-self-healing-absorb-plan.md` を実行する。
