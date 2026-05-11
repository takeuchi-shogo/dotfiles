---
status: active
last_reviewed: 2026-04-23
---

# Integration Plan: Empirical Prompt Tuning (mizchi)

## Overview

| Field | Value |
|-------|-------|
| Source | mizchi/chezmoi-dotfiles `dot_claude/skills/empirical-prompt-tuning/SKILL.md` |
| Analysis | `docs/research/2026-04-19-empirical-prompt-tuning-absorb-analysis.md` |
| Total Tasks | 4 (T1-T4, targets_criterion 棄却) |
| Estimated Size | M-L (約 10-12 files changed) |
| Priority Order | T1 → (T4 並列) → T2+T3 (template 統合) |

## Goal

mizchi の Empirical Prompt Tuning 5 手法から抽出した 4 タスクを dotfiles に統合し、プロンプト品質の客観的評価基盤を強化する。Phase 2.5 (Codex+Gemini 並列) で検出した Self-preference Bias / Reward Hacking / Holdout Contamination / Evaluator Drift のリスクも同時に対策する。

## Tasks

### Task 1 (T1): tool_uses + qualitative_signals 接続 (P1)

| Field | Value |
|-------|-------|
| Files | `.config/claude/skills/skill-creator/scripts/aggregate.py`, `.config/claude/skills/improve/SKILL.md`, `.config/claude/skills/improve/instructions/evolve-mode.md`, `.config/claude/skills/skill-creator/instructions/testing-evaluation.md`, **新規** `.config/claude/references/qualitative-signals-spec.md` |
| Dependencies | なし (最優先) |
| Size | M (4 既存 + 1 新規) |

**Changes:**
- `aggregate.py`: 既存 `quality_score` + `duration_ms` に加え `tool_count` (session-trace-store.py から) と `precision_of_tool_use` (= 有効呼び出し数 / 全呼び出し数) を primary 指標に追加。reward hacking 防止のため必ず併記
- `improve/SKILL.md` Convergence Check セクション: `tool_uses` 安定性 (±10-15%) を判定条件に追加
- `evolve-mode.md`: proposer/evaluator に「eval 出力に `tool_uses`, `qualitative_signals` を含めること」明記
- `testing-evaluation.md`: `qualitative_signals.jsonl` の記録規約 (記録タイミング・粒度・retention)
- 新規 `qualitative-signals-spec.md`: schema 定義
  - `event_type`: `ambiguity` | `retry` | `failure_reason` | `clarification_request`
  - `severity`: `low` | `medium` | `high`
  - `source_agent`: agent name
  - `message`: short description
  - `iteration_id`, `timestamp`

**Acceptance Criteria:**
- [critical] `aggregate.py` 出力に `tool_count` と `precision_of_tool_use` カラムが含まれる
- [critical] improve eval 1 サイクル実行で `qualitative_signals.jsonl` が生成される
- Convergence Check ログに tool_uses 安定性判定が出力される

### Task 2 (T2): Convergence holdout + evaluator drift 対策 (P2)

| Field | Value |
|-------|-------|
| Files | `.config/claude/skills/improve/SKILL.md`, `.config/claude/scripts/runtime/learner/` 配下の improve-history schema (要事前調査), `.config/claude/references/improve-policy.md` |
| Dependencies | T1 (qualitative_signals が convergence 判定の前提) |
| Size | M (3-4 files) |

**Changes:**
- `improve/SKILL.md`: `--validate-holdout` フェーズ追加 (収束判定後、spec の `holdout_scenarios` で再評価。失敗したら convergence 否認)
- improve-history schema: `evaluator_model_version` フィールド追加。drift 検出ロジック (前回と version が違えばベースライン再測定推奨)
- `improve-policy.md`:
  - **Rule 24**: 収束判定の前に必ず `holdout_scenarios` で再評価する。spec から事前分離保持
  - **Rule 25**: evaluator model version が変動したら drift とみなし、ベースラインスコアを再測定する

**Acceptance Criteria:**
- [critical] `improve --validate-holdout` で holdout シナリオ評価が実行される
- [critical] `improve-history.jsonl` の各エントリに `evaluator_model_version` が記録される
- Rule 24/25 が `improve-policy.md` に明記される

**事前調査:**
- `scripts/runtime/learner/` 配下で improve-history.jsonl を書き出すスクリプト特定
- 既存 schema との後方互換性確保 (`schema_version` フィールドで分岐)

### Task 3 (T3): spec template に scenarios 構造化 (P2 強化)

| Field | Value |
|-------|-------|
| Files | `.config/claude/skills/spec/templates/prompt-as-prd-template.md`, `.config/claude/scripts/policy/spec-quality-check.py` |
| Dependencies | T2 と template ファイルが重なるので統合可能 |
| Size | S (2 files) |

**Changes:**
- `prompt-as-prd-template.md`: `scenarios:` セクション追加
  - `median:` (1 ケース必須)
  - `edge_cases:` (1-2 ケース推奨)
  - `holdout_scenarios:` (T2 で消費される、spec から分離保持)
- `spec-quality-check.py`: `scenarios.median` 必須チェック追加 (新規 spec のみ error、既存 spec は warning)

**Acceptance Criteria:**
- [critical] 新規 spec ファイルで `scenarios.median` 欠如時に hook が警告
- template 例として 1 median + 2 edge_cases + 1 holdout が含まれる

### Task 4 (T4): blind 評価の memory 分離 + 異モデル契約 (P3 強化)

| Field | Value |
|-------|-------|
| Files | `.config/claude/skills/improve/instructions/phase4-adversarial-gate.md`, `.config/claude/agents/codex-reviewer.md` |
| Dependencies | 独立 (T1 と並列実行可) |
| Size | S (2 files) |

**Changes:**
- `phase4-adversarial-gate.md`: 「異モデル必須・local memory disable」契約明記。Anthropic Agent Evals の Self-preference Bias 知見を引用 (https://www.anthropic.com/news/evaluating-ai-agents)
- `codex-reviewer.md`: Self-preference Bias 警告セクション追記。評価対象が Claude 系の場合は Codex (GPT-5.4) 使用を推奨

**Acceptance Criteria:**
- [critical] `adversarial-gate.md` に「同モデルファミリー禁止」明記
- `codex-reviewer.md` に Self-preference Bias セクション

## Risks / Mitigations

| リスク | 出典 | 対策タスク |
|------|------|----------|
| Self-preference Bias | Gemini, Anthropic Agent Evals | T4 で異モデル必須化 |
| Reward Hacking (tool_uses 単独最適化) | Gemini, arXiv:2403.03023 | T1 で `precision_of_tool_use` 併用 |
| Holdout Contamination | Gemini, arXiv:2211.01910 | T2 で `holdout_scenarios` を spec から分離保持 |
| Evaluator Drift | Gemini | T2 で `evaluator_model_version` 記録 |
| 共有 memory バイアス | Codex | T4 で local memory disable 契約 |

## Reversibility

すべての変更は `git revert` で復元可能:
- 新規 reference (`qualitative-signals-spec.md`) と新規 hook ルール (Rule 24/25) は最小限の追加で副作用なし
- template 変更は既存 spec と互換 (新規 spec のみ強制)
- aggregate.py の primary 指標追加は既存カラムを維持して追加のみ

## Pre-mortem (失敗モード)

| 失敗モード | 検知 | 対策 |
|----------|------|------|
| T1 で `aggregate.py` 改変が既存 eval pipeline を壊す | task validate-configs 失敗、improve eval 落ちる | adapt mode で旧フォーマット読み取り fallback |
| T2 で `improve-history.jsonl` schema 変更が既存履歴と非互換 | parser エラー、convergence 判定不能 | `schema_version` フィールドで分岐、旧履歴は v1 として読む |
| T3 で `spec-quality-check.py` が既存 spec を全部 fail にする | pre-commit hook 大量 block | Phase 0: `scenarios` キー欠如は warning のみ、新規ファイルのみ error |
| T4 の異モデル必須化で Codex CLI 障害時に improve がブロック | adversarial-gate 永続失敗 | fallback: Claude Sonnet で評価可だが warning 表示 |
| `precision_of_tool_use` の「有効」判定基準が曖昧 | 集計値が 0/1 に偏る | spec で「エラーなく完了したツール呼び出し」と暫定定義、改善余地として残す |

## Implementation Order

1. **Wave 1 (並列可)**: T1 と T4 を並列実行 (独立)
2. **Wave 2 (T1 完了後)**: T2 + T3 (template 統合のため同時)
3. **Wave 3 (全体検証)**:
   - `task validate-configs`
   - `task validate-symlinks`
   - 既存 improve eval を 1 サイクル実行 → qualitative_signals.jsonl 生成確認
   - 新規 spec ファイルを 1 つ生成 → spec-quality-check.py 通過確認

## Verification

- [x] `task validate-configs` 通過
- [x] `task validate-symlinks` 通過
- [ ] improve eval 実行で `qualitative_signals.jsonl` 生成
- [ ] spec template から `scenarios` セクション付き spec を 1 つ生成して spec-quality-check.py 通過
- [ ] `improve --validate-holdout` で holdout シナリオ評価が動作
- [ ] `adversarial-gate.md` に異モデル契約明記、codex-reviewer.md に Self-preference Bias セクション

## Chaining

- **Spec/Plan Gate**: M-L 規模なので `codex-plan-reviewer` で Plan レビューを通すこと
- **Edge Case Analysis**: `/edge-case-analysis` で異常系 (CLI 障害時 fallback、schema migration) を洗い出す
- **Review Gate**: コード変更後は `/review` で Codex Review Gate 経由
