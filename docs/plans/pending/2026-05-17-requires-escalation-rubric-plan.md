---
status: pending
created: 2026-05-17
size: M
origin: /absorb of "Agent Governance Layers" (@techwith_ram, content farm pattern 8 件目)
analysis_report: docs/research/2026-05-17-agent-governance-layers-absorb-analysis.md
---

# Plan: High-stakes Agent に requires-escalation Rubric 導入

## Background

`/absorb` 記事「Agent Governance Layers」(by @techwith_ram) の Layer 1 (Intent Boundary) 主張に対する dotfiles の応答。

**Codex (gpt-5.5, 1m45s, 76k tokens) が Opus 初期判定を訂正:**

| 私の判定 | Codex 訂正 | 根拠 |
|---|---|---|
| T1 = "Already 強化可能" | **「Gap」(Already ではない)** | `agent-design-lessons.md:252` で「他 33 subagent の大半には体系化されていない」と明記。`skill-creator/SKILL.md:8,181` の "Do NOT use for" は scope creep 用で escalation rubric ではない。`security-reviewer.md:14` も CVE 級 escalation path 不在 |

**既存方針との整合**: `agent-design-lessons.md:259`「高 stakes agent に**限定して**導入」と一致 — 全 33 agent に展開せず high-stakes 4 体に絞る。

## Why (motivation)

- 4 体 (code-reviewer / security-reviewer / codex-reviewer / codex-plan-reviewer) は **BLOCK verdict** を出す品質ゲートだが、「BLOCK 時に何を escalate するか」の明文 rubric がない
- `security-reviewer` は CVE/auth/secrets を検知する read-only agent だが、検出後の人間 hand-off path が未定義
- `codex-plan-reviewer` は M/L 規模 plan 段階で破壊的変更を見つけるが、escalation target (architect or user) が未指定
- ad-hoc な escalation (今 Claude が判断) は再現性が低く、subagent によって挙動がブレる

## Scope

### In-scope (実装対象: 6 ファイル)

| # | ファイル | 変更内容 |
|---|---|---|
| 1 | `.config/claude/agents/security-reviewer.md` | requires-escalation セクション追加 (CVE/secrets/auth bypass) |
| 2 | `.config/claude/agents/code-reviewer.md` | requires-escalation セクション追加 (BLOCK verdict 時の hand-off) |
| 3 | `.config/claude/agents/codex-reviewer.md` | requires-escalation セクション追加 (Verdict 未出力 terminate) |
| 4 | `.config/claude/agents/codex-plan-reviewer.md` | requires-escalation セクション追加 (Plan 段階 breaking change) |
| 5 | `.config/claude/skills/skill-creator/SKILL.md` | agent 作成 rubric に requires-escalation 必須化 (high-stakes 限定) |
| 6 | `.config/claude/references/agent-design-lessons.md` | rubric specification セクション追記 (line 252 周辺更新) |

### Out-of-scope

- **Archived agents** (autoevolve-core / migration-guard / golden-cleanup / triage-router): 再有効化時に同 rubric を適用する旨を `agent-design-lessons.md` にメモのみ
- **Tier 2 候補 (今サイクル除外、30 日後 friction 評価で含める判断)**: `debugger.md` (Write/Edit + memory:user + permissionMode: plan で事故時影響大), `test-engineer.md` (Write/Edit で test infrastructure 変更可能), `simplify` skill (semantic rewrite で意味的破壊リスク)
- **全 33 agent への展開**: high-stakes 限定が Codex 推奨方針
- **静的 lint hook** (rubric 不在を warn): Codex の T2 代替案だが、本 plan の Step 4 で別 plan 候補として記録 (今回は実装せず)
- **L2 強化 (tool-scope-enforcer の warn → block 昇格)**: 副次採用候補、別 spec
- **Meta-permission 整理 (誰が governance を変更できるか)**: 副次採用候補、別 spec
- **Prompt-only enforcement のリスク**: 本 plan の rubric は subagent prompt に書くだけで、参照する hook は存在しない (Codex 指摘)。「効いているつもり」リスクあり。30 日後 friction 評価で `## Requires Escalation` セクションを参照する lint hook を別 plan で起票検討

## Rubric Template (要決定)

agent.md に追加する形式の候補:

### Option A: Markdown section (推奨)

```markdown
## Requires Escalation

| Condition | Severity | Action | Hand-off Target |
|---|---|---|---|
| CVE pattern match (CVE-YYYY-NNNNN format) | critical | pause review + write finding to security log | user (immediate) |
| Hard-coded credential detected (api key/token/password) | critical | pause + redact in finding | user (immediate) |
| Authentication bypass logic detected | critical | block PR + flag | security-aware reviewer |
```

### Option B: YAML in frontmatter

```yaml
escalation_required:
  - condition: "CVE pattern match"
    severity: critical
    action: pause_with_security_finding
    target: user
```

**判断軸**: Option A は人間可読性高、Option B は機械処理可能。dotfiles の harness で機械処理する hook が現状ないので **Option A 推奨**。Step 1 で確定する。

## Implementation Steps

### Step 1: 責務分離表 + Rubric format 確定 (Opus, 30 min)

**Step 1.0 (前置)**: 「scope boundary / reject rule / escalation」の **責務分離表** を先に作成 (Pre-mortem #4 重複防止):

| 領域 | 既存セクション | 用途 | 例 |
|---|---|---|---|
| Scope boundary | `description` + `tools:` | この agent は何の責務か | "security-reviewer: deep security analysis" |
| Reject rule | Skill description `Do NOT use for:` | この agent を **使うべきでないシナリオ** (scope creep 防止) | "Do NOT use for: 単純な review (use code-reviewer)" |
| **Escalation** | **新規 `## Requires Escalation`** | この agent 実行中に **不確実時/critical 時の hand-off 手順** | "CVE pattern match → pause + user notify" |

`Reject rule` と `Escalation` は完全に直交 (前者=入口判定、後者=実行中判定)。重複させない。

**Step 1.1**: Option A (Markdown table) vs B (YAML frontmatter) の選択。dotfiles に機械処理 hook が現状ないため **Option A 推奨**。

**Step 1.2**: security-reviewer 用に **rubric 1 件を試作**して形式確認。次の 6 カラム必須:
- `Condition / Detector / Evidence / Severity / Action / Target`
- `Detector` は `regex | verdict | command exit/log | file pattern | semantic-with-required-evidence` のいずれか
- `Evidence` は Detector の根拠 (regex なら pattern、verdict なら出力 token、command なら exit code、semantic なら required citation 形式)

**Step 1.3**: 他 3 agent に展開可能か検証 (template generalize)。

### Step 2: 4 agent への rubric 追加 (Opus, 1-1.5h)

各 agent.md の末尾 (existing Operating Mode セクションの後) に `## Requires Escalation` を追加:

- **security-reviewer.md**: CVE / hard-coded credential / auth bypass / privilege escalation / SSRF / SQL injection 等
- **code-reviewer.md**: BLOCK verdict 発動条件、3 サイクル PASS せず時、Layer 0 (test) 未実行時
- **codex-reviewer.md**: Codex CLI が verdict 出力前に terminate (silent stall)、Capability score 1/5 以下、矛盾 finding 連発
- **codex-plan-reviewer.md**: Plan に breaking change 検出、AC が測定不能、reversible decision の閾値が恣意的

### Step 3: 仕様文書追記 (Opus, 30 min)

- **skill-creator/SKILL.md**: agent 作成チェックリストに「high-stakes か?」判定 + Yes なら rubric 必須を追記
- **agent-design-lessons.md**: line 252 の「他 33 subagent の大半には体系化されていない」記述を更新し、rubric specification セクションを新設

### Step 4: 静的 lint hook (別 plan 候補、本 plan では実装しない)

- 候補: `scripts/policy/agent-rubric-check.py` で high-stakes agent に rubric セクション存在を確認
- Codex の T2 (regression test) 代替案だが、本 plan のスコープ外とする
- 30 日後に friction-events で「rubric にあったが踏んだ」事案があれば別 plan 起票

### Step 5: Codex Review Gate (Opus + Sonnet 並列, 20 min)

- 6 ファイル変更 → S/M 規模 → code-reviewer + codex-reviewer 並列
- 期待: PASS or NEEDS_FIX (修正サイクル 1-2 回)

### Step 6: Verify (Opus, 20 min)

- 各 rubric の condition が **objective に判定可能** か
- `## Requires Escalation` セクションが consistent な見出しレベル
- Markdown lint (mdl) を実行可能なら通す

## Reversible Decisions

参照: `references/reversible-decisions.md`

| 決定 | 撤退条件 |
|---|---|
| rubric format (Option A vs B) | **14 日間** 使ってフィードバックがあれば変更 (rubric は発火頻度低いため 7 日は false negative 観測不可) |
| 4 agent への限定 | 30 日後の friction-events で「**対象外 agent で escalation すべき事案が出た**」1 件以上 → 対象拡大 (Tier 2 候補: `debugger.md` (Write/Edit + memory:user + permissionMode: plan), `test-engineer.md` (Write/Edit), `simplify` skill (semantic rewrite), archived `golden-cleanup` (再有効化時)) |
| Markdown vs YAML | 機械処理 hook 化が必要になった時点で YAML 移行 |

## Pre-mortem

参照: `references/pre-mortem-checklist.md`

| # | 失敗モード | 検知方法 | 対策 |
|---|---|---|---|
| 1 | rubric が actionable でない (曖昧条件 "重要な変更時" 等) | Step 6 verify で reviewer が「これでどう判定するの?」と質問 | 各 condition は具体的 (CVE / BLOCK verdict / 数値閾値) |
| 2 | rubric の維持コスト > 効果 | 30 日後 friction-events に「rubric 起因の作業遅延」事案 | 4 agent 限定 + 拡大は friction 検証後のみ |
| 3 | AutoEvolve retire と同じ false-positive 発生 | 自動修正 hook を実装した瞬間に再発リスク | **自動修正は実装しない** (Codex の T2 reject 方針) |
| 4 | rubric が Skill "Do NOT use for:" と重複・矛盾 | Step 3 で agent-design-lessons.md に書き起こす時に衝突発見 | 用途分離を明示: `Do NOT use for` = scope creep 防止、`Requires Escalation` = 不確実時の手順 |
| 5 | high-stakes 4 体に過剰絞り込み (本来 5-6 体必要) | 30 日後に escalation 必須事案が他 agent で発覚 | Archived 4 体 + design-reviewer/test-engineer も評価対象に再追加 |

## Acceptance Criteria

- [ ] **AC1**: 4 high-stakes agent.md の指定セクションに requires-escalation rubric が存在 (Markdown table 形式、**6 カラム必須**: `Condition / Detector / Evidence / Severity / Action / Target`)
- [ ] **AC2**: skill-creator/SKILL.md の agent 作成ガイドに「high-stakes 判定 → rubric 必須」が明文化
- [ ] **AC3**: agent-design-lessons.md の line 252 周辺記述が更新され、rubric specification セクション (見出し含む) が追加。Step 1.0 の責務分離表 (Scope boundary / Reject rule / Escalation の直交) も含める
- [ ] **AC4**: Codex Review Gate PASS (codex-reviewer + code-reviewer 並列、NEEDS_FIX なら 2 回まで修正サイクル)
- [ ] **AC5**: 各 rubric の `Detector` カラムが `regex | verdict | command exit/log | file pattern | semantic-with-required-evidence` のいずれかに **分類されている** (主観的判定なし)。`Evidence` カラムが Detector の根拠を具体的に記述 (regex なら pattern、verdict なら出力 token、command なら exit code、semantic なら required citation 形式)

## Estimated Effort

| Step | Effort |
|---|---|
| Step 1 (責務分離表 + format 確定 + 試作) | 30 min |
| Step 2 (4 agent rubric) | 1-1.5h |
| Step 3 (仕様文書追記) | 30 min |
| Step 5 (Codex Review Gate) | 20 min (+ 修正サイクル) |
| Step 6 (Verify) | 20 min |
| **合計** | **2.5-3h** |

## Chain (副次 plan / spec 候補)

本 plan 完了後、別タスクで起票:

1. `docs/specs/2026-05-XX-tool-scope-enforcer-block-spec.md` — L2 強化 (`tool-scope-enforcer.py:109` warn → block 昇格)
2. `docs/specs/2026-05-XX-meta-permission-governance-spec.md` — Codex 指摘「誰が governance を変更できるか」
3. `docs/plans/2026-05-XX-agent-rubric-lint-hook-plan.md` — Step 4 の静的 lint hook (本 plan 30 日後 friction 確認後に検討)

## Origin Citation

- 記事: https://(URL なし、Telegram/Twitter content farm 由来)
- /absorb 分析: `docs/research/2026-05-17-agent-governance-layers-absorb-analysis.md`
- Codex Phase 2.5 批評: `/tmp/governance-codex-result.md` (302KB, session 019e32ef-27b9-7901-a93f-9890df91373c)
- Codex Plan Gate 批評: `/tmp/governance-plan-gate-result.md` (136KB, 1m22s, 117k tokens) — NEEDS_FIX → 修正済 (AC1/AC5 6 カラム化、Step 1 責務分離表、パス修正 `.claude/` → `.config/claude/`、Tier 2 候補追記、Reversible decisions 14 日化 + 拡大条件文言変更、Prompt-only リスク明示)
- 既存方針: `references/agent-design-lessons.md:252-280`
