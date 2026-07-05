---
title: ナレッジパイプライン
topics: [memory, productivity]
sources: [2026-04-03-karpathy-llm-knowledge-bases-analysis.md, 2026-04-05-karpathy-llm-wiki-gist-analysis.md, 2026-03-25-second-brain-thinking-partner-analysis.md, 2026-03-30-personal-ai-infrastructure-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 18
confidence: established
---

# ナレッジパイプライン

## 概要

LLM を使って個人の知識を収集・構造化・再利用するパイプライン設計。raw データの取り込みからインクリメンタルな wiki コンパイル、フィードバックによる知識強化まで一連のループとして捉える。単なる情報保存ではなく、セッション横断で思考を支援する「生きたシステム」として機能させることが目標。

## 主要な知見

- **Karpathy の 7ステップモデル**: Ingest → Wiki Compile → Auto Index → Wiki Linting → Output Filing → CLI Tools → Obsidian IDE。RAG なしで ~400K words の Q&A が機能する
- **情報保存 ≠ 思考実行**: 第二の脳の大半はファイリングキャビネットに過ぎず、真の思考支援には「今何が不確実か」を記録するコンテキストドキュメントが必要
- **思考プロトコルの明示化**: 自分の考えを先に述べる → 最強の反論を求める → 「何が見えていないか」で締める、の3段階
- **TELOS による深い目標理解**: MISSION/GOALS/BELIEFS/MODELS/STRATEGIES など 10 のアイデンティティファイルで個人の目標体系を構造化
- **学習シグナルの継続収集**: インタラクション毎に rating/sentiment/outcome を記録し、hot/warm/cold の3層で管理
- **セッション開始プロンプト**: CONTEXT → SESSION GOAL → MY CURRENT THINKING → WHAT I NEED FROM YOU の構造で stranger 問題を解消
- **インクリメンタル wiki コンパイル**: バッチ処理ではなくレポート追加のたびに差分更新し、横断的サマリ・バックリンク・概念記事を自動生成
- **コンテキスト圧縮閾値**: 83% で自動トリガーするなど、コンテキストウィンドウを管理する機構が不可欠
- **3層アーキテクチャ**: Raw Sources（不変）→ Wiki（LLM が保守）→ Schema（CLAUDE.md 等の運用規約）。Karpathy の "LLM Wiki" Gist で明確化
- **Query 操作の形式化**: INDEX → 関連ページドリルダウン → 合成回答 → 回答の wiki 再投入。Q&A 結果も知識資産として蓄積
- **log.md による操作追跡**: 時系列の操作ログ（ingest/compile/query/lint）で wiki の進化履歴を可視化
- **問いの順序設計が分析品質を決める**: 学術論文分析では「何を要約するか」ではなく「矛盾検出 → 引用系譜 → ランドスケープ → 統合 → ギャップ → 手法監査 → 知識地図 → 含意テスト → 仮定破壊」という問いの順序と構造こそが分析の質を左右する。個別プロンプトの寄せ集めではなく1本のワークフローに統合し、幽霊引用（存在しない論文の生成）対策として原典照合ゲート・チャンキング・複数モデル独立検証（Sycophancy 対策）を組み込む
- **コンテキストデザインの5層モデル**: Context Infrastructure（知識の収集・版管理）→ Creation & Editing → Skill Distribution → Action Governance → Execution の5層で、組織でも個人でもボトルネックはモデル性能ではなく知識の構造化・配布・ガバナンスにある。中でも Connector Inventory（MCP 接続先の分散と drift 検査）と Telemetry 信号品質（「ある」≠「使える品質」）が下流タスク全ての前提となる基盤層で、ここを直さずに応用層へ進むと成果が無意味になる
- **知識グラフ変換ツールより既存パイプラインへの関係抽出追加**: 71.5x トークン削減を謳う専用ツール導入より、既存の要約パイプラインに concept→concept の関係抽出（EXTENDS/CONTRADICTS/APPLIES 等）を追加し、EXTRACTED/INFERRED/AMBIGUOUS の三値 provenance タグを confidence score と直交させて併記する方が費用対効果が高い。ベンチマーク数値はコーパス条件（構成・件数）を必ず併記し数値の一人歩きを防ぐ
- **自己進化型ソース収集の罠**: 情報ソース（キーワード・サイト等）の採用実績で自動昇格/降格する設計は、評価指標ゲーミング（LLM が要約しやすい浅いソースへ偏る）とコールドスタート問題を招く。read-only 計測 → human-in-loop 昇格 → MAB（UCB1/Thompson）探索という段階移行が安全で、昇格だけでなく「死んだソースの退役」という在庫管理の視点こそが本質
- **フィードバックループは軽量記入・提案止まりが安全**: 定期ブリーフ末尾に3行程度の軽量 annotation（useful/noise/missing）を残し、週次でそれを集計してコンテキストファイルの更新差分を「提案」する設計は有効。ただし自動更新は手動負担増による更新停止や意図しないコンテキスト歪みを招くため、user 承認制に限定する
- **自己改善ループは Analyzer と DB の lineage が核**: 学習（retrieval 品質）→分析（batch だけでは停滞するため即時蒸留が必要）→データベース（保存だけでなく parent_id・novelty_score 等の系譜追跡）の3点が自己改善サイクルの本体。サンプリング最適化（UCB1 等）の寄与は全体の1割程度に過ぎず、探索効率の大半は初期知識基盤の質で説明される。バンディット最適化はデータ整備（30件以上の outcome 蓄積等）の後に回す
- **signal density と enforcement の分離に注意**: パイプラインは volume ではなく signal density で質が決まるという原則を codify していても、それを実行する mechanism（pruning script・hook 登録等）が実際に配線されていなければ drift（閾値超過の放置）が起きる。原則の明文化と enforcement の接続は別物として検証する

## 実践的な適用

dotfiles リポジトリでは Karpathy の3層を完全に実装済み: `docs/research/` = Raw Sources、`docs/wiki/` = Wiki（149レポート、26概念、12トピック）、`CLAUDE.md` + `references/` = Schema。`/absorb` → `/compile-wiki` パイプラインが Ingest を、`/compile-wiki query` が Query を、`/compile-wiki lint` が Lint をそれぞれ担当。`docs/wiki/log.md` で操作履歴を時系列追跡し、wiki の進化を可視化する。加えて `/paper-analysis` スキルが学術論文コーパスの構造分析を、`/absorb` の Saturation Gate + Codex/Gemini 並列批評（Phase 2.5）が評価指標ゲーミングや前提の誤りを検出するセカンドオピニオン層を担っている。

## 関連概念

- [obsidian-integration](obsidian-integration.md) — Obsidian を IDE として wiki を閲覧・編集する統合層
- [agent-memory](agent-memory.md) — セッション横断でコンテキストを保持するメモリアーキテクチャ
- [context-engineering](context-engineering.md) — コンテキストウィンドウの効率的な利用設計

## ソース

- [Karpathy "LLM Knowledge Bases" 分析](../../research/2026-04-03-karpathy-llm-knowledge-bases-analysis.md) — 7ステップの個人 wiki パイプライン。RAG 不要の Q&A アーキテクチャ
- [Karpathy "LLM Wiki" Gist 分析](../../research/2026-04-05-karpathy-llm-wiki-gist-analysis.md) — 3層アーキテクチャ・Query操作・log.md の形式化
- [第二の脳・思考パートナー分析](../../research/2026-03-25-second-brain-thinking-partner-analysis.md) — 思考プロトコルと永続的環境の設計原則
- [Personal AI Infrastructure 分析](../../research/2026-03-30-personal-ai-infrastructure-analysis.md) — PAI フレームワーク。TELOS・学習シグナル・Scaffolding > Model 原則
- [ASI-Evolve: AI Accelerates AI (arXiv:2603.29640)](../../research/2026-04-08-asi-evolve-autoevolve-integration-analysis.md) — AI自己進化ループを分析、Analyzer/DB連携など5項目を段階採用
- [Obsidian + Claude Code is the New Meta (Noah)](../../research/2026-04-09-obsidian-claude-code-meta-analysis.md) — Obsidian統合記事を分析、Vault自動メンテナンス等採用
- [9 Prompts for Academic Paper Analysis (James, Twitter)](../../research/2026-04-09-paper-analysis-prompts-analysis.md) — 学術論文分析9手法を統合、/paper-analysisスキル新設
- [I Want to Extend My Claude Sessions (NotebookLM統合ガイド)](../../research/2026-04-10-notebooklm-claude-extend-sessions-analysis.md) — NotebookLM連携記事を分析、DBS rubricのみ採用
- [『Build Agents that never forget』(Akshay Pachaar, Cognee) 分析](../../research/2026-04-14-cognee-agent-memory-analysis.md) — Cognee記事、vector/graph DB導入は見送り、usage-based重み付け等を採用
- [Modified Karpathy Method セカンドブレイン記事 (Kevin) 分析](../../research/2026-04-14-karpathy-second-brain-modified-analysis.md) — Karpathy法改変記事分析、frontmatterでなく_drafts分離方式で採用
- [コンテキストデザイン組織活用記事 (久保星哉) 分析](../../research/2026-04-17-context-design-absorb-analysis.md) — コンテキストデザイン記事分析、MCP分散とTelemetry品質を最優先Gapと特定
- [Obsidian × Claude Code — .claude ディレクトリ設計パターン (@akira_papa_AI)](../../research/2026-04-21-obsidian-claudecode-absorb-analysis.md) — Obsidianのcommands/skills設計を分析、Inbox連携等5タスクを採用
- [graphify (知識グラフ変換ツール) absorb分析](../../research/2026-04-27-graphify-absorb-analysis.md) — 知識グラフツールgraphifyを分析、本体棄却し3件軽量採用
- [育てるClaude Codeから勝手に育つClaude Codeへ (@0xfene)](../../research/2026-05-13-grown-claude-code-metabolism-absorb-analysis.md) — skill代謝記事からGotchas欄と週次friction digestを採用
- [Codex Research Agent Workflow (中国語記事、10分構築)](../../research/2026-05-28-codex-research-agent-workflow-absorb-analysis.md) — 朝ブリーフ記事、注釈欄と週次差分提案など3件採用
- [Turn Every Note Into Something You Actually Use (@cyrilXBT)](../../research/2026-05-30-cyrilxbt-notes-into-output-absorb-analysis.md) — ノート活用術記事、キャプチャ規約と意思決定フィード採用
- [@damidefi Delete 90% of Your Obsidian Notes](../../research/2026-05-31-damidefi-delete-90-vault-absorb-analysis.md) — Vault削除記事のsignal density原則を分析、MEMORY.mdを223→154行に圧縮
- [生成AIトレンド自己進化型情報収集 (Zenn, tokium_dev)](../../research/2026-06-04-ai-tech-researcher-self-evolving-absorb-analysis.md) — AI技術情報収集の自己進化記事を分析、read-only MVPとdrift監視のみ採用
