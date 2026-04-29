---
source: "How OpenAI Is Setting the Default Orchestration Layer for Coding Agents (AlphaSignal @AlphaSignalAI, 2026-04-28)"
date: 2026-04-29
status: analyzed
---

## Source Summary

**主張**: OpenAI が autonomous coding agent の orchestration layer を 2 つの reference implementation でオープンソース化した（[Symphony](https://github.com/openai/symphony) Apache-2.0 ~17.3K★ / [ClawSweeper](https://github.com/openclaw/clawsweeper) MIT ~1.3K★）。両者とも Codex App Server に bind し、per-task isolation + auditable evidence + human review-only という共通パターンを持つ。

**手法**:
1. WORKFLOW.md（YAML front-matter + body）で tracker config + prompt template を宣言
2. Issue tracker polling（Linear cadence-based）
3. Per-issue workspace isolation（dir + hooks.after_create で git clone）
4. No persistent DB — tracker + filesystem からのみ state 復元
5. `codex app-server`（JSON-RPC headless mode）
6. Sandbox=workspace-write + max_concurrent_agents=10 + max_turns=20
7. Tiered cron scheduling（hot=hourly, <30d=daily, old=weekly, apply=15min）
8. Sharded parallel review（313 items × 100 shards）
9. Markdown evidence reports（records/<repo>/items/<n>.md）
10. Snapshot hash + apply-skip on drift
11. Token-stripped sandbox（review lane に token 渡さず、apply lane だけ GitHub App token 取得）
12. Proposal-only review lane（review ≠ close）
13. Conservative close threshold / keep-open bias（0% close rate on proposals）
14. Per-item timeout（10 min）
15. Apply cap（50 fresh per checkpoint）
16. Open-source spec + reference 分離（SPEC.md は language-agnostic、Elixir reference は OTP supervision のため）

**根拠**: Symphony は OpenAI 内部で PR throughput +500%。ClawSweeper は day-1 で 4000 issue close / 7 日 0% close rate on proposals = keep-open bias が効いている。

**前提条件**: 高ボリュームバックログ（>1000 issue or >100 PR/week）、Codex CLI を CI で標準化、Linear トラッカー、CI/harness engineering の地力あり。

---

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | WORKFLOW.md 概念 | Already | `docs/workflows/symphony/WORKFLOW.md` 完備（commit 609b040） |
| 2 | Issue tracker polling | Already | Symphony pilot で Linear polling 設定済み / `/improve` で `gh issue list autoevolve` label 既存 |
| 3 | Per-task workspace isolation | Already | `symphony-pilot.md` workspace.root 設定 + `worktree-based-tasking` playbook |
| 4 | Stateless orchestrator | Already | `docs/agent-harness-contract.md` durable state 3 性質 / `tools/codex-janitor` manifest+stages |
| 5 | codex app-server | N/A | Symphony WORKFLOW は app-server 指定 / Codex Janitor は `codex exec` ベース。両系統共存方針（decision log 明記）|
| 6 | Sandbox + concurrency limits | Already | `.codex/config.toml` profiles + symphony WORKFLOW `max_concurrent_agents=1` |
| 7 | Tiered cron scheduling | N/A (棄却) | `symphony-pilot.md` L24-28 で "Always-on daemon: Not adopted yet" と明言 |
| 8 | Sharded parallel review | Already | `dispatch` skill + 12 read-only Codex agent。`max_concurrent_agents=1` を意図的維持 |
| 9 | Markdown evidence reports | Gap | `runs/<ts>/manifest.json` + `stdout.jsonl` は raw 保存のみ。ClawSweeper 型 decision+evidence+snapshot hash 構造化レコード未実装（`runner.py:448-457`） |
| 10 | Snapshot hash + apply-skip on drift | Gap (high) | Janitor の stop rule（skip/usefulness/non-zero/session_lost）に drift detection なし |
| 11 | Token-stripped sandbox | Gap (low) | `profiles.review` が read-only sandbox なので実害なし。env 物理 strip は wrapper script レベルで対応可 |
| 12 | Proposal-only review lane | Already | `reviewer` / `security_auditor` 12 read-only agents で実装済み |
| 13 | Conservative close threshold / keep-open bias | Gap (mid) | `improve-policy.md` L637-643 で半分カバー。Janitor `refactor-loop.toml` stop rule に 1 件 + playbook 1 行で完結 |
| 14 | Per-item timeout | Already | symphony WORKFLOW `turn_timeout_ms=3600000` / `tools/codex-janitor` subprocess timeout |
| 15 | Apply cap | N/A (棄却) | `improve-policy` resource_targets ≤ 2 + 3 要素同時変更禁止で個人 blast radius 十分 |
| 16 | Spec + reference 分離 | Already | Symphony 自体が SPEC.md + Elixir reference。dotfiles は `WORKFLOW.md`（repo-local spec）|
| F0 | Janitor Follow-Ups (既存 TODO) | Gap | `docs/playbooks/codex-janitor-workflow.md` L66-72 に TODO 化されている no-op diff / validation failure summary / token budget stop conditions 未実装 |

---

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | `runs/<ts>/manifest.json` + `stdout.jsonl` | raw 保存のみ。decision rationale・snapshot hash・evidence 欠落。Codex 批評で過小評価判明 | ClawSweeper 型構造化レコード（decision/evidence/snapshot_hash フィールド）を manifest schema に追加 | 強化可能（#9 と #10 で同実装） |
| S2 | `dispatch` skill + 12 read-only agents | sharding logic なし（個人規模では不要） | 強化不要（max_concurrent_agents=1 を意図的維持） | 強化不要 |
| S3 | `profiles.review` read-only sandbox | token 物理 strip なし | wrapper script レベルで env strip 追記（低優先） | 強化可能（#13+#11 に bundled） |

---

## Integration Decisions

### Decision Log

- **哲学衝突なし**: Symphony WORKFLOW（app-server ベース）と Codex Janitor（`codex exec` ベース）は二系統共存で OK。`codex-apps-pilot.md` の deny-by-default 方針を維持。
- **Codex 推奨**: 既存 Janitor Follow-Ups（F0）の消化を最上位優先度とする。新規 Gap より既存 TODO 消化が先。
- **Gemini 警告反映**: snapshot detection の scope を single-run 内のみに限定。cron tier 化（hot/warm/cold）は YAGNI＋個人 dotfiles のローカル手動編集頻発リスクで棄却。
- **#9 と #10 は同実装**: Already 強化可能（#9）と Gap（#10）は `runner.py` manifest schema 拡張で同源実装。別タスクに分けず統合。

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| F0 | Janitor Follow-Ups（no-op diff/validation failure summary/token budget stop conditions） | **採用・最優先** | Codex 推奨。既存 TODO の消化。`codex-janitor-workflow.md` L66-72 に明記済みの未実装 4 条件を実装 |
| #9+#10 | Snapshot hash 付き構造化 evidence record | **採用** | manifest schema 拡張 + drift detection（scope: single-run 内のみ）。Gemini 警告でスコープ限定 |
| #13+#11 | Keep-open bias 明記 + Token strip（軽量追記） | **採用** | `refactor-loop.toml` + `codex-janitor-workflow.md` に 1 行追記 + `.codex/config.toml` wrapper stub |
| #7 | Tiered cron scheduling | **棄却** | `symphony-pilot.md` で "Not adopted" 明言。個人 dotfiles では on-demand/manual が適切（YAGNI） |
| #15 | Apply cap（50 fresh per checkpoint） | **棄却** | `improve-policy` resource_targets ≤ 2 + 3 要素同時変更禁止で個人 blast radius 十分 |
| #5 | codex app-server 全面採用 | **棄却** | 思想差。`codex-apps-pilot.md` deny-by-default 維持。両系統共存で OK |
| #2 | GitHub issue cron polling | **棄却** | YAGNI。個人 dotfiles なら on-demand で十分 |
| #8 | Sharded parallel review | **棄却** | 個人規模に不要。dispatch + read-only agents で十分 |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | Markdown evidence reports（#9 Already 強化可能） | **採用（#9+#10 に統合）** | Codex 批評で過小評価と指摘。runner.py manifest schema 拡張で対処 |
| S2 | Sharded parallel review | **強化不要** | `max_concurrent_agents=1` 意図的維持。個人規模に sharding 不要 |
| S3 | Token-stripped sandbox（#11） | **採用（軽量）** | #13+#11 bundle で wrapper stub 追記。実害なしのため最下位優先 |

---

## Plan

統合プラン: [`docs/plans/active/2026-04-29-symphony-clawsweeper-absorb-plan.md`](../plans/active/2026-04-29-symphony-clawsweeper-absorb-plan.md)

全体規模: **L 規模**（~9 files、~300 LOC）→ 新セッションで `/rpi` 推奨

### Task F0: Janitor Follow-Ups（既存 TODO 消化）【最優先】

- **Files**:
  - `tools/codex-janitor/runner.py`
  - `tools/codex-janitor/workflows/refactor-loop.toml`
  - `tools/codex-janitor/tests/` (該当テスト)
  - `docs/playbooks/codex-janitor-workflow.md`
- **Changes**: `codex-janitor-workflow.md` L66-72 の TODO 化されている 4 stop conditions を実装（no-op diff / validation failure summary / token budget超過 / session_lost 詳細化）
- **Size**: M

### Task #9+#10: Snapshot Hash 付き構造化 Evidence Record

- **Files**:
  - `tools/codex-janitor/runner.py`（snapshot 計算 + manifest schema 拡張）
  - `tools/codex-janitor/tests/` (snapshot tests)
  - `docs/playbooks/codex-janitor-workflow.md`（schema ドキュメント更新）
- **Changes**: `manifest.json` に `decision` / `evidence` / `snapshot_hash` フィールドを追加。drift detection は single-run 内のみ（cron tier 化禁止）。ClawSweeper 型 `records/<repo>/items/<n>.md` 構造化レコード出力
- **Size**: M
- **Note**: #9（Already 強化可能）と #10（Gap high）は runner.py 同実装源のため統合。Gemini 警告でスコープを single-run 内に限定

### Task #13+#11: Keep-Open Bias 明記 + Token Strip 軽量追記

- **Files**:
  - `tools/codex-janitor/workflows/refactor-loop.toml`（stop rule に keep-open bias 1 行追記）
  - `docs/playbooks/codex-janitor-workflow.md`（keep-open bias 方針 1 行追記）
  - `.codex/config.toml`（review profile に token strip wrapper stub）
  - `docs/playbooks/symphony-pilot.md`（keep-open bias 参照リンク追記）
- **Changes**: Conservative close threshold を `refactor-loop.toml` の stop rule に明示。Token strip は env 物理 strip wrapper stub を `.codex/config.toml` に追記（`profiles.review` read-only で実害なしのため最下位優先）
- **Size**: S
