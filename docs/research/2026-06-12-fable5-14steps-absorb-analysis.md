---
title: "Build self-improving agent system with Fable 5 in 14 steps (0xCodez) — absorb analysis"
date: 2026-06-12
source:
  title: "Build self-improving agent system with Fable 5 in 14 steps : loops, dynamic workflows, routines"
  author: 0xCodez (movez.substack.com)
  url: https://x.com/0xCodez/status/2065089060104720776
  type: x-post
status: implemented
family: multi-agent-orchestration / self-evolving (cross-family)
adopted: 3
---

## Source Summary

**主張**: Fable 5 (Mythos-class, 2026-06-09 launch) は単独モデルではなく、自己改善ループ (state管理・skills・vision検証・eval) を備えたシステムの基盤。システム側 (環境) を設計することで days-long 自律実行が compound する。

**手法 14 ステップ**:
1. Fable=Mythos-class positioning
2. self-improving=環境側複合化 (重み更新ではない)
3. 4層スタック Primitives→Orchestration→Memory→Self-improvement
4. コストルーティング Fable=orch/Opus=hard subtask/Sonnet=worker/Haiku=grader
5. `/goal` vs Outcomes
6. verifier subagent > self-critique
7. Dynamic Workflows fan-out/adversarial/loop-until-done
8. worktree maker/verifier 分離
9. Routines schedule/API/GitHub trigger
10. 5段階メモリ進行 Fail→Investigate→Verify→Distill→Consult
11. STATE.md 構造 Verified facts/General rules/Open failures/Last session
12. skill への教訓書き戻し+eval suite
13. vision 自己検証
14. Mythos 安全境界 classifier block→Opus 4.8 fallback

---

## Fact-check (grounding)

**VERIFIED** (公式 docs):

- `/goal` (code.claude.com/docs/en/goal, session-scoped prompt-based Stop hook wrapper, Haiku evaluator 毎ターン, v2.1.139+)
- Outcomes (platform.claude.com/docs/en/managed-agents/define-outcomes, rubric + max_iterations default 3 max 20)
- Claude Managed Agents (2026-04-08 公開ベータ)
- Routines (2026-04-14 research preview, schedule/API/GitHub trigger)
- Fable 5 domain classifier の server-side Opus 4.8 自動 fallback (platform.claude.com/cookbook/fable-5-fallback-billing-guide, billing は cache hit 扱い)
- Prithvi Rajasekaran の harness design 記事 (anthropic.com/engineering/harness-design-long-running-apps, 2026-03-24)
- Dynamic Workflows + isolation:worktree (本 session の harness で直接観測)

**UNVERIFIED**:

- 「Parameter Golf」実験名・~6×改善値 (第三者ブログのみ、ベンチ数値を採用根拠にしない原則を適用)
- 「Continual Learning Bench 1.0」・73% vs 17% 数値 (第三者ブログのみ)
- "Rather than directly prompting..." の verbatim quote (出典不明)
- 319-page system card controversy

**grounding 代替**: Gemini CLI timeout + API quota 枯渇 (429) で 2/14 のみ完了 → claude-code-guide agent (WebSearch/WebFetch) で代替。bias-mitigation (非 Claude モデル批評) は Codex で達成 (前例: 2026-06-02 suzanne absorb)。

---

## Saturation Gate (Phase 1.5)

- **self-evolving family**: N=10+、直近 sonicgarden 採用2/SkillOpt 採用4/RSI 採用3 → 採用率 >=20%。非飽和
- **multi-agent-orchestration family**: N>=6、直近 dynamic-workflows 採用0 の前は 30-subagents 採用4 → 連続 reject なし

**判定: PASS (warning, 重複領域)**

Stale-Plan Audit: 同 family 直近レポート全て 30 日未満 → audit skip

---

## Phase 2 + 2.5 修正済み判定テーブル

| # | 手法 | Phase 2 判定 | Phase 2.5 修正後 | 修正根拠 |
|---|------|------|------|------|
| 1 | Haiku grader 役割 | Already 強化可能 | **採用 (境界付き)** | Codex: 「非権威 cheap prefilter まで。permission/safety/最終評価には使わない」境界必須 (LLM permission classifier は 2026-05-31 cursor-run-mode absorb #4 で reject 済) |
| 2,3 | self-improving 定義 / 4層スタック | Already | Already (rehash) | sonicgarden/RSI absorb の rehash |
| 4+14 | classifier 境界 codify | Partial | **採用 (文書化のみ)** | server-side fallback は repo で実装するものではない。platform domain fallback ≠ ローカル permission classifier outage の区別を 5-10 行 |
| 5 | /goal | Gap | **Partial → pilot のみ採用** | Codex: PLANS.md Success Criteria + completion-gate が既に同責務。公式機能の存在だけで Gap にするのは強すぎ |
| 6 | verifier ≠ self-critique | Already | Already (注記) | Generator-Verifier + Codex Review Gate で model-family diversity 達成済。検証側捕捉率計測は Wave3 entry requirement に codify 済 (二重採用しない) |
| 7 | Dynamic Workflows | Already | Already | deliberate non-adopt 維持 (N=7 回目の照合) |
| 8 | worktree | Already | Already | best-of-n-guide + worktree playbook。常時分離はコスト過多 (必要時のみが現方針) |
| 9 | Routines API/GitHub trigger | Partial | **deferred by pilot gate** | Codex: scheduling-decision-table Phase 0→3 が先。sonicgarden 教訓「mechanical lane 不在 (139件中0)」「dry-run は状態が進まない」= trigger 種別より fuel/idempotency 検証が先 |
| 10+11 | 5段階メモリ進行 + STATE.md 構造 | Partial | **採用 (Codex 最優先)** | verification_status: verified/hypothesis/stale/retracted の薄いラベル。新規ループ不要。数値根拠 (73%/17%) UNVERIFIED のため概念のみ |
| 12 | skill 書き戻し + eval suite | Already | Already 維持 | retrospective-codify 既存。mechanical 変更への fixture 必須化は SkillOpt objective-lane gate と重複、Pruning-First で見送り |
| 13 | vision 自己検証 | Already | Already | ui-observer (UX Score Gate + baseline diff + 構造化 feedback) |

---

## Phase 2.5 詳細

**Codex** (gpt-5.5, cmux Worker w-1781263933-codex):

総評「公式機能が存在する = Gap と寄せすぎ。真の差分は状態の信頼度ラベル、無人化前の fuel/idempotency 検証、モデル安全境界の文書化」。

優先度:
1. verification_status ラベル (T1 — 最優先)
2. model-routing 安全境界注記 (T2)
3. /goal は pilot のみ (T3)
4. GitHub trigger は後回し (pilot gate 先)
5. 採用しない: 無人 learned→PR、LLM permission classifier、Dynamic Workflow 常用化

**Gemini**: API quota 枯渇 (429, リセット ~16h) で失敗。silent fallback せず claude-code-guide grounding で周辺知識を代替した旨明記。

---

## 採用 (3 件、実装済み)

### T1: verification_status ラベル (Codex 最優先)

`references/memory-schema.md` に `verification_status` 任意フィールドを追加:
- 値: `verified` / `hypothesis` / `stale` / `retracted`
- 欠落時デフォルト: `hypothesis` 扱い
- 適用: event/learning/proposal/summary の全 type に optional で付与可能

`references/handoff-template.md` に §3.7「検証済み事実 / 未検証仮説」セクションを追加 (Dead Ends の対として):
- Verified facts: grounding 済みの前提
- Unverified hypotheses: 採用したが未検証の数値・主張
- Example: 「Continual Learning Bench 73% — 数値 UNVERIFIED、構造 (verified/hypothesis 区別の価値) のみ採用」

### T2: Model Safety Boundary 文書化

`references/model-routing.md` に「Model Safety Boundary」セクションを追加:
- platform domain fallback (server-side Opus 4.8 自動 fallback) ≠ ローカル permission classifier outage の区別
- Haiku grader 境界: 非権威 cheap prefilter のみ。permission/safety/最終評価には使わない
- Tier 3 行に grader/prefilter 役割を追記

### T3: /goal pilot 条件

`references/scheduling-decision-table.md` に `/goal` 行を追加:
- フローチャート分岐: 「session-scoped 目標追跡が必要か?」
- Step 6.5 pilot 条件: opt-in のみ、PLANS.md Success Criteria + completion-gate との重複確認必須
- 撤退判定: 2-3 回試して差分価値なければ節ごと削除

---

## 不採用

| 項目 | 理由 |
|------|------|
| Routines GitHub/API trigger 配線 | pilot gate 先行 (fuel/idempotency 検証が未完) |
| 無人 learned→PR ループ復活 | sonicgarden 教訓: mechanical lane 0/139 件 |
| LLM permission classifier | 2026-05-31 cursor-run-mode absorb #4 で明示 reject 済 |
| Dynamic Workflows 常用化 | deliberate non-adopt 維持 (N=7 回目) |
| 5-stage の数値主張 (73%/17%) | UNVERIFIED — 概念のみ採用 |
| skill eval suite 必須化 | SkillOpt objective-lane gate と重複、Pruning-First |
| verifier 捕捉率計測の即時実装 | Wave3 entry requirement に codify 済 |

---

## Validation-only Follow-up

| 対象 | drift/未完内容 | 対応 |
|------|--------------|------|
| nightly wake (PR #71 merged) | 有効化未実施のまま (`task nightly:install` → `nightly:wake`) — 記事の Routines framing で再露出 | ユーザー判断待ち (本 absorb では変更せず) |

---

## 教訓

1. **platform drift 検証トリガーとして機能した** (claude-code-tips family 教訓の再確認): /goal・Outcomes・CMA・server-side fallback という実在機能の存在を dotfiles が未認知だった。採用 0 でも記事の価値がある典型例

2. **数値と概念を分離して評価する**: ベンチ数値 (73%/6×) は UNVERIFIED でも、その背後の構造 (verified/hypothesis 区別) は概念として採用可能。UNVERIFIED を「不採用」と混同しない

3. **Gemini quota 枯渇時の Phase 2.5 代替パス**: 「Codex で bias-mitigation + 公式 docs grounding で周辺知識」の組み合わせで代替可能 (2 例目。1 例目: 2026-06-02 suzanne absorb)

4. **Fable 5 = routing 境界の再確認機会**: Tier 4 (Fable=指揮) は既に model-routing.md に codify 済。今回は Tier 3 (Haiku=grader/prefilter) の境界注記が欠落していたことが露出した
