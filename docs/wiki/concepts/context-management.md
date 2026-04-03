---
title: コンテキスト管理
topics: [memory]
sources: [2026-03-18-cursor-self-summarization-analysis.md, 2026-03-20-agent-engineering-practices-analysis.md, 2026-04-02-claude-code-memory-system-explained-analysis.md]
updated: 2026-04-04
---

# コンテキスト管理

## 概要

コンテキスト管理とは、LLMエージェントが限られたコンテキストウィンドウの中で長時間タスクを遂行するために、情報の保持・圧縮・取得を制御する手法群を指す。CursorのRL自己要約研究では「短く構造化された~1,000トークンの要約が長い指示付き要約（5,000+トークン）より50%エラーを削減する」という知見が実証されており、簡潔さが量より重要であることが示されている。コンテキストは4層（常駐/オンデマンド/ランタイム注入/記憶）に分離して管理するのが効果的であり、Claude Codeの内部実装では5層メモリアーキテクチャがハーネス側で厳格に制御されている。

## 主要な知見

- **簡潔さの優位性**: ~1,000トークンの構造化要約が5,000+トークンの詳細要約より優れ、50%のエラー削減を実証
- **コンテキスト4層分離**: 常駐情報・オンデマンド情報・ランタイム注入・記憶の4層を分離して管理する
- **3種の圧縮戦略**: スライディングウィンドウ・LLM要約・ツール結果置換を使い分ける
- **Context Anxiety対策**: モデルにより長いコンテキストへの感受性が異なり、適切なリセット/コンパクション戦略が必要
- **圧縮回数カウンター**: 3回以上の圧縮は新セッション移行の合図として機能する
- **MEMORY.mdインデックス**: 常時ロードされるため200行/25KB上限を超えると全ターンでトークンを消費する
- **Sonnetフィルタ**: frontmatterのdescriptionのみを判断材料としてtop 5の記憶ファイルを選択する
- **staleness warning**: 1日超のメモリに自動注入されるため、記憶の鮮度管理が重要
- **hasMemoryWritesSince()**: メイン/バックグラウンドの相互排他で重複記憶書き込みを防止する
- **AutoDream 4フェーズ**: Read→Gather→Merge→Pruneの24h+5セッションサイクルで記憶を自動整理する

## 実践的な適用

このリポジトリでは`pre-compact-save.js`がコンテキスト圧縮時の3段階ガイダンスと圧縮回数追跡を担い、Brevity Principleセクションで~1,000トークン目標を明示している。`output-offload.py`が大きな出力をファイルに退避してコンテキスト消費を抑制する。MEMORY.mdは現在157行で上限余裕があるが、description品質がSonnetフィルタの精度に直結するため全ファイルのdescription品質監査が重要。`context-compaction-policy.md`と`resource-bounds.md`に閾値とカウンター定数が定義されている。

## 関連概念

- [agent-memory](agent-memory.md) — エージェントのメモリシステムの設計と種別
- [context-engineering](context-engineering.md) — コンテキストを意図的に設計するアプローチ
- [long-running-agents](long-running-agents.md) — セッション跨ぎのコンテキスト継続戦略

## ソース

- [Cursor Self-Summarization](../../research/2026-03-18-cursor-self-summarization-analysis.md) — RLベースの自己要約で~1,000トークン要約が50%エラー削減を実証
- [Agent Engineering Practices](../../research/2026-03-20-agent-engineering-practices-analysis.md) — コンテキスト4層分離・3種圧縮戦略・記憶4分類の体系的整理
- [Claude Code Memory System Explained](../../research/2026-04-02-claude-code-memory-system-explained-analysis.md) — Claude Code内部の5層メモリアーキテクチャをソースマップ逆コンパイルから解析
