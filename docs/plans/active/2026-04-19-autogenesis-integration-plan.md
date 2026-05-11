---
status: active
last_reviewed: 2026-04-23
---

# Integration Plan: Autogenesis Self-Evolving Agent Protocol

## Overview

| Field | Value |
|-------|-------|
| Source | Autogenesis: A Self-Evolving Agent Protocol (arxiv 2604.15034) |
| Analysis | `docs/research/2026-04-19-autogenesis-absorb-analysis.md` |
| Total Tasks | 5 |
| Estimated Size | L (7-9 files changed) |
| Priority Order | T1 → T2 → T3 → T4 → T5 (T1 が他の前提) |

## Tasks

### Task 1 (T1): hypotheses.jsonl registry を Phase 1 に追加

| Field | Value |
|-------|-------|
| Files | `.config/claude/agents/autoevolve-core.md` (Phase 1 セクション), `.config/claude/references/autoevolve-artifacts.md` (新規 or 既存更新), `.config/claude/scripts/learner/session-learner.py` (optional: auto-populate) |
| Dependencies | なし (他タスクの前提) |
| Size | M |

**Changes:**
- autoevolve-core.md Phase 1 出力に `hypotheses.jsonl` を追加
- schema: `{trace_id, hypothesis, falsification_criteria, metric, status: pending/confirmed/refuted, created_at, resolved_at}`
- Reflect (meta-analyzer) が生成、Select (Phase 2.0) が消費、Evaluate (Phase 2.5 Codex gate) が falsification を確認
- 永続化: `.config/claude/learnings/hypotheses.jsonl` (retention: learning 永続)
- evidence_chain との関係を明文化 (evidence_chain は提案側、hypotheses は観測側)

### Task 2 (T2): Co-evolution 候補 schema (resource_targets 3 次元化)

| Field | Value |
|-------|-------|
| Files | `.config/claude/agents/autoevolve-core.md` (Phase 2.0), `.config/claude/references/improve-policy.md` (候補生成ルール), `.config/claude/references/proposal-schema.md` (新規 or 既存更新) |
| Dependencies | T1 (hypotheses を参照する候補生成) |
| Size | M |

**Changes:**
- Phase 2.0 candidate schema を拡張: `resource_targets: ["prompt" | "config" | "strategy" (複数可)]`, `interaction_hypothesis: string`
- 1 候補内で最大 2 resource を同時変更 (dotfiles blast radius 対策 — Codex 指摘)
- Debate フェーズで「prompt-only / strategy-only / both」の ablation 意識を促すプロンプト追加
- mutation_type (refine/pivot/novel) は維持、`resource_targets` と直交して使う

### Task 3 (T3): Rule 8 をカテゴリ別 MDE + holdout 明文化に拡張

| Field | Value |
|-------|-------|
| Files | `.config/claude/references/improve-policy.md` (Rule 8) |
| Dependencies | なし |
| Size | S |

**Changes:**
- Rule 8 `+2pp merge / -2pp revert` を以下に分解:
  - retrieval tasks: +3pp merge / -2pp revert
  - generation tasks: +2pp merge / -2pp revert
  - gate/classifier tasks: +1pp merge / -1pp revert
- holdout set の指定を明文化: eval と improvement の両方で同じ holdout を使わない (overfitting 防止)
- 天井接続: baseline >= 0.9 の場合、delta 閾値を緩める (ceiling aware)

### Task 4 (T4): skill-benchmarks に task_category/model_tier + ceiling detection

| Field | Value |
|-------|-------|
| Files | `.config/claude/scripts/learner/skill-tier-shadow.py` (schema 拡張), `.config/claude/scripts/policy/gaming-detector.py` (ceiling 検知ルール), `.config/claude/references/memory-schema.md` (benchmarks schema 反映) |
| Dependencies | T3 (MDE が category 別) |
| Size | M |

**Changes:**
- skill-benchmarks.jsonl schema 追加: `task_category: retrieval|generation|gate`, `model_tier: weak|strong`
- gaming-detector に ceiling rule: `if baseline_score >= 0.9 and delta < 0.03: flag as ceiling_effect (not improvement)`
- 強/弱モデル両方で評価される skill のみ cross-model ceiling を検知 (常時ではない)

### Task 5 (T5): Cost-aware evolution gate

| Field | Value |
|-------|-------|
| Files | `.config/claude/references/improve-policy.md` (Rule 追加), `.config/claude/scripts/policy/completion-gate.py` or 新 `cost-gate.py`, `.config/claude/agents/autoevolve-core.md` (Phase 0 or 1 頭) |
| Dependencies | なし (独立) |
| Size | M |

**Changes:**
- AutoEvolve run_started_at.txt と並行して `cycle-cost.json` を記録
- schema: `{cycle_id, model, input_tokens, output_tokens, cost_usd, cumulative_usd}`
- budget gate: 1 サイクル当たり $5 超で警告、$10 超で停止 (値は暫定、運用後調整)
- Gemini 指摘 "$1 問題に $10 API 費" 対策

### Task 6 (T6, 低優先度・オプション): memory version + snapshot

| Field | Value |
|-------|-------|
| Files | `.config/claude/references/memory-schema.md`, `docs/specs/2026-04-17-memory-schema-retention.md` 更新 |
| Dependencies | T1-T5 完了後 |
| Size | M |

**Changes:**
- memory-schema に `version: int`, `snapshot_ref: git_sha | null` 追加
- MEMORY.md 更新を Phase 2 Improve commit に連動 (既存 git で 80% 代替可能なため実装は最小限)

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Co-evolution で blast radius 増大 | 中 | 1 候補内で最大 2 resource のみ同時変更、Codex Adversarial Gate を強化 |
| hypotheses.jsonl が未消化で肥大化 | 低 | retention: unresolved hypotheses は 60 日で archive、confirmed/refuted は永続 |
| category 別 MDE でカテゴリ誤分類 | 中 | skill 定義に task_category を必須化、未指定は generation 扱い (safe default) |
| Cost gate が autoevolve を止める | 低 | budget は警告→停止の 2 段階、ユーザー override 可 |
| Alignment faking (Gemini 指摘) | 中 | S4 holdout 明文化で「評価通過 != 実タスク通過」を検知。将来 N4 として別途取り組み |

## Pre-mortem (`references/pre-mortem-checklist.md` 参照)

- **失敗モード 1**: hypotheses.jsonl が session-learner の出力をコピペしただけになる → Reflect フェーズで「既知 → 仮説化」の変換を必須化
- **失敗モード 2**: resource_targets が常に `[prompt, config, strategy]` (全部入り) になる → Debate プロンプトで「最小変更原則」を明示
- **失敗モード 3**: category 別 MDE がカテゴリ自己申告で緩く調整される → skill-audit で抜き打ち検証を年 1 回

## Reversibility (`references/reversible-decisions.md` 参照)

- T1-T5 全て autoevolve/2026-04-19-autogenesis-integration ブランチで隔離
- T3 (Rule 8 拡張) のみ policy 変更で影響広範 → Rule 8 を separate commit にして revert しやすく
- 撤退条件: 2 サイクル連続で co-evolution 候補が失敗 (revert) → T2 を旧 mutation_type に revert

## Execution

| Size | Approach |
|------|----------|
| L (7-9 files, T1-T5) | 新セッションで `/rpi docs/plans/active/2026-04-19-autogenesis-integration-plan.md` で段階実行 |

実行順: T1 → T2 (T1 依存) → T3 → T4 (T3 依存) → T5 (独立、T1-T4 と並行可能) → T6 (後回し)

## Handoff Notes

- 論文 arxiv 2604.15034 の Pass@1 ベンチマーク前提は dotfiles には合わない (Codex 指摘) → 個人 CLI 設定リポの KPI は friction 減少、再発率、rollback 率、手戻り時間
- AFlow / ADAS が prompt + strategy co-evolution を支持 (Gemini) → 参考実装
- 統合プランの T1 が起点。T1 完了後に T2 のスキーマ詳細を再検討可
