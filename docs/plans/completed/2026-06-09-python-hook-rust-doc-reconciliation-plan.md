---
title: Python hook → Rust ドキュメント整合 + 残骸削除
date: 2026-06-09
status: planned
size: L
origin: 2026-06-08 「30 Copy-Paste System Prompts」重複 absorb の wiring-check #2
related:
  - docs/specs/2026-04-27-claude-hooks-codex-migration.md  # Rust 移行の設計 spec (source of truth)
  - docs/wiki/log.md  # 2026-06-08 ingest-skip エントリ + wiring-check #2
---

# Python hook → Rust ドキュメント整合 + 残骸削除

## 背景 (何が起きたか)

2026-06-08 に Khairallah「30 Copy-Paste System Prompts」を absorb (実は同日2回目の重複) した際、
ユーザーの「skip は知ってるだけか・配線できてるか」という問いを起点に wiring-check を実施。
マルチモデル連携 hook の配線を検証した結果、**システミックな drift** を発見した:

- **Rust binary `tools/claude-hooks` (1.7M, 2026-04-14 build) が live** で settings.json に登録済み
  (UserPromptSubmit / PostToolUse の各サブコマンド)
- **Python `.py` 版は settings.json 未登録 = 一度も発火しない移行残骸**。しかも DEPRECATED マーカーなし
- `error-to-codex.py` のみ正しく削除済み (de016cf)、他3つ (agent-router / suggest-gemini / post-test-analysis) は消し忘れ
- **MEMORY.md のマルチモデル連携セクションが旧 .py 名で記載** → これが wiring-check を「死蔵」と誤誘導した
  (→ 2026-06-09 訂正済み: Rust 移行先を明記)
- **ドキュメント体系全体が Python hook 前提のまま** = .py が 23ファイルから「現役 hook」として参照されている

## 目的

Python hook の Rust 移行を**現役ドキュメントに反映**し、**.py 残骸を安全に削除**する。
歴史記録 (ADR / migration spec / completed・paused plan) は immutable として保全する (歴史改竄しない)。

## Rust 移行マッピング (source of truth)

| Python 残骸 (.py) | Rust live 先 | サブコマンド | 確認済み |
|---|---|---|---|
| `scripts/policy/agent-router.py` | `tools/claude-hooks/src/user_prompt.rs` | UserPromptSubmit (`claude-hooks user-prompt`) | ✅ src:1 "agent-router: keyword detection" |
| `scripts/policy/suggest-gemini.py` | `tools/claude-hooks/src/pre_tool.rs` | PreToolUse WebSearch (`pre-websearch`) | ✅ src:379 "pre-websearch: suggest gemini" |
| `scripts/policy/post-test-analysis.py` | `tools/claude-hooks/src/post_bash.rs` | PostToolUse Bash (`post-bash`) | ✅ src:419 `fn check_post_test` |
| (参考) `error-to-codex.py` 削除済 | `tools/claude-hooks/src/post_bash.rs` | post-bash | ✅ src:235 `fn check_error_to_codex` |

詳細な移行設計は `docs/specs/2026-04-27-claude-hooks-codex-migration.md` を参照 (Research フェーズで必読)。

## スコープ

### A. 削除 (4ファイル) — 本丸の死蔵除去

- `scripts/policy/agent-router.py`
- `scripts/policy/suggest-gemini.py`
- `scripts/policy/post-test-analysis.py`
- `scripts/tests/test_agent_router.py` ← **削除前チェック必須** (下記 failure mode 参照)

### B. 現役ドキュメント書き換え (13ファイル) — .py 参照を Rust に

| ファイル | hit | 主な箇所 |
|---|---|---|
| `.config/claude/README.md` | 6 | :184,:197 (agent-router) / :187,:215 (suggest-gemini) / :189,:207 (post-test) |
| `.config/claude/references/diagrams/agent-routing.md` | 4 | routing 図の node ラベル |
| `.config/claude/references/agent-orchestration-map.md` | 4 | :106,:107 + **:187 nextjs-architecture-expert 退役参照も同時訂正** |
| `.config/claude/references/workflow-guide.md` | 3 | :85,:676,:892 |
| `.config/claude/references/subagent-delegation-guide.md` | 3 | (Research で特定) |
| `.config/claude/references/multi-agent-coordination-patterns.md` | 3 | (Research で特定) |
| `.config/claude/references/observability-signals.md` | 2 | :23 (Gap 5 routing ログ), :94 |
| `.config/claude/references/hook-failure-policy.md` | 2 | :54,:59 |
| `.config/claude/references/advisor-strategy.md` | 1 | :84 |
| `.config/claude/references/agency-safety-framework.md` | 1 | :127 |
| `.config/claude/references/cross-model-insights.md` | 1 | :186 |
| `.config/claude/rules/codex-delegation.md` | 1 | (Research で特定) |
| `.config/claude/references/` 配下の wiki | — | `docs/wiki/concepts/multi-agent-architecture.md`(1), `docs/wiki/concepts/skill-invocation-patterns.md`(1) |

(計: references/rules 11 + README 1 + wiki concepts 2 = 13。wiki は docs/ だが現役ドキュメントなので B に含む)

書き換え方針: 「`agent-router.py` が…」→「`claude-hooks` (Rust, `user_prompt.rs`) が…」のように、
Python ファイル名を Rust binary + サブコマンドに置換する。**実装の実際の挙動を読んでから書く**
(推測で書くと新たな drift を生む — pre-mortem 参照)。

### C. active plan 修正 (2ファイル) — stale 前提を Rust に

- `docs/plans/active/2026-06-05-rsi-governance-frontier-plan.md` :70,:84 —
  **C1 (捕捉率計測) が post-test-analysis.py への append を前提**にしている。
  Rust `post_bash.rs check_post_test` への実装に載せ替え可能か検討し、plan を更新
  (載せ替え不可なら C1 スコープ再設計を plan 内に明記)
- `docs/plans/active/2026-04-19-harness-everything-absorb-plan.md` :1 — .py 参照を確認し現状反映

### D. immutable 除外 (7ファイル) — 触らない

- `docs/adr/0003-multi-model-orchestration.md`, `0006-hook-philosophy.md`, `0008-coordinator-vs-human-ram.md`
- `docs/plans/completed/2026-03-15-harness-improvements-from-article.md`
- `docs/plans/paused/2026-03-13-performance-optimization.md`
- `docs/specs/2026-04-27-claude-hooks-codex-migration.md` (Python 名が出るのが**正しい** — 移行記録)

**理由**: ADR は決定時点の記録、completed/paused plan と migration spec は歴史の足跡。
書き換えると決定の歴史が壊れる。任意で ADR 0003/0006 に「Superseded by Rust migration (spec 2026-04-27)」
の1行注記を**追記** (書き換えではなく追記) するのは可。判断は Research フェーズで。

## 削除前チェック (failure mode ガード)

1. **test_agent_router.py のカバレッジ喪失リスク**:
   削除前に `tools/claude-hooks` 側に同等の Rust テスト (user_prompt.rs のキーワード検出テスト) が
   存在するか確認する。**なければ .py 削除前に Rust テストを追加** (ロジックテストを失わない)。
   `grep -rn "test\|#\[cfg(test)\]" tools/claude-hooks/src/user_prompt.rs`
2. **active plan C1 の載せ替え可否**: rsi-governance C1 が Rust に移植不能なら plan 再設計が必要
3. **ドキュメント書き換えの新 drift**: Rust 実装の実挙動を読まずに書くと、今度は「ドキュメント vs Rust」の
   新 drift を生む。各書き換えは `tools/claude-hooks/src/*.rs` の該当ロジックを引用根拠にする

## 撤退条件 (reversible-decisions)

- .py 削除後、Rust binary に未カバーの機能 (Python にあって Rust にない挙動) が判明 → 該当 .py を revert + issue 化
- ドキュメント書き換えが Rust 実挙動と乖離していると Codex Review で判明 → 該当ファイルを revert
- active plan C1 の Rust 載せ替えが破壊的 → C 部分のみ切り離して別 plan に

## 検証 (verification-before-completion)

1. `task validate-configs` + `task validate-symlinks`
2. `cd tools/claude-hooks && cargo test` (Rust テスト全通過)
3. `.py` 3削除後: `grep -rn -E "agent-router|suggest-gemini|post-test-analysis" .config docs` で
   **残るのは immutable 7ファイル + research/log のみ**であることを確認 (現役からの参照ゼロ)
4. settings.json に変更なし (Rust binary 登録は既存のまま) を確認
5. Codex Review Gate (codex-reviewer + code-reviewer 並列) — harness ドキュメント変更のため

## 実行手順 (新セッション /rpi)

```
/rpi docs/plans/active/2026-06-09-python-hook-rust-doc-reconciliation-plan.md
```

1. **Research**: migration spec (2026-04-27) + Rust src (user_prompt/pre_tool/post_bash.rs) を読み、
   各 .py 参照の正確な書き換え先を確定。test_agent_router.py の Rust カバレッジ確認
2. **Plan**: worktree 作成 (`.worktrees/` or native EnterWorktree)、B→C→A の順 (削除は最後)
3. **Implement**: 13ドキュメント書き換え → 2 active plan 修正 → 4削除 (test カバレッジ確保後)
4. **Verify**: 上記検証5項目
5. **Review**: Codex Review Gate
6. PR 作成 (/pull-request)

## メモ

- 同時訂正: agent-orchestration-map.md:187 の `nextjs-architecture-expert` は agents/_archived/ 退役済み
  (2026-06-08 absorb wiring-check #1 で発見の積み残し)。本 plan の B で agent-orchestration-map.md を
  触るので、ついでに訂正する
- MEMORY.md マルチモデル連携セクションは 2026-06-09 訂正済み (本 plan の対象外)
- **退役記録 (慣行)**: スコープ A の .py 4削除を実行したら `docs/decommission-log.md` に追記する。
  形式: `| 実行日 | scripts/policy/{agent-router,suggest-gemini,post-test-analysis}.py + scripts/tests/test_agent_router.py | Rust claude-hooks (user_prompt/pre_tool/post_bash) 移行済・settings.json 未登録の残骸 | 即削除済 |`。
  dotfiles は退役を decommission-log に集約する (新規 CHANGELOG は作らない)
