---
title: 矛盾検出
topics: [research, personal-analyst]
sources: [2026-04-09-paper-analysis-prompts-analysis.md, 2026-05-23-damidefi-claude-obsidian-second-brain-absorb-analysis.md]
updated: 2026-07-05
confidence: emerging
source_count: 2
last_validated: 2026-07-05
---

# 矛盾検出

## 概要

矛盾検出は、複数の情報源やナレッジベース内の主張を突き合わせ、対立する claim を明示的に洗い出す手法である。dotfiles では対象範囲によって扱いが分かれており、内部ナレッジベース (Claude memory) 内の矛盾は `contradiction-mapping.md` (Rule 26) が扱う一方、外部の学術論文コーパス間の矛盾検出や、Obsidian Vault 全体を対象にした矛盾検出は、それぞれ別の設計判断が必要になる。

## 主要な知見

- **内部矛盾検出と外部コーパス矛盾検出は別物として扱う**: `contradiction-mapping.md` は Claude memory 内の矛盾を対象にしており、複数の学術論文間での claim レベルの矛盾抽出には対応していない。学術論文分析向けの「Contradiction Finder + WHY 分析」は、この区別を踏まえて `/paper-analysis` skill という別ワークフローに統合された `[EXTRACTED, conf=85]`
- **9 プロンプト手法は個別追加ではなく1本の統合ワークフローに集約する判断がなされた**: 矛盾検出・引用系譜・ランドスケープマッピング・コンセンサス抽出・ギャップ分析・手法論監査・知識地図・含意テスト・仮定破壊の9手法はいずれも既存の部分的な仕組み (contradiction-mapping.md、Scite MCP、/research、knowledge-pyramid、/digest、/absorb) と重なるが、専用の統合フローとしての価値があると判断され `/paper-analysis` skill として実装された `[EXTRACTED, conf=80]`
- **幽霊引用・Lost in the Middle・Sycophancy という3つの LLM 固有リスクが安全機構として組み込まれた**: 存在しない論文を生成するリスクへは DOI/URL 原典照合の必須化、長文中央部の精度低下へはチャンキング戦略、矛盾を調和させてしまう傾向へは複数モデル独立検証という対策が `/paper-analysis` skill に反映されている `[EXTRACTED, conf=75]`
- **Vault 全体を対象とする矛盾検出 (Vault-wide contradiction) は常時化を避け、明示実行時限定にとどめる判断がなされた**: 「AI second brain」記事が提案する Contradictions セクションの自動生成は、既存の `contradiction-scanner.py` (Claude memory 対象) とは範囲が異なる Partial 項目と判定されたが、Vault 全文を常時スキャンすると誤検出・ノイズ・文脈肥大のリスクが高いため、`/think` や `/obsidian-knowledge` の明示実行時のみに限定し、実装は見送られた `[EXTRACTED, conf=80]`
- **「Daily 4-section synthesis (Connections/Patterns/Contradictions/Open Questions)」は novel ではなく既に検討・棄却済みのパターンだった**: Sonnet が Pass 1 で Gap (novel) と報告したが、Codex 批評で同系統の Cyril 記事群で既に検討・棄却されていたことが判明し、Sonnet imagination の一例として Partial に降格された `[EXTRACTED, conf=80]`
- **creator-monetization 系記事の矛盾検出提案は anecdotal な効果測定が多い**: 「30日 surprise test」のような効果測定プロトコルは実装ではなく評価メモとして扱う validation-only 判定にとどめられた `[EXTRACTED, conf=70]`

## 実践的な適用

`.config/claude/skills/paper-analysis/SKILL.md` は学術論文コーパスを対象にした矛盾検出を含む9段階の分析ワークフローとして実装されている。`references/contradiction-mapping.md` (Rule 26) は Claude memory 内の矛盾を扱う既存機構として維持され、外部コーパスとは責務が分離されている。Vault 全体の矛盾検出は `contradiction-scanner.py` の対象拡大ではなく、`/think` Step 4 や `/obsidian-knowledge` の明示実行時にとどめる方針が確認されている。

## 関連概念

- [Obsidian統合](obsidian-integration.md) — Vault-wide contradiction detection の適用範囲と、常時化を避ける設計判断
- [ナレッジパイプライン](knowledge-pipeline.md) — /paper-analysis skill を含む知見統合ワークフローとの関連
- [プルーニングファースト](pruning-first.md) — 既存の contradiction-mapping.md が記事提案を上回ると判断される際の基準
- [Sonnetイマジネーションバイアス](sonnet-imagination-bias.md) — Daily 4-section synthesis が novel と誤判定された事例との関連

## ソース

- [9 Prompts for Academic Paper Analysis (James, Twitter)](../../research/2026-04-09-paper-analysis-prompts-analysis.md) — 学術論文分析9手法を統合、/paper-analysisスキル新設
- [I Connected Claude to My Obsidian Vault (@damidefi)](../../research/2026-05-23-damidefi-claude-obsidian-second-brain-absorb-analysis.md) — second brain記事は採用0、Vault-wide矛盾検出は明示実行時限定にとどめる判断、creator-monetization型構造を確認
