---
title: "stop-slop (AI tell removal from prose) absorb 分析"
date: 2026-06-17
source: https://github.com/hardikpandya/stop-slop
author: Hardik Pandya
type: skill (prose writing, MIT, 10.9k stars)
family: prose-writing-style
status: adopted-minimal
adopted: 1 (false agency / throat-clearing opener / em-dash soft-default を prose.md に追記)
---

## Source Summary

**主張**: AI 文章には予測可能な tell（定型句・構造・リズム）があり、それを検出・除去するよう LLM に教える skill。

**手法**:
1. 禁止フレーズ — throat-clearing opener / emphasis crutch / business jargon / 全副詞 / vague declarative / meta-commentary
2. 構造的クリシェ — binary contrast / negative listing / dramatic fragmentation / rhetorical setup / false agency / narrator-from-a-distance / passive voice
3. 文レベル規則 — Wh- 文頭禁止 / em-dash 禁止 / staccato 禁止 / 能動態強制
4. 5次元スコアリング (Directness/Rhythm/Trust/Authenticity/Density, 35/50 未満は改稿)
5. before/after 例
6. progressive disclosure (SKILL.md + references load on demand)

**前提**: プロース(文章)出版用。コードではない。

## Phase 1.5 Saturation Gate

family = `prose-writing-style`。真に同 family の過去 absorb は caveman+genshijin brevity (2026-04-11) と Fable5 O4 prose output-mode の 2 件で、いずれも採用あり。Hermes (2026-05-31) は **コード slop の eval-loop** で別 family。skill 執筆メタ系 (Tan/Atomic/PostHog 等) も別軸。N<3 かつ採用率高 → **PASS**。

stop-slop の新規軸: 既存 prose 資産は「簡潔性(語数削減)」中心。stop-slop は「AI tell 除去(em-dash/false agency/受動態)」という別軸を持つ。

## Pass 1/2 判定テーブル

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | filler/hedge 削除 (well, just, really, I think) | Already | `concise.md` Drop List が英日カバー |
| 2 | 英語 throat-clearing opener (Here's the thing/It turns out) | Partial→**採用** | 日本語 filler のみ存在。英語 opener は未収載 |
| 3 | business jargon (navigate/unpack/deep dive) | Gap (不採用) | 会話応答で頻度低・YAGNI |
| 4 | 全副詞削除 (deeply/fundamentally/literally) | Partial (不採用) | **絶対ルール=二次 slop リスク** (Gemini) |
| 5 | binary contrast (Not X. It's Y.) | Gap (不採用) | 会話応答で実害低 |
| 6 | false agency → 能動態/行為者名指し | Gap→**採用** | robustly-good・低論争。最高シグナル |
| 7 | passive voice → 行為者名指し | Gap (部分採用) | #6 に統合 (能動態方針)。絶対禁止はしない |
| 8 | em-dash 全面禁止 | Gap→**採用(soft)** | 有名 tell だが「絶対禁止」でなく「既定で避ける」 |
| 9 | Wh- 文頭禁止 | Gap (不採用) | 日本語応答主体で適用機会小 |
| 10 | 5次元スコアリング (35/50) | N/A | prose 用スコアリングは過剰 |
| 11 | progressive disclosure | Already | dotfiles 基本構造 |

## Phase 2.5 (Gemini grounding, Codex は down-scope)

第三者成果物 (self-preference bias 小) + Gap が事実検証可能なため Codex 批評は down-scope し、Gemini grounding に絞った。

Gemini の警告 (二次 slop): 絶対ルールは逆効果。
- em-dash 全禁止 → 文章が短文羅列化、リズム喪失
- 副詞全削除 → technically/legally 等の文脈規定副詞まで失い解像度低下
- 禁止語リスト遵守 → 「検閲を潜る不自然な文章」という新たな AI 臭 (secondary slop)
- 受動態の画一排除 → 科学的記述で焦点ぼやけ

→ **絶対ルールは採用せず「既定の傾向 + 既存の例外条項」として翻訳**。

## 採用 (Phase 3-4)

`.config/claude/output-styles/prose.md` に `## AI tell を避ける` を追記 (S, 1 ファイル):
1. false agency 禁止 → 行為者名指し / 該当者なしなら「あなた」
2. 英語 throat-clearing opener を切る
3. em-dash は既定で避ける (絶対でない)
+ 「機械的一掃は二次 slop」の注記で絶対ルール化を防止。

## 棄却台帳 (次回 prose-slop absorb の anchor)

- **skill 丸ごと vendor**: YAGNI。dotfiles の散文は大半が会話応答 (prose.md/concise.md 統治済) か内部レポート。英語 publish prose を書く頻度が上がれば再考
- **絶対ルール (em-dash全禁止/全副詞削除/受動態禁止)**: Gemini 実証で二次 slop。既存の「例外条項を持つ brevity 規律」とも衝突
- **5次元スコアリング**: prose 用スコアは harness にオーバーキル
- **business jargon / binary contrast / Wh- 文頭**: 会話応答での実害低、日本語主体で適用機会小
