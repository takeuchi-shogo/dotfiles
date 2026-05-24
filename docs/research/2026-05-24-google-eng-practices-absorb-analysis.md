---
title: Google eng-practices Code Review Guide /absorb Analysis
date: 2026-05-24
source: https://github.com/google/eng-practices
source_type: repository
license: CC-BY 3.0
family: code-review-best-practices
status: integration-plan
adopted: 13
rejected_or_na: 13
total: 26
scale: L
---

# Google eng-practices Code Review Guide /absorb Analysis

## 1. Source Summary

- **URL**: https://github.com/google/eng-practices
- **Stars**: 20,871 / **Created**: 2019-09-04 / **Last update**: 2026-05-23 (現在もアクティブ)
- **License**: CC-BY 3.0 (共有・改変可)
- **構成**: README + Reviewer Guide (6 ファイル) + Developer Guide (3 ファイル) + Emergencies (1 ファイル) + index ファイル
- **総コンテンツ量**: ~70KB markdown
- **Fetch 経路**: gh raw fetch (C1 override、Haiku truncation なし)
- **Core claim**: "Code review の primary purpose は overall code health を時間とともに改善すること。Reviewer は完璧を求めず、CL が improve code health なら approve すべき" (Senior principle)

---

## 2. Phase 1.5 Saturation Gate 結果

- **Family**: code-review-best-practices
- **同 family の過去 absorb 数**: 2件
  - `2026-03-26-findy-code-review-readability-analysis.md` (Findy = AI readability scoring)
  - `2026-03-30-code-review-graph-analysis.md` (code-review-graph = MCP ツール)
- **両エントリの文脈**: 別文脈 (Findy は AI 可読性スコアリング、code-review-graph は MCP ツール)
- **判定**: N < 3 → **PASS** (本記事は family 内での新規文脈)

---

## 3. Phase 1 抽出 — 26 手法

Pass 1 dispatch で抽出した 22 手法 + Codex Phase 2.5 で補足した 4 手法の合計。

| # | 手法 | 出典 | キーワード |
|---|------|------|-----------|
| 1 | code-health-improvement-principle | standard.md | overall code health, time horizon |
| 2 | technical-facts-over-opinions | standard.md | evidence-based, cite specific |
| 3 | review-checklist-12-items | looking-for.md | every line, good things |
| 4 | over-engineering-vigilance | looking-for.md | YAGNI, complexity |
| 5 | why-not-what-comments | looking-for.md | context, intent |
| 6 | navigate-three-steps | navigate.md | design-first, immediate return |
| 7 | 1-business-day-response | speed.md | SLA, turnaround |
| 8 | focus-protection-interrupt-rule | speed.md | deep work, interrupt cost |
| 9 | response-speed-priority | speed.md | velocity, throughput |
| 10 | lgtm-with-comments | speed.md | FYI, non-blocking |
| 11 | kind-comments-courtesy | comments.md | tone, courtesy |
| 12 | label-severity-prefix | comments.md | Nit, FYI, blocking |
| 13 | pushback-who-is-right | pushback.md | counter-argument, evidence |
| 14 | no-cleanup-later | pushback.md | TODO boundary, deferred debt |
| 15 | small-cl-one-thing | small-cls.md | PR size, focus |
| 16 | cl-splitting-strategies | small-cls.md | stacked PRs, split patterns |
| 17 | separate-refactoring-cls | small-cls.md | refactor mixing block |
| 18 | tests-in-same-cl | small-cls.md | refactor-only tests, independent test CL |
| 19 | cl-description-what-why | cl-descriptions.md | PR description, context |
| 20 | mentoring-via-review | standard.md | education, knowledge transfer |
| 21 | emergency-definition | emergencies.md | emergency criteria, urgent fix |
| 22 | conflict-escalation-path | standard.md | escalation, NEEDS_HUMAN_REVIEW |
| 23 | Style authority / author preference | standard.md "Principles" section | style guide, author decision |
| 24 | Documentation update check | looking-for.md "Documentation" section | doc sync, drift |
| 25 | Large CL exception handling | small-cls.md "Can't Make it Small Enough" section | large CL, exception |
| 26 | Don't break the build between stacked CLs | small-cls.md "Don't Break the Build" section | stacked CL, build stability |

---

## 4. Phase 2 — Pass 1 (Sonnet Explore) + Pass 2 (Opus) 判定

| # | 手法 | Pass 1 (Sonnet) | Pass 2 (Opus) 修正後 |
|---|------|----------------|---------------------|
| 1 | code-health-improvement-principle | not_found (Gap) | Partial (PASS 設計が正 framing、positive 原則未明文化) |
| 2 | technical-facts-over-opinions | not_found (Gap) | Partial (レビュー feedback に証拠引用義務なし) |
| 3 | review-checklist-12-items | exists | Already 強化可能 (good things 視点なし) |
| 4 | over-engineering-vigilance | exists | Already 強化不要 (YAGNI 既実装) |
| 5 | why-not-what-comments | exists | Already 強化不要 (context comments 既実装) |
| 6 | navigate-three-steps | not_found (Gap) | Partial (design-first feedback gate なし) |
| 7 | 1-business-day-response | exists | N/A (AI review に SLA 概念無効) |
| 8 | focus-protection-interrupt-rule | exists | N/A (AI review に interrupt cost 概念無効) |
| 9 | response-speed-priority | exists | N/A (AI review に response speed 概念無効) |
| 10 | lgtm-with-comments | exists | Already 強化可能 (FYI label で部分カバー) |
| 11 | kind-comments-courtesy | partial | Already 強化可能 (Bad/Good 例示なし) |
| 12 | label-severity-prefix | exists | Already 強化不要 (Nit/FYI/blocking 既実装) |
| 13 | pushback-who-is-right | not_found (Gap) | Partial (developer counter-argument first 規約なし) |
| 14 | no-cleanup-later | partial | Partial (TODO 検出は既存、新規 complexity 区別なし) |
| 15 | small-cl-one-thing | exists | Already 強化可能 (閾値未統一) |
| 16 | cl-splitting-strategies | partial | Already 強化可能 (splitting patterns 文書なし) |
| 17 | separate-refactoring-cls | exists | Already 強化可能 (review-side block 基準なし) |
| 18 | tests-in-same-cl | exists | Already 強化可能 (refactor-only test / 独立テスト CL 先行 nuance なし) |
| 19 | cl-description-what-why | exists | Already 強化不要 (what-why 既実装) |
| 20 | mentoring-via-review | not_found (N/A) | Partial (AI review = future-self education として transferable) |
| 21 | emergency-definition | not_found (N/A) | Partial (shell/hook 破損 = emergency として valid) |
| 22 | conflict-escalation-path | not_found (N/A) | Already 強化可能 (NEEDS_HUMAN_REVIEW = AI escalation として既存) |
| 23 | Style authority / author preference | — | Partial (Codex Phase 2.5 追加) |
| 24 | Documentation update check | — | Already 強化可能 (Codex Phase 2.5 追加) |
| 25 | Large CL exception handling | — | Gap (Codex Phase 2.5 追加) |
| 26 | Don't break the build between stacked CLs | — | Partial (Codex Phase 2.5 追加、低優先) |

---

## 5. Phase 2.5 — Codex + Gemini 批評

### Codex (high-value: file 参照付き批評) — 全 5 件再分類を採用

| 元判定 | 手法 | 修正後 | 根拠 |
|--------|------|--------|------|
| Gap | #1 code-health-improvement-principle | Partial | PASS 設計が許容済み。positive 原則のみ未明文化 |
| Gap | #14 no-cleanup-later | Partial | TODO 検出は既存。新規 complexity だけ未実装 |
| Already sufficient | #17 separate-refactoring-cls | Already 強化可能 | review-side block 基準なし |
| Already sufficient | #18 tests-in-same-cl | Already 強化可能 | refactor-only test / 独立テスト CL 先行 nuance なし |
| N/A | #20 mentoring-via-review | Partial | AI review = future-self education として transferable |
| N/A | #21 emergency-definition | Partial | shell/hook 破損 = emergency として valid |
| N/A | #22 conflict-escalation-path | Already 強化可能 | NEEDS_HUMAN_REVIEW = AI escalation として既存 |

追加訂正: #4 YAGNI 根拠を GP-012 → CLAUDE.md:84 に修正。

### Gemini (industry context)

**採用企業**: GitLab (handbook 明示参照)、Netlify、Auth0、PayPal、New Relic、Bitcoin Core、Go/Kubernetes/TensorFlow/Angular

**批判点**:
- human-linter 化リスク (形式遵守が目的化)
- Speed 理想と現実の乖離 (Google 自社 OSS が PR 数ヶ月放置 = HN 揶揄)
- Critique tool dependency (Google 内部ツール前提)
- 小規模組織オーバーヘッド

**代替アプローチ**:
- Meta: P75 Time In Review + ML reviewer
- Microsoft: 心理的安全性重視
- Stripe: Trustworthy First Draft + Taste
- GitHub: Draft PR + CODEOWNERS

**AI 2024-2026 trend**:
- Nit は AI 完全担当
- Speed は Rigor 再優先
- LGTM for small は形骸化
- Spec-Driven Development 前段化

**暗黙制約の確認**: Piper monorepo + One Version + OWNERS + Critique Attention Set は個人 dotfiles に不適合な部分が大きく、N/A 判定の妥当性を支持。ただし「AI 自動レビューに transferable な原則」は適用範囲の再評価価値あり (Codex 指摘)。

---

## 6. 最終分類 (26 手法)

| 分類 | 手法番号 | 件数 |
|------|---------|------|
| **Gap** | #25 | 1 |
| **Partial** | #1, #2, #6, #13, #14, #20, #21, #23, #26 | 9 |
| **Already 強化可能** | #3, #10, #11, #15, #16, #17, #18, #22, #24 | 9 |
| **Already 強化不要** | #4, #5, #12, #19 | 4 |
| **N/A** | #7, #8, #9 | 3 |
| **合計** | | 26 |

---

## 7. 採用項目 (13 件 — Tier 1 + Tier 2 全採用)

**ユーザー意図**: "Google エンジニアになりたい" 目線で mindset/discipline transfer を含めて全採用。AI review が Google 水準の規律を毎回適用する harness を構築する。

### Gap / Partial 採用 (7件)

| # | 手法 | 採用理由 |
|---|------|---------|
| #14 | no-cleanup-later (cleanup-later 境界) | TODO 新規 vs 既存の区別を明確化 |
| #21 | emergency-definition | dotfiles 文脈 (shell/hook 破損) に適用可能 |
| #25 | Large CL exception handling | github-pr skill に例外処理を追加 |
| #1 | code-health-improvement-principle (Positive principle) | approve 判定の正方向 framing を明文化 |
| #2 | technical-facts-over-opinions (Tier 2) | review feedback に具体的証拠引用義務 |
| #6 | navigate-three-steps (Tier 2) | design 重大問題は即時返却 = design-first feedback gate |
| #13 | pushback-who-is-right (Tier 2) | code-reviewer agent に "consider developer counter-argument first" 規約 |

### Already 強化可能 採用 (6件)

| # | 手法 | 採用理由 |
|---|------|---------|
| #15 | small-cl-one-thing (小 CL 閾値統一) | 複数ファイル間で threshold を統一 |
| #16 | cl-splitting-strategies (PR splitting patterns) | splitting patterns を文書化 |
| #11 | kind-comments-courtesy (Courtesy + Bad/Good) | Bad/Good 例示を追加 |
| #3 | review-checklist-12-items (Every Line + Good Things) | good things 視点を追加 |
| #17 | separate-refactoring-cls (refactor mixing block) (Tier 2) | code-reviewer agent が大規模 refactor × feature/bugfix 混在を NIT で block |
| #18 | tests-in-same-cl (refactor-only tests + 独立テスト CL 先行) (Tier 2) | Google nuance を code-reviewer agent に追加 |

---

## 8. 採用見送り / N/A 項目 (13 件)

| # | 手法 | 分類 | 見送り理由 |
|---|------|------|-----------|
| #20 | mentoring-via-review | Partial | #5/#19 強化 + Tier 2 #2 で吸収可 |
| #23 | Style authority / author preference | Partial | #2 と関連、将来検討 |
| #26 | Stacked CL build | Partial (低優先) | 個人 dotfiles で stack 分割稀 |
| #10 | lgtm-with-comments | Already 強化可能 | FYI label で部分カバー、追加 ROI 低 |
| #22 | conflict-escalation-path | Already 強化可能 | NEEDS_HUMAN_REVIEW で既にカバー |
| #24 | Documentation update check | Already 強化可能 | doc-gardener で部分カバー |
| #4 | over-engineering-vigilance | Already 強化不要 | YAGNI 既実装 (CLAUDE.md:84) |
| #5 | why-not-what-comments | Already 強化不要 | context comments 既実装 |
| #12 | label-severity-prefix | Already 強化不要 | Nit/FYI/blocking 既実装 |
| #19 | cl-description-what-why | Already 強化不要 | what-why 既実装 |
| #7 | 1-business-day-response | N/A | AI review に SLA 概念無効 |
| #8 | focus-protection-interrupt-rule | N/A | AI review に interrupt cost 概念無効 |
| #9 | response-speed-priority | N/A | AI review に response speed 概念無効 |

---

## 9. Integration Plan (T1–T8)

### タスク一覧

| Task | 対象ファイル | 対応手法 | 規模 |
|------|------------|---------|------|
| T1a | `references/pr-splitting-patterns.md` (NEW) | #16 | S |
| T1b | `references/review-courtesy-examples.md` (NEW) | #11 | S |
| T1c | `references/emergency-definition.md` (NEW) | #21 | S |
| T2 | `agents/code-reviewer.md` 編集 (6 セクション追加: cleanup-later boundary + courtesy core + every-line/good-things + pushback-who-is-right + refactor-mixing-block + refactor-only-tests-nuance) | #14, #11, #3, #13, #17, #18 | M-L |
| T3 | `skills/github-pr/SKILL.md` (#15 threshold unification + #25 Large CL exception) | #15, #25 | S |
| T4 | `skills/github-pr/self-review.md` (#15 threshold sync) | #15 | S |
| T5 | `agents/golang-reviewer.md` (#15 threshold sync) | #15 | S |
| T6 | `references/review-checklists/cross-cutting.md` (TODO 新規 vs 既存 区別) | #14 | S |
| T7 | `skills/review/SKILL.md` + `references/review-consensus-policy.md` (positive principle + evidence-based feedback rubric + design-first feedback gate) | #1, #2, #6 | M |
| T8 | MEMORY.md pointer entry | meta | S |

### 規模見積もり

- 新規ファイル: 3件 (T1a, T1b, T1c)
- 編集ファイル: 8件 (T2, T3, T4, T5, T6, T7 x2, T8)
- **総規模: L 確定**

### 依存関係

- T1a, T1b, T1c (新規ファイル) → T2 (#11 が T1b 参照、#14 が cross-cutting 経由) + T3 (#25 が T1c 参照)
- T2 → T6 (TODO 区別 sync)
- T3 → T4, T5 (threshold sync)
- T7 は独立 (review skill 内完結)

**推奨**: 新セッションで `/rpi docs/plans/active/2026-05-24-google-eng-practices-integration-plan.md`

---

## 10. Handoff 推奨

本セッションは /absorb で context が長いため、同一セッション内での実装は非推奨。新セッションで以下を実行:

```
/rpi docs/plans/active/2026-05-24-google-eng-practices-integration-plan.md
```

L 規模 (3 新規ファイル + 8 編集ファイル) のため plan 作成 → Codex Spec/Plan Gate → 段階的実装の流れを推奨。

---

## 11. Meta Findings (/absorb workflow への学び)

本 absorb セッションは /absorb workflow 自体の品質に関する重要な知見を提供した。

### Phase 2.5 Codex による救出の価値

Phase 1 (Pass 1 dispatch) で Sonnet が漏らした 4 手法 (#23, #24, #25, #26) を Codex Phase 2.5 が補足した。**Phase 1 の抽出は完全ではなく、Codex の file 参照付き批評が見落とし検出に有効**であることを実証している。

特に #25 (Large CL exception handling) は Gap 判定で実際に採用された手法であり、Phase 1 漏れが採用機会の損失に直結するリスクを示した。

### Pass 2 誤判定の修正パターン

Opus Pass 2 段階での誤判定 6 件を Codex が訂正した:
- **Gap → Partial** (2件): 既存実装が部分的に機能していることを見落としていた
- **sufficient → 強化可能** (2件): "既存あり" で満足してしまい改善余地を見逃していた
- **N/A → Partial** (2件): Google 暗黙制約 (Piper monorepo 等) を AI review 文脈に転用可能な点を見逃していた

このパターンは `/absorb` workflow の **Pass 2 → Phase 2.5 のゲート** が誤判定に対する重要な安全弁であることを示している。

### Gemini による AI 2024-2026 trend の確認

Gemini grounding で確認された AI review trend (Rigor 再優先 / Spec-Driven Development 前段化) は、dotfiles の `/spec` skill が業界 trend と整合していることを支持した。外部情報源による dotfiles 設計の独立検証として機能した。

### Google 暗黙制約の N/A 判定精度

Piper monorepo + One Version + OWNERS + Critique Attention Set という Google 固有インフラへの依存は、個人 dotfiles 文脈での N/A 判定を妥当化した。一方 Codex が指摘した「AI 自動レビューに transferable な原則」(#20, #21, #22) は、暗黙制約の影に隠れていた適用可能性を発掘した。この発掘は **"N/A と見えるものにも AI 文脈での転用可能性がある"** という absorb workflow の refinement ポイントを示している。

---

## 12. Sources & Citation

- **記事**: https://github.com/google/eng-practices
- **Reviewer Guide**: standard.md, looking-for.md, navigate.md, speed.md, comments.md, pushback.md
- **Developer Guide**: small-cls.md, cl-descriptions.md, handling-comments.md
- **Emergencies**: emergencies.md
- **License**: CC-BY 3.0 (https://creativecommons.org/licenses/by/3.0/)
- **Codex 批評**: `codex exec -m gpt-5.5 --sandbox read-only` reasoning=high (147k tokens)
- **Gemini grounding**: `gemini --approval-mode plan`
- **Pass 1 Sonnet Explore**: 22 keywords searched across dotfiles + ~/.claude

---

## Related Plan

詳細 integration plan: [`docs/plans/active/2026-05-24-google-eng-practices-integration-plan.md`](../../plans/active/2026-05-24-google-eng-practices-integration-plan.md)

---

## 13. Phase 2 採用転換 (2026-05-24 同日追記)

### 経緯

Phase 1 完了直後、ユーザーが `/challenge` で「同等以上達成?」を独立検証。本文書 §8 で「採用見送り 13 件」とした項目のうち、`looking-for.md` Google エンジニア基準で **5 項目に parity gap が残存** することが判明。ユーザー承認 ("全部進めて") に基づき Phase 2 として 5 項目追加採用。

### 棄却決定を覆す根拠

| # | 元判定 | 元棄却理由 | 反証 (Phase 2 採用根拠) |
|---|--------|-----------|----------------------|
| #20 mentoring-via-review | Partial | "#5/#19 + Tier 2 #2 で吸収可" | #5/#19 は context 説明、#2 は evidence 提示 = いずれも mentoring tone (Why + 学習リソース) を保証しない。AI reviewer が future-self education として transferable な独立規律 |
| #23 Style authority | Partial | "#2 と関連、将来検討" | Principle 2 (Evidence-Based) は「根拠の品質」、Style Authority は「指摘範囲の制限」で論理的に直交。AI reviewer の主観 NIT 量産抑制に必要 |
| #24 Documentation update | Already 強化可能 | "doc-gardener で部分カバー" | doc-gardener は **既存 docs の定期 drift スキャン**、本項目は **本 CL 内の同期強制**。責務分離可能で並立する規律 |
| #10 lgtm-with-comments (再判定) | Already 強化可能 | "FYI label で部分カバー" | FYI は label レベル、Google LGTM = approve + non-blocking nits **並立の verdict 表現** が欠落 → `[NITS_REMAIN]` タグで operationalize |
| navigate.md ファイル順 (新規抽出) | Phase 1 未抽出 | (Codex Phase 2.5 でも未検出) | severity 順 (broad→specific→nit, Principle 3) と直交する **ファイル読み順** (main file first → affected → trivial last)。cognitive load 削減 |

### Phase 2 採用 5 項目と対応ファイル

| # | 手法 | 対応ファイル | 規模 |
|---|------|------------|------|
| #20 | Mentoring Tone | `agents/code-reviewer.md` Section G | S |
| #23 | Author Preference Authority | `skills/review/SKILL.md` Principle 4 | S |
| #24 | Documentation Sync | `references/review-checklists/cross-cutting.md` CC-10 | S |
| #10 | LGTM with comments | `agents/code-reviewer.md` Verdict 補助タグ `[NITS_REMAIN]` + `skills/review/SKILL.md` Step 5 完了報告 | S |
| navigate.md file order | Navigation Order | `skills/review/SKILL.md` Step 1.4 | S |

Phase 2 規模: 3 ファイル編集、+120 行。Phase 1 (13 採用) との合計で **18 採用 + 8 棄却 (#26/#22/#4/#5/#12/#19 + #7/#8/#9 N/A) + 0 未判定** = 26 件 100% 処理完了。

### Phase 2 検証

- code-reviewer + codex-reviewer 並列 BLOCK 検出 (Plan Alignment Contradiction)
- 本セクション (§13) 追記で contradiction 解消
- 再 review で PASS 取得 (harness_review_flag 書き出し)

---

## 14. Meta Finding: /challenge による棄却決定の見直し

Phase 1 で「13 棄却」と確定した判断を、**同日の独立検証 (Persona-based challenge)** で 5 件覆した経験は、`/absorb` workflow の改善ポイントを示唆する:

- Phase 2.5 の Codex 批評は **手法の抽出漏れ** は補足したが、**棄却理由の妥当性検証** は不十分だった
- 棄却判定 (`Already 強化可能` / `Partial → 見送り`) は **正当化バイアス** に流れやすい (既存実装 = sufficient と即断)
- ユーザーの "Google エンジニアになりたい" 目線 = persona 視点での再検証が **棄却理由の弱さ** を露呈
- 今後の /absorb workflow に「棄却 N 件のうち X% は persona challenge で覆ることがある」事前期待値を組み込むべき (Phase 2 backlog として retain)
