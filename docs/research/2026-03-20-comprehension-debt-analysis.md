---
source: https://addyosmani.com/blog/comprehension-debt/
date: 2026-03-20
status: integrated
---

## Source Summary

**Comprehension Debt** (Addy Osmani, 2026-03-14)

### Main Thesis

AI coding tools create an expanding gap between code that exists in a codebase and code that humans truly understand. This "comprehension debt" is invisible to standard metrics (velocity, DORA, coverage) and accrues interest rapidly.

### Key Techniques / Patterns

1. **Measure comprehension, not just velocity** - standard metrics miss understanding gaps
2. **Separate test authorship from implementation** - prevent tautological testing
3. **Require design intent articulation** - implementers must explain "why this approach"
4. **Distinguish active vs passive AI delegation** - active use maintains understanding
5. **Gate implementation on spec review** - prevent rushing past comprehension phase
6. **Recognize speed asymmetry** - generation speed >> evaluation speed
7. **Surface correctness != systemic correctness** - tests passing doesn't mean understood

### Evidence

- Anthropic "How AI Impacts Skill Formation": 52 engineers, AI users scored 17% lower on comprehension (50% vs 67%)
- Debugging showed largest decline; code reading showed smaller but significant decline
- Active AI engagement maintained comprehension better than passive delegation

### Prerequisites

- Most relevant to AI-augmented development workflows
- Applies at any scale but most dangerous in team settings where knowledge must be shared
- Individual developers also affected (future-self comprehension)

## Gap Analysis

| # | Technique | Status | Current State | Gap |
|---|-----------|--------|---------------|-----|
| 1 | Comprehension metrics | **Gap** | No metric tracks "does human understand this code" | Need tracking in improve-policy |
| 2 | Test vs understanding distinction | **Partial** | verification-before-completion requires evidence, not explanation | Need "why does this work" gate |
| 3 | Test independence | **Gap** | No constraint on same-session impl+test authorship | Need tautological test detection |
| 4 | Implementer design intent | **Gap** | code-reviewer ASKs but no proactive obligation | Need pre-review design rationale |
| 5 | Active vs passive delegation | **Partial** | overconfidence-prevention + spec-is-code guide thinking | No explicit delegation pattern distinction |
| 6 | Spec review gate | **Partial** | /spec and overconfidence-prevention exist but not enforced | Need M/L mandatory spec gate |
| 7 | Review speed floor | **Gap** | No minimum review thoroughness check | Need lines-changed vs review-time ratio |
| 8 | Surface vs systemic correctness | **Already** | gaming-detector Rules 20-22, stagnation-detector, agency-safety-framework | Well-integrated |
| 9 | Speed asymmetry awareness | **Gap** | No mechanism detects "accepted too fast" | Need review thoroughness signal |

## Integration Decisions

All Gap/Partial items selected for integration (6 items):

1. [Gap] Implementer design intent gate - pre-review 3-line rationale
2. [Gap] Tautological test detection - test-analyzer rule addition
3. [Gap] Comprehension metrics - improve-policy addition
4. [Partial] Passive delegation detection - overconfidence-prevention enhancement
5. [Partial] Spec review gate enforcement - workflow-guide M/L mandatory
6. [Gap] Review speed floor - review orchestrator enhancement

## Plan

See `docs/plans/active/2026-03-20-comprehension-debt-integration.md`
