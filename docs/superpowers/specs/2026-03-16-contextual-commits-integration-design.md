# Contextual Commits Integration Design

**Date**: 2026-03-16
**Status**: Approved
**Scope**: Global infrastructure (all projects via dotfiles)
**Approach**: Approach 1 — Skill extension only (minimal changes)

## Problem

AI coding sessions produce three outputs: code changes, decisions, and understanding.
Only code survives in git. Decisions and understanding evaporate when the session closes.

The dotfiles repository has a sophisticated 4-layer context preservation system
(SessionStart/End, AutoEvolve learnings, Checkpoints, ADRs), but **no mechanism
attaches decision context to individual commits**. ADRs record architecture decisions
separately. Plans have Decision Logs but commits don't reference them.

## Solution

Integrate the [Contextual Commits](https://github.com/berserkdisruptors/contextual-commits)
convention (v0.1.0) into the dotfiles global infrastructure. Commits carry structured
action lines in the body that preserve intent, decisions, rejected alternatives,
constraints, and learnings alongside the code change.

### Source

- **Spec**: https://github.com/berserkdisruptors/contextual-commits/blob/main/SPEC.md
- **Reference implementation**: Adapted from `skills/contextual-commit/SKILL.md` and
  `skills/recall/SKILL.md`, not imported via `npx skills add`

## Design Decisions

| Decision | Choice | Alternatives Rejected |
|----------|--------|-----------------------|
| Integration scope | Global (all projects) | dotfiles-only — value is universal |
| Integration method | Self-contained skill extension | `npx skills add` — incompatible with symlink management |
| AutoEvolve integration | One-way bridge (commit → learnings) | Independent (data duplication), Bidirectional (overengineering) |
| Recall timing | Lightweight SessionStart + manual full | Manual only (misses safety net), Full auto (token waste) |
| Validation | None | Lefthook regex (blocks manual commits), commitlint plugin (extra dependency) |
| Action line source | Session context only | session_events augmentation (YAGNI, KISS) |

## Components

### 1. `/commit` Command Extension

**File**: `commands/commit.md`

**Change**: Add action line generation phase after subject line generation, before `git commit`.

**Flow**:
```
git status → git diff analysis → split detection → subject line generation
→ action line judgment → body generation → commit → AutoEvolve emit
```

**Action line judgment rules**:

| Condition | Action lines |
|-----------|-------------|
| Typo fix, dependency bump, formatting | None (subject only) |
| Clear technical choice was made | `decision()` only |
| Alternatives were considered and rejected | `decision()` + `rejected()` |
| User's goal not obvious from subject | Add `intent()` |
| Implementation constraint discovered | Add `constraint()` |
| API quirk or library gotcha discovered | Add `learned()` |
| No session context for the change | Only diff-inferable `decision()`, or omit |

**Limits**: Typically 1-3 action lines, maximum 5. If more are needed, suggest commit splitting.

**MUST rules**:
- Subject line remains `<emoji> <type>(<scope>): <description>` (unchanged)
- Action lines go in body only, after blank line separator
- NEVER fabricate action lines without session evidence (SPEC Rule 14)
- For changes without session context, only `decision()` may be inferred from diff
- `rejected()` MUST include the reason for rejection (SPEC Rule 13)
- Check existing scopes on current branch before creating new ones

**Commit execution** uses HEREDOC for correct formatting:
```bash
git commit -m "$(cat <<'EOF'
✨ feat(auth): implement Google OAuth provider

intent(auth): social login starting with Google, then GitHub and Apple
decision(oauth-library): passport.js over auth0-sdk for multi-provider flexibility
rejected(oauth-library): auth0-sdk — locks into their session model
EOF
)"
```

**Compatibility**:
- Lefthook `commit-msg` validates subject line only — no changes needed
- `pre-commit-check.js` operates on staged files — unaffected
- semantic-release, changelog generators read subject line — unaffected

### 2. `/recall` Command (New)

**File**: `commands/recall.md` (new)

**Three invocation modes**:

#### Mode 1: Default (no arguments) — `/recall`

Detects branch state and generates appropriate briefing:

| State | Behavior |
|-------|----------|
| Feature branch + commits | Extract action lines from all branch commits, synthesize by priority: intent → decision → rejected → constraint → learned |
| Feature branch + no commits | Report staged/unstaged changes + parent branch recent activity |
| Default branch | Group last 20 commits by scope area |

Base branch detection:
1. Try `@{upstream}` (fast path)
2. Fallback: nearest local branch by commit distance
3. Final fallback: repository default branch

#### Mode 2: Scope query — `/recall auth`

```bash
git log --all --grep="(${SCOPE}" --format="%H%n%s%n%b%n---COMMIT_END---"
```

Prefix matching: `auth` matches `auth`, `auth-tokens`, `auth-library`.
Output grouped by action type, chronological within each group.

#### Mode 3: Action+scope query — `/recall rejected(auth)`

```bash
git log --all --grep="${ACTION}(${SCOPE}" --format="%H%n%s%n%b%n---COMMIT_END---"
```

Flat chronological list with commit subject for provenance.

**Output principles**:
- Dense over conversational — every line carries information
- Grounded in data — only report what action lines and diffs show
- Surface rejections prominently — highest-value signal
- Scale to data — 2 commits → 3-4 lines, 20 commits → grouped paragraphs

**Graceful degradation**: When no action lines exist in history, produce useful
output from conventional commit subjects and suggest contextual-commit adoption.

### 3. SessionStart Lightweight Integration

**File**: `scripts/runtime/session-load.js` (modify)

**Trigger**: Feature branch AND 1+ commits ahead of base branch.
**Not triggered**: Default branch, non-git directory, 0 commits ahead.

**Execution**:
```bash
git log ${BASE_BRANCH}..HEAD --format="%b" \
  | grep -E "^(rejected|constraint)\(" \
  | head -5
```

**Output** (appended to existing session-load output):
```
⚠️ Boundaries:
  rejected(oauth-library): auth0-sdk — session model incompatible with redis store
  constraint(callback-routes): must follow /api/auth/callback/:provider pattern
```

**Design constraints**:
- stderr output only (non-blocking, informational)
- 2-second timeout on git command
- try-catch: silently skip on failure
- 0 results → omit `⚠️ Boundaries:` section entirely
- Only `rejected()` and `constraint()` — these are "don't do this" signals
  worth showing automatically. intent/decision/learned require manual `/recall`

### 4. AutoEvolve One-Way Bridge

**Trigger**: After successful `git commit` in `/commit` command.

**Transferred action types**:

| Action type | Target category | Reason |
|-------------|----------------|--------|
| `rejected()` | `pattern` | Cross-project reuse value for rejected approaches |
| `learned()` | `pattern` | API quirks equivalent to error-fix guides |
| `intent()` | Not transferred | Session-specific, low cross-project value |
| `decision()` | Not transferred | Git history is sufficient |
| `constraint()` | Not transferred | Project-specific, git history is authoritative |

**Mechanism**: Call `emit_event()` from `/commit` command via bash:
```bash
python3 -c "
import sys; sys.path.insert(0, '$HOME/.claude/scripts/lib')
from session_events import emit_event
emit_event('pattern', {
    'type': 'rejected',
    'scope': '${SCOPE}',
    'detail': '${DETAIL}',
    'source': 'contextual-commit'
})
"
```

**Identification**: All emitted events carry `"source": "contextual-commit"` field
for downstream filtering by `autoevolve-core`.

**Failure handling**: Best-effort. Emit failure does not affect the already-completed
commit. Git history is the single source of truth; learnings JSONL is a search index.

**Existing code impact**: Zero. Uses existing `emit_event()` API and `pattern` category.

## Risk Analysis

| Risk | Probability | Impact | Mitigation | Residual |
|------|-------------|--------|------------|----------|
| Over-generation (noisy action lines) | Medium | Low | Judgment rules + 5-line limit in skill | Acceptable |
| **Fabrication (false context)** | **Medium** | **High** | **MUST rule: no evidence → no action line** | **Monitor** |
| Scope inconsistency | High | Medium | Existing scope check instruction | Acceptable |
| Unintended effect on other projects | Medium | Low | Body-only, no toolchain impact | Acceptable |
| SessionStart delay/error | Low | Low | Timeout + try-catch + silent skip | Negligible |

**Critical risk**: Fabrication. A false `rejected()` line can mislead future sessions
into avoiding valid approaches. The `/commit` skill MUST emphasize:
"A clean conventional commit with no action lines is always better than fabricated context."

## Files Changed

| File | Change | Type |
|------|--------|------|
| `commands/commit.md` | Add action line generation logic | Modify |
| `commands/recall.md` | New command for context reconstruction | New |
| `scripts/runtime/session-load.js` | Add rejected/constraint display for feature branches | Modify |

## Files NOT Changed

| File | Reason |
|------|--------|
| `lefthook.yml` | commit-msg validates subject only, body is unaffected |
| `scripts/policy/pre-commit-check.js` | Operates on staged files, not message format |
| `scripts/lib/session_events.py` | Existing `emit_event()` API used as-is |
| `scripts/learner/session-learner.py` | `pattern` category already flushed |
| `settings.json` | No new hooks, no new permissions needed |

## Future Extensions (Not In Scope)

- **Proactive recall check**: PreToolUse hook before `git commit` that auto-checks
  `rejected()` history for the current scope. Deferred per Determinism Boundary principle.
- **Bidirectional bridge**: `/recall` searching both git history and learnings JSONL.
- **Scope registry**: Per-project `.contextual-commits.yml` with known scopes.
- **commitlint plugin**: Formal validation of action line format.
- **`decision` event category**: New category in `session_events.py` for mid-session
  decision tracking, enabling richer auto-generation at commit time.

## Acceptance Criteria

1. `/commit` generates action lines when session context warrants them
2. `/commit` omits action lines for trivial changes (typo, format, bump)
3. `/commit` never fabricates action lines for changes without session context
4. `/recall` reconstructs context from git history in all 3 modes
5. `/recall` degrades gracefully in repos without contextual commits
6. SessionStart shows rejected/constraint on feature branches
7. SessionStart adds no latency on default branch or non-git directories
8. `learned()` and `rejected()` are emitted to AutoEvolve learnings
9. All existing lefthook validations continue to pass
10. Existing commit workflow (emoji + conventional commit subject) is unchanged
