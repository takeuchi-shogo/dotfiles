---
title: 脱AI臭の文章規範
topics: [skill, decision]
sources:
  - 2026-06-17-stop-slop-prose-anti-slop-absorb-analysis.md
  - 2026-06-18-japanese-tech-writing-absorb-analysis.md
updated: 2026-07-05
confidence: emerging
source_count: 2
last_validated: 2026-07-05
---

# 脱AI臭の文章規範

## 概要

AI生成文章に特有のパターン（false agency、前置きの決まり文句、em-dashの多用、機械的なヘッジなど）を検出・除去するための文章規範。ルールを絶対禁止として運用すると、検閲を潜り抜けるような不自然な文章という別種のAI臭（二次slop）を生んでしまうため、「既定の傾向として避けるが、例外条項を残す」設計が要点になる。

## 主要な知見

- em-dash全面禁止・副詞全削除・受動態禁止といった絶対ルール化は、文章が短文の羅列になったりtechnically/legallyのような文脈を規定する語彙まで失われたりする「二次slop」を招く。絶対ルールではなく「既定の傾向＋例外条項」として翻訳するのが正しい [EXTRACTED, conf=90]
- false agency（行為者が不明な受動的表現）を能動態・行為者名指しへ転換するルールは、論争が少なく効果が高い最も信頼できる改善項目である [EXTRACTED, conf=85]
- 英語圏由来のthroat-clearing opener（Here's the thing、It turns outなど）は、既存の日本語filler削除ルールとは別軸の対象であり、追加で扱う必要がある [EXTRACTED, conf=80]
- 段落の役割（受ける・果たす・渡す）を軸にしたパラグラフライティングをLLM向けの規範として明文化した日本語の事例は希少である。ただし機械的なチェックリストとして運用するとfalse positiveを生みやすいため、設計指針として扱う方が適切 [EXTRACTED, conf=75]
- 論証の厳密さ（異なるものを同一視しない、単一の原因に還元しない、因果の機構を一文で示す、「必ず」のような断定を避ける）は、長文の技術文書には直接効くが、短いPRやIssue、会話での応答にそのまま適用すると過剰になる [EXTRACTED, conf=75]
- 文章規範をskillとしてまるごと取り込むと、既存の複数箇所（AI臭除去・簡潔性・LLM口調）と二重管理になりやすい。1つの参照ファイルへ差分だけを追記する方が一元管理を保てる [INFERRED, conf=70]

## 実践的な適用

dotfilesでは`.config/claude/output-styles/prose.md`にfalse agency禁止・throat-clearing opener除去・em-dashの既定回避を追記し、`.config/claude/references/japanese-ai-prose.md`には論証の厳密さ・パラグラフライティング・整形の細部・演出の節度を「長文ドキュメント限定」の注記付きで拡張した。

## ソース

- [stop-slop: AI tell removal from prose (Hardik Pandya)](../../research/2026-06-17-stop-slop-prose-anti-slop-absorb-analysis.md) — AI臭除去skillからfalse-agency・em-dash回避等をprose.mdに最小追記
- [japanese-tech-writing SKILL (k16shikano)](../../research/2026-06-18-japanese-tech-writing-absorb-analysis.md) — 日本語技術文章規範から論証設計・段落構造等6件をprose.mdに統合
