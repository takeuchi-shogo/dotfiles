---
date: 2026-07-06
source: "A Field Guide to Fable: Finding Your Unknowns" (Anthropic 関係者ブログ + X 引用 @dzhng)
status: analyzed
family: none (明示判断 — claude-code-tips 隣接だが listicle でなく方法論エッセイ、keyword 閾値未達)
---

# Fable Field Guide to Unknowns — absorb analysis

## Source Summary

**主張**: Fable 級モデルでは作業品質のボトルネックがモデル能力から「unknowns を明確化する能力」に移った。unknown とは map (プロンプト・context) と territory (実コードベース) の差分。指示が具体的すぎるとモデルは pivot すべき場面でも従い続け、曖昧すぎると業界標準を仮定して外す。Known Knowns / Known Unknowns / Unknown Knowns / Unknown Unknowns の 4 分類で整理する。

**手法**:
1. Blind Spot Pass — 着手前に unknown unknowns を洗い出す
2. Brainstorm + HTML プロトタイプで複数方向を可視化
3. 1 問ずつインタビュー、アーキテクチャ影響順に質問する
4. 参照実装を port する
5. 実装プランは volatile な判断を先頭に置く
6. implementation-notes.md に逸脱ログを残す
7. buy-in explainer を作る
8. 変更理解クイズに合格するまで merge しない

**X 引用 (@dzhng)**: この記事から explore-unknowns skill (scan→interview→sweep) を作り、eval-hardening (planted-landmine fixture + 期待出力を見ない独立 judge + blind run) で 3 ラウンド改善した。初版は 0/2 失敗— artifact 自体は見事だったが interview 会話を丸ごとスキップしていた。参照実装: https://github.com/dzhng/skills

**前提条件**: 主著者は Anthropic 内部でエージェント運用に日常的に触れる立場。手法は「モデルに何を聞くか」の prompting/interview パターンが中心で、mechanism 化しやすいものと human-in-the-loop 前提のものが混在する。

## Saturation Gate (Phase 1.5)

PASS。既存 4 family (harness-engineering / eval-loop / claude-code-tips / obsidian-second-brain 系) いずれの keyword 閾値にも達しない。claude-code-tips に隣接するが listicle ではなく単一手法を掘り下げる方法論エッセイのため、family 分類なしを明示判断として記録する。Stale-Plan Audit は family N=0 のため発火しない。

## Phase 2 判定テーブル (Phase 2.5 修正済み)

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Blind Spot Pass | Partial | `pre-mortem-checklist.md` と edge-case-analysis は Plan 後の失敗モード・コードの異常系検出に閉じる。着手前の汎用 unknowns pass は存在しない |
| 4 | 参照実装 port | N/A | prompting パターンであり mechanism 化は YAGNI。Codex 注: Claude→Codex へのハーネス移植作業の手順としては有効 |
| 5 | 実装プランを volatile 判断先頭に並べる | Partial | `PLANS.md` に順序規定がない |
| 7 | buy-in explainer | N/A | solo 運用で buy-in の対象が不在。`/pull-request` が実質この役割を担っている (enterprise→個人の原則翻訳) |
| 9 | explore-unknowns 複合 skill | Gap→降格 (Codex 指摘) | monolithic な新規 skill は instruction DRY 違反。既存 (grill-interview / pre-mortem / PLANS) を薄く繋ぐ「unknowns gate」で代替し、採用候補 A に統合する |

### Already 強化分析

| # | 既存 | 記事の差分 | 判定 |
|---|------|-----------|------|
| 2 | superpowers:brainstorming (2-3 案 + HARD-GATE + visual-companion) | 4 directions を提示する | 強化不要 |
| 3 | grill-interview:55「後続の決定に影響する分岐から先に解決」 | アーキテクチャ影響順に質問を優先する | 強化不要→強化可能に修正 (Codex): 「高影響 unknown を黙って仮定しない」を明文化する → 候補 D |
| 6 | `PLANS.md` の Surprises & Discoveries + Decision Log + contextual commits | Deviations 見出し + conservative に続行する運用 | 強化不要 — conservative 続行は「壊れたら即 STOP」原則と衝突するため意図的に不採用 |
| 8 | teachback --strict | merge ゲート化 | 強化不要 — 呼び出し判断で足りる |
| 10 | skill-creator evals + skill-audit A/B | (a) planted-landmine fixture (b) judge 独立性 (c) 失敗→edit spec 化 | 強化可能 → 候補 C。Codex 注: landmine より process-adherence judging を優先する |

## Phase 2.5 (Refine)

Codex (gpt-5.5 xhigh, `codex exec --sandbox read-only`) で 4 点修正:
- #9 を Gap から降格 (monolithic skill を避け既存の薄い接続に統合)
- #3 を強化不要から強化可能に昇格
- #10 は landmine fixture より process-adherence judging を優先
- 見落とし: starting point の開示 (Known / Assumptions / High-impact unknowns / Questions / Blind spots) を候補 A の中核に追加すべき、との指摘

優先度提言: 大きな複合 skill を新設するより、薄い unknowns gate + eval 強化を先に入れる。

**Gemini: 未実行 (degraded)** — `gemini -p` は IneligibleTierError (individuals sunset、2026-07-05 再確認、memory `feedback_gemini_cli_sunset.md`)。Phase 2.5 は Codex 単独で実施した。

## Phase 3 (Triage) — 全 4 候補採用

- **A**: pre-plan Unknowns Pass (`PLANS.md` + `pre-mortem-checklist.md`、#1 + #9 + starting-point 開示を統合)
- **B**: `PLANS.md` の volatile-first 順序規定
- **C**: skill eval の blind-judge 強化 (judge 独立性 / process-adherence / landmine fixture)
- **D**: `CLAUDE.md:44` の既存行を書き換え「高影響 unknown を黙って仮定せず確認し、低影響は仮定した上で Decision Log に記録する」(instruction DRY: 新規追加ではなく統合)

## Phase 4 タスクリスト (M 規模、worktree+PR)

- T1: `.config/claude/references/pre-mortem-checklist.md` に「Pre-plan Unknowns Pass」セクションを追加 (約 10 行)
- T2: `PLANS.md` テンプレに `## Unknowns` セクションを追加し、Working Rules に volatile-first を 1 行追加
- T3: `.config/claude/skills/skill-creator/instructions/testing-evaluation.md` Step 4 に judge 独立性 + process-adherence + landmine fixture を追記
- T4: `.config/claude/CLAUDE.md:44` を書き換え
- 検証: `task validate-configs` / `task validate-symlinks`

## 教訓

- 記事由来の eval 失敗事例 (artifact の品質は高いが interview 工程を丸ごとスキップ) は「成果物採点だけでは process violation を見逃す」ことの実証で、process-adherence judging の直接的な根拠になる。
- Fable 時代の方法論エッセイは listicle 系 family と区別して扱う。Saturation Gate の family 分類は keyword 閾値で機械的に判定した。
