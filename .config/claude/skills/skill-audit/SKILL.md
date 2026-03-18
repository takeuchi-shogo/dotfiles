---
name: skill-audit
description: "Batch A/B benchmarking and health audit for skills. Use when user says 'audit skills', 'benchmark skills', 'skill health check', 'retire unused skills', or 'check skill quality'. Runs A/B tests across multiple skills, detects description conflicts, and generates audit reports. Do NOT use for creating or editing individual skills (use skill-creator instead)."
metadata:
  pattern: reviewer
---

# Skill Audit

Batch A/B benchmarking and health audit for installed skills. This skill orchestrates the eval infrastructure scripts (`run_eval.sh`, `compare.sh`, `aggregate.py`) across multiple skills to measure their value, detect description conflicts between competing skills, and produce actionable audit reports.

Use this skill when you want to:

- Benchmark multiple skills in a single pass
- Find skills that overlap or conflict in their trigger descriptions
- Identify skills that should be retired, improved, or kept as-is
- Get a data-driven overview of skill health

## Default Target Batches

### Batch 1 — High Risk (model knowledge overlap)

Skills whose domains overlap heavily with the base model's knowledge. These are most likely to show marginal or negative delta vs baseline:

- `react-best-practices`
- `react-expert`
- `senior-architect`
- `senior-backend`
- `senior-frontend`
- `search-first`

### Batch 2 — Competing Pairs (trigger conflicts)

Skill pairs whose descriptions may cause incorrect or ambiguous triggering:

- `frontend-design` vs `ui-ux-pro-max`
- `codex-review` vs `review`

The user can override these defaults with a custom skill list.

## Workflow

Execute the following steps in order:

### Step 0: 5D Quality Scan

A/B ベンチマーク（重い）を回す前に、対象スキルの SKILL.md を 5 次元で静的スクリーニングする。

#### 手順

1. 対象スキルの SKILL.md + references/ + scripts/ を読む
2. 以下の 5 次元それぞれを Good/Average/Poor で判定する
3. いずれかが Poor → audit report の「Improve」セクションに `(5D)` 注記付きで分類
4. 結果を audit report Summary テーブルの 5D 列に記録

#### 5 次元の定義（SkillNet [arXiv:2603.04448](https://arxiv.org/abs/2603.04448) prompts.py 準拠）

| 次元 | Good | Average | Poor |
|------|------|---------|------|
| **Safety** | 破壊的操作をデフォルト回避、安全チェック含む、スコープ制限明示 | 良性ドメインだがリスク操作のセーフガード言及なし | 危険なアクション(delete/reset等)をガードなしで言及 |
| **Completeness** | 目標+手順+入出力が明確、前提条件を記載 | 目標は明確だが手順/前提/出力が不十分 | 曖昧すぎて行動不能、核心的手順欠如 |
| **Executability** | 具体的アクション/コマンド/パラメータ。指示のみスキルは明確ガイダンスで OK | 概ね実行可能だが曖昧ステップあり | 実行不能な曖昧指示 |
| **Maintainability** | 狭いスコープ、モジュール性、明確な入出力、低結合 | 再利用部分はあるが境界が不明確 | スコープ広すぎ or 密結合 |
| **Cost-awareness** | 軽量タスクは低コスト。重量タスクはバッチ/制限/キャッシュを明示 | コスト制御なしだが無駄もない | 無駄なワークフローを限度なく推奨 |

#### 追加ルール

- `allowed_tools` が必要以上に広い場合 → Safety を 1 レベル下げ
- コア式/アルゴリズムの致命的エラー → Completeness を最大 Average（通常 Poor）
- トリビアルなスクリプト（echo のみ等）→ Executability を最大 Average

### Step 1: Select target skills

Ask the user which batch to audit, or accept a custom skill list. Default to both batches if unspecified.

### Step 2: Generate test prompts

For each skill, generate 3 test prompts in `evals.json` format:

1. **Clear-trigger** — a prompt that unambiguously belongs to this skill's domain
2. **Borderline** — a prompt on the edge between this skill and general model capability
3. **Domain-depth** — a prompt requiring deep specialized knowledge the skill should provide

Save each skill's prompts to `.skill-eval/{skill-name}/evals/evals.json`:

```json
{
  "skill_name": "{skill-name}",
  "evals": [
    {
      "id": 1,
      "name": "clear-trigger",
      "prompt": "...",
      "expected_output": "..."
    },
    {
      "id": 2,
      "name": "borderline",
      "prompt": "...",
      "expected_output": "..."
    },
    {
      "id": 3,
      "name": "domain-depth",
      "prompt": "...",
      "expected_output": "..."
    }
  ]
}
```

### Step 3: Run A/B benchmark

For each skill, run the eval harness. This launches `claude -p` with and without the skill for each prompt:

```bash
bash ~/.claude/skills/skill-creator/scripts/run_eval.sh "{skill-name}" ".skill-eval/{skill-name}/evals/evals.json"
```

### Step 4: Compare and grade

For each eval directory produced by step 3, run blind A/B comparison:

```bash
bash ~/.claude/skills/skill-creator/scripts/compare.sh ".skill-eval/{skill-name}/iteration-N/eval-{name}"
```

Run this for every `eval-*` subdirectory within the iteration.

### Step 5: Aggregate results

Aggregate all grading data into a benchmark summary:

```bash
python3 ~/.claude/skills/skill-creator/scripts/aggregate.py ".skill-eval/{skill-name}/iteration-N" --skill-name "{skill-name}"
```

This produces `benchmark.json` and `benchmark.md` in the iteration directory.

### Step 6: Emit results to AutoEvolve

Record the benchmark data in the AutoEvolve learning system:

```bash
python3 ~/.claude/skills/skill-creator/scripts/emit_benchmark.py ".skill-eval/{skill-name}/iteration-N/benchmark.json"
```

This appends results to `~/.claude/agent-memory/learnings/skill-benchmarks.jsonl`.

### Step 7: Generate audit report

After all skills have been benchmarked, compile results into a single audit report at `docs/benchmarks/YYYY-MM-DD-audit.md` (see Audit Report Format below).

## Scale-Aware Execution

Adapt parallelism to the number of skills being audited:

| Skills | Strategy                                                               |
| ------ | ---------------------------------------------------------------------- |
| 1-2    | Execute `run_eval.sh` sequentially in the main session                 |
| 3-6    | Run `run_eval.sh` instances in parallel via subagents (one per skill)  |
| 7+     | Split into 2 batches, run each batch's skills in parallel sequentially |

Steps 4-6 (compare, aggregate, emit) always run sequentially per skill after its eval completes.

## Competing Pair Analysis

For Batch 2 skills, perform additional conflict detection after the standard benchmark:

1. **Extract descriptions** — Read both skills' SKILL.md frontmatter descriptions
2. **Generate test queries** — Create 10 test queries:
   - 5 that should trigger Skill A but not Skill B
   - 5 that should trigger Skill B but not Skill A
3. **Test triggering** — For each query, run `claude -p` and check which skill actually triggers
4. **Measure overlap** — Calculate the percentage of queries that triggered the wrong skill or both skills
5. **Recommend action** — If overlap exceeds 40%, recommend description rewrite via `skill-creator` description optimization flow

Include conflict analysis results in the audit report under "Description Conflicts Detected".

## Audit Report Format

Generate the report at `docs/benchmarks/YYYY-MM-DD-audit.md` using this template:

```markdown
# Skill Audit Report — YYYY-MM-DD

## Summary

| Skill   | Safety | Comp. | Exec. | Maint. | Cost | Quality (with) | Quality (baseline) | Delta | Recommendation |
| ------- | ------ | ----- | ----- | ------ | ---- | -------------- | ------------------ | ----- | -------------- |
| skill-a | Good   | Good  | Avg   | Good   | Good | 7.5            | 6.0                | +1.5  | Keep           |
| skill-b | Avg    | Poor  | Good  | Avg    | Good | —              | —                  | —     | Improve (5D)   |

## Recommendations

### Retire

- **skill-b** — Degrades quality (delta: -0.5). Consider removing or reworking.

### Improve

- **skill-c** — Marginal difference (delta: +0.2). Needs description or content refinement.

### Keep

- **skill-a** — Clearly improves quality (delta: +1.5).

## Description Conflicts Detected

| Pair                             | Overlap % | Detail                                     |
| -------------------------------- | --------- | ------------------------------------------ |
| frontend-design vs ui-ux-pro-max | 60%       | 6/10 queries triggered both or wrong skill |
```

## K-Variant Testing (RLOO/GRPO)

スキルの設定バリエーションを K>=3 個用意し、
RLOO/GRPO advantage で最適な variant を特定する。

### 手順

1. 対象スキルの SKILL.md を K 個の variant にコピー
2. 各 variant で `run_eval.sh` を実行し result JSON を生成
3. `aggregate_benchmark.py --variants` で比較:

```bash
python3 ~/.claude/scripts/eval/aggregate_benchmark.py \
    --variants v1.json v2.json v3.json \
    --output report.md
```

4. レポートの Advantage 値を確認:
   - **RLOO Advantage > 0**: baseline より優れている
   - **RLOO Advantage < 0**: baseline より劣っている
   - **GRPO Advantage**: z-score 正規化された相対位置

### RLOO Advantage 解釈ガイド

| Advantage | 解釈 | アクション |
|-----------|------|-----------|
| > +0.5 | 明確に優秀 | merge 推奨 |
| +0.1 ~ +0.5 | やや優秀 | 追加テスト推奨 |
| -0.1 ~ +0.1 | 差なし | 変更不要 |
| < -0.1 | 劣化 | revert 推奨 |

GRPO は z-score なので ±1.0 が1標準偏差。
±2.0 を超える variant は外れ値として注意。

## Output Locations

| Artifact                   | Path                                                      |
| -------------------------- | --------------------------------------------------------- |
| Benchmark data (per skill) | `.skill-eval/{skill-name}/iteration-N/benchmark.json`     |
| Audit report               | `docs/benchmarks/YYYY-MM-DD-audit.md`                     |
| AutoEvolve learnings       | `~/.claude/agent-memory/learnings/skill-benchmarks.jsonl` |

## Gotchas

- **統計的検出力不足**: 2-3回の eval では有意差を検出できない。最低5回、理想は10回以上
- **cherry-pick 結果**: 成功ケースだけ報告するバイアス。失敗ケースも含めた全結果を評価
- **description conflict 誤検知**: 似た description でも対象ドメインが異なれば競合しない。Do NOT use for を確認
- **退役判断の早まり**: 使用頻度が低くても特定シナリオで重要なスキルがある。頻度だけで判断しない
