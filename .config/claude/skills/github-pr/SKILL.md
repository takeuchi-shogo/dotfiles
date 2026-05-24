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

## Size & Splitting

Google eng-practices `small-cls.md` 由来の規律。PR (CL) は "one thing" に focus し、レビュー可能なサイズに保つ。

### Threshold: 300 行

- **目安: insertions + deletions = 300 行**を超える PR は分割検討必須
- 生成コード (`.pb.go` / lockfile / `_gen.go`) は threshold 計算から除外可
- threshold は `skills/github-pr/self-review.md` および `agents/golang-reviewer.md` (#16) と統一

### PR 分割パターン

300 行超 PR を分割する 5 パターン (stacking / by-files / horizontal / vertical / grid) は `references/pr-splitting-patterns.md` 参照。

| 状況 | 推奨 pattern |
|------|------------|
| 依存関係が直列 | stacking |
| refactoring + feature 混在 | by-files |
| 全 layer で 1 機能 | horizontal |
| 1 CL = 1 layer | vertical |
| 大規模機能 (機能 × layer) | grid |

### Large CL Exception

300 行超は原則禁止だが、**emergency 認定時のみ** Large CL が許容される。
emergency 定義 (本番障害 / リリースブロッカー / harness 破損) と NOT emergency 一覧は `references/emergency-definition.md` 参照。

emergency 認定 Large CL の必須記載事項 (PR description に明記):

```
EMERGENCY: <種別 — 本番障害 / リリースブロッカー / harness 破損>
影響範囲: <ユーザー数 / システム範囲 / データ量>
follow-up: <分割計画 / 後日 cleanup CL の予定>
```

follow-up CL の **作成自体は義務**、**期限 (3 営業日以内推奨)** の詳細は `references/emergency-definition.md` §3 参照。

`EMERGENCY:` 行なし / NOT emergency 該当 / follow-up 欠落のいずれかなら、`agents/code-reviewer.md` は `[MUST]` で対応を要求する。

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
- **大規模 diff**: 300行超の diff は reviewer の負荷が高い。可能なら PR を分割 (詳細は上記 "Size & Splitting" セクション参照)

## Anti-Patterns

| NG | 理由 |
|----|------|
| レビューコメントを読まずに一括 resolve する | 指摘の意図を見落とし、同じ問題が再発する |
| CI 失敗のまま merge 判断する | CI が通っていない PR をマージすると本番障害のリスク |
| セルフレビューせずにマージ要求する | 自分の diff を見直さないと明らかな問題を見逃す |
