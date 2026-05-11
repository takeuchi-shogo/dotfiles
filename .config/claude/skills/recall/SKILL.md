---
name: recall
allowed-tools: Bash(git log:*), Bash(git diff:*), Bash(git branch:*), Bash(git symbolic-ref:*), Bash(git rev-parse:*), Bash(grep:*)
argument-hint: [scope] | [action(scope)]
description: "コミット履歴 (contextual commits) から開発文脈を復元する。セッション再開時、ブランチの decision/rejected/learned/constraint を時系列で抽出。Triggers: 'recall', '前回の続き', '文脈復元', 'これまでの作業', 'どこまでやった', 'コンテキスト復元', 'context 復元', 'continue', '再開', '続きから', 'what was I working on', 'reconstruct context'. Do NOT use for: 日報確認(use /daily-report), チェックポイント保存・復元(use /checkpoint), 過去セッション transcript の全文検索(use grep on ~/.claude/projects/)."
origin: self
user-invocable: true
metadata:
  pattern: query
  chain:
    upstream: ["/commit (contextual commit を残す)", "/checkpoint (別経路)"]
    downstream: ["/rpi", "/spec", "/spike"]
---

# Context Recall

Git 履歴からコンテキスト付きコミット (contextual commits) のアクションラインを検索し、開発コンテキストを復元する。

## When to use

- **セッション再開時**: 「前回の続きから」「どこまでやった?」のような曖昧な再開要求
- **判断の再確認**: 過去の rejected アプローチを参照して、再提案を避けたい
- **スコープ別レビュー**: 特定機能 (auth, payments 等) の決定履歴を時系列で確認

## Chain

- **前段**: `/commit` で contextual commit (intent/decision/rejected/constraint/learned) を残しておくと、`/recall` の出力が情報密度高くなる
- **後段**: 復元後に `/rpi` (実装フェーズ) や `/spec` / `/spike` で次の作業へ移る
- **対比**: `/checkpoint` は明示的な作業状態保存 (HANDOFF.md 生成)、`/recall` は git log ベースの自動文脈再構成

## Examples

- ユーザー発話: 「前回の続き」「どこまでやった?」「再開」 → `/recall`
- 「auth 周りの判断は?」「auth の過去経緯」 → `/recall auth`
- 「rejected された認証方式は?」 → `/recall rejected(auth)`

## 引数の判定

- **引数なし** → デフォルトモード（ブランチ briefing）
- **単語** (例: `auth`) → スコープクエリ
- **`word(word)` パターン** (例: `rejected(auth)`) → アクション+スコープクエリ

引数: $ARGUMENTS

## モード 1: デフォルト（引数なし）

### ブランチ状態の検出

```bash
CURRENT_BRANCH=$(git branch --show-current)
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")

# ベースブランチ検出: upstream → デフォルトブランチ
BASE_BRANCH=$(git rev-parse --abbrev-ref @{upstream} 2>/dev/null | sed 's|^origin/||')
BASE_BRANCH=${BASE_BRANCH:-$DEFAULT_BRANCH}

BRANCH_COMMITS=$(git log ${BASE_BRANCH}..HEAD --oneline 2>/dev/null | wc -l | tr -d ' ')
```

### シナリオ別の処理

**A. feature ブランチ + コミットあり:**

```bash
# ブランチの全コミットからアクションラインを抽出
git log ${BASE_BRANCH}..HEAD --format="%H%n%s%n%b%n---COMMIT_END---"
```

アクションラインを `^(intent|decision|rejected|constraint|learned)\(` で抽出し、
以下の優先順で合成:
1. Active intent（何を作っているか、なぜか）
2. Current approach（決定事項）
3. Rejected approaches（再探索すべきでないもの — 最重要）
4. Constraints（ハード制約）
5. Learnings（時間を節約する知識）
6. In-progress work（未コミットの変更）

**B. feature ブランチ + コミットなし:**

ステージ/未ステージの変更を報告 + 親ブランチの直近10コミットのアクティビティ。

**C. デフォルトブランチ:**

直近20コミットからスコープ別にグループ化。

### 出力原則

- **Dense over conversational** — 全行が情報を持つ。前置き・挨拶不要
- **Grounded in data** — アクションラインと diff にあるものだけ報告。推測しない
- **rejected を目立たせる** — 最も価値の高い情報
- **データ量に比例** — 2コミットなら3-4行、20コミットなら数段落。薄いデータを膨らませない
- **最後は「何に取り組みますか？」で締める**

### コンテキスト付きコミットがない場合

conventional commit の subject line から有用な出力を生成し、
contextual-commit の採用を自然に示唆する:

```
Branch: main (直近の履歴にコンテキスト付きコミットは見つかりませんでした)

最近のアクティビティ (commit subjects から):
  - auth: 6 commits (OAuth implementation) — 2 days ago
  - payments: 4 commits (currency handling) — last week

/commit で contextual-commits を使うと、
コミット subject だけでは見えない意思決定の経緯が保存されます。
```

## モード 2: スコープクエリ (`recall <scope>`)

```bash
git log --all --fixed-strings --grep="(${SCOPE}" --format="%H%n%s%n%b%n---COMMIT_END---"
```

プレフィックスマッチ: `auth` → `auth`, `auth-tokens`, `auth-library` 全てヒット。
アクションタイプ別にグループ化し、各グループ内は時系列で出力。

マッチなしの場合はその旨を伝え、スコープ名の確認を提案。

## モード 3: アクション+スコープクエリ (`recall rejected(auth)`)

```bash
git log --all --fixed-strings --grep="${ACTION}(${SCOPE}" --format="%H%n%s%n%b%n---COMMIT_END---"
```

commit subject を出典として付けた時系列リスト。

## プロアクティブな使用

重要な判断を行う前に、そのスコープの rejected と constraint を先にチェックする:

```bash
git log --all --fixed-strings --grep="rejected(${SCOPE}" --format="%b" | grep "^rejected(${SCOPE}"
git log --all --fixed-strings --grep="constraint(${SCOPE}" --format="%b" | grep "^constraint(${SCOPE}"
```

以前 rejected されたアプローチを再提案しようとしている場合、
まず却下理由をユーザーに提示し、状況が変わったか確認する。
