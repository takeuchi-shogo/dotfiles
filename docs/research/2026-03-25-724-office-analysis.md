---
source: https://github.com/wangziqi06/724-office
date: 2026-03-25
status: integrated
---

## Source Summary

Self-evolving AI Agent system. ~3500 lines pure Python, zero framework dependency, 26 tools, 24/7 production.

**Key patterns**:
1. LLM compression memory pipeline: session overflow -> LLM structured fact extraction -> embedding -> cosine dedup (0.92) -> LanceDB. Background thread auto-execution
2. MCP client auto-recovery: JSON-RPC stdio/HTTP, crash detect -> 1x reconnect -> tool re-discovery
3. Personality file separation: SOUL.md (personality) / AGENT.md (ops procedures) / USER.md (user preferences) injected into system prompt
4. Self-check cron loop: nightly cron -> agent calls self_check tool -> LLM formats report -> owner notification
5. Runtime tool creation: agent dynamically generates Python functions (`create_tool`)
6. Zero-framework philosophy: `urllib.request` only, 3 dependencies (croniter, lancedb, websocket-client)
7. Session management: 40-message cap, overflow auto-compression, image_url -> [image] strip on save
8. Tool decorator pattern: `@tool(name, desc, schema)` one-line registration

**Context**: 825 stars, runs on Jetson Orin Nano (8GB). Single-agent, single-LLM design.

## Gap Analysis

### Gap / Partial / N/A

| # | Pattern | Verdict | Current State |
|---|---------|---------|---------------|
| 1 | LLM compression memory (auto fact extraction + vector dedup) | **Partial** | `analyze-tacit-knowledge` provides equivalent functionality but manual trigger only. No session overflow -> auto-compress mechanism |
| 2 | MCP client auto-recovery | **N/A** | Claude Code manages MCP connections internally. User-side reconnect logic unnecessary |
| 3 | Personality file separation (SOUL/AGENT/USER) | **Partial** | `CLAUDE.md` (AGENT equivalent) + `memory/user_*.md` (USER equivalent) exist. SOUL (tone) via `/persona`. No auto-injection at session start |
| 4 | Self-check cron loop | **Gap** | `/check-health` is manual only. `/schedule` skill exists but no periodic health check configured |
| 5 | Runtime tool creation | **N/A** | Skill system is superior. Dynamic code generation violates `agency-safety-framework.md` policy |
| 6 | Zero-framework philosophy | **Already (no enhancement)** | KISS/YAGNI codified in CLAUDE.md |
| 7 | Session overflow image strip | **N/A** | Claude Code manages context internally |
| 8 | Tool decorator pattern | **Already (no enhancement)** | SkillNet 5D evaluation + relationship types is more advanced |

### Already Enhancement Analysis

| # | Existing Mechanism | Article Insight | Verdict |
|---|---|---|---|
| 6 | KISS/YAGNI principles | 724-office implements LLM + embedding + MCP with urllib.request only, 3 deps for production | **Already (no enhancement)** -- principle is codified; implementation decisions are project-specific |
| 8 | Skill system (SKILL.md) | `@tool` decorator = 1 function = 1 tool, no separate file | **Already (no enhancement)** -- SkillNet 5D evaluation is more advanced |

## Integration Decisions

Selected all 3 actionable items:

1. **[Partial -> Integrate]** Auto knowledge extraction at session end -- add hook to session-learner.py
2. **[Partial -> Integrate]** User profile auto-injection -- consolidate user_*.md for session-start reference
3. **[Gap -> Integrate]** Scheduled health check cron -- set up daily /check-health via /schedule

## Plan

### Task 1: Session-end auto knowledge extraction
- Modify `scripts/learner/session-learner.py` to suggest `/analyze-tacit-knowledge` when session has significant activity
- Inspired by 724-office `compress_async` auto-trigger pattern
- Scale: S (1 file)

### Task 2: User profile auto-injection
- Add consolidated user profile reference to session-start context
- Inspired by 724-office SOUL.md/USER.md separation
- Scale: S (1-2 files)

### Task 3: Scheduled health check
- Configure daily `/check-health` via `/schedule` skill
- Inspired by 724-office self_check cron pattern
- Scale: S (1 trigger)
