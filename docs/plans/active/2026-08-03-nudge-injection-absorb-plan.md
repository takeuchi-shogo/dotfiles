---
date: 2026-08-03
status: active
source: docs/research/2026-08-03-prompt-improver-nudge-injection-absorb-analysis.md
---

# Nudge Injection Absorb Plan

L 規模 (6 タスク・8 ファイル超) の実装プラン。分析元は `severity1/claude-code-prompt-improver` の absorb 分析 (上記 source)。

## タスク

### T1 (M): `measure-instruction-budget.py` の修理 + 配線

- **対象**: `.config/claude/scripts/policy/measure-instruction-budget.py`, Taskfile.yml or 既存 weekly cron
- **変更**:
  (a) `measure_hook_outputs()` の glob 先を `~/.claude/logs/session-*.jsonl` から Rust hook の実出力先 `~/.claude/agent-memory/current-session.jsonl` に変更し、`_HOOK_EVENT_TYPES` が実際のイベント形式に合うか確認する
  (b) データが無いとき `0 tokens` でなく `unknown` を返し silent zero をやめる
  (c) weekly cron か `task` target に配線
- **検証**: 修正後に実走行して `hook_injected` が非ゼロになること。0 のままなら (b) により `note` 付きで報告されること
- **撤退条件**: `current-session.jsonl` に hook 注入テキストの本文が記録されていない (イベント種別だけで本文が無い) 場合、計測は原理的に不可能なので T1 を撤去 (retire) に切り替える。この判断は実データを見てから行う

### T2 (S): `plan-implement-bridge.py` の配線 or 撤去の確定

- **対象**: `.config/claude/settings.json` の PostToolUse (Edit|Write)、または `docs/decommission-log.md`
- **変更**: docstring 通り配線するか、`references/harness-stability.md` (削除は 30 日評価後) に従って撤去する。2026-04-23 の escalation から 100 日以上経過しており評価期間は満了している
- **検証**: 配線するなら PLANS.md の Success Criteria を編集して advisory が出ることを確認。撤去するなら `hook-failure-policy.md:43` の該当行も削除
- **撤退条件**: なし (どちらかに確定させることが目的)

### T3 (S): router 系 hook の self-cancel 句 + ADR-0006 への明文化

- **対象**: `tools/claude-hooks/src/user_prompt.rs` (`[Agent Router]`), `tools/claude-hooks/src/pre_tool.rs` (`[Suggest-Gemini]`), `docs/adr/0006-hook-philosophy.md`
- **変更**: 検出を事実として述べる注入文の末尾に「該当しなければこの提案は無視してよい」相当の句を足す。ADR-0006 の分類 2 (Semantic Advisory、条件 b「false positive が避けられない」) の実装規約に「注入文は条件節で始め自己キャンセル句で終える」を追記
- **検証**: `cargo test` + `cargo build` して binary を更新。既存テストが落ちないこと
- **撤退条件**: 既存の Rust テストが注入文の完全一致を assert していて大量に落ちる場合、文面変更を最小化する
- **注意**: `post_edit.rs:357` の Loop Detection は既に自己キャンセル相当 (`この警告は情報提供であり、修正不要です。`) なので触らない (leave neighbors untouched)

### T4 (S): audience/timing 規約表を既存 reference に追記

- **対象**: `.config/claude/references/hook-failure-policy.md` (または `determinism-boundary-analysis.md` — 実装時に既存の hook 規約文書を grep して適切な 1 箇所に決める。新規 reference は作らない = instruction DRY)
- **変更**: hook event ごとに「出力を読むのは誰か (subagent / 親エージェント)」「いつ届くか (UserPromptSubmit は即時 / PreToolUse の additionalContext は次のモデルリクエスト)」「どれだけ持続するか」を表で 1 節追記。記事の Timing rule を出典として引用
- **検証**: `task validate-configs` / 参照切れがないこと
- **撤退条件**: 既存文書に同等の表が既にあれば追記せず、そこへのリンクだけ張って閉じる (grep で先に確認する)

### T5 (S): `run_hook()` fail-open の回帰テスト

- **対象**: `.config/claude/scripts/tests/` に新規テストファイル
- **変更**: `hook_utils.run_hook()` に malformed JSON / 欠損ペイロード / main_func が例外を投げるケースを与え、`fail_closed=False` なら exit 0 + 空 JSON、`fail_closed=True` なら exit 2 になることを検証
- **検証**: `pytest` で green
- **撤退条件**: なし

### T6 (S): validation-only — memory の因果訂正

- **対象**: `~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/feedback_explore_subagent_bash_limit.md`
- **変更**: 分析ドキュメントの「Validation-only Follow-up」表の訂正方針の通り書き換える。ファイル名 (slug) が内容と合わなくなるので `feedback_subagent_bash_permission_deny.md` にリネームし MEMORY.md の索引行も更新することを検討する
- **検証**: `.config/claude/agents/Explore.md` が存在しないことを再確認したうえで書き換える
- **撤退条件**: なし

## 依存関係

- T1 → (#2 UserPromptSubmit 評価注入の再評価。計測基盤が直るまで着手しない)
- T3 は Rust binary の rebuild が必要なので T4/T5/T6 とは独立に扱う
- T2 は T1 の判断 (配線 or 撤去) と方針を揃える (どちらも orphan の処分)
- T4/T5/T6 は相互に独立、並列実行可

## 運用注意

- 現在のブランチは `chore/drop-unwired-rules-paths-frontmatter` で未コミット変更あり。着手前に `git branch --show-current` を確認し、worktree + PR 運用に従って新ブランチを切る (`memory/feedback_dotfiles_worktree_pr_workflow.md`)
- harness 変更を含むため `docs/agent-harness-contract.md` と `references/change-surface-matrix.md` に従い、最低検証は `task validate-configs` + `task validate-symlinks`
- settings.json 変更時は全 event 配列を先に grep する (`memory/feedback_settings_json_grep_first.md`)。また `~/.claude/settings.json` は symlink でなく実体なので dotfiles 変更が live に自動反映されない (`memory/project_claude_settings_live_drift.md`)
