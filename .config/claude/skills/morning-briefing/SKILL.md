---
name: morning-briefing
description: "朝の運営全体像を 1 ファイルにまとめる。前日 17:00 以降の friction events / オープン PR・Issue / 停滞中の plan / 昨日の日報 を統合し、URGENT・今日の焦点・昨日振り返り を出力。Discord (MORNING_WEBHOOK_URL) にも通知。Triggers: '朝のブリーフィング', 'morning-briefing', '/morning', '朝の運営', 'briefing', '今日何やる', '朝の状況'. Do NOT use for: 日報生成 (use /daily-report)、週次レビュー (use /timekeeper review)、Issue 修正 (use /fix-issue)."
origin: self
user-invocable: true
metadata:
  pattern: generator
  chain:
    upstream: ["/daily-report (前日の日報)"]
    downstream: ["/timekeeper plan (朝の計画への接続)"]
---

# Morning Briefing Generator

朝起きた時点で「URGENT は何か」「今日の焦点」「昨日の振り返り」が 1 画面に出来上がっている状態を作る。
記事「Claude Code Skills で寝てる間に仕事を回す方法」の morning-briefing 相当の個人開発者版。

## 引数の解釈

- 引数なし → 今日の日付
- `yesterday` → 昨日の日付 (テスト/回顧用)
- `YYYY-MM-DD` → その日付

## 処理手順

以下の手順を **必ず順番に** 実行すること。

### Step 1: 対象日付の決定

引数を解釈し、対象日付を `YYYY-MM-DD` 形式で確定する。
macOS BSD date 例: `date -j -v-1d -f "%Y-%m-%d" "$TODAY" "+%Y-%m-%d"`

### Step 2: 入力収集 (collect-morning-inputs.sh)

```bash
sh ~/dotfiles/.config/claude/skills/morning-briefing/scripts/collect-morning-inputs.sh "$TARGET_DATE"
```

出力 JSON のフィールド:
- `today` / `yesterday`
- `friction_since_yesterday_17`: 昨日 17:00 以降の friction events (UTC 比較)
- `open_prs`: `gh pr list --search "involves:@me state:open"` の結果
- `open_issues`: `gh issue list --assignee=@me --state=open` の結果
- `stale_plans_over_7d`: `~/dotfiles/docs/plans/active/*.md` で mtime 7 日以上前
- `yesterday_report_path`: `~/daily-reports/YYYY-MM-DD.md` の存在パス (なければ null)

### Step 3: URGENT 抽出

以下を URGENT として拾う。**該当なしの場合はセクションごと「なし」と書く** (フェイク URGENT を作らない)。
**最大 3 件まで** (警告疲労を避ける。それ以上は📌セクションに集約)。

1. `open_prs` で `statusCheckRollup` に `FAILURE` / `ERROR` を含むもの (上限なし、全て上げる)
2. `friction_since_yesterday_17` で `severity == "critical"` または `friction_class` が `blocker` 系 (上限なし)
3. `stale_plans_over_7d` で **28 日以上経過 + 同一トピックで 3 件以上集中** したケースのみ URGENT に上げる
   - 28 日 = 「ほぼ 1 ヶ月放置」= 記憶減衰で再開コスト極大
   - トピック集中 (例: `nix-migration` で 6 件) は 1 件に集約して URGENT (個別列挙しない)

それ以外の 7-27 日 stale plan は📌セクションでカウントのみ表示。

### Step 4: 今日の 1 つの焦点

以下の優先順位で 1 つだけ選ぶ:

1. URGENT があれば、その解消が焦点
2. URGENT なしなら、昨日の `daily-report` の「主な成果」未完了部分
3. それもなければ、`stale_plans_over_7d` で最も古い plan の再開

**重要**: 焦点は **1 個だけ**。複数挙げない。記事の "Today's One Thing" は字義通り 1 つ。

### Step 5: 昨日振り返り (3 行要約)

`yesterday_report_path` が存在すれば、その内容を 3 行に圧縮して出力。
- 1 行目: プロジェクト数 / セッション数 / 主な成果
- 2 行目: 詰まり (エラー・品質指摘・パターン) の有無
- 3 行目: 今日に繰り越すべき事項

`yesterday_report_path` が null の場合は「昨日の日報未生成」と書く (推測で埋めない)。

### Step 6: ファイル保存

`~/daily-reports/morning/YYYY-MM-DD.md` に保存する。

```bash
mkdir -p ~/daily-reports/morning
```

`templates/briefing.md` の placeholder を埋めて Write ツールで書き出す。
**上書き確認**: 同名ファイルが既に存在する場合は、ユーザーに上書きしてよいか確認する。

### Step 7: Discord 通知

別 webhook (`MORNING_WEBHOOK_URL`) で通知する。nightly と同じ `notify-discord.sh` を使う。

```bash
# . (POSIX dot) で source。notify-discord.sh 自体は bash 前提なので bash で実行すること。
. "$HOME/dotfiles/scripts/runtime/nightly/lib/notify-discord.sh"

REPORT="$HOME/daily-reports/morning/${TARGET_DATE}.md"

# briefing 本文の冒頭部 (URGENT + 今日の焦点 + 昨日振り返り) を抽出
DETAIL=$(sed -n '/^## 🔥/,/^## 📌/p' "$REPORT" | head -40)

# MORNING_WEBHOOK_URL を一時的に DISCORD_WEBHOOK_URL として注入
DISCORD_WEBHOOK_URL="${MORNING_WEBHOOK_URL:-}" notify_discord \
    "ok" \
    "morning-briefing" \
    "0" \
    "$REPORT" \
    "" \
    "$DETAIL"
```

**Fail Fast**: `MORNING_WEBHOOK_URL` が未設定なら stderr に WARN を出して skip (`notify-discord.sh` の既存挙動と同じ)。`task` は失敗扱いにしない。

## Templates

- `templates/briefing.md` — 出力テンプレート (placeholder: `{{DATE}}`, `{{URGENT_SECTION}}`, `{{FOCUS_SECTION}}`, `{{YESTERDAY_SECTION}}`, `{{PR_ISSUE_SECTION}}`, `{{STALE_COUNT}}`, `{{STALE_PLANS_SECTION}}`, `{{FRICTION_COUNT}}`)

## Skill Assets

- 入力収集: `scripts/collect-morning-inputs.sh` — `sh scripts/collect-morning-inputs.sh [YYYY-MM-DD]`
- テンプレート: `templates/briefing.md`

## Schedule との連携

定期実行は `~/.claude/skills/schedule` で登録する (本 skill 自体は cron を持たない)。
推奨 cron: `30 21 * * 1-5` UTC (= 平日 06:30 JST)。

```bash
claude -p '/morning-briefing'
```

## Anti-Patterns

| NG | 理由 |
|----|------|
| URGENT を毎日無理やり 1 つ捻り出す | フェイク URGENT は警報疲労を生む。なければ「なし」と書く |
| 今日の焦点を複数挙げる | 「1 つ」が記事の核。複数挙げると焦点ではなくなる |
| `yesterday_report_path: null` のときに昨日の振り返りを想像で書く | 推測で埋めると briefing 全体の信頼が落ちる |
| `stale_plans_over_7d` を全件列挙する | 14 日以上のみ URGENT、それ以外は件数のみ表示で十分 |
| Discord 通知失敗で skill を fail させる | 通知は副作用。本体 (ファイル保存) が成功すれば OK |

## Data Storage

このスキルは保存メタデータを `~/.claude/skill-data/morning-briefing/` に蓄積する。

- `~/.claude/skill-data/morning-briefing/history.jsonl` — 各実行のメタデータ (append-only)

フォーマット (1 行 1 JSON):
```json
{"date": "2026-05-27", "urgent_count": 0, "stale_plans": 19, "friction_count": 0, "yesterday_report_exists": true}
```
