---
name: verification-before-completion
description: >
  Mandatory verification before claiming work is complete. Run actual commands to
  confirm success — never claim completion based on assumptions. Evidence before assertions.
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

## Anti-Patterns

- 「おそらく動くはず」で完了宣言する
- ビルドやテストを実行せずに「問題ありません」と言う
- エラーが出ているのに「些細な問題」として無視する
- 前回の実行結果を使い回す（変更後は必ず再実行）
