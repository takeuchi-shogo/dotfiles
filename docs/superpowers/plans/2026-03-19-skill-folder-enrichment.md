# Skill Folder Enrichment Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 57スキルを5つの enrichment archetype に基づき、templates/references/scripts を追加してフォルダ型リッチスキルに強化する。

**Architecture:** Tier 1→2→3 の優先度順で実装。各スキルに新規ファイルを追加し、SKILL.md に参照ポインタを追記。既存ファイルは変更しない（並存）。

**Tech Stack:** Markdown templates, POSIX sh scripts, jq

**Spec:** `docs/superpowers/specs/2026-03-19-skill-folder-enrichment-design.md`

**Base path:** `.config/claude/skills/` (以下すべてこのパスからの相対)

---

## Task 1: review — Pipeline enrichment

**Files:**
- Create: `review/templates/synthesis-report.md`
- Create: `review/scripts/extract-diff-stats.sh`
- Modify: `review/SKILL.md` (末尾に参照ポインタ追記)

- [ ] **Step 1: Create templates directory and synthesis report template**

```bash
mkdir -p .config/claude/skills/review/scripts
```

Create `review/templates/synthesis-report.md`:

```markdown
# Review Synthesis Report

## Summary

| Metric | Value |
|--------|-------|
| Files reviewed | {file_count} |
| Total findings | {finding_count} |
| Reviewers | {reviewer_list} |
| Agreement Rate | {agreement_rate}% |
| Verdict | {PASS / NEEDS_FIX / BLOCK} |

## Critical

| # | File | Line | Finding | Reviewer | Confidence |
|---|------|------|---------|----------|------------|
| 1 | {file} | {line} | {finding} | {reviewer} | {confidence} |

## Important

| # | File | Line | Finding | Reviewer | Confidence |
|---|------|------|---------|----------|------------|
| 1 | {file} | {line} | {finding} | {reviewer} | {confidence} |

## Watch

| # | File | Line | Finding | Reviewer | Confidence |
|---|------|------|---------|----------|------------|
| 1 | {file} | {line} | {finding} | {reviewer} | {confidence} |

## Conflicts

> 同一箇所で矛盾する指摘がある場合にのみ記載

| File | Line | Reviewer A | Reviewer B | Details |
|------|------|-----------|-----------|---------|
| {file} | {line} | {reviewer_a}: {opinion_a} | {reviewer_b}: {opinion_b} | {context} |

## Reviewer Breakdown

| Reviewer | Findings | Avg Confidence |
|----------|----------|----------------|
| {reviewer} | {count} | {avg_confidence} |
```

- [ ] **Step 2: Create extract-diff-stats script**

Create `review/scripts/extract-diff-stats.sh`:

```bash
#!/bin/sh
# Extract structured diff statistics for review scaling decisions
# Usage: extract-diff-stats.sh [ref]
# Output: JSON with line counts, file counts, and language breakdown

set -e

REF="${1:-HEAD}"

# Total insertions/deletions
STAT=$(git diff --shortstat "$REF" 2>/dev/null || echo "0 files changed")
FILES=$(echo "$STAT" | grep -oE '[0-9]+ file' | grep -oE '[0-9]+' || echo 0)
INSERTIONS=$(echo "$STAT" | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+' || echo 0)
DELETIONS=$(echo "$STAT" | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+' || echo 0)
TOTAL=$((INSERTIONS + DELETIONS))

# Language breakdown
LANGS=$(git diff --name-only "$REF" 2>/dev/null | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -5)
LANG_JSON=$(echo "$LANGS" | awk '{printf "{\"ext\":\".%s\",\"files\":%d},", $2, $1}' | sed 's/,$//')

cat <<ENDJSON
{
  "ref": "$REF",
  "files_changed": $FILES,
  "insertions": $INSERTIONS,
  "deletions": $DELETIONS,
  "total_lines": $TOTAL,
  "languages": [$LANG_JSON],
  "scale": "$(
    if [ "$TOTAL" -le 10 ]; then echo "skip"
    elif [ "$TOTAL" -le 30 ]; then echo "basic"
    elif [ "$TOTAL" -le 50 ]; then echo "standard"
    elif [ "$TOTAL" -le 200 ]; then echo "thorough"
    else echo "comprehensive"
    fi
  )"
}
ENDJSON
```

```bash
chmod +x .config/claude/skills/review/scripts/extract-diff-stats.sh
```

- [ ] **Step 3: Add reference pointers to review/SKILL.md**

Append to end of `review/SKILL.md`:

```markdown

## Skill Assets

- 統合レポートテンプレート: `templates/synthesis-report.md`
- diff 統計抽出: `scripts/extract-diff-stats.sh` — `sh scripts/extract-diff-stats.sh [ref]` で JSON 出力
```

- [ ] **Step 4: Verify**

```bash
test -f .config/claude/skills/review/templates/synthesis-report.md && echo "OK: synthesis-report"
test -x .config/claude/skills/review/scripts/extract-diff-stats.sh && echo "OK: extract-diff-stats"
grep -q "Skill Assets" .config/claude/skills/review/SKILL.md && echo "OK: SKILL.md pointer"
```

- [ ] **Step 5: Commit**

```bash
git add .config/claude/skills/review/templates/synthesis-report.md \
       .config/claude/skills/review/scripts/extract-diff-stats.sh \
       .config/claude/skills/review/SKILL.md
git commit -m "✨ feat(skills): enrich review with synthesis template and diff stats script"
```

---

## Task 2: research — Pipeline enrichment

**Files:**
- Create: `research/templates/subtask-prompt.md`
- Create: `research/references/model-assignment-guide.md`
- Modify: `research/SKILL.md` (末尾に参照ポインタ追記)

- [ ] **Step 1: Create subtask prompt template**

Create `research/templates/subtask-prompt.md`:

```markdown
# Subtask: {subtask_name}

## Context

You are a subagent conducting research on behalf of a parent agent.
Your findings will be aggregated with other subagents' results.

**Research topic:** {parent_topic}
**Your focus area:** {focus_area}

## Instructions

{specific_instructions}

## Output Format

### Findings

1. **{finding_title}**
   - Source: {source_url_or_reference}
   - Confidence: {HIGH/MEDIUM/LOW}
   - Details: {concise_description}

### Key Takeaways

- {takeaway_1}
- {takeaway_2}

### Gaps & Unknowns

- {what_could_not_be_determined}
```

- [ ] **Step 2: Create model assignment guide**

Create `research/references/model-assignment-guide.md`:

```markdown
# Model Assignment Guide

サブタスクの性質に応じてモデルを自動割り当てする基準。

## Assignment Matrix

| サブタスク性質 | 推奨モデル | 理由 |
|---------------|-----------|------|
| 外部リサーチ（Web検索、最新情報） | Gemini CLI | Google Search grounding、1Mコンテキスト |
| 深い推論・設計分析 | Codex CLI (gpt-5.4) | reasoning effort: high で深い分析 |
| コードベース分析 | claude -p | ローカルファイル直接アクセス |
| 論文要約・文献調査 | Gemini CLI | 1Mコンテキストで長文処理 |
| 比較分析・トレードオフ | Codex CLI | 構造化推論が得意 |
| デフォルト（汎用） | claude -p | 最も安定・高速 |

## Model Characteristics

### Gemini CLI
- **強み**: 1M コンテキスト、Google Search grounding、マルチモーダル
- **弱み**: 過度に楽観的な傾向、指示の細部を見落とす場合あり
- **コマンド例**: `gemini -p "Research topic" --grounding`

### Codex CLI (gpt-5.4)
- **強み**: 深い推論、構造化分析、reasoning effort 調整可能
- **弱み**: 外部検索なし、ローカルファイルアクセスが限定的
- **コマンド例**: `codex exec "Analyze..." --reasoning-effort high`

### claude -p (headless)
- **強み**: ローカルファイル完全アクセス、ツール使用、安定性
- **弱み**: 200K コンテキスト制限
- **コマンド例**: `claude -p "Analyze..." --allowedTools Read,Grep,Glob`

## Language Protocol

- CLI への指示は **英語** で記述する
- ユーザーへの最終レポートは **日本語** で記述する
```

- [ ] **Step 3: Add reference pointers to research/SKILL.md**

Append to end of `research/SKILL.md`:

```markdown

## Skill Assets

- サブタスクプロンプト: `templates/subtask-prompt.md`
- モデル割り当て基準: `references/model-assignment-guide.md`
- レポートテンプレート: `templates/research-report-template.md` (既存)
```

- [ ] **Step 4: Verify and commit**

```bash
test -f .config/claude/skills/research/templates/subtask-prompt.md && echo "OK"
test -f .config/claude/skills/research/references/model-assignment-guide.md && echo "OK"
git add .config/claude/skills/research/ && git commit -m "✨ feat(skills): enrich research with subtask prompt and model guide"
```

---

## Task 3: improve — Pipeline enrichment

**Files:**
- Create: `improve/templates/improvement-report.md`
- Create: `improve/templates/experiment-log.md`
- Create: `improve/references/analysis-categories.md`
- Modify: `improve/SKILL.md` (末尾に参照ポインタ追記)

- [ ] **Step 1: Create directories**

```bash
mkdir -p .config/claude/skills/improve/templates .config/claude/skills/improve/references
```

- [ ] **Step 2: Create improvement report template**

Create `improve/templates/improvement-report.md`:

```markdown
# AutoEvolve Improvement Report — {date}

## Data Overview

| Data Source | Count | Status |
|------------|-------|--------|
| errors.jsonl | {n} | {OK/empty} |
| quality.jsonl | {n} | {OK/empty} |
| patterns.jsonl | {n} | {OK/empty} |
| session-metrics.jsonl | {n} | {OK/empty} |

## Experiment Status

| ID | Status | Target | Result |
|----|--------|--------|--------|
| {exp_id} | {pending/merged/measured} | {target} | {outcome} |

## Analysis Summary

### Errors — Top Patterns
| Pattern | Count | Severity | Proposed Fix |
|---------|-------|----------|-------------|
| {pattern} | {n} | {HIGH/MED/LOW} | {fix} |

### Quality — Violations
| Rule | Violations | Trend |
|------|-----------|-------|
| {rule} | {n} | {↑/↓/→} |

### Agents — Efficiency
| Agent | Invocations | Avg Duration | Issues |
|-------|------------|-------------|--------|
| {agent} | {n} | {ms} | {issues} |

### Skills — Health
| Skill | Score | Trend | Action |
|-------|-------|-------|--------|
| {skill} | {score} | {↑/↓/→} | {action} |

## Proposals

| # | Hypothesis | Target File | Risk | Priority |
|---|-----------|------------|------|----------|
| 1 | {hypothesis} | {file} | {LOW/MED/HIGH} | {P1/P2/P3} |

## Next Cycle Notes

- {carry_forward_items}
```

- [ ] **Step 3: Create experiment log template**

Create `improve/templates/experiment-log.md`:

```markdown
# Experiment: {exp_id}

## Metadata

| Field | Value |
|-------|-------|
| Date | {YYYY-MM-DD} |
| Target | {skill/agent/rule name} |
| Hypothesis | {one_sentence_hypothesis} |
| Branch | autoevolve/{topic} |

## Baseline

| Metric | Value |
|--------|-------|
| {metric_name} | {baseline_value} |

## Variant

| Change | Details |
|--------|---------|
| File | {file_path} |
| Diff summary | {what_changed} |

## Results

| Metric | Baseline | Variant | Delta |
|--------|----------|---------|-------|
| {metric} | {before} | {after} | {delta} |

## Verdict

**{KEEP / REVERT / PENDING_REVIEW}**

Reason: {justification}
```

- [ ] **Step 4: Create analysis categories reference**

Create `improve/references/analysis-categories.md`:

```markdown
# Analysis Categories — 判断基準

## errors（エラーパターン分析）

**データソース**: `learnings/errors.jsonl`
**判断基準**:
- 同一エラーが 3回以上 → パターンとして認定
- root_cause フィールドがある場合、根本原因でグルーピング
- 環境固有（PATH, バージョン等）vs コード固有を分類

**改善アクション例**:
- hook 追加で事前検出
- rules/ にパターン追加
- エージェント定義に Symptom-Cause-Fix テーブル追加

## quality（品質違反分析）

**データソース**: `learnings/quality.jsonl`
**判断基準**:
- 違反ルール別に集計、上位5つを重点分析
- トレンド（増加/減少/横ばい）を直近30日で判定
- 新規違反 vs 再発を区別

**改善アクション例**:
- チェックリスト強化
- pre-commit hook でブロック
- Bad Example をルールに併記

## agents（エージェント効率分析）

**データソース**: `metrics/session-metrics.jsonl`
**判断基準**:
- 起動回数 × 成功率でランキング
- 平均所要時間が外れ値のエージェントを検出
- Knowledge Embedding Ratio < 50% → 改善候補

**改善アクション例**:
- エージェント定義にドメイン知識追加
- ルーティング条件の調整
- 不要エージェントの統廃合

## skills（スキル健全性分析）

**データソース**: `learnings/skill-executions.jsonl`, `skill-benchmarks.jsonl`
**判断基準**:
- failure_count >= 3 → degraded
- ベンチマークスコア < 0.8 → needs_improvement
- 30日以上ベンチマーク未実施 → stale

**改善アクション例**:
- SKILL.md のリライト
- テンプレート/references の追加
- --evolve ループで反復改善

## environment（環境設計分析）

**データソース**: 全カテゴリ横断
**判断基準**: Harness Audit Framework の4診断質問
1. アクセス不能な情報はあるか
2. 欠落したフィードバックループはあるか
3. コンテキスト汚染はあるか
4. 機械的に強制すべき制約はあるか

**起動条件**: errors.jsonl 20件以上 かつ 前回分析から7日以上経過
```

- [ ] **Step 5: Add reference pointers and commit**

Append to `improve/SKILL.md`:

```markdown

## Skill Assets

- 改善レポートテンプレート: `templates/improvement-report.md`
- 実験ログテンプレート: `templates/experiment-log.md`
- 分析カテゴリ判断基準: `references/analysis-categories.md`
```

```bash
git add .config/claude/skills/improve/ && git commit -m "✨ feat(skills): enrich improve with report templates and analysis guide"
```

---

## Task 4: check-health — Pipeline enrichment

**Files:**
- Create: `check-health/templates/health-report.md`
- Create: `check-health/references/staleness-criteria.md`
- Modify: `check-health/SKILL.md`

- [ ] **Step 1: Create directories and health report template**

```bash
mkdir -p .config/claude/skills/check-health/templates .config/claude/skills/check-health/references
```

Create `check-health/templates/health-report.md`:

```markdown
# Health Check Report — {date}

## Overall Status: {HEALTHY / WARNING / CRITICAL}

## Code-Document Drift

| File | Last Code Change | Last Doc Update | Drift (days) | Status |
|------|-----------------|-----------------|-------------|--------|
| {file} | {code_date} | {doc_date} | {days} | {OK/STALE/DRIFT} |

## Document Staleness

| Document | Last Updated | Age (days) | Status |
|----------|-------------|-----------|--------|
| {doc} | {date} | {days} | {OK/STALE} |

## Broken References

| Source File | Line | Reference | Status |
|------------|------|-----------|--------|
| {file} | {line} | {ref_path} | {BROKEN/MOVED} |

## Skill Benchmark Staleness

| Skill | Last Benchmark | Age (days) | Status |
|-------|---------------|-----------|--------|
| {skill} | {date} | {days} | {OK/STALE/NEVER} |

## Undocumented Subsystems

| Module | Path | Recommendation |
|--------|------|---------------|
| {module} | {path} | {action} |

## Actions Required

- [ ] {action_item_1}
- [ ] {action_item_2}
```

- [ ] **Step 2: Create staleness criteria reference**

Create `check-health/references/staleness-criteria.md`:

```markdown
# Staleness Criteria — 鮮度判定基準

## Document Staleness

| 閾値 | 判定 | アクション |
|------|------|-----------|
| 0-30日 | OK | なし |
| 31-60日 | STALE | レビュー推奨 |
| 61日以上 | CRITICAL | 即座に更新 or アーカイブ |

## Code-Document Drift

| 条件 | 判定 |
|------|------|
| コード変更後7日以内にドキュメント更新 | OK |
| コード変更後7-14日 | WARNING |
| コード変更後14日以上 | DRIFT |

## Skill Benchmark Staleness

| 閾値 | 判定 |
|------|------|
| 0-30日 | OK |
| 31-60日 | STALE → `/skill-audit` 推奨 |
| 未実施 | NEVER → `/skill-audit` 必須 |

## Reference Integrity

参照先ファイルが存在しない場合は **即 BROKEN** と判定。
ファイルが移動された場合は **MOVED** と判定し、新パスを提示。
```

- [ ] **Step 3: Add pointers and commit**

Append to `check-health/SKILL.md`:

```markdown

## Skill Assets

- レポートテンプレート: `templates/health-report.md`
- 鮮度判定基準: `references/staleness-criteria.md`
```

```bash
git add .config/claude/skills/check-health/ && git commit -m "✨ feat(skills): enrich check-health with report template and staleness criteria"
```

---

## Task 5: absorb — Pipeline enrichment

**Files:**
- Create: `absorb/templates/analysis-report.md`
- Create: `absorb/templates/integration-plan.md`
- Create: `absorb/references/triage-criteria.md`
- Modify: `absorb/SKILL.md`

- [ ] **Step 1: Create directories**

```bash
mkdir -p .config/claude/skills/absorb/templates .config/claude/skills/absorb/references
```

- [ ] **Step 2: Create analysis report template**

Create `absorb/templates/analysis-report.md`:

```markdown
---
source: "{URL or title}"
date: {YYYY-MM-DD}
status: {analyzed | integrated | skipped}
---

## Source Summary

**主張**: {core_claim_1_to_3_sentences}

**手法**:
- {technique_1}
- {technique_2}

**根拠**: {evidence_or_data}

**前提条件**: {context_where_valid}

## Gap Analysis

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | {technique} | {Already/Partial/Gap/N/A} | {details} |

## Integration Decisions

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1 | {item} | {採用/スキップ} | {reason} |

## Plan

### Task 1: {task_name}
- **Files**: {file_paths}
- **Changes**: {what_to_do}
- **Size**: {S/M/L}
```

- [ ] **Step 3: Create integration plan template**

Create `absorb/templates/integration-plan.md`:

```markdown
# Integration Plan: {source_title}

## Overview

| Field | Value |
|-------|-------|
| Source | {url_or_title} |
| Analysis | `docs/research/{analysis_file}` |
| Total Tasks | {n} |
| Estimated Size | {S/M/L} |

## Tasks

### Task 1: {task_name}

| Field | Value |
|-------|-------|
| Files | {file_list} |
| Dependencies | {deps_or_none} |
| Size | {S/M/L} |

**Changes:**
- {change_description}

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|-----------|
| {risk} | {impact} | {mitigation} |

## Execution

| Size | Approach |
|------|----------|
| S | その場で実行 |
| M | ユーザー確認後、同一セッション |
| L | docs/plans/ に保存 → 新セッションで /rpi |
```

- [ ] **Step 4: Create triage criteria reference**

Create `absorb/references/triage-criteria.md`:

```markdown
# Triage Criteria — 知見の取捨選択基準

## 判定マトリクス

|  | 適用コスト 低 | 適用コスト 高 |
|--|-------------|-------------|
| **効果 高** | 即採用 | 検討（ROI評価） |
| **効果 低** | 後回し | スキップ |

## 適用コスト評価

| コストレベル | 基準 |
|-------------|------|
| 低 | 1ファイル変更、既存パターンに沿う |
| 中 | 2-5ファイル、新パターン導入 |
| 高 | 6ファイル超、アーキテクチャ変更、hook追加 |

## 効果評価

| 効果レベル | 基準 |
|-----------|------|
| 高 | 毎日の作業に影響、エラー防止、時間短縮 |
| 中 | 週1回程度の作業に影響 |
| 低 | 稀なケースにのみ有効 |

## フィルタリングルール

1. **Already → スキップ**: 既に実装済みは取り込まない
2. **N/A → スキップ**: 前提条件が合わないものは取り込まない
3. **1記事から最大5タスク**: 消化不良防止
4. **前提条件チェック**: 記事の前提と当セットアップの文脈が合うか確認
5. **既存の仕組みとの衝突チェック**: 新手法が既存パターンと矛盾しないか
```

- [ ] **Step 5: Add pointers and commit**

Append to `absorb/SKILL.md`:

```markdown

## Skill Assets

- 分析レポートテンプレート: `templates/analysis-report.md`
- 統合プランテンプレート: `templates/integration-plan.md`
- 取捨選択基準: `references/triage-criteria.md`
```

```bash
git add .config/claude/skills/absorb/ && git commit -m "✨ feat(skills): enrich absorb with analysis templates and triage criteria"
```

---

## Task 6: daily-report — Generator enrichment

**Files:**
- Create: `daily-report/scripts/collect-session-stats.sh`
- Modify: `daily-report/SKILL.md`

- [ ] **Step 1: Create script**

```bash
mkdir -p .config/claude/skills/daily-report/scripts
```

Create `daily-report/scripts/collect-session-stats.sh`:

```bash
#!/bin/sh
# Collect session statistics for daily report generation
# Usage: collect-session-stats.sh [YYYY-MM-DD]
# Output: JSON summary of the day's development activity

set -e

DATE="${1:-$(date +%Y-%m-%d)}"
PROJECTS_DIR="$HOME/.claude/projects"

echo "{"
echo "  \"date\": \"$DATE\","

# Git commits for the day
COMMITS=$(git log --since="$DATE 00:00:00" --until="$DATE 23:59:59" --oneline 2>/dev/null | wc -l | tr -d ' ')
echo "  \"commits\": $COMMITS,"

# Files changed
FILES_CHANGED=$(git log --since="$DATE 00:00:00" --until="$DATE 23:59:59" --name-only --pretty=format: 2>/dev/null | sort -u | grep -c . || echo 0)
echo "  \"files_changed\": $FILES_CHANGED,"

# Lines added/removed
STATS=$(git log --since="$DATE 00:00:00" --until="$DATE 23:59:59" --shortstat --pretty=format: 2>/dev/null | awk '
  /insertion/ { ins += $4 }
  /deletion/  { del += $6 }
  END { printf "%d %d", ins+0, del+0 }
')
INSERTIONS=$(echo "$STATS" | cut -d' ' -f1)
DELETIONS=$(echo "$STATS" | cut -d' ' -f2)
echo "  \"insertions\": $INSERTIONS,"
echo "  \"deletions\": $DELETIONS,"

# Session count (approximate from projects dir)
SESSION_COUNT=0
if [ -d "$PROJECTS_DIR" ]; then
  SESSION_COUNT=$(find "$PROJECTS_DIR" -name "*.jsonl" -newer /tmp/.daily-report-marker 2>/dev/null | wc -l | tr -d ' ' || echo 0)
fi
echo "  \"sessions\": $SESSION_COUNT,"

# Current branch
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
echo "  \"branch\": \"$BRANCH\""

echo "}"
```

```bash
chmod +x .config/claude/skills/daily-report/scripts/collect-session-stats.sh
```

- [ ] **Step 2: Add pointer and commit**

Append to `daily-report/SKILL.md`:

```markdown

## Skill Assets

- セッション統計収集: `scripts/collect-session-stats.sh` — `sh scripts/collect-session-stats.sh [YYYY-MM-DD]`
- 日報テンプレート: `templates/daily-report-template.md` (既存)
```

```bash
git add .config/claude/skills/daily-report/ && git commit -m "✨ feat(skills): enrich daily-report with session stats script"
```

---

## Task 7: eureka — Generator enrichment

**Files:**
- Create: `eureka/templates/breakthrough-template.md`
- Modify: `eureka/SKILL.md`

- [ ] **Step 1: Create template**

```bash
mkdir -p .config/claude/skills/eureka/templates
```

Create `eureka/templates/breakthrough-template.md`:

```markdown
---
date: {YYYY-MM-DD}
tags: [breakthrough, {domain}]
impact: {LOW/MEDIUM/HIGH/CRITICAL}
---

# {breakthrough_title}

## Problem

{what_was_the_problem_or_challenge}

## Insight

{the_key_realization_or_discovery}

## Implementation

{how_it_was_applied}

```{language}
{code_snippet_if_applicable}
```

## Metrics

| Before | After | Improvement |
|--------|-------|-------------|
| {before} | {after} | {delta} |

## Reuse Pattern

**When to apply:** {conditions_where_this_insight_is_useful}

**How to apply:**
1. {step_1}
2. {step_2}

**Anti-pattern:** {what_NOT_to_do}
```

- [ ] **Step 2: Add pointer and commit**

Append to `eureka/SKILL.md`:

```markdown

## Skill Assets

- 発見記録テンプレート: `templates/breakthrough-template.md`
```

```bash
git add .config/claude/skills/eureka/ && git commit -m "✨ feat(skills): enrich eureka with breakthrough template"
```

---

## Task 8: Tier 2 — Pipeline skills (5 skills)

**Skills:** continuous-learning, epd, validate, spike, interviewing-issues

All files follow the same pattern: create templates/ and/or references/ directory, add content, append pointer to SKILL.md.

- [ ] **Step 1: continuous-learning (2 files)**

Create `continuous-learning/templates/pattern-record.md`:

```markdown
---
type: {correction/convention/debug-pattern/anti-pattern}
detected: {YYYY-MM-DD}
source: {user_feedback/repeated_fix/debugging}
---

# {pattern_name}

## Rule

{the_rule_or_pattern}

## Why

{reason_this_matters}

## How to Apply

{when_and_where_to_use_this}

## Evidence

- {occurrence_1}
- {occurrence_2}
```

Create `continuous-learning/references/detection-signals.md`:

```markdown
# Pattern Detection Signals

| Signal Type | Detection Method | Example |
|------------|-----------------|---------|
| User correction | "no not that", "instead do", "don't" | "don't mock the database" |
| Repeated fix | Same fix applied 2+ times in session | Identical Edit patterns |
| New convention | Consistent pattern in 3+ files | Import ordering, naming |
| Debug insight | Root cause found after investigation | "The issue was actually..." |
| Anti-pattern | User explicitly flags bad practice | "never do X because Y" |

## Classification Rules

1. **correction** → User explicitly corrects behavior
2. **convention** → Consistent pattern observed in codebase
3. **debug-pattern** → Reusable debugging technique
4. **anti-pattern** → Explicitly flagged bad practice

## Duplicate Detection

Before saving, check existing memories for:
- Same rule with different wording → update existing
- Contradicting rule → flag for user resolution
- Already codified in CLAUDE.md/rules → skip
```

- [ ] **Step 2: epd (2 files)**

Create `epd/templates/phase-transition.md`:

```markdown
# EPD Phase Transition Checklist

## Phase {N} → Phase {N+1}: {from_name} → {to_name}

### Exit Criteria (Phase {N})

- [ ] {criterion_1}
- [ ] {criterion_2}

### Entry Criteria (Phase {N+1})

- [ ] {criterion_1}
- [ ] {criterion_2}

### Artifacts

| Artifact | Status | Path |
|----------|--------|------|
| {artifact} | {created/updated/N/A} | {path} |

### Decision

- [ ] Proceed to Phase {N+1}
- [ ] Return to Phase {N} (reason: ___)
- [ ] Abort (reason: ___)
```

Create `epd/references/workflow-decision.md`:

```markdown
# Workflow Decision Guide

## EPD vs RPI vs Spike

| Situation | Recommended | Reason |
|-----------|------------|--------|
| 仕様が不確実、探索が必要 | `/epd` | Spec→Spike→Validate の探索サイクルが必要 |
| 仕様が明確、実装のみ | `/rpi` | Research→Plan→Implement で直行 |
| 素早い技術検証 | `/spike` | worktree で隔離、テスト/lint 不要 |
| バグ修正 | 直接修正 or `/rpi` | 既知の問題なら探索不要 |
| 1行変更 | 直接修正 | ワークフロー不要 |

## EPD Phase Overview

| Phase | 名前 | 目的 | 成果物 |
|-------|------|------|--------|
| 1 | Spec | 仕様定義 | `docs/specs/{feature}.prompt.md` |
| 2 | Spike | 技術検証 | プロトタイプ + spike-report |
| 3 | Refine | 仕様修正 | 更新された spec |
| 4 | Decide | Go/No-Go | 判断記録 |
| 5 | Build | 実装 | プロダクションコード |
| 6 | Review | 品質確認 | レビューレポート |
| 7 | Ship | デリバリー | PR or merge |
```

- [ ] **Step 3: validate (2 files)**

Create `validate/templates/validation-report.md`:

```markdown
# Validation Report: {feature_name}

**Spec:** `{spec_file_path}`
**Date:** {YYYY-MM-DD}

## Results

| # | Acceptance Criteria | Status | Evidence |
|---|-------------------|--------|----------|
| 1 | {criterion} | {PASS/FAIL/PARTIAL} | {evidence} |

## Scope Check

| Check | Status |
|-------|--------|
| Spec にない機能の追加 | {NONE/FOUND: details} |
| 未実装の acceptance criteria | {NONE/FOUND: details} |

## Verdict

**{VALIDATED / NEEDS_WORK / BLOCKED}**

## Actions Required

- [ ] {action_if_any}
```

Create `validate/references/criteria-extraction.md`:

```markdown
# Acceptance Criteria Extraction Guide

## Supported Formats

| Format | Pattern | Example |
|--------|---------|---------|
| YAML frontmatter | `acceptance_criteria:` list | spec の frontmatter |
| Markdown checklist | `- [ ]` under "Acceptance Criteria" | spec 本文 |
| Given/When/Then | `Given ... When ... Then ...` | BDD 形式 |
| Numbered list | `1. ` under criteria heading | 番号付きリスト |

## Extraction Steps

1. spec ファイルを Read で読み込む
2. `acceptance_criteria` セクションを探す
3. 上記フォーマットのいずれかでパース
4. 各 criteria を独立した検証項目として扱う

## Verification Methods

| Criteria Type | Verification |
|--------------|-------------|
| UI/UX behavior | webapp-testing / ui-observer で確認 |
| API response | Bash で curl/httpie 実行 |
| Data integrity | DB query or file check |
| Performance | benchmark 実行 |
| Error handling | 異常系テスト実行 |
```

- [ ] **Step 4: spike (1 file)**

Create `spike/templates/spike-report.md`:

```markdown
# Spike Report: {feature_name}

## Metadata

| Field | Value |
|-------|-------|
| Date | {YYYY-MM-DD} |
| Duration | {time_spent} |
| Spec | `{spec_path}` |
| Worktree | `{worktree_path}` |

## Hypothesis

{what_we_wanted_to_learn}

## Approach

{what_we_tried}

## Findings

### What Worked
- {finding_1}

### What Didn't Work
- {finding_1}

### Surprises
- {finding_1}

## Validation Against Spec

| Acceptance Criteria | Feasible? | Notes |
|-------------------|-----------|-------|
| {criterion} | {YES/NO/PARTIAL} | {notes} |

## Recommendation

**{PROCEED / PIVOT / ABANDON}**

Reason: {justification}

## Learnings to Preserve

- {learning_for_implementation_phase}
```

- [ ] **Step 5: interviewing-issues (2 files)**

Create `interviewing-issues/templates/structured-spec.md`:

```markdown
# Issue Specification: {issue_title}

**Source:** {github_issue_url}
**Date:** {YYYY-MM-DD}

## Problem Statement

{clear_description_of_the_problem}

## Acceptance Criteria

### Given/When/Then

1. **Given** {precondition}
   **When** {action}
   **Then** {expected_result}

## Scope

### In Scope
- {item_1}

### Out of Scope
- {item_1}

## Technical Notes

- {implementation_consideration}

## Priority

| Factor | Value |
|--------|-------|
| Impact | {HIGH/MEDIUM/LOW} |
| Urgency | {HIGH/MEDIUM/LOW} |
| Complexity | {S/M/L} |
```

Create `interviewing-issues/references/question-patterns.md`:

```markdown
# Question Patterns by Category

## Scope (スコープ確認)
- "この Issue の影響範囲はどこまでですか？"
- "関連するコンポーネント/モジュールは？"
- "今回のスコープに含めないものは？"

## Requirements (要件)
- "期待する動作を具体的に教えてください"
- "エラー時の挙動はどうあるべきですか？"
- "パフォーマンス要件はありますか？"

## Edge Cases (エッジケース)
- "この操作を連続して行うとどうなりますか？"
- "入力が空/null の場合は？"
- "権限がないユーザーの場合は？"

## Priority (優先度)
- "この Issue のビジネスインパクトは？"
- "いつまでに解決が必要ですか？"
- "ワークアラウンドはありますか？"

## Constraints (制約)
- "技術的な制約はありますか？"
- "互換性の要件は？"
- "テスト環境の制約は？"
```

- [ ] **Step 6: Add pointers to all 5 SKILL.md files and commit**

Each SKILL.md gets a `## Skill Assets` section appended. Then:

```bash
git add .config/claude/skills/continuous-learning/ \
       .config/claude/skills/epd/ \
       .config/claude/skills/validate/ \
       .config/claude/skills/spike/ \
       .config/claude/skills/interviewing-issues/
git commit -m "✨ feat(skills): enrich Tier 2 pipeline skills with templates and references"
```

---

## Task 9: Tier 2 — Generator + KB + Tool Wrapper (8 skills)

**Skills:** spec, digest, timekeeper, senior-frontend, senior-backend, senior-architect, codex, codex-review, gemini, debate

- [ ] **Step 1: spec — references/precision-ceiling.md**

```markdown
# Precision Ceiling — Spec Slop 検知基準

## Borges 問題

仕様が詳細になりすぎると、実装そのものと同じ長さ・複雑さになる（Borges の地図の寓話）。

## Spec Slop シグナル

| シグナル | 例 | 対処 |
|---------|-----|------|
| 実装詳細の記述 | "React.useState を使って..." | 方針レベルに抽象化 |
| 行数が実装を超える | spec 200行、実装見積 100行 | 分割または簡素化 |
| 変更頻度が高い | spec を3回以上修正 | 要件が不安定、/spike 推奨 |
| 全エッジケース列挙 | 20以上の Given/When/Then | 代表的な5つに絞る |

## 適切な精度レベル

| 項目 | 記述すべき | 記述不要 |
|------|----------|---------|
| What（何を） | ✓ | |
| Why（なぜ） | ✓ | |
| How（どう実装） | | ✗ |
| 受入条件 | ✓（5-10個） | |
| 全テストケース | | ✗ |
```

- [ ] **Step 2: digest — references/metadata-inference.md**

```markdown
# Metadata Inference Rules

## Source Type Detection

| Pattern | source_type |
|---------|-------------|
| youtube.com, youtu.be | YouTube |
| arxiv.org | Paper |
| github.com | Repository |
| *.pdf URL | PDF |
| podcast/episode in text | Podcast |
| Default | Article |

## Auto-Inference Fields

| Field | Method |
|-------|--------|
| title | First H1 or bold text |
| author | Byline, channel name, or "Unknown" |
| url | Extracted URL or empty |
| language | Text language detection (ja/en) |
| tags | Extract from content keywords (max 5) |
| date | Publication date or today |
```

- [ ] **Step 3: timekeeper — scripts/accuracy-tracker.sh**

```bash
#!/bin/sh
# Track planning accuracy: planned vs actual tasks
# Usage: accuracy-tracker.sh [YYYY-MM-DD]
set -e
DATE="${1:-$(date +%Y-%m-%d)}"
VAULT="$HOME/Documents/Obsidian Vault/07-Daily"
FILE="$VAULT/$DATE.md"
if [ ! -f "$FILE" ]; then echo "No daily note for $DATE"; exit 0; fi
PLANNED=$(grep -c '^\- \[.\]' "$FILE" 2>/dev/null || echo 0)
DONE=$(grep -c '^\- \[x\]' "$FILE" 2>/dev/null || echo 0)
if [ "$PLANNED" -gt 0 ]; then
  RATE=$((DONE * 100 / PLANNED))
  echo "{\"date\":\"$DATE\",\"planned\":$PLANNED,\"done\":$DONE,\"rate\":$RATE}"
else
  echo "{\"date\":\"$DATE\",\"planned\":0,\"done\":0,\"rate\":0}"
fi
```

- [ ] **Step 4: senior-frontend — references/a11y-checklist.md**

```markdown
# Accessibility Checklist (WCAG 2.1 AA)

## Perceivable
- [ ] All images have meaningful alt text
- [ ] Color is not the only means of conveying information
- [ ] Contrast ratio ≥ 4.5:1 (normal text), ≥ 3:1 (large text)
- [ ] Text can be resized to 200% without loss of content

## Operable
- [ ] All functionality available via keyboard
- [ ] No keyboard traps
- [ ] Focus order is logical and intuitive
- [ ] Focus indicators are visible
- [ ] Skip navigation link present

## Understandable
- [ ] Language attribute set on html element
- [ ] Form inputs have associated labels
- [ ] Error messages are descriptive and suggest fixes
- [ ] Consistent navigation across pages

## Robust
- [ ] Valid HTML (no duplicate IDs)
- [ ] ARIA roles used correctly
- [ ] Custom components have proper ARIA attributes
- [ ] Works with screen readers (VoiceOver, NVDA)
```

- [ ] **Step 5: senior-backend (2 files), senior-architect (2 files)**

Create `senior-backend/references/security-checklist.md`, `senior-backend/templates/api-spec-template.md`, `senior-architect/templates/architecture-proposal.md`, `senior-architect/templates/tech-evaluation.md` with appropriate content following the same pattern.

- [ ] **Step 6: codex, codex-review, gemini, debate (8 files total)**

Create respective references/ and scripts/ files as specified in the spec.

- [ ] **Step 7: Add pointers to all SKILL.md files and commit**

```bash
git add .config/claude/skills/{spec,digest,timekeeper,senior-frontend,senior-backend,senior-architect,codex,codex-review,gemini,debate}/
git commit -m "✨ feat(skills): enrich Tier 2 generator, KB, and tool wrapper skills"
```

---

## Task 10: Tier 3 — All 12 skills (12 files)

Each skill gets 1 file. Follow the same pattern: create file, add SKILL.md pointer.

- [ ] **Step 1: Create all 12 files**

| Skill | File | Content Summary |
|-------|------|----------------|
| skill-audit | `templates/audit-report.md` | Benchmark results, health scores, recommendations |
| create-pr-wait | `templates/ci-fix-log.md` | CI failure → fix → retry log |
| obsidian-knowledge | `templates/moc-template.md` | Map of Content with linked notes |
| ai-workflow-audit | `references/audit-checklist.md` | AI workflow quality checklist |
| obsidian-content | `templates/content-templates.md` | Newsletter/blog/tweet skeleton |
| obsidian-vault-setup | `references/plugin-recommendations.md` | Plugin by use case |
| frontend-design | `references/anti-patterns.md` | Design anti-patterns catalog |
| meeting-minutes | `templates/minutes-template.md` | Agenda, decisions, action items |
| weekly-review | `templates/weekly-report.md` | Weekly achievements, blockers, plan |
| morning | `templates/morning-routine.md` | Morning routine structure |
| web-design-guidelines | `references/checklist-by-category.md` | 11 category checklists |
| react-expert | `references/api-quick-ref.md` | React API quick reference |

Each file follows the template/reference conventions established in Tier 1-2.

- [ ] **Step 2: Add SKILL.md pointers to all 12 skills**

- [ ] **Step 3: Commit**

```bash
git add .config/claude/skills/{skill-audit,create-pr-wait,obsidian-knowledge,ai-workflow-audit,obsidian-content,obsidian-vault-setup,frontend-design,meeting-minutes,weekly-review,morning,web-design-guidelines,react-expert}/
git commit -m "✨ feat(skills): enrich Tier 3 skills with templates and references"
```

---

## Task 11: skill-creator integration

**Files:**
- Create: `skill-creator/references/skill-archetypes.md`
- Modify: `skill-creator/SKILL.md` (Pattern Selection フェーズに参照追加)

- [ ] **Step 1: Create skill-archetypes.md**

Create `skill-creator/references/skill-archetypes.md`:

```markdown
# Skill Archetypes — 新スキル作成時の型選択ガイド

## 判断フロー

```
スキルの主な役割は？
├─ 操作をブロック/確認する → Guard
├─ 複数ステップを順序実行する → Pipeline
├─ ファイルを生成する → Generator
├─ 知識を提供し判断を支援する → Knowledge Base
└─ 外部CLIツールをラップする → Tool Wrapper
```

## Archetype 定義

### 1. Guard
**役割**: 操作インターセプト、安全担保
**構造**: SKILL.md のみ
**例**: freeze, careful, verification-before-completion

### 2. Pipeline
**役割**: 複数フェーズの順序実行 + ゲート
**必須**: templates/ (出力フォーマット)
**推奨**: references/ (フェーズ別ガイド)
**任意**: scripts/ (自動化)
**例**: review, research, improve, absorb

### 3. Generator
**役割**: 構造化ファイル生成
**必須**: templates/ (出力テンプレート)
**任意**: scripts/ (データ収集), data/ (ドメインコンテンツ)
**例**: daily-report, eureka, spec, digest

### 4. Knowledge Base
**役割**: ドメイン知識の構造化、意思決定支援
**必須**: references/ (パターンカタログ)
**任意**: data/ (判断マトリクス), scripts/ (検証ツール)
**例**: senior-frontend, edge-case-analysis, react-best-practices

### 5. Tool Wrapper
**役割**: 外部CLIツールの最適な使い方を教える
**推奨**: scripts/ (ヘルパー), references/ (CLIリファレンス)
**任意**: examples/ (実行可能サンプル)
**例**: codex, gemini, webapp-testing

## 新スキル作成時の手順

1. 上記判断フローで archetype を選択
2. archetype の「必須」ディレクトリを作成
3. SKILL.md に `## Skill Assets` セクションで参照ポインタを記載
4. 「任意」は実際に必要になってから追加 (YAGNI)
```

- [ ] **Step 2: Add reference to skill-creator SKILL.md**

In the "Pattern Selection" section of `skill-creator/SKILL.md`, add:

```markdown
> **Archetype Reference**: 新スキルの型選択には `references/skill-archetypes.md` を参照してください。
```

- [ ] **Step 3: Commit**

```bash
git add .config/claude/skills/skill-creator/
git commit -m "✨ feat(skills): add skill archetypes reference for skill-creator"
```

---

## Task 12: Verification

- [ ] **Step 1: Verify all new files exist**

```bash
echo "=== Tier 1 ==="
for f in \
  review/templates/synthesis-report.md \
  review/scripts/extract-diff-stats.sh \
  research/templates/subtask-prompt.md \
  research/references/model-assignment-guide.md \
  improve/templates/improvement-report.md \
  improve/templates/experiment-log.md \
  improve/references/analysis-categories.md \
  check-health/templates/health-report.md \
  check-health/references/staleness-criteria.md \
  absorb/templates/analysis-report.md \
  absorb/templates/integration-plan.md \
  absorb/references/triage-criteria.md \
  daily-report/scripts/collect-session-stats.sh \
  eureka/templates/breakthrough-template.md; do
  test -f ".config/claude/skills/$f" && echo "✓ $f" || echo "✗ $f MISSING"
done

echo "=== skill-creator integration ==="
test -f ".config/claude/skills/skill-creator/references/skill-archetypes.md" && echo "✓ skill-archetypes.md" || echo "✗ MISSING"
```

- [ ] **Step 2: Verify SKILL.md pointers**

```bash
for skill in review research improve check-health absorb daily-report eureka; do
  grep -q "Skill Assets" ".config/claude/skills/$skill/SKILL.md" && echo "✓ $skill has pointer" || echo "✗ $skill MISSING pointer"
done
```

- [ ] **Step 3: Verify scripts are executable**

```bash
for s in \
  review/scripts/extract-diff-stats.sh \
  daily-report/scripts/collect-session-stats.sh; do
  test -x ".config/claude/skills/$s" && echo "✓ $s executable" || echo "✗ $s not executable"
done
```

- [ ] **Step 4: Run extract-diff-stats to verify it works**

```bash
sh .config/claude/skills/review/scripts/extract-diff-stats.sh HEAD~1
```

Expected: JSON output with files_changed, insertions, deletions, languages, scale fields.

- [ ] **Step 5: Final git status check**

```bash
git status
git log --oneline -10
```

Expected: Clean working tree, commits for each tier visible.
