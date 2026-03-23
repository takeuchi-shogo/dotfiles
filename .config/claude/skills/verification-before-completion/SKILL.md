---
name: verification-before-completion
description: >
  Mandatory verification before claiming work is complete. Run actual commands to
  confirm success — never claim completion based on assumptions. Evidence before assertions.
  Do NOT use for: テスト実行のみ（use test-engineer agent）、コードレビュー（use /review）、仕様検証（use /validate）。
allowed-tools: "Read, Bash, Grep, Glob, Agent"
metadata:
  pattern: pipeline+reviewer
---

# Verification Before Completion

## Rule

**完了を宣言する前に、必ず検証コマンドを実行して出力を確認する。**

仮定に基づく完了宣言は禁止。証拠が先、主張は後。

## Trigger

以下の行動の直前に発動:

- 「完了しました」「修正しました」「テストが通りました」と言おうとしている
- コミットを作成しようとしている
- PR を作成しようとしている
- 「問題ありません」と報告しようとしている

## Self-Verification Limitation

> Schwartz (2026): 「バグがないか確認せよ」に対し Claude は「問題なし」と回答したが、
> 実際には問題が存在していた。自己検証の判断自体が信頼できない。

**自己検証はコマンド実行による客観的証拠に限定する。**
「確認しました」「問題ありません」という主観的判断ではなく、
コマンドの exit code・テスト結果・lint 出力という客観データで判断する。

**M/L 規模の変更では**、自己検証に加えてクロスモデル検証（codex-reviewer 等への委譲）を推奨する。
自分の出力を自分で検証することの限界を認識し、独立した視点を入れる。

## Verification Checklist

### Build Check

```bash
# プロジェクトのビルドコマンドを実行
npm run build 2>&1 | tail -5
# or
go build ./... 2>&1
```

- exit code 0 を確認
- 新しい warning がないことを確認

### Test Check

```bash
# テストを実行
npm test 2>&1 | tail -20
# or
go test ./... 2>&1
```

- 全テスト PASS を確認
- skip されたテストの理由を把握

### Lint Check

```bash
# lint を実行（プロジェクトに存在する場合）
npm run lint 2>&1 | tail -10
# or
npx eslint --ext .ts,.tsx [変更ファイル]
```

### Type Check (TypeScript)

```bash
npx tsc --noEmit 2>&1 | tail -10
```

### Diff Review

```bash
# 変更内容を最終確認
git diff --stat
git diff
```

- 意図しない変更がないか
- デバッグ用コード（console.log 等）が残っていないか
- 機密情報が含まれていないか

## Decision Matrix

| 検証結果 | アクション |
|---------|-----------|
| 全パス | 完了を宣言してよい |
| ビルド失敗 | 修正してから再検証 |
| テスト失敗 | 修正してから再検証 |
| lint 警告のみ | 警告内容を報告し、修正判断をユーザーに委ねる |
| コマンドが存在しない | その旨を報告（「テストコマンドが未設定」等） |

## Output Format

検証結果は以下の形式で報告:

```
## 検証結果
- Build: PASS (exit 0)
- Test: PASS (42 tests, 0 failures)
- Lint: PASS (no warnings)
- Type: PASS (no errors)
- Diff: 3 files changed, 45 insertions, 12 deletions
```

## Iterative Convergence Check

> Schwartz (2026) の "Check again until nothing new" パターン。
> 単一パスでは見逃すエラーが、反復検証で浮上する。

**適用条件**: M/L 規模の変更、または Build/Test/Lint のいずれかで修正を行った場合。

### 手順

1. 上記 Verification Checklist を1パス実行する
2. 問題が見つかり修正した場合、**もう一度最初から**チェックを実行する
3. 新しい問題が見つからなくなるまで繰り返す（最大 3 イテレーション）
4. 3 イテレーションで収束しない場合、残存問題をユーザーに報告して判断を委ねる

### 判定

| イテレーション結果 | アクション |
|-------------------|-----------|
| 1パス目で全パス | 完了宣言 OK |
| 修正後の再検証で全パス | 完了宣言 OK |
| 3回繰り返しても新しい問題が出る | ユーザーにエスカレーション |

## Anti-Patterns

- 「おそらく動くはず」で完了宣言する
- ビルドやテストを実行せずに「問題ありません」と言う
- エラーが出ているのに「些細な問題」として無視する
- 前回の実行結果を使い回す（変更後は必ず再実行）
- 1パスの検証で安心し、修正が連鎖的に影響する可能性を無視する
