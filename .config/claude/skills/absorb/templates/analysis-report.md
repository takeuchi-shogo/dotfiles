---
source: "{URL or title}"
date: {YYYY-MM-DD}
status: {analyzed | integrated | skipped}
family: {Family ID | none}
---

<!--
family は Phase 1.5 Step 1 で判定した Family ID をそのまま書く
(`references/topic-family-saturation.md` の taxonomy 表の左列)。
該当 family なし = 新分野なら `none`。判定が割れて分類しないと決めた場合も `none`。
このフィールドが Step 2 の件数集計の唯一の入力なので、省略すると次回以降の N が過小になる。
-->


## Source Summary

**主張**: {core_claim_1_to_3_sentences}

**手法**:
- {technique_1}
- {technique_2}

**根拠**: {evidence_or_data}

**前提条件**: {context_where_valid}

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | {technique} | {Already/Partial/Gap/N/A} | {details} |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | {existing_mechanism} | {weakness_from_article} | {concrete_enhancement} | {強化不要/強化可能} |

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1 | {item} | {採用/スキップ} | {reason} |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | {item} | {採用/スキップ} | {reason} |

## Plan

### Task 1: {task_name}
- **Files**: {file_paths}
- **Changes**: {what_to_do}
- **Size**: {S/M/L}
