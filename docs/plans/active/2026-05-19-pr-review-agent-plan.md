# PR Review Agent (cmux + サブスク Claude) Plan

> **Status**: 🟢 B 検証完了 / Phase A 未着手 (kept)
> **Owner**: ShogoTakeuchi
> **Started**: 2026-05-19
> **Last updated**: 2026-06-20
> **kept-by**: 2026-06-20 (loop-engineering absorb stale-plan audit、意図的保留で active 維持。実装は追いかける)
> **Resume command**: このファイルを読んだ後 `## 次に再開する手順` セクションへ

## ゴール

GitHub PR で **`work-dev` 所属の自分がレビュアーに指定されたら、Mac 内で Claude が自動レビューしてローカルに review.md を出す** 仕組みを作る。

## 制約

- **サブスク内で完結**: `ANTHROPIC_API_KEY` は使わない (OAuth/サブスク認証のまま)
- **対象リポジトリ**: `knowledge-work/knowledgework` のみ (ハードコード)
- **`gh pr review` は実行しない**: 出力はローカル markdown のみ
- **既存資産活用**: cmux Worktree Agents action (Issue #49) の流儀に合わせる
- **観測可能性**: cmux pane で進行が見える / 途中で止められる

## アーキテクチャ

```
┌──────────────────────────────────────────────────────┐
│ macOS                                                 │
│                                                       │
│  [Phase A: 自動化 — 未着手]                            │
│  launchd (10分polling) ← 未実装                       │
│     │ gh search prs --review-requested=@me            │
│     ▼                                                 │
│  cmux automation socket (port 9100~)                  │
│                                                       │
│  [Phase B: cmux UI 経路 — 実装済]                      │
│  cmux "PR Review Agent" action                        │
│     ├─ Setup pane: PR番号入力 → prepare-pr-review.sh   │
│     └─ Claude pane: state 待機 → cd worktree → claude  │
│                                                       │
│  [Phase D1/C: 手動経路 — 検証済 ✅]                    │
│  ~/dotfiles/scripts/runtime/prepare-pr-review.sh <#>  │
│     ├─ knowledgework-review/.claude/worktrees/pr-<#>/  │
│     ├─ REVIEW_TASK.md 配置                             │
│     └─ Claude セッション起動を案内                      │
└──────────────────────────────────────────────────────┘
```

## 進捗

| Phase | 内容 | 状態 | 備考 |
|---|---|---|---|
| **C** | `REVIEW_TASK.md.tpl` (プロンプトテンプレ) | ✅ 完了 | 3観点: diff / 影響範囲 / KW固有リスク |
| **D1** | 手動セットアップ script (`prepare-pr-review.sh`) | ✅ 完了 | PR #115802 で動作確認済み |
| **B** | cmux.json に `pr-review-agent` action 追加 | ✅ 検証完了 | PR #114950 で動作確認、production 品質出力 |
| **B-host** | work Mac 限定 host gate (commit `964749d`) | ✅ 完了 | private profile での誤起動防止 |
| **B-fix** | Completion Gate 誤発火 + worktree trust (commit `0db6fce`) | ✅ 完了 | CLAUDE_SKIP_TEST_GATE=1 + direnv allow + mise trust |
| **A** | launchd + polling script で完全自動化 | ⬜ 未着手 | 次のステップ |

## 検証結果 (PR #115802)

- PR: `feat(recording/be): implement SearchTranscriptions RPC handler` by @haniwawww
- 出力: `knowledgework-review/.claude/worktrees/pr-115802/.claude/pr-reviews/pr-115802.md`
- **品質**: production レベル、人間が読んで価値あり
  - 3 観点全カバー、reviewer-ma/mu 並列起動 → 統合所見
  - file:line 参照付き、severity ラベル (BLOCKING/SHOULD/NICE-TO-HAVE)
  - KW 固有 context (SecureString / CODEOWNERS / multi-tenant / PII) を踏まえた指摘
  - **自己批判セクションが秀逸**: 確信度低い finding、未確認の前提を正直に記載
  - 制約遵守: `gh pr review` 未実行、出力先以外への write なし

## 既知の問題

### ⚠️ `code-review-graph` MCP が利用されない → **別タスク化 (Issue #54)** → 🚧 暫定対応中 (2026-05-20)

→ https://github.com/takeuchi-shogo/dotfiles/issues/54

検証時 (PR #115802) のレビュー出力で `code-review-graph MCP は当環境で未利用可能` と記載され、`rg` 代替に。

**この plan のスコープ外** として切り出し:
- MCP scope / worktree からの可視性調査
- グラフの初回 build 自動化
- 別タスクで進める

**2026-05-20 暫定対応 (実装済 / 検証待ち)**:
- 原因特定: `.code-review-graph/` は per-cwd 配置のため worktree から見えなかった (MCP scope 問題ではない)
- dotfiles に code-review-graph install (`uvx code-review-graph install --platform claude-code`)
- knowledgework-review でグラフ初回 build 完了 (46,045 files / 401,277 nodes / 3.35M edges)
- `prepare-pr-review.sh` に worktree 用 symlink ロジック追加 (`<worktree>/.code-review-graph -> ${REVIEW_REPO_DIR}/.code-review-graph`)
- グローバル gitignore に `.code-review-graph/` を追加 (誤コミット防止)
- 次の PR Review 起動で動作確認すること (受入基準は Issue #54 参照)

**この plan での対応** (2026-05-19 実施):
- `REVIEW_TASK.md.tpl` に **Phase 0 (環境 sanity check)** を追加
- MCP 不可時に silent fallback 禁止、出力先 markdown に明記を強制
- 観点② で MCP 可用なら graph tools を順番に強制実行

### ⚠️ worktree 作成後の副作用 (PR #114950 で判明)

- `direnv: error .envrc is blocked` (要 `direnv allow`)
- `mise ERROR Config files ... are not trusted` (要 `mise trust`)
- `starship node コマンド timeout` (警告のみ)

→ Phase B 検証完了後、`prepare-pr-review.sh` で自動承認を検討。

## 次に再開する手順

**現在の position**: ユーザーが「1 から順に」(= B のテスト → MCP 修正 → A の自動化) を選択。今 **B のテスト待ち**。

### Step 1 — B (cmux UI 経路) を試す

ユーザーアクション:
1. cmux で `cmd+shift+,` (config リロード) または cmux 再起動
2. New Workspace → context menu → **「PR Review Agent」** 選択
3. Setup pane で PR 番号入力 (例: 115802 は既存 worktree あり → skip 動作確認になる、別の新規 PR がベター)
4. Claude pane が自動起動するか観察

確認ポイント:
- ✅ Setup pane に黄色タイトル `PR Review Agent — knowledge-work/knowledgework` が出るか
- ✅ `Enter PR number: ` プロンプトで入力できるか
- ✅ Claude pane が timeout (300s) 前に claude 起動するか
- ⚠️ 失敗時は Setup pane の ERROR / Claude pane の待機状態を確認

### ✅ B 検証完了 (PR #114950, 2026-05-20)

- 出力: `~/projects/knowledge-work/knowledgework-review/.claude/worktrees/pr-114950/.claude/pr-reviews/pr-114950.md`
- Phase 0 環境チェック動作確認:
  - MCP code-review-graph: NG (ToolSearch にすら出ない) → Issue #54 に追加証拠コメント
  - 観点② rg / Grep フォールバック明記 ✅ silent fallback 防止成功
- レビュー本体品質: production 級 (dead code 発見 = PR #114950 は誤ったファイルを修正していた)
- 副作用 (direnv blocked / mise untrusted / Completion Gate 誤発火) を commit `0db6fce` で修正
- worktree 撤収済み (2026-05-20)

### Step 2 — テンプレ強化 ✅ 完了 (2026-05-19)

`templates/pr-review/REVIEW_TASK.md.tpl` を強化:
- **Phase 0**: `mcp__code-review-graph__list_repos_tool` で MCP 可用性チェック → 結果を最終 markdown 冒頭の「環境チェック」セクションに必ず記載
- MCP 可用なら `build_or_update_graph_tool` を強制実行
- 観点② で graph tools (`get_impact_radius_tool` / `get_affected_flows_tool` / `cross_repo_search_tool`) を順番に強制
- silent fallback 禁止 (使えなかった事実を出力に明記)

→ pr-114950 worktree は古いテンプレ展開済みのため、Claude pane で上書きプロンプトを投入して再検証。

**MCP を worktree で使えるようにする件は別タスク化** (この plan のスコープ外)。

### Step 3 — A (launchd + polling) で完全自動化

設計案:
- launchd plist: `~/Library/LaunchAgents/com.user.pr-reviewer.plist` (10 分間隔)
- polling script: `~/dotfiles/scripts/runtime/poll-pr-reviewer.sh`
  - `gh search prs --review-requested=@me --state=open --repo knowledge-work/knowledgework`
  - 完了マーカー: `~/projects/knowledge-work/knowledgework-review/.claude/pr-reviews/.processed/pr-<#>.done`
  - cmux automation socket (port 9100~) で `pr-review-agent` action を invoke
- 並列上限 N=2、レート枠保護のため polling 間隔は 10 分推奨

## ファイル一覧

実装済 (未コミット):
- `templates/pr-review/REVIEW_TASK.md.tpl` — Claude セッション初期プロンプト
- `scripts/runtime/prepare-pr-review.sh` — worktree 作成 + テンプレ展開 (ユーザーが lint で微修正済: sed → python literal 置換に変更)
- `.config/cmux/cmux.json` — `actions.pr-review-agent` + `commands[1]` 追加、`ui.newWorkspace.contextMenu` にも追加

未作成 (Phase A 用):
- `scripts/runtime/poll-pr-reviewer.sh`
- `scripts/runtime/com.user.pr-reviewer.plist`

参照:
- 既存 cmux Worktree Agents: `.config/cmux/cmux.json` の `worktree-agents` action (Issue #49)
- 既存 wt-* wrappers: `.config/zsh/functions/worktree.zsh` (Issue #48)
- KW レビュアー agents: `templates/pr-review/REVIEW_TASK.md.tpl` 内で reviewer-ma / reviewer-mu を参照 (user-level agents)
- 検証 PR: https://github.com/knowledge-work/knowledgework/pull/115802

## セッション復帰のための最短コマンド

新セッションで再開する場合:

```bash
# 1. このプランを読む
cat ~/dotfiles/docs/plans/active/2026-05-19-pr-review-agent-plan.md

# 2. 検証済の出力を確認 (品質チェック用リファレンス)
cat ~/projects/knowledge-work/knowledgework-review/.claude/worktrees/pr-115802/.claude/pr-reviews/pr-115802.md

# 3. 現在のスクリプトを確認
cat ~/dotfiles/scripts/runtime/prepare-pr-review.sh
cat ~/dotfiles/templates/pr-review/REVIEW_TASK.md.tpl

# 4. cmux.json の該当アクションを確認
grep -A 30 'pr-review-agent' ~/dotfiles/.config/cmux/cmux.json
```

## やらないこと (スコープ外)

- 複数リポジトリ対応 (knowledgework 専用にハードコード)
- `gh pr review --comment` で GitHub に直接 post (人間 in the loop を維持)
- レビュー品質の自動評価 (人間が判断)
- 並列 N>2 (サブスクレート枠保護)
