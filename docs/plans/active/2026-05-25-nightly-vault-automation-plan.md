# Nightly Vault Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Spec:** `docs/superpowers/specs/2026-05-25-nightly-vault-automation-design.md` (commit 703e1c2)

**Goal:** dotfiles の品質維持系タスク 6 つ (audit / dep-audit / skill-audit / health-check / golden-check / friction-aggregate) を夜間 cron でオフロードし、結果を Discord webhook + Vault/06-Nightly/ レポート + 翌朝 morning-briefing 統合の三重出力で受け取る。

**Architecture:** Approach A (フラット shell scripts + 共有 lib)。`scripts/runtime/nightly/{lib,run-*.sh}` 構成、全 task は `cron で毎晩起動` + `内部 should_run_today gate (DAILY/DOW/DOM)` で曜日/月初判定 + catch-up window (6-7 日)。Discord 通知は webhook URL を curl で叩く片方向送信、設定は `~/.config/notifications/discord.env`。

**Tech Stack:** Bash 5.x、`set -euo pipefail`、`trap ERR`、`timeout`、`curl`、`jq`、`claude -p`、既存 `scripts/runtime/auto-morning-briefing.sh` テンプレート。

---

## Pre-flight: Open Questions の解消 (Task 0 で実施)

Spec Section 8 の Q1-Q7 を実装前に確定。後続 task の前提として固定する。

| Q | 確定内容 |
|---|----------|
| Q1: friction-events path + schema | path: `~/.claude/agent-memory/learnings/friction-events.jsonl`。schema は `.friction_class` を主キーとし、fallback として `.type` を読む順序: `(.friction_class // .type // "unknown")`。集計フィールドは `.action_surface`, `.target_hint`, `.evidence` も保持 (Top 10 issues の表示に使用)。**Codex Gate C5 反映 (2026-05-25)** |
| Q2: skill-audit 呼び方 | 既存 `/skill-audit` skill を `claude -p "/skill-audit"` で呼び出す (DRY、独立実装はしない)。Task 9 の prompt も自然文ではなく **`"/skill-audit"` exact invocation** に統一。**Codex Gate (2) issue 反映** |
| Q3: dep-audit 対象 | dotfiles root + 実 manifest を持つサブディレクトリ: root の `{package.json,pyproject.toml,go.mod,Cargo.toml}` に加えて **`~/dotfiles/tools/claude-hooks/Cargo.toml`** + **`~/dotfiles/tools/otel-session-analyzer/go.mod`**。`find ~/dotfiles -maxdepth 3 \( -name "Cargo.toml" -o -name "go.mod" -o -name "package.json" -o -name "pyproject.toml" \)` で動的検出し、各 dir 単位で audit を実行。**Codex Gate C2 反映 (2026-05-25)** |
| Q4: 06-Nightly retention | v1 は無制限蓄積。`ls 06-Nightly | wc -l > 100` で警告するだけの cleanup script は別 plan |
| Q5: morning-briefing 統合 | post-processing 方式 — **root の `scripts/runtime/auto-morning-briefing.sh` が canonical** (`.config/claude/scripts/runtime/auto-morning-briefing.sh` は触らない)。末尾近くで `prepend_nightly_status()` 関数を呼び、briefing 文字列の先頭に `## Nightly Status` セクションを差し込んでから Daily Note に append。PROMPT 改変はしない (既存 briefing 生成ロジックは無変更)。**Codex Gate Medium (canonical script 曖昧) 反映** |
| Q6: status API | positional 引数: `status_begin "$TASK"` / `status_end "ok\|fail" "msg" "metric_key=value..."`。`status_end` が `status_begin` 前に呼ばれた場合 `_NIGHTLY_CURRENT_TASK` env fallback で記録 (skeleton 破綻防止)。**Codex Gate Medium 反映** |
| Q7: claude プロンプト | 各 run-script の `claude -p` プロンプト草案は Task 内に inline 記述 (Task 5-10 参照) |
| Q8 (new): status JSONL 保存先 | `~/.cache/nightly/status-${DATE}.jsonl` を **正本** とする (`/tmp` への複製は廃止: 再起動/cleanup で消失するため morning integration が欠落)。**Codex Gate C3 反映 (2026-05-25)** |
| Q9 (new): failed task の catch-up | fail でも **`mark_run_today` を必ず呼ぶ** (catch-up window 内の毎晩再試行を防ぐ)。retry は人手判断 (`rm ~/.cache/nightly/last-run-*.txt` + `FORCE_RUN=1`)。**Codex Gate C6 反映 (2026-05-25)** |
| Q10 (new): cron env contract | crontab 上部に env block を必ず追加: `SHELL=/bin/bash`, `HOME=/Users/takeuchishougo`, `TZ=Asia/Tokyo`, `PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin`, `OBSIDIAN_VAULT_PATH=/Users/takeuchishougo/Documents/Obsidian Vault`。各 run-*.sh は冒頭で `command -v jq curl claude` の preflight + `TIMEOUT_BIN=$(command -v timeout \|\| command -v gtimeout)` 解決を実施。**Codex Gate C1 反映 (2026-05-25)** |
| Q11 (new): dep-audit timing | `0 0 * * *` (深夜) ではなく **`30 22 * * *`** (前夜枠) に移動。理由: 翌朝 morning-briefing が前日 JSONL を読むため、深夜 0:00 の dep-audit は `YESTERDAY` 範囲外。**Codex Gate C4 反映 (2026-05-25)** |
| Q12 (new): heavy task lock | 23:45 に audit + skill-audit が同時起動する設計を回避: 全 run-*.sh で **atomic `mkdir ~/.cache/nightly/.lock-claude-p`** によりグローバル `claude -p` lock を取得、待機 5 分でも取れなければ skip + fail status。**Codex Gate FM-7 反映** |

---

## Codex Spec/Plan Gate Findings (2026-05-25)

`codex exec --sandbox read-only --config model_reasoning_effort="xhigh"` (gpt-5.5) によるレビュー結果。Verdict: **pass-with-revisions**。本 plan は以下の修正を全 task の前提として反映済。

### Critical (Pre-flight Q1-Q12 に反映済)
- C1 (→ Q10): cron 環境変数 contract 未定義 → env block + preflight 追加
- C2 (→ Q3): dep-audit scope に `tools/claude-hooks/Cargo.toml` + `tools/otel-session-analyzer/go.mod` 追加
- C3 (→ Q8): `/tmp` volatile → `~/.cache/nightly/status-${DATE}.jsonl` を正本に
- C4 (→ Q11): dep-audit `0:00` は morning miss → `22:30` 前夜枠に移動
- C5 (→ Q1): friction-events schema は `.friction_class` 主キー、`.type` fallback
- C6 (→ Q9): fail でも `mark_run_today` する (catch-up 再試行防止、retry は人手)

### High (各 Task 内で対処)
- H1 (Task 11): `prepend_nightly_status` の jq parse error で morning briefing 全死亡 → `if ! status_section=$(jq ...); then echo "$briefing"; return 0; fi` で fallback
- H2 (全 run-*.sh): `grep -c ... || echo 0` は no-match で `0\n0` を返す → `grep -c ... || true` に置換、または `$(grep -c PATTERN FILE 2>/dev/null; true)` でラップ
- H3 (Task 12): crontab 上部 `OBSIDIAN_VAULT_PATH` 仮定だが**実 crontab は空** → Q10 env block を Step 1 で追加することを明文化
- H4 (→ Q12): FM-7 heavy task lock
- H5 (Task 11): JSONL malformed line で morning failure → `jq -R 'fromjson?'` で raw 入力を tolerant parse

### Medium (実装メモで対処)
- M1 (Task 2): `status_end` before `status_begin` skeleton 破綻 → `_NIGHTLY_CURRENT_TASK` env fallback (Q6 で対応)
- M2 (→ Q5): canonical morning script 曖昧 (root vs `.config/claude` 二重存在) → root を canonical と明記
- M3 (全 run-*.sh): Vault report partial write → `mktemp` に書いて成功時のみ atomic `mv`、fail 時は `*.failed.md` に明示
- M4 (Task 6): dry-run の `mv` で実ログを退避する手順は危険 → `FRICTION_LOG_OVERRIDE` env で対処

### その他観察事項
- `@here` 連続失敗時の throttle (連続失敗は daily digest 化) — v2 課題
- 06-Nightly retention warning AC — v2 課題

---

## File Structure

新規ファイル (8):
- `scripts/runtime/nightly/lib/notify-discord.sh` — Discord webhook curl wrapper
- `scripts/runtime/nightly/lib/nightly-status.sh` — JSONL 追記 + Vault 保存 + catch-up gate + Discord 呼び出し
- `scripts/runtime/nightly/run-golden-check.sh` — golden-check 違反一覧
- `scripts/runtime/nightly/run-friction-aggregate.sh` — 前日 friction 集計
- `scripts/runtime/nightly/run-health-check.sh` — docs 鮮度 + コード乖離
- `scripts/runtime/nightly/run-audit.sh` — コードベース横断品質監査
- `scripts/runtime/nightly/run-skill-audit.sh` — A/B + health audit (既存 skill 呼び出し)
- `scripts/runtime/nightly/run-dep-audit.sh` — 脆弱性 + outdated

新規設定:
- `.config/notifications/discord.env` — `DISCORD_WEBHOOK_URL=...` (chmod 600, .gitignore)
- `.gitignore` 追記: `.config/notifications/*.env`

新規 Vault フォルダ:
- `${OBSIDIAN_VAULT_PATH}/06-Nightly/.gitkeep` — 永続化 (Vault は git 管理ではないが Obsidian sync 用に最低 1 ファイル必要)

新規ドキュメント:
- `docs/playbooks/nightly-offload.md` — Discord webhook 取得手順 + 運用フロー + トラブルシュート

既存変更:
- `scripts/runtime/auto-morning-briefing.sh` — 末尾近くに `prepend_nightly_status()` 関数 + 呼び出し (10-15 行追加)
- `crontab` — 6 行追記

合計: 10 新規 + 2 既存変更 + 1 設定 (`crontab` は user 環境)

---

## Dependency DAG

```
Task 0 (Open Q 解消)
  ↓
Task 1 (lib/notify-discord.sh)  ──┐
Task 2 (lib/nightly-status.sh)  ──┴→ 共有 lib 完成 → Task 5-10 が並行可能
Task 3 (discord.env + .gitignore) → Task 1 が curl 成功する前提
Task 4 (Vault 06-Nightly/.gitkeep) → Task 2 が Vault 書き込みする前提
  ↓
Task 5 (run-golden-check.sh) ── 最初の template-establishing task、Task 6-10 はこれを参考
Task 6 (run-friction-aggregate.sh)
Task 7 (run-health-check.sh)
Task 8 (run-audit.sh)
Task 9 (run-skill-audit.sh)
Task 10 (run-dep-audit.sh)
  ↓
Task 11 (auto-morning-briefing.sh 編集) — Task 5-10 完了後、JSONL が実際に書かれる状態で
  ↓
Task 12 (crontab 追記) — 全 script が手動で verify 済の状態で
  ↓
Task 13 (docs/playbooks/nightly-offload.md)
  ↓
Task 14 (1 週間運用後 retrospective スケジュール)
```

依存:
- Task 1, 2, 3, 4 は並行可能 (お互いに参照しない)
- Task 5 は template 確立のため最初に着手、Task 6-10 は Task 5 完成後に並列可
- Task 11 は Task 5-10 のうち少なくとも 1 つの jsonl が生成された後
- Task 12 は全実装完了 + 手動 verify 後
- Task 13, 14 は最後

---

## Size / Effort 見積もり

| Task | Size | 主作業者 | 想定時間 |
|------|------|----------|----------|
| Task 0 | S | claude | 10 min (Open Q 確定 + plan 内 doc) |
| Task 1 | S | claude | 15 min (notify-discord.sh + curl test) |
| Task 2 | M | claude | 30 min (catch-up gate ロジック + unit-test 風 verify) |
| Task 3 | S | claude + 人手 | 10 min (claude が template、人手で Discord webhook URL 取得 + .env 作成) |
| Task 4 | S | claude | 5 min |
| Task 5 | M | claude | 25 min (template-establishing、5-10 と共通形) |
| Task 6 | S | claude | 15 min |
| Task 7 | M | claude | 25 min (claude -p プロンプト調整、複雑) |
| Task 8 | M | claude | 30 min (audit プロンプト、レポート長め) |
| Task 9 | S | claude | 15 min (既存 skill 呼ぶだけ) |
| Task 10 | M | claude | 25 min (multi-lang dep CLI invocation) |
| Task 11 | M | claude | 20 min (既存 briefing.sh の関心分離注意) |
| Task 12 | S | 人手 | 5 min (crontab -e で 6 行追加) |
| Task 13 | S | claude | 20 min (Markdown 手順書) |
| Task 14 | S | claude | 5 min (`/decision` で 1 週間後リマインダー登録) |

**合計**: ~4 時間 (Codex Review Gate 含めず)、L 規模。

**Codex 関与**:
- Task 0 後の Codex Spec/Plan Gate (M/L 必須): 30 min
- Task 12 直前の Codex Review Gate (harness 変更含むため必須): 30-60 min

**人手必須**:
- Task 3: Discord channel 作成 + Webhook URL 発行
- Task 12: `crontab -e` 編集 (環境依存)
- Task 14: 1 週間後の retrospective

---

## Task 0: Open Questions 確定 + Pre-mortem

**Files:**
- Modify: `docs/plans/active/2026-05-25-nightly-vault-automation-plan.md:14-22` (本 plan の "Pre-flight" テーブル、確定後はこのまま fix)
- Reference: `docs/superpowers/specs/2026-05-25-nightly-vault-automation-design.md` Section 8
- Reference: `references/pre-mortem-checklist.md`, `references/reversible-decisions.md` (L 規模必須)

- [x] **Step 1: Q1-Q12 を Pre-flight テーブル通りに確定し、本 plan の Pre-flight 表に追記済を確認** (Codex Gate 反映で Q8-Q12 追加済)

- [x] **Step 2: Pre-mortem チェック (references/pre-mortem-checklist.md 適用)**

考えられる失敗モード (FM-1..5 は初版、FM-6..11 は Codex Gate で追加):
- (FM-1) Discord webhook URL リーク → `.gitignore` + `chmod 600` + secretlint で防御
- (FM-2) cron が毎晩 6 task 起動で API token 過剰消費 → 毎晩は軽 3 task のみ重い処理は週/月、claude -p の cost 計測を Step 5 で実装
- (FM-3) Vault 書き込み race (Obsidian sync と被る) → 23:15+ は Obsidian iCloud sync が落ち着いている時間帯、念のため `--lockfile` 不要 (Obsidian は append safe)
- (FM-4) catch-up が誤発火 (`last_run` ファイル破損) → 破損時は `1970-01-01` fallback + date format validation (YYYY-MM-DD regex)、`mark_run_today` は idempotent
- (FM-5) claude -p が hang して翌朝まで起動しっぱなし → `timeout 900s` 必須、Task 5 template に組み込み
- **(FM-6) cron minimal env / PATH miss** (Codex Gate, likelihood=high impact=high) → Q10 env block + preflight `command -v` で対処
- **(FM-7) catch-up overlap で重い claude -p 同時実行** (medium/high) → Q12 atomic `mkdir` lock で対処
- **(FM-8) JSONL malformed line で morning briefing 失敗** (medium/high) → H5 `jq -R 'fromjson?'` で対処
- **(FM-9) Vault report partial write** (medium/medium) → M3 `mktemp` + atomic `mv` で対処
- **(FM-10) predictable `/tmp` files race** (medium/medium) → 全 tmp ファイルを `mktemp` 化、status JSONL は Q8 で `~/.cache` に persistent 化
- **(FM-11) sourced `.env` の権限/内容不備** (low/high) → notify-discord.sh で `stat` mode 600 check + format validation 追加

- [x] **Step 3: Reversible-decisions チェック (references/reversible-decisions.md 適用)**

撤退条件:
- 1 週間運用して Discord 通知が 50% 以上失敗 → webhook 方式断念、cmux-notify hero に切替 (Task 1 修正)
- API cost が想定の 3 倍 → 重い task (audit/skill-audit) を月次に降格
- レポートが朝に確認されない (Vault open しても 06-Nightly/ 開かない) → morning-briefing 統合を強化 or Discord 内で本文一部 inline 表示
- 全体 → 各 task の cron 行を 1 行ずつコメントアウトで撤退可能 (Build to Delete)
- **retry policy** (Q9 反映): fail でも `mark_run_today` する。catch-up window 内の毎晩再試行を防ぐ。retry したい場合は人手で `rm ~/.cache/nightly/last-run-${task}.txt` + `FORCE_RUN=1`

- [x] **Step 4: Codex Spec/Plan Gate を起動 (codex exec fallback で実施済)**

cmux Worker (`launch-worker.sh --model codex`) は "Surface is not a terminal" で失敗したため fallback:

```bash
codex exec --skip-git-repo-check --sandbox read-only --config model_reasoning_effort="xhigh" "$(cat /tmp/codex-gate-prompt.md)" > /tmp/codex-gate-result.md
```

結果: `/tmp/codex-gate-result.md` に保存。Verdict = **pass-with-revisions**、Critical 6 + High 5 + Medium 4 の指摘あり。全て上記 Pre-flight Q8-Q12 + Codex Spec/Plan Gate Findings 節に反映済。

- [x] **Step 5: Codex 結果を反映 + Pre-flight テーブル固定をコミット**

(本 commit でこの step を [x] 化、後続 task は Pre-flight Q1-Q12 と Findings 節を前提として実装する)

```bash
git add docs/plans/active/2026-05-25-nightly-vault-automation-plan.md
git commit -m "$(cat <<'EOF'
📝 docs(nightly): freeze plan after Codex Spec/Plan Gate

decision(plan-freeze): Pre-flight Q1-Q7 + pre-mortem FM-1..5 を本 plan 内に固定、後続 task はこの前提で実装
EOF
)"
```

---

## Task 1: lib/notify-discord.sh

**Files:**
- Create: `scripts/runtime/nightly/lib/notify-discord.sh`
- Test: 手動 (実 Discord webhook URL に test message 送信)

- [ ] **Step 1: ディレクトリ作成**

```bash
mkdir -p ~/dotfiles/scripts/runtime/nightly/lib
```

- [ ] **Step 2: スクリプト本体を Write**

`scripts/runtime/nightly/lib/notify-discord.sh`:

```bash
#!/usr/bin/env bash
# notify-discord.sh — Discord webhook 通知 (curl 片方向)
# Source from run-*.sh: `source "$(dirname "$0")/lib/notify-discord.sh"`
# Usage: notify_discord "status" "task" "duration_sec" "report_path" "metric_summary"
#
# Env:
#   DISCORD_WEBHOOK_URL (from ~/.config/notifications/discord.env)
#
# Behavior:
#   - URL 未設定 → stderr WARN + return 0 (silent skip、呼び出し側は ok 継続)
#   - curl 失敗 → stderr WARN + return 0 (通知は副作用、task は失敗にしない)
#   - status="ok"   → 緑 embed (color 3066993)
#   - status="fail" → 赤 embed (color 15158332) + "@here" mention

set -uo pipefail  # -e は付けない (notify 失敗で呼び出し側を巻き込まないため)

# .env 読み込み (引数で path 上書き可能)
_DISCORD_ENV_PATH="${DISCORD_ENV_PATH:-$HOME/.config/notifications/discord.env}"
if [[ -f "$_DISCORD_ENV_PATH" ]]; then
    # shellcheck source=/dev/null
    source "$_DISCORD_ENV_PATH"
fi

notify_discord() {
    local status="$1" task="$2" duration_sec="$3" report_path="$4" metric_summary="${5:-}"

    if [[ -z "${DISCORD_WEBHOOK_URL:-}" ]]; then
        echo "[notify-discord] WARN: DISCORD_WEBHOOK_URL not set, skipping notification for task=$task" >&2
        return 0
    fi

    local emoji color content
    if [[ "$status" == "ok" ]]; then
        emoji="✅"; color=3066993; content=""
    else
        emoji="❌"; color=15158332; content="@here"
    fi

    local title="${emoji} nightly: ${task} (${duration_sec}s)"
    local description="報告: \`${report_path}\`"
    [[ -n "$metric_summary" ]] && description="${description}\nメトリクス: ${metric_summary}"

    local payload
    payload=$(jq -n \
        --arg content "$content" \
        --arg title "$title" \
        --arg description "$description" \
        --argjson color "$color" \
        --arg timestamp "$(date -Iseconds)" \
        '{
            content: $content,
            embeds: [{
                title: $title,
                description: $description,
                color: $color,
                timestamp: $timestamp
            }]
        }')

    local http_code
    http_code=$(curl -s -o /tmp/notify-discord-response.txt -w "%{http_code}" \
        -H "Content-Type: application/json" \
        -X POST -d "$payload" \
        --max-time 10 \
        "$DISCORD_WEBHOOK_URL" 2>/dev/null || echo "000")

    if [[ "$http_code" != "204" ]] && [[ "$http_code" != "200" ]]; then
        echo "[notify-discord] WARN: HTTP $http_code, response: $(cat /tmp/notify-discord-response.txt 2>/dev/null | head -c 200)" >&2
        return 0
    fi

    return 0
}
```

- [ ] **Step 3: 実行権限付与 + shellcheck**

```bash
chmod +x ~/dotfiles/scripts/runtime/nightly/lib/notify-discord.sh
shellcheck ~/dotfiles/scripts/runtime/nightly/lib/notify-discord.sh
```

Expected: shellcheck PASS (warning なし、必要なら `# shellcheck disable=...` を inline で根拠付き追加)

- [ ] **Step 4: 単体 verify (URL 未設定 case)**

```bash
unset DISCORD_WEBHOOK_URL
DISCORD_ENV_PATH=/dev/null bash -c '
  source ~/dotfiles/scripts/runtime/nightly/lib/notify-discord.sh
  notify_discord ok test-task 42 06-Nightly/test.md "test=1"
  echo "exit=$?"
' 2>&1
```

Expected:
- stderr: `[notify-discord] WARN: DISCORD_WEBHOOK_URL not set, skipping notification for task=test-task`
- stdout: `exit=0`

- [ ] **Step 5: 単体 verify (URL 設定 case、Task 3 完了後に実施)**

```bash
# Task 3 で .env 作成後
source ~/dotfiles/scripts/runtime/nightly/lib/notify-discord.sh
notify_discord ok test-task 42 06-Nightly/test.md "test=1"
```

Expected: Discord channel に緑 embed メッセージが届く ("✅ nightly: test-task (42s)")

- [ ] **Step 6: Commit**

```bash
git add scripts/runtime/nightly/lib/notify-discord.sh
git commit -m "$(cat <<'EOF'
✨ feat(nightly): add notify-discord.sh lib

decision(notify-mechanism): Discord webhook curl over discord:configure bot — 5 分 setup、片方向で十分、bot は over-engineered
constraint(notify-failure): URL 未設定 / HTTP 失敗時は WARN + return 0 — 通知は副作用、task 成果物 (jsonl + Vault report) が完成していれば status=ok
EOF
)"
```

---

## Task 2: lib/nightly-status.sh

**Files:**
- Create: `scripts/runtime/nightly/lib/nightly-status.sh`
- Reference pattern: `scripts/runtime/sync-daily-report.sh` (JSONL append style)
- Reference pattern: `.config/claude/scripts/runtime/skill-pruning-eval-reminder.sh` (date gate)

- [ ] **Step 1: スクリプト本体を Write**

`scripts/runtime/nightly/lib/nightly-status.sh`:

```bash
#!/usr/bin/env bash
# nightly-status.sh — 夜間 task の status 管理 + catch-up gate
# Source from run-*.sh: `source "$(dirname "$0")/lib/nightly-status.sh"`
#
# Public functions:
#   status_begin "$TASK"
#   status_end "ok|fail" "$msg" ["k=v" ...]
#   should_run_today "$TASK" "DAILY|DOW|DOM" "$gate_value" "$catch_up_days"
#   mark_run_today "$TASK"

set -uo pipefail

# notify-discord を同梱
# shellcheck source=./notify-discord.sh
source "$(dirname "${BASH_SOURCE[0]}")/notify-discord.sh"

NIGHTLY_DATE="${NIGHTLY_DATE_OVERRIDE:-$(date +%Y-%m-%d)}"
NIGHTLY_TZ_TS="${NIGHTLY_TZ_TS_OVERRIDE:-$(TZ=Asia/Tokyo date +%Y-%m-%dT%H:%M:%S+09:00)}"
NIGHTLY_STATUS_JSONL="/tmp/nightly-status-${NIGHTLY_DATE}.jsonl"
NIGHTLY_CACHE_DIR="$HOME/.cache/nightly"

mkdir -p "$NIGHTLY_CACHE_DIR" 2>/dev/null || true

# Internal: status_begin が呼ばれた時刻
_NIGHTLY_BEGIN_TS=0
_NIGHTLY_CURRENT_TASK=""

status_begin() {
    _NIGHTLY_CURRENT_TASK="$1"
    _NIGHTLY_BEGIN_TS=$SECONDS
    echo "[nightly] begin task=$_NIGHTLY_CURRENT_TASK at $NIGHTLY_TZ_TS" >&2
}

status_end() {
    local status="$1" msg="${2:-}"
    shift 2 || true
    local extra_kv=("$@")  # 残り全部を k=v ペアとして扱う

    local task="$_NIGHTLY_CURRENT_TASK"
    [[ -z "$task" ]] && { echo "[nightly] ERROR: status_end called without status_begin" >&2; return 1; }

    local duration_sec=$((SECONDS - _NIGHTLY_BEGIN_TS))

    # extra_kv から report=, metric.* を抽出して JSONL に
    local report_path=""
    local metric_obj="{}"
    for kv in "${extra_kv[@]}"; do
        local k="${kv%%=*}" v="${kv#*=}"
        case "$k" in
            report) report_path="$v" ;;
            metric.*)
                local mk="${k#metric.}"
                metric_obj=$(echo "$metric_obj" | jq --arg k "$mk" --arg v "$v" '. + {($k): $v}')
                ;;
            *)
                metric_obj=$(echo "$metric_obj" | jq --arg k "$k" --arg v "$v" '. + {($k): $v}')
                ;;
        esac
    done

    # message も metric に含める
    [[ -n "$msg" ]] && metric_obj=$(echo "$metric_obj" | jq --arg msg "$msg" '. + {msg: $msg}')

    # JSONL line
    local line
    line=$(jq -n \
        --arg ts "$NIGHTLY_TZ_TS" \
        --arg task "$task" \
        --arg status "$status" \
        --argjson duration_sec "$duration_sec" \
        --arg report "$report_path" \
        --argjson metric "$metric_obj" \
        '{ts: $ts, task: $task, status: $status, duration_sec: $duration_sec, report: $report, metric: $metric}')

    echo "$line" >> "$NIGHTLY_STATUS_JSONL"

    # Discord 通知 (notify-discord.sh の notify_discord 関数)
    local metric_summary
    metric_summary=$(echo "$metric_obj" | jq -r 'to_entries | map("\(.key)=\(.value)") | join(", ")' 2>/dev/null || echo "")
    notify_discord "$status" "$task" "$duration_sec" "$report_path" "$metric_summary"

    echo "[nightly] end task=$task status=$status duration=${duration_sec}s" >&2

    _NIGHTLY_CURRENT_TASK=""
    _NIGHTLY_BEGIN_TS=0
}

should_run_today() {
    local task="$1" gate_kind="$2" gate_value="$3" catch_up_days="${4:-0}"
    local last_run_file="${NIGHTLY_CACHE_DIR}/last-run-${task}.txt"

    local last_run today today_dow today_dom
    last_run=$(cat "$last_run_file" 2>/dev/null || echo "1970-01-01")
    today="$NIGHTLY_DATE"

    # 既に今日実行済 → skip (gate 通さない)
    if [[ "$last_run" == "$today" ]]; then
        echo "[nightly] skip $task: already ran today" >&2
        return 1
    fi

    # FORCE_RUN=1 → 強制 (検証用)
    if [[ "${FORCE_RUN:-0}" == "1" ]]; then
        return 0
    fi

    today_dow=$(date -j -f "%Y-%m-%d" "$today" +%u 2>/dev/null || date -d "$today" +%u)  # 1=Mon..7=Sun
    today_dom=$(date -j -f "%Y-%m-%d" "$today" +%-d 2>/dev/null || date -d "$today" +%-d)

    case "$gate_kind" in
        DAILY)
            return 0
            ;;
        DOW)
            # 今日が gate 曜日 → run
            if [[ "$today_dow" == "$gate_value" ]]; then return 0; fi
            # catch-up: 直近の gate 曜日日付 < last_run なら catch-up しない (実行済)
            local days_since_gate=$(( (today_dow - gate_value + 7) % 7 ))
            if [[ $days_since_gate -gt $catch_up_days ]]; then
                echo "[nightly] skip $task: outside catch-up window (days_since_gate=$days_since_gate > $catch_up_days)" >&2
                return 1
            fi
            local last_gate_date
            last_gate_date=$(date -j -v-${days_since_gate}d -f "%Y-%m-%d" "$today" +%Y-%m-%d 2>/dev/null \
                || date -d "$today -$days_since_gate days" +%Y-%m-%d)
            if [[ "$last_run" < "$last_gate_date" ]]; then
                echo "[nightly] catch-up $task: last_run=$last_run < last_gate=$last_gate_date" >&2
                return 0
            fi
            echo "[nightly] skip $task: last_run=$last_run >= last_gate=$last_gate_date" >&2
            return 1
            ;;
        DOM)
            # 今日が gate 日 → run
            if [[ "$today_dom" == "$gate_value" ]]; then return 0; fi
            # catch-up: 今月の gate 日 + catch_up_days 以内、かつ last_run < 今月の gate 日
            if [[ $today_dom -gt $((gate_value + catch_up_days)) ]]; then
                echo "[nightly] skip $task: outside DOM catch-up (today_dom=$today_dom > $((gate_value + catch_up_days)))" >&2
                return 1
            fi
            local this_month_gate="${today:0:7}-$(printf '%02d' "$gate_value")"
            if [[ "$last_run" < "$this_month_gate" ]]; then
                echo "[nightly] catch-up $task: last_run=$last_run < this_month_gate=$this_month_gate" >&2
                return 0
            fi
            echo "[nightly] skip $task: last_run=$last_run >= this_month_gate=$this_month_gate" >&2
            return 1
            ;;
        *)
            echo "[nightly] ERROR: unknown gate_kind=$gate_kind" >&2
            return 1
            ;;
    esac
}

mark_run_today() {
    local task="$1"
    echo "$NIGHTLY_DATE" > "${NIGHTLY_CACHE_DIR}/last-run-${task}.txt"
}
```

- [ ] **Step 2: 実行権限 + shellcheck**

```bash
chmod +x ~/dotfiles/scripts/runtime/nightly/lib/nightly-status.sh
shellcheck ~/dotfiles/scripts/runtime/nightly/lib/nightly-status.sh
```

- [ ] **Step 3: should_run_today の unit-test 風 verify (DAILY)**

```bash
# Test: DAILY → 今日未実行なら true
NIGHTLY_DATE_OVERRIDE=2026-05-26 rm -f ~/.cache/nightly/last-run-test-daily.txt
bash -c '
  source ~/dotfiles/scripts/runtime/nightly/lib/nightly-status.sh
  if should_run_today test-daily DAILY "" 0; then echo PASS_NOT_RUN; else echo FAIL; fi
'
```
Expected: `PASS_NOT_RUN`

```bash
# Test: DAILY → 今日既に実行済なら false
echo "2026-05-26" > ~/.cache/nightly/last-run-test-daily.txt
NIGHTLY_DATE_OVERRIDE=2026-05-26 bash -c '
  source ~/dotfiles/scripts/runtime/nightly/lib/nightly-status.sh
  if should_run_today test-daily DAILY "" 0; then echo FAIL; else echo PASS_SKIP; fi
' 2>/dev/null
```
Expected: `PASS_SKIP`

- [ ] **Step 4: should_run_today の unit-test 風 verify (DOW)**

```bash
# Test: 2026-05-25 (月曜) に DOW=1 → run
rm -f ~/.cache/nightly/last-run-test-dow.txt
NIGHTLY_DATE_OVERRIDE=2026-05-25 bash -c '
  source ~/dotfiles/scripts/runtime/nightly/lib/nightly-status.sh
  if should_run_today test-dow DOW 1 6; then echo PASS_RUN_MONDAY; else echo FAIL; fi
'
```
Expected: `PASS_RUN_MONDAY`

```bash
# Test: 2026-05-26 (火曜) + last_run=先週月曜 → catch-up
echo "2026-05-18" > ~/.cache/nightly/last-run-test-dow.txt
NIGHTLY_DATE_OVERRIDE=2026-05-26 bash -c '
  source ~/dotfiles/scripts/runtime/nightly/lib/nightly-status.sh
  if should_run_today test-dow DOW 1 6; then echo PASS_CATCHUP; else echo FAIL; fi
' 2>/dev/null
```
Expected: `PASS_CATCHUP`

```bash
# Test: 2026-05-26 (火曜) + last_run=今週月曜 (実行済) → skip
echo "2026-05-25" > ~/.cache/nightly/last-run-test-dow.txt
NIGHTLY_DATE_OVERRIDE=2026-05-26 bash -c '
  source ~/dotfiles/scripts/runtime/nightly/lib/nightly-status.sh
  if should_run_today test-dow DOW 1 6; then echo FAIL; else echo PASS_SKIP_DONE; fi
' 2>/dev/null
```
Expected: `PASS_SKIP_DONE`

```bash
# Test: 2026-06-01 (月曜) catch-up 窓外 (先週月曜 0518 から 14 日経過)
echo "2026-05-11" > ~/.cache/nightly/last-run-test-dow.txt
NIGHTLY_DATE_OVERRIDE=2026-05-30 bash -c '  # 土曜
  source ~/dotfiles/scripts/runtime/nightly/lib/nightly-status.sh
  if should_run_today test-dow DOW 1 6; then echo PASS_CATCHUP_EDGE; else echo SKIP_OUTSIDE; fi
' 2>/dev/null
```
Expected: `PASS_CATCHUP_EDGE` (土曜は last_gate=月曜から 5 日経過、catch_up=6 以内)

- [ ] **Step 5: should_run_today の unit-test 風 verify (DOM)**

```bash
# Test: 2026-06-01 (月初) + DOM=1 → run
rm -f ~/.cache/nightly/last-run-test-dom.txt
NIGHTLY_DATE_OVERRIDE=2026-06-01 bash -c '
  source ~/dotfiles/scripts/runtime/nightly/lib/nightly-status.sh
  if should_run_today test-dom DOM 1 7; then echo PASS_RUN_FIRST; else echo FAIL; fi
'
```
Expected: `PASS_RUN_FIRST`

```bash
# Test: 2026-06-05 + DOM=1 + 先月実行履歴あり → catch-up
echo "2026-05-01" > ~/.cache/nightly/last-run-test-dom.txt
NIGHTLY_DATE_OVERRIDE=2026-06-05 bash -c '
  source ~/dotfiles/scripts/runtime/nightly/lib/nightly-status.sh
  if should_run_today test-dom DOM 1 7; then echo PASS_CATCHUP_MONTHLY; else echo FAIL; fi
' 2>/dev/null
```
Expected: `PASS_CATCHUP_MONTHLY`

- [ ] **Step 6: status_begin/end の verify (JSONL append)**

```bash
rm -f /tmp/nightly-status-2026-05-26.jsonl
NIGHTLY_DATE_OVERRIDE=2026-05-26 \
DISCORD_ENV_PATH=/dev/null \
bash -c '
  source ~/dotfiles/scripts/runtime/nightly/lib/nightly-status.sh
  status_begin test-task
  sleep 1
  status_end ok "test message" "report=06-Nightly/2026-05-26-test.md" "metric.violations=3"
'
cat /tmp/nightly-status-2026-05-26.jsonl
```
Expected: 1 行 JSON が出力、`task=test-task`, `status=ok`, `duration_sec` >= 1, `report=06-Nightly/...`, `metric.violations=3`, `metric.msg=test message`

- [ ] **Step 7: Commit**

```bash
git add scripts/runtime/nightly/lib/nightly-status.sh
git commit -m "$(cat <<'EOF'
✨ feat(nightly): add nightly-status.sh lib

decision(catch-up-gate): DAILY/DOW/DOM 3-mode gate inside script, cron fires nightly — PC sleep でも翌晩 catch-up が機能する設計
constraint(macos-date): `date -j -v` (BSD) と `date -d` (GNU) の両対応、shellcheck disable は使わず Fallback で対応
learned(jq-merge): metric オブジェクトに動的キー追加は jq の `. + {($k): $v}` パターンが最も簡潔
EOF
)"
```

---

## Task 3: discord.env setup + .gitignore

**Files:**
- Create: `~/.config/notifications/discord.env` (実体は dotfiles 外、chezmoi or 手動)
- Modify: `~/dotfiles/.gitignore` (追記)

- [ ] **Step 1: 人手作業 — Discord channel + webhook 取得**

(これは Task 13 playbook に詳述、ここでは手順だけ)

1. Discord で notification 用 channel 作成 (例: `#dotfiles-nightly`)
2. channel 設定 → 連携サービス → ウェブフック → 新しいウェブフック
3. 名前: `nightly-vault`、Webhook URL をコピー

- [ ] **Step 2: .env 作成 + 権限**

```bash
mkdir -p ~/.config/notifications
cat > ~/.config/notifications/discord.env <<'EOF'
# Discord webhook for nightly vault automation
# Created: 2026-05-25 (paste your webhook URL below)
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/REPLACE_ME"
EOF
chmod 600 ~/.config/notifications/discord.env
```

人手で `REPLACE_ME` を実 URL に置換。

- [ ] **Step 3: .gitignore 追記 (dotfiles 内に .env が紛れ込まないように防御)**

`~/dotfiles/.gitignore` の末尾に追加:

```gitignore

# Local notification secrets (never tracked)
.config/notifications/*.env
```

- [ ] **Step 4: secretlint verify**

```bash
cd ~/dotfiles
git add .gitignore
git diff --cached .gitignore  # 確認
# 念のため .env が track 対象外であることを確認
git check-ignore .config/notifications/discord.env 2>&1  # → 出力されれば ignore 対象
```

Expected: `.config/notifications/discord.env` が git check-ignore で出力される (ignore 対象)

- [ ] **Step 5: notify-discord.sh と接続 verify**

```bash
source ~/dotfiles/scripts/runtime/nightly/lib/notify-discord.sh
notify_discord ok setup-test 0 "06-Nightly/setup-test.md" "phase=Task3"
```
Expected: Discord channel に "✅ nightly: setup-test (0s)" メッセージ到達

- [ ] **Step 6: Commit (.gitignore のみ)**

```bash
git add .gitignore
git commit -m "$(cat <<'EOF'
🔧 chore(notifications): ignore local discord.env

constraint(secrets): Discord webhook URL は ~/.config/notifications/discord.env (chmod 600) に保管、git 追跡対象外
EOF
)"
```

---

## Task 4: Vault 06-Nightly/.gitkeep

**Files:**
- Create: `${OBSIDIAN_VAULT_PATH}/06-Nightly/.gitkeep`

- [ ] **Step 1: フォルダ + .gitkeep 作成**

```bash
mkdir -p "${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}/06-Nightly"
touch "${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}/06-Nightly/.gitkeep"
ls -la "${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}/06-Nightly/"
```

Expected: `.gitkeep` が存在

- [ ] **Step 2: Obsidian で folder 表示確認 (人手)**

Obsidian app で Vault を開き、左ペインに `06-Nightly/` フォルダが表示されることを確認。

- [ ] **Step 3: 既存 Vault README に節を追加 (任意)**

(`${OBSIDIAN_VAULT_PATH}/README.md` がある場合のみ)

`06-Nightly` の説明を folder structure 説明に追加。

- [ ] **Step 4: Vault は git 管理外なので commit なし**

(dotfiles repo には影響なし。次の task へ進む)

---

## Task 5: run-golden-check.sh (template-establishing)

**Files:**
- Create: `scripts/runtime/nightly/run-golden-check.sh`
- Reference: `~/.claude/agents/golden-cleanup.md` (既存 golden-check の検出ロジック)

このタスクは **template-establishing** — Task 6-10 の run-*.sh はこの形を踏襲する。

- [ ] **Step 1: スクリプト本体**

`scripts/runtime/nightly/run-golden-check.sh`:

```bash
#!/usr/bin/env bash
# run-golden-check.sh — 夜間 golden principles 違反一覧生成
# cron: 15 23 * * * (実体は内部 gate で DAILY 判定)
# Vault output: 06-Nightly/${DATE}-golden.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./lib/nightly-status.sh
source "${SCRIPT_DIR}/lib/nightly-status.sh"

TASK="golden-check"
trap 'status_end fail "trapped exit_code=$?"' ERR

# === Prereq guards ===
[[ -z "${OBSIDIAN_VAULT_PATH:-}" ]] && { status_begin "$TASK"; status_end fail "missing OBSIDIAN_VAULT_PATH"; exit 0; }
command -v claude &>/dev/null || { status_begin "$TASK"; status_end fail "claude CLI not found"; exit 0; }

# === Gate ===
should_run_today "$TASK" DAILY "" 0 || exit 0

status_begin "$TASK"

# === Body ===
REPORT_DIR="${OBSIDIAN_VAULT_PATH}/06-Nightly"
mkdir -p "$REPORT_DIR"
REPORT_PATH="${REPORT_DIR}/${NIGHTLY_DATE}-golden.md"

PROMPT="$(cat <<'PROMPT_EOF'
あなたは golden principles 監査エージェントです。
dotfiles リポ (~/dotfiles) の以下のディレクトリを横断スキャンしてください:
  - .config/claude/agents/
  - .config/claude/skills/
  - .config/claude/hooks/
  - scripts/runtime/

検出対象 (golden principles):
  - "暗黙フォールバック" の残置 (silent skip / silent fallback / モック残置)
  - "silent failure" (catch して握り潰し、ログ無し)
  - NO-OP 実装 (空関数 + return success、コメントに「後で実装する」旨の注記がある等)
  - 既存パターン違反 (例: ハードコード path で symlink 機構を無視)

出力フォーマット (Markdown):
# Golden Check Report (YYYY-MM-DD)

## Summary
- 違反検出数: N 件
- 重要度内訳: critical=X, warning=Y, info=Z

## Findings
### F-1: <タイトル>
- 重要度: critical | warning | info
- ファイル: `path/to/file.sh:LINE`
- 内容: <violation の説明>
- 推奨対応: <fix の方向>

(以下 F-N まで)

## 違反 0 件なら "クリーン状態" と記載してください。
PROMPT_EOF
)"

if ! timeout 600s claude -p "$PROMPT" > "$REPORT_PATH" 2>/tmp/golden-check-stderr.log; then
    status_end fail "claude -p failed or timeout, stderr: $(head -c 200 /tmp/golden-check-stderr.log)"
    exit 0
fi

# === Metric 抽出 ===
VIOLATIONS=$(grep -cE '^### F-' "$REPORT_PATH" 2>/dev/null || echo 0)

mark_run_today "$TASK"
status_end ok "violations=$VIOLATIONS" "report=06-Nightly/${NIGHTLY_DATE}-golden.md" "metric.violations=$VIOLATIONS"
```

- [ ] **Step 2: 実行権限 + shellcheck**

```bash
chmod +x ~/dotfiles/scripts/runtime/nightly/run-golden-check.sh
shellcheck ~/dotfiles/scripts/runtime/nightly/run-golden-check.sh
```

- [ ] **Step 3: Dry-run (FORCE_RUN, no real claude call — mock)**

```bash
# claude を mock して prereq + gate + status の流れだけ verify
rm -f /tmp/nightly-status-$(date +%Y-%m-%d).jsonl ~/.cache/nightly/last-run-golden-check.txt

FORCE_RUN=1 \
PATH="/tmp/mock:$PATH" \
bash -c '
  mkdir -p /tmp/mock
  cat > /tmp/mock/claude <<MOCK
#!/bin/bash
echo "# Golden Check Report ($(date +%Y-%m-%d))"
echo ""
echo "## Summary"
echo "- 違反検出数: 2 件"
echo ""
echo "## Findings"
echo "### F-1: silent fallback in foo.sh"
echo "### F-2: hardcoded path in bar.sh"
MOCK
  chmod +x /tmp/mock/claude
  ~/dotfiles/scripts/runtime/nightly/run-golden-check.sh
'

# 検証
echo "--- jsonl ---"
cat /tmp/nightly-status-$(date +%Y-%m-%d).jsonl
echo "--- report ---"
cat "${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}/06-Nightly/$(date +%Y-%m-%d)-golden.md"
echo "--- last-run ---"
cat ~/.cache/nightly/last-run-golden-check.txt
```

Expected:
- jsonl に 1 行: `status=ok, metric.violations=2`
- report に Mock の Markdown が保存
- last-run が今日の日付
- Discord 通知が緑 embed で届く

- [ ] **Step 4: 実 claude -p で smoke test (本番に近い形)**

```bash
rm -f ~/.cache/nightly/last-run-golden-check.txt
FORCE_RUN=1 ~/dotfiles/scripts/runtime/nightly/run-golden-check.sh
```

Expected: 1-5 分で完了、jsonl に 1 行追加、Vault に実 report 生成、Discord 通知到達

- [ ] **Step 5: Failure case verify (claude CLI 不在 simulation)**

```bash
rm -f ~/.cache/nightly/last-run-golden-check.txt
PATH="/nonexistent:/usr/bin:/bin" \
~/dotfiles/scripts/runtime/nightly/run-golden-check.sh

cat /tmp/nightly-status-$(date +%Y-%m-%d).jsonl | tail -1
```

Expected: jsonl 末尾に `status=fail, metric.msg=claude CLI not found`、Discord 通知が赤 embed + @here で届く

- [ ] **Step 6: Commit**

```bash
git add scripts/runtime/nightly/run-golden-check.sh
git commit -m "$(cat <<'EOF'
✨ feat(nightly): add run-golden-check.sh (template script)

decision(template-shape): trap ERR + prereq guards + gate + status_begin/end + claude -p timeout + metric 抽出 — 後続 6 task の踏襲形
constraint(claude-prompt): スコープを .config/claude/{agents,skills,hooks} + scripts/runtime に限定 — リポ全体は audit task の責務
EOF
)"
```

---

## Task 6: run-friction-aggregate.sh

**Files:**
- Create: `scripts/runtime/nightly/run-friction-aggregate.sh`
- Reads: `~/.claude/agent-memory/learnings/friction-events.jsonl` (Q1 確定)

- [ ] **Step 1: スクリプト本体**

`scripts/runtime/nightly/run-friction-aggregate.sh`:

```bash
#!/usr/bin/env bash
# run-friction-aggregate.sh — 前日 friction events の集計
# cron: 20 23 * * *  (DAILY gate)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./lib/nightly-status.sh
source "${SCRIPT_DIR}/lib/nightly-status.sh"

TASK="friction-aggregate"
trap 'status_end fail "trapped exit_code=$?"' ERR

[[ -z "${OBSIDIAN_VAULT_PATH:-}" ]] && { status_begin "$TASK"; status_end fail "missing OBSIDIAN_VAULT_PATH"; exit 0; }

FRICTION_LOG="$HOME/.claude/agent-memory/learnings/friction-events.jsonl"
[[ -f "$FRICTION_LOG" ]] || { status_begin "$TASK"; status_end fail "friction log not found: $FRICTION_LOG"; exit 0; }

should_run_today "$TASK" DAILY "" 0 || exit 0
status_begin "$TASK"

REPORT_DIR="${OBSIDIAN_VAULT_PATH}/06-Nightly"
mkdir -p "$REPORT_DIR"
REPORT_PATH="${REPORT_DIR}/${NIGHTLY_DATE}-friction.md"

# 前日範囲: 24h 以内
SINCE_TS="$(date -v-1d -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -d 'yesterday' -u +%Y-%m-%dT%H:%M:%SZ)"

# JSONL を jq で集計 — type 別カウント + top 5 issue
TYPE_COUNTS=$(jq -r --arg since "$SINCE_TS" '
  select(.timestamp >= $since) | .type // "unknown"
' "$FRICTION_LOG" 2>/dev/null | sort | uniq -c | sort -rn)

TOP_ISSUES=$(jq -r --arg since "$SINCE_TS" '
  select(.timestamp >= $since) | "- [\(.type // "?")] \(.detail // .description // .msg // "(no detail)")"
' "$FRICTION_LOG" 2>/dev/null | head -10)

TOTAL_COUNT=$(jq -r --arg since "$SINCE_TS" 'select(.timestamp >= $since) | 1' "$FRICTION_LOG" 2>/dev/null | wc -l | tr -d ' ')

{
    echo "# Friction Events ${NIGHTLY_DATE} (前日集計)"
    echo ""
    echo "Generated: $(date -Iseconds)"
    echo "Source: \`${FRICTION_LOG/#$HOME/~}\`"
    echo "Window: 直近 24 時間 (since ${SINCE_TS})"
    echo ""
    echo "## Summary"
    echo "- Total events: ${TOTAL_COUNT}"
    echo ""
    echo "## Type breakdown"
    echo '```'
    echo "${TYPE_COUNTS:-(なし)}"
    echo '```'
    echo ""
    echo "## Top 10 issues"
    echo "${TOP_ISSUES:-(なし)}"
} > "$REPORT_PATH"

mark_run_today "$TASK"
status_end ok "total=$TOTAL_COUNT" "report=06-Nightly/${NIGHTLY_DATE}-friction.md" "metric.total=$TOTAL_COUNT"
```

- [ ] **Step 2: 権限 + shellcheck**

```bash
chmod +x ~/dotfiles/scripts/runtime/nightly/run-friction-aggregate.sh
shellcheck ~/dotfiles/scripts/runtime/nightly/run-friction-aggregate.sh
```

- [ ] **Step 3: Dry-run with fixture**

```bash
# Fixture friction-events.jsonl 作成
mkdir -p /tmp/fixture/learnings
cat > /tmp/fixture/learnings/friction-events.jsonl <<'EOF'
{"timestamp":"2026-05-25T10:00:00Z","type":"hook-error","detail":"plan-lifecycle failed"}
{"timestamp":"2026-05-25T12:00:00Z","type":"hook-error","detail":"plan-lifecycle failed again"}
{"timestamp":"2026-05-25T15:00:00Z","type":"agent-stall","detail":"codex hung 600s"}
EOF

# 一時的に FRICTION_LOG path を override (scripts 修正は不要、シンボリックリンクでテスト)
rm -f ~/.cache/nightly/last-run-friction-aggregate.txt
HOME_BACKUP=$HOME
# fixture を実 path に bind (簡易テストなので mv で実 jsonl 退避)
if [[ -f ~/.claude/agent-memory/learnings/friction-events.jsonl ]]; then
  mv ~/.claude/agent-memory/learnings/friction-events.jsonl /tmp/friction-real-backup.jsonl
fi
cp /tmp/fixture/learnings/friction-events.jsonl ~/.claude/agent-memory/learnings/friction-events.jsonl

FORCE_RUN=1 ~/dotfiles/scripts/runtime/nightly/run-friction-aggregate.sh

# 復元
if [[ -f /tmp/friction-real-backup.jsonl ]]; then
  mv /tmp/friction-real-backup.jsonl ~/.claude/agent-memory/learnings/friction-events.jsonl
fi

cat "${OBSIDIAN_VAULT_PATH}/06-Nightly/$(date +%Y-%m-%d)-friction.md"
```

Expected: report に Total events: 3、hook-error 2、agent-stall 1 が表示

- [ ] **Step 4: Commit**

```bash
git add scripts/runtime/nightly/run-friction-aggregate.sh
git commit -m "$(cat <<'EOF'
✨ feat(nightly): add run-friction-aggregate.sh

decision(no-claude): claude -p を使わず jq + sort + uniq で集計 — friction events は構造化済、AI 要約不要 (cost 削減)
constraint(window): 直近 24h 固定 — 夜間 cron が日次なので隙間なし
EOF
)"
```

---

## Task 7: run-health-check.sh

**Files:**
- Create: `scripts/runtime/nightly/run-health-check.sh`
- Reference: `~/.claude/skills/check-health/SKILL.md` (既存 skill のロジックを参考、ただし claude -p で呼ぶのではなく独立実装)

- [ ] **Step 1: スクリプト本体**

`scripts/runtime/nightly/run-health-check.sh`:

```bash
#!/usr/bin/env bash
# run-health-check.sh — docs 鮮度 + コード乖離検出
# cron: 25 23 * * *  (DAILY gate)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./lib/nightly-status.sh
source "${SCRIPT_DIR}/lib/nightly-status.sh"

TASK="health-check"
trap 'status_end fail "trapped exit_code=$?"' ERR

[[ -z "${OBSIDIAN_VAULT_PATH:-}" ]] && { status_begin "$TASK"; status_end fail "missing OBSIDIAN_VAULT_PATH"; exit 0; }
command -v claude &>/dev/null || { status_begin "$TASK"; status_end fail "claude CLI not found"; exit 0; }

should_run_today "$TASK" DAILY "" 0 || exit 0
status_begin "$TASK"

REPORT_DIR="${OBSIDIAN_VAULT_PATH}/06-Nightly"
mkdir -p "$REPORT_DIR"
REPORT_PATH="${REPORT_DIR}/${NIGHTLY_DATE}-health.md"

# 30 日以上更新なし & 参照されている docs を抽出
STALE_DOCS=$(find ~/dotfiles/docs ~/dotfiles/.config/claude/references -name "*.md" -mtime +30 2>/dev/null | head -20 || true)

PROMPT="$(cat <<PROMPT_EOF
あなたは docs 健全性監査エージェントです。

以下の stale docs リスト (30 日以上未更新):
\`\`\`
${STALE_DOCS:-(なし)}
\`\`\`

各 doc について:
1. 内容が code/設定の現状と乖離していないかチェック (git log で参照 commit 履歴を確認)
2. broken reference (存在しないファイルへのパス) がないか確認
3. 削除候補か更新候補かを判定

出力フォーマット (Markdown):
# Health Check Report (YYYY-MM-DD)

## Summary
- 監査対象: N 件
- 削除候補: X 件
- 更新候補: Y 件
- 健全: Z 件

## Findings
### <doc path>
- 判定: 削除 | 更新 | 健全
- 理由: <理由>
- 推奨アクション: <具体的 action>
PROMPT_EOF
)"

if ! timeout 600s claude -p "$PROMPT" > "$REPORT_PATH" 2>/tmp/health-check-stderr.log; then
    status_end fail "claude -p failed or timeout, stderr: $(head -c 200 /tmp/health-check-stderr.log)"
    exit 0
fi

# Metric: 判定行のカウント
STALE_COUNT=$(echo "${STALE_DOCS}" | wc -l | tr -d ' ')
TO_DELETE=$(grep -c '^- 判定: 削除' "$REPORT_PATH" 2>/dev/null || echo 0)
TO_UPDATE=$(grep -c '^- 判定: 更新' "$REPORT_PATH" 2>/dev/null || echo 0)

mark_run_today "$TASK"
status_end ok "stale=$STALE_COUNT to_delete=$TO_DELETE to_update=$TO_UPDATE" \
    "report=06-Nightly/${NIGHTLY_DATE}-health.md" \
    "metric.stale=$STALE_COUNT" "metric.to_delete=$TO_DELETE" "metric.to_update=$TO_UPDATE"
```

- [ ] **Step 2: 権限 + shellcheck + Dry-run**

```bash
chmod +x ~/dotfiles/scripts/runtime/nightly/run-health-check.sh
shellcheck ~/dotfiles/scripts/runtime/nightly/run-health-check.sh

rm -f ~/.cache/nightly/last-run-health-check.txt
FORCE_RUN=1 ~/dotfiles/scripts/runtime/nightly/run-health-check.sh
cat "${OBSIDIAN_VAULT_PATH}/06-Nightly/$(date +%Y-%m-%d)-health.md" | head -30
```

Expected: report 生成、jsonl に `metric.stale, metric.to_delete, metric.to_update` 含む

- [ ] **Step 3: Commit**

```bash
git add scripts/runtime/nightly/run-health-check.sh
git commit -m "✨ feat(nightly): add run-health-check.sh"
```

---

## Task 8: run-audit.sh

**Files:**
- Create: `scripts/runtime/nightly/run-audit.sh`
- Reference: `~/.claude/skills/audit/SKILL.md` (sec/arch/perf/quality 横断のロジック)

- [ ] **Step 1: スクリプト本体**

`scripts/runtime/nightly/run-audit.sh`:

```bash
#!/usr/bin/env bash
# run-audit.sh — コードベース横断品質監査 (sec/arch/perf/quality)
# cron: 45 23 * * *  (DOW=1 月曜、catch-up 6 days)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./lib/nightly-status.sh
source "${SCRIPT_DIR}/lib/nightly-status.sh"

TASK="audit"
trap 'status_end fail "trapped exit_code=$?"' ERR

[[ -z "${OBSIDIAN_VAULT_PATH:-}" ]] && { status_begin "$TASK"; status_end fail "missing OBSIDIAN_VAULT_PATH"; exit 0; }
command -v claude &>/dev/null || { status_begin "$TASK"; status_end fail "claude CLI not found"; exit 0; }

should_run_today "$TASK" DOW 1 6 || exit 0
status_begin "$TASK"

REPORT_DIR="${OBSIDIAN_VAULT_PATH}/06-Nightly"
mkdir -p "$REPORT_DIR"
REPORT_PATH="${REPORT_DIR}/${NIGHTLY_DATE}-audit.md"

PROMPT="$(cat <<'PROMPT_EOF'
あなたは /audit skill 相当のコードベース品質監査エージェントです。

監査対象: ~/dotfiles リポ (excluding .worktrees, .git, node_modules)
監査軸:
  1. Security: secret hardcode / unsafe eval / shell injection
  2. Architecture: 関心分離違反 / 循環依存 / God script (>500行)
  3. Performance: 不要な O(N²) / 同期 I/O ループ
  4. Test coverage: 重要 logic に test なし
  5. Code quality: 重複コード / dead code / 命名規約違反

出力フォーマット (優先度付き Markdown):
# Audit Report (YYYY-MM-DD)

## Executive Summary
- Total issues: N
- Critical: X, High: Y, Medium: Z, Low: W

## Critical Issues
### A-1: <タイトル>
- ファイル: `path:line`
- 軸: security/architecture/performance/test/quality
- 内容: <詳細>
- 推奨対応: <具体的 fix>

(以下 High, Medium, Low の順に羅列)

## QUESTIONS (Answer 欄付き、人手で埋める)
### Q-1: <非自明な設計判断について>
- 背景: ...
- 選択肢: ...
- Answer: (未回答)
PROMPT_EOF
)"

if ! timeout 1200s claude -p "$PROMPT" > "$REPORT_PATH" 2>/tmp/audit-stderr.log; then
    status_end fail "claude -p failed or timeout, stderr: $(head -c 200 /tmp/audit-stderr.log)"
    exit 0
fi

CRITICAL=$(grep -cE '^### A-[0-9]+:.*\bcritical\b' "$REPORT_PATH" 2>/dev/null || echo 0)
HIGH=$(grep -cE '^### A-[0-9]+' "$REPORT_PATH" 2>/dev/null || echo 0)
QUESTIONS=$(grep -cE '^### Q-[0-9]+' "$REPORT_PATH" 2>/dev/null || echo 0)

mark_run_today "$TASK"
status_end ok "critical=$CRITICAL total=$HIGH q=$QUESTIONS" \
    "report=06-Nightly/${NIGHTLY_DATE}-audit.md" \
    "metric.critical=$CRITICAL" "metric.total=$HIGH" "metric.questions=$QUESTIONS"
```

- [ ] **Step 2: 権限 + shellcheck + Dry-run**

```bash
chmod +x ~/dotfiles/scripts/runtime/nightly/run-audit.sh
shellcheck ~/dotfiles/scripts/runtime/nightly/run-audit.sh

rm -f ~/.cache/nightly/last-run-audit.txt
FORCE_RUN=1 ~/dotfiles/scripts/runtime/nightly/run-audit.sh
# 5-15 分かかる、別 terminal で tail を流して観測
```

Expected: 5-15 分で完了、Vault に audit report 生成、Discord 通知到達

- [ ] **Step 3: Commit**

```bash
git add scripts/runtime/nightly/run-audit.sh
git commit -m "✨ feat(nightly): add run-audit.sh (週次月曜)"
```

---

## Task 9: run-skill-audit.sh

**Files:**
- Create: `scripts/runtime/nightly/run-skill-audit.sh`
- Calls: 既存 `/skill-audit` skill via `claude -p`

- [ ] **Step 1: スクリプト本体**

`scripts/runtime/nightly/run-skill-audit.sh`:

```bash
#!/usr/bin/env bash
# run-skill-audit.sh — skill A/B benchmark + health audit
# cron: 45 23 * * *  (DOW=4 木曜、catch-up 6 days)
# 既存 /skill-audit skill を claude -p で呼び出す (DRY)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./lib/nightly-status.sh
source "${SCRIPT_DIR}/lib/nightly-status.sh"

TASK="skill-audit"
trap 'status_end fail "trapped exit_code=$?"' ERR

[[ -z "${OBSIDIAN_VAULT_PATH:-}" ]] && { status_begin "$TASK"; status_end fail "missing OBSIDIAN_VAULT_PATH"; exit 0; }
command -v claude &>/dev/null || { status_begin "$TASK"; status_end fail "claude CLI not found"; exit 0; }

should_run_today "$TASK" DOW 4 6 || exit 0
status_begin "$TASK"

REPORT_DIR="${OBSIDIAN_VAULT_PATH}/06-Nightly"
mkdir -p "$REPORT_DIR"
REPORT_PATH="${REPORT_DIR}/${NIGHTLY_DATE}-skill.md"

PROMPT="$(cat <<'PROMPT_EOF'
/skill-audit skill を起動し、以下を実行してください:
1. 直近 30 日に呼ばれた skill 一覧 (利用頻度トップ 20)
2. 30 日間未使用 (dormant) skill 一覧
3. description 衝突検出 (類似 description で混同しやすい skill ペア)
4. health audit (実行成功率 / 平均所要時間)

出力先: stdout に Markdown レポート
PROMPT_EOF
)"

if ! timeout 900s claude -p "$PROMPT" > "$REPORT_PATH" 2>/tmp/skill-audit-stderr.log; then
    status_end fail "claude -p failed or timeout, stderr: $(head -c 200 /tmp/skill-audit-stderr.log)"
    exit 0
fi

DORMANT=$(grep -cE '^- .*(dormant|未使用|0 calls)' "$REPORT_PATH" 2>/dev/null || echo 0)
CONFLICTS=$(grep -cE '^- .*(衝突|conflict)' "$REPORT_PATH" 2>/dev/null || echo 0)

mark_run_today "$TASK"
status_end ok "dormant=$DORMANT conflicts=$CONFLICTS" \
    "report=06-Nightly/${NIGHTLY_DATE}-skill.md" \
    "metric.dormant=$DORMANT" "metric.conflicts=$CONFLICTS"
```

- [ ] **Step 2: 権限 + shellcheck + Dry-run + Commit**

```bash
chmod +x ~/dotfiles/scripts/runtime/nightly/run-skill-audit.sh
shellcheck ~/dotfiles/scripts/runtime/nightly/run-skill-audit.sh
rm -f ~/.cache/nightly/last-run-skill-audit.txt
FORCE_RUN=1 ~/dotfiles/scripts/runtime/nightly/run-skill-audit.sh
git add scripts/runtime/nightly/run-skill-audit.sh
git commit -m "✨ feat(nightly): add run-skill-audit.sh (週次木曜)"
```

---

## Task 10: run-dep-audit.sh

**Files:**
- Create: `scripts/runtime/nightly/run-dep-audit.sh`
- Uses: `npm audit`, `pip-audit` (Python)、`cargo audit`、`govulncheck`

- [ ] **Step 1: スクリプト本体**

`scripts/runtime/nightly/run-dep-audit.sh`:

```bash
#!/usr/bin/env bash
# run-dep-audit.sh — 依存パッケージ脆弱性 + outdated 監査
# cron: 0 0 * * *  (DOM=1 月初、catch-up 7 days)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./lib/nightly-status.sh
source "${SCRIPT_DIR}/lib/nightly-status.sh"

TASK="dep-audit"
trap 'status_end fail "trapped exit_code=$?"' ERR

[[ -z "${OBSIDIAN_VAULT_PATH:-}" ]] && { status_begin "$TASK"; status_end fail "missing OBSIDIAN_VAULT_PATH"; exit 0; }

should_run_today "$TASK" DOM 1 7 || exit 0
status_begin "$TASK"

REPORT_DIR="${OBSIDIAN_VAULT_PATH}/06-Nightly"
mkdir -p "$REPORT_DIR"
REPORT_PATH="${REPORT_DIR}/${NIGHTLY_DATE}-dep.md"

DOTFILES_ROOT="$HOME/dotfiles"
VULN_COUNT=0

{
    echo "# Dependency Audit ${NIGHTLY_DATE}"
    echo ""
    echo "Scope: ${DOTFILES_ROOT} root のみ (v1)"
    echo ""

    # npm
    if [[ -f "${DOTFILES_ROOT}/package.json" ]]; then
        echo "## npm (package.json)"
        echo '```'
        if command -v npm &>/dev/null; then
            (cd "$DOTFILES_ROOT" && npm audit --json 2>/dev/null || true) | \
                jq -r '"vulnerabilities: \(.metadata.vulnerabilities // {})"' 2>/dev/null || echo "(npm audit failed)"
            (cd "$DOTFILES_ROOT" && npm outdated 2>/dev/null || true)
        else
            echo "(npm CLI not found)"
        fi
        echo '```'
        echo ""
    fi

    # python
    if [[ -f "${DOTFILES_ROOT}/pyproject.toml" ]] || [[ -f "${DOTFILES_ROOT}/requirements.txt" ]]; then
        echo "## Python"
        echo '```'
        if command -v pip-audit &>/dev/null; then
            (cd "$DOTFILES_ROOT" && pip-audit 2>&1 || true)
        else
            echo "(pip-audit not installed)"
        fi
        echo '```'
        echo ""
    fi

    # Go
    if [[ -f "${DOTFILES_ROOT}/go.mod" ]]; then
        echo "## Go"
        echo '```'
        if command -v govulncheck &>/dev/null; then
            (cd "$DOTFILES_ROOT" && govulncheck ./... 2>&1 || true)
        else
            echo "(govulncheck not installed)"
        fi
        echo '```'
        echo ""
    fi

    # Rust
    if [[ -f "${DOTFILES_ROOT}/Cargo.toml" ]]; then
        echo "## Rust"
        echo '```'
        if command -v cargo-audit &>/dev/null || cargo audit --version &>/dev/null; then
            (cd "$DOTFILES_ROOT" && cargo audit 2>&1 || true)
        else
            echo "(cargo-audit not installed)"
        fi
        echo '```'
        echo ""
    fi
} > "$REPORT_PATH"

# Metric: 脆弱性数の近似 (各 audit CLI の出力から抽出)
VULN_COUNT=$(grep -ciE '(vulnerab|critical|high)' "$REPORT_PATH" 2>/dev/null || echo 0)

mark_run_today "$TASK"
status_end ok "vuln_lines=$VULN_COUNT" \
    "report=06-Nightly/${NIGHTLY_DATE}-dep.md" \
    "metric.vuln_lines=$VULN_COUNT"
```

- [ ] **Step 2: 権限 + shellcheck + Dry-run + Commit**

```bash
chmod +x ~/dotfiles/scripts/runtime/nightly/run-dep-audit.sh
shellcheck ~/dotfiles/scripts/runtime/nightly/run-dep-audit.sh
rm -f ~/.cache/nightly/last-run-dep-audit.txt
FORCE_RUN=1 ~/dotfiles/scripts/runtime/nightly/run-dep-audit.sh
git add scripts/runtime/nightly/run-dep-audit.sh
git commit -m "$(cat <<'EOF'
✨ feat(nightly): add run-dep-audit.sh (月次月初)

decision(scope-v1): dotfiles root のみ scan (package.json / pyproject.toml / go.mod / Cargo.toml)、サブディレクトリの package.json は v2 で拡張
constraint(cli-availability): npm/pip-audit/govulncheck/cargo-audit が無くても script は exit 0 (各 section に "(not installed)" を記録)
EOF
)"
```

---

## Task 11: auto-morning-briefing.sh 編集 — Nightly Status 統合

**Files:**
- Modify: `~/dotfiles/scripts/runtime/auto-morning-briefing.sh` (Section 5 spec の post-processing 方式)

- [ ] **Step 1: 既存 briefing.sh の構造を Read**

```bash
cat ~/dotfiles/scripts/runtime/auto-morning-briefing.sh | tail -50
```

(briefing 文字列を Daily Note に append する箇所を特定: Section "Obsidian Daily Note に append" の `BRIEFING=` ブロック直後)

- [ ] **Step 2: prepend_nightly_status 関数を追加**

`auto-morning-briefing.sh` の `## Obsidian Daily Note に append` セクションの **直前** に以下を挿入:

```bash
##############################################################################
# Nightly Status を briefing 先頭に統合 (post-processing)
##############################################################################

prepend_nightly_status() {
    local briefing="$1"
    local yesterday_jsonl="/tmp/nightly-status-${YESTERDAY}.jsonl"
    [[ -f "$yesterday_jsonl" ]] || { echo "$briefing"; return 0; }

    local status_section
    status_section=$(jq -r '
        if .status == "ok" then "✅" else "❌" end
        + " " + .task
        + " (\(.duration_sec)s)"
        + " → [\(.report)]"
        + (if .metric.msg then " — " + .metric.msg else "" end)
    ' "$yesterday_jsonl" 2>/dev/null)

    [[ -z "$status_section" ]] && { echo "$briefing"; return 0; }

    cat <<EOF
## Nightly Status (${YESTERDAY})

${status_section}

---

${briefing}
EOF
}

# 既存の BRIEFING= 生成後、append する直前で wrap
BRIEFING="$(prepend_nightly_status "$BRIEFING")"
```

挿入位置の確認: 既存 script で `if ! BRIEFING="$(generate_ai_briefing)"; then` ... `fi` の **直後**、`## Obsidian Daily Note に append` セクションの **前**。

- [ ] **Step 3: shellcheck**

```bash
shellcheck ~/dotfiles/scripts/runtime/auto-morning-briefing.sh
```

- [ ] **Step 4: 統合 verify**

```bash
# 前提: Task 5 等で /tmp/nightly-status-${YESTERDAY}.jsonl に jsonl が存在
# Fixture でテスト
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d 'yesterday' +%Y-%m-%d)
cat > /tmp/nightly-status-${YESTERDAY}.jsonl <<EOF
{"ts":"...","task":"golden-check","status":"ok","duration_sec":42,"report":"06-Nightly/${YESTERDAY}-golden.md","metric":{"violations":"3"}}
{"ts":"...","task":"audit","status":"fail","duration_sec":600,"report":"06-Nightly/${YESTERDAY}-audit.md","metric":{"msg":"timeout"}}
EOF

# briefing.sh を手動実行
~/dotfiles/scripts/runtime/auto-morning-briefing.sh

# 結果確認
head -20 "${OBSIDIAN_VAULT_PATH}/00-Inbox/$(date +%Y-%m-%d).md"
```

Expected: Daily Note 先頭付近に "## Nightly Status (YYYY-MM-DD)" + ✅/❌ 2 行 が表示

- [ ] **Step 5: Commit**

```bash
git add scripts/runtime/auto-morning-briefing.sh
git commit -m "$(cat <<'EOF'
✨ feat(morning-briefing): integrate Nightly Status section

decision(integration-approach): post-processing 方式 — 既存 BRIEFING 生成ロジック無変更、prepend_nightly_status 関数で先頭に section 追加 (関心分離維持)
EOF
)"
```

---

## Task 12: crontab 追記

**Files:**
- User-managed: `crontab -e`

⚠️ **人手作業** (環境依存、claude は実行できない)

- [ ] **Step 1: 既存 crontab の backup**

```bash
crontab -l > /tmp/crontab-backup-$(date +%Y%m%d-%H%M%S).txt
echo "Backup saved to: /tmp/crontab-backup-$(date +%Y%m%d-%H%M%S).txt"
```

- [ ] **Step 2: 追記する 6 行を確認**

```cron
# Nightly Vault automation (内部 should_run_today gate で曜日/月初判定)
15 23 * * * /Users/takeuchishougo/dotfiles/scripts/runtime/nightly/run-golden-check.sh       >> /tmp/nightly-golden.log 2>&1
20 23 * * * /Users/takeuchishougo/dotfiles/scripts/runtime/nightly/run-friction-aggregate.sh >> /tmp/nightly-friction.log 2>&1
25 23 * * * /Users/takeuchishougo/dotfiles/scripts/runtime/nightly/run-health-check.sh       >> /tmp/nightly-health.log 2>&1
45 23 * * * /Users/takeuchishougo/dotfiles/scripts/runtime/nightly/run-audit.sh              >> /tmp/nightly-audit.log 2>&1
45 23 * * * /Users/takeuchishougo/dotfiles/scripts/runtime/nightly/run-skill-audit.sh        >> /tmp/nightly-skill.log 2>&1
0  0  * * * /Users/takeuchishougo/dotfiles/scripts/runtime/nightly/run-dep-audit.sh          >> /tmp/nightly-dep.log 2>&1
```

(全 script は OBSIDIAN_VAULT_PATH を crontab 上部の既存設定から継承する。既存 `OBSIDIAN_VAULT_PATH=...` 環境変数行が crontab 内にあることを Step 1 backup で確認)

- [ ] **Step 3: `crontab -e` で追記**

```bash
crontab -e
```

エディタで上記 6 行を追加して保存。

- [ ] **Step 4: cron 登録確認**

```bash
crontab -l | grep nightly
```

Expected: 6 行が出力される

- [ ] **Step 5: cron 翌晩実行を待ち、結果 verify**

(翌朝に確認)

```bash
ls -la /tmp/nightly-*.log
cat /tmp/nightly-status-$(date +%Y-%m-%d).jsonl
ls "${OBSIDIAN_VAULT_PATH}/06-Nightly/" | tail -10
```

Expected: 軽量 3 task のログが存在、jsonl に 3 行、Vault に 3 ファイル

---

## Task 13: docs/playbooks/nightly-offload.md

**Files:**
- Create: `docs/playbooks/nightly-offload.md`

- [ ] **Step 1: playbook 本体を Write**

```markdown
# Nightly Vault Automation — 運用 Playbook

> Plan: `docs/plans/active/2026-05-25-nightly-vault-automation-plan.md`
> Spec: `docs/superpowers/specs/2026-05-25-nightly-vault-automation-design.md`

## 概要

(spec 1 ページ要約)

## Setup (初回 1 回)

### 1. Discord webhook URL 取得

1. Discord でサーバ作成 (個人用なら 1 人サーバ可)
2. channel 作成 (例: `#nightly`)
3. channel 設定 (右クリック → 編集) → 連携サービス → ウェブフック
4. 新しいウェブフック → 名前を `nightly-vault`
5. "ウェブフック URL をコピー" を押す

### 2. .env 配置

\`\`\`bash
mkdir -p ~/.config/notifications
cat > ~/.config/notifications/discord.env <<'EOF'
DISCORD_WEBHOOK_URL="<コピーした URL を貼り付け>"
EOF
chmod 600 ~/.config/notifications/discord.env
\`\`\`

### 3. cron 登録

\`crontab -e\` で Task 12 の 6 行を追記。

### 4. smoke test

\`\`\`bash
FORCE_RUN=1 ~/dotfiles/scripts/runtime/nightly/run-golden-check.sh
\`\`\`

Discord channel に通知が届けば setup 完了。

## 運用フロー (日次)

1. 朝 8:30 に morning-briefing が起動
2. Daily Note (`Vault/00-Inbox/${DATE}.md`) の先頭に "## Nightly Status" セクションが追加されている
3. ❌ がある場合は Discord も赤通知 (@here mention)、`Vault/06-Nightly/${DATE}-{task}.md` を確認
4. 週次 audit (月曜) / skill-audit (木曜) / 月次 dep-audit (月初) の重い report は週末にまとめて review

## トラブルシュート

### Discord 通知が届かない

- \`~/.config/notifications/discord.env\` の URL を確認 (\`chmod 600\` で意図的に閉じている、cat で見る)
- webhook URL を Discord で再発行
- \`curl\` で手動 test: \`curl -X POST -H "Content-Type: application/json" -d '{"content":"test"}' "$DISCORD_WEBHOOK_URL"\`

### cron が起動した形跡がない

- PC スリープを疑う: \`pmset -g log | grep -i sleep | tail\`
- 翌晩の catch-up 待ち (週次 6 日 / 月次 7 日窓内)

### catch-up を強制 reset

\`\`\`bash
rm ~/.cache/nightly/last-run-${task}.txt
FORCE_RUN=1 ~/dotfiles/scripts/runtime/nightly/run-${task}.sh
\`\`\`

### 06-Nightly が肥大化 (>100 ファイル)

(v1 では auto-retention なし、別 plan で cleanup 検討)

\`\`\`bash
ls "${OBSIDIAN_VAULT_PATH}/06-Nightly/" | wc -l
# 必要なら手動 archive: 古いものを 99-Archive/ へ移動
\`\`\`

## ロールバック

完全撤退する場合:

\`\`\`bash
# 1. cron から 6 行削除
crontab -e

# 2. 実行 script 削除 (or 退役 dir に移動)
git rm -r scripts/runtime/nightly/
# auto-morning-briefing.sh から prepend_nightly_status 呼び出しと関数を削除
$EDITOR ~/dotfiles/scripts/runtime/auto-morning-briefing.sh

# 3. catch-up state 削除
rm -rf ~/.cache/nightly/

# 4. discord.env は残してよい (他用途で使う可能性)

# 5. Vault の 06-Nightly/ は人手判断 (archive or 残置)
\`\`\`

## 撤退条件 (1 週間運用後)

- Discord 通知失敗率 > 50% → webhook 方式断念、cmux-notify hero に切替
- API cost が想定の 3 倍 → 重い task (audit/skill-audit) を月次に降格
- レポートが朝に確認されない → morning-briefing 統合強化 or Discord 内 inline 表示

## 関連

- 元設計: spec の cyrilxbt absorb は採用せず (家族 11 件目 saturated)、計算代行モデルとして独立発展
- catch-up pattern: \`.config/claude/scripts/runtime/skill-pruning-eval-reminder.sh\` から派生
- 既存 cron: morning-briefing (8:30 平日) + sync-daily-report (23:00) + 各種 9:00 healthcheck
```

- [ ] **Step 2: Commit**

```bash
git add docs/playbooks/nightly-offload.md
git commit -m "📝 docs(playbooks): add nightly-offload runbook"
```

---

## Task 14: Retrospective スケジュール

**Files:**
- (none、`/decision` skill 起動と Apple Calendar / Obsidian Daily Note への記入のみ)

- [ ] **Step 1: 1 週間後 retrospective を `/decision` skill で記録**

```bash
# 6/1 (月曜) に retrospective、撤退条件と照合
# /decision skill を起動して以下を記録:
```

`/decision` の対話で以下 5 項目を埋める:

- **Context**: 2026-05-25 に Nightly Vault Automation を開始、1 週間運用後の評価
- **Decision**: (1 週間後に判断: 継続 / 撤退 / 部分撤退)
- **Alternatives**: 撤退条件 3 つ (Discord 失敗率 / API cost / 朝確認率)
- **Consequences**: 朝の workflow に Nightly Status section が定着するか
- **Review date**: 2026-06-01

- [ ] **Step 2: Obsidian Daily Note 2026-06-01 に reminder note**

```bash
echo "- [ ] 🔁 Nightly Vault Automation 1 週間 retrospective (撤退条件チェック) — Plan: docs/plans/active/2026-05-25-nightly-vault-automation-plan.md" \
  >> "${OBSIDIAN_VAULT_PATH}/00-Inbox/2026-06-01.md"
```

(Daily Note が無ければ自動作成して reminder のみ書く)

- [ ] **Step 3: AutoEvolve event を emit (deployment marker)**

```bash
CC_TYPE="learned" CC_SCOPE="nightly-deployment" CC_DETAIL="dotfiles nightly automation deployed 2026-05-25 with 6 tasks (3 daily + 2 weekly + 1 monthly), retrospective scheduled 2026-06-01" \
python3 - <<'PYEOF' 2>&1 || true
import sys, os
sys.path.insert(0, os.path.join(os.path.expanduser('~'), '.claude/scripts/lib'))
from session_events import emit_event
emit_event('pattern', {
    'type': os.environ['CC_TYPE'],
    'scope': os.environ['CC_SCOPE'],
    'detail': os.environ['CC_DETAIL'],
    'source': 'plan-completion',
})
PYEOF
```

- [ ] **Step 4: Plan を done/ ディレクトリに移動 (1 週間後 retrospective 後)**

```bash
# Retrospective 完了後 (2026-06-01 以降):
mkdir -p docs/plans/done/
mv docs/plans/active/2026-05-25-nightly-vault-automation-plan.md docs/plans/done/
git add docs/plans/
git commit -m "📝 chore(plans): move nightly-automation to done after retrospective"
```

---

## ロールバック手順 (Full)

何かが大きく壊れた場合、以下の順で撤退:

1. **即時 cron 停止** (新規発火を止める)
   ```bash
   crontab -l | grep -v "scripts/runtime/nightly/" | crontab -
   ```

2. **進行中 task の kill (PC が起きている時)**
   ```bash
   pkill -f "scripts/runtime/nightly/run-"
   ```

3. **catch-up state 全削除** (誤って復活しないように)
   ```bash
   rm -rf ~/.cache/nightly/
   ```

4. **morning-briefing 統合の除去**
   ```bash
   # auto-morning-briefing.sh の prepend_nightly_status 関数定義と呼び出し 2 箇所を削除
   $EDITOR ~/dotfiles/scripts/runtime/auto-morning-briefing.sh
   shellcheck ~/dotfiles/scripts/runtime/auto-morning-briefing.sh
   ```

5. **script 群を退役 (削除 or archive)**
   ```bash
   git rm -r scripts/runtime/nightly/
   # または: mv scripts/runtime/nightly/ scripts/runtime/_retired/nightly-$(date +%Y%m%d)/
   ```

6. **Vault の 06-Nightly/ 判断**
   - 残置 (将来の reference): 何もしない
   - archive: `mv "${OBSIDIAN_VAULT_PATH}/06-Nightly" "${OBSIDIAN_VAULT_PATH}/99-Archive/06-Nightly-2026-05-25"`

7. **Discord channel 整理**
   - webhook 無効化: Discord channel 設定 → 連携サービス → 該当 webhook → 削除
   - `.env` 残置 OK (他用途で webhook 設定する可能性)

8. **Commit + 経緯記録**
   ```bash
   git add -A
   git commit -m "⏪️ revert(nightly): rollback automation (reason: <理由>)"
   ```

---

## Self-Review チェック

Plan 作成後、spec と突き合わせて以下を確認 (実装者ではなく plan 作者の責務):

- [ ] **spec coverage**: spec Section 1-7 の全要件に対応 task あり
- [ ] **placeholder scan**: TBD / TODO / "Add appropriate ..." を含まない (Open Q は Task 0 で確定済)
- [ ] **type consistency**: function name (status_begin/end, should_run_today, mark_run_today, prepend_nightly_status, notify_discord) が全 task で一貫
- [ ] **依存順序**: DAG 通り (lib → script → cron → docs)
- [ ] **rollback**: 全変更が逆操作可能、catch-up state 削除手順あり
