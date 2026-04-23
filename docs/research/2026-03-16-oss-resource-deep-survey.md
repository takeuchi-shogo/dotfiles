---
status: active
last_reviewed: 2026-04-23
---

# OSS リソース深層調査レポート

**調査日**: 2026-03-16
**調査対象**: ソーシャルメディア投稿から抽出した正規リソース 42 件
**調査方法**: WebFetch 直接取得 + 4 並列リサーチエージェント（ナレッジベース補完）
**目的**: dotfiles / Claude Code エージェントシステムへの適用可能性評価

---

## 目次

1. [調査概要](#調査概要)
2. [リソース一覧と評価](#リソース一覧と評価)
3. [活かせるもの](#1-活かせるもの)
4. [改善するもの](#2-改善するもの)
5. [残しておくもの](#3-残しておくもの)
6. [知見として知っておくべきもの](#4-知見として知っておくべきもの)
7. [アクションアイテム](#アクションアイテム)
8. [ブックマーク最終リスト](#ブックマーク最終リスト)

---

## 調査概要

ソーシャルメディア投稿（Hinglish 混在のリソースまとめ）から危険なリンク（海賊版・不明 Google Drive・Mega・bit.ly・メール収集系）を除外し、公式・正規リソースのみを深層調査した。

### 除外したリソース

| カテゴリ | 例 | リスク |
|---|---|---|
| 海賊版サイト | `downloadlynet.ir` | 著作権侵害・マルウェア |
| 不明 Google Drive | 出所不明の PDF/ドキュメント | マルウェア・著作権 |
| Mega.nz | Udemy コース等 | 海賊版の可能性 |
| bit.ly 短縮リンク | money making guides | アフィリエイト詐欺 |
| Beehiiv 登録リンク | メール収集目的 | スパム |

### 調査対象の正規リソース（42 件）

- **GitHub リポジトリ**: 30 件
- **Coursera 公式コース**: 9 件
- **無料オンライン書籍**: 7 件
- **学習プラットフォーム**: 12 件
- **その他正規サイト**: 数件

---

## リソース一覧と評価

### A. プロンプトエンジニアリング・Claude 関連

| リソース | ★ | 内容 | dotfiles 関連度 |
|---|---|---|---|
| [anthropics/anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook) | 35.1k | Claude 公式レシピ集。Agent SDK, extended_thinking, patterns/agents/ | **極高** |
| [anthropics/prompt-eng-interactive-tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial) | 33.5k | 9 章 + 付録の公式チュートリアル | **高** |
| [dair-ai/Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide) | 71.7k | 学術論文ベースの技法カタログ (CoT, ToT, ReAct, APE 等) | **高** |
| [f/awesome-chatgpt-prompts](https://github.com/f/awesome-chatgpt-prompts) | 143k | プロンプトライブラリ。MCP Server (`prompts.chat/api/mcp`) あり | **中** |
| [0xeb/TheBigPromptLibrary](https://github.com/0xeb/TheBigPromptLibrary) | 5k+ | リークされた実運用システムプロンプトの構造パターン | **中** |
| [langgptai/awesome-claude-prompts](https://github.com/langgptai/awesome-claude-prompts) | 2k+ | Claude 専用。LangGPT 構造化フォーマット | **中高** |
| [learnprompting.org](https://learnprompting.org/) | — | 体系的コース。Prompt Hacking 防御パターンが価値高い | **中** |
| [ai.google.dev/gemini-api/prompts](https://ai.google.dev/gemini-api/prompts) | — | Gemini プロンプトギャラリー | **低** |
| [google/generative-ai-docs](https://github.com/google/generative-ai-docs) | 3k+ | Gemini 公式ドキュメント | **低** |

### B. AI/ML 学習・LLM アーキテクチャ

| リソース | ★ | 内容 | dotfiles 関連度 |
|---|---|---|---|
| [microsoft/ai-agents-for-beginners](https://github.com/microsoft/ai-agents-for-beginners) | — | 15 レッスン。MCP/A2A/メモリ/Metacognition | **高** |
| [microsoft/generative-ai-for-beginners](https://github.com/microsoft/generative-ai-for-beginners) | — | 21 レッスン。RAG, AI Agents, Security 含む | **中** |
| [microsoft/ML-For-Beginners](https://github.com/microsoft/ML-For-Beginners) | — | ML 基礎コース | **低** |
| [rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch) | — | Transformer 実装。DPO, LoRA, MoE 含む | **中** |
| [langchain-ai/langchain](https://github.com/langchain-ai/langchain) | 130k | LCEL, LangGraph, 200+ 統合 | **中** |
| [run-llama/llama_index](https://github.com/run-llama/llama_index) | — | RAG フレームワーク | **中** |
| [deepset-ai/haystack](https://github.com/deepset-ai/haystack) | — | RAG/NLP パイプライン | **低** |
| [vllm-project/vllm](https://github.com/vllm-project/vllm) | — | 高速推論エンジン | **低** |
| [ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp) | — | ローカル LLM 推論 | **低** |
| [chiphuyen/aie-book](https://github.com/chiphuyen/aie-book) | — | AI Engineering 体系書 | **中** |

### C. AI アプリ・プロジェクト・RAG 技法

| リソース | ★ | 内容 | dotfiles 関連度 |
|---|---|---|---|
| [NirDiamant/GenAI_Agents](https://github.com/NirDiamant/GenAI_Agents) | 6k+ | エージェント設計パターン百科事典 | **極高** |
| [NirDiamant/RAG_Techniques](https://github.com/NirDiamant/RAG_Techniques) | 8k+ | 34 種の RAG テクニック実装 | **極高** |
| [Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) | 10k+ | LLM アプリ集。MCP 統合・メモリパターン含む | **中** |
| [Arindam200/awesome-ai-apps](https://github.com/Arindam200/awesome-ai-apps) | 3k+ | AI アプリキュレーション集 | **低** |
| [GokuMohandas/Made-With-ML](https://github.com/GokuMohandas/Made-With-ML) | 37k | MLOps 包括コース | **中** |
| [eriklindernoren/ML-From-Scratch](https://github.com/eriklindernoren/ML-From-Scratch) | 24k | ML アルゴリズムのスクラッチ実装 | **低** |
| [probml/pyprobml](https://github.com/probml/pyprobml) | 6k+ | 確率的 ML 理論のコード集 | **低** |
| [jakevdp/PythonDataScienceHandbook](https://github.com/jakevdp/PythonDataScienceHandbook) | 42k | データサイエンス基礎教科書 | **低** |
| [arxiv:2501.09223 (DeepSeek-R1)](https://arxiv.org/pdf/2501.09223) | — | RL による LLM 推論能力獲得 | **中** |

### D. 開発ツール・セキュリティ・学習

| リソース | ★ | 内容 | dotfiles 関連度 |
|---|---|---|---|
| [PortSwigger Web Security Academy](https://portswigger.net/web-security) | — | セキュリティラボ。Web LLM attacks (4 labs) 含む | **高** |
| [roadmap.sh](https://roadmap.sh/) | — | Claude Code, AI Agents, Prompt Engineering ロードマップ | **中** |
| [EbookFoundation/free-programming-books](https://github.com/EbookFoundation/free-programming-books) | 384k | 50 言語 10k+ リソース | **低** |
| [gto76/python-cheatsheet](https://github.com/gto76/python-cheatsheet) | — | Python チートシート | **低** |
| [tryhackme.com](https://tryhackme.com/) | — | セキュリティ学習プラットフォーム | **低** |
| [cs50.harvard.edu/ai](https://cs50.harvard.edu/ai/) | — | Harvard CS50 AI | **低** |

### E. 無料オンライン書籍（著者公認）

| 書籍 | URL | 内容 |
|---|---|---|
| Dive Into Deep Learning | [d2l.ai](https://d2l.ai) | DL 包括教科書 |
| Deep Learning (Goodfellow) | [deeplearningbook.org](https://www.deeplearningbook.org) | DL 理論 |
| Mathematics for ML | [mml-book.github.io](https://mml-book.github.io) | ML の数学基礎 |
| Automate the Boring Stuff | [automatetheboringstuff.com](https://automatetheboringstuff.com/) | Python 自動化 |
| Eloquent JavaScript | [eloquentjavascript.net](https://eloquentjavascript.net/) | JS 教科書 |
| Mathematics for CS (MIT) | [MIT PDF](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf) | CS 数学 |

---

## 1. 活かせるもの

dotfiles / Claude Code 設定に直接適用可能な知見。

### A. エージェント設計パターン — GenAI_Agents

#### ATLAS パターン（4 エージェント協調）
- **Coordinator, Planner, Notewriter, Advisor** の協調が、現在の triage-router → specialist agents と類似
- **差分**: Notewriter（知識永続化専門）が独立。AutoEvolve に「知識書き出し専門フェーズ」を追加する余地

#### Metacognition パターン（自己反省・適応）
- Microsoft ai-agents-for-beginners Lesson 9 に詳細実装
- 現在の AutoEvolve は「セッション後の学習」だが、**タスク実行中の自己修正**は未実装

#### Self-Reflective Agent パターン
- 各ステップの出力を評価し、品質不十分なら自己修正
- `completion-gate.py`（Stop hook）の拡張として、タスク完了前に LLM 自身に品質評価させるパターンに応用可能
- `/review` のレビュー結果の自己評価。信頼度 80 未満フィルタ + 妥当性再評価ステップの追加

#### Plan-and-Execute パターン
- 計画 → 逐次実行 → 再計画のループ
- `plan-lifecycle.py` hook の強化として構造化可能

#### Human-in-the-Loop 設計
- `/autonomous` モードに明示的な人間承認ポイント設計（現在は Lock + Budget cap）

### B. RAG テクニック — RAG_Techniques

#### Corrective RAG (CRAG)
- 検索結果の品質を判定し、低品質なら再検索
- `/research` スキルの検索精度向上に直接適用可能
- `error-to-codex.py` のフォールバック戦略として:
  1. `error-fix-guides.md` で完全一致
  2. キーワードでファジー検索
  3. Codex/Gemini に修正ガイド生成を委譲
  4. 生成結果を `learnings/recovery-tips.jsonl` に保存

#### Self-RAG
- 生成結果を自己評価して改善
- `/review` の false positive 削減に応用可能

#### Agentic RAG
- エージェントが自律的に検索戦略を選択
- 現在の `/research` は固定パイプラインだが、動的戦略選択への改善余地

#### HyDE (Hypothetical Document Embedding)
- 「理想的な回答文書」を仮生成し、その embedding で検索
- `search-first-gate.py` の検索精度向上に応用

### C. プロンプトエンジニアリング — anthropic-cookbook + tutorial

#### Sub-agent Architecture パターン
- `patterns/agents/`: Anthropic 公式のエージェントパターン集
- `claude_agent_sdk/`: Claude Agent SDK のサンプルコード
- 現在のエージェント定義の検証リファレンスとして最適

#### Extended Thinking パターン
- `extended_thinking/` ディレクトリ
- Codex との使い分けの判断材料

#### Speaking for Claude（プライミング）
- Claude の応答冒頭を事前に書いておくことで出力フォーマットと品質を制御
- `/review`, `/spec`, `/validate` で assistant ターンの冒頭をプライミング

#### Data/Instruction 分離の徹底
- XML タグでデータと指示を明確に分離
- 現在の CLAUDE.md は既に活用中だが、スキル定義内でさらに徹底可能

#### Prompt Caching 戦略
- 長いシステムプロンプトや references のキャッシュ効率化
- hook で毎回大きなコンテキストを注入する場面での最適化

### D. MCP サーバー統合 — awesome-chatgpt-prompts

- `prompts.chat/api/mcp` でプロンプトライブラリを MCP 経由で利用可能
- Claude Code に MCP として追加すれば、プロンプトパターンを直接参照可能

### E. Web Security チェックリスト — PortSwigger

#### Web LLM attacks (4 labs)
- LLM 特有の脆弱性ラボが存在
- `security-reviewer` の Agentic Security チェックリストに追加可能

#### GraphQL API vulnerabilities
- `graphql-expert` スキルのレビューチェックリスト強化に直接適用

### F. LangGPT 構造化フォーマット — awesome-claude-prompts

- `Role > Profile > Rules > Workflow > Init` の明確なセクション構造
- エージェント定義ファイル (`.config/claude/agents/*.md`) の一貫性と可読性向上

---

## 2. 改善するもの

現在の設定を改善するためのヒント。

### A. Context Engineering の体系化

Microsoft ai-agents-for-beginners Lesson 12「Context Engineering for AI Agents」が独立レッスンとして存在。現在の Progressive Disclosure + CLAUDE.md でのコンテキスト管理に対し、**コンテキスト予算の動的調整**を改善するヒント。

### B. エージェントの信頼性向上

- Microsoft Lesson 6「Building Trustworthy AI Agents」: 安全性・透明性・信頼性の体系的フレームワーク
- 現在の golden-principles.md (GP-001〜010) は品質中心だが、**信頼性軸**（hallucination rate, tool call success rate）の追加を検討

### C. Agentic Protocol 対応

- Microsoft Lesson 11 が **MCP, A2A (Agent-to-Agent), NLWeb** の 3 プロトコルをカバー
- 現在は MCP のみ対応。A2A プロトコルは将来のマルチエージェント間通信に関連

### D. ハルシネーション防止の体系化

- prompt-eng-interactive-tutorial Ch.8 の技法
- 「根拠が不十分な場合は指摘を省略せよ」ルールを review チェックリストに追加
- 信頼度 80 未満フィルタ + 根拠チェーンの明示を義務付け

### E. Self-Consistency による品質向上

- 同じ質問を複数回推論し、多数決で回答を決定
- `/review` で同一観点の複数回実行 → 一致する指摘のみ採用で false positive 削減

### F. 検索品質の定量評価 — RAGAS

- `/research` の出力品質を Faithfulness, Relevance, Precision, Completeness で定量評価
- `evaluator_metrics.py` への 4 軸評価追加

### G. MLOps 的実験追跡 — Made-With-ML

- AutoEvolve の改善サイクルに対する効果測定の体系化
- ベースライン指標 → 変更内容 → 結果指標 → 差分を `metrics/experiments/` に構造化記録

### H. Prompt Injection 防御強化 — learnprompting.org

- Sandwich Defense (指示を入力の前後に配置)
- XML Tagging Defense, Random Sequence Enclosure
- `/research`, `/autonomous` で入力データを `<user_input>` タグで囲み防御

### I. awesome-llm-apps のメモリシステム

- **Shared memory across instances**: エージェント間の共有メモリ設計パターン
- **RAG failure diagnostics**: 検索失敗の診断パターン

### J. LangChain/LangGraph のパターン参照

- LangGraph の **state-managed graph-based execution** は hook ベースのワークフロー制御の代替設計として参考
- LCEL のチェーン合成パターンはスキルの組み合わせ設計に示唆

### K. Multi-Agent Debate パターン

- 設計判断が分かれる場面で `backend-architect` vs `codex-risk-reviewer` に同じ問題を投げて議論させる
- `/spec` でのアーキテクチャ選択に応用

---

## 3. 残しておくもの

ブックマークとして保持すべきリソース。

### 必須（定期的に参照）

| リソース | ★ | 理由 |
|---|---|---|
| [anthropics/anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook) | 35.1k | Claude 公式レシピ集。Agent SDK, extended_thinking, patterns/agents/ |
| [NirDiamant/RAG_Techniques](https://github.com/NirDiamant/RAG_Techniques) | 8k+ | 34 種の RAG テクニック。実装付き辞書 |
| [NirDiamant/GenAI_Agents](https://github.com/NirDiamant/GenAI_Agents) | 6k+ | エージェント設計パターンの百科事典 |
| [PortSwigger Web Security Academy](https://portswigger.net/web-security) | — | 実践的セキュリティラボ。Web LLM attacks 含む |

### 高（設計変更時に参照）

| リソース | ★ | 理由 |
|---|---|---|
| [microsoft/ai-agents-for-beginners](https://github.com/microsoft/ai-agents-for-beginners) | — | 15 レッスン。MCP/A2A/メモリ/Metacognition |
| [dair-ai/Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide) | 71.7k | プロンプト技法の学術辞書 |
| [anthropics/prompt-eng-interactive-tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial) | 33.5k | Claude 公式チュートリアル |
| [roadmap.sh](https://roadmap.sh/) | — | Claude Code, AI Agents, Prompt Engineering ロードマップ |

### 中（必要時に参照）

| リソース | ★ | 理由 |
|---|---|---|
| [Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) | 10k+ | LLM アプリ実装集。MCP 統合パターン含む |
| [rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch) | — | Transformer 実装理解。DPO, LoRA 含む |
| [GokuMohandas/Made-With-ML](https://github.com/GokuMohandas/Made-With-ML) | 37k | MLOps ベストプラクティス |
| [langchain-ai/langchain](https://github.com/langchain-ai/langchain) | 130k | LangGraph のグラフ実行パターン参照 |
| [learnprompting.org](https://learnprompting.org/) | — | Prompt Hacking 防御セクション |
| [chiphuyen/aie-book](https://github.com/chiphuyen/aie-book) | — | AI Engineering 体系書 |
| [langgptai/awesome-claude-prompts](https://github.com/langgptai/awesome-claude-prompts) | 2k+ | LangGPT 構造化フォーマット |

### 低（辞書的）

| リソース | ★ | 理由 |
|---|---|---|
| [EbookFoundation/free-programming-books](https://github.com/EbookFoundation/free-programming-books) | 384k | 50 言語 10k+ リソース |
| [f/awesome-chatgpt-prompts](https://github.com/f/awesome-chatgpt-prompts) | 143k | MCP Server (`prompts.chat/api/mcp`) |
| [arxiv:2501.09223 (DeepSeek-R1)](https://arxiv.org/pdf/2501.09223) | — | AutoEvolve の理論的裏付け |

---

## 4. 知見として知っておくべきもの

### A. エージェント設計の業界動向

#### Metacognition パターンの主流化
エージェントが自身の推論プロセスを監視・修正する設計が Microsoft, NirDiamant 両方で独立トピック。現在の Claude Code 設定は「事後学習」中心だが、**リアルタイム自己修正**が次のフロンティア。

#### A2A (Agent-to-Agent) プロトコル
Google 主導の標準化。MCP（ツール統合）+ A2A（エージェント間通信）が 2025-2026 の 2 大プロトコル。

#### エージェントパターンの収束
Supervisor, Hierarchical, Peer-to-Peer の 3 パターンに収束しつつある。dotfiles の 30+ エージェント体制は Hierarchical に近い。

### B. RAG の進化方向

#### RAG 成熟度モデル

```
L1 Basic     ← 現在の /research
L2 Optimized ← Query Transformation + Re-ranking で到達可能
L3 Adaptive  ← Self-RAG / CRAG（P0-P1 アクション）
L4 Agentic   ← エージェントがパイプライン全体を制御（中期目標）
L5 Multi-Modal ← テキスト+画像+構造化データ統合（長期）
```

#### Agentic RAG の標準化
単純な retrieve → generate ではなく、エージェントが検索戦略を動的に選択・修正するパターンが主流に。

#### GraphRAG
Microsoft が推進するグラフベースの RAG。知識の構造化・関係性推論に強い。

### C. LLM セキュリティの新カテゴリ

- PortSwigger が **Web LLM attacks** を正式カテゴリ化（4 labs）
- LLM を使った Web アプリ特有の攻撃パターン（prompt injection via web, indirect injection）が体系化
- 現在の `agentic_security_insights.md` と組み合わせるとより包括的なセキュリティレビューが可能

### D. RL による推論能力の自発的出現 — DeepSeek-R1

- 明示的に CoT を教えなくても、RL の報酬設計だけで推論行動が自発的に出現（"aha moment"）
- **AutoEvolve の設計の理論的裏付け**: 失敗からの学習ループが自発的な品質改善につながる
- ただし RL のみだと不安定 → cold-start データ（= CLAUDE.md の core_principles）とのハイブリッドが重要
- 蒸留により小モデルでも推論能力を獲得可能 → ローカルエージェントへの応用可能性

### E. 教育設計のパターン

- **Feynman-style teaching loops**（GenAI_Agents）: 「教える」ことで理解を検証。複雑なコードレビューの説明生成に応用可能
- **70% 理解度チェックポイント**: 段階的理解確認のパターン

### F. プロダクション AI エンジニアリング

- **chiphuyen/aie-book**: evaluation, monitoring, deployment のベストプラクティスを体系化
- **LLMOps**: Microsoft Lesson 14 が LLM アプリのライフサイクル管理を定義

### G. roadmap.sh の AI 関連ロードマップ

**Claude Code**, **AI Agents**, **AI Red Teaming**, **Prompt Engineering** が独立ロードマップとして存在。dotfiles 設計の網羅性チェックに使える。

### H. プロンプト技法の知見

#### Tree of Thoughts (ToT)
推論を木構造で探索し、各分岐を評価して最適パスを選択。複雑な設計判断で有用。

#### Directional Stimulus Prompting
望ましい出力方向への「ヒント」をプロンプトに含める。レビューで特定観点に注意を向けさせるのに有用。

#### Few-shot の配置位置
Claude は末尾の例に最も強く影響される（recency bias）。スキル定義での出力フォーマット例の配置設計に影響。

#### Prompt Chaining vs. Mega-Prompt
チェーンは各ステップの品質が高くデバッグ容易。Mega-Prompt はレイテンシ低。現在のワークフロー（Plan → Implement → Test → Review）は既にチェーンパターン。

---

## アクションアイテム

### P0（即座に適用可能）

| アクション | 関連リソース | 対象 |
|---|---|---|
| `anthropic-cookbook/patterns/agents/` を精読し現在のエージェント定義との差分を検証 | anthropic-cookbook | エージェント設計全体 |
| PortSwigger の Web LLM attacks を `security-reviewer` チェックリストに追加 | PortSwigger | `references/review-checklists/` |
| `error-to-codex.py` に CRAG 段階エスカレーション追加 | RAG_Techniques | `scripts/policy/error-to-codex.py` |

### P1（短期改善）

| アクション | 関連リソース | 対象 |
|---|---|---|
| CRAG / Self-RAG パターンを `/research` に統合検討 | RAG_Techniques | `/research` スキル |
| Metacognition パターンを AutoEvolve の「実行中自己修正」として検討 | GenAI_Agents, MS ai-agents | AutoEvolve |
| Speaking for Claude をスキルに適用 | prompt-eng-tutorial | `/review`, `/spec` |
| Self-Consistency を `/review` に導入 | Prompt-Engineering-Guide | `/review` |
| RAGAS 4 軸評価を `evaluator_metrics.py` に追加 | RAG_Techniques | `scripts/lib/evaluator_metrics.py` |

### P2（中期改善）

| アクション | 関連リソース | 対象 |
|---|---|---|
| `prompts.chat` MCP サーバーを Claude Code に追加 | awesome-chatgpt-prompts | MCP 設定 |
| LangGPT 構造化フォーマットをエージェント定義に導入 | awesome-claude-prompts | `.config/claude/agents/*.md` |
| Prompt Injection 防御を `/research`, `/autonomous` に追加 | learnprompting.org | スキル定義 |
| HyDE で検索強化 | RAG_Techniques | `search-first-gate.py` |
| A2A プロトコルの動向ウォッチ | MS ai-agents Lesson 11 | — |

### P3（長期検討）

| アクション | 関連リソース | 対象 |
|---|---|---|
| Multi-Agent Debate を `/spec` に | GenAI_Agents | `/spec` スキル |
| MLOps 的実験追跡を AutoEvolve に | Made-With-ML | `metrics/experiments/` |
| GraphRAG の検討 | RAG_Techniques | `/research` スキル |

---

## ブックマーク最終リスト

```
必須 (定期的に参照)
├── anthropics/anthropic-cookbook        — 公式エージェントパターン・Agent SDK
├── NirDiamant/RAG_Techniques           — RAG 34技法の実装辞書
├── NirDiamant/GenAI_Agents             — エージェント設計パターン百科事典
└── PortSwigger Web Security Academy    — LLM attacks 含むセキュリティラボ

高 (設計変更時に参照)
├── microsoft/ai-agents-for-beginners   — MCP/A2A/メモリ/Metacognition
├── dair-ai/Prompt-Engineering-Guide    — プロンプト技法の学術辞書 (71.7k★)
├── anthropics/prompt-eng-tutorial      — Claude 公式チュートリアル
└── roadmap.sh                          — Claude Code/AI Agents ロードマップ

中 (必要時に参照)
├── Shubhamsaboo/awesome-llm-apps       — LLM アプリ実装集 (MCP統合含む)
├── rasbt/LLMs-from-scratch             — Transformer 実装理解
├── GokuMohandas/Made-With-ML           — MLOps ベストプラクティス (37k★)
├── langchain-ai/langchain              — LangGraph のグラフ実行パターン
├── learnprompting.org                  — Prompt Hacking 防御パターン
├── chiphuyen/aie-book                  — AI Engineering 体系書
└── langgptai/awesome-claude-prompts    — LangGPT 構造化フォーマット

低 (辞書的)
├── EbookFoundation/free-programming-books — 50言語 10k+リソース (384k★)
├── f/awesome-chatgpt-prompts           — MCP Server (prompts.chat/api/mcp)
└── DeepSeek-R1 論文                    — AutoEvolve の理論的裏付け
```

---

## 付録: 安全な Coursera 公式コース一覧

| コース | 提供元 |
|---|---|
| Introduction to Generative AI | Google Cloud |
| Prompt Engineering for Generative AI | Google Cloud |
| Google AI Essentials | Google |
| Crash Course on Python | Google |
| Machine Learning Specialization | DeepLearning.AI / Andrew Ng |
| Google Cloud Fundamentals | Google Cloud |
| Google Data Analytics Professional Certificate | Google |
| Google Cybersecurity Professional Certificate | Google |
| AI For Everyone | DeepLearning.AI |
| Deep Learning Specialization | DeepLearning.AI |
| Generative AI for Software Developers | DeepLearning.AI |
| AI Agent Developer Specialization | DeepLearning.AI |
| Automating Tasks with Python | Google |
| Big Data Introduction | UC San Diego |
| Business Foundations | Wharton |

## 付録: 安全な学習プラットフォーム

| プラットフォーム | URL | 内容 |
|---|---|---|
| Harvard CS50 AI | cs50.harvard.edu/ai | AI 基礎 |
| Elements of AI | elementsofai.com | AI 入門（Helsinki 大学） |
| Kaggle Learn | kaggle.com/learn | ML, Python, Data Viz |
| AWS Skill Builder | explore.skillbuilder.aws | AWS 公式トレーニング |
| GCP Training | cloud.google.com/training | GCP 公式トレーニング |
| TryHackMe | tryhackme.com | セキュリティ学習 |
| PortSwigger WSA | portswigger.net/web-security | Web セキュリティ |
| roadmap.sh | roadmap.sh | 開発者ロードマップ |
| javascript.info | javascript.info | モダン JS ガイド |
| learnprompting.org | learnprompting.org | プロンプトエンジニアリング |
