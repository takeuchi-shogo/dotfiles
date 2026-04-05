---
name: nano-banana
description: >
  nano-banana CLI で AI 画像生成。インフォグラフィック、PR画像、バナー、透過アセット作成に使用。Gemini 3.1 Flash ベース。
  Triggers: '画像生成', 'nano-banana', 'インフォグラフィック', 'バナー作成', 'PR画像', 'AI image', '透過アセット'.
  Do NOT use for: スクリーンショット取得（use agent-browser CLI）、PR への画像埋め込み（use /upload-image-to-pr）、UI デザイン（use /frontend-design）。
allowed-tools: Bash, Read, Write, Glob
user-invocable: true
disable-model-invocation: true
metadata:
  pattern: tool-wrapper
---

# /nano-banana — AI 画像生成

nano-banana CLI（Gemini 3.1 Flash / Gemini 3 Pro）を使って画像を生成する。

## Prerequisites

- **Bun**: `brew install bun`
- **FFmpeg**: `brew install ffmpeg`（透過モード用）
- **ImageMagick**: `brew install imagemagick`（透過モード用）
- **Gemini API Key**: [Google AI Studio](https://aistudio.google.com/) で取得 → `~/.nano-banana/.env`

## Setup（初回のみ）

```bash
git clone https://github.com/kingbootoshi/nano-banana-2-skill.git ~/tools/nano-banana-2
cd ~/tools/nano-banana-2
bun install
bun link
mkdir -p ~/.nano-banana
echo "GEMINI_API_KEY=your_key_here" > ~/.nano-banana/.env
```

## Usage

ユーザーが「画像を生成して」「バナーを作って」等と依頼したら、以下の手順で実行する。

### 1. プロンプト構築

ユーザーの要件を具体的な英語プロンプトに変換する:

- 被写体、構図、スタイルを明示
- 色調やムードを指定
- テキスト描画が必要な場合は引用符で囲む

### 2. コマンド実行

```bash
nano-banana "A modern tech blog header with abstract geometric shapes in blue and purple gradients" \
  -s 2K \
  -a 16:9 \
  -d ./output
```

### Options

| Flag | 説明 | 値 |
|------|------|-----|
| `-s` | 解像度 | `512`, `1K`(default), `2K`, `4K` |
| `-a` | アスペクト比 | `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3`, `4:5`, `5:4`, `21:9` |
| `-m` | モデル | `flash`/`nb2`(default), `pro`/`nb-pro` |
| `-r` | 参照画像 | パス（スタイル転写用、複数指定可） |
| `-t` | 透過背景 | green screen → FFmpeg colorkey → ImageMagick auto-crop |
| `-o` | 出力ファイル名 | |
| `-d` | 出力ディレクトリ | |
| `--costs` | コスト履歴表示 | `~/.nano-banana/costs.json` |

### 3. 結果確認

生成された画像パスをユーザーに報告する。必要に応じて再生成やパラメータ調整を行う。

## Use Cases

| ケース | 推奨設定 |
|--------|---------|
| PR 用スクリーンショット代替 | `-s 1K -a 16:9` |
| ブログヘッダー | `-s 2K -a 16:9` |
| SNS 投稿画像 | `-s 1K -a 1:1` |
| アイコン/ロゴ（透過） | `-s 1K -a 1:1 -t` |
| スライド挿入図 | `-s 2K -a 16:9` |
| モバイルバナー | `-s 2K -a 9:16` |

## Chaining

- **`/upload-image-to-pr`**: 生成画像を PR に埋め込み
- **`/obsidian-content`**: Obsidian ノートの挿入画像として使用

## Anti-Patterns

| NG | 理由 |
|----|------|
| 日本語プロンプトをそのまま渡す | 英語の方が生成品質が高い |
| 4K を常用する | コスト増。必要な解像度を選ぶ |
| API Key をコードに直書き | `~/.nano-banana/.env` を使う |
