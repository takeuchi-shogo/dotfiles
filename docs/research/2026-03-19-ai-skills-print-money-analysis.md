---
source: "The AI Skills That Will Print Money in 2026-2027" (article, no URL - pasted text)
date: 2026-03-19
status: skipped
---

## Source Summary

**主張**: AI スキルは4階層ピラミッドに分かれ、2026-2027年は「プロンプト使い」から「AIシステム設計者」への移行期。単発のAI利用ではなく、自律的AIエコシステムの構築が高収益を生む。

**手法**:
- 4階層スキルピラミッド: Tier 1 Prompt Architecture ($30-80K) → Tier 2 Agent Orchestration ($60-150K) → Tier 3 Fine-tuning/Model Customization ($100-250K) → Tier 4 AI-Native Business Design ($200-500K+)
- 3層オートメーションスタック: Trigger / Processing / Action
- 3種カスタマイズ: RAG, Fine-tuning, Model Distillation
- AI-Native Architecture 4本柱: AI-First Product, Autonomous Ops, AI-Augmented Teams, Dynamic Models
- 90日プログレッションパス

**根拠**: 具体的ROI事例（コンテンツ制作10x、サポート78%自動化、コスト80%削減）

**前提条件**: ビジネス/起業志向の個人向け。エンジニアリングチームの生産性向上とは文脈が異なる

## Gap Analysis

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Prompt Architecture（XML構造化、CoT、コンテキスト管理） | Already | 全スキル・エージェントでXML構造化済み。subagent-framing でコンテキスト圧縮も実装 |
| 2 | 3層オートメーションスタック（Trigger/Processing/Action） | Already | hooks 4層アーキテクチャ（Pre/Post/Stop + 70スクリプト）で記事を上回る実装 |
| 3 | Agent Orchestration（マルチエージェント協調） | Already | 31エージェント + Implicit Coordinator + triage-router |
| 4 | Multi-Model Integration（モデル使い分け） | Already | Codex（推論）/ Gemini（1M分析）/ Claude（メイン）の3層委譲ルール |
| 5 | Self-Improving Systems（自己改善ループ） | Already | AutoEvolve 3フェーズ + session-learner + stagnation/gaming detector |
| 6 | RAG / ベクトルDB による知識検索 | Gap | Obsidian統合はテキスト検索のみ。セマンティック検索なし。ただし Gemini 1M コンテキストで代替可能 |
| 7 | Fine-tuning / Model Distillation | N/A | dotfiles/エージェントハーネスの文脈では不要 |
| 8 | AI-Native Business Design（4本柱） | N/A | ビジネス設計フレームワーク。個人開発環境最適化とは対象が異なる |
| 9 | Dynamic Business Models | N/A | ビジネスモデル論。dotfiles の範疇外 |
| 10 | AI-Augmented Team Structure | Partial | コンセプトは実装済み（1人+31エージェント）。チーム間ハンドオフは未文書化 |

## Integration Decisions

**スキップ**: 全項目。記事の前提（AI初学者→ビジネス構築）と当セットアップの目的（シニアエンジニアの開発生産性最大化）が根本的に異なる。Tier 1-2 は既に上回っており、Tier 3-4 は対象ドメインが異なる。唯一の Gap（RAG/セマンティック検索）も現時点では Grep + Gemini 1M コンテキストで十分カバーできている。
