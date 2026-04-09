---
source: "James (@jamescoder12) Twitter スレッド — 9 Prompts for Academic Paper Analysis"
date: 2026-04-09
status: integrated
---

## Source Summary

**主張**: 学術論文群を「要約」ではなく「構造分析」するための9つのプロンプトテンプレート。矛盾検出→引用系譜→ランドスケープ→統合→ギャップ→手法監査→知識地図→含意テスト→仮定破壊の順で多角的に分析する。本質的な価値は「構造化された問いの順序設計」にある。

**手法**:
1. Contradiction Finder — 複数論文間の矛盾検出 + WHY 分析
2. Citation Chain — 概念の知的系譜（導入→批判→精緻化→合意）追跡
3. Intake Protocol — 論文群のランドスケープマッピング（要約ではなく関係性可視化）
4. Master Synthesis — 分野全体の Consensus/Contested/Unresolved 3層統合
5. Gap Scanner — 未回答の研究問い + 原因診断（too hard/niche/overlooked）
6. Methodology Audit — 研究手法の分類・支配的手法・偏り・弱点
7. Knowledge Map Builder — 中核主張・支持柱・争点・フロンティアの階層地図
8. "So What" Test — 非専門家向け「1文証明・限界・最重要含意」3点要約
9. Assumption Killer — 暗黙仮定の抽出 + 反事実分析

**根拠**: 「何を分析するか」の設計として優れており、LLM に「どういう順序と構造で聞くか」が分析品質を決めるという考え方は正しい。ただし「どのツールで・どう検証するか」が抜けている。

**前提条件**: 複数の学術論文が入力として提供されること。LLM のコンテキスト長制限、ハルシネーション、Sycophancy のリスクに対する安全機構が必要。

## Gap Analysis (Pass 1: 存在チェック → Codex 修正後)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | 矛盾検出 | Partial | contradiction-mapping.md（知識ベース内矛盾向け）。外部論文間 claim-level 矛盾抽出なし |
| 2 | 引用系譜 | Partial | Scite MCP 統合あるが「導入→批判→精緻化→合意」の系譜追跡フローなし |
| 3 | ランドスケープマッピング | Partial | /research multi-source 集約が土台。intake schema と出力形式が不足 |
| 4 | コンセンサス抽出 | Partial | knowledge-pyramid Doctrine Synthesis 近似。3層分離形式は未対応 |
| 5 | リサーチギャップ分析 | Partial | /research+/absorb でギャップ検出あるが論文特化の原因診断なし |
| 6 | 手法論監査 | Partial | Scite support/contradiction で部分対応。専用ルーブリックなし |
| 7 | 知識地図 | Partial | knowledge-pyramid 4層あるが形式が異なる |
| 8 | 実世界含意テスト | Partial | /digest に So What? セクションあり。論文特化の3点固定形式なし |
| 9 | 暗黙仮定抽出 | Partial | /absorb+/deep-read で前提確認あるが複数論文横断の反事実分析なし |

## Already Strengthening Analysis (Pass 2: 強化チェック)

全項目が Partial のため Already 強化分析は該当なし。

## Phase 2.5: Refine Results

### Codex 批評の主要指摘
- #8 So What, #6 Methodology Audit, #3 Landscape Mapping を Gap → Partial に修正（既存基盤あり）
- #1 Contradiction を Already → Partial に降格（知識ベース内矛盾であり外部論文間矛盾ではない）
- 優先度: 個別プロンプト9本ではなく「論文コーパス専用ワークフロー」1本が最優先

### Gemini 補完: 記事の盲点
| 問題 | 深刻度 | 対策 |
|------|--------|------|
| 幽霊引用（存在しない論文の生成） | 高 | DOI/URL 原典照合必須化 |
| Lost in the Middle（長文中央部精度低下） | 高 | チャンキング戦略・分割分析 |
| Sycophancy（矛盾を調和させる傾向） | 中 | 複数モデル独立検証 |
| 再現性の欠如 | 中 | temperature=0、バージョン固定 |
| 著作権・OA 制限 | 中 | arXiv/PubMed Central/OA 優先 |

### Gemini 補完: 代替ツール
- NotebookLM: Intake + So What 向き（Audio Overview）
- Elicit: Methodology Audit 半自動化に最も近い
- Semantic Scholar API: Citation Chain 自動化
- Scite.ai: Contradiction Finder 半自動化
- Connected Papers: Knowledge Map 視覚化

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1-9 | 全9手法 | 採用（統合ワークフロー） | 個別追加ではなく /paper-analysis スキル1本に統合 |

## Plan

### Task 1: /paper-analysis スキル作成
- **Files**: `.config/claude/skills/paper-analysis/SKILL.md`, `templates/paper-analysis-report.md`, `references/analysis-prompts.md`
- **Changes**: 9プロンプトを統合した論文コーパス分析ワークフローを新規スキルとして実装。安全機構（原典照合ゲート、チャンキング、Sycophancy 防止）組み込み
- **Size**: M
- **Status**: completed
