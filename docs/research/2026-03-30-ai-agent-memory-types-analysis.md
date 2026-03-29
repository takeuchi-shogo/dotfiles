---
source: "AI Agent Memory Types Explained (article)"
date: 2026-03-30
status: integrated
---

## Source Summary

AI エージェントに必要な4層メモリアーキテクチャを解説する記事。

- **主張**: ステートレス LLM から有能なエージェントへの進化は、4層メモリ（Short-term / Episodic / Semantic / Procedural）の構築の物語
- **手法**: MemGPT 式 eviction、Reflection による episodic→semantic 昇格、GraphRAG、adaptive procedural memory + catastrophic drift 防止
- **根拠**: Stanford Generative Agents 研究、MemGPT OS metaphor
- **前提**: 長時間・マルチセッション自律エージェント

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | MemGPT 式自己管理型 eviction | N/A | Opus 4.6 auto-compaction + `context-compaction-policy.md` で管理。LLM が eviction API を呼ぶモデルは Claude Code アーキテクチャに不適 |
| 2 | Vector DB / Knowledge Graph / GraphRAG | N/A | ファイルベースメモリ + Grep で semantic retrieval を実現。Vector DB はオーバーキル |
| 3 | RLAIF（自己強化学習） | N/A | LLM 重み更新不可。AutoEvolve がテキストベースで procedural memory を更新 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示すポイント | 判定 |
|---|-------------|-------------------|------|
| A1 | Short-term: `context-compaction-policy.md` + `/check-context` | "lost in the middle" 対策 | Already (強化不要) — compaction 後の情報保持チェック・品質劣化兆候検出・fallback トリガーが網羅的 |
| A2 | Episodic: `lessons-learned.md` + `decision-journal.md` + `/eureka` | 失敗記録が最重要。Reflection で昇格 | Already (強化可能) → **統合済み** |
| A3 | Semantic: MEMORY.md + `references/` + `knowledge-pyramid.md` (Tier 0-3) | 汎用事実の体系的管理 | Already (強化不要) — Knowledge Pyramid + Doctrine Synthesis で完全カバー |
| A4 | Procedural: スキル体系 + AutoEvolve + `improve-policy.md` | catastrophic drift 防止 | Already (強化不要) — ドリフトガード（連続reject上限・目的メトリクス後退検出）+ human-in-the-loop (ルール10) が存在 |
| A5 | 4層連携: `workflow-guide.md` | 4層同時参照→推論→書き戻し | Already (参考情報として記録) |

## 4層メモリモデル対応表

記事の理論モデルと現セットアップの対応:

| 記事の層 | 認知的役割 | 現セットアップの対応 | キーファイル |
|---------|-----------|-------------------|------------|
| **Short-term** (作業デスク) | コンテキストウィンドウ。即座にアクセス可能だが有限 | Opus 4.6 auto-compaction + 品質劣化検知 | `context-compaction-policy.md`, `/check-context` |
| **Episodic** (日記) | タイムスタンプ付き経験記録。失敗の記録が最重要 | lessons-learned + decision-journal + `/eureka` | `lessons-learned.md`, `decision-journal.md` |
| **Semantic** (知識ベース) | 汎用・非時間的事実。信頼度による階層管理 | MEMORY.md + references/ + Knowledge Pyramid (Tier 0-3) | `knowledge-pyramid.md`, `MEMORY.md` |
| **Procedural** (筋肉記憶) | マルチステップワークフロー。適応的更新 + ドリフト防止 | スキル体系 + AutoEvolve + improve-policy ドリフトガード | `improve-policy.md`, `skills/*/SKILL.md` |

**注**: 記事の Reflection プロセス（episodic→semantic 昇格）は `knowledge-pyramid.md` の Tier 昇格条件（Tier 0→1: 3セッション観察、Tier 1→2: 定量確認、Tier 2→3: 3コンテキスト検証）として実装済み。

## Integration Decisions

- **A2 統合済み**: `lessons-learned.md` に「成功より失敗エピソードを優先記録」ルールを追記
- **A5 記録済み**: 4層対応表をこの分析レポート内に記録（独立 reference ファイルにするほどの分量ではない）
- **N/A スキップ**: MemGPT / GraphRAG / RLAIF はアーキテクチャ制約で適用不可
