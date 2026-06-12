---
title: nrslib サーヴァントエンジニアリング absorb 分析 — レビュー速度改善
date: 2026-06-12
source: https://speakerdeck.com/nrslib/implementation-got-faster-so-what-about-reviews-an-invitation-to-servant-engineering-recreating-your-own-code-reviews-with-ai
author: nrslib (AI Engineering Summit 2026, SpeakerDeck 97枚)
family: code-review-best-practices (8件目, PASS-warning 採用率高)
status: integration-plan
adopted: 8
plan: docs/plans/active/2026-06-12-servant-engineering-review-speed-plan.md
---

## Source Summary

**主張**: AIで実装が速くなるほど「自分のレビュー」が Human in the loop のボトルネックになる。自分の判断基準を観点ごとに分解しファイル化 (Review as Code) し、専門エージェント群として並列実行することで解消する (サーヴァントエンジニアリング)。委譲するのは判断基準であり、違和感・事業判断・最後の責任は自分に残す。

**手法** (10件):

1. サーヴァントエンジニアリング定義 p.9-16
2. 1エージェント=1観点並列レビュー p.31-33 — 観点混在だと注意がアーキ42%/品質36%/安全31%に割れる
3. 判断基準ファイル化 policies/*.md + knowledge/*.md p.37-38
4. Faceted Prompting: Persona/Policy/Knowledge/Instruction/Output Contract の5分割 p.68-75
5. 決定論的オーケストレーション workflow.yaml FSM + Worker(edit:false)/Judge 分離 + loop monitor p.77-81
6. TAKT (作者の OSS) p.44-54
7. CodeRabbit への基準ファイル渡し .coderabbit.yaml p.55-61
8. Skill 読了の検証 — 「読んだ宣言だけで読み切っていない」実例 p.22/64
9. レビュー観点の棚卸し: 見る/見ない/部分的に見る p.34-40
10. Output Contract: approved/needs_fix/loop + finding_id p.76/81

**根拠**: 観点混在時の注意分散データ (アーキ42%/品質36%/安全31%)、Skill 読了検証の実例スライド、TAKT OSS の実装例

**前提条件**: 実装速度がレビューより速い状況 (AIコーディング環境)、判断基準が言語化可能なドメイン

**取得経路**: SpeakerDeck transcript なし (全 None) → defuddle/curl/Jina 失敗 → PDF 直接取得 (Node fetch 27.6MB) → Sonnet 全 97 ページ視覚読み取り

---

## Gap Analysis (Pass 1 + Phase 2.5 Codex 修正後)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | review tiering (light/standard/deep) + policy conflict 解消 | **Gap** (Codex 新規指摘) | CLAUDE.md:81「S も Codex Review Gate」vs review/SKILL.md:209「~10行 Verify のみ」の矛盾を実ファイルで確認。typo 修正にも 5-10 分ゲート |
| 2 | T8 並列 closeout (format → tests ∥ review) | **既採用・未実装** | docs/plans/active/2026-05-28-autoreview-absorb-plan.md T8 が pending 15日 |
| 3 | 自分のレビュー観点の蒸留 → review-learnings | **Gap 確定** | 注入機構 (review/SKILL.md:252) + persona reviewer 機構は実装済みだが実ファイル 0 個。feedback_*.md 直注入は危険 → domain 別 5-10 rule に蒸留 (Codex 補強) |
| 4 | レビュー速度の計測基盤 | **Gap** (Codex 新規指摘) | reviewer 別 duration/accept率/rerun数の記録なし。「5-10分」は体感値のみ |
| 5 | outcome 書き戻し (findings 学習ループ) | **Partial** | review-feedback-tracker 退役で Rust 版に findings 書き戻し等 4 点欠落 (decommission-log 既知) |
| 6 | checklist 読了検証 | **Partial** | Read 強制でなく Applied Checklists manifest 出力方式を採用 (Codex 提案) |
| 7 | Policy 一元化 (code-reviewer.md 重複) | **Partial** (優先度低) | compiled prompt として機能している面もある (Codex) |
| 8 | 観点別並列レビュー | **Already** (注記あり) | /review の content-signal dispatch は記事より精緻。ただし code-reviewer 自体は広い agent で「1 agent=1観点」に完全一致せず (Codex 注記、分割は合意コスト増とのトレードオフで現状維持) |
| 9 | Output Contract | **Already** (形式) / **Partial** (学習ループ=#5) | PASS/NEEDS_FIX/BLOCK + rf-ID + synthesis 17 rules |
| 10 | FSM ループ制御 | **Already** (実用) | max 3 cycles + oscillation 検出。instruction-driven であり記事の workflow.yaml 決定論 runner とは異なるが review-phase-gate.py で要所は mechanism 化済み |
| 11 | TAKT / CodeRabbit | **N/A** | Claude Code harness が TAKT 相当。CodeRabbit 不使用 (checklists は markdown なので将来渡すことは可能) |

---

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | /review content-signal dispatch (観点別並列) | code-reviewer 自体が広い agent — 1観点完全分離でない | 分割は合意コスト増とのトレードオフ → 現状維持 (観点ごとに専用 skill 切り出す場合は別タスク) | 強化不要 |
| S2 | Output Contract (PASS/NEEDS_FIX/BLOCK + rf-ID) | findings の学習ループへの書き戻し欠落 | outcome 復旧 (#5, Gap 扱いで採用) | 強化不要 (Gap 側で対処) |
| S3 | FSM ループ制御 (max 3 cycles + oscillation) | instruction-driven は決定論的保証が弱い | review-phase-gate.py で mechanism 化済み → 追加不要 | 強化不要 |

---

## Phase 2.5 批評記録

- **Codex** (gpt-5.5, cmux Worker w-1781263855): 「Already 強化不要が甘い — 文書にあると実行時に効いているを分けるべき」。見落とし指摘 4 件 (レビュー強制レベル advisory/mandatory の区別、feedback loop 退役欠落、計測基盤なし、人間が読む時間)。優先度提案: tiering+計測 → 並列 closeout → outcome 復旧/蒸留/manifest → Policy 一元化(最後)
- **Gemini**: quota exhausted (429, 16h) で実行不能 → WebSearch で代替
- **周辺知識** (WebSearch 代替):
  - AutoReview (FSE 2025, https://dl.acm.org/doi/10.1145/3696630.3728618): multi-agent 分割で検出 F1 +18.72%
  - LLM ensemble の popularity trap: 同分布モデル合議は共有エラー増幅 — dotfiles の Claude+Codex+Gemini 異種構成は緩和済み
  - 同系事例: GLOBIS「単一責任の原則で育てた話」https://zenn.dev/globis/articles/d0c73d2b176ba5
  - Cloudflare AI code review: https://blog.cloudflare.com/ai-code-review/
  - minewo「指摘の分類・記録・改善の回し方」https://zenn.dev/minewo/articles/ai-code-review-feedback-ops

---

## バッチ収集との照合

tech-researcher adoption-ledger (90件) 中、類似 1 件:

- 「コードレビューは、人もAIも『基準』がないと不安定だった」https://zenn.dev/moimoi/articles/review-rubric-essay (2026-06-07 収集、claude キュレーター不採用)
- 主張は本記事の核心 (レビュー基準の明文化) と同型 — キュレーターの不採用判定は今回のユーザー関心と乖離していた事例として記録

**手動 absorb 済み code-review family 8件**:
1. google-eng-practices (13件採用)
2. openclaw-autoreview (5件)
3. code-review-6-stages (2件)
4. cursor-auto-review (0件)
5. code-review-graph
6. findy-readability
7. harness-engineering-human-review
8. agents-md-review-skills

---

## Integration Decisions

### Gap / Partial → 採用タスク

| # | 項目 | 判定 | Wave | 理由 |
|---|------|------|------|------|
| T1 | review tiering (light/standard/deep) + CLAUDE.md ↔ review/SKILL.md policy conflict 解消 | **採用** | Wave 1 | policy conflict は即解消が必要。typo 修正に 5-10 分ゲートは摩擦過多 |
| T2 | レビュー速度計測基盤 (reviewer別 duration/accept率/rerun数) | **採用** | Wave 1 | 「5-10分」体感値のままでは改善できない。計測なし = 改善不能 |
| T3 | T8 並列 closeout (format → tests ∥ review) | **採用** | Wave 2 | 15日 pending の実装完了。autoreview-absorb-plan.md T8 を消化 |
| T4 | 自分のレビュー観点の蒸留 → domain 別 5-10 rule ファイル | **採用** | Wave 3 | 注入機構は実装済み → 実ファイル 0 の Gap を埋める |
| T5 | outcome 書き戻し復旧 (findings 学習ループ、decommission-log 既知欠落4点) | **採用** | Wave 3 | 退役で切れた学習ループを繋ぎ直す |
| T6 | Applied Checklists manifest 出力 (checklist 読了検証) | **採用** | Wave 3 | 「読んだ宣言」問題を manifest で機械的に証明可能に |
| T7 | Policy 一元化 (code-reviewer.md 重複整理) | **採用** | Wave 4 | 優先度低だが長期保守コスト削減 |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | 観点別並列 (code-reviewer 分割) | **強化不要** | 分割コスト > 効果、現状維持 |
| S2 | Output Contract 拡張 | **強化不要** | Gap T5 (outcome 復旧) で対処 |
| S3 | FSM 決定論化 | **強化不要** | review-phase-gate.py で要所 mechanism 化済み |

---

## Plan

プラン全体: `docs/plans/active/2026-06-12-servant-engineering-review-speed-plan.md` (L 規模)

### Task T1: review tiering + policy conflict 解消
- **Files**: `.claude/skills/review/SKILL.md`, `CLAUDE.md` (templates 経由)
- **Changes**: S/M/L ごとのレビュー強制レベル (advisory/mandatory) を明示。~10行 Verify のみ 条件を tiering 表に統合
- **Size**: M

### Task T2: レビュー速度計測基盤
- **Files**: `scripts/learner/review-metrics-logger.py` (新規), `docs/specs/review-metrics-schema.md` (新規)
- **Changes**: reviewer, duration_sec, accept_rate, rerun_count を JSONL 記録
- **Size**: M

### Task T3: 並列 closeout (autoreview-absorb-plan.md T8)
- **Files**: `docs/plans/active/2026-05-28-autoreview-absorb-plan.md`
- **Changes**: T8 を実装完了としてクローズ、実装差分を適用
- **Size**: S

### Task T4: レビュー観点蒸留ファイル
- **Files**: `.claude/policies/review-criteria-*.md` (新規, domain 別)
- **Changes**: feedback_*.md から domain 別 5-10 rule に蒸留して review/SKILL.md の注入機構に接続
- **Size**: M

### Task T5: outcome 書き戻し復旧
- **Files**: `scripts/policy/review-feedback-tracker.py` (再実装 or Rust 補完)
- **Changes**: findings 書き戻し / 3値判定 / R-05 explicit 優先 / redaction の欠落4点を補填
- **Size**: M

### Task T6: Applied Checklists manifest
- **Files**: `.claude/skills/review/SKILL.md`
- **Changes**: レビュー完了時に適用済みチェックリスト名を manifest 形式で出力するルールを追加
- **Size**: S

### Task T7: Policy 一元化
- **Files**: `.claude/agents/code-reviewer.md`, policy 参照先
- **Changes**: compiled prompt 重複を整理し single source of truth に寄せる
- **Size**: S
