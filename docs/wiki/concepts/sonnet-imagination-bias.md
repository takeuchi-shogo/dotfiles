---
title: Sonnetイマジネーションバイアス
topics: [agent, claude-code, decision]
sources: [2026-05-22-khairallah-40-features-absorb-analysis.md, 2026-05-23-cyrilxbt-18-steps-absorb-analysis.md, 2026-05-23-khairallah-30-workflows-absorb-analysis.md]
updated: 2026-07-05
confidence: emerging
source_count: 3
last_validated: 2026-07-05
---

# Sonnetイマジネーションバイアス

## 概要

Sonnet イマジネーションバイアスとは、absorb ワークフローの Pass 1 (Sonnet Explore による存在チェック) で、記事中の generic な名詞や曖昧な言い回しから「強化案」を Sonnet が創作 (hallucinate) してしまう現象である。記事原文には存在しない具体的な提案を、既存機構への強化候補として過大評価してしまうため、Pass 2 で記事原文を verbatim 引用照合するガードが必須になる。このバイアスは Sonnet 固有ではなく、Opus 自身が Pass 2 の判断段階で同様の誤りを犯すことも確認されている。

## 主要な知見

- **40 Features 記事で TOP 5 強化候補が 5/5 すべて Sonnet imagination だったと確定した最初の事例**: 「Per-Project CLAUDE.md」「Scheduled Tasks Bridge」「Extended Thinking Budget Allocation」等、記事原文には基本的な言及しかないのに Sonnet が具体的な実装案を創作していた `[EXTRACTED, conf=90]`
- **verbatim 引用照合という対策の確立**: Sonnet が提案した強化候補それぞれについて、記事原文の該当箇所を一字一句引用し、提案内容が実際に記事に書かれているかを照合する手順が Pass 2 の必須ステップとして codify された `[EXTRACTED, conf=85]`
- **Opus 自身も Pass 2 の framing 段階で同種の誤りを犯す**: 30 Workflows 記事の absorb で、Opus が「2 回訂正で自動 rule 昇格」という閾値を提案したが、記事原文を verbatim で確認すると "every mistake becomes a permanent fix" (閾値は 1) であり、Opus 自身の imagination だったと自己訂正された `[EXTRACTED, conf=90]`
- **Sonnet imagination は既存の防御機構によって 1 日後には正しく機能した**: 18 Steps 記事で Sonnet Explore が Voice Profile (音声プロファイル抽出プロンプト) を「partial (強化可能)」と報告したが、Pass 2 で `feedback_absorb_sonnet_imagination.md` と過去の Wave 3 Light Touch 決定を照合し、「N/A by design」へ正しく訂正できた `[EXTRACTED, conf=85]`
- **listicle 形式でも Pass 2 の verbatim 照合を通せば真の Gap は抽出できる**: 30 Workflows 記事では、"every mistake" の誤読は自己訂正したが、Skill 末尾の 5 項目 self-check embed (B) や金曜 15 分レビュー cadence (D) は記事原文の verbatim 引用で Gap と確定でき、実際に採用された `[EXTRACTED, conf=80]`
- **既知の逆方向バイアスとペアで扱う**: 「Already = 存在確認 ≠ 品質保証」という過小評価の罠 (`feedback_absorb_already_deepdive.md`) と、Sonnet imagination という過大評価の罠は対になる概念であり、Pass 2 では両方向を同時に検査する `[EXTRACTED, conf=75]`
- **absorb SKILL.md への anti-pattern 追加という mechanism 化**: 「Sonnet 強化案を Pass 2 で検証せず昇格させる罠」「未知用語を grounding せず factually dubious と即断する罠」の 2 点が `~/.claude/skills/absorb/SKILL.md` の anti-patterns table に追加された `[EXTRACTED, conf=80]`

## 実践的な適用

`~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/feedback_absorb_sonnet_imagination.md` に発生事例・Pass 2 必須チェック・文体識別フィルターが記録されている。`~/.claude/skills/absorb/SKILL.md` の anti-patterns table に、Sonnet imagination と未知用語の即断リスクへの対策が明記されている。absorb ワークフローの Phase 2 (Gap Analysis) では、Sonnet Explore の Pass 1 報告をそのまま採用せず、Opus (Pass 2) が記事原文の該当箇所を引用してから判定を確定する運用が定着している。

## 関連概念

- [プルーニングファースト](pruning-first.md) — 新規追加を抑制する既定バイアスと、その判断過程で発生する逆方向の過大評価リスク
- [モデルルーティング](model-routing.md) — absorb 対象がモデル選定記事であることが多く、判断バイアスが特に発生しやすい領域
- [矛盾検出](contradiction-detection.md) — 過去 absorb 履歴との照合によって Sonnet imagination を検出する仕組みとの関連

## ソース

- [How to Actually Set Up Claude: 40 Features (Khairallah)](../../research/2026-05-22-khairallah-40-features-absorb-analysis.md) — 40機能記事は採用0だがCowork stale doc driftを発見修正、TOP5強化候補が全てSonnet imaginationと確定
- [18 Steps That Unlock the Other 90% (@cyrilXBT)](../../research/2026-05-23-cyrilxbt-18-steps-absorb-analysis.md) — 18ステップ記事は全て既存実装済みで採用0件確定、防御機構が1日後に機能した実例
- [30 Claude Workflows That Most Users Never Know (Khairallah)](../../research/2026-05-23-khairallah-30-workflows-absorb-analysis.md) — 30ワークフロー記事からoutput self-checkと週次reviewを採用、Opus自身のimagination自己訂正事例
