---
name: create-pr-wait
description: "PR作成→CI監視→失敗時自動修正→再pushを自動化するワークフロー。/pull-request の拡張版で、CIが通るまで面倒を見る。"
metadata:
  pattern: pipeline
---

# /create-pr-wait — PR作成からCI通過まで自動化

PR作成、CI監視、失敗時の自動修正、再pushを一連のフローとして実行する。
CIがグリーンになるまで面倒を見るワークフロー。

## ワークフロー

```
PR作成 → CI監視(gh pr checks --watch) → PASS → 完了報告
                                       → FAIL → ログ取得(gh run view --log-failed)
                                              → 原因診断 → 修正 → 再push → CI監視
                                              → 3回失敗 → ユーザーに報告
```

**リトライ上限: 最大3回**

---

## Step 1: PR作成

リモートにpushし、PRを作成する。既にPRが存在する場合はスキップ。

```bash
# リモートにpush
git push -u origin HEAD

# PR作成（既存PRがあればスキップ）
gh pr create --fill || echo "PR already exists"

# PR URL を取得・記録
gh pr view --json url --jq '.url'
```

## Step 2: CI監視

PRのCIチェックを監視する。`--watch` で完了まで待機。

```bash
# CI結果を待機（最大15分）
gh pr checks --watch --fail-fast
```

- 全チェックがPASSすれば Step 3 へ
- いずれかがFAILすれば Step 4 へ
- タイムアウト: 最大15分

## Step 3: CI成功時

CIが全てグリーンになったらユーザーに報告して完了。

```
## 完了
- PR: <PR_URL>
- CI: 全チェック PASS
- リトライ回数: N/3
```

## Step 4: CI失敗時

失敗ログを取得し、原因を診断して修正する。

### 4-1. 失敗ログの取得

```bash
# 失敗したランIDを取得
BRANCH=$(git branch --show-current)
RUN_ID=$(gh run list --branch "$BRANCH" --status failure --limit 1 --json databaseId --jq '.[0].databaseId')

# 失敗ログを取得
gh run view "$RUN_ID" --log-failed
```

### 4-2. 原因診断

取得したログから以下を特定する:

- どのジョブ/ステップが失敗したか
- エラーメッセージの内容
- lint / test / build / type-check のいずれか

### 4-3. 修正の実装

原因に基づいてコードを修正し、pushする。

```bash
# 修正をコミット・push
git add -A
git commit -m "fix: CI failure - <description>"
git push
```

### 4-4. 再監視

Step 2 に戻り、CIを再度監視する。

## Step 5: 3回失敗時のエスカレーション

3回修正してもCIが通らない場合、手動介入を依頼する。

```
## CI修正エスカレーション
3回の自動修正で解決できませんでした。

### 失敗履歴
1. [1回目] <失敗内容のサマリー>
2. [2回目] <失敗内容のサマリー>
3. [3回目] <失敗内容のサマリー>

### 推奨アクション
- ログを確認: gh run view <RUN_ID> --log-failed
- ローカルで再現: <再現コマンド>
- 手動で修正後、git push で再トリガー
```

---

## 注意事項

- `gh` CLI が認証済みであること（`gh auth status` で確認）
- CI が設定されていないリポジトリでは使用不可
- 既存の `/pull-request` スキルとは独立したスキル
- 修正コミットは `fix: CI failure - <description>` の形式を使う
- `--fail-fast` により最初の失敗で即座にログ取得に移行する

## いつ使うか

- PR を出してCIを通すまでを一気に済ませたいとき
- CI失敗の修正を手動で繰り返したくないとき
- `/pull-request` だと CI の面倒まで見てくれないとき
