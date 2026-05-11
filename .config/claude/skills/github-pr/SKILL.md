---
name: github-pr
description: "GitHub PR のセルフレビュー・レビューコメント対応・マージ判断を支援する。未解決コメント検出 → 修正 → 再レビューの cycle を回す。Triggers: 'セルフレビュー', 'PR確認', 'PR チェック', 'コメント対応', 'コメント返す', 'マージしていい', 'マージ判断', 'PR review', 'merge check', 'unresolved コメント', 'レビューに返信'. Do NOT use for: PR作成（use /pull-request or /create-pr-wait）、コードレビュー（use /review）、CI修正（use /create-pr-wait）。"
origin: self
user-invocable: true
allowed-tools: Bash(*gh-unresolved-threads*), Bash(gh pr *), Bash(gh api graphql *)
metadata:
  pattern: pipeline
  chain:
    upstream: ["/pull-request (PR作成)", "/create-pr-wait (CI待機)"]
    downstream: ["/commit (修正コミット)"]
---

# GitHub PR

PR品質を繰り返しチェックし、マージ判断を行う。

## 開発フローとスキルの役割

1. 実装・push・PR作成（`/pull-request` or `/create-pr-wait`）
2. **セルフレビュー** → ready にしてレビュー依頼
3. レビュワーからコメント → **レビューコメント対応**
4. **セルフレビュー**（都度実行）
5. レビュワーから Approve
6. **セルフレビュー**（最終確認）
7. **マージ** → リリース・動作確認

太字の箇所でこのスキルを使用。

## ルール

- **レビュー後のrebase禁止**: レビュワーからコメントを受けた後はrebaseしない。コミットツリーが変わるとレビュー後の差分が追跡不能になる
- **PR description更新は確認不要**: 実装が正。実装と乖離したdescriptionの修正は常に正しいため、ユーザー確認なしで実行してよい

## ルーティング

ユーザーの意図に応じて参照先を切り替える:

- **セルフレビュー**（「セルフレビューして」「PR確認して」）→ [self-review.md](self-review.md)
- **レビューコメント対応**（「コメント対応して」「レビュー対応して」）→ [review-response.md](review-response.md)
- **マージ判断**（「マージしていい？」「マージして」）→ [merge.md](merge.md)

## 関連スキル

- `/pull-request` — PR作成
- `/create-pr-wait` — PR作成 + CI監視
- `/review` — コード変更のレビュー（コミット前）
- `github-pr`（本スキル）— PR提出後のライフサイクル管理

## Gotchas

- **rebase after review**: レビュー承認後の rebase は reviewer の approve を無効化する。rebase は review 前に完了させる
- **unresolved thread 見落とし**: `gh-unresolved-threads` スクリプトで未解決スレッドを確認してからマージ
- **concurrent reviewer changes**: 複数 reviewer が同時にコメントすると対応漏れが発生。コメント一覧を毎回取得し直す
- **draft PR の自動マージ**: draft 状態の PR に auto-merge を設定しても ready-for-review に変更されるまで発動しない
- **大規模 diff**: 500行超の diff は reviewer の負荷が高い。可能なら PR を分割

## Anti-Patterns

| NG | 理由 |
|----|------|
| レビューコメントを読まずに一括 resolve する | 指摘の意図を見落とし、同じ問題が再発する |
| CI 失敗のまま merge 判断する | CI が通っていない PR をマージすると本番障害のリスク |
| セルフレビューせずにマージ要求する | 自分の diff を見直さないと明らかな問題を見逃す |
