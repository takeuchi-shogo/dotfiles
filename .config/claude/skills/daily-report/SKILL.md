---
name: daily-report
description: >
  1日の全プロジェクト横断セッションをまとめた日報を生成する。/daily-report で今日、/daily-report yesterday で昨日、/daily-report YYYY-MM-DD で指定日の日報を作成。
  Triggers: '日報', 'daily-report', '今日何した', 'what did I do today', '作業ログ'.
  Do NOT use for: 朝の計画（use /morning）、週次レビュー（use /weekly-review）、セッション分析（use /analyze-tacit-knowledge）。
origin: self
disable-model-invocation: true
metadata:
  pattern: generator
---

# Daily Report Generator

全プロジェクトの Claude Code セッション履歴から、1日の作業内容を日報としてまとめる。

## 引数の解釈

- 引数なし → 今日の日付
- `yesterday` → 昨日の日付
- `YYYY-MM-DD` 形式 → その日付

## 処理手順

以下の手順を **必ず順番に** 実行すること。

### Step 1: 対象日付の決定

引数を解釈し、対象日付を `YYYY-MM-DD` 形式で確定する。

### Step 2: セッション情報の収集 (jsonl 直読み式)

> **2026-05-03 改訂**: 旧版は `sessions-index.json` 依存だったが、Claude Code 本体の挙動変更で
> 3 ヶ月以上 index が更新停止する事象が発生 (確認: 2026-02-11 で停止、jsonl は 248 個に対し index entries は 22 のみ)。
> jsonl ファイルを直接 walk する設計に変更し、index に依存しない。

Bash で以下を実行し、対象日に活動のあった jsonl を全プロジェクトから収集する:

```bash
TARGET_DATE="YYYY-MM-DD"
NEXT_DATE=$(date -j -v+1d -f "%Y-%m-%d" "$TARGET_DATE" "+%Y-%m-%d")

# find -newermt で対象日 modified の jsonl を探索 (空 dir でも error なし)
while IFS= read -r jsonl; do
  proj_name=$(basename $(dirname "$jsonl"))
  session_id=$(basename "$jsonl" .jsonl)
  # 最初の user message と cwd / branch を抽出
  first_user=$(jq -r 'select(.type == "user") | (.message.content | tostring | .[0:120])' "$jsonl" 2>/dev/null | head -1)
  cwd=$(jq -r '.cwd // empty' "$jsonl" 2>/dev/null | head -1)
  git_branch=$(jq -r '.gitBranch // empty' "$jsonl" 2>/dev/null | head -1)
  msg_count=$(grep -c '"type":"user"' "$jsonl" 2>/dev/null)
  echo "{\"project\":\"$proj_name\",\"session_id\":\"$session_id\",\"cwd\":\"$cwd\",\"branch\":\"$git_branch\",\"messages\":$msg_count,\"first_user\":\"$first_user\",\"path\":\"$jsonl\"}"
done < <(find ~/.claude/projects -maxdepth 2 -name "*.jsonl" \
  -newermt "$TARGET_DATE 00:00" -not -newermt "$NEXT_DATE 00:00" 2>/dev/null)
```

**設計判断**:
- `find -newermt` は zsh の `*.jsonl` glob NOMATCH error を回避する
- `-newermt "$TARGET_DATE 00:00" -not -newermt "$NEXT_DATE 00:00"` で「対象日 00:00〜翌日 00:00」に modified された jsonl を厳密 filter
- mtime ベースなので **multi-day session も拾う** (作業した日として全て計上)

**結果の解釈**:
- `mtime` ベースの filter は「その日に活動があった session」を検出する (multi-day session も拾う)
- 結果が 0 件の場合は「対象日のセッションが見つかりませんでした」と報告して終了
- `cwd` が project の判別に最も信頼できる (project_dir 名は path encoded で読みにくい)

### Step 3: JSONL からユーザーメッセージを抽出

各セッションの JSONL ファイルから、対象日のユーザーメッセージを抽出して作業内容を把握する:

```bash
TARGET_DATE="YYYY-MM-DD"
jq -r --arg d "$TARGET_DATE" '
  select(.type == "user") |
  select(.timestamp | startswith($d)) |
  .timestamp + " | " + (.message.content | tostring | .[0:200])
' "$JSONL_PATH" | head -10
```

**制約**:
- 各セッションから最大10メッセージまで (トークン節約)
- メッセージは先頭200文字に切り詰める
- timestamp prefix で対象日のみフィルタ (multi-day session の他日メッセージを除外)

### Step 4: グルーピングと関連付け

収集した情報を以下のルールでグルーピングする:

1. **cwd** でプロジェクト単位にまとめる (Step 2 で抽出済み、cwd の最後のディレクトリ名を project name として使用)
2. 同じプロジェクト内で **branch** が同じセッションをさらにまとめる
3. first_user の内容が類似しているセッションは、ブランチが異なっていても同じ「やったこと」としてまとめて良い
4. 各グループ内で **mtime 時系列順** に並べる

**プロジェクト名の表示**: `cwd` の最後のディレクトリ名を使う（例: `/Users/foo/dev/my-app` → `my-app`）。
`cwd` が空の場合は `project` (path-encoded directory 名) を fallback として使い、`-` を `/` に置換して表示する。

### Step 4.5: AutoEvolve データの収集

対象日のセッション学習データを収集する:

```bash
TARGET_DATE="YYYY-MM-DD"
# セッションメトリクス
cat ~/.claude/agent-memory/metrics/session-metrics.jsonl 2>/dev/null | jq -r --arg date "$TARGET_DATE" 'select(.timestamp | startswith($date))'
# エラーイベント
cat ~/.claude/agent-memory/learnings/errors.jsonl 2>/dev/null | jq -r --arg date "$TARGET_DATE" 'select(.timestamp | startswith($date))'
# 品質指摘
cat ~/.claude/agent-memory/learnings/quality.jsonl 2>/dev/null | jq -r --arg date "$TARGET_DATE" 'select(.timestamp | startswith($date))'
```

データが存在しない場合は、このセクションをスキップする。

### Step 5: 日本語サマリーの生成

グルーピング結果をもとに、以下のフォーマットで日報を生成する:

```markdown
# 日報 - YYYY-MM-DD

## プロジェクト別

### <プロジェクト名>

#### <やったこと>（ブランチ: <branch>）

- セッション (HH:MM-HH:MM): やったことの要約
- セッション (HH:MM-HH:MM): やったことの要約
- 成果: 具体的な成果

### <別プロジェクト名>

...

## 今日の学び

- エラー: N 件（主なもの: ...）
- 品質指摘: N 件（主なルール: ...）
- パターン: N 件

## 今日のまとめ

- N セッション / N プロジェクト
- 主な成果: ...
- 学び: エラー N 件、品質指摘 N 件を記録
```

**「今日の学び」セクションのルール**:

- Step 4.5 で AutoEvolve データが存在する場合のみ表示する。データがない場合はセクションごと省略する
- 「今日のまとめ」の「学び」行も、データがある場合のみ含める

**ルール**:

- 時刻は JST (UTC+9) に変換して表示する
- セッション単位ではなく「やったこと」単位でまとめる
- summary と firstPrompt、そしてユーザーメッセージの内容をもとに、何をしたかを具体的に書く
- 「成果」は各グループの最終的なアウトプットを簡潔に記載する

## Templates

- `templates/daily-report-template.md` — 日報出力テンプレート

### Step 6: ファイル保存

1. `~/daily-reports/` ディレクトリが存在しなければ作成する
2. Write ツールで `~/daily-reports/YYYY-MM-DD.md` に保存する
3. 保存完了を報告する

**上書き確認**: 同名ファイルが既に存在する場合は、ユーザーに上書きして良いか確認する。

## Data Storage

このスキルは実行結果のメタデータを `~/.claude/skill-data/daily-report/` に蓄積します。
過去の実行結果を参照して差分ベースの出力を生成します。

### 保存先
- `~/.claude/skill-data/daily-report/history.jsonl` — 各実行のメタデータ (append-only)

### フォーマット (1行1JSON)
```json
{"date": "2026-03-18", "projects": ["dotfiles", "myapp"], "sessions": 5, "commits": 3, "files_changed": 12}
```

### 使い方
1. 日報生成完了後、上記フォーマットでメタデータを追記
2. 次回実行時に history.jsonl を読み、前回との差分を計算
3. 「前日比: セッション +2, コミット -1」のような差分情報を出力に含める

## Skill Assets

- セッション統計収集: `scripts/collect-session-stats.sh` — `sh scripts/collect-session-stats.sh [YYYY-MM-DD]`
- 日報テンプレート: `templates/daily-report-template.md` (既存)

## Anti-Patterns

| NG | 理由 |
|----|------|
| セッションログなしで日報を書く | 記憶頼みだと作業漏れが発生する。ログベースで生成する |
| 全プロジェクトを手動で列挙する | スクリプトで自動収集し、漏れを防ぐ |
| 翌日以降にまとめて書く | 鮮度が落ちて詳細を忘れる。当日中に生成する |
