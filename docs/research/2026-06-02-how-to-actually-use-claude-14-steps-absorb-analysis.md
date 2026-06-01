---
source: "movez (Substack) — How to actually use Claude: 14 steps that unlock 100% of its potential and replace 10 apps"
date: 2026-06-02
status: light-phase2-only
verdict: ingest-skip (light Phase 2, adopt=0) — SATURATED-but-novel → 修正後 delta=0
---

# 「14 steps to use Claude」absorb 分析 (light Phase 2)

## Source Summary

**主張**: Claude を chat window だけで使うのは潜在能力の 5%。Projects / Skills / Connectors / Memory / Code / Routines / API を組み合わせれば「10 アプリを置き換えるワークフローエンジン」になる (14 ステップ・3 階層)。

**手法 (14 steps)**: Projects, Project instructions, Project knowledge base, Artifacts, custom Skills, Connectors (Gmail/Calendar/Drive/Notion/Slack), Memory + chat search, Styles, Voice mode + Quick Entry, Microsoft 365 + Chrome add-ins, Claude Code, Visual Artifacts, Routines (cloud scheduler), API + Cowork。

**根拠**: 著者主張では「Anthropic 公式 docs・launches ベース」。実態は growth-hacker Substack (movez.substack.com, "fresh AI alpha")。検証可能な数値・出典なし。

**前提条件**: 主に claude.ai consumer product + Claude Desktop ユーザー向け。Claude Code / harness 文脈は 14 中 4 ステップ (Skills, Code, Routines, API) のみ。

## Phase 1.5: Saturation Gate 結果

- **Family**: `claude-code-tips` (generic-listicle サブパターン)
- **判定**: **SATURATED-but-novel** (採用率 < 20%、初期 delta=2)
- **最類似先行**: `2026-05-22-khairallah-40-features` (同 family 11 件目、ほぼ同一ジャンル・同一機能群、**採用 0 件**)
- **生成元パターン一致**: Boris 30 Tips / Khairallah 40 features と同じ growth-hacker listicle (公式機能の独自編纂 + 「N% 潜在能力」煽り)

### Step 3.5 手法 delta 計算 (false-skip ガード)

初期照合 (直近 3 family レポート: Khairallah 40 / 30 subagents) では下記 2 件を novel 候補とした:

| novel 候補 | 初期判定 |
|-----------|---------|
| Voice mode + Quick Entry (音声入力/dictation) | novel (Khairallah 40 に無し) |
| Microsoft 365 add-ins (Excel/PowerPoint/Word/Outlook) | novel (先行は Claude in Chrome のみ) |

→ 初期 delta = 2 → ユーザー選択で **light-phase2** 実行。

**light Phase 2 で判明**: 両候補とも `docs/research/2026-03-25-claude-2026-everything-guide-analysis.md` (同 family) で**既にカバー済み・N/A 判定済み**。直近 3 レポートのみ照合した初期 delta 計算の盲点。

→ **修正後 delta = 0** (full family history 照合)。

## Gap Analysis (light Phase 2: novel 2 件のみ)

| # | 手法 | 判定 | 根拠 |
|---|------|------|------|
| 1 | Voice mode + Quick Entry | **N/A** | claude.ai / Claude Desktop consumer GUI 機能。terminal + dotfiles harness にスコープ外。先行 `2026-03-25-claude-2026-everything-guide` で同一 N/A 判定済み (line 50: "Voice mode ... N/A スコープ外") |
| 2 | Microsoft 365 add-ins (Excel/PPT/Word/Outlook) | **N/A** | 同上。Office GUI アドインは harness 設定 (hook/script/skill) に落とせない。先行で "Excel/PowerPoint add-ins ... N/A" 判定済み |

残り 12 手法は Khairallah 40 features absorb (2026-05-22) で既に検証済み (Already / partial / N/A、採用 0)。

## Integration Decisions

| 項目 | 判定 | 理由 |
|------|------|------|
| novel 2 件 (Voice / M365) | **スキップ** | consumer GUI 機能、harness にスコープ外。先行で N/A 判定済み |
| 残り 12 手法 | **スキップ** | Khairallah 40 features (同 family 直前) で検証済み・採用 0 |
| Validation-only follow-up | **なし** | 記事 framing が露出する新規 stale fact / drift なし (Cowork drift は Khairallah absorb で訂正済み) |

## Verdict

**採用件数**: 0 件 (light Phase 2 まで検証、全て Already/N/A)。
**meta-finding**: 0 件 (Sonnet imagination ガード・grounding rule・platform drift ledger は Khairallah absorb で既に skill に codify 済み。本件で新規の failure mode 検出なし)。

generic-listicle として Khairallah 40 features (2026-05-22) と同結論を再現。Phase 1.5 + Step 3.5 light-phase2 が永続ループを 1 ラウンドで閉じた事例。

## 教訓 (Step 3.5 delta 計算の改善ヒント)

- Step 3.5 の prior_methods 集合は「直近 3 レポート」だけでなく **family 全履歴を grep で照合**すべきだった (本件は light Phase 2 の grep で救済されたが、初期 delta=2 は過大評価だった)。
- consumer-GUI 系 novel 候補 (Voice / Office add-in / Chrome 等) は claude-code-tips family で繰り返し N/A 判定される定番パターン。delta 計算時に「GUI 製品機能 = harness スコープ外の既定 N/A」を semantic-equivalence で先に弾けば false-novel を減らせる。

## 関連

- `docs/research/2026-05-22-khairallah-40-features-absorb-analysis.md` — 同 family 直前 (ほぼ同一ジャンル、採用 0)
- `docs/research/2026-03-25-claude-2026-everything-guide-analysis.md` — Voice / Excel-PowerPoint add-ins を先行 N/A 判定
- `docs/research/2026-04-30-boris-30tips-absorb-analysis.md` — 同パターン listicle 先行棄却
