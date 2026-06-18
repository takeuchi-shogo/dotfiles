# Nightly Vault Automation — 運用 Playbook

> Plan: `docs/plans/active/2026-05-25-nightly-vault-automation-plan.md`
> Spec: `docs/superpowers/specs/2026-05-25-nightly-vault-automation-design.md`

## 概要

dotfiles の品質維持系タスク 6 つを夜間 cron で自動実行し、結果を **三重出力** で受け取る:

1. **Discord webhook** — 即時通知 (✅/❌ embed + `@here` on fail)
2. **Vault `06-Nightly/`** — 構造化レポート (Markdown、Obsidian で参照)
3. **翌朝 morning-briefing** — Daily Note 冒頭に `## Nightly Status` セクション

| Task | スケジュール | 用途 |
|---|---|---|
| `golden-check` | 毎晩 23:15 (DAILY) | golden principles 違反検出 |
| `health-check` | 毎晩 23:25 (DAILY) | docs 鮮度 + コード乖離 |
| `daily-report` | 毎晩 23:35 (DAILY) | 今日の活動サマリ (sessions+Obsidian+git+friction を claude -p で要約) |
| `audit` | 月曜 23:45 (DOW=1, catch-up 6 日) | コードベース横断品質監査 |
| `skill-audit` | 木曜 23:45 (DOW=4, catch-up 6 日) | skill A/B benchmark + health |
| `dep-audit` | 月初 22:30 (DOM=1, catch-up 7 日) | 依存パッケージ脆弱性 |

各 task の Discord 通知には `embed description` に **詳細** code block が含まれる (2000 char truncate)。
- `golden-check`: 違反 top 5 F-N タイトル
- `health`: stale/to_delete/to_update + stale docs top 5
- `audit`: total + issues top 5
- `skill-audit`: dormant/conflicts findings
- `dep-audit`: manifests + vuln summary
- `daily-report`: report head (主要トピック + 取り組み)

## Setup (初回 1 回)

### 1. Discord webhook URL 取得

1. Discord でサーバ作成 (個人用なら 1 人サーバ可)
2. channel 作成 (例: `#nightly`)
3. channel 設定 (右クリック → 編集) → 連携サービス → ウェブフック
4. 新しいウェブフック → 名前を `nightly-vault`
5. "ウェブフック URL をコピー" を押す

### 2. `.env` 配置

```bash
mkdir -p ~/.config/notifications
cat > ~/.config/notifications/discord.env <<'EOF'
DISCORD_WEBHOOK_URL="<コピーした URL を貼り付け>"
EOF
chmod 600 ~/.config/notifications/discord.env
```

⚠️ chmod 600 は `notify-discord.sh` が起動時に検証する (FM-11 mitigation)。

### 3. cron 登録

`crontab -e` で以下の 6 行を追記。**先頭の env block は必須** (Codex Gate C1/Q10 反映、cron は `.zshenv` を読まない):

```cron
# Nightly Vault automation — env block (Q10)
SHELL=/bin/bash
HOME=/Users/takeuchishougo
TZ=Asia/Tokyo
PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin
OBSIDIAN_VAULT_PATH=/Users/takeuchishougo/Documents/Obsidian Vault

# Nightly tasks (内部 should_run_today gate で曜日/月初判定)
30 22 * * * /Users/takeuchishougo/dotfiles/scripts/runtime/nightly/run-dep-audit.sh          >> /tmp/nightly-dep.log 2>&1
15 23 * * * /Users/takeuchishougo/dotfiles/scripts/runtime/nightly/run-golden-check.sh       >> /tmp/nightly-golden.log 2>&1
25 23 * * * /Users/takeuchishougo/dotfiles/scripts/runtime/nightly/run-health-check.sh       >> /tmp/nightly-health.log 2>&1
35 23 * * * /Users/takeuchishougo/dotfiles/scripts/runtime/nightly/run-daily-report.sh       >> /tmp/nightly-daily.log 2>&1
45 23 * * * /Users/takeuchishougo/dotfiles/scripts/runtime/nightly/run-audit.sh              >> /tmp/nightly-audit.log 2>&1
45 23 * * * /Users/takeuchishougo/dotfiles/scripts/runtime/nightly/run-skill-audit.sh        >> /tmp/nightly-skill.log 2>&1
```

⚠️ 23:45 に audit + skill-audit が同時起動するが、`acquire_claude_lock` (atomic `mkdir`) で順次実行される (FM-7 / Q12 反映)。

### 4. smoke test

```bash
FORCE_RUN=1 ~/dotfiles/scripts/runtime/nightly/run-golden-check.sh
```

確認:
- Discord channel に "✅ nightly: golden-check (Ns)" 通知が届く
- `${OBSIDIAN_VAULT_PATH}/06-Nightly/$(date +%Y-%m-%d)-golden.md` が生成
- `~/.cache/nightly/status-$(date +%Y-%m-%d).jsonl` に行追加

## 運用フロー (日次)

1. 朝 8:30 (平日) に morning-briefing が起動
2. Daily Note (`${VAULT}/07-Daily/${DATE}.md`) の **冒頭** に `## Nightly Status (YESTERDAY)` セクションが追加される
3. ❌ がある場合は Discord も赤通知 (@here mention) — `${VAULT}/06-Nightly/${YESTERDAY}-{task}.md` を確認
4. 週次 audit (月曜) / skill-audit (木曜) / 月次 dep-audit (月初) の重い report は週末にまとめて review

## トラブルシュート

### Discord 通知が届かない

- `~/.config/notifications/discord.env` の URL を確認 (chmod 600)
- webhook URL を Discord で再発行
- 手動 test:
  ```bash
  source ~/dotfiles/scripts/runtime/nightly/lib/notify-discord.sh
  notify_discord ok smoke-test 0 "06-Nightly/smoke.md" "test=1"
  ```

### cron が起動した形跡がない

- PC スリープを疑う: `pmset -g log | grep -i sleep | tail`
- 翌晩の catch-up 待ち (週次 6 日 / 月次 7 日窓内)
- env block が crontab 上部にあるか確認 (`crontab -l | head -10`)

### claude lock timeout

23:45 同時起動の片方が hang した場合、もう片方は最大 5 分待って fail status を記録する。
手動 release:
```bash
rmdir ~/.cache/nightly/.lock-claude-p
```

### catch-up を強制 reset (人手 retry)

```bash
rm ~/.cache/nightly/last-run-${task}.txt
FORCE_RUN=1 ~/dotfiles/scripts/runtime/nightly/run-${task}.sh
```

⚠️ Q9 (Codex C6) 反映: **fail でも `mark_run_today` する** ため、catch-up window 内の毎晩再試行は発生しない。retry したい場合は明示的に上記コマンドを実行する。

### morning-briefing に Nightly Status が出ない

- 前日 JSONL の存在確認: `ls ~/.cache/nightly/status-$(date -v-1d +%Y-%m-%d).jsonl`
- jq parse エラーは silent fallback (briefing は素通し、ログに WARN)

### 06-Nightly が肥大化 (>100 ファイル)

(v1 では auto-retention なし、別 plan で cleanup 検討)
```bash
ls "${OBSIDIAN_VAULT_PATH}/06-Nightly/" | wc -l
# 必要なら手動 archive: 古いものを 99-Archive/ へ移動
```

## ロールバック (Full)

```bash
# 1. cron から行削除
crontab -l | grep -v "scripts/runtime/nightly/" | crontab -

# 2. 進行中 task の kill (PC が起きている時)
pkill -f "scripts/runtime/nightly/run-"

# 3. catch-up state 全削除
rm -rf ~/.cache/nightly/

# 4. morning-briefing 統合の除去
$EDITOR ~/dotfiles/.config/claude/scripts/runtime/auto-morning-briefing.sh
# prepend_nightly_status 関数定義と呼び出しを削除

# 5. script 群を退役
git rm -r scripts/runtime/nightly/
# または: mv scripts/runtime/nightly/ scripts/runtime/_retired/nightly-$(date +%Y%m%d)/

# 6. Vault の 06-Nightly/ は人手判断 (archive or 残置)

# 7. Discord channel 整理
# webhook 無効化: Discord channel 設定 → 連携サービス → 該当 webhook → 削除
# .env 残置 OK (他用途で webhook 設定する可能性)
```

## 撤退条件 (1 週間運用後)

- Discord 通知失敗率 > 50% → webhook 方式断念、cmux-notify hero に切替
- API cost が想定の 3 倍 → 重い task (audit/skill-audit) を月次に降格
- レポートが朝に確認されない → morning-briefing 統合強化 or Discord 内 inline 表示

## 既知の制約 / v2 候補

- 06-Nightly retention は無制限 (warning 条件のみ追加候補)
- `@here` 連続失敗時の throttle (連続失敗 daily digest 化)
- friction-events schema は `.friction_class` 主キー + `.type` fallback (Codex C5 反映)
- dep-audit scope は `find -maxdepth 3` で動的検出 (`tools/claude-hooks/Cargo.toml` + `tools/otel-session-analyzer/go.mod` カバー、Codex C2 反映)

## 関連

- **canonical morning-briefing**: `.config/claude/scripts/runtime/auto-morning-briefing.sh` (root の同名 file は scratch copy)
- **catch-up pattern**: `.config/claude/scripts/runtime/skill-pruning-eval-reminder.sh` から派生
- **status JSONL 正本**: `~/.cache/nightly/status-${DATE}.jsonl` (Q8 / Codex C3 反映、`/tmp` は廃止)
- **既存 cron**: morning-briefing (8:30 平日) + sync-daily-report (23:00) + 各種 9:00 healthcheck
