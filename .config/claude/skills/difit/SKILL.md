---
name: difit
description: >
  GitHub風のブラウザベース diff ビューアを起動する。構文ハイライト付きで変更を視覚的にレビュー。
  コメント機能で気になる箇所をマークし、AI プロンプトとしてコピー可能。
  Triggers: 'diff 見せて', 'diff viewer', '変更を見たい', 'difit', 'レビュー画面',
  'PR見たい', '差分確認', 'コメント処理して', 'difit コメント', 'レビューコメント反映'.
  Do NOT use for: エージェントによるコードレビュー (use /review).
allowed-tools: Bash
user-invocable: true
metadata:
  pattern: single-shot
---

# /difit — GitHub-Style Diff Viewer

ブラウザで GitHub の "Files changed" 風の diff ビューアを開く。
Prism.js による構文ハイライト、行コメント→AIプロンプトコピー機能付き。

## Usage

引数に応じてモードを切り替える:

```
/difit              → working directory の全変更 (npx difit .)
/difit staged       → ステージング済みの変更のみ
/difit main..HEAD   → ブランチ比較
/difit --pr <url>   → GitHub PR をローカルでレビュー
```

## Execution

1. 引数をパースする（デフォルトは `.`）

2. cmux 環境を検出し、起動方法を分岐する:

### cmux 環境の場合（`CMUX_WORKSPACE_ID` が設定済み）

```bash
# バックグラウンドで difit を起動（ブラウザ自動オープンを抑制、untracked 対話回避）
npx -y difit {args} --no-open --port 13579 --include-untracked 2>&1 &
DIFIT_PID=$!
sleep 3

# cmux ブラウザペインで開く
/Applications/cmux.app/Contents/Resources/bin/cmux new-pane --type browser --direction right --url "http://localhost:13579"
```

ユーザーに伝える:

> difit を cmux ブラウザペインで開きました。
> - ファイルツリーから変更ファイルを選択
> - 行をクリックしてコメントを追加可能
> - コメントは「Copy as AI prompt」でクリップボードにコピーし、ここに貼り付けて修正指示できます
> - 終了時は difit プロセスを停止してください（PID: $DIFIT_PID）

### cmux 外の場合

```bash
npx -y difit {args}
```

`-y` で確認プロンプトをスキップする。引数がなければ `.` を渡す。

ユーザーに伝える:

> difit を起動しました。ブラウザで diff ビューアが開きます。
> - ファイルツリーから変更ファイルを選択
> - 行をクリックしてコメントを追加可能
> - コメントは「Copy as AI prompt」でクリップボードにコピーし、ここに貼り付けて修正指示できます
> - 終了は Ctrl+C

## Comment Processing

ユーザーが「コメント処理して」「difit コメント」等と言ったら、実行中の difit からコメントを取得して修正を実行する。

1. difit が起動中か確認し、コメントを取得する:

```bash
curl -s http://localhost:13579/api/comments-output
```

2. 出力が空なら「コメントがありません」と伝えて終了。

3. コメントがあれば、各コメントを解析する（フォーマット: `ファイルパス:L行番号` + コメント本文）。

4. コメントの内容に従ってコードを修正する。各コメントについて:
   - 該当ファイル・行を Read で確認
   - コメントの指示に従って Edit で修正
   - 修正内容を簡潔に報告

5. 全コメントの処理後、サマリを表示する。

## Tips

- cmux 利用時（`CMUX_WORKSPACE_ID` 設定済み）は `--no-open` + `cmux new-pane --type browser` で cmux 内ブラウザに自動表示される
- `/review` と併用すると効果的: `/review` の Step 4.5 でレビュー指摘が `--comment` 付きで difit に自動出力される
- 手動で `/difit` を実行した場合はコメントなしの素のビューアーが起動する
