---
title: 批評という成果物
topics: [evaluation, harness]
sources: [2026-04-09-12-claude-patterns-analysis.md, 2026-04-14-creao-ai-first-analysis.md, 2026-05-28-openclaw-autoreview-absorb-analysis.md, 2026-05-31-hermes-eval-loop-absorb-analysis.md, 2026-06-02-code-review-6-stages-ai-human-boundary-absorb-analysis.md, 2026-06-14-opik-self-repairing-harness-absorb-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 6
confidence: established
---

# Criticism as First-Class Artifact

## 概要

批評 (criticism) を会話の副産物ではなく、pre-mortem / review / retrospective の 1st-class artifact として扱う原則。批評は監査可能な構造化レコードとして残し、self-preference bias を避けるため分離された checker が生成し、指摘ゼロという「批評の不在」さえも盲点シグナルとして成果物化する。CLAUDE.md core_principles に明記され、Codex Review Gate や /review Step4 (Negative Signal Review Rule) が実装にあたる。

## 原則

批評 (criticism) は会話の副産物ではなく、pre-mortem / review / retrospective の 1st-class artifact として扱う。

## 具体化

- **Plan 段階**: pre-mortem checklist (reference: [pre-mortem-checklist.md](../../../.config/claude/references/pre-mortem-checklist.md))
- **Implementation 段階**: `/review` の責務ドメイン並列 (quality / security / dependency)
- **Post-task 段階**: `continuous-learning` skill + `improve` loop

## 主要な知見

- 「批評を成果物にする」原則は CREAO AI-First 記事の absorb (2026-04-14) で Codex 批評 (Phase 2.5) が抽出した4つの抽象原理の1つとして定式化され、CLAUDE.md core_principles に明記された。対になる原理は「観測可能にする」「判断をゲート化する」「失敗を capability gap として durable artifact に変える」で、根底には no-blame improvement (バグでエンジニアを罰するのではなくレビュープロセス自体を改善する) の発想がある [EXTRACTED, conf=85]
- 反論生成 (steelmanning) とレッドチーム (破綻シナリオの事前生成) は批評を明示的に作り出す具体的手法。`/think` Step4・`/challenge`・`/debate` adversarial・`/grill-interview` が実装として対応する [EXTRACTED, conf=75]
- レビュー findings は「隠蔽不可能な成果物」として扱うべき — suppress した findings も structured output に残し、active output には unsuppressible な notice を残し、集約結果が無関係なリスクを隠せないようにする (suppression auditability) [EXTRACTED, conf=80]
- レビュー結果は command / tests / findings / clean の4要素を持つ構造化レポートとして残す。批評は口頭コメントでなく監査可能な記録である [EXTRACTED, conf=70]
- AI の沈黙は情報である — verdict=PASS かつ指摘ゼロの場合こそ、仕様書や ADR を人間が深掘りすべき「盲点シグナル」として扱う (Negative Signal Review Rule) [EXTRACTED, conf=85]
- ADR に Affected paths / Invariants / Verification command を明記すると、本来 AI 比率 0% の Architecture 層の批評の一部が機械照合可能になる。文章化は批評の AI 委譲可能領域を広げる [EXTRACTED, conf=75]
- 批評は自己採点 (self-grading) ではなく分離された checker が行うべき — self-preference bias を避けるため。Codex Review Gate (異モデル + memory 遮断) がこの原則の実装にあたる [EXTRACTED, conf=65]
- 批評ループの自動化は precision (false positive 率) を先に担保しないと、批評そのものがノイズ artifact 化し、人間の負荷を「修正」から「レビュー」へ転嫁するだけになる。`/improve` self-improvement loop の退役 (2026-05-03, 5 連続 false-positive) はこの実例 [INFERRED, conf=60]

## 実践的な適用

- `.config/claude/skills/review/SKILL.md` Step4 Synthesis: Negative Signal Review Rule。verdict=PASS かつ Critical/Important=0 かつ spec/ADR が存在する M/L タスクで `[NEGATIVE SIGNAL]` を出力し、批評の不在自体を成果物化する
- `docs/adr/template.md`: Decision 節の後に Verification 節 (Affected paths / Invariants / Verification command) を追加し、Architecture 批評の一部を機械照合可能にする

## 出典

- CREAO AI-First 記事 (2026-04): "The ability to criticise AI will be more valuable than the ability to produce code"
- Karpathy LLM 4 原則 (既統合): "批判的思考を訓練せよ"

## 関連

- [harness-engineering.md](harness-engineering.md)
- [automated-code-review.md](automated-code-review.md) — 批評成果物の具体的な実装先 (レビューパイプライン)
- [self-improving-agents.md](self-improving-agents.md) — 批評ループの自動化と precision の緊張関係
- Plan: [2026-04-14-creao-absorb-plan.md](../../plans/2026-04-14-creao-absorb-plan.md)

## ソース

- [12 Claude Patterns 分析レポート](../../research/2026-04-09-12-claude-patterns-analysis.md) — Claude活用12パターン、反論生成・レッドチームを批評生成手法として既存ツールにマッピング
- [CREAO AI-First Strategy 記事分析レポート](../../research/2026-04-14-creao-ai-first-analysis.md) — CREAO AI-First戦略、Codex批評が「批評を成果物にする」を4原理の1つとして抽出しCLAUDE.mdに統合
- [OpenClaw autoreview SKILL.md 取り込み分析](../../research/2026-05-28-openclaw-autoreview-absorb-analysis.md) — suppression auditability と4要素 final report で批評結果の隠蔽不可能性を担保
- [How To Fix AI Slop (Using Hermes) — absorb analysis](../../research/2026-05-31-hermes-eval-loop-absorb-analysis.md) — 自動批評ループの precision 未担保リスクを反証データとして記録 (採用0)
- [コードレビュー6段階と AI/人間の境界 absorb 分析](../../research/2026-06-02-code-review-6-stages-ai-human-boundary-absorb-analysis.md) — AI沈黙=盲点シグナルの Negative Signal Rule を `/review` に実装
- [Opik Self-Repairing Harness + Karpathy Loop Engineering 分析レポート](../../research/2026-06-14-opik-self-repairing-harness-absorb-analysis.md) — 全 rehash だが検証過程で退役済み self-healing orphan を発見・整理
