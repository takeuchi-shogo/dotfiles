---
name: skill-audit
description: >
  Batch A/B benchmarking and health audit for skills. Runs A/B tests across multiple skills,
  detects description conflicts, and generates audit reports.
  Triggers: 'audit skills', 'benchmark skills', 'skill health check', 'retire unused skills', 'check skill quality', 'スキル監査'.
  Do NOT use for: creating or editing individual skills (use skill-creator instead), コードベース監査（use /audit）、AI ワークフロー監査（use /ai-workflow-audit）。
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

### Step 0.5: Usage Tier Classification

5D スキャンと並行して、対象スキルの使用頻度を分類する。

#### 手順

1. `skill-executions.jsonl` を読み、過去 30 日間の各スキルの実行回数を集計する
2. **全スキルの合計実行回数に対する占有率**を算出し、以下の 4 段階に分類する:

| Tier | 基準（過去30日） | アクション |
|------|----------------|-----------|
| **Dominant** | 全実行の **40% 以上** を占有 | Expert Collapse 兆候。役割重複 or 過剰委譲を疑う |
| **Weekly** | 4回以上（Dominant 未満） | 維持・優先改善対象 |
| **Monthly** | 1〜3回 | 現状維持。改善は低優先 |
| **Unused** | 0回 | retire 候補としてレポートに出力 |

3. `skill-executions.jsonl` が存在しない、またはデータ不足の場合はこのステップをスキップし、5D スキャンのみで判定する
4. 結果を audit report Summary テーブルの Usage 列に記録する
5. Unused スキルは audit report の「Retire Candidates」セクションにリストする
6. Dominant スキルは audit report の「Over-Use (Expert Collapse)」セクションにリストし、以下を確認する:
   - **役割重複**: 本来別スキルが担うべきタスクを吸収していないか（description の境界が曖昧になっていないか）
   - **過剰委譲**: 代替スキルが使われない理由が description 不備か品質問題か
   - **代替不在**: 実運用で他に選択肢がないだけなのか（この場合は崩壊ではなく健全な専門化）

#### 判断ガイド

- Unused でも 5D が全 Good → 休眠状態。削除より「使われない理由」を調査（description 改善で復活する可能性）
- Unused かつ 5D に Poor あり → retire 最有力候補
- Weekly かつ 5D に Poor あり → 品質改善を最優先
- **Dominant かつ 5D 全 Good** → 役割集中リスク。同ドメインの代替スキルを育成 or 明示的に「主スキル」と宣言する判断が必要
- **Dominant かつ 5D に Poor あり** → 品質に関わらず使われている = 代替不在の信号。最優先で改善
- **Dominant + Unused の共存** → Expert Collapse の決定的証拠。Unused スキル側の description/trigger 不備を真っ先に疑う

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

#### Optional: 3-arm evaluation（terse-control）

スキルの真の付加価値を「Just tell the model to be terse」の効果と分離して測定したい場合、3-arm モードを使う。JuliusBrussee/caveman リポジトリの評価手法より。

**3 つの条件**:

- **arm A (baseline)**: プロンプトそのまま、スキルなし
- **arm B (terse-control)**: 「Answer concisely. No preamble, no summary.」のみ追加、スキルなし
- **arm C (with-skill)**: 通常の with-skill 実行

**解釈**:

| 比較 | 意味 |
|------|------|
| arm C − arm A | スキル全体の効果（従来の 2-arm delta） |
| arm C − arm B | **スキル固有の付加価値**（terse 指示で代替不可能な部分） |
| arm B − arm A | terse 指示だけで得られる効果（ベースライン補正） |

2-arm delta が大きくても arm C − arm B が小さい場合、そのスキルは「単に簡潔に書けと指示すれば代替可能」を意味する。過大評価を防ぐ重要な補正。

**起動方法**（※現状 `run_eval.sh` の `--three-arm` は未実装。下記「最小実装」の手順で代替する）:

```bash
# 将来 run_eval.sh が --three-arm をサポートした際のインタフェース想定
bash ~/.claude/skills/skill-creator/scripts/run_eval.sh "{skill-name}" ".skill-eval/{skill-name}/evals/evals.json" --three-arm
```

**現時点での最小実装**（`run_eval.sh` が `--three-arm` をサポートしないため、以下を手動で実行する）:

1. `evals.json` の各 eval に `terse_control_prompt` フィールドを追加（省略時は元プロンプト + "Answer concisely. No preamble, no summary."）
2. eval を 3 回実行（A/B/C）し、結果を `arm_{a,b,c}.json` に分けて保存
3. `aggregate.py` が 3 アーム対応で `delta_skill_vs_terse` と `delta_terse_vs_baseline` を出力

**適用基準**: 出力スタイル系スキル（concise, persona, output-mode, rewrite 等）や「簡潔さ・文体で価値を出す」タイプのスキルに優先適用。複雑なワークフロー系（review, audit, epd 等）は 2-arm で十分。

**注意**: 3-arm は実行コスト 1.5 倍。Step 0.5 の Usage Tier で Dominant / Weekly に分類されたスキルから優先適用する。

**出典**: `docs/research/2026-04-11-caveman-genshijin-brevity-analysis.md`

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

## Full Trigger Conflict Scan

全スキルの Triggers フレーズを一括スキャンし、重複・曖昧性を検出する軽量モード。
A/B ベンチマーク不要で、description の静的解析のみで実行できる。

### 起動

`/skill-audit conflict-scan` または audit ワークフロー中に「衝突スキャンも実行」と指示。

### 手順

1. **全スキル description 収集** — `~/.claude/skills/*/SKILL.md` の frontmatter から `description` を全件抽出
2. **Trigger フレーズ抽出** — 各 description から `Triggers:` と `Do NOT use for:` のフレーズリストを分離
3. **重複検出** — 以下の3種の衝突を検出:
   - **完全一致**: 同一の Trigger フレーズが複数スキルに存在
   - **部分包含**: あるスキルの Trigger が別スキルの Trigger の部分文字列（例: "レビュー" vs "コードレビュー"）
   - **Do NOT use for 欠落**: Trigger が重複するペアで、片方に対応する `Do NOT use for` 排他が未定義
4. **テリトリーマップ生成** — スキル×ドメインのマトリクスを出力し、テリトリー境界を可視化
5. **レポート出力** — audit レポートの "Trigger Conflict Scan" セクションに結果を記載

### 出力テーブル

```markdown
## Trigger Conflict Scan

### 検出された衝突

| # | Type | Skill A | Skill B | 重複フレーズ | 推奨アクション |
|---|------|---------|---------|-------------|---------------|
| 1 | 完全一致 | review | simplify | "コードレビュー" | Do NOT use for を追記 |
| 2 | 部分包含 | spec | interview | "仕様" ⊂ "仕様書" | Trigger を具体化 |
| 3 | 排他欠落 | frontend-design | ui-ux-pro-max | "UI" | 双方に Do NOT use for を追記 |

### テリトリーマップ

| ドメイン | Primary Skill | Secondary | 境界明確？ |
|---------|--------------|-----------|-----------|
| コードレビュー | review | simplify | Yes |
| フロントエンド | frontend-design | ui-ux-pro-max | No → 要修正 |
```

### 判定基準

| 衝突タイプ | 深刻度 | アクション |
|-----------|--------|-----------|
| 完全一致 + 排他なし | **High** | 即座に description 修正が必要 |
| 部分包含 + 排他あり | **Low** | 監視のみ |
| 部分包含 + 排他なし | **Medium** | Do NOT use for 追記を推奨 |

## Gotchas Coverage Scan

スキル本文の `## Gotchas` セクション浸透率を監査し、`references/lessons-learned.md` からの昇格漏れを検出する。
A/B ベンチマークとは独立の軽量スキャン。`/skill-audit gotchas-scan` で単独実行、または通常の audit ワークフロー末尾で自動実行。

### 背景

Anthropic "Skills for Claude Code" (2026-04) は「Gotchas セクションが最も価値のある部分 — 時間とともに更新し続けるべき」と主張。
一方、現状の dotfiles では `references/lessons-learned.md` に 1 行 Gotcha が蓄積されていても、対応スキルの `## Gotchas` に昇格する経路がなく、
新規スキル作成時も `## Gotchas` の記述が義務化されていないため浸透率が低い。このスキャンはその乖離を定量化する。

### 手順

1. **Coverage 集計** — `~/.claude/skills/*/SKILL.md` を全件走査し、`## Gotchas` セクションの有無を数える:

   ```bash
   total=$(find ~/.claude/skills -name SKILL.md | wc -l)
   covered=$(grep -l '^## Gotchas' ~/.claude/skills/*/SKILL.md 2>/dev/null | wc -l)
   echo "Coverage: $covered / $total ($(( covered * 100 / total ))%)"
   ```

2. **Gotchas-less skill の抽出** — `## Gotchas` を持たないスキルを audit report に一覧化
3. **Promotion Backlog 検出** — `~/.claude/references/lessons-learned.md` の各行を走査し、スキル名への言及（例: `/review で`, `skill-creator の`）を抽出。該当スキルの `## Gotchas` に未反映なら「昇格候補」としてフラグ
4. **優先度付け** — 以下のいずれかに該当するスキルを「最優先追加対象」としてマーク:
   - Usage Tier が Dominant または Weekly（使用頻度が高い）
   - Guard 型（freeze, careful 等、失敗すると影響大）
   - Pipeline 型（review, absorb 等、複数フェーズで落ちる箇所が多い）

### 判定基準

| 状況 | アクション |
|------|-----------|
| Coverage < 40% | 全スキルに `## Gotchas` 追加を次回 audit 目標とする |
| 40% ≤ Coverage < 70% | Dominant/Weekly スキルから優先追加 |
| Coverage ≥ 70% | 個別のギャップ補填のみ |
| Promotion backlog ≥ 3 件/スキル | そのスキルを次回改善最優先 |

### 出力テーブル

```markdown
## Gotchas Coverage Scan

### サマリ

- 全スキル: 92 件
- `## Gotchas` あり: 23 件 (25%)
- Promotion backlog (lessons-learned 未反映): 14 件

### Gotchas 未整備スキル（Dominant/Weekly のみ）

| Skill | Usage Tier | Archetype | 推奨 Gotchas ソース |
|-------|-----------|-----------|--------------------|
| review | Weekly | Pipeline | lessons-learned: "レビュー中 Edit/Write 禁止" |
| absorb | Weekly | Pipeline | lessons-learned: "Already=存在≠品質保証" |

### Promotion Backlog（lessons-learned → ## Gotchas 昇格候補）

| lessons-learned 行 | 対象スキル | 既存 Gotchas に含まれるか |
|-------------------|-----------|-------------------------|
| "git commit --no-verify は絶対禁止" | commit | No → 追加推奨 |
| "hook 正規表現で \\b を使うと日本語で誤動作" | hook-debugger | Yes |
```

### 昇格ワークフロー（ユーザー向けガイド）

lessons-learned.md の 1 行 Gotcha をスキルの `## Gotchas` に昇格させる標準フロー:

1. **引用**: lessons-learned.md の該当行を `## Gotchas` にコピー
2. **文脈化**: 「なぜそのスキルで発生するか」を 1 行追加
3. **対処**: 回避策を 1 行で明示（lessons-learned に既にあるはず）
4. **verify 行の残存**: `references/lessons-learned.md` 側は削除せず残す（他スキルが参照する可能性があるため）

> **原則**: lessons-learned = 全体台帳、`## Gotchas` = スキル固有の実行時ガイド。両方に残して良い（単一責任ではなく、視点違いの冗長）

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

## Agent Consolidation Scan

エージェント数の肥大化を防ぎ、統合候補を検出する。`/skill-audit consolidation` で単独実行、または通常の audit ワークフロー末尾で自動実行。

### 背景

モデル能力の向上に伴い、1エージェントが複数専門をカバーできるようになる。30+エージェントの管理オーバーヘッドを定期的に評価し、skill modes 化（1エージェント+複数モード）への統合判断材料を提供する。

### 手順

1. **エージェント一覧収集** — `~/.claude/agents/*.md` の frontmatter から name, description, tools を全件抽出
2. **ドメイン重複検出** — description のキーワードが重複するエージェントペアを抽出（閾値: 3語以上の共通キーワード）
3. **使用頻度推定** — `git log --oneline -100` でエージェント名の出現頻度を計測。直近100コミットで起動ゼロのエージェントをフラグ
4. **統合候補判定** — 以下のいずれかに該当するペアを統合候補として提示:
   - 同一 tools セットを持ち、ドメインが隣接
   - 片方の機能が他方の機能の部分集合
   - 両方とも使用頻度が低い（直近100コミットで各5回未満）
5. **Orthogonality Check (出力種別の直交性)** — description から各エージェントの**主な出力種別**を推定し (`review-report` / `observation-report` / `plan` / `spec` / `implementation-patch` / `research-summary` など)、以下をフラグする:
   - 同一出力種別のエージェントが **3 体以上**存在 → 役割の直交性が低い。主エージェント + skill mode 化を検討
   - ドメインが異なっても出力種別が同じペア → 統合判定の補助シグナルとして提示（ドメイン重複とは独立に評価）

> **Orthogonality の原則**: 「エージェントの役割空間は出力種別 × ドメインの 2 軸で張る。同じセルに複数エージェントが居ると Expert Collapse または Role Confusion を起こしやすい」(2025-2026 マルチエージェント粒度研究より)

### 出力テーブル

```markdown
## Agent Consolidation Scan

| # | Agent A | Agent B | 重複理由 | 推奨アクション |
|---|---------|---------|---------|---------------|
| 1 | code-reviewer | golang-reviewer | Go レビューが code-reviewer の skill mode で可能 | 統合検討 |
| 2 | silent-failure-hunter | — | 直近100コミットで起動0回 | 退役 or 統合検討 |
```

### 判定基準

| パターン | アクション |
|---------|-----------|
| ドメイン重複 + 同一 tools | 統合を強く推奨 |
| 使用頻度ゼロ（100コミット） | 退役候補としてフラグ（即削除しない） |
| 部分集合関係 | 親エージェントの skill mode 化を提案 |

## Gotchas

- **統計的検出力不足**: 2-3回の eval では有意差を検出できない。最低5回、理想は10回以上
- **cherry-pick 結果**: 成功ケースだけ報告するバイアス。失敗ケースも含めた全結果を評価
- **description conflict 誤検知**: 似た description でも対象ドメインが異なれば競合しない。Do NOT use for を確認
- **退役判断の早まり**: 使用頻度が低くても特定シナリオで重要なスキルがある。頻度だけで判断しない

## Skill Assets

- `templates/audit-report.md` — Audit report template (date, summary table, description conflicts, recommendations)
