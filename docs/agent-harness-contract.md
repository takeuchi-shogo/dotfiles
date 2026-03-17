# Agent Harness Contract

この repo では、agent の能力を model 本体ではなく harness で補強する。

## Shared Invariants

- durable state は filesystem に残す
- 新規実装の前に既存の task / script / skill / MCP を調べる
- 完了宣言の前に最小限の validation を実行する
- 最新情報が必要な場合だけ Web / MCP を使う
- 長時間タスクは中断前に checkpoint を残す
- persistent personality と task ごとの output control を分離する
- compact / resume 前後で goal と completion criteria を勝手に変えない

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
- `~/.codex/skills/`, `~/.agents/skills/`
  - Codex skill discovery の compatibility surface
- `~/.claude/session-state/`, `~/.claude/agent-memory/`
  - Claude の checkpoint / learnings surface

## Scaffolding vs Harness 分離

OpenDev paper (arxiv 2603.05344) に基づくアーキテクチャ境界:

| 層 | フェーズ | 目的 | 実装 |
|---|---|---|---|
| **Scaffolding** | SessionStart (1回) | コールドスタート構築 — 状態復元、ツール登録 | `session-load.js`, `checkpoint_recover.py` |
| **Harness** | ツール実行毎 | ランタイムオーケストレーション — ポリシー強制、品質ゲート | PreToolUse/PostToolUse/Stop hooks |

- **Scaffolding は情報提供のみ** (stderr 出力) — ブロッキングしない
- **Harness はポリシー強制** (exit code 2 でブロック可能)
- 各フェーズは独立に最適化可能: scaffolding はコールドスタート遅延、harness は長期セッション生存率

## Claude-Specific Harness

- 実装場所: `.config/claude/settings.json`, `.config/claude/scripts/`
- 主な primitives:
  - hook-based formatting / policy checks
  - completion gate
  - checkpoint and recovery
  - compaction reminders
  - agent routing and learnings flush

### Hook 閾値サマリー（Obliviousness 対策）

エージェントが自分を保護しているインフラの具体的なパラメータ:

| Hook | 閾値 | 動作 |
|------|------|------|
| `output-offload.py` | 150行 or 6000文字超 | 全文を `/tmp/claude-tool-outputs/` に退避 |
| `golden-check.py` | 5分クールダウン/file:rule | 同一ファイル+ルールの重複警告を抑制 |
| `checkpoint_manager.py` | 15編集 / 60%コンテキスト / 30分 | いずれかで自動チェックポイント（5分クールダウン） |
| `suggest-compact.js` | 同一ファイル3回/10分 | 編集ループ検出。30/50編集でコンパクション提案 |
| `completion-gate.py` | MAX_RETRIES=2 | Ralph Loop + テスト失敗を2回まで差し戻し |
| `completion-gate.py` | 10編集以上 | Review Gate: `/review` 実行を提案（アドバイザリー） |
| `pre-commit-check.js` | パターンマッチ | `sk-`, `ghp_`, `AKIA` 等のシークレットをブロック |
| `protect-linter-config.py` | ファイル名一致 | `.eslintrc*`, `biome.json` 等の変更をブロック |
| `check_gp_blocking` (Rust) | パターンマッチ | GP-004 (空catch) / GP-005 (any型) の編集をブロック |
| `pre-compact-save.js` | PreCompact | 圧縮ガイダンス + アクティブプラン追跡 + offload索引 |

## Codex-Specific Harness

- 実装場所: `.codex/config.toml`, `.codex/AGENTS.md`, `.codex/agents/`, `.agents/skills/`
- 主な primitives:
  - profiles / sandbox / approval policy
  - MCP server configuration
  - review / verification / search-first skills
  - checkpoint-resume skill
  - memory-capture skill
  - subagent runtime (`[agents]` - `max_threads`, `max_depth`)
  - custom agents (`.codex/agents/*.toml` - read-only explorer / reviewer / researcher)

## Runtime Integration Notes

- `personality`
  - global default として安定した行動原則だけを置く
  - 長さ、tone、表現形式、箇条書きの有無などは task prompt や skill で決める
- `commentary` と `final`
  - commentary は進捗共有と未検証項目の明示
  - final は完了済み、検証済み、または未達成の gap の明示
- compact / resume
  - compact 前に checkpoint を残す
  - resume 後も goal、completion criteria、pending validation は維持する
  - checkpoint や compacted state は要約として使い、必要なら git / filesystem で再検証する
- memory
  - repo ごとの stable learnings は `~/.codex/memories/<slug>-memory.md` と `~/.codex/memories/<slug>-learnings.jsonl` に残す
  - 一時的なログや transient failure は durable memory に昇格させない

## Rules

- agent 固有の保証を repo 共通 contract に混ぜない
- validation は tool 不在だけで hard fail させない。必要なら skip を明示する
- 同じ friction を 2 回経験したら durable memory か skill へ昇格を検討する
