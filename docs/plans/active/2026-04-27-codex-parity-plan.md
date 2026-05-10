# Codex/Claude Parity Integration Plan

**Source**: [docs/research/2026-04-27-codex-claude-parity-absorb-analysis.md](../../research/2026-04-27-codex-claude-parity-absorb-analysis.md)
**Date**: 2026-04-27
**Scale**: L (8 tasks across config / agents / skills / docs)
**Workflow stage**: Plan → (Codex Plan Gate) → Implement → Review

## Goal

Codex CLI セットアップを Claude Code 並みに引き上げる。**ただし Pruning-First** — 全 sync ではなく価値の高い厳選のみ。

## Success Criteria

- ✅ `~/.codex/config.toml` に `[hooks]` 1 本以上配置 (codex_hooks stable feature 実機検証)
- ✅ `~/.mcp.json` に Codex 側と同等の MCP 4 件
- ✅ `.codex/agents/` に reviewer 系 5 agents 追加 (現行 7 → 12)
- ✅ `.codex/skills/` に dependency-auditor + hook-debugger 追加 (現行 6 dotfiles symlink → 8)
- ✅ Codex slash commands の仕様を確認し、可能な範囲で port
- ✅ `dotfiles/.codex/AGENTS.md` に未活用 stable feature の活用方針を明示
- ✅ G8 / G13 は spec stub として記録、別セッションで実装

## Reversibility & Pre-mortem

### Reversible 判定
- 全タスクが additive (既存ファイルを書き換えるのは config.toml の hooks 追加のみ)
- 撤退条件: hooks pilot で誤発火が頻発 → `[hooks]` セクション削除のみ
- agent / skill 移植: 削除も symlink 解除も容易

### 主な失敗モード
1. **Codex hooks 仕様の誤認** → mitigation: 公式 docs (`developers.openai.com/codex/config-reference`) を pilot 前に確認
2. **agent .toml schema 互換性問題** → mitigation: 既存の `debugger.toml` 等 7 件を rigorously template として使う
3. **Codex slash commands ディレクトリ非対応** → mitigation: 調査して非対応なら spec stub に降格
4. **既存 symlink 衝突 (dotfiles/.agents → ~/.codex/skills)** → mitigation: 既存 6 symlink パターンに従う

## Tasks

### Phase A: Low-risk additions (config + MCP)

#### Task A1: G1 Codex hooks pilot

**⚠️ Pre-flight (Plan Gate 修正)**:
- 既知バグ [#19199](https://github.com/openai/codex/issues/19199): v0.124.0 で `codex_hooks=true` 設定時にクラッシュ報告あり
- mitigation: 公式 docs のスキーマを **二層構造で厳密に守る**: `[[hooks.<Event>]]` (外側 matcher) + `[[hooks.<Event>.hooks]]` (内側 command 配列)
- rollback: 起動失敗時は `[features] codex_hooks = false` に変更 → 設定削除

**Files**: `dotfiles/.codex/config.toml`
**Changes** (公式: https://developers.openai.com/codex/hooks):
```toml
[features]
codex_hooks = true  # **必須** — false/未設定だと hooks がサイレントに無視される

[[hooks.PostToolUse]]
matcher = "apply_patch"

[[hooks.PostToolUse.hooks]]
type = "command"
command = "echo '[codex hook pilot] apply_patch completed'"
timeout = 5
statusMessage = "Pilot hook firing"
```

**Verification**:
1. `codex --version` で v0.124.0 以上確認
2. 設定追加前: `codex exec --skip-git-repo-check -p fast 'echo before-hook-pilot'` (起動確認)
3. 設定追加
4. `codex exec --skip-git-repo-check -p fast 'apply_patch test trigger'` で hook 発火確認
5. 起動失敗時の rollback: `codex_hooks = false` で再起動

**Size**: S

#### Task A2: G7 MCP sync
**Files**: `~/.mcp.json`
**Changes**: `deepwiki` + `openaiDeveloperDocs` 追加
```json
{
  "mcpServers": {
    "playwright": {...既存...},
    "context7": {...既存...},
    "deepwiki": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic-ai/deepwiki-mcp@latest"]
    },
    "openaiDeveloperDocs": {
      "type": "http",
      "url": "https://developers.openai.com/mcp"
    }
  }
}
```
**Verification**: Claude Code 再起動 → `/mcp` で 4 件確認
**Size**: S

### Phase B: Agents migration (G6)

#### Task B1: Claude → Codex agent 変換テンプレート確認
**Files**: 読み取りのみ (`dotfiles/.codex/agents/debugger.toml` をテンプレートとして使用)
**Verification**: 既存 7 件の TOML schema 共通点を抽出 (name, description, developer_instructions, model, model_reasoning_effort, sandbox_mode, approval_policy, nickname_candidates)

#### Task B2: 5 agents 移植

**選定基準** (Plan Gate 修正):
- **security_reviewer**: 既存 `security_auditor.toml` あるが Claude `security-reviewer` の OWASP/trust boundary 観点を補完
- **edge_case_hunter**: 既存 agents に該当なし、明確な gap
- **silent_failure_hunter**: 既存 agents に該当なし、明確な gap
- **code_reviewer**: 既存 `reviewer.toml` あるが Claude `code-reviewer` の包括チェックを補完。**重複確認**: reviewer.toml の内容を確認後に意義確認
- **test_engineer** (← test_analyzer から変更): `validation_explorer.toml` と nickname `validator` 衝突回避

**Files** (新規):
- `dotfiles/.codex/agents/security_reviewer.toml`
- `dotfiles/.codex/agents/edge_case_hunter.toml`
- `dotfiles/.codex/agents/silent_failure_hunter.toml`
- `dotfiles/.codex/agents/code_reviewer.toml`
- `dotfiles/.codex/agents/test_engineer.toml` (← test_analyzer 改名)

**Source**: `~/.claude/agents/{name}.md` の description + 主要 instruction を抽出
**Constraint**:
- Codex 用は **read-only sandbox + approval_policy = "never"** 推奨 (既存 debugger.toml に準拠)
- Claude 固有 tool 名 (`Agent`, `AskUserQuestion`) を `developer_instructions` から除去
- `model = "gpt-5.4"` 統一 (深い推論)

**Verification**: `codex exec --skip-git-repo-check -m gpt-5.4 -p review "agents 一覧確認"` で discovery 確認
**Size**: M (5 files、各 15-30 行)

### Phase C: Skills (G2 + G3)

#### Task C1: G2 dependency-auditor port
**Files**:
- `dotfiles/.agents/skills/dependency-auditor/SKILL.md` (新規、共有)
- `~/.codex/skills/dependency-auditor` symlink → 上記
- `~/.claude/skills/dependency-auditor` 既存 (要更新検討)

**Source**: `~/.claude/skills/dependency-auditor/SKILL.md`
**Changes**:
- `allowed-tools` から `Agent`, `Write` 削除 (read-only)
- frontmatter の Claude 固有部分削除
- 本文を Codex 文脈に書き換え (Claude `Bash` → Codex `shell`)

**Verification**: `~/.codex/skills/dependency-auditor/SKILL.md` 読み込み確認、`codex exec` で skill discovery 確認
**Size**: M

#### Task C2: G3 hook-debugger Codex rewrite
**Files**:
- `dotfiles/.agents/skills/hook-debugger-codex/SKILL.md` (Codex 専用として別名で新規)
- `~/.codex/skills/hook-debugger-codex` symlink

**Source**: `~/.claude/skills/hook-debugger/SKILL.md`
**Changes**:
- Claude path (`~/.claude/settings.json`) → Codex path (`~/.codex/config.toml [hooks]`, `~/.codex/hooks.json`)
- Claude hook event 名 (`PreToolUse`, `PostToolUse`, `SessionStart`) → Codex hook event 名 (要調査)
- Python script 前提 → bash + JSON I/O 前提

**Note**: 既存 `~/.claude/skills/hook-debugger/` は **そのまま維持** (Claude 用)。Codex 用は別名で並存。
**Size**: M

### Phase D: Slash commands (G5) — 調査主導

#### Task D1: Codex commands 仕様調査
**Investigation**:
- `~/.codex/commands/` ディレクトリは Codex CLI で読まれるか?
- Codex のスラッシュコマンドは plugin 経由のみか?
- 公式 docs / GitHub issues で確認

**Output**: 調査結果を本 plan に追記、可能性ありならば D2 へ進む、不可なら D3 へ降格

#### Task D2 (条件付き): top 5 commands 移植
**Files** (条件付き):
- `~/.codex/commands/commit.md`
- `~/.codex/commands/review.md`
- `~/.codex/commands/spec.md`
- `~/.codex/commands/rpi.md`
- `~/.codex/commands/checkpoint.md`

**Source**: `~/.config/claude/commands/{name}.md`
**Changes**:
- frontmatter の Claude 固有 (`allowed-tools`, `argument-hint`) 削除
- 本文の Claude tool 呼び出し (`Skill`, `Agent`) → Codex 表現

#### Task D3 (代替): spec stub
**Files**: `docs/specs/2026-04-27-codex-slash-commands-spec.md`
**Changes**: Codex commands 機能の仕様提案、別セッションで実装

### Phase E: Documentation (G9)

#### Task E1: AGENTS.md に Codex stable features の活用方針を追記
**Files**: `dotfiles/.codex/AGENTS.md` (Mandatory Skill Usage の後に新セクション追加)

**Changes**: 以下の 4 stable features の使用ガイドを追記
- `guardian_approval` — 危険コマンドの追加承認層
- `tool_search` — 大量 tool から関連検索 (deferred tools)
- `tool_suggest` — tool 推薦
- `skill_mcp_dependency_install` — skill が要求する MCP の自動インストール

**Verification**: `codex exec` で再読み込み、AGENTS.md の参照確認
**Size**: S

### Phase F: Spec stubs for deferred items

#### Task F1: G8 plugin selection spec
**Files**: `docs/specs/2026-04-27-codex-plugin-selection.md`
**Changes**: Codex 116 plugins から実利用 plugin を選別する spec。User workflow 依存項目 (linear / notion / slack / vercel など) のリスト化。別セッションで `/spec` → `/spike` → 採用判断

#### Task F2: G13 Claude hooks → Codex 移植 spec
**Files**: `docs/specs/2026-04-27-claude-hooks-codex-migration.md`
**Changes**: 43 hook 設定 + Rust binary (claude-hooks) + Python scripts の Codex 移植戦略。Phase 分割 (top 5 → top 10 → 全)

### Phase G: Index updates

#### Task G1: Memory index update
**Files**:
- `~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/MEMORY.md` (ポインタ追加)
- `dotfiles/docs/research/_index.md` (新エントリ)

**Changes**: 1 行ずつ追加

## Out of Scope (本 plan では実施しない)

- ❌ 全 130 Claude skills の Codex sync (Pruning-First 違反)
- ❌ petekp/claude-code-setup の丸ごと採用 (Nix で代替済)
- ❌ AGENTS.md subdir 拡張
- ❌ `instructions/{common,*-only}.md` assembly pattern
- ❌ Codex を MCP server 化 (YAGNI)
- ❌ Codex Cloud (experimental)

## Implementation Order

1. **A1 (Codex hooks 仕様調査) → A1 実装**: 最小コストで実機検証
2. **A2 (MCP sync)**: 1 ファイル編集
3. **B1 → B2**: agents 5 件移植 (template 確認後)
4. **C1, C2**: skills 2 件移植
5. **D1 (調査) → D2 or D3**: commands 移植 or spec
6. **E1**: AGENTS.md 追記
7. **F1, F2**: deferred spec stub
8. **G1**: index 更新
9. **Final**: Codex Plan Gate (`codex-plan-reviewer`)、Review Gate (`codex-reviewer`)

## Validation

各 phase 完了後:
- `codex exec --skip-git-repo-check -p resume` で discovery 確認
- `task validate-configs` (dotfiles task)
- `task validate-symlinks` (dotfiles task)
