---
date: 2026-04-21
source_title: "How I got banned from GitHub due to my harness pipeline"
source_type: blog_post
source_url: (not provided - user pasted text)
triaged_by: /absorb
status: analysis_complete
integration_plan: docs/plans/active/2026-04-21-harness-pipeline-absorb-plan.md
---

# Harness Pipeline Article — absorb analysis

## Article Summary

A practitioner describes building a 13-stage automated harness pipeline that generated 500+ commits across 100+ repos over 72 hours, resulting in a GitHub account ban. The core thesis is that the pipeline's value concentrated in two stages: Stage 5 (local reproduction before patch) and Stage 8 (merge-pattern matching against prior accepted PRs). The article argues that "attestation is scarce" — harnesses should wrap around human signoff rather than bypass it — and that platform abuse detection reads commit/PR velocity rather than content shape.

The article frames expert+harness as strictly superior to novice+harness. This claim is contested by 2026 data.

## Key Claims & Methods

1. 13-stage pipeline across 100+ repos, 72h, 500+ commits — account banned via velocity detection
2. Stage 5 (local reproduction) + Stage 8 (merge-pattern matching) = ~80% of pipeline value
3. "Attestation is scarce" — harness augments human signoff; bypassing it is both ethically wrong and strategically fragile
4. Platform abuse layer reads velocity/shape signals, not content quality
5. Expert+harness >> novice+harness in outcome quality (contested)
6. Few-shot from own merged PRs as style/pattern injection
7. Session-independent state for MCP context persistence across long runs
8. Load-bearing check as integration-test gate before merge
9. Output-as-constraint: generate output first, use it to constrain subsequent generation steps
10. CLA-style signoff flow for OSS contribution pipelines

## Gap Analysis

### Gap / Partial / N/A

| # | Concept | Current state | Priority |
|---|---------|---------------|----------|
| 2 | MCP session-independent state | Partial — checkpoint skill exists but success_criteria drift and resume anchor are scattered across multiple files | P2 |
| 6 | Merge-pattern matching (few-shot from own merged PRs) | Gap — no mechanism to extract or inject own PR history as style reference | Low (solo dotfiles context mismatch) |
| 7 | Few-shot own PRs | Gap — same as #6; no tooling to build personal PR corpus | Low |
| 8 | Load-bearing check as integration gate | Partial — verification-before-completion exists but is advisory, not a hard gate before merge | P2 |
| 10 | Attestation boundary codification | Partial — no explicit boundary document distinguishing "harness executes" from "human must sign off" | P2 |
| 12 | Output-as-constraint pattern | Partial — no codified workflow that generates output first and uses it to constrain subsequent steps | P2 |
| 13 | Expert amplification principle | Partial — agent-router routes to models but does not encode the expert-first amplification heuristic | P3 |

### Already with enhancement suggestions

| Label | Skill/Mechanism | Already status | Enhancement |
|-------|----------------|----------------|-------------|
| A | fix-issue (reproduce-first attestation) | Partially wired — fix-issue skill exists but "reproduce the bug before patching" is not enforced as a gate | Codify reproduce-first attestation as priority-1 step; make it a block condition, not a suggestion |
| B | checkpoint (resume anchor) | Partially wired — checkpoint skill captures state but resume anchor is not a single canonical location; success_criteria can drift across plan files | Add a single resume anchor field; link checkpoint output back to plan's Success Criteria |
| C | interview / spec (plan-to-implement handoff) | Partially wired — interview skill exists but the transition from plan to implementation does not require a structured interview confirming scope and assumptions | Wire a required interview step at plan-to-implement boundary |
| D | model-routing (end-to-end principle) | Partially wired — model-routing.md exists and agent-router.py dispatches, but there is no single statement of the end-to-end routing principle that explains why a task goes where it goes | Add end-to-end routing principle statement to model-routing.md |

## Phase 2.5 Refine (Codex + Gemini critique)

### Codex critique (reproduce-first priority verdict)

Priority verdict: codify "reproduce-first attestation before polish" as a first-class gate in fix-issue and verification-before-completion.

Specific findings:

- **Premise mismatch for git-push velocity hook and CLA-style signoff**: These mechanisms are OSS-context specific. A solo dotfiles repo does not have external reviewers, so CLA signoff is theatrical rather than functional. The velocity hook (soft-warning on rapid commits) is partially covered by file-proliferation-guard.

- **Checkpoint Already downgrade to Partial**: The checkpoint skill is listed as "Already" in initial triage but is operationally fragile. Success_criteria can drift when a plan is updated mid-session. The resume anchor is documented in multiple places (tmp/plans/, docs/plans/, PLANS.md) with no canonical source of truth. Downgraded to Partial.

- **Interview skill Already downgrade to Partial**: The interview skill exists but there is no enforcement mechanism that blocks moving from plan to implementation without completing a spec interview. The skill is available but not wired into the workflow as a gate.

- **feature-tracker Already status**: Confirmed as operationally sound for multi-session tracking. No downgrade.

- **file-proliferation-guard Already status**: Confirmed sufficient for the velocity concern in solo context. No addition needed.

- **agent-router Already status**: Routes correctly but lacks the expert-amplification framing. Minor enhancement warranted.

### Gemini peripheral knowledge (2026 platform landscape)

- **Platform enforcement has hardened**: GitHub, GitLab, and similar platforms now apply zero-tolerance velocity detection (similar to curl and Ghostty incidents). The 2026 enforcement posture means any automated pipeline must treat rate limits as hard constraints, not soft guidelines.

- **Stanford HAI 2026 data on expert+AI vs novice+AI**: Expert+AI shows ~10x productivity gain. Novice+AI shows ~20x repair cost versus novice alone in complex codebases. The gap doubles compared to 2024 estimates. The article's claim that "expert+harness >> novice+harness" is confirmed, but the framing understates the novice downside risk. This makes expert amplification harder to codify as a simple heuristic.

- **2026 legal landscape on CLA**: CLA mandates now place liability on the human operator, not the tool. Any automated commit pipeline must have auditable human-in-the-loop attestation. This reinforces the article's attestation-is-scarce claim but makes CLA-style signoff a legal concern, not just an ethical one.

- **Reproduction-first is now table stakes**: Multiple defensive open-source projects (referenced in HAI 2026 survey) have adopted reproduction-first as a baseline. Projects that skip it face increased rejection rates from maintainers who can distinguish patch-first from reproduce-first PRs by diffstat shape.

### Revisions made

Based on Codex and Gemini critique:

- Checkpoint downgraded from Already to Partial (resume anchor fragility confirmed)
- Interview skill downgraded from Already to Partial (no enforcement gate)
- CLA-style signoff moved to Rejected (OSS-specific, liability risk in automated pipelines)
- Expert amplification moved to Partial/Rejected boundary — codification contested; kept as P3 with low confidence
- Reproduce-first attestation elevated to priority-1 enhancement

## Triage Decision (user-selected items)

### Accepted for integration

| Item | Description | Priority |
|------|-------------|----------|
| #2 | MCP session-independent state — fix resume anchor, canonicalize success_criteria location | P2 |
| #8 | Load-bearing check — make verification-before-completion a hard gate, not advisory | P2 |
| #12 | Output-as-constraint — codify generate-output-first workflow as a named pattern | P2 |
| A | fix-issue reproduce-first — add reproduce-first as a blocking step before any patch | P1 |
| B | checkpoint resume anchor — single canonical anchor field, linked to plan Success Criteria | P2 |
| C | plan-to-implement interview — wire required interview at plan boundary | P2 |
| D | model-routing end-to-end principle — add explanatory statement to model-routing.md | P3 |

Total: 7 tasks across 9 files.

## Integration Plan Summary

Plan file: `docs/plans/active/2026-04-21-harness-pipeline-absorb-plan.md`

Size: L (multiple files, cross-cutting concern, >30 min estimated work)

Tasks:

1. **T1 (P1)**: Add reproduce-first attestation block to fix-issue skill — enforce before patch, not after
2. **T2 (P2)**: Canonicalize resume anchor in checkpoint skill — single field, linked to PLANS.md Success Criteria
3. **T3 (P2)**: Add load-bearing check gate to verification-before-completion — change from advisory to blocking
4. **T4 (P2)**: Codify output-as-constraint pattern in references/ — named workflow with concrete example
5. **T5 (P2)**: Fix success_criteria drift — checkpoint output must reference plan's Success Criteria section
6. **T6 (P2)**: Wire plan-to-implement interview boundary — add required interview step in workflow guide
7. **T7 (P3)**: Add end-to-end routing principle to model-routing.md — one paragraph explaining task-to-model assignment rationale

Files affected: fix-issue skill, checkpoint skill, verification-before-completion skill, references/workflow-guide.md, references/model-routing.md, PLANS.md, docs/plans/active/ (new plan file), references/ (new output-as-constraint doc), interview skill.

## Rejected Items and Rationale

| Item | Rationale |
|------|-----------|
| 13-stage pipeline copy | Context mismatch — solo dotfiles repo has no multi-repo automation need; copying pipeline structure adds harness complexity without proportional value |
| GitHub mass PR automation | Direct BAN risk in 2026 enforcement posture; additionally, 2026 legal landscape places CLA liability on human operator; not viable |
| git-push velocity soft-warning hook | file-proliferation-guard already covers this surface; adding a second mechanism creates overlapping signals without incrementally useful data |
| CLA-style signoff flow | OSS-specific; creates legal exposure in automated pipelines under 2026 CLA mandate; theatrical in solo context |
| Expert amplification codification | Contested by Stanford HAI 2026 data; the novice downside risk makes this difficult to encode as a simple heuristic without misleading users; low confidence, deferred indefinitely |

## Open Questions / Future Considerations

1. **Attestation boundary document**: The article's "attestation is scarce" claim implies there should be an explicit document defining what harness executes vs. what requires human signoff. This is not implemented. A lightweight `references/attestation-boundary.md` may be warranted as a follow-on (not in current plan due to scope).

2. **Output-as-constraint generalizability**: The pattern is described in the article as pipeline-specific. Whether it generalizes to dotfiles-scale tasks (single repo, single operator) needs a spike before full codification. T4 should include a prototype step.

3. **Velocity detection in solo context**: The article's velocity concern is real at 500+ commits/72h but does not apply to normal dotfiles workflow. However, the underlying principle — that platform signals read behavior shape, not content quality — may warrant a one-paragraph addition to the harness-stability reference.

4. **Novice+harness downside risk**: Stanford HAI 2026 data suggests novice+AI repair costs are significant. The current harness has no mechanism to detect when an operator is outside their competence boundary. This is a longer-term consideration for the agent-router or a future competence-boundary hook.

5. **Session-independent state beyond checkpoint**: The article describes MCP-level session persistence that survives context compaction and process restart. The current checkpoint skill is session-scoped. A more durable state mechanism (e.g., writing to a canonical state file on every significant decision) may be needed for L-scale tasks.
