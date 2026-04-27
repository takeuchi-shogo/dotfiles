---
topic: "{topic}"
date: {YYYY-MM-DD}
paper_count: {N}
steps_executed: [0,1,2,3,3.5,4,5,6,7,8,9]
status: {completed | partial}
---

> **Provenance & Confidence 表記**
>
> 主張・関係・仮定には `[provenance, conf=NN]` を併記する。
> - `provenance`: `EXTRACTED` (本文直接) / `INFERRED` (合理推論) / `AMBIGUOUS` (本文では断定不能)
> - `conf`: 0-100 整数。provenance とは直交軸（出所 vs 確度）
> - 詳細: `~/.claude/references/provenance-tagging.md`

## Corpus Overview

| # | 著者(年) | タイトル | 手法 | 核心主張 |
|---|---------|---------|------|---------|
| 1 | {author} ({year}) | {title} | {method} | {claim} |

## Step 1: Landscape Map

### 共有仮説クラスター

| クラスター | 共有仮説 | 論文 |
|-----------|---------|------|
| {name} | {hypothesis} | {papers} |

### 対立軸

| 論点 | 陣営A | 陣営B |
|------|------|------|
| {issue} | {papers + position} | {papers + position} |

## Step 2: Contradictions

| # | 主張A (論文) | 主張B (論文) | WHY | 解決可能性 | provenance | conf |
|---|-------------|-------------|-----|-----------|-----------|------|
| 1 | {claim} ({paper}) | {claim} ({paper}) | {reason} | {resolvable/fundamental} | EXTRACTED | 90 |

## Step 3: Citation Chains

### Concept 1: {concept_name}

| 段階 | 論文 | 内容 | provenance | conf |
|------|------|------|-----------|------|
| 導入 | {paper} | {description} | EXTRACTED | 95 |
| 批判 | {paper} | {description} | EXTRACTED | 85 |
| 精緻化 | {paper} | {description} | INFERRED | 70 |
| 現在の合意 | — | {consensus_or_disputed} | AMBIGUOUS | 60 |

## Step 3.5: Concept Relations

> 概念ペア間の構造化関係を `(subject, predicate, object)` トリプルで抽出。
> predicate vocabulary: `cites`, `extends`, `contradicts`, `depends_on`, `refines`, `unifies`
> 詳細: `references/relation-extraction.md`

| # | A (subject) | predicate | B (object) | provenance | conf | evidence |
|---|------------|-----------|-----------|-----------|------|----------|
| 1 | {concept_a} | extends | {concept_b} | EXTRACTED | 90 | {paper} §{section} |
| 2 | {concept_a} | depends_on | {concept_c} | INFERRED | 75 | {paper} §{section} |

**Skip 条件**: 論文 3 本以下なら本セクションをスキップ可。

## Step 4: Synthesis

### Consensus
{what_the_field_collectively_believes} `[EXTRACTED, conf=NN]`

### Contested
{active_debates_with_evidence} `[EXTRACTED, conf=NN]`

### Unresolved
{questions_without_sufficient_evidence} `[INFERRED, conf=NN]`

### The Single Most Important Unanswered Question
{question}

## Step 5: Research Gaps

| # | 未回答の問い | 存在理由 | 最接近論文 | 必要な手法 | provenance | conf |
|---|------------|---------|-----------|-----------|-----------|------|
| 1 | {question} | {too_hard/niche/overlooked} | {paper} | {methodology} | INFERRED | 65 |

## Step 6: Methodology Audit

### 手法分布

| 手法 | 論文数 | 割合 |
|------|-------|------|
| {method} | {count} | {%} |

### 評価

- **支配的手法**: {method} — {why}
- **過小利用**: {method} — {why}
- **最弱論文**: {paper} — {weakness}

## Step 7: Knowledge Map

### Central Claim
{core_claim}

### Supporting Pillars
1. {pillar} — 根拠: {papers}

### Contested Zones
1. {debate} — {side_A} vs {side_B}

### Frontier Questions
1. {question}

### Must-Read Papers
1. {paper} — {why_read_first}

## Step 8: So What

1. **証明されたこと**: {one_sentence}
2. **まだ知らないこと**: {honest_limitation}
3. **最重要な現実含意**: {implication}

## Step 9: Assumptions

| # | 暗黙の仮定 | 依存論文 | 仮定が誤りなら | provenance | conf |
|---|-----------|---------|--------------|-----------|------|
| 1 | {assumption} | {papers} | {counterfactual_impact} | INFERRED | 70 |
