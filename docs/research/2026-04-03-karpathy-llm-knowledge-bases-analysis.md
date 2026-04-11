---
source: Andrej Karpathy "LLM Knowledge Bases" (X/Twitter post, 2026-04)
date: 2026-04-03
status: analyzed
---

## Source Summary

**主張**: LLM を使って個人ナレッジベースを構築・維持するパイプラインが研究効率を劇的に上げる。トークンの大半はコード操作ではなく知識操作に使うべき。

**手法**:
1. **Data Ingest**: raw/ にソースドキュメント（記事、論文、リポジトリ等）を収集。Obsidian Web Clipper で .md 変換、画像もローカル保存
2. **Wiki Compile**: LLM が raw/ から wiki をインクリメンタルにコンパイル。サマリ、バックリンク、概念記事、カテゴリ分類を自動生成
3. **Auto Index**: LLM がインデックスファイルと文書サマリを自動保守。~400K words/~100記事規模で RAG 不要の Q&A が機能
4. **Wiki Linting**: 一貫性チェック、欠損データ補完（Web検索併用）、新接続の発見、記事候補の提案
5. **Output Filing**: Q&A の出力結果を wiki にフィードバックして知識を蓄積強化
6. **Custom CLI Tools**: wiki 上の検索エンジン等を開発し、LLM に CLI ツールとして提供
7. **Obsidian as IDE**: raw データ、コンパイル済み wiki、ビジュアライゼーション（Marp スライド、matplotlib 等）を Obsidian で閲覧

**根拠**: Karpathy 本人の実践。~100記事、~400K words の wiki で複雑な Q&A が RAG なしで機能。

**前提条件**: ある程度の規模のリサーチトピックがあること、Obsidian 利用、LLM エージェント利用可能。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | raw/ → wiki コンパイル | **Gap** | docs/research/ にレポート蓄積あるが横断的 wiki 構造化なし |
| 2 | インデックス自動保守 | **Partial** | MEMORY.md がポインタ索引。docs/research/ 横断インデックスは手動 |
| 3 | Wiki Linting | **Partial** | /check-health がドキュメント鮮度チェック。内容レベルの一貫性は未対応 |
| 4 | 出力フィードバック | **Partial** | /absorb がレポート保存。Q&A 結果の体系的フィードバックなし |
| 5 | カスタム CLI ツール | **Already** | code-review-graph MCP + Obsidian MCP で同等機能あり |
| 6 | Obsidian as IDE | **Already (強化可能)** | /digest が NotebookLM 限定。/absorb → Obsidian ブリッジなし |
| 7 | 合成データ + FT | **N/A** | dotfiles/ハーネス設定が対象で FT のユースケースなし |

## Integration Decisions

全 Gap/Partial 項目 (#1-#4) + Already 強化 (#6) を取り込み。

## Plan

`docs/plans/2026-04-03-llm-knowledge-base-pipeline.md` に詳細プランを記載。
Wave 1 (wiki コンパイル+インデックス) → Wave 2 (Linting+Obsidian ブリッジ) → Wave 3 (フィードバックループ)。
