---
name: daily-report
description: 1日の全プロジェクト横断セッションをまとめた日報を生成する。/daily-report で今日、/daily-report yesterday で昨日、/daily-report YYYY-MM-DD で指定日の日報を作成。
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

### Step 2: セッション情報の収集

Bash で以下を実行し、対象日のセッションを全プロジェクトから収集する:

```bash
TARGET_DATE="YYYY-MM-DD"
for index_file in ~/.claude/projects/*/sessions-index.json; do
  jq -r --arg date "$TARGET_DATE" '
    .entries[]
    | select(
        (.created // "" | startswith($date)) or
        (.modified // "" | startswith($date))
      )
    | {sessionId, firstPrompt, summary, messageCount, created, modified, gitBranch, projectPath, fullPath}
  ' "$index_file" 2>/dev/null
done
```

結果が0件の場合は「対象日のセッションが見つかりませんでした」と報告して終了。

### Step 3: JSONL からユーザーメッセージを抽出

各セッションの JSONL ファイルから、ユーザーメッセージを抽出して作業内容を把握する:

```bash
jq -r 'select(.type == "user") | .timestamp + " | " + (.message.content | tostring | .[0:200])' "$JSONL_PATH" | head -10
```

**制約**: 各セッションから最大10メッセージまで。トークン節約のため、メッセージは先頭200文字に切り詰める。

### Step 4: グルーピングと関連付け

収集した情報を以下のルールでグルーピングする:

1. **projectPath** でプロジェクト単位にまとめる
2. 同じプロジェクト内で **gitBranch** が同じセッションをさらにまとめる
3. summary / firstPrompt の内容が類似しているセッションは、ブランチが異なっていても同じ「やったこと」としてまとめて良い
4. 各グループ内で **時系列順** に並べる

**プロジェクト名の表示**: `projectPath` の最後のディレクトリ名を使う（例: `/Users/foo/dev/my-app` → `my-app`）

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
