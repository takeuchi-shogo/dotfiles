---
name: refactor-session
description: >
  機能実装禁止の清掃専用セッション。技術的負債の解消、コード品質改善、テスト補強に集中する。progress.log で5セッション連続機能追加時に自動推奨。
  Triggers: 'リファクタ', 'refactor', '技術的負債', 'tech debt', 'コード整理', 'cleanup session'.
  Do NOT use for: 機能追加を含む作業（use /rpi or /epd）、コードレビュー（use /review）、監査（use /audit）。
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
metadata:
  pattern: executor
disable-model-invocation: true
hooks:
  PreToolUse:
    - matcher: "Write"
      hooks:
        - type: prompt
          prompt: "[Refactor Session] 新規ファイル作成が検出されました。リファクタリングセッションでは新機能の追加を避け、既存コードの改善に集中してください。本当に必要ですか？"
---

# Refactor Session

技術的負債を解消するための清掃専用セッション。

## Rules

1. **新機能の実装は禁止** — 既存コードの改善のみ
2. **対象作業**:
   - デッドコードの削除
   - 重複コードの統合（DRY）
   - 命名の改善
   - テストの補強・リファクタリング
   - ドキュメントの更新
   - lint 警告の解消
   - 依存関係の更新
3. **スコープ**: 1セッションで1モジュールまたは1カテゴリに集中

## Workflow

1. `/refactor-session` を実行してモードに入る
2. 改善対象を特定する:
   - `progress.log` から最近の変更が集中しているファイルを確認
   - lint/test の警告を確認
   - `feature_list.json` の完了済み機能周辺を重点チェック
3. 改善を実施する（新規ファイル作成は警告付き）
4. テストを実行して回帰がないことを確認
5. コミットメッセージに `refactor:` プレフィックスを使用

## Trigger

`session-load.js` が以下を検出した場合に自動推奨:
- `progress.log` の直近5エントリが全て機能追加系（feat/add/implement）

手動でも `/refactor-session` で起動可能。

## Anti-Patterns

| NG | 理由 |
|----|------|
| リファクタ中に機能を追加する | スコープが混在し、レビュー困難＆リグレッションリスク増大 |
| テストなしでリファクタする | 動作が変わっていないことを保証できない |
| 一度に大量のファイルを変更する | diff が巨大化しレビュー不能。小さな単位で進める |
