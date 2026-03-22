# Review Synthesis Report

## Summary

| Metric | Value |
|--------|-------|
| Files reviewed | {file_count} |
| Total findings | {finding_count} |
| Reviewers | {reviewer_list} |
| Agreement Rate | {agreement_rate}% |
| Verdict | {PASS / NEEDS_FIX / BLOCK / NEEDS_HUMAN_REVIEW} |

<!-- Agreement Rate 計算: 1 - (conflict_count / total_findings)
     conflict_count = 同一ファイル+-5行で矛盾する指摘の組数
     >= 90%: 高い一致。70-89%: 中程度（Conflicts 明記）。< 70%: CONVERGENCE STALL -->
<!-- Verdict が NEEDS_HUMAN_REVIEW の場合: 収束停滞を検出。ユーザー判断を要求 -->

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

| Reviewer | Findings | Avg Confidence | Status |
|----------|----------|----------------|--------|
| {reviewer} | {count} | {avg_confidence} | {OK / [OUTLIER] / [DEEP_REASONING]} |

<!-- Outlier 判定: Finding 重複率 < 20% AND 指摘数が平均の 3x 以上 → [OUTLIER]
     codex-reviewer の Severity 乖離は [DEEP_REASONING] として保持（除外しない）
     詳細: references/review-consensus-policy.md -->
