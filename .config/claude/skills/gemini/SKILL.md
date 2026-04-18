---
name: gemini
description: >
  Gemini CLI (1Mコンテキスト) を使った大規模分析・リサーチ・マルチモーダル処理。コードベース全体分析、
  外部リサーチ、PDF/動画/音声の読み取りに使用。設計/推論には codex スキルを使うこと。
  Triggers: 'gemini', 'Gemini で', '1M コンテキスト', '大規模分析', 'PDF読んで', '動画分析', 'Google検索'.
  Do NOT use for tasks that fit within Claude's 200K context or simple web searches.
origin: self
metadata:
  pattern: tool-wrapper
---

# Gemini Skill Guide

## Running a Task

1. デフォルトで非対話モード (`-p`) を使用する
2. 用途に応じて approval-mode を選択:
   - `plan` (default): read-only 分析
   - `yolo`: ファイル操作が必要な場合（ユーザー確認後のみ）
3. コマンドを組み立てて実行する

### Quick Reference

| Use case         | Approval mode | Command                                                               |
| ---------------- | ------------- | --------------------------------------------------------------------- |
| コードベース分析 | `plan`        | `gemini --approval-mode plan -p "Analyze: {prompt}" 2>/dev/null`      |
| 外部リサーチ     | `plan`        | `gemini --approval-mode plan -p "Research: {topic}" 2>/dev/null`      |
| マルチモーダル   | `plan`        | `gemini --approval-mode plan -p "Read this file: {path}" 2>/dev/null` |
| セッション再開   | inherited     | `gemini --resume latest -p "{prompt}" 2>/dev/null`                    |

### 出力が大きい場合

結果を `.claude/docs/research/` に保存する:

```bash
gemini --approval-mode plan -p "..." 2>/dev/null > .claude/docs/research/{topic}.md
```

## When to Use Gemini

- **使う**: コードベース全体分析、外部リサーチ（Google Search grounding）、PDF/動画/音声/画像の読み取り、ライブラリ比較調査
- **使わない**: 設計判断（→Codex）、デバッグ（→Codex）、コード実装（→Claude 直接）、単純なファイル読み取り（→Read ツール）

## Language Protocol

Gemini への指示は英語で行い、結果をユーザーの言語（日本語）で報告する。

## Error Handling

- `gemini --version` が失敗したら Gemini CLI 未インストールを報告
- 出力が空の場合はプロンプトを見直して再試行
- タイムアウト（2分超）の場合はプロンプトを分割する

## Gotchas

- **出力サイズ爆発**: 1Mコンテキストに大量ファイルを投入すると、出力も肥大化する。`--max-output-tokens` や要約指示で制御
- **approval mode 混同**: `plan` モードは変更提案のみ、`yolo` は即時実行。本番環境では必ず `plan` を使う
- **grounding hallucination**: Google Search grounding でも最新情報は不正確な場合がある。重要な事実は別ソースで裏取り
- **バイナリ/画像の読み取り**: マルチモーダル入力はファイルサイズ制限あり。大きな PDF は分割してページ指定
- **言語プロトコル**: Gemini への指示は英語で渡す。日本語指示だと推論品質が落ちる場合がある

## Skill Assets

- コンテキスト準備ガイド: `references/context-preparation.md`
- コンテキスト生成スクリプト: `scripts/prepare-context.sh`

## Anti-Patterns

| NG | 理由 |
|----|------|
| 200K 以内のタスクに Gemini を使う | Claude 単体で十分。Gemini は 1M コンテキストが必要な場合のみ |
| 設計判断を Gemini に任せる | Gemini は楽観バイアスがある。設計/推論は Codex を使う |
| コンテキスト準備なしで投げる | 巨大入力は精度低下。prepare-context.sh で関連部分を抽出する |
