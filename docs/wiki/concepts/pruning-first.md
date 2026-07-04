---
title: プルーニングファースト
topics: [skill, decision, harness]
sources: [2026-04-19-top67-claude-skills-analysis.md, 2026-04-26-skill-md-15min-guide-absorb-analysis.md, 2026-05-16-dreaming-local-replica-absorb-analysis.md]
updated: 2026-07-05
confidence: emerging
source_count: 3
last_validated: 2026-07-05
---

# プルーニングファースト

## 概要

プルーニングファーストは、「新規追加より既存強化・削除を優先する」という運用方針である。スキル数やハーネス機構が成熟した環境では、新しい手法を無条件に取り込むと discovery cost や指示数の増大 (IFScale) を招くため、外部記事から知見を吸収する際の既定バイアスとして機能する。dotfiles では `references/improve-policy.md` に方針として明文化されており、absorb ワークフローの判断基準の中心に据えられている。

## 主要な知見

- **新規スキルは「既存の説明に1行足す」より強い理由が必要**: 67 個の Claude Skills 紹介記事を精査した結果、約半数 (34件) が既存ローカルスキル・サブエージェント・MCP tool で既にカバー済みと判明し、真に価値ある Gap は 2 件 (Ubiquitous Language、Dependency Auditor) + 既存強化 1 件に絞られた `[EXTRACTED, conf=85]`
- **成熟したセットアップに対する初級記事はほぼ全項目が Already になる**: SKILL.md オーサリングの初心者向けガイド (7手法) は、90 スキル環境の DBS (Direction/Blueprints/Solutions) 設計や cwd-routing-matrix と比較すると全て Already/N/A と判定され、取り込みは見送られた `[EXTRACTED, conf=85]`
- **「100% 適用済み」は品質保証と同義ではない**: description の Triggers/Do NOT use 記述率が 100% であることは「フォーマット遵守」を意味するが、「誤発火率の最適化」という別軸の品質は継続検証が必要という区別が導入された `[EXTRACTED, conf=80]`
- **技術的詐称の検出が Pruning-First の前提条件になる**: Anthropic の Dreaming feature を local 再現したと主張する記事は、公式 docs (`platform.claude.com/docs/en/managed-agents/dreams`) との突き合わせで API・パラメータ・対象データが完全に別物と判明した。この場合は「既存が優れているから不採用」ではなく「主張自体が技術的に成立していない」ため reject する `[EXTRACTED, conf=90]`
- **既存の Contradiction Mapping (Rule 26) + Build to Delete wiring (Rule 51) が記事の削除分類提案を完全に上回った事例**: 「一回限りの修正 / 老朽化した文脈 / 矛盾」という3分類の削除アイデアは、既に運用中の仕組みで代替されており、強化不要と判定された `[EXTRACTED, conf=80]`
- **`/improve` の自動修正ループが 2026-05-03 に retire 済みという制約が判断に影響する**: 自動 audit・auto_apply 系の主張は false-positive 多発で撤退した過去の失敗と同根のリスクを持つため、Pruning-First の判断は「自動化の再導入は不可」という user instruction とも整合している `[EXTRACTED, conf=75]`
- **Layer 分離の設計判断は崩さない**: SKILL.md の path-scoped activation (`paths:` field) を追加すべきという提案は、skill=task intent / rules=file・cwd constraint という既存の責務分離を壊すため N/A (by design) と判定された `[EXTRACTED, conf=75]`

## 実践的な適用

`references/improve-policy.md` の Pruning-First philosophy がスキル追加・absorb 判断の既定バイアスとして機能している。`docs/plans/active/2026-04-19-top67-skills-integration-plan.md` では、67 件の候補から採用 2 件・強化 1 件のみに絞った判断過程が記録されている。`~/.claude/skills/absorb/SKILL.md` の anti-patterns には、Already 判定を過小評価する罠 (`feedback_absorb_already_deepdive.md`) と過大評価する罠 (`feedback_absorb_sonnet_imagination.md`) の両方向が codify されている。

## 関連概念

- [スキル設計](skill-design.md) — DBS (Direction/Blueprints/Solutions) や Progressive Disclosure など、成熟したスキルセットの判断基盤
- [Sonnetイマジネーションバイアス](sonnet-imagination-bias.md) — Pruning-First の判断で「強化余地」を誤って過大評価する逆方向の罠
- [矛盾検出](contradiction-detection.md) — Contradiction Mapping (Rule 26) など、既存の削除・整理機構との重なり
- [メタ進化](meta-evolution.md) — Build to Delete の wiring と削除提案の自動化に関する設計

## ソース

- [Top 67 Claude Skills (polydao)](../../research/2026-04-19-top67-claude-skills-analysis.md) — Claude Skills 67選記事を分析、新規2件+既存強化1件のみ採用
- [SKILL.md 15分ガイド absorb分析 (著者: Nyk)](../../research/2026-04-26-skill-md-15min-guide-absorb-analysis.md) — SKILL.md初級ガイドを分析、成熟済みで不採用と判定
- [73% of my CLAUDE.md was lying to Claude — Dreaming local replica](../../research/2026-05-16-dreaming-local-replica-absorb-analysis.md) — Dreaming再現記事はAPI捏造と判明、既存Pruning-First優位確認
