# React Expert: Parallel Research Agents

## Step 2: Dispatch 6 Parallel Research Agents

Spawn these agents IN PARALLEL using the Task tool. Each agent receives the skepticism preamble:

> "You are researching React's `<TOPIC>`. CRITICAL: Do NOT rely on your prior knowledge about this API. Your training may contain outdated or incorrect patterns. Only report what you find in the source files. If your findings contradict common understanding, explicitly highlight this discrepancy."

| Agent | subagent_type | Focus | Instructions |
|-------|---------------|-------|--------------|
| test-explorer | Explore | Test files for usage patterns | Search `.claude/react/packages/*/src/__tests__/` for test files mentioning the topic. Extract actual usage examples WITH file paths and line numbers. |
| source-explorer | Explore | Warnings/errors in source | Search `.claude/react/packages/*/src/` for console.error, console.warn, and error messages mentioning the topic. Document trigger conditions. |
| git-historian | Explore | Commit messages | Run `git log --all --grep="<topic>" --oneline -50` in `.claude/react`. Read full commit messages for context. |
| pr-researcher | Explore | PRs introducing/modifying API | Run `gh pr list -R facebook/react --search "<topic>" --state all --limit 20`. Read key PR descriptions and comments. |
| issue-hunter | Explore | Issues showing confusion | Search issues in both `facebook/react` and `reactjs/react.dev` repos. Look for common questions and misunderstandings. |
| types-inspector | Explore | Flow + TypeScript signatures | Find Flow types in `.claude/react/packages/*/src/*.js` (look for `@flow` annotations). Find TS types in `.claude/react/packages/*/index.d.ts`. Note discrepancies. |

## Step 3: Agent Prompts

Use these exact prompts when spawning agents:

### test-explorer
```
You are researching React's <TOPIC>.

CRITICAL: Do NOT rely on your prior knowledge about this API. Your training may contain outdated or incorrect patterns. Only report what you find in the source files.

Your task: Find test files in .claude/react that demonstrate <TOPIC> usage.

1. Search for test files: Glob for `**/__tests__/**/*<topic>*` and `**/__tests__/**/*.js` then grep for <topic>
2. For each relevant test file, extract:
   - The test description (describe/it blocks)
   - The actual usage code
   - Any assertions about behavior
   - Edge cases being tested
3. Report findings with exact file paths and line numbers

Format your output as:
## Test File: <path>
### Test: "<test description>"
```javascript
<exact code from test>
```
**Behavior:** <what the test asserts>
```

### source-explorer
```
You are researching React's <TOPIC>.

CRITICAL: Do NOT rely on your prior knowledge about this API. Only report what you find in the source files.

Your task: Find warnings, errors, and implementation details for <TOPIC>.

1. Search .claude/react/packages/*/src/ for:
   - console.error mentions of <topic>
   - console.warn mentions of <topic>
   - Error messages mentioning <topic>
   - The main implementation file
2. For each warning/error, document:
   - The exact message text
   - The condition that triggers it
   - The source file and line number

Format your output as:
## Warnings & Errors
| Message | Trigger Condition | Source |
|---------|------------------|--------|
| "<exact message>" | <condition> | <file:line> |

## Implementation Notes
<key details from source code>
```

### git-historian
```
You are researching React's <TOPIC>.

CRITICAL: Do NOT rely on your prior knowledge. Only report what you find in git history.

Your task: Find commit messages that explain <TOPIC> design decisions.

1. Run: cd .claude/react && git log --all --grep="<topic>" --oneline -50
2. For significant commits, read full message: git show <hash> --stat
3. Look for:
   - Initial introduction of the API
   - Bug fixes (reveal edge cases)
   - Behavior changes
   - Deprecation notices

Format your output as:
## Key Commits
### <short hash> - <subject>
**Date:** <date>
**Context:** <why this change was made>
**Impact:** <what behavior changed>
```

### pr-researcher
```
You are researching React's <TOPIC>.

CRITICAL: Do NOT rely on your prior knowledge. Only report what you find in PRs.

Your task: Find PRs that introduced or modified <TOPIC>.

1. Run: gh pr list -R facebook/react --search "<topic>" --state all --limit 20 --json number,title,url
2. For promising PRs, read details: gh pr view <number> -R facebook/react
3. Look for:
   - The original RFC/motivation
   - Design discussions in comments
   - Alternative approaches considered
   - Breaking changes

Format your output as:
## Key PRs
### PR #<number>: <title>
**URL:** <url>
**Summary:** <what it introduced/changed>
**Design Rationale:** <why this approach>
**Discussion Highlights:** <key points from comments>
```

### issue-hunter
```
You are researching React's <TOPIC>.

CRITICAL: Do NOT rely on your prior knowledge. Only report what you find in issues.

Your task: Find issues that reveal common confusion about <TOPIC>.

1. Search facebook/react: gh issue list -R facebook/react --search "<topic>" --state all --limit 20 --json number,title,url
2. Search reactjs/react.dev: gh issue list -R reactjs/react.dev --search "<topic>" --state all --limit 20 --json number,title,url
3. For each issue, identify:
   - What the user was confused about
   - What the resolution was
   - Any gotchas revealed

Format your output as:
## Common Confusion
### Issue #<number>: <title>
**Repo:** <facebook/react or reactjs/react.dev>
**Confusion:** <what they misunderstood>
**Resolution:** <correct understanding>
**Gotcha:** <if applicable>
```

### types-inspector
```
You are researching React's <TOPIC>.

CRITICAL: Do NOT rely on your prior knowledge. Only report what you find in type definitions.

Your task: Find and compare Flow and TypeScript type signatures for <TOPIC>.

1. Flow types (source of truth): Search .claude/react/packages/*/src/*.js for @flow annotations related to <topic>
2. TypeScript types: Search .claude/react/packages/*/index.d.ts and @types/react
3. Compare and note any discrepancies

Format your output as:
## Flow Types (Source of Truth)
**File:** <path>
```flow
<exact type definition>
```

## TypeScript Types
**File:** <path>
```typescript
<exact type definition>
```

## Discrepancies
<any differences between Flow and TS definitions>
```
