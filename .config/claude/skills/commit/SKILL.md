---
name: commit
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git diff:*), Bash(git log:*)
argument-hint: [message] | --amend | --no-verify
description: >
  conventional commit + 絵文字プレフィックスで整形されたコミットを作成する。
  Triggers: 'commit', 'コミット', 'コミットして', 'save changes', 'git commit'.
  Do NOT use for: PR 作成（use /pull-request）、チェックポイント保存（use /checkpoint）。
origin: self
---

# Smart Git Commit

Create well-formatted commit: $ARGUMENTS

## Current Repository State

- Git status: !`git status --porcelain`
- Current branch: !`git branch --show-current`
- Staged changes: !`git diff --cached --stat`
- Unstaged changes: !`git diff --stat`
- Recent commits: !`git log --oneline -5`

## What This Command Does

1. プロジェクトに lint/test コマンドがあれば実行して品質を確認
2. `git status` でステージ済みファイルを確認
3. ステージ済みファイルが0件なら、変更・新規ファイルを `git add`
4. `git diff` で変更内容を分析
5. 複数の論理的変更がある場合、コミット分割を提案
6. 絵文字付き conventional commit 形式でコミットメッセージを作成

## Conventional Commit Format

`<emoji> <type>: <description>` — 1行目は72文字以内、現在形・命令形で記述。

### 頻出絵文字

| Emoji | Type | 用途 |
|-------|------|------|
| ✨ | feat | 新機能 |
| 🐛 | fix | バグ修正 |
| 📝 | docs | ドキュメント |
| 💄 | style | フォーマット・スタイル |
| ♻️ | refactor | リファクタリング |
| ⚡️ | perf | パフォーマンス改善 |
| ✅ | test | テスト追加・修正 |
| 🔧 | chore | ツール・設定変更 |
| 🚀 | ci | CI/CD 改善 |
| ⏪️ | revert | 変更の取り消し |
| 🔒️ | fix | セキュリティ修正 |
| 🔥 | fix | コード・ファイル削除 |
| 💥 | feat | 破壊的変更 |
| 🏷️ | feat | 型定義の追加・更新 |
| 🚑️ | fix | クリティカルな修正 |

## Guidelines for Splitting Commits

以下に該当する場合、コミットの分割を提案する:

1. **異なる関心事**: コードベースの無関係な部分への変更
2. **異なる変更タイプ**: feat, fix, refactor 等の混在
3. **ファイルパターン**: ソースコードとドキュメント等、異なる種類のファイル

## Contextual Commits — Action Lines

コミットメッセージの **ボディ** に構造化されたアクションラインを追加し、
diff だけでは見えない意思決定コンテキストを保存する。
Ref: https://github.com/berserkdisruptors/contextual-commits (SPEC v0.1.0)

### いつアクションラインを書くか

| 状況 | アクションライン |
|------|----------------|
| typo修正、依存バンプ、フォーマット | なし（subject のみ） |
| 明確な技術選択があった | `decision()` のみ |
| 代替案を検討・却下した | `decision()` + `rejected()` |
| ユーザーの目的が subject から自明でない | `intent()` 追加 |
| 実装中に制約を発見した | `constraint()` 追加 |
| API quirk やライブラリの罠を発見した | `learned()` 追加 |
| このセッションでコンテキストがない変更 | diff から推測できる `decision()` のみ、または省略 |

**推奨: 1-3行、最大5行。** 超える場合はコミット分割を提案する。

### アクションタイプ

- `intent(scope)`: ユーザーの目的・動機。ユーザーの言葉で記述する
- `decision(scope)`: 選択したアプローチ。代替案が存在した場合のみ
- `rejected(scope)`: 却下した選択肢。**理由を必ず含める**（理由なしの rejected は禁止）
- `constraint(scope)`: 実装を形作った制約。次の人が知るべき境界条件
- `learned(scope)`: 発見した API quirk や非自明な挙動。「知っていれば時間を節約できた」情報

### scope ルール

- lowercase alphanumeric + hyphens（例: `auth`, `oauth-library`, `payment-flow`）
- コミット前に同一ブランチの既存スコープを確認し、既存スコープを優先使用する:
  `git log --format="%b" | grep -oP '(?<=\()[a-z0-9-]+(?=\))' | sort -u`
- subject line の scope と action line の scope は独立（異なって良い）

### MUST ルール（絶対遵守）

1. **fabrication 禁止**: このセッションで議論していない変更には intent/rejected/constraint/learned を書かない。根拠のないアクションラインは書くな。書かない方が100倍マシ
2. diff から推測できる `decision()` のみ、コンテキストなしの変更に許可
3. `rejected()` には必ず却下理由を含める
4. trivial な変更（typo、bump、format）にはアクションラインを書かない

### コミット実行フォーマット

アクションラインがある場合は HEREDOC を使用:

```bash
git commit -m "$(cat <<'EOF'
✨ feat(auth): implement Google OAuth provider

intent(auth): social login starting with Google, then GitHub and Apple
decision(oauth-library): passport.js over auth0-sdk for multi-provider flexibility
rejected(oauth-library): auth0-sdk — locks into their session model
EOF
)"
```

アクションラインがない場合は従来通り:

```bash
git commit -m "🐛 fix(button): correct alignment on mobile viewport"
```

## AutoEvolve 連携

コミット成功後、`rejected()` と `learned()` を AutoEvolve learnings に転送する。
intent/decision/constraint は転送しない（git 履歴が権威ソース）。

アクションラインを含むコミットが成功したら、rejected/learned ごとに実行:

```bash
CC_TYPE="rejected" CC_SCOPE="oauth-library" CC_DETAIL="auth0-sdk — session model incompatible" \
python3 - <<'PYEOF'
import sys, os
sys.path.insert(0, os.path.join(os.path.expanduser('~'), '.claude/scripts/lib'))
from session_events import emit_event
emit_event('pattern', {
    'type': os.environ['CC_TYPE'],
    'scope': os.environ['CC_SCOPE'],
    'detail': os.environ['CC_DETAIL'],
    'source': 'contextual-commit'
})
PYEOF
```

- emit 失敗はコミットに影響しない（best-effort）
- `source: contextual-commit` で AutoEvolve 側でフィルタ可能

## Examples

### Trivial — アクションラインなし
- 🐛 fix(button): correct alignment on mobile viewport
- 📝 docs: update API documentation with new endpoints

### Moderate — 1-3行

```
✨ feat(notifications): add email digest for weekly summaries

intent(notifications): users want batch notifications instead of per-event emails
decision(digest-schedule): weekly on Monday 9am — matches user research feedback
```

### Complex — 3-5行

```
♻️ refactor(payments): migrate from single to multi-currency support

intent(payments): enterprise customers need EUR and GBP alongside USD
decision(currency-handling): per-transaction currency over account-level default
rejected(currency-handling): account-level default — too limiting for marketplace sellers
constraint(stripe-integration): Stripe requires currency at PaymentIntent creation
learned(stripe-multicurrency): presentment currency vs settlement currency are different concepts
```

### コンテキストなし — diff のみから推測

```
♻️ refactor(http-client): replace axios with native fetch

decision(http-client): switched from axios to native fetch for zero-dependency HTTP
```
