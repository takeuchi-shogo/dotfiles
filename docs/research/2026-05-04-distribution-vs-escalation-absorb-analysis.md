---
source: "Distribution vs Escalation: When to Use Subagents or Advisors"
date: 2026-05-02
absorbed: 2026-05-04
status: integrated
hallucination_risk: high  # advisor_20260301 tool / Anthropic blog April 9 / UC Berkeley advisor models 論文 が確認不可
related:
  - .config/claude/references/decision-tables-index.md
  - .config/claude/references/advisor-strategy.md
  - .config/claude/references/subagent-delegation-guide.md
  - .config/claude/references/review-consensus-policy.md
  - docs/research/2026-04-27-subagent-context-fork-absorb-analysis.md (Forked subagent N/A 確定)
---

# Distribution vs Escalation: When to Use Subagents or Advisors — Absorb Analysis

## 1. Source Summary

記事「Distribution vs Escalation: When to Use Subagents or Advisors」(2026-05-02) の主張:

- **1行差分**: "Subagents isolate context. Advisors unblock execution."
- **Subagent pattern (distribution)**: scoped task を独立 context window で実行、要約のみ親に返す。context 汚染を防ぎ、並列実行を可能にする
- **Advisor pattern (escalation)**: cheaper executor (Sonnet/Haiku) が hard call で stronger advisor (Opus) を tool として呼ぶ。判断が必要な岐路でのみ escalation する
- **Forked subagent** (`CLAUDE_CODE_FORK_SUBAGENT=1`): 親 transcript 継承、prompt cache 再利用。context cleanliness を犠牲にした最適化手法
- **Decision framework (3 質問)**:
  1. タスクを専門的なサブタスクに分割できるか？ → Yes → Subagent
  2. executor が行き詰まっているか、強い judgment が必要か？ → Yes → Advisor
  3. context 汚染を避ける必要があるか？ → Yes → Subagent
- **Composition モデル**: Sonnet executor + Opus advisor + Haiku subagent の3層構成
- **Agent teams (3rd shape)**: 簡単言及のみ、詳細は記事外
- **Anthropic eval 数値**: SWE-bench Multilingual +2.7pp / cost -11.9%（独立検証なし）
- **UC Berkeley "advisor models" 論文** (late 2025): advisor pattern の学術的裏付けとして言及

## 2. Hallucination Risk Caveat

Phase 2.5 の Gemini Google Search grounding で以下が **確認不可** だった:

- `advisor_20260301` という Anthropic Platform tool の実在性
- Anthropic 公式 blog "The advisor strategy" (April 9, 2026) の存在
- UC Berkeley "advisor models" 論文 (late 2025) の arxiv 該当
- 記事著者の身元（unknown blogger、ベンダーバイアス評価不可）
- SWE-bench +2.7pp / cost -11.9% の独立検証

**採用根拠は pattern level の主張のみ**。specific tool names / 数値は採用しない。

## 3. Gap Analysis (Phase 2 Pass 1 + Pass 2 + Phase 2.5 修正後)

修正後の判定テーブル:

| # | 手法 | 判定 | 根拠ファイル |
|---|---|---|---|
| 1 | Subagent delegation | exists | .config/claude/agents/ (33個), references/subagent-delegation-guide.md |
| 2 | Forked subagent (CLAUDE_CODE_FORK_SUBAGENT=1) | **N/A (intentional non-adoption, 再確認 2026-05-04)** | docs/research/2026-04-27-subagent-context-fork-absorb-analysis.md |
| 3 | Advisor concept | **partial (索引・workflow gate 接続が弱)** | references/advisor-strategy.md |
| 4 | Multi-model composition | exists | references/model-routing.md |
| 5 | Decision framework (subagent vs advisor) | **partial (drive 主体逆転の統合表なし)** | references/decision-tables-index.md, model-routing.md, advisor-strategy.md |
| 6 | Built-in subagents (Explore/Plan/general) | exists | Claude Code 組み込み + .config/claude/agents/ |
| 7 | Agent teams | partial (lifecycle registry coverage が weak) | references/team-harness-patterns.md, agent-invocation-logger.py |
| 8 | Nested delegation 禁止 | exists | .codex/AGENTS.md max_depth=1, subagent-delegation-guide.md |
| 9 | Skill abstraction over MCP | exists (enforcement, sys.exit(2)) | scripts/policy/mcp-audit.py |
| 10 | Advisor concept (review) | exists | code-reviewer + codex-reviewer + reviewer-capability-scores.md |

### Codex 批評による修正点（Phase 2.5 の出力を反映）

- **#2**: partial → N/A 格下げ。理由は context cleanliness 哲学と逆方向で、2026-04-27 の決定を再確認
- **#3**: API-level N/A は誤り。制約本体は存在、弱いのは索引と workflow gate への接続
- **#5**: 「Opus 主導 (model-routing) vs Executor 主導 (advisor)」の drive 主体逆転を統合する表が欠落
- **#7**: agent-invocation-logger.py で観測実装済み、欠けているのは /research, /loop の lifecycle registry coverage のみ
- **#9**: "soft block" は事実誤認、sys.exit(2) で enforcement

## 4. 採用された取り込み (Bundle A + B1 + B2)

### A1: decision-tables-index.md に Advisor 選択 + Drive 主体逆転表追加

- 変更箇所: `.config/claude/references/decision-tables-index.md` Routing 系 + 新規節
- 内容: Advisor 相談行を追加、Top-Down (Opus 主導) vs Bottom-Up (Executor 主導) の統合表

### A2: advisor-strategy.md に "one-shot per decision" 制約追加

- 変更箇所: `.config/claude/references/advisor-strategy.md` Role-Specific 制約 + 新規 §1 回性の意味
- 内容: iteration / debate per decision 1 回 / no debate 行を追加、One-Shot Per Decision サブ節

### A3: subagent-delegation-guide.md に Return Contract 追加

- 変更箇所: `.config/claude/references/subagent-delegation-guide.md` § Summary 層パターン直後
- 内容: Explore / 実装系 / Review / Advisor の役割別返却サイズ表 + Re-Flooding 防止 4 ルール

### A2 副次: review-consensus-policy.md に §9 Advisor Stop Signal との関係を追加

- 変更箇所: `.config/claude/references/review-consensus-policy.md` §8 直後に新規 §9
- 内容: Advisor response (plan/correction/stop) の Review verdict 相当 + 判定経路の独立性

### B1: absorb SKILL.md "soft block" → "enforcement" 修正

- 変更箇所: `.config/claude/skills/absorb/SKILL.md` line 295
- 内容: 事実誤認の修正（mcp-audit.py は sys.exit(2) で hard block）

### B2: 2026-04-27 fork-analysis に reaffirmed footnote 追加

- 変更箇所: `docs/research/2026-04-27-subagent-context-fork-absorb-analysis.md` frontmatter
- 内容: 2026-05-04 に N/A / intentional non-adoption を再確認した記録

## 5. 分離された取り込み (Bundle B3 — separate plan)

B3 (lifecycle registry coverage) は新規実装で 2-4h の L 規模のため、`docs/plans/2026-05-05-lifecycle-registry-coverage-plan.md` に分離して保存（Opus 本体が並行作成中）。

## 6. 不採択 / N/A

- **Forked subagent (CLAUDE_CODE_FORK_SUBAGENT=1)**: 意図的非採用（2026-04-27 決定 + 2026-05-04 再確認）。context cleanliness 哲学と逆方向
- **`advisor_20260301` API tool 直接対応**: Anthropic Platform 機能で local Claude Code session には適用不可。代わりに concept (中間相談プロトコル) のみ採用済み
- **SWE-bench +2.7pp / cost -11.9% を採用根拠とする**: 独立検証なし、ベンダーバイアス警戒

## 7. 残存課題 / Follow-up

- B3 (lifecycle registry coverage) の L plan 実行（別セッション推奨）
- Phase 2.5 Gemini が `research_advisor_pattern_verification.md` (memory 領域) に詳細を保存。継続検証時に参照

## 8. References

- 元記事: "Distribution vs Escalation: When to Use Subagents or Advisors" (2026-05-02, author unknown)
- 関連 absorb: docs/research/2026-04-27-subagent-context-fork-absorb-analysis.md (Forked subagent intentional non-adoption)
- 関連 references: advisor-strategy.md, decision-tables-index.md, subagent-delegation-guide.md, review-consensus-policy.md
- Phase 2.5 Codex 批評: 内部記録のみ
- Phase 2.5 Gemini 検証: memory/research_advisor_pattern_verification.md
