---
title: "A harness for every task: dynamic workflows in Claude Code — absorb 分析"
date: 2026-06-03
source:
  title: "A harness for every task: dynamic workflows in Claude Code"
  authors: ["Thariq Shihipar", "Sid Bidasaria"]
  org: Anthropic
  type: official-blog
family: multi-agent-orchestration
status: drift-fix-only
adopted: 0
drift_fixes: 1
---

# dynamic workflows in Claude Code — absorb 分析

## Source Summary

Claude Code の新ツール **Workflow tool**（JS で `agent()`/`parallel()`/`pipeline()`/`phase()`/`log()` を呼び subagent を協調する harness を動的生成）の紹介記事。単一コンテキストの failure mode（agentic laziness / self-preferential bias / goal drift）を、独立コンテキストの subagent オーケストレーションで構造的に回避する。

**12 パターン**: classify-and-act / fan-out-and-synthesize / adversarial verification / generate-and-filter / tournament / loop-until-done / model routing / worktree isolation / token budget / quarantine / save-as-skill。

## Phase 1.5: Saturation Gate

- **family**: multi-agent-orchestration（Opus 4.8 新機能系、claude-code-tips の platform-drift トリガー）
- **N ≥ 3**: `2026-05-30-single-threaded-300-agents`, `2026-05-31-32-claude-code-hacks`, `2026-05-30-opus48-setup-guide` が直接 Workflow tool に言及。他に multi-agent-coordination / 30-subagents / CORAL 等。
- **採用率**: 直接言及3件で 2/3 ≈ 67%（≥20%）→ **PASS (warning)**
- **delta ≥ 2**: 過去3件は Workflow tool を「Already」「deliberate non-adopt」と**一括処理**しており、記事が説明する**個別パターンを個別照合した absorb は存在しない**。この棚卸し角度が新規論点。

## Phase 2: ギャップ分析（Explore 統合）

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | fan-out-and-synthesize | Already | research/dispatch skill |
| 2 | loop-until-done | Already | implement-loop/review-loop/completion-gate.py |
| 3 | classify-and-act / model routing | Already | agent-router.py + model-routing.md |
| 4 | worktree isolation | Already | spike/dispatch/best-of-n-guide |
| 5 | adversarial verification | Partial | security-reviewer に限定（agency-safety-framework.md の意図的設計） |
| 6 | tournament | Partial | improve-policy.md にあるが参照先 `tournament-mode.md` が**欠損（リンク切れ）** |
| 7 | token budget (explicit) | Partial | effort level の間接制御のみ。Workflow tool 側の機能 |
| 8 | quarantine | Partial | injection policy で代替。読取/実行エージェント分離は未形式化 |
| 9 | generate-and-filter | Partial | best-of-n-guide で近似 |
| 10 | Workflow tool JS harness (.workflow.js) | **Gap（意図的非採用）** | `2026-05-31-32-hacks` で deliberate non-adopt 記録済 |

**決定的な既存判断**: 32-hacks absorb で「Workflow tool は tool description が毎セッション自動注入 + opt-in gated のため harness reference 追加は redundant (KISS/YAGNI)」と意図的非採用済。記事の主眼（harness を作る）は却下済み領域。

## Phase 2.5: Refine

- **Codex**: `launch-worker.sh` の codex 呼び出しが不正な `-q` フラグでエラー終了（harness バグ、別途要修正）。skeptic 役は Opus が代行。
- **Gemini**: 周辺知識取得。ただし**具体採用事例（Vercel/Supabase/Shopify、開発速度3倍）と CVE 番号（CVE-2025-66479/66032）は検証困難で hallucination 懸念が強く採用根拠にしない**。定性的洞察のみ採用:
  - LangGraph（決定論グラフ）vs Workflow tool（自律オーケストレーション）の対比 — 妥当
  - quarantine のバイパス手法（検証エンジンと実行シェルの引数解釈差）— CVE番号は怪しいが脆弱性パターン自体は既知
  - Permission Drift（CLAUDE.md/.mcp.json のグローバル上書き）— dotfiles は protect-linter-config 等で既に対処

**統合判定**: Workflow tool 本体は deliberate non-adopt を維持。adversarial の security 限定・token の effort-level 間接制御は意図的設計のため拡大却下（over-engineering）。

## 採用結果

**新規 instruction 採用: 0 件**（全パターンが既存判断でカバー or 意図的非採用）。

## Validation-only Follow-up（drift 露出）

記事 framing（個別パターンの棚卸し）が、過去 absorb の一括「Already」処理で見逃された **improve-policy.md のリンク切れ**を露出させた。

| 対象ファイル | drift 内容 | 訂正 |
|-------------|-----------|------|
| `.config/claude/references/improve-policy.md:503` | 参照先 `skills/improve/instructions/tournament-mode.md` が欠損 | `references/best-of-n-guide.md` に付替（実体カバー先） |
| `.config/claude/agents/autoevolve-core.md:311` | 同上（同じ欠損ファイルを参照） | 同上 |

- `tournament-mode.md` は `docs/plans/completed/2026-03-19-autocontext-v2-integration.md` で「新規作成」予定だったが**未作成のまま放置**された孤児参照。
- `best-of-n-guide.md` が tournament の「複数戦略並列比較 + スコアリング/Pruning/Escalation/Pareto」を完全カバーするため付替が最小修正。
- 完了プラン履歴（`docs/plans/completed/`）の参照は記録として正しいため未変更。

## 教訓

- **Workflow tool は何度 absorb しても deliberate non-adopt**（tool description 自動注入 + opt-in gated）。次の dynamic-workflows 記事も saturation gate で同判定が妥当。
- 一括「Already」処理は**個別パターンの drift を隠す**。棚卸し角度の absorb は採用 0 でも drift 露出の価値がある。
- harness バグ発見: `launch-worker.sh --model codex` が `-q` フラグでエラー（要修正）。
