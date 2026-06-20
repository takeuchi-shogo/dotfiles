#!/usr/bin/env bash
# run-weekly-report.sh — 過去 7 日の活動サマリ + 来週の TODO 草案 (3 カテゴリ別)
# DOW gate: 日曜 (0) のみ実行、月曜 catch-up 1 日
# Sources:
#   - ~/.claude/projects/*/*.jsonl (-mtime -7)
#   - ${VAULT}/**/*.md (-mtime -7, 06-Nightly 除外)
#   - git log --since='7 days ago' (3 categories)
#   - merged PR / open PR (per repo)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./lib/nightly-status.sh
source "${SCRIPT_DIR}/lib/nightly-status.sh"

TASK="weekly-report"

_cleanup() {
    local ec=$?
    if [[ -n "${_NIGHTLY_CURRENT_TASK:-}" ]]; then
        status_end fail "trapped exit_code=$ec"
    fi
    release_claude_lock
}
trap _cleanup EXIT

# Prereq
if [[ -z "${OBSIDIAN_VAULT_PATH:-}" ]]; then
    status_begin "$TASK"; status_end fail "missing OBSIDIAN_VAULT_PATH"
    exit 0
fi
for cmd in jq codex; do
    if ! command -v "$cmd" &>/dev/null; then
        status_begin "$TASK"; status_end fail "preflight: $cmd CLI not found"
        exit 0
    fi
done
TIMEOUT_BIN=$(command -v timeout 2>/dev/null || command -v gtimeout 2>/dev/null || true)
if [[ -z "$TIMEOUT_BIN" ]]; then
    status_begin "$TASK"; status_end fail "preflight: timeout/gtimeout not found"
    exit 0
fi

# DOW 0 = 日曜、catch_up 1 日 (月曜まで)
should_run_today "$TASK" DOW 0 1 || exit 0
status_begin "$TASK"

if ! acquire_claude_lock; then
    status_end fail "claude lock timeout"
    exit 0
fi

REPORT_DIR="${OBSIDIAN_VAULT_PATH}/06-Nightly"
mkdir -p "$REPORT_DIR"
REPORT_PATH="${REPORT_DIR}/${NIGHTLY_DATE}-weekly.md"
REPORT_TMP=$(mktemp -t "nightly-weekly-${NIGHTLY_DATE}.XXXXXX")
trap 'rm -f "$REPORT_TMP"; _cleanup' EXIT

# === Source data 収集 (過去 7 日) ===

# Claude sessions
SESSION_LIST=$(find "$HOME/.claude/projects" -name "*.jsonl" -mtime -7 2>/dev/null | head -100 || true)
SESSION_COUNT=$(echo "${SESSION_LIST}" | grep -cE '\.jsonl$' || true)
SESSION_COUNT="${SESSION_COUNT:-0}"

# プロジェクト別 cwd 集計 (どこで作業したか)
SESSION_BY_CWD=""
if [[ -n "$SESSION_LIST" ]]; then
    SESSION_BY_CWD=$(echo "$SESSION_LIST" | while IFS= read -r f; do
        [[ -z "$f" ]] && continue
        jq -r 'select(.cwd) | .cwd' "$f" 2>/dev/null | head -1
    done | sort | uniq -c | sort -rn | head -10 | awk '{
        cwd=$2; for(i=3;i<=NF;i++) cwd=cwd" "$i;
        sub(ENVIRON["HOME"], "~", cwd);
        printf "  %4d  %s\n", $1, cwd
    }')
fi

# Vault 変更
VAULT_CHANGED=$(find "$OBSIDIAN_VAULT_PATH" -name "*.md" -mtime -7 \
    -not -path "*06-Nightly*" 2>/dev/null | wc -l | tr -d ' ')

# Literature 新規 (今週読んだ記事)
LIT_LIST=$(find "$OBSIDIAN_VAULT_PATH/05-Literature" -name "*.md" -mtime -7 2>/dev/null | head -20 || true)
LIT_COUNT=$(echo "$LIT_LIST" | grep -cE '\.md$' || true)
LIT_COUNT="${LIT_COUNT:-0}"
LIT_TITLES=""
if [[ -n "$LIT_LIST" ]]; then
    LIT_TITLES=$(echo "$LIT_LIST" | while IFS= read -r f; do
        [[ -z "$f" ]] && continue
        basename "$f" .md
    done | sed 's/^/  - /' | head -10)
fi

# === 3 カテゴリ別 git 統計 (過去 7 日) ===
# ponytail: daily と仕様統一: remote 未設定なら gh 呼ばない (誤 PR 混入回避)

_collect_repo_week() {
    local repo="$1"
    [[ ! -d "$repo/.git" ]] && return
    local branch commit_count recent merged_pr open_pr uncommitted remote_url nwo
    branch=$(git -C "$repo" branch --show-current 2>/dev/null)
    commit_count=$(git -C "$repo" log --since='7 days ago' --oneline 2>/dev/null | wc -l | tr -d ' ')
    recent=$(git -C "$repo" log --since='7 days ago' --oneline 2>/dev/null | head -8)
    uncommitted=$(git -C "$repo" status --short 2>/dev/null | head -5)
    merged_pr=""
    open_pr=""
    remote_url=$(git -C "$repo" config --get remote.origin.url 2>/dev/null)
    if [[ -n "$remote_url" ]] && command -v gh &>/dev/null; then
        nwo=$(echo "$remote_url" | sed -E 's|.*[:/]([^/]+/[^/.]+)(\.git)?$|\1|')
        if [[ -n "$nwo" ]]; then
            merged_pr=$(gh -R "$nwo" pr list --author=@me --state=merged \
                --search "merged:>$(date -v-7d +%Y-%m-%d 2>/dev/null || date -d '7 days ago' +%Y-%m-%d)" \
                --json number,title 2>/dev/null \
                | jq -r '.[] | "  #\(.number) \(.title)"' 2>/dev/null | head -8)
            open_pr=$(gh -R "$nwo" pr list --author=@me --state=open --json number,title,headRefName 2>/dev/null \
                | jq -r '.[] | "  #\(.number) \(.title) [\(.headRefName)]"' 2>/dev/null | head -5)
        fi
    fi
    local repo_short="${repo/#$HOME/~}"
    echo "#### \`${repo_short}\` (branch: ${branch:-?}, 今週 commit: ${commit_count})"
    echo "- 今週の commit:"
    if [[ -z "$recent" ]]; then echo "  (なし)"; else echo "$recent" | sed 's/^/  - /'; fi
    echo "- 今週 merge した PR:"
    if [[ -z "$merged_pr" ]]; then echo "  (なし)"; else echo "$merged_pr"; fi
    echo "- 現在 open の自分の PR:"
    if [[ -z "$open_pr" ]]; then echo "  (なし)"; else echo "$open_pr"; fi
    echo "- 現在 uncommitted:"
    if [[ -z "$uncommitted" ]]; then echo "  (clean)"; else echo "$uncommitted" | sed 's/^/    /'; fi
}

# 副業: hearable (app2 は app の clone のため除外)
SIDEJOB_STATE=""
for repo in "$HOME/dev-app/hearable/app" "$HOME/dev-app/hearable/survey"; do
    SIDEJOB_STATE+="$(_collect_repo_week "$repo")"$'\n'
done

# AI 改善: dotfiles
AI_STATE=$(_collect_repo_week "$HOME/dotfiles")

# 自己学習: dev-app その他 (hearable 除外、git 管理のみ)
LEARN_STATE=""
while IFS= read -r repo; do
    [[ -z "$repo" ]] && continue
    [[ "$repo" == */hearable/* ]] && continue
    LEARN_STATE+="$(_collect_repo_week "$repo")"$'\n'
done < <(find "$HOME/dev-app" -maxdepth 3 -name '.git' -type d 2>/dev/null | sed 's|/.git$||')

# === Prompt 構築 ===
PROMPT="$(cat <<PROMPT_EOF
あなたは過去 7 日 (${NIGHTLY_DATE} 終わりの週) を要約する Weekly Report エージェントです。

**重要な制約 (必ず守ること)**:
- 出力は Weekly Report のみ。コードレビュー / verdict / Severity 表 / Findings は禁止
- 提供されたデータを要約するだけ、独自に file を Read しない
- 「下記出力フォーマット」セクションの構造を厳守

# 今週のデータ

## Claude Code セッション
- 件数: ${SESSION_COUNT} (過去 7 日)
- プロジェクト別 cwd 集計 (top 10):
\`\`\`
${SESSION_BY_CWD:-(なし)}
\`\`\`

## Obsidian Vault 変更
- 変更ファイル数: ${VAULT_CHANGED} 件 (06-Nightly 除外)

## 新規 Literature (今週読んだ記事)
- 件数: ${LIT_COUNT}
- タイトル (top 10):
\`\`\`
${LIT_TITLES:-(なし)}
\`\`\`

## 3 カテゴリ別 git 統計 (過去 7 日)

### 副業 (~/dev-app/hearable, app2 除く)
\`\`\`
${SIDEJOB_STATE:-(なし)}
\`\`\`

### AI 改善 (~/dotfiles)
\`\`\`
${AI_STATE:-(なし)}
\`\`\`

### 自己学習 (~/dev-app/* で git 管理されてる repo)
\`\`\`
${LEARN_STATE:-(なし)}
\`\`\`

# 出力フォーマット (Markdown、40-80 行で簡潔に)

# Weekly Report (${NIGHTLY_DATE} 終わりの週)

## 今週のハイライト
- (各カテゴリで顕著な進捗を 1 文で 2-4 個)

## カテゴリ別サマリ

### 副業 (hearable)
- **commit/PR**: (今週の数値と主な内容)
- **進捗**: (merged PR から完了したものを 1-3 個)
- **残課題**: (open PR + uncommitted から進行中を 1-3 個)

### AI 改善 (dotfiles)
- 同上

### 自己学習 (dev-app)
- 同上 (commit 0 件の repo は「触らず」と書く、ノイズを減らす)

## 読んだ記事 (${LIT_COUNT} 件)
- (タイトルから 2-4 個ピックして、何の領域か 1 文で要約)

## 来週の TODO 草案

各カテゴリで「来週着手すべきもの」を 1-3 個ずつ抽出。データは:
- open PR で merge 待ちのもの (レビュー対応 / コンフリクト解消 / ready 化)
- uncommitted で commit/PR 化できるもの
- 1 週間 commit ゼロの repo は「ストール: 続けるか撤退判断」と書く

**重複排除**: 同じ remote を共有する複数 clone (例: hearable/app と app2) の open PR は 1 つにまとめる。

### 副業 (hearable)
- (1-3 個、対応する repo パスを括弧付きで)

### AI 改善 (dotfiles)
- (1-3 個)

### 自己学習 (dev-app)
- (1-3 個、または「全 stall: 復帰計画 or 撤退判断」)

## 気づき / 次週への留意
- (今週のセッション cwd 分布、Literature テーマから 1-3 個。なければ「特になし」)
PROMPT_EOF
)"

# codex exec (read-only 分析 → -o で REPORT_TMP に最終メッセージのみ書き出す)
if ! run_codex_report 720 "$REPORT_TMP" "$PROMPT"; then
    status_end fail "codex failed/timeout: $CODEX_ERR_HEAD"
    exit 0
fi

mv "$REPORT_TMP" "$REPORT_PATH"

# Discord 詳細: report の hilight + 来週の TODO セクション (head 20 行)
DETAIL=$(head -20 "$REPORT_PATH" 2>/dev/null || echo "")

status_end ok "sessions=$SESSION_COUNT vault=$VAULT_CHANGED lit=$LIT_COUNT" \
    "report=06-Nightly/${NIGHTLY_DATE}-weekly.md" \
    "metric.sessions=$SESSION_COUNT" "metric.vault=$VAULT_CHANGED" "metric.lit=$LIT_COUNT" \
    "detail=$DETAIL"
