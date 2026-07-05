---
title: 確証バイアスの検証
topics: [agent, tooling, claude-code]
sources:
  - 2026-05-23-cmux-coding-agent-workflow-absorb-analysis.md
  - 2026-05-25-claude-agent-teams-7steps-absorb-analysis.md
updated: 2026-07-05
confidence: emerging
source_count: 2
last_validated: 2026-07-05
---

# 確証バイアスの検証

## 概要

外部AI（Claude/Codex/Gemini）が生成する提案や記事には、実在するAPIと架空のAPI（fabrication）が混在しやすい。一度fabricationを見つけると以降の主張も無条件にrejectしたくなる、逆に一度信頼すると自分の判断（追認バイアス）に無自覚になる、という2方向の確証バイアスが繰り返し観測されている。個別検証をゼロベースで毎回やり直すことがこのバイアスへの対処になる。

## 主要な知見

- CLI/API提案の検証は「help一覧の目視」「既存スクリプトのgrep」「個別`--help`の実行」の三重チェックが必要。トップレベルのCommands一覧に表示されないだけで「存在しない」と即断すると、undocumented subcommandとして実在するAPIを見逃す [EXTRACTED, conf=90]
- 一度fabricationを検出すると、その後の類似した主張も検証せずに一括でreject判定してしまう傾向がある。Tier別の検証を毎回ゼロベースで実施しないと、実在する機能まで巻き添えで棄却する [EXTRACTED, conf=85]
- 実在するAPIと架空のAPIを混在させることで「もっともらしいprimitive連鎖」を合成するパターンが繰り返し観測される。個別の主張は妥当でも、それらをつなぐ主張が飛躍している場合は要注意 [EXTRACTED, conf=80]
- 出典を示さない社会的証明表現（「海外で広く使われている」「公式が推奨」）は検証不能であり、そのままでは採用判断の根拠に使えない [EXTRACTED, conf=85]
- 過去に実機検証済みで否定的な結論が出ている主張（memoryに記録済み）を、後続の類似記事が無自覚に繰り返すケースがある。新しい記事を評価する際は過去の検証結果を必ず参照する [EXTRACTED, conf=75]
- WebSearchによる実在性のgrounding検証と、「既存方針でその主張を採用しないという判定が正しいか」というバイアス検証は別の軸であり、片方だけでは不十分。実在性が確認された主張でも、既存方針を理由に切り捨てる判定自体に追認バイアスが混入しうる [EXTRACTED, conf=70]

## 実践的な適用

dotfilesの/absorb skillはPhase 1.6でWebSearch groundingによる実在性検証、Phase 2.5でCodex+Gemini並列批評による確証バイアス検証を分離して運用している。`feedback_absorb_already_hallucination.md`や`feedback_settings_json_grep_first.md`はこの種の再発防止策として記録されている。

## 関連概念

- [config-drift-audit.md](config-drift-audit.md) — 外部知見の検証結果を自harnessの監査に転用する手法

## ソース

- [cmux Coding Agent Workflow (外部AI応答)](../../research/2026-05-23-cmux-coding-agent-workflow-absorb-analysis.md) — 外部AI生成cmux提案は大半fabricated、実在API 8件のみ記録
- [How to Build a Claude Agent Team in 7 Steps (Twitter)](../../research/2026-05-25-claude-agent-teams-7steps-absorb-analysis.md) — Agent Team記事はほぼAlready、cmuxとの境界注記のみ採用
