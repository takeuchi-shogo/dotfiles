---
title: "Agent Governance Layers (absorb)"
date: 2026-05-17
source_type: article
source_author: "@techwith_ram (Twitter/Telegram, unverifiable)"
source_url: "(none; content pasted directly)"
absorb_verdict: "Partial (content farm pattern 8件目。T1 requires-escalation rubric のみ採用、副次 2 件を別 spec へ)"
adopted_tasks: [T1]
deferred_tasks: [L2-warn-to-block, meta-permission]
rejected_main_claims:
  - ".claude/governance/ 一元管理構造"
  - "write-only audit trail"
  - "confidence threshold escalation"
  - "regression test 自動化"
---

## Section 1: 記事の主張 (Phase 1 構造化抽出)

### 核心主張

**Governance が bottleneck**: AI agent 失敗の大半は「権限境界未定義」が原因。Trust が先ではなく、5 層 Control Plane が Trust を生む。

### 5 Layer Control Plane

| Layer | 名称 | 手法 |
|---|---|---|
| L1 | Intent Boundary | `mandate.md` で in-scope / out-of-scope / requires-escalation を明文化 |
| L2 | Permission Model | `permissions.json` で least privilege + scoped token + write 監査 |
| L3 | Audit Trail | `audit/*.jsonl` 構造化ログ、agent から write-only (read 不可) |
| L4 | Escalation Protocol | `escalation.md` で trigger / path / format 事前定義、不確実時 wait |
| L5 | Feedback Loop | `reviews/*.md` で review → update → regression test、narrow → 実績で expand |

**推奨ディレクトリ**: `.claude/governance/{mandate.md, permissions.json, audit/, escalation.md, reviews/}` 一元管理

### 著者バイアス警戒

- 定量データなし、著者個人経験談のみ
- @techwith_ram は X account verify 不可
- 自作図・煽り CTA (Follow @techwith_ram)
- content farm pattern **8 件目** (Boris / Three-Model Stack / Cyril / 12-rule / zodchixquant / 0xfene / Nav Toor / Khairallah に続く)

---

## Section 2: Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | dotfiles 対応状況 |
|---|------|------|------------------|
| L1 | requires-escalation 明文セクション | **Gap** | agents/*.md frontmatter (description + tools:) + Skill "Do NOT use for:" は scope creep 用。requires-escalation 体系化は agent-design-lessons.md:252 で「他 33 subagent の大半には未実装」と明記 |
| L2 | Permission Model (least privilege) | **Partial** | settings.json allow/deny (84+/127) + mcp-audit.py + tool-scope-enforcer.py + subagent tools: フィールド = 4 重防御。ただし tool-scope-enforcer.py:109 は warn-only (block しない) |
| L3 | Audit Trail (write-only) | **Partial (Reject)** | agent-memory/learnings/*.jsonl + agent-invocations.jsonl あり。write-only 設計は session-learner.py の retrospective と対立 |
| L4 | Escalation Protocol | **Partial** | AskUserQuestion + advisor-strategy.md + completion-gate.py + cascade-routing.md あり。confidence threshold は handoff-template.md と対立 |
| L5 | Feedback Loop + regression test | **Partial** | friction-weekly-digest.sh (集計のみ) あり。AutoEvolve 2026-05-03 retire 済。regression test 未実装 |
| (新) | Meta-permission (誰が governance を変更できるか) | **Gap** | Codex 指摘。既存 surface に薄く足す話だが体系化なし |

---

## Section 3: Codex 批評後の修正済みテーブル (Phase 2.5)

**Codex 実行**: gpt-5.5, 1m45s, 76,563 tokens, cmux Worker 経由 (Skill codex:rescue は permission storm で NG)

### Codex が Opus 判定を 3 点訂正

| 訂正点 | Opus 判定 | Codex 訂正 | 根拠 (file:line) |
|--------|-----------|------------|-----------------|
| L1 requires-escalation | "Already 強化可能" | **「Already ではない、明確な Gap」** | `agent-design-lessons.md:252`「他 33 subagent の大半には体系化されていない」/ `skill-creator/SKILL.md:8,181` は scope creep 用 / `security-reviewer.md:14` も CVE 級 escalation path 不在 |
| L5 regression test | "強化可能 (慎重評価)" | **「Reject」** | `improve-policy.md:1-11,182-190`「/improve は false-positive と認知負荷で retire 済」。代替: T1 rubric の静的 lint / advisory まで |
| L2 評価 | "4 重防御 → 強化不要" | **「過大評価」** | `tool-scope-enforcer.py:109` は out-of-scope を **warn するだけで block しない** |

### Codex の追加見落とし指摘

- **Meta-permission gap**: 「誰が governance を変更できるか」が欠落。既存 surface に薄く足す話

---

## Section 4: Integration Decisions

### Gap / Partial 項目

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| T1 | high-stakes agents への requires-escalation rubric 追加 | **採用 (最優先)** | 5-8 体の high-stakes agent 限定。agent-design-lessons.md:252 + security-reviewer.md:14 + skill-creator/SKILL.md:8 に実害確認 |
| T2 | L5 regression test | **Reject** | improve-policy.md:1-11 — /improve retire 失敗条件を踏む再導入リスク |
| T3 | L2 warn → block 昇格 | **副次採用候補 (別 spec)** | tool-scope-enforcer.py:109 の enforcement 昇格。Pruning-First で本 absorb には含めない |
| T4 | Meta-permission 整理 | **副次採用候補 (別 spec)** | 誰が governance を変更できるか。本 absorb には含めない |
| T5 | .claude/governance/ 一元化 | **Reject** | 分散管理が現行 dotfiles の意図。移行コスト > 効果 |
| T6 | write-only audit trail | **Reject** | session-learner.py の retrospective 機能と直接対立 |
| T7 | confidence threshold escalation | **Reject** | handoff-template.md:* と対立。既存設計を壊す |

---

## Section 5: 採用タスク

### T1: high-stakes agents への requires-escalation rubric 追加 (L 規模)

- **Plan ファイル**: `docs/plans/2026-05-17-requires-escalation-rubric-plan.md`
- **対象 agent (5-8 体)**:
  - `agents/security-reviewer.md` — CVE 級判断の escalation path 不在 (`security-reviewer.md:14`)
  - `agents/autonomous.md` — 長時間自律実行、境界なし
  - `agents/codex-reviewer.md` — code merge 判断に関与
  - `agents/agent-router.md` — routing 誤判断が全体に波及
  - `agents/completion-gate.md` — completion pass/block の最終判断
- **追加セクション例**:
  ```
  ## Escalation Triggers
  - MUST escalate: [具体条件リスト]
  - MAY proceed: [具体条件リスト]
  - NEVER do: [禁止事項]
  ```
- **追加先**:
  - `agent-design-lessons.md` に requires-escalation rubric ガイドライン
  - `skill-creator/SKILL.md` の high-stakes agent チェックリストに追記
- **根拠**: `agent-design-lessons.md:252` で「他 33 subagent の大半には体系化されていない」と明記

---

## Section 6: 棄却タスクと理由

| 棄却項目 | 理由 |
|---------|------|
| .claude/governance/ 一元化 | 分散管理が意図。symlink 構造 (dotfiles/.config/claude/) と相性が悪い |
| write-only audit trail | session-learner.py の retrospective と対立。自己観察が阻害される |
| confidence threshold escalation | handoff-template.md と対立、既存設計を壊す |
| L5 regression test 自動化 | improve-policy.md:1-11,182-190 で /improve retire 済。同じ失敗条件を踏む |

---

## Section 7: 教訓 (Lessons learned)

1. **content farm pattern 8 件目 (@techwith_ram)**: 匿名・自作図・出典なし・煽り CTA。Boris / Three-Model Stack / Cyril / 12-rule / zodchixquant / 0xfene / Nav Toor / Khairallah に続く。

2. **Codex 批評 (76k token deep reasoning) が 3 点訂正**: Sonnet 探索の "Already 強化可能" 判定が「明確な Gap」に昇格。file:line citation 付き根拠が信頼性を担保。cmux Worker 経由の Codex 批評は ROI 高い。

3. **`tool-scope-enforcer.py:109` は warn-only**: 4 重防御と見えていた L2 の実態は「notify して通す」設計。「4 重防御 = 強化不要」は過大評価だった。

4. **`skill-creator/SKILL.md` の "Do NOT use for:" は scope creep 用であり requires-escalation rubric ではない**: 用途が別物。既存記述を「既に対応」と読み誤るリスクがあった。

5. **Skill codex:rescue は使わない**: Permission Storm + Silent Stall + 6 段ホップ抽象。`feedback_codex_casual_use.md` に追記済 (launch-worker.sh cmux/codex 仕様変更未追従で部分的に rot)。

---

## Section 8: 関連参照

- `agents/security-reviewer.md:14` — CVE 級 escalation path 不在の実害
- `agent-design-lessons.md:252` — 33 subagent に requires-escalation 未体系化の明記
- `skill-creator/SKILL.md:8,181` — "Do NOT use for:" は scope creep 用 (escalation rubric ではない)
- `tool-scope-enforcer.py:109` — warn-only block しない (L2 過大評価の根拠)
- `improve-policy.md:1-11,182-190` — /improve retire 経緯 (regression test 棄却根拠)
- `references/improve-policy.md` — Pruning-First 方針
- `docs/plans/2026-05-17-requires-escalation-rubric-plan.md` — T1 実装 plan (並行作成)
- 過去の content farm pattern absorb:
  - `docs/research/2026-04-30-boris-30tips-absorb-analysis.md`
  - `docs/research/2026-05-10-12-rule-claude-md-absorb-analysis.md`
  - `docs/research/2026-05-10-zodchixquant-15-settings-absorb-analysis.md`
  - `docs/research/2026-05-13-9-overnight-agents-absorb-analysis.md`
  - `docs/research/2026-05-14-claude-code-routines-absorb-analysis.md`
