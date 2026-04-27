---
source: "Optimize Codex just like your Claude Code setup (X/Twitter post, 4 tips)"
date: 2026-04-27
status: integrated
---

## Source Summary

**主張**: Codex CLI を Claude Code 並みに最適化するには 4 ステップで足りる: (1) AGENTS.md (CLAUDE.md と同じ階層), (2) config.toml (settings.json 相当), (3) Skills (claude→codex copy/symlink), (4) Hooks (.py/.sh の移動)。

**手法**:
- AGENTS.md を `~/.codex/AGENTS.md` + `.codex/AGENTS.md` + subdir で管理。`/init` で skeleton 生成。petekp/claude-code-setup で symlink。
- config.toml で model/sandbox/hooks/MCP を global/project/local 階層に配置。`/config` で skeleton 生成。
- Skills は agentskills.io 標準で portable。`~/.claude/skills/<name>/` を `~/.codex/skills/<name>/` にコピー。ariccb/sync-claude-skills-to-codex で symlink。`claude-to-codex` community skill が自動適応。
- Codex は最近 hooks framework を stable 化 (lighter、command-focused)。`.claude/hooks/*.{sh,py}` を `~/.codex/hooks/` に移動可能。

**根拠**: 著者の体験談ベース、データ・出典なし。
**前提条件**: greenfield setup の場合、または Claude Code 設定が小規模な場合に有効。

## Critical Self-Reflection

初期分析で記事の 4 項目だけをチェックして「2 項目は Already、Hooks は N/A、Skills は Partial」と表面判定した。ユーザーから「見落としは問題すぎる。手を抜くな」と指摘を受け、現状調査を機械的に拡張した結果、**追加 9 項目の見落とし**を検出。失敗パターンを `feedback_absorb_thoroughness.md` に記録。

## Gap Analysis (Pass 1: 存在チェック)

### 記事の 4 項目

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | AGENTS.md 階層 | **Already (強化不要)** | `~/.codex/AGENTS.md` 91行 + `dotfiles/AGENTS.md` 99行 + project-level 3件。Karpathy 4原則・Mandatory Skills・Security profile 等網羅。Nix home-manager で symlink 管理 |
| 2 | config.toml | **Already (強化不要)** | 96行で profile 6種 (fast/frontend/review/research/security/resume) + MCP 4種 + agents (max_threads=4, max_depth=1) + memories + plugins。記事の例を上回る |
| 3 | Skills sync (bulk copy) | **棄却** | Codex 批評で `careful/freeze` 等 Claude 固有 hook 前提が portable でないと判明。bulk symlink (ariccb 方式) は危険 |
| 4 | Hooks framework | **Gap (Partial)** ⚠️ 重大変更 | Codex CLI v0.124.0 で `codex_hooks stable true`。`developers.openai.com/codex/config-reference` に Hooks セクションあり。**ローカル `[hooks]` 設定なし** → 採択 |

### 周辺領域の追加調査 (見落とし発見)

| # | 領域 | 判定 | 詳細 |
|---|------|------|------|
| G5 | Codex slash commands | **Gap** | Claude 32個 vs Codex 0個 (`~/.codex/commands/` 不存在)。`/spec`, `/spike`, `/review`, `/commit`, `/improve`, `/absorb` 等が Codex で使えない |
| G6 | Codex agents drift | **Gap (最大)** | Claude 33 vs Codex 7。**26 agents が未移植** (security-reviewer, code-reviewer, edge-case-hunter, silent-failure-hunter, comment-analyzer, test-engineer 等) |
| G7 | MCP config drift (逆方向) | **Gap (Claude側)** | `~/.mcp.json` 2件、`~/.codex/config.toml` 4件。**Claude側に deepwiki + openaiDeveloperDocs が欠落** |
| G8 | Codex plugins 未活用 | **Partial (要選別)** | 116 plugin cached、有効は `github@openai-curated` のみ。linear, notion, slack, stripe 等候補多数。実利用次第 |
| G9 | Codex stable features 未活用 | **Partial** | `guardian_approval`, `tool_search`, `tool_suggest`, `skill_mcp_dependency_install` が stable だが config に明示なし (default ON の可能性あり) |
| G10 | Codex `mcp-server` (Codex を MCP 化) | **N/A (棄却)** | YAGNI、現状のサブエージェント機構で十分 |
| G11 | CLAUDE.md vs AGENTS.md assembly | **N/A (棄却)** | 70行 vs 99行、diff 141行差異 → 重複度低、`instructions/` assembly の効果限定 |
| G12 | Codex `.system` skills | **Already** | imagegen, openai-docs, plugin-creator, skill-creator, skill-installer (built-in) |
| G13 | Claude hooks → Codex 移植 | **Gap (大規模)** | Claude side: PostToolUse 22, PreToolUse 9, SessionStart 5 等の 43 hook 設定 + Rust binary (claude-hooks) + Python scripts。記事の「ファイル移動」主張は本 user の setup には非現実的 |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | AGENTS.md (91行 global) | subdir hierarchy 強調 | サブディレクトリ AGENTS.md 一律追加 | **強化不要** (search sprawl 増加リスク、Codex は最も近い AGENTS.md を優先するため必要時のみで十分) |
| S2 | config.toml (96行 profiles) | `/config` skeleton 推奨 | 既存で profile 6種・MCP 4種 | **強化不要** (記事の例を上回る) |
| S3 | Skills (37個、6 dotfiles symlink) | bulk sync 推奨 | top 候補のみ厳選 port | **強化可能** → G2/G3 として採択 |

## Integration Decisions

### Gap / Partial 採択

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| G1 | Codex hooks pilot 1 本 | **採用** | 記事の主張が実は正しい。最小コスト (config.toml に数行) で hooks framework 実機検証 |
| G2 | dependency-auditor Codex 用 read-only port | **採用** | 既存 Codex skill に supply-chain skill なし |
| G3 | hook-debugger Codex 版 rewrite | **採用** | hooks stable 化により価値急上昇 |
| G5 | Codex slash commands top 5 移植 | **採用 (調査込み)** | Codex の commands ディレクトリ仕様を調査後、可能なら移植 |
| G6 | Codex agents top 5 移植 | **採用** | 33 vs 7 の drift は最大の機能差。reviewer 強化 (現状 reviewer.toml 1本のみ) |
| G7 | MCP sync (Claude 側 → 4件) | **採用** | 単純な追加、リサーチ強化 |
| G9 | Codex stable features 設定 | **採用 (AGENTS.md 追記)** | guardian_approval / tool_search / tool_suggest を AGENTS.md で明示活用 |
| G8 | Codex plugin 選別有効化 | **延期 (spec stub)** | ユーザー workflow 依存、別セッションで決定 |
| G13 | Claude hooks 全移植 | **延期 (spec stub)** | Rust binary + 43 hook 設定の移植は L 規模、別セッションで /epd 推奨 |

### 棄却

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| - | 全 130 Claude skills bulk sync (ariccb) | **棄却** | Claude 固有 hook 前提が portable でない、Pruning-First 違反 |
| - | petekp/claude-code-setup 丸ごと採用 | **棄却** | Nix home-manager で代替済 (`codex-exclude` パターンのみ参考) |
| - | claude-to-codex 自動変換 skill | **棄却** | 品質未成熟 (5⭐, 7 commits) |
| - | AGENTS.md subdir 拡張 | **棄却** | search sprawl 増加 |
| - | `instructions/` assembly pattern | **棄却** | 実測 141 行差異で重複度低、効果限定 |
| - | Codex を MCP server 化 | **棄却** | YAGNI |
| - | Codex Cloud (experimental) | **棄却** | 未要求機能 |

## Side Findings (本タスクスコープ外)

- `~/.agents/skills/` と `~/dotfiles/.agents/skills/` で **9 件の skill conflict** (Gemini ログ確認)。別途 `/skill-audit` で統合推奨

## External Critique Summary

### Codex (codex-rescue subagent)
- 記事 #4 の「Codex hooks framework」主張は**事実** (release v0.124.0 で stable 化、2026-04-23 推定)
- 記事 #3 の bulk sync は危険 (`careful/freeze` 等で実証)
- 採択 3 件 / 棄却 4 件 / 要再検証 1 件 の助言を受領
- Top 5 移植候補: dependency-auditor, hook-debugger, careful, freeze, skill-audit

### Gemini
- capacity 切れで empty return (既知パターン)
- 補完されず Codex 批評単独で判定

### 記事の著者バイアス
- petekp は claude-code-setup repo オーナー、第三者ツール推奨にバイアスあり
- ariccb の "identical SKILL.md formats" 主張は Codex 批評で反証済 (Claude 固有 frontmatter は要 pruning)
- 記事内の `claude-to-codex` community skill は `padmilkhandelwal/convert-claude-to-codex-skill` (5⭐, 未成熟)

## Plan

詳細は `docs/plans/active/2026-04-27-codex-parity-plan.md`。

### Task 1: G1 Codex hooks pilot
- **Files**: `.codex/config.toml` (1 file)
- **Changes**: `[hooks]` table 追加、PostToolUse `apply_patch` 後に lint warning 1 本
- **Size**: S

### Task 2: G7 MCP sync
- **Files**: `~/.mcp.json` (1 file)
- **Changes**: deepwiki + openaiDeveloperDocs を追加
- **Size**: S

### Task 3: G6 Agents top 5 port
- **Files**: `.codex/agents/{security_reviewer,edge_case_hunter,silent_failure_hunter,code_reviewer,test_analyzer}.toml` (5 files)
- **Changes**: Claude .md → Codex .toml 変換 (developer_instructions, model, sandbox_mode, approval_policy)
- **Size**: M

### Task 4: G2 dependency-auditor port
- **Files**: `~/.codex/skills/dependency-auditor/SKILL.md` (1 file via symlink to `.agents/skills/dependency-auditor/`)
- **Changes**: Claude 用から Agent/Write 削除、read-only バージョン
- **Size**: M

### Task 5: G3 hook-debugger Codex rewrite
- **Files**: `~/.codex/skills/hook-debugger/SKILL.md` (1 file)
- **Changes**: Claude path → Codex `[hooks]` config.toml 前提に rewrite
- **Size**: M

### Task 6: G5 Codex commands investigation + (port)
- **Files**: 調査結果次第。可能なら `~/.codex/commands/{commit,review,spec,rpi,checkpoint}.md`
- **Changes**: Codex CLI の commands 仕様確認 → 可能なら移植、不可なら spec として残す
- **Size**: S (調査) + M (実装、可能な場合)

### Task 7: G9 Stable features documentation
- **Files**: `dotfiles/.codex/AGENTS.md` (1 file)
- **Changes**: guardian_approval / tool_search / tool_suggest / skill_mcp_dependency_install の活用方針を追記
- **Size**: S

### Task 8 (deferred): G8 plugin 選別 + G13 hooks 全移植
- **Files**: `docs/specs/` に spec stub 作成
- **Changes**: spec として記録、別セッションで /epd 推奨
- **Size**: L (本セッションでは実施しない)

### Task 9: Codex Plan Gate
- **Files**: なし (review)
- **Changes**: `codex-plan-reviewer` で Plan 批評
- **Size**: -
