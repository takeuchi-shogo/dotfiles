# Agent Harness Contract

この repo では、agent の能力を model 本体ではなく harness で補強する。

## Shared Invariants

- durable state は filesystem に残す
- 新規実装の前に既存の task / script / skill / MCP を調べる
- 完了宣言の前に最小限の validation を実行する
- 最新情報が必要な場合だけ Web / MCP を使う
- 長時間タスクは中断前に checkpoint を残す

## Durable State Surfaces

- `AGENTS.md`
  - repo 共通の行動 contract
- `Taskfile.yml`, `.bin/validate_*.sh`
  - deterministic verification surface
- `.mcp.json`
  - repo で使う external context surface
- `.agents/skills/`
  - repo-local workflow and policy surface
- `tmp/codex-state/`
  - Codex の short-term checkpoint surface
- `~/.codex/memories/`
  - Codex の durable memory surface
- `~/.claude/session-state/`, `~/.claude/agent-memory/`
  - Claude の checkpoint / learnings surface

## Claude-Specific Harness

- 実装場所: `.config/claude/settings.json`, `.config/claude/scripts/`
- 主な primitives:
  - hook-based formatting / policy checks
  - completion gate
  - checkpoint and recovery
  - compaction reminders
  - agent routing and learnings flush

## Codex-Specific Harness

- 実装場所: `.codex/config.toml`, `.codex/AGENTS.md`, `.agents/skills/`
- 主な primitives:
  - profiles / sandbox / approval policy
  - MCP server configuration
  - review / verification / search-first skills
  - checkpoint-resume skill
  - memory-capture skill

## Rules

- agent 固有の保証を repo 共通 contract に混ぜない
- validation は tool 不在だけで hard fail させない。必要なら skip を明示する
- 同じ friction を 2 回経験したら durable memory か skill へ昇格を検討する
