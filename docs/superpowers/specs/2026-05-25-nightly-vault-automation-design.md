---
title: Nightly Vault Automation — 計算代行型夜間オフロード
date: 2026-05-25
status: design-approved
author: opus-4-7 (brainstormed)
parent_context: |
  /absorb 2026-05-25 (cyrilxbt rehash, SATURATED-pure-rehash, skip 確定後の
  user actionable separation) → brainstorming で計算代行モデルに収斂
size_estimate: L (新規 8 ファイル + 既存 1 ファイル編集 + cron 6 行追加 + ドキュメント 1)
implementation_skill: superpowers:writing-plans → /rpi
---

## 1. Why (動機)

### 1.1 Problem

「やった方がいいのは分かっているが、日中に走らせると時間を取られて回せていない」品質維持系タスクが存在する:

- `/audit` (コードベース横断品質監査): 5-15min、claude -p 大量
- `dependency-auditor` (脆弱性 + outdated + abandoned): 3-8min、外部 CLI 呼び出し
- `skill-audit` (A/B benchmark + health audit): 5-10min、複数 skill 並列走行
- `/check-health` (docs 鮮度 + コード乖離): 1-3min、Read 多発
- `golden-check` (golden principles 違反): <1min
- `friction-events.jsonl` 集計 (前日活動メトリクス): <1min

日中はユーザーが foreground 作業をしているため、これらの heavyweight 処理を回す心理的・時間的余裕がない。結果として「やってないわけではないが、頻度が不安定」状態。

### 1.2 Goal

**「寝てる間に Vault が賢くなる」を計算代行モデルで実現する。**

具体的には:
- 上記 6 タスクを夜間 cron でオフロード
- 結果は Vault の専用フォルダにファイル別保存
- 完了 / 失敗を Discord Webhook で即時通知
- 翌朝 morning-briefing (8:30) の先頭で「昨夜の Nightly Status」を 5 行サマリ

### 1.3 Non-Goals (Out of Scope)

- **記事 (cyrilxbt) の Daily Brief / Weekly Synthesis 機能の取り込み**: 既に 2026-05-08 absorb で検証済、本 spec は別主題 (思考アシストではなく計算代行)
- **他 project の audit**: dotfiles 単体に絞る (拡張は将来別 spec で)
- **launchd / GitHub Actions オフロード**: cron + catch-up window で代替 (既存 dotfiles パターンと一貫性優先)
- **Discord Bot (双方向 ack 等)**: webhook URL の単方向通知のみ
- **Vault 横断の AI 合成 (CONNECTIONS / PATTERN 抽出)**: 思考アシスト系、本 spec の責務外
- **Inbox 自動分類 (capture pipeline)**: 整理代行系、本 spec の責務外

## 2. Architecture

### 2.1 ディレクトリ構成

```
scripts/runtime/nightly/                          # 新規
├── lib/
│   ├── notify-discord.sh                         # webhook curl, severity 別装飾
│   └── nightly-status.sh                         # JSONL 追記 + Vault 保存 + Discord 呼び出し
├── run-golden-check.sh                           # 毎晩 23:15
├── run-friction-aggregate.sh                     # 毎晩 23:20
├── run-health-check.sh                           # 毎晩 23:25
├── run-audit.sh                                  # 月曜 23:45
├── run-skill-audit.sh                            # 木曜 23:45
└── run-dep-audit.sh                              # 月初 1 日 0:00

既存ファイル変更:
└── scripts/runtime/auto-morning-briefing.sh      # 10 行追加 (Nightly Status を briefing 先頭に)

新規設定ファイル:
└── .config/notifications/discord.env             # DISCORD_WEBHOOK_URL (.gitignore 追加、chmod 600)

新規 Vault フォルダ:
└── ${OBSIDIAN_VAULT_PATH}/06-Nightly/            # task 別レポート保存先 (.gitkeep)

新規ドキュメント:
└── docs/playbooks/nightly-offload.md             # 運用手順 + Discord webhook 取得手順
```

**設計原則:**
- **Approach A (フラット + 共有 lib)**: 各 task は独立した `run-*.sh`、cron で個別起動。failure isolation。
- **lib 経由の共通処理**: Discord 通知、JSONL 集計、Vault 保存、catch-up gate は lib に集約。各 run-script は 30 行程度に収まる。
- **Build to Delete**: 個別 task script を削除しても他に影響なし。cron 行を 1 行消すだけで task 退役可能。

### 2.2 Task lineup

**cron は全 task が毎晩起動、曜日 / 日付の絞り込みは各スクリプト内の `should_run_today` gate で行う。** これは PC スリープによる catch-up を機能させるための設計上の決定 (詳細は Section 5.3 参照)。

| Task | 論理頻度 | cron 行 (毎晩起動) | 想定時間 | 出力 (Vault パス) | gate (script 内) |
|------|----------|--------------------|----------|-------------------|------------------|
| golden-check | 毎晩 | `15 23 * * *` | < 1min | `06-Nightly/${DATE}-golden.md` | DAILY |
| friction-aggregate | 毎晩 | `20 23 * * *` | < 1min | `06-Nightly/${DATE}-friction.md` | DAILY |
| health-check | 毎晩 | `25 23 * * *` | 1-3min | `06-Nightly/${DATE}-health.md` | DAILY |
| audit | 週 1 (月曜) | `45 23 * * *` | 5-15min | `06-Nightly/${DATE}-audit.md` | DOW=1, catch_up=6 days |
| skill-audit | 週 1 (木曜) | `45 23 * * *` | 5-10min | `06-Nightly/${DATE}-skill.md` | DOW=4, catch_up=6 days |
| dep-audit | 月 1 (月初) | `0 0 * * *` | 3-8min | `06-Nightly/${DATE}-dep.md` | DOM=1, catch_up=7 days |

**配置ポイント:**
- 既存 cron `23:00 sync-daily-report` / `23:05 sync-session-insights` / `23:10 sync-tacit-knowledge` の **直後** に nightly task を並べる (一貫性 + 同期完了後に audit が走る順序)
- 軽量 3 つ (毎晩実行) は連続 5 分で終わる (23:15 → 23:25)
- 重い 2 つ (audit / skill-audit) は `45 23 * * *` で同じ枠だが、内部 gate により別々の曜日でのみ実行される
- dep-audit は `0 0 * * *` で日付境界に乗せる (月初 1 日 = ファイル名も月初日付)
- **重要**: 各 script の冒頭で `should_run_today` を呼んで gate を評価、不一致なら即 `exit 0`。gate 評価コストは <1ms なので毎晩起動しても無害

## 3. Data Flow

```
[cron 起動] → run-${task}.sh
   │
   ├─ source lib/nightly-status.sh  → status_begin "task=audit"
   ├─ 本処理 (claude -p / npm audit / 集計 etc.)
   └─ status_end "ok|fail" "duration=N" "report=path"
            │
            ▼
   /tmp/nightly-status-${DATE}.jsonl  ← 1 task 1 行 (JSONL)
            │
            ├─→ Vault/06-Nightly/${DATE}-${task}.md  (本文レポート)
            └─→ lib/notify-discord.sh                (即時通知)
                   │
                   └─→ Discord channel (webhook URL)
                          - ok:   緑 embed + report path
                          - fail: 赤 embed + @here mention + error 抜粋

翌朝 8:30:
   auto-morning-briefing.sh
      ├─ /tmp/nightly-status-${YESTERDAY}.jsonl を読む
      └─ briefing 先頭に "## Nightly Status" 5 行追加
            "✅ golden-check (45s) → [06-Nightly/...-golden.md]
             ✅ friction (10s)    → [06-Nightly/...-friction.md]
             ❌ audit (timeout)   → [06-Nightly/...-audit.md] ← 確認"
      └─ 既存 briefing 生成は変更なし
```

### 3.1 JSONL スキーマ (`/tmp/nightly-status-${DATE}.jsonl`)

1 行 1 task。task ごとに 1 度だけ append される (catch-up で複数回走った場合は最新で上書きせず追記、最新行が有効)。

```json
{
  "ts": "2026-05-25T23:15:32+09:00",
  "task": "golden-check",
  "status": "ok",
  "duration_sec": 42,
  "report": "06-Nightly/2026-05-25-golden.md",
  "metric": {"violations": 3}
}
```

**フィールド:**
- `ts`: ISO8601 with TZ (Asia/Tokyo)
- `task`: golden-check / friction-aggregate / health-check / audit / skill-audit / dep-audit
- `status`: `ok` | `fail`
- `duration_sec`: 整数
- `report`: Vault root からの相対パス
- `metric`: task 固有メトリクス (任意フィールド、failure 時は `{"error": "..."}`)

### 3.2 Discord 通知 payload

```json
{
  "embeds": [{
    "title": "✅ nightly: golden-check (45s)",
    "color": 3066993,
    "description": "報告: `06-Nightly/2026-05-25-golden.md`\nメトリクス: 違反 3 件",
    "timestamp": "2026-05-25T23:15:32+09:00"
  }]
}
```

failure 時は `"color": 15158332` (赤) + `"content": "@here"` で channel 全員通知。

## 4. Error Handling

各 `run-*.sh` の枠組み (テンプレ、共通):

```bash
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/lib/nightly-status.sh"

TASK="audit"  # task 名
trap 'status_end fail "exit_code=$?"' ERR

# 必須前提チェック (失敗時は status=fail で記録、cron は exit 0)
[[ -z "${OBSIDIAN_VAULT_PATH:-}" ]] && { status_end fail "missing OBSIDIAN_VAULT_PATH"; exit 0; }
command -v claude &>/dev/null || { status_end fail "claude CLI not found"; exit 0; }

# catch-up gate
should_run_today "$TASK" DOW 1 6 || { echo "[nightly] skip (gate)"; exit 0; }

status_begin "$TASK"

# 本処理 (timeout 必須)
REPORT_PATH="${OBSIDIAN_VAULT_PATH}/06-Nightly/${DATE}-${TASK}.md"
timeout "${TIMEOUT:-900}"s bash -c "claude -p '...' > '$REPORT_PATH'" \
  || { status_end fail "timeout or claude error"; exit 0; }

mark_run_today "$TASK"
status_end ok "duration=${SECONDS}" "report=06-Nightly/${DATE}-${TASK}.md"
```

### 4.1 原則 (CLAUDE.md core_principles 準拠)

- ❌ **silent fail 禁止** — 必ず `status_end fail` を呼ぶ。trap ERR と前提チェックで網羅
- ❌ **暗黙 fallback 禁止** — `OBSIDIAN_VAULT_PATH` 未設定は明示エラー扱い (silent skip ではなく fail で記録)
- ✅ **`exit 0` は cron MAILTO 抑止用** — failure 情報は status_jsonl + Discord に集約
- ✅ **`timeout` 必須** — claude -p の hang を防ぐ (default 900s = 15min)
- ✅ **`trap ... ERR`** — 想定外の失敗もカバー

### 4.2 失敗カテゴリと対応

| Failure | 検知方法 | 通知 | リカバリ |
|---------|----------|------|----------|
| OBSIDIAN_VAULT_PATH 未設定 | 冒頭の `[[ -z ]]` 検査 | Discord fail (赤) + jsonl fail | 環境変数設定 |
| claude CLI 不在 | `command -v claude` | 同上 | 手動 install |
| Vault フォルダ書き込み失敗 | `mkdir -p` の exit code | 同上 + 詳細 path | 権限確認 / disk full 確認 |
| claude -p timeout | `timeout` exit 124 | 同上 + 部分出力保存試行 | 翌週まで待つ (catch-up しない) |
| Discord webhook 失敗 | curl exit code | stderr WARN のみ (jsonl ok は記録) | webhook URL 再生成 |
| DISCORD_WEBHOOK_URL 未設定 | env 未定義 | stderr WARN + skip notify | `.config/notifications/discord.env` 作成 |

**Discord 通知失敗は task 失敗にしない** — 通知は副作用、task 成果物 (レポート + jsonl) が完成していれば status=ok。

## 5. Catch-up Window (PC スリープ対策)

Mac は深夜帯にスリープに入る前提。cron は flap する。既存 `skill-pruning-eval-reminder.sh` で動作実績ある「内部 date gate + N 日間 catch-up」パターンを `lib/nightly-status.sh` に共通関数化。

### 5.1 共通関数

```bash
# lib/nightly-status.sh
should_run_today() {
  local task="$1" gate_kind="$2" gate_value="$3" catch_up_days="$4"
  local last_run_file="$HOME/.cache/nightly/last-run-${task}.txt"
  mkdir -p "$(dirname "$last_run_file")"

  local last_run today
  last_run=$(cat "$last_run_file" 2>/dev/null || echo "1970-01-01")
  today=$(date +%Y-%m-%d)

  # 既に今日実行済 → skip
  [[ "$last_run" == "$today" ]] && return 1
  # FORCE_RUN=1 → 強制実行 (検証用)
  [[ "${FORCE_RUN:-0}" == "1" ]] && return 0

  case "$gate_kind" in
    DAILY)
      return 0
      ;;
    DOW)
      # 今日が gate 曜日 → 即実行
      # それ以外なら、最後の gate 曜日日付 + catch_up_days 以内に未実行なら catch-up
      local today_dow=$(date +%u)  # 1=Mon, 7=Sun
      if [[ "$today_dow" == "$gate_value" ]]; then return 0; fi
      # last gate date 計算 → catch-up 窓判定
      local days_since_gate=$(( (today_dow - gate_value + 7) % 7 ))
      local last_gate_date=$(date -v-${days_since_gate}d +%Y-%m-%d)
      if [[ "$last_run" < "$last_gate_date" ]] && [[ $days_since_gate -le $catch_up_days ]]; then
        return 0  # catch-up
      fi
      return 1
      ;;
    DOM)
      local today_dom=$(date +%-d)
      if [[ "$today_dom" == "$gate_value" ]]; then return 0; fi
      # 月初 + catch_up_days 以内に未実行なら catch-up
      local this_month_first="${today:0:7}-$(printf '%02d' "$gate_value")"
      if [[ "$last_run" < "$this_month_first" ]] && [[ $today_dom -le $((gate_value + catch_up_days)) ]]; then
        return 0
      fi
      return 1
      ;;
  esac
}

mark_run_today() {
  local task="$1"
  echo "$(date +%Y-%m-%d)" > "$HOME/.cache/nightly/last-run-${task}.txt"
}
```

### 5.2 Gate 設定

| Task | gate_kind | gate_value | catch_up_days | 意味 |
|------|-----------|------------|---------------|------|
| golden-check | DAILY | - | 0 | 今日実行できなければ翌日まとめて catch しない (毎日完結) |
| friction-aggregate | DAILY | - | 0 | 同上 |
| health-check | DAILY | - | 0 | 同上 |
| audit | DOW | 1 (月) | 6 | 月曜実行、PC スリープなら次の cron で土曜まで catch-up |
| skill-audit | DOW | 4 (木) | 6 | 木曜実行、catch-up は水曜まで |
| dep-audit | DOM | 1 (月初) | 7 | 月初実行、catch-up は 8 日まで |

### 5.3 Catch-up の発火タイミング

毎晩 23:15 から走る軽量 task は確実に gate 評価が走る (火曜 23:15 の golden-check 起動時に audit の gate を兼任評価する必要はない、各 run-*.sh は自分の gate のみ見る)。

しかし「月曜 23:45 が飛んだ → 火曜 23:45 に audit cron が走らない」問題がある (audit cron は月曜のみ)。これを解決するため、**audit / skill-audit / dep-audit の cron は毎晩 23:45 で走らせ、各スクリプト内で gate 判定する**:

```cron
# 毎晩 23:45 (週次 task 兼任、内部 gate で曜日判定)
45 23 * * * /Users/takeuchishougo/dotfiles/scripts/runtime/nightly/run-audit.sh         >> /tmp/nightly-audit.log 2>&1
45 23 * * * /Users/takeuchishougo/dotfiles/scripts/runtime/nightly/run-skill-audit.sh   >> /tmp/nightly-skill.log 2>&1

# dep-audit は月内毎晩 0:00 で同様 (gate 内で DOM 判定)
0  0  * * * /Users/takeuchishougo/dotfiles/scripts/runtime/nightly/run-dep-audit.sh     >> /tmp/nightly-dep.log 2>&1
```

これにより、月曜 PC スリープでも火曜 23:45 に audit が catch-up 発火する。gate 評価は <1ms なので毎晩走らせても無害。

cron 行の具体形は Section 2.2 を参照 (毎晩起動 + 内部 gate 方式)。

## 6. Verification (検証方法)

### 6.1 単体動作 (FORCE_RUN で即実行)

```bash
# (1) 単体実行: gate 無視
FORCE_RUN=1 ./scripts/runtime/nightly/run-golden-check.sh

# (2) status JSONL に行が増えたか
cat /tmp/nightly-status-$(date +%Y-%m-%d).jsonl
# → {"ts":"...","task":"golden-check","status":"ok",...} が 1 行

# (3) Vault に出力されたか
ls -la "$OBSIDIAN_VAULT_PATH/06-Nightly/" | tail -3
# → 2026-05-25-golden.md が存在
```

### 6.2 失敗ケース

```bash
# (4) Discord webhook 未設定 → stderr WARN + jsonl ok のまま
DISCORD_WEBHOOK_URL="" FORCE_RUN=1 ./scripts/runtime/nightly/run-golden-check.sh

# (5) VAULT 未設定 → exit 0 + jsonl fail で記録
env -u OBSIDIAN_VAULT_PATH FORCE_RUN=1 ./scripts/runtime/nightly/run-golden-check.sh
# 期待: stderr に "missing OBSIDIAN_VAULT_PATH" + jsonl status=fail
```

### 6.3 catch-up シミュレーション

```bash
# (6) 月曜 audit が飛んだ翌火曜の挙動
echo "2026-05-18" > ~/.cache/nightly/last-run-audit.txt  # 先週月曜の last_run
# → 火曜 23:45 cron で audit が catch-up 発火
./scripts/runtime/nightly/run-audit.sh
# 期待: gate 通過、実行、~/.cache/nightly/last-run-audit.txt が今日に更新

# (7) catch-up 窓外
echo "2026-05-11" > ~/.cache/nightly/last-run-audit.txt  # 14 日前の last_run
./scripts/runtime/nightly/run-audit.sh
# 期待: gate 拒否、skip (catch_up_days=6 を超過)
```

### 6.4 morning-briefing 統合

```bash
# (8) Nightly Status セクションが briefing 先頭に出るか
./scripts/runtime/auto-morning-briefing.sh
# Vault/00-Inbox/${DATE}.md を開く
# → briefing 先頭に "## Nightly Status" 5 行 (✅/❌ + Wiki link)
```

## 7. Acceptance Criteria

実装完了の判定基準:

- [ ] `scripts/runtime/nightly/` 配下に 8 ファイル (lib 2 + run-*.sh 6) が存在
- [ ] `lib/nightly-status.sh` の `should_run_today` が DAILY / DOW / DOM 全 3 mode で正しく gate 判定する (unit test 風シェルテスト)
- [ ] `lib/notify-discord.sh` が DISCORD_WEBHOOK_URL 未設定時に silent skip + stderr WARN (exit 0)、設定時に curl 成功 (response 204)
- [ ] `run-golden-check.sh` を FORCE_RUN=1 で実行すると `/tmp/nightly-status-*.jsonl` に 1 行 append + `Vault/06-Nightly/*.md` 生成 + Discord 通知到達
- [ ] OBSIDIAN_VAULT_PATH 未設定で実行すると stderr に WARN + jsonl status=fail + exit 0
- [ ] crontab に 6 task の cron 行が追加されている (catch-up 方式で毎晩起動 + 内部 gate 判定)
- [ ] `auto-morning-briefing.sh` の出力先頭に "## Nightly Status" セクションが付与される
- [ ] `.config/notifications/discord.env` が `.gitignore` 対象 (commit されない)
- [ ] `docs/playbooks/nightly-offload.md` に Discord webhook 取得手順 + 運用フロー記載
- [ ] catch-up シミュレーション (Section 6.3) で期待通り catch-up 発火 / 窓外 skip
- [ ] 1 週間連続運用後、Discord 通知が日々届き、Vault `06-Nightly/` にレポートが蓄積される

## 8. Open Questions (Plan 段階で詰める)

- **Q1**: `friction-aggregate` の集計対象は `~/.cache/agent-events/friction-events.jsonl` で正しいか? path 確認
- **Q2**: `skill-audit` は既存 `skill-audit` skill / `scripts/runtime/skill-audit-batch.sh` を呼ぶ? それとも独立実装?
- **Q3**: `dep-audit` の対象ファイル列挙: `~/dotfiles/package.json` のほか、`~/dotfiles/.config/*/package.json` も含む?
- **Q4**: `06-Nightly/` フォルダの retention policy (古いレポートの自動削除 / アーカイブ)? 初期は無制限蓄積で良いか
- **Q5**: 既存 `scripts/runtime/auto-morning-briefing.sh` の `briefing` テンプレに Nightly Status セクションをどう差し込むか (PROMPT 改変 vs post-processing で markdown 結合)
- **Q6**: `lib/nightly-status.sh` 内 `status_begin` / `status_end` の API シグネチャ (kwargs 風 vs positional)
- **Q7**: 各 run-script の `claude -p` プロンプト文 (audit / health-check / skill-audit) は新規作成 or 既存 skill から流用?

## 9. References

- 既存 cron: `crontab -l` (23:00 sync-* / 8:30 morning-briefing / 9:00 probation-30day / catch-up window pattern: `skill-pruning-eval-reminder.sh`)
- 既存 morning-briefing: `scripts/runtime/auto-morning-briefing.sh`
- 既存 daily sync: `scripts/runtime/sync-daily-report.sh` / `sync-session-insights.sh` / `sync-tacit-knowledge.sh`
- 既存類似処理: `golden-check` hook, `friction-events.jsonl` (path 要確認), `/audit` skill, `dependency-auditor` skill, `skill-audit` skill, `/check-health` skill
- 関連 absorb 分析: `docs/research/2026-05-08-cyril-obsidian-vault-absorb-analysis.md` (記事 absorb 棄却、本 spec は独立トピックとして発生)
- CLAUDE.md core_principles: 暗黙フォールバック禁止、silent failure 禁止、Build to Delete

## 10. Implementation Path

1. 本 spec を user review
2. `superpowers:writing-plans` skill で本 spec を入力に implementation plan を生成
3. plan を `docs/plans/active/2026-05-25-nightly-vault-automation-plan.md` に保存
4. 別セッションで `/rpi` または手動実装
5. 実装後、Section 6 verification を全項目クリア
6. 1 週間運用後に retrospective (`/eureka` or `/decision`)
