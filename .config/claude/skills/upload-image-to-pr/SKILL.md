---
name: upload-image-to-pr
description: >
  画像を GitHub PR に埋め込む。Playwright MCP または gh CLI でコメント経由アップロードし、永続 URL を PR 本文に挿入。
  Triggers: 'PR に画像', '画像アップロード', 'スクショを PR に', 'embed image in PR', 'PR image'.
  Do NOT use for: 画像生成（use /nano-banana）、スクリーンショット取得のみ（use Playwright MCP directly）。
allowed-tools: Bash, Read, Write, Edit
user-invocable: true
disable-model-invocation: true
metadata:
  pattern: tool-wrapper
---

# /upload-image-to-pr — PR に画像を埋め込む

スクリーンショットや生成画像を GitHub PR の説明文に埋め込む。

## Workflow

```
1. 画像ファイルの準備（パス確認）
2. GitHub にアップロード（コメント経由で永続 URL 取得）
3. PR 本文に画像マークダウンを挿入
```

## Method 1: gh CLI（推奨）

`gh` コマンドで Issue/PR コメントに画像を添付し、URL を取得する。

### 手順

```bash
# 1. 現在の PR 番号を取得
PR_NUM=$(gh pr view --json number -q .number)

# 2. 画像をコメントとして投稿（GitHub が自動的に永続 URL を発行）
gh pr comment $PR_NUM --body "![screenshot]($(cat image.png | base64))"

# 3. 別手法: GitHub API で直接アップロード
# コメント本文に画像をドラッグ&ドロップした際の動作を再現
```

### 代替: Playwright MCP 経由

Playwright MCP が利用可能な場合、ブラウザ操作で画像をアップロードできる:

1. `browser_navigate` で PR ページを開く
2. コメント欄のファイルアップロードエリアを特定
3. `browser_file_upload` で画像をアップロード
4. GitHub が発行する `https://github.com/user-attachments/assets/...` URL を取得
5. コメントを投稿せずに URL だけ使用

```
# Playwright MCP 使用例
1. browser_navigate → https://github.com/{owner}/{repo}/pull/{num}
2. browser_click → コメント入力欄
3. browser_file_upload → 画像ファイルを選択
4. Wait for URL → user-attachments URL を抽出
5. browser_snapshot → アップロード結果確認
```

## Method 2: PR 本文への挿入

取得した画像 URL を PR 本文に埋め込む:

```bash
# 既存の PR 本文を取得
BODY=$(gh pr view $PR_NUM --json body -q .body)

# 画像セクションを追加
NEW_BODY="$BODY

## Screenshots

![Before](https://github.com/user-attachments/assets/xxx)
![After](https://github.com/user-attachments/assets/yyy)
"

# PR 本文を更新
gh pr edit $PR_NUM --body "$NEW_BODY"
```

## Usage

```
/upload-image-to-pr path/to/screenshot.png     # 指定画像をPRに埋め込み
/upload-image-to-pr                             # 画像パスを聞く
```

## Use Cases

| ケース | 説明 |
|--------|------|
| UI 変更の Before/After | デザインレビュー品質向上 |
| エラー再現スクリーンショット | バグ修正 PR の根拠 |
| nano-banana 生成画像 | アーキテクチャ図やフロー図 |
| テスト結果のスクリーンショット | CI 結果の可視化 |

## Chaining

- **`/nano-banana`**: 画像生成 → PR 埋め込み
- **`/pull-request`**: PR 作成時に画像を含める

## Limitations

- GitHub の画像アップロードはブラウザ経由の仕組みに依存
- Playwright MCP がない場合、手動で画像 URL を取得する必要がある場合あり
- 大きな画像（10MB超）はアップロードに失敗する可能性
