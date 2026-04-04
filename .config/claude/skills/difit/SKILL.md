---
name: difit
description: >
  GitHub風のブラウザベース diff ビューアを起動する。構文ハイライト付きで変更を視覚的にレビュー。
  コメント機能で気になる箇所をマークし、AI プロンプトとしてコピー可能。
  Triggers: 'diff 見せて', 'diff viewer', '変更を見たい', 'difit', 'レビュー画面',
  'PR見たい', '差分確認'.
  Do NOT use for: エージェントによるコードレビュー (use /review).
allowed-tools: Bash
user-invocable: true
disable-model-invocation: true
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

2. difit を起動:

```bash
npx -y difit {args}
```

`-y` で確認プロンプトをスキップする。引数がなければ `.` を渡す。

3. ユーザーに伝える:

> difit を起動しました。ブラウザで diff ビューアが開きます。
> - ファイルツリーから変更ファイルを選択
> - 行をクリックしてコメントを追加可能
> - コメントは「Copy as AI prompt」でクリップボードにコピーし、ここに貼り付けて修正指示できます
> - 終了は Ctrl+C

## Tips

- cmux 利用時はブラウザペインに自動表示される
- `/review` と併用すると効果的: `/review` の Step 4.5 でレビュー指摘が `--comment` 付きで difit に自動出力される
- 手動で `/difit` を実行した場合はコメントなしの素のビューアーが起動する
