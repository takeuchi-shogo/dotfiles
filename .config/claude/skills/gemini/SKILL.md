---
name: gemini
description: >
  Antigravity CLI (`agy`) を使った大規模分析・リサーチ・マルチモーダル処理。
  個人向け Gemini CLI は sunset 済み。コードベース全体分析、外部リサーチ、
  PDF/動画/音声の読み取りに使用。設計/推論には codex スキルを使うこと。
  Triggers: 'gemini', 'agy', 'Gemini で', '1M コンテキスト', '大規模分析', 'PDF読んで', '動画分析', 'Google検索'.
  Do NOT use for: Claude の 200K に収まるタスク、単純な web 検索。
origin: self
metadata:
  pattern: tool-wrapper
---

# Gemini / Antigravity Skill Guide

個人アカウントの Gemini CLI (`gemini`) は 2026-06-18 に sunset。実行バイナリは `agy`。

## Running a Task

1. デフォルトで非対話モード (`-p`) を使用する
2. 用途に応じて mode を選択:
   - `plan` (default): read-only 分析
   - ファイル操作が必要な場合はユーザー確認後に `--dangerously-skip-permissions`
3. コマンドを組み立てて実行する

### Quick Reference

| Use case         | Mode   | Command                                                    |
| ---------------- | ------ | ---------------------------------------------------------- |
| コードベース分析 | `plan` | `agy --mode plan -p "Analyze: {prompt}" 2>/dev/null`       |
| 外部リサーチ     | `plan` | `agy --mode plan -p "Research: {topic}" 2>/dev/null`       |
| マルチモーダル   | `plan` | `agy --mode plan -p "Read this file: {path}" 2>/dev/null`  |
| セッション再開   | inherited | `agy --continue -p "{prompt}" 2>/dev/null`              |

### 出力が大きい場合

結果を `.claude/docs/research/` に保存する:

```bash
agy --mode plan -p "..." 2>/dev/null > .claude/docs/research/{topic}.md
```

## When to Use

- **使う**: コードベース全体分析、外部リサーチ、PDF/動画/音声/画像の読み取り、ライブラリ比較調査
- **使わない**: 設計判断（→Codex）、デバッグ（→Codex）、コード実装（→Claude 直接）、単純なファイル読み取り（→Read ツール）

## Language Protocol

`agy` への指示は英語で行い、結果をユーザーの言語（日本語）で報告する。

## Error Handling

- `agy --version` が失敗したら Antigravity CLI 未インストールを報告
- 出力が空の場合はプロンプトを見直して再試行
- タイムアウト（2分超）の場合はプロンプトを分割する

## Gotchas

- **出力サイズ爆発**: 巨大コンテキストに大量ファイルを投入すると、出力も肥大化する。要約指示で制御
- **mode 混同**: `plan` は変更提案のみ。`--dangerously-skip-permissions` は確認後のみ
- **grounding hallucination**: 検索 grounding でも最新情報は不正確な場合がある。重要な事実は別ソースで裏取り
- **バイナリ/画像の読み取り**: マルチモーダル入力はファイルサイズ制限あり。大きな PDF は分割してページ指定
- **言語プロトコル**: 指示は英語で渡す。日本語指示だと推論品質が落ちる場合がある

## Skill Assets

- コンテキスト準備ガイド: `references/context-preparation.md`
- コンテキスト生成スクリプト: `scripts/prepare-context.sh`

## Anti-Patterns

| NG | 理由 |
|----|------|
| 200K 以内のタスクに `agy` を使う | Claude 単体で十分。巨大コンテキストが必要な場合のみ |
| 設計判断を任せる | 楽観バイアスがある。設計/推論は Codex を使う |
| コンテキスト準備なしで投げる | 巨大入力は精度低下。prepare-context.sh で関連部分を抽出する |
