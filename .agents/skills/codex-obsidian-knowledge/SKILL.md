---
name: codex-obsidian-knowledge
description: "Codex から Obsidian Vault を検索・読むためのファイルシステム経路。Vault root の AGENTS.md / CLAUDE.md を読み、rg でノート検索し、出典パスと行番号つきで回答する。Triggers: 'Obsidian 読んで', 'Vault 検索', 'Vault から探して', 'ノート探して', 'Daily Note 確認', 'Obsidian 経路'. Do NOT use for: Claude Code plugin 固有の obsidian:* skill 呼び出し、ブラウザ操作、外部記事取得。"
platforms: [agents, codex]
---

# Codex Obsidian Knowledge

Codex が Obsidian Vault を「読める」状態にするための薄いファイルシステム bridge。
Claude Code の `obsidian@obsidian-skills` plugin や `obsidian:*` skill は前提にしない。

## Vault Path

既定の Vault は次。

```bash
${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}
```

まず以下で preflight する。

```bash
vault="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
test -d "$vault"
rg --hidden --files "$vault" -g '*.md' -g '!**/.obsidian/**' -g '!**/.trash/**' | sed -n '1,40p'
```

`Operation not permitted` が出たら、Vault が無いとは判断しない。macOS の Full Disk Access / Files and Folders 権限が足りない状態として報告し、Terminal / Codex を許可してもらう。

## Read Protocol

1. Vault root の `AGENTS.md`、なければ `CLAUDE.md` を読む。
2. 依頼が検索なら、まず `rg -n` で候補を絞る。
3. 回答には根拠ファイルを `path:line` で出す。
4. Vault に根拠がない判断は `推測:` と明示する。
5. `.obsidian/`、`.trash/`、添付ファイルは明示依頼がない限り読まない。

## Search Patterns

トピック検索:

```bash
vault="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
rg -n --hidden -S "<keyword>" "$vault" -g '*.md' -g '!**/.obsidian/**' -g '!**/.trash/**'
```

Daily Note:

```bash
vault="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
today="$(date +%Y-%m-%d)"
rg --hidden --files "$vault/07-Daily" -g "${today}.md"
```

Inbox:

```bash
vault="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
rg --hidden --files "$vault/00-Inbox" -g '*.md' | sort | tail -40
```

## Write Rules

- 読み取りは通常タスクとして実行してよい。
- Vault への書き込みは、ユーザーが明示した場合だけ行う。
- dotfiles 以外の Vault path は sandbox 外書き込みになることがあるため、承認が必要なら要求する。
- 書く場合は既存の Vault root `AGENTS.md` / `CLAUDE.md` の命名・リンク・frontmatter 規約に合わせる。

## Boundaries

- これは MCP connector ではなく、filesystem + `rg` の Codex-native route。
- Claude 固有の `Agent`、`AskUserQuestion`、slash command、`obsidian:*` plugin skill をそのまま実行しない。
- `.config/claude/scripts/runtime/*` は Claude CLI 前提のものがあるため、Codex からは内容確認なしに流用しない。
