---
source: "Como funciona realmente Claude Code (by Santi) - Spanish article on Claude Code internals"
date: 2026-03-23
status: skipped
---

## Source Summary

### Claims

Claude Code is an agent, not a chat. Understanding its 7 building blocks (Agent Loop, Tools, Memory, Hooks, Skills, SubAgents, MCP) enables developers to maximize its potential.

### Techniques

- **Agent Loop**: 3-phase cycle (gather context -> take action -> verify results), repeating until objective met
- **Tools**: Native tools (Read/Edit/Write/Bash/Grep/Glob/WebFetch/WebSearch) as the agent's interface to the local environment
- **Memory**: CLAUDE.md (3 tiers: global/project/rules) + Auto Memory for persistent context across sessions
- **Hooks**: 4 types (PreToolUse/PostToolUse/Notification/Stop) for deterministic behavior guarantees
- **Skills**: SKILL.md + templates/examples/scripts structure for repeatable workflows
- **SubAgents**: Separate context instances for parallel execution, context protection, and tool-restricted specialists
- **MCP**: Model Context Protocol for external service integration (GitHub, Slack, DB, Jira)

### Evidence

Author's practical experience (100+ Skills in production). No quantitative data.

### Preconditions

Beginner-to-intermediate Claude Code users. Assumes daily CLI usage for software engineering.

## Gap Analysis

| # | Technique | Verdict | Current State |
|---|-----------|---------|---------------|
| 1 | Agent Loop (gather/act/verify) | Already | 7-stage workflow (Plan->Risk->Implement->Test->Review->Verify->Security) in CLAUDE.md subsumes the 3-phase model |
| 2 | Tools usage patterns | Already | All native tools + Codex CLI + Gemini CLI integrated |
| 3 | CLAUDE.md 3-tier (global/project/rules) | Already | Progressive Disclosure: CLAUDE.md (~130 lines) + `<important if>` conditional tags + references/ + rules/ |
| 4 | Auto Memory periodic review | Already | MEMORY.md + memory/ directory. AutoEvolve daily loop maintains quality |
| 5 | `.claude/rules/` modular rules | Partial | Equivalent functionality via `references/` + `rules/` + `<important if>` tags. Official `.claude/rules/` glob-based activation unused, but current approach is more flexible |
| 6 | Hooks (4 types) | Already | All 4 types configured. golden-check, plan-lifecycle, completion-gate, protect-linter-config, output-offload, etc. |
| 7 | Skills (SKILL.md structure) | Already | 65+ Skills with skill-creator and skill-audit for quality management |
| 8 | SubAgents (context protection, parallelism, tool restrictions) | Already | 31+ custom agents with triage-router auto-routing and worktree isolation |
| 9 | MCP external integration | Already | Obsidian MCP, Discord MCP, Playwright MCP, etc. configured |
| 10 | Practical recommendations (5 items) | Already | All 5 implemented at scale |

## Integration Decisions

No items selected for integration. The article covers beginner-to-intermediate fundamentals that the current setup has fully implemented and extended beyond.

The single Partial item (`.claude/rules/`) was evaluated and determined to offer no practical benefit over the existing Progressive Disclosure architecture (`<important if>` tags + `references/` + `rules/`).
