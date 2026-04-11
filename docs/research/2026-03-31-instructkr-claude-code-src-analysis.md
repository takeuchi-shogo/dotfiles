---
source: https://github.com/instructkr/claude-code/tree/main/src
date: 2026-03-31
status: analyzed
---

## Source Summary

`instructkr/claude-code` は Claude Code の `src/` 公開スナップショットを保持する archive。README の説明どおり、通常の開発用 repo というより 2026-03-31 の source exposure を受けて保存された mirror で、`src/` の静的読解に向く。今回 clone して確認した範囲では `src/` 配下だけで **1,902 files / 512,664 LOC**。

技術スタックは import と README から見る限り:
- Runtime: Bun
- UI: React + Ink
- CLI parsing: Commander
- Core integrations: Anthropic API, MCP, OAuth, plugin/skill system, remote bridge

## Architecture Map

### Core entrypoints

| File | Role |
|---|---|
| `src/main.tsx` | 起動順序の統括。MDM / keychain prefetch、feature-gated import、commands/tools 初期化 |
| `src/entrypoints/init.ts` | config 有効化、safe env 適用、mTLS/proxy、preconnect、remote settings/policy limits 準備 |
| `src/QueryEngine.ts` | 会話単位の stateful engine。message history、permission denial、file cache、usage を保持 |
| `src/query.ts` | model loop 本体。streaming、tool follow-up、fallback、compaction、retry の状態機械 |
| `src/cli/print.ts` | headless / SDK / remote path の巨大 runtime |
| `src/screens/REPL.tsx` | interactive Ink UI の中心 |

### Primary registries

| File | Role |
|---|---|
| `src/Tool.ts` | tool contract の中心。schema、permission、rendering、telemetry、concurrency/read-only 判定 |
| `src/tools.ts` | built-in tools registry。mode や deny rules を反映した tool pool 組み立て |
| `src/commands.ts` | slash commands registry。built-in / bundled skills / plugin / MCP skills を合成 |
| `src/state/AppStateStore.ts` | MCP / plugin / task / bridge / prompt state を含む session-wide store |

### Main subsystems

| Directory | Responsibility |
|---|---|
| `src/services/api/` | Anthropic API、retry、usage、files API、bootstrap |
| `src/services/mcp/` | MCP transport、auth、config、resource/tool discovery |
| `src/services/tools/` | tool execution、hook integration、tool orchestration |
| `src/tools/AgentTool/` | subagent spawn、background execution、worktree/remote isolation |
| `src/utils/plugins/` | plugin discovery、cache、marketplace、versioning |
| `src/skills/` | skills loading、frontmatter parsing、MCP skill builders |
| `src/bridge/` | remote/IDE bridge、session spawning、heartbeat、reconnect |
| `src/services/compact/` | auto/reactive compact、session memory compaction、cleanup |

## Key Flows

### 1. Startup path

- `main.tsx` は通常の import 前に `startMdmRawRead()` と `startKeychainPrefetch()` を走らせ、起動時レイテンシを削る。
- `init.ts` は trust 前に safe env のみ適用し、config / proxy / cert / graceful shutdown / telemetry bootstrap を準備する。
- 初期化時点で remote settings と policy limits の loading promise を先に張り、後続 subsystem が await できるようにしている。

### 2. Conversation path

- `QueryEngine.submitMessage()` が system prompt、user context、system context を組み立てる。
- `processUserInput()` で slash command や attachment を message history に落とし込む。
- `query()` が streaming を回し、assistant message 内の `tool_use` を収集し、tool 実行後に follow-up turn へ進む。
- transcript は API 応答前にも user message を先書きし、kill mid-request でも `--resume` 可能にしている。

### 3. Tool execution path

- `toolOrchestration.ts` は tool を concurrency-safe な read-only batch と serial batch に分割する。
- `toolExecution.ts` は `runPreToolUseHooks` → permission resolution → actual tool call → `runPostToolUseHooks` の順に処理する。
- hook は message 追加だけでなく updated input、stop continuation、hook-based permission decision まで差し込める。

### 4. Agent path

- `AgentTool` は subagent spawn の front door。
- agent は background / in-process / worktree isolation / remote isolation を切り替えられる。
- `runAgent.ts` は parent context を fork し、agent-specific MCP server を追加接続できる。

### 5. Headless / remote path

- `cli/print.ts` は SDK / CCR / remote session の実行面で、interactive path と別の主戦場。
- `bridge/bridgeMain.ts` は session spawn、heartbeat、token refresh、capacity wake を持つ poll-loop runtime。

## Important Design Patterns

### Recovery-first architecture

このコードベースは単純な chat loop よりも、失敗時の復旧に多くの複雑さを使っている。

- orphaned partial messages を tombstone 化
- prompt-too-long 時の auto/reactive compact
- transcript repair と resume 安定化
- tool result / tool use pairing repair
- streaming fallback 後の pending tool result discard

### Tool system is richer than function calling

`Tool.ts` の contract は単なる `name + schema + execute` ではない。以下まで標準化されている。

- permission checks
- user-facing rendering
- read/search/list classification
- auto-classifier input
- result truncation / persistence
- MCP metadata passthrough
- interrupt behavior

### Skills, commands, plugins are intentionally blended

`commands.ts` では built-in command、bundled skill、plugin skill、MCP skill をまとめて command space に統合する。`SkillTool` に見せる prompt command と slash command の境界は薄い。

### MCP is a platform, not an adapter

`services/mcp/client.ts` は transport だけでなく以下を持つ。

- stdio / SSE / streamable HTTP / websocket / SDK transport
- OAuth refresh と `needs-auth` cache
- timeout wrapping
- output truncation / binary persistence
- MCP skill fetch

### Feature-flag-heavy product layering

`feature('...')` の出現が非常に多く、単一コードベースで複数 product tier を同居させている。特に頻出:

- `KAIROS`
- `TRANSCRIPT_CLASSIFIER`
- `TEAMMEM`
- `VOICE_MODE`
- `BASH_CLASSIFIER`
- `COORDINATOR_MODE`
- `BRIDGE_MODE`
- `CONTEXT_COLLAPSE`

## Notable Findings

1. `src` snapshot は完全な pristine TypeScript source ではなく、一部に transformed output が混じる。
   - 例: `src/hooks/useCanUseTool.tsx` は `react/compiler-runtime` を直接 import している。
2. main thread だけでなく headless / SDK / remote path が同等以上に重要。
   - 特に `src/cli/print.ts` は 5.5k lines 超で、別プロダクト級の重さがある。
3. multi-agent は補助機能ではなく主軸。
   - `AgentTool`, `coordinator/`, task system, remote/worktree isolation まで一体化している。
4. prompt/cache stability をかなり気にしている。
   - mutable input の backfill を clone 上だけで行う、system prompt を fork child に持ち込む、cache break detection を持つ。
5. session state は UI state を超えて orchestration state になっている。
   - `AppStateStore.ts` に MCP / bridge / tasks / notifications / thinking / prompt suggestion が集約されている。

## Files To Read Next

優先順:

1. `src/main.tsx`
2. `src/entrypoints/init.ts`
3. `src/QueryEngine.ts`
4. `src/query.ts`
5. `src/Tool.ts`
6. `src/services/tools/toolExecution.ts`
7. `src/services/mcp/client.ts`
8. `src/tools/AgentTool/AgentTool.tsx`
9. `src/tools/AgentTool/runAgent.ts`
10. `src/cli/print.ts`

補助:

- `src/commands.ts`
- `src/tools.ts`
- `src/state/AppStateStore.ts`
- `src/services/api/claude.ts`
- `src/bridge/bridgeMain.ts`
- `src/skills/loadSkillsDir.ts`
- `src/utils/plugins/pluginLoader.ts`

## Caveats

- 今回の調査は `src/` 中心の静的読解。build 実行や test 実行はしていない。
- repo root の package metadata や bundler config は snapshot に含まれないため、一部の build/runtime 前提は import と README からの推定。
- 公開 archive 由来の snapshot なので、元の private/internal repo の全体像と完全一致する保証はない。
