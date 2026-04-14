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
- `.codex/rules/`
  - Codex の exec policy surface
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

## Runtime Charter vs Harness Logic 分離

> 出典: Pan et al. 2026 "Natural-Language Agent Harnesses" — runtime skill (共有ポリシー) と harness skill (タスク固有ロジック) を分離し、runtime contamination を防ぐ

ハーネスを2層に分離する:

| 層 | 役割 | dotfiles での実体 | 変更頻度 |
|---|------|-----------------|---------|
| **Runtime Charter** | 全タスク共通のポリシー・制約・品質ゲート | `CLAUDE.md`, `settings.json` hooks, `references/workflow-guide.md` | 低（月次） |
| **Harness Logic** | タスクファミリ固有の制御ロジック | `skills/*/SKILL.md`, `agents/*.md`, タスク固有の plan | 高（日次） |

**Runtime Charter の責務**: オーケストレーション・委譲境界・完了ゲート・セキュリティポリシー
**Harness Logic の責務**: ステージ構成・ロール定義・ドメイン固有の検証・失敗時回復

**Runtime Contamination リスク**: 強い runtime charter がハーネスロジックの効果を吸収し、モジュール追加の効果測定を困難にする。新モジュールの効果検証時は、runtime charter の影響を意識する。

### Operational Contract（SOP として昇格した手順の I/O 契約）

> 出典: CREAO AI-First 統合 (2026-04-14) — SOP は単なる手順書ではなく入力・失敗分岐・終了条件を持つ運用契約

Runtime Charter に SOP を昇格させる際は、**Operational Contract** の 3 要素を必ず備える:

| 要素 | 定義 | 例（`/commit` skill） |
|---|---|---|
| **Input Conditions** | 起動の前提条件（必要な状態・ファイル・権限） | working tree が clean でない、ステージ済み変更がある |
| **Failure Branching** | 失敗時の分岐パス（rollback / retry / escalate） | hook 失敗 → 修正して新コミット作成（amend 禁止） |
| **Exit Criteria** | 終了条件（成功/失敗の判定基準） | `git log -1` で commit 確認、CI が走り出す |

3 要素を満たさない手順は Harness Logic 側（skill / agent）に留め、Runtime Charter には昇格させない。
昇格判定は `docs/guides/ai-workflow-audit.md` の **SOP Promotion Criteria** を参照。

## Durable State の3性質

> 出典: Pan et al. 2026 "Natural-Language Agent Harnesses" §2.4 — file-backed state モジュールの設計原則

永続状態を設計する際、以下の3性質を満たすこと:

| 性質 | 定義 | dotfiles での対応 |
|------|------|-----------------|
| **Externalized** | 状態はトランジェントなコンテキストではなくファイルに書き出す | Plan ファイル、checkpoint、Decision Log |
| **Path-Addressable** | 後続ステージがパス指定で正確に状態を再オープンできる | `tmp/plans/{name}.md`, `docs/plans/` |
| **Compaction-Stable** | コンテキスト圧縮・再起動・委譲後も状態が生存する | ファイルベースなので自動的に満たす。ただし状態を会話コンテキストにのみ保持するのは NG |

**設計チェック**: 新しい状態を導入する際「コンテキストが圧縮された後も、この情報は復元できるか？」を問う。答えが No なら、ファイルに書き出す。

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
  - exec policy rules (`.codex/rules/*.rules`)
  - MCP server configuration
  - Apps / connectors feature and app configuration
  - review / verification / search-first skills
  - checkpoint-resume skill
  - memory-capture skill
  - subagent runtime (`[agents]` - `max_threads`, `max_depth`)
  - custom agents (`.codex/agents/*.toml` - read-only explorer / reviewer / researcher / validation mapper)
  - subagent operation playbook (`docs/playbooks/codex-subagent-usage.md`)

## Runtime Integration Notes

- `personality`
  - global default として安定した行動原則だけを置く
  - 長さ、tone、表現形式、箇条書きの有無などは task prompt や skill で決める
- `commentary` と `final`
  - commentary は進捗共有と未検証項目の明示
  - final は完了済み、検証済み、または未達成の gap の明示
- subagent orchestration
  - 役割が明確で並列化できる read-heavy task だけに使う
  - `objective`、`scope`、`expected output` を親 agent が明示する
  - 編集、重複 findings の統合、validation 実行は親 agent が持つ
- compact / resume
  - compact 前に checkpoint を残す
  - resume 後も goal、completion criteria、pending validation は維持する
  - checkpoint や compacted state は要約として使い、必要なら git / filesystem で再検証する
- memory
  - repo ごとの stable learnings は `~/.codex/memories/<slug>-memory.md` と `~/.codex/memories/<slug>-learnings.jsonl` に残す
  - 一時的なログや transient failure は durable memory に昇格させない

## Rules

- agent 固有の保証を repo 共通 contract に混ぜない
- `AGENTS.md` は自然言語の行動方針、`.codex/rules/*.rules` は sandbox 外 command の機械判定として分離する
- exec policy は broad allow より minimal adoption を優先し、read-only prefix から始める
- validation は tool 不在だけで hard fail させない。必要なら skip を明示する
- 同じ friction を 2 回経験したら durable memory か skill へ昇格を検討する
