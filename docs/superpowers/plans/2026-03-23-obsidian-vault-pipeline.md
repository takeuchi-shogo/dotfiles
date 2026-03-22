# Obsidian Vault 自動蓄積パイプライン Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Claude Code のセッションデータ（memory, 日報, 暗黙知, 手動メモ）を Obsidian Vault に自動同期するパイプラインを構築する

**Architecture:** シェルスクリプト4本 + `/note` スキル1本。hook（memory 即時同期）と cron（日次バッチ3本）のハイブリッドトリガー。全スクリプトは `OBSIDIAN_VAULT_PATH` 環境変数で vault を解決し、冪等に動作する。

**Tech Stack:** Bash, jq, cron, Claude Code hooks (settings.json)

**Spec:** `docs/superpowers/specs/2026-03-23-obsidian-vault-pipeline-design.md`

---

## File Structure

```
dotfiles/
├── .config/zsh/core/
│   └── exports.zsh              (新規: OBSIDIAN_VAULT_PATH 定義)
├── .config/claude/
│   ├── scripts/runtime/
│   │   ├── sync-memory-to-vault.sh    (既存改修: DEST_DIR 08 + migration)
│   │   ├── sync-daily-report.sh       (新規)
│   │   ├── sync-session-insights.sh   (新規)
│   │   ├── sync-tacit-knowledge.sh    (新規)
│   │   └── note-to-vault.sh           (新規)
│   ├── skills/note/
│   │   └── SKILL.md                   (新規)
│   └── settings.json                  (hook 追加)
└── templates/obsidian-vault/
    └── CLAUDE.md                      (カスタマイズ)
```

---

### Task 1: 環境変数の設定

**Files:**
- Create: `.config/zsh/core/exports.zsh`

- [ ] **Step 1: exports.zsh を作成**

```bash
# Obsidian Vault
export OBSIDIAN_VAULT_PATH="$HOME/Documents/Obsidian Vault"
```

`.config/zsh/core/` に配置すれば `.zshrc` のローダーが自動で読み込む。

> **Note:** spec は `.zshenv` への追加と記載しているが、このリポジトリに `.zshenv` は存在しない。zsh 設定は `.config/zsh/` 配下に auto-loading される構成のため、`core/exports.zsh` に配置する。

- [ ] **Step 2: 読み込みを確認**

Run: `source ~/.config/zsh/.zshrc && echo "$OBSIDIAN_VAULT_PATH"`
Expected: `/Users/takeuchishougo/Documents/Obsidian Vault`

- [ ] **Step 3: Commit**

```bash
git add .config/zsh/core/exports.zsh
git commit -m "🔧 chore(zsh): add OBSIDIAN_VAULT_PATH environment variable"
```

---

### Task 2: sync-memory-to-vault.sh の改修

**Files:**
- Modify: `.config/claude/scripts/runtime/sync-memory-to-vault.sh:19` (DEST_DIR)

- [ ] **Step 1: DEST_DIR を変更し migration ロジックを追加**

`.config/claude/scripts/runtime/sync-memory-to-vault.sh` の変更:

1. Line 19: `DEST_DIR="07-Agent-Memory"` → `DEST_DIR="08-Agent-Memory"`
2. `mkdir -p "$TARGET"` の**直後**に migration ロジックを追加（`$TARGET` ディレクトリが作成済みであることを前提とする）:

```bash
# Migration: 07 → 08
OLD_TARGET="$VAULT_PATH/07-Agent-Memory"
if [[ -d "$OLD_TARGET" ]] && [[ ! -d "$TARGET" ]]; then
    mv "$OLD_TARGET" "$TARGET"
    echo "[sync-memory] Migrated 07-Agent-Memory → 08-Agent-Memory"
elif [[ -d "$OLD_TARGET" ]] && [[ -d "$TARGET" ]]; then
    # Both exist: merge old into new
    cp -n "$OLD_TARGET"/*.md "$TARGET/" 2>/dev/null || true
    rm -rf "$OLD_TARGET"
    echo "[sync-memory] Merged 07-Agent-Memory into 08-Agent-Memory"
fi
```

3. `MEMORY_SOURCES` をグロブに拡張:

```bash
MEMORY_SOURCES=("$HOME/.claude/projects"/*/memory)
```

- [ ] **Step 2: dry-run で動作確認**

Run: `OBSIDIAN_VAULT_PATH="$HOME/Documents/Obsidian Vault" bash ~/.config/claude/scripts/runtime/sync-memory-to-vault.sh --dry-run`
Expected: `[dry-run] would sync: ...` と表示されるか、または `[sync-memory] OBSIDIAN_VAULT_PATH not set, skipping` でないこと

- [ ] **Step 3: 実際に同期を実行**

Run: `OBSIDIAN_VAULT_PATH="$HOME/Documents/Obsidian Vault" bash ~/.config/claude/scripts/runtime/sync-memory-to-vault.sh`
Expected: `[sync-memory] Synced N file(s) to .../08-Agent-Memory`

- [ ] **Step 4: vault 側を確認**

Run: `ls "$HOME/Documents/Obsidian Vault/08-Agent-Memory/" | head -5`
Expected: memory ファイルが存在する

- [ ] **Step 5: Commit**

```bash
git add .config/claude/scripts/runtime/sync-memory-to-vault.sh
git commit -m "✨ feat(obsidian): update sync-memory-to-vault for 08-Agent-Memory with migration"
```

---

### Task 3: sync-daily-report.sh の作成

**Files:**
- Create: `.config/claude/scripts/runtime/sync-daily-report.sh`

- [ ] **Step 1: スクリプトを作成**

```bash
#!/usr/bin/env bash
# sync-daily-report.sh — ~/daily-reports/*.md → Obsidian Vault 07-Daily/
set -euo pipefail

VAULT_PATH="${OBSIDIAN_VAULT_PATH:-}"
if [[ -z "$VAULT_PATH" ]]; then
    echo "[sync-daily] OBSIDIAN_VAULT_PATH not set, skipping" >&2
    exit 0
fi

SOURCE_DIR="$HOME/daily-reports"
TARGET="$VAULT_PATH/07-Daily"

[[ -d "$SOURCE_DIR" ]] || { echo "[sync-daily] No daily-reports dir, skipping" >&2; exit 0; }
mkdir -p "$TARGET"

synced=0

for src_file in "$SOURCE_DIR"/*.md; do
    [[ -f "$src_file" ]] || continue
    filename="$(basename "$src_file")"
    dest_file="$TARGET/$filename"

    # Skip if already synced and source hasn't changed
    if [[ -f "$dest_file" ]] && [[ ! "$src_file" -nt "$dest_file" ]]; then
        continue
    fi

    synced_at="$(TZ=Asia/Tokyo date +%Y-%m-%dT%H:%M:%S+09:00)"

    # Check if source has frontmatter
    if head -1 "$src_file" | grep -q "^---"; then
        awk -v ts="$synced_at" '
            BEGIN { fence=0 }
            /^---$/ { fence++
                if (fence == 2) {
                    print "obsidian_tags: [agent/daily-report]"
                    print "synced_at: " ts
                }
            }
            { print }
        ' "$src_file" > "$dest_file"
    else
        {
            echo "---"
            echo "obsidian_tags: [agent/daily-report]"
            echo "synced_at: $synced_at"
            echo "---"
            echo ""
            cat "$src_file"
        } > "$dest_file"
    fi

    synced=$((synced + 1))
done

if [[ $synced -gt 0 ]]; then
    echo "[sync-daily] Synced $synced file(s) to $TARGET"
fi
```

- [ ] **Step 2: 実行権限を付与**

Run: `chmod +x ~/.config/claude/scripts/runtime/sync-daily-report.sh`

- [ ] **Step 3: テスト用の日報がなければ /daily-report で生成、あれば既存ファイルで動作確認**

Run: `OBSIDIAN_VAULT_PATH="$HOME/Documents/Obsidian Vault" bash ~/.config/claude/scripts/runtime/sync-daily-report.sh`
Expected: `[sync-daily] Synced N file(s)` または `No daily-reports dir, skipping`

- [ ] **Step 4: 冪等性確認（2回目はスキップ）**

Run: `OBSIDIAN_VAULT_PATH="$HOME/Documents/Obsidian Vault" bash ~/.config/claude/scripts/runtime/sync-daily-report.sh`
Expected: 何も出力されない（全てスキップ）

- [ ] **Step 5: Commit**

```bash
git add .config/claude/scripts/runtime/sync-daily-report.sh
git commit -m "✨ feat(obsidian): add sync-daily-report.sh for vault pipeline"
```

---

### Task 4: sync-session-insights.sh の作成

**Files:**
- Create: `.config/claude/scripts/runtime/sync-session-insights.sh`

- [ ] **Step 1: スクリプトを作成**

```bash
#!/usr/bin/env bash
# sync-session-insights.sh — セッション JSONL → Obsidian Vault 00-Inbox/
set -euo pipefail

VAULT_PATH="${OBSIDIAN_VAULT_PATH:-}"
if [[ -z "$VAULT_PATH" ]]; then
    echo "[sync-insights] OBSIDIAN_VAULT_PATH not set, skipping" >&2
    exit 0
fi

TARGET="$VAULT_PATH/00-Inbox"
mkdir -p "$TARGET"

TODAY="$(TZ=Asia/Tokyo date +%Y-%m-%d)"
DEST_FILE="$TARGET/insight-${TODAY}.md"

# Idempotent: skip if already generated today
if [[ -f "$DEST_FILE" ]]; then
    exit 0
fi

# Collect today's sessions from all projects
sessions=""
for index_file in "$HOME"/.claude/projects/*/sessions-index.json; do
    [[ -f "$index_file" ]] || continue
    result=$(jq -c --arg date "$TODAY" '
        .entries[]
        | select(
            (.created // "" | startswith($date)) or
            (.modified // "" | startswith($date))
        )
        | {sessionId, firstPrompt, summary, projectPath, fullPath}
    ' "$index_file" 2>/dev/null) || continue
    [[ -n "$result" ]] && sessions+="$result"$'\n'
done

# No sessions today
if [[ -z "${sessions:-}" ]]; then
    exit 0
fi

synced_at="$(TZ=Asia/Tokyo date +%Y-%m-%dT%H:%M:%S+09:00)"

# Build the insight note
{
    echo "---"
    echo "tags: [agent/session-insight, status/seed]"
    echo "created: $TODAY"
    echo "synced_at: $synced_at"
    echo "---"
    echo ""
    echo "# Session Insights - $TODAY"
    echo ""

    # Process each session
    echo "$sessions" | jq -rs '
        group_by(.projectPath)[]
        | "## " + (.[0].projectPath | split("/") | last) + "\n" +
          ([.[] | "- **" + (.firstPrompt // "no prompt" | .[0:100]) + "**\n  " + (.summary // "no summary" | .[0:200])] | join("\n"))
    ' 2>/dev/null || echo "(sessions could not be parsed)"

} > "$DEST_FILE"

echo "[sync-insights] Generated $DEST_FILE"
```

- [ ] **Step 2: 実行権限を付与**

Run: `chmod +x ~/.config/claude/scripts/runtime/sync-session-insights.sh`

- [ ] **Step 3: 動作確認**

Run: `OBSIDIAN_VAULT_PATH="$HOME/Documents/Obsidian Vault" bash ~/.config/claude/scripts/runtime/sync-session-insights.sh`
Expected: `[sync-insights] Generated .../00-Inbox/insight-2026-03-23.md` または無言終了（セッションなし）

- [ ] **Step 4: 生成されたファイルの中身を確認**

Run: `cat "$HOME/Documents/Obsidian Vault/00-Inbox/insight-$(date +%Y-%m-%d).md" 2>/dev/null | head -20`
Expected: frontmatter + プロジェクト別のセッションサマリ

- [ ] **Step 5: 冪等性確認**

Run: `OBSIDIAN_VAULT_PATH="$HOME/Documents/Obsidian Vault" bash ~/.config/claude/scripts/runtime/sync-session-insights.sh`
Expected: 何も出力されない（ファイルが既に存在するのでスキップ）

- [ ] **Step 6: Commit**

```bash
git add .config/claude/scripts/runtime/sync-session-insights.sh
git commit -m "✨ feat(obsidian): add sync-session-insights.sh for vault pipeline"
```

---

### Task 5: sync-tacit-knowledge.sh の作成

**Files:**
- Create: `.config/claude/scripts/runtime/sync-tacit-knowledge.sh`

- [ ] **Step 1: スクリプトを作成**

```bash
#!/usr/bin/env bash
# sync-tacit-knowledge.sh — agent-memory/learnings/*.jsonl → Obsidian 04-Galaxy/
set -euo pipefail

VAULT_PATH="${OBSIDIAN_VAULT_PATH:-}"
if [[ -z "$VAULT_PATH" ]]; then
    echo "[sync-tacit] OBSIDIAN_VAULT_PATH not set, skipping" >&2
    exit 0
fi

LEARNINGS_DIR="$HOME/.claude/agent-memory/learnings"
TARGET="$VAULT_PATH/04-Galaxy"
mkdir -p "$TARGET"

TODAY="$(TZ=Asia/Tokyo date +%Y-%m-%d)"
synced=0

for jsonl_file in "$LEARNINGS_DIR"/*.jsonl; do
    [[ -f "$jsonl_file" ]] || continue
    source_name="$(basename "$jsonl_file" .jsonl)"

    # Extract entries (--all: all entries, default: today only)
    date_filter="$TODAY"
    [[ "${1:-}" == "--all" ]] && date_filter=""
    while IFS= read -r entry; do
        [[ -z "$entry" ]] && continue

        # Generate hash for dedup
        hash=$(echo "$entry" | md5 -q 2>/dev/null || echo "$entry" | md5sum | cut -d' ' -f1)
        short_hash="${hash:0:8}"
        timestamp=$(echo "$entry" | jq -r '.timestamp // empty' 2>/dev/null)
        ts_prefix="${timestamp//[:-]/}"
        ts_prefix="${ts_prefix:0:14}"
        [[ -z "$ts_prefix" ]] && ts_prefix="$(date +%Y%m%d%H%M%S)"

        dest_file="$TARGET/${ts_prefix}-learning-${short_hash}.md"

        # Skip if already exists
        [[ -f "$dest_file" ]] && continue

        # Extract fields
        msg=$(echo "$entry" | jq -r '.message // .rule // .pattern // "no description"' 2>/dev/null)
        category=$(echo "$entry" | jq -r '.category // .type // "unknown"' 2>/dev/null)

        synced_at="$(TZ=Asia/Tokyo date +%Y-%m-%dT%H:%M:%S+09:00)"

        {
            echo "---"
            echo "created: \"$TODAY\""
            echo "tags:"
            echo "  - type/permanent"
            echo "  - agent/tacit-knowledge"
            echo "  - status/seed"
            echo "  - \"source/$source_name\""
            echo "source: \"$source_name\""
            echo "synced_at: $synced_at"
            echo "---"
            echo ""
            echo "# Learning: $category"
            echo ""
            echo "## 主張"
            echo ""
            echo "$msg"
            echo ""
            echo "## 詳細"
            echo ""
            echo '<!-- 自動抽出。必要に応じて編集 -->'
            echo ""
            echo "\`\`\`json"
            echo "$entry" | jq '.' 2>/dev/null || echo "$entry"
            echo "\`\`\`"
            echo ""
            echo "## 関連ノート"
            echo ""
            echo "- [[]] — 関連の理由"
        } > "$dest_file"

        synced=$((synced + 1))
    done < <(if [[ -n "$date_filter" ]]; then jq -c --arg date "$date_filter" 'select(.timestamp // "" | startswith($date))' "$jsonl_file" 2>/dev/null; else jq -c '.' "$jsonl_file" 2>/dev/null; fi)
done

if [[ $synced -gt 0 ]]; then
    echo "[sync-tacit] Synced $synced learning(s) to $TARGET"
fi
```

- [ ] **Step 2: 実行権限を付与**

Run: `chmod +x ~/.config/claude/scripts/runtime/sync-tacit-knowledge.sh`

- [ ] **Step 3: 動作確認**

Run: `OBSIDIAN_VAULT_PATH="$HOME/Documents/Obsidian Vault" bash ~/.config/claude/scripts/runtime/sync-tacit-knowledge.sh`
Expected: `[sync-tacit] Synced N learning(s)` または無言終了（今日のエントリなし）

- [ ] **Step 4: Commit**

```bash
git add .config/claude/scripts/runtime/sync-tacit-knowledge.sh
git commit -m "✨ feat(obsidian): add sync-tacit-knowledge.sh for vault pipeline"
```

---

### Task 6: note-to-vault.sh + /note スキルの作成

**Files:**
- Create: `.config/claude/scripts/runtime/note-to-vault.sh`
- Create: `.config/claude/skills/note/SKILL.md`

- [ ] **Step 1: note-to-vault.sh を作成**

```bash
#!/usr/bin/env bash
# note-to-vault.sh — テキストを Obsidian Vault 00-Inbox/ に即時保存
set -euo pipefail

VAULT_PATH="${OBSIDIAN_VAULT_PATH:-}"
if [[ -z "$VAULT_PATH" ]]; then
    echo "[note] OBSIDIAN_VAULT_PATH not set" >&2
    exit 1
fi

TEXT="${1:-}"
if [[ -z "$TEXT" ]]; then
    echo "[note] Usage: note-to-vault.sh 'content'" >&2
    exit 1
fi

TARGET="$VAULT_PATH/00-Inbox"
mkdir -p "$TARGET"

TODAY="$(TZ=Asia/Tokyo date +%Y-%m-%d)"
TIMESTAMP="$(TZ=Asia/Tokyo date +%Y%m%d%H%M%S)"
DEST_FILE="$TARGET/note-${TIMESTAMP}.md"

{
    echo "---"
    echo "tags: [status/seed]"
    echo "created: \"$TODAY\""
    echo "---"
    echo ""
    echo "$TEXT"
} > "$DEST_FILE"

echo "$DEST_FILE"
```

- [ ] **Step 2: 実行権限を付与**

Run: `chmod +x ~/.config/claude/scripts/runtime/note-to-vault.sh`

- [ ] **Step 3: /note スキル定義を作成**

`.config/claude/skills/note/SKILL.md`:

```markdown
---
name: note
description: "セッション中の知見を Obsidian Vault の Inbox に即時保存する。Triggers: '/note 内容'. Do NOT use for: ナレッジ整理 (use obsidian-knowledge)."
metadata:
  pattern: action
argument-hint: "<保存したい内容>"
---

# Note to Vault

セッション中に残したい知見・メモを Obsidian Vault の 00-Inbox/ に即座に書き出す。

## 処理手順

1. 引数テキストを受け取る
2. Bash で `note-to-vault.sh` を実行する:

\`\`\`bash
~/.config/claude/scripts/runtime/note-to-vault.sh '引数テキスト'
\`\`\`

3. 保存先パスをユーザーに報告する
```

- [ ] **Step 4: 動作確認**

Run: `OBSIDIAN_VAULT_PATH="$HOME/Documents/Obsidian Vault" bash ~/.config/claude/scripts/runtime/note-to-vault.sh 'テストメモ: パイプライン動作確認'`
Expected: `/Users/takeuchishougo/Documents/Obsidian Vault/00-Inbox/note-YYYYMMDDHHMMSS.md`

- [ ] **Step 5: 生成ファイルの中身確認**

Run: `ls -t "$HOME/Documents/Obsidian Vault/00-Inbox"/note-*.md | head -1 | xargs cat`
Expected: frontmatter + テストメモ

- [ ] **Step 6: Commit**

```bash
git add .config/claude/scripts/runtime/note-to-vault.sh .config/claude/skills/note/SKILL.md
git commit -m "✨ feat(obsidian): add /note skill and note-to-vault.sh"
```

---

### Task 7: settings.json に hook を追加

**Files:**
- Modify: `.config/claude/settings.json` (PostToolUse セクション)

- [ ] **Step 1: PostToolUse の `Skill` matcher hook の直前に sync hook を追加**

`edit-failure-tracker.py` hook と `updated_at` 更新 hook（memory ファイルの `updated_at` を書き換える既存 hook）の後、`Skill` matcher hook の前に新しいエントリを挿入する。

既存 hook のパターン（stdin から `tool_input.file_path` を jq で読む）に合わせる:

```json
{
    "matcher": "Edit|Write",
    "hooks": [
        {
            "type": "command",
            "command": "jq -r '.tool_input.file_path // empty' | { read -r f; case \"$f\" in */.claude/projects/*/memory/*.md) [ \"$(basename \"$f\")\" = \"MEMORY.md\" ] && exit 0; export OBSIDIAN_VAULT_PATH=\"$HOME/Documents/Obsidian Vault\"; $HOME/.config/claude/scripts/runtime/sync-memory-to-vault.sh >> /tmp/obsidian-sync.log 2>&1 & ;; esac; }",
            "timeout": 5
        }
    ]
}
```

注意: `&` でバックグラウンド実行し hook のタイムアウトに引っかからないようにする。`export` で環境変数を子プロセスに渡す。

- [ ] **Step 2: settings.json の JSON が有効か確認**

Run: `jq '.' ~/.config/claude/settings.json > /dev/null && echo "valid JSON"`
Expected: `valid JSON`

- [ ] **Step 3: Commit**

```bash
git add .config/claude/settings.json
git commit -m "🔧 chore(hooks): add PostToolUse hook for obsidian memory sync"
```

---

### Task 8: Vault CLAUDE.md のカスタマイズ

**Files:**
- Modify: `templates/obsidian-vault/CLAUDE.md`

- [ ] **Step 1: テンプレートの placeholder を更新**

以下の置換を行う:
- `[YOUR_NAME]` → `takeuchishougo`
- `[YOUR_ROLE]` → `ソフトウェアエンジニア`
- `[YOUR_INTERESTS]` → `AI エージェント設計、Claude Code ハーネスエンジニアリング、Go、開発者生産性`
- `[CASUAL/FORMAL/MIXED]` → `MIXED`
- `[ja/en/mixed]` → `ja`

Vault Architecture テーブルに行を追加:
```
| 07-Daily | 日報。/daily-report の出力が自動同期される |
| 08-Agent-Memory | Claude Code の memory が自動同期される。エージェントの蓄積知識 |
```

- [ ] **Step 2: 実際の vault の CLAUDE.md にも適用**

サンドボックス制限のため、ユーザーに手動コピーを依頼:
```bash
cp ~/dotfiles/templates/obsidian-vault/CLAUDE.md ~/Documents/Obsidian\ Vault/CLAUDE.md
```

- [ ] **Step 3: Commit**

```bash
git add templates/obsidian-vault/CLAUDE.md
git commit -m "📝 docs(obsidian): customize vault CLAUDE.md with user profile"
```

---

### Task 9: Cron の登録

- [ ] **Step 1: crontab にエントリを追加**

Run:
```bash
(crontab -l 2>/dev/null; cat <<'EOF'
# Obsidian Vault sync pipeline
OBSIDIAN_VAULT_PATH=/Users/takeuchishougo/Documents/Obsidian Vault
0 23 * * * /Users/takeuchishougo/.config/claude/scripts/runtime/sync-daily-report.sh >> /tmp/obsidian-sync.log 2>&1
5 23 * * * /Users/takeuchishougo/.config/claude/scripts/runtime/sync-session-insights.sh >> /tmp/obsidian-sync.log 2>&1
10 23 * * * /Users/takeuchishougo/.config/claude/scripts/runtime/sync-tacit-knowledge.sh >> /tmp/obsidian-sync.log 2>&1
EOF
) | crontab -
```

- [ ] **Step 2: 登録を確認**

Run: `crontab -l | grep obsidian`
Expected: 3つの cron エントリが表示される

---

### Task 10: E2E 検証

- [ ] **Step 1: 全スクリプトを手動実行して vault を確認**

```bash
export OBSIDIAN_VAULT_PATH="$HOME/Documents/Obsidian Vault"
bash ~/.config/claude/scripts/runtime/sync-memory-to-vault.sh
bash ~/.config/claude/scripts/runtime/sync-daily-report.sh
bash ~/.config/claude/scripts/runtime/sync-session-insights.sh
bash ~/.config/claude/scripts/runtime/sync-tacit-knowledge.sh
bash ~/.config/claude/scripts/runtime/note-to-vault.sh 'E2E テスト完了'
```

- [ ] **Step 2: vault 内のファイルを確認**

```bash
echo "=== 08-Agent-Memory ===" && ls "$OBSIDIAN_VAULT_PATH/08-Agent-Memory/" | wc -l
echo "=== 07-Daily ===" && ls "$OBSIDIAN_VAULT_PATH/07-Daily/" 2>/dev/null | wc -l
echo "=== 00-Inbox (insights) ===" && ls "$OBSIDIAN_VAULT_PATH/00-Inbox/insight-"* 2>/dev/null | wc -l
echo "=== 00-Inbox (notes) ===" && ls "$OBSIDIAN_VAULT_PATH/00-Inbox/note-"* 2>/dev/null | wc -l
echo "=== 04-Galaxy (learnings) ===" && ls "$OBSIDIAN_VAULT_PATH/04-Galaxy/"*learning* 2>/dev/null | wc -l
```

Expected: 各ディレクトリに1つ以上のファイル（日報とlearnings は当日データの有無による）

- [ ] **Step 3: 冪等性の最終確認（全スクリプト2回目実行）**

同じコマンドを再実行し、出力がないこと（重複なし）を確認

- [ ] **Step 4: Obsidian アプリで vault を開き、同期されたファイルが表示されることを目視確認**
