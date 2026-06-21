---
name: codex-review
description: "Codex read-only review gate that runs reviewer subagents or a read-only CLI review, fixes blocking findings, and reruns until ok=true. Use after SPEC/PRD/PLANS.md changes, medium or large implementations, refactors, public API/config/infra/security changes, 5+ touched files, or before commit/PR/release handoff. Do NOT use for tiny obvious diffs where normal validation is enough."
platforms: [agents, codex]
---

# Codex Review

Use this skill as a review gate, not as a substitute for tests, commit, push, merge, or task completion. Keep Implementer and Reviewer separate: the parent Codex instance may fix issues, but it must not self-certify the review result without a read-only reviewer pass.

## Gate Rule

The gate passes only when all reviewer runs return valid structured output and no blocking issue remains.

Treat these as gate failures:
- reviewer did not run
- reviewer output is missing, malformed, or not attributable to a read-only reviewer
- any blocking issue remains
- review scope is incomplete or unknown
- validation needed for the critical path was not run
- the maximum fix loop is reached

Default `max_iters` is 5.

## Scope

Prepare the review input before launching a reviewer:

1. Inspect `git status --short` and `git diff --stat`.
2. Identify the review target: uncommitted diff, staged diff, branch diff, or specific files.
3. List touched files, risk areas, related tests, and validation already run.
4. Classify size:

| Size | Heuristic | Reviewer strategy |
|---|---|---|
| small | <=3 files and <=100 changed lines | one `reviewer` diff pass |
| medium | 4-10 files or 100-500 changed lines | `reviewer`; add `cross_file_reviewer` for multi-file contracts |
| large | >10 files or >500 changed lines | split by directory or concern; run 3-4 focused reviewers, then synthesize |

Raise the size one level for auth, security, data deletion, migrations, public APIs, infra/config, external side effects, dependency changes, or harness changes.

## Reviewer Selection

Prefer configured read-only Codex custom agents when available:

- `reviewer`: default correctness, security, and test-gap review
- `cross_file_reviewer`: interface drift, imports, callers, and multi-file refactors
- `security_auditor`: auth, secrets, input validation, scripts, MCP, or config security
- `edge_case_hunter`: nil, empty, boundary, retry, timeout, timezone, and unusual-path risks
- `silent_failure_hunter`: swallowed errors, unsafe fallback, log-and-continue patterns
- `migration_guard`: DB/API/dependency breaking changes

Use the smallest reviewer set that covers the risk. Do not launch extra reviewers after a clean pass just to get nicer wording or a second opinion.

If custom agents are unavailable, record that attempt and use a read-only CLI fallback such as `codex review --uncommitted --plain` or an equivalent read-only `codex exec --sandbox read-only` review. The fallback must still produce enough structured findings to decide the gate.

## Reviewer Prompt Contract

Ask every reviewer for one JSON object only:

```json
{
  "ok": false,
  "phase": "diff",
  "summary": "short review summary",
  "reviewed_scope": ["path/or/scope"],
  "unreviewed_scope": [],
  "issues": [
    {
      "severity": "blocking",
      "category": "correctness",
      "file": "src/example.ts",
      "lines": "42-45",
      "problem": "what is wrong",
      "recommendation": "minimal fix",
      "verification": "how to verify the fix"
    }
  ],
  "notes_for_next_review": "carry-forward notes"
}
```

Required prompt details:

- State that the reviewer is read-only and must not edit files.
- Focus on P0/P1-equivalent risks: correctness, security, compatibility, data loss, missing critical tests, broken workflows, and release blockers.
- Ignore style, naming, wording, and broad refactors unless they create blocking risk.
- Inspect the diff first; read directly related callers, tests, docs, configs, and type definitions only when needed.
- If scope is too large or unclear, put it in `unreviewed_scope`; do not return `ok: true`.
- If any blocking issue exists, return `ok: false`.

## Fix Loop

When `ok` is false:

1. Parse blocking issues and decide the minimal fix plan.
2. Apply fixes in the parent Codex instance only.
3. Run focused validation for the changed area. If a review-triggered fix changed code, rerun affected tests or the closest available validation before re-review.
4. Re-run review with the same reviewer type and include `notes_for_next_review`.
5. Stop at `ok=true`, `max_iters`, two consecutive validation failures, reviewer failure, or unresolved unreviewed scope.

Do not independently dismiss a blocking issue. If dismissal seems correct, document the evidence and ask the reviewer to re-check that specific point.

## Final Report

Report these items:

- mode: custom agents or read-only CLI fallback
- review scope and size
- reviewers used and fallback evidence, if any
- iterations used
- gate result: `ok=true` or `ok=false`
- validation commands and result
- fixed issues
- unresolved blocking issues, unreviewed scope, or reviewer failures

Make clear that `ok=true` means the review gate passed only. It does not imply commit, push, merge, release, or task completion.
