---
source: "How Karpathy's CLAUDE.md made me $147,000 (anonymous content-farm article, Discord-screenshot 起点)"
date: 2026-06-07
status: skip + validation-only-follow-up
verdict: "SATURATED-pure-rehash (delta=0, 採用0) → ultracode validation audit で既存 harness drift 15 件確定"
family: claude-code-tips / CLAUDE.md best-practices (N=15+)
adopted_tasks: []
validation_findings_confirmed: 15
validation_findings_rejected: 8
related:
  - docs/research/2026-05-10-12-rule-claude-md-absorb-analysis.md
  - memory/reference_karpathy_llm_coding.md
  - docs/research/2026-05-22-khairallah-40-features-absorb-analysis.md
---

# Karpathy 24-rule CLAUDE.md ($147,000 記事) absorb 分析

## Source Summary

**主張**: Karpathy 4 ルール + 7 (kill noise) + 7 (stop unauthorized) + 6 (memory/stack) = 21 ルール CLAUDE.md + MEMORY.md/ERRORS.md の3ファイルで coding accuracy 65%→94%、週 18 時間 / 年 $147,000 の cleanup コストを削減。

**著者バイアス**: 匿名、Discord screenshot 起点、$147,000 / 65%→94% / 18h-week は全て出典なし fake precision。前回 12-rule 記事 (2026-05-10) で確立した content-farm pattern (匿名 + fake precision + engagement bait) と同型。

## Phase 1.5 Saturation Gate: SATURATED-pure-rehash (delta=0)

**Family**: claude-code-tips / CLAUDE.md best-practices、N=15+ (Karpathy 系だけで `reference_karpathy_llm_coding.md` + 10 件超の docs/research)。採用率 <20% (N-rule CLAUDE.md template 系は前回 Reject)。

**per-method 照合台帳**: 24 ルール + メモリアーキテクチャの全手法を既存 prior に1対1で名指し照合。delta_methods = ∅ (novel 0 / ambiguous 0 / N/A 1)。

| 手法群 | matched_prior |
|--------|---------------|
| R1-R4 Karpathy 4 rules | `reference_karpathy_llm_coding.md:11-20` (4大失敗パターン) + project CLAUDE.md "Think before coding"/"Editing rules"/"Sanity check" |
| R5-R8 kill-noise/uncertainty | `user_ai_collaboration.md` "冗長な説明NG" + global honesty 原則 (commit eb73573) + output-mode skill |
| R9-R11 profile/voice | user profile memories ×4 + /onboarding /profile-drip (R11 voice-lock のみ N/A: コーディング harness 対象外) |
| R12-R18 scope/confirm | global system prompt (hard-to-reverse/destructive/external 確認) + project CLAUDE.md "trace to request" + lefthook gate |
| R19-R24 memory/stack | 既存メモリ3層 + /checkpoint /daily-report + failure-escalation + /think + model-routing |
| メモリアーキテクチャ (200行cap/自動ロード/on-demand) | MEMORY.md(索引) + references/ on-demand + `feedback_memory_style.md` + `_index.md` 分離 (**dotfiles の方が高度**) |

→ 全て rehash。記事から新規採用される手法は**ゼロ**。前回 12-rule で既に「N-rule 全採用=Reject (Pruning-First 違反 + ceiling 抵触)」と結論済みのパターンの煽り版。**skip 確定**。

## Validation-only Follow-up (ultracode 24原則 validation audit)

記事の 24 原則を adversarial lens として既存 harness に適用 (delta=0 なので「採用」ではなく「品質監査」)。6 lens 並列 find → 各 finding を skeptic agent で adversarial verify (default false / covered-elsewhere チェック)。**前回 12-rule で fail-loud lens が completion-gate.py の silent success を発見した手口の再現**。

**Workflow**: 29 agents / confirmed=15, rejected=8。lens 健全性: memory-loop=**broken**、他5 lens=drift。

### Tier 1 — 実機構の欠陥 (NO-OP / dead pipeline、S-size クリーン修正)

| # | finding | file:line | 実害 | 修正 |
|---|---------|-----------|------|------|
| SC-1 | change-surface-advisor.py が存在しない `TOOL_INPUT` env var を読む → harness 編集 advisory が**一度も発火しない** | `scripts/runtime/change-surface-advisor.py:130` | 2026-04-07 から dead な NO-OP hook (settings.json に wire 済) | stdin `load_hook_input()` 化 + `run_hook(fail_closed=False)` |
| SC-2 | skill-suggest.py が同じ `TOOL_INPUT` 欠陥 → 編集時の skill suggestion が発火しない | `scripts/runtime/skill-suggest.py:87` | 同上、PATH_MAP/SKILL_MAP 提案が死亡 | 同上 |
| BL-2 | measure-instruction-budget.py が `~/.claude/references/` (非存在) を読む → references 常時 "0 tokens" の silent undercount (~162 files) | `scripts/policy/measure-instruction-budget.py:195` | symlink gap (MEMORY.md:11 記載済) | `hook_utils.get_references_dir()` で1行修正 |
| CG-4 | `--no-verify` deny が `git commit -n` (公式短縮形) と末尾配置を bypass。CLAUDE.md:61 の "lefthook で強制" は論理破綻 (lefthook 自身の bypass フラグを lefthook が強制不可、実 enforcer は deny ルール) | `settings.json:98` / `CLAUDE.md:61` | --no-verify gate に bypass 経路 | deny に `git commit -n *` / `* --no-verify *` 追加 + CLAUDE.md 根拠訂正 |

### Tier 2 — orphan / fate 判断 (Build-to-Delete)

| # | finding | 判断要 |
|---|---------|--------|
| BL-3 | measure-instruction-budget.py が orphan (どの hook/cron/task にも wire されず)、total=12437 tokens (自身の閾値 6000 の2x、skill_descriptions=10066/121 skills) を誰も消費しない。system-prompt-policy.md:25 の "検出する" 主張が decorative | wire (weekly cron) or retire。先に BL-2 修正で数値を信頼可能に |
| ML-1 | run-learned-promote.sh (acde494 で実装済) が `launchd-install.sh` TASKS から漏れ、148 候補 pending・promoted-ledger 0 bytes・未スケジュール | **設計判断**: sonicgarden で unattended は YAGNI 撤退し human-gated 化済 (rejected ML-2)。run-learned-promote.sh は PR-gated 昇格 = 人間 in-loop なので scheduling は設計と整合。ただし `2026-06-06-plan-status-close-gate-plan.md:27` で既に tracked gap。ユーザー意図確認後に1行追加 |

### Tier 3 — stale-fact / doc drift (安価な correctness 修正)

| # | finding | file:line |
|---|---------|-----------|
| CG-3 | careful SKILL.md description "Blocks ... via PreToolUse guard" 誇張 (実体は advisory prompt、DROP TABLE/kubectl delete は完全未ガード) | `skills/careful/SKILL.md:5` |
| SF-2 | README/constraints が orphan な pre-commit-check.js を "施行中の secret ゲート" と記述 (実体は Rust binary) | `README.md:186,208` + `constraints-library.md:92` |
| SC-3 | tool-scope-enforcer.py が "active PreToolUse hook" と文書化されるが settings.json に未配線 | `references/tool-scoping-guide.md:39` |
| ML-4 | MEMORY.md stale fact ×3: "status フィールド不在"(実在=promotion_status) / "error-to-codex は key hook"(削除済) / "配線復旧は別タスク"(script 完成済) | `MEMORY.md` 改善ループ節 + hooks 行 |
| PF-1 | MEMORY.md:5 memory スコープ件数 user(17)/project(14)/local(1) が実測 (73 detail / feedback31/reference13/project12/user7/local0) と全面 drift | `MEMORY.md:5` |
| PF-3 | MEMORY.md:83,88 が 3x `../` で非存在パス `.claude/dotfiles/` に解決 (4x が正、line 92/159 と不統一) | `MEMORY.md:83,88` |
| PF-4 | user_tech_stack.md エディタ stack が Zed 採用 (config 管理下) を反映せず Cursor/Neovim のまま stale | `user_tech_stack.md:3,18-19` (要 1 問確認) |
| BL-1 | global CLAUDE.md 8436B = 4096B budget の206% + ADR-0007:84 baseline stale ("94 行...マイグレ不要")。ただし verify で LOW: 150行 PRIMARY 上限内 + 日本語 byte proxy の既知 false-alarm | `.config/claude/CLAUDE.md` / `ADR-0007:84` |
| CG-1 | git mutation 前 branch 確認が instruction 止まり (PR#60 amend 事故対策が未 mechanism 化)。verify で LOW: 事故は recoverable + 主因 daemon は無効化済 | `CLAUDE.md` project memory |

### Rejected (adversarial verify が棄却した 8 件 — 監査品質の証跡)

- **ML-2** 旧 promote-patterns.py cron 停止: 意図的 YAGNI 撤退 (sonicgarden analysis)、human-gated 設計。defect ではない
- **ML-3** errors.jsonl appender 不在: session-learner.py:539 が live appender、凍結は upstream producer gap (improve-policy.md:11 記載済)
- **ML-5** learned-nudge.sh 未スケジュール: cosmetic notify helper、実 drain は run-learned-promote.sh (ML-1 と重複)
- **BL-4** MEMORY.md 改善ループ節 re-bloat: claudemd-size-check 閾値以下 + memory-pruning.md が "残す (thinking)" と保護
- **SF-1** commit secret gate fail-open: lefthook publicity-review が fail-closed で独立 enforce (superset patterns)
- **SF-3** JS→Rust 移行で password 検出脱落: lefthook 側で intentional warn-only (doc false-positive 配慮)
- **PF-2** local memory scope phantom: scope/sensitivity tier と content type の直交軸を混同、local は意図的機密 tier
- **CG-2** 保護ブランチ直 commit gate dead: 単一ユーザーは master 直 commit が intended workflow、block は逆に破壊

## 教訓

1. **delta=0 でも ultracode validation は実りがある**: 記事の 24 原則を物差しに、harness の **2ヶ月死んでいた NO-OP hook 2件 (SC-1/2)**、symlink undercount (BL-2)、--no-verify bypass (CG-4) を file:line で発見。「採用0 ≠ 終了」family 教訓の最大級の実証。
2. **adversarial verify が監査の信頼性を担保**: 8件を covered-elsewhere で棄却、HIGH 候補の多くを honest に LOW へ降格。skeptic default が「煽り記事の lens で過剰検出する」リスクを抑制。
3. **memory-loop lens が唯一 broken 判定**: learned 昇格ループは「script 完成・launchd 未登録」が実態 (MEMORY.md の "配線復旧は別タスク" は半 stale)。ただし unattended 化は YAGNI 撤退済みなので、scheduling は設計判断としてユーザー確認を要する。
