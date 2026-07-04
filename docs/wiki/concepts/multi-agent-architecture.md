---
title: マルチエージェントアーキテクチャ
topics: [agent]
sources: [2026-03-12-subagent-patterns-analysis.md, 2026-03-23-multi-agent-scaling-analysis.md, 2026-03-26-hierarchical-mas-theory-analysis.md, 2026-04-02-self-organizing-llm-agents-analysis.md, 2026-04-04-12-claude-features-top-operators-analysis.md, 2026-04-05-parallel-agent-worktrees-orchestration-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 33
confidence: established
---

# マルチエージェントアーキテクチャ

## 概要

マルチエージェントシステムの設計は「増やせば賢くなる」という単純な話ではなく、タスクの特性（並列可能か逐次推論か）によって効果が大きく異なる。階層化された構造では制御スパンを O(log W) に圧縮することでエラーの連鎖増幅を抑制でき、フラットな線形チェーンが引き起こす指数的失敗拡大を回避できる。また大規模実験（25,000+ タスク）では、プロトコル選択が品質差異の 44% を説明し、モデル選択は約 14% にとどまることが示されており、協調設計こそが最重要変数である。

## 主要な知見

- **Sync / Async / Scheduled の3パターン**: サブエージェント委譲はブロッキング（結果待ち）、ファイア＆フォーゲット（長時間非同期）、定期スケジュールの3形式に分類できる
- **並列化の両刃**: 独立並列構成ではエラーが 17.2 倍に増幅するが、中央集権型では 4.4 倍に抑制される。並列化は慎重なトポロジ設計が前提
- **Depth-1 原則**: サブエージェントはサブエージェントを生まない（深さ 1 制限）。再帰的委譲は制御とデバッグを困難にする
- **Sequential プロトコルが最優秀**: 4〜256 エージェントへのスケーリングで品質低下なし（p=0.61）。Shared メモリ方式との差は +44%（Cohen's d=1.86）
- **能力閾値が分岐点**: 強力なモデルでは自律性で +3.5% 改善、弱いモデルでは自律性が -9.6% の悪化を招く
- **3層構造分離（HMASTheory）**: トポロジ圧縮・スコープ分離・検証ゲートの3メカニズムを組み合わせると失敗指数が Θ(W) から O(log W) に低減する
- **異種レビューアーの優位性**: 均質な8エージェントより異種2エージェントの方が AUROC が高い（84.2 vs 81.4）。エラーモードの直交性が重要
- **コンテキスト圧縮が本質的 ROI**: 並列性よりも、サブエージェントへの委譲によるコンテキスト分割・圧縮が実際の価値源泉
- **Generic > Specialized**: 特化エージェントを増やすより、汎用エージェントにチェックリストを注入する段階的特化の方がルーティング複雑度を抑えられる
- **Awareness Summary**: 並列実行する Subagent 間で「他のエージェントが何をしているか」を 1-2 行で共有する相互認識プロトコル。衝突回避のための最小限の情報共有であり、過剰な情報共有ではない
- **Pre-Merge Conflict Detection**: 並列 worktree の全作業完了後、マージ前に複数エージェントが同一ファイルを変更した箇所を事前検出・警告するパターン。発生後の解決より発生前の検出が安全
- **Worktree = ランタイム環境全体の隔離**: worktree はファイルシステムだけでなく、サーバー・プロセス・ドメインを含むランタイム環境全体を隔離する。Docker Compose のサービス並列化と同じ発想でブランチを並列化できる
- **Managed Agents の Brain/Hands/Session 分離**: ハーネス（脳）・ツール実行サンドボックス（手）・セッションログ（状態）を独立インタフェースに分ける設計。Managed Agents を計画・推論層、Custom Harness を実行・検証層として併用する Hybrid Architecture が最もインパクトが大きい統合パターンとして評価された
- **Advisor-Executor パターン**: 大規模モデル（Opus）を小規模実行部（Sonnet/Haiku）のアドバイザーとして組み合わせ、Executor が判断困難を検知したときだけ相談する。ベンチマークでは Haiku+Opus Advisor が単独 Sonnet より 85% 低コストで性能は上回る。Advisor の応答型（plan/correction/stop）を持たせることで、相談結果を構造化して返せる
- **MoE の類推適用と粒度の罠**: LLM 内部の Router+Expert 構造はマルチエージェント設計の棚卸しに使えるが、MoE はトークン単位（ミリ秒）、ハーネスはタスク単位（秒〜分）で 6 桁以上粒度が異なる。無視すると Contextual Fragmentation（論理一貫性の崩壊）・Gradient Blackout（Top-k から漏れたエージェントに学習信号が届かない）・Latency Cascade の 3 失敗モードを招く
- **5 パターン協調フレームワーク**: Generator-Verifier / Orchestrator-Subagent / Agent Teams / Message Bus / Shared State の 5 パターンは協調問題の種類ごとに異なるトレードオフを持つ。原則は最もシンプルな Orchestrator-Subagent から始め、観測された限界（Context Budget 超過など）に応じて他パターンへ進化させる。5 subagent で Context 60-70%、15 subagent で 90% 超という具体的な閾値が Orchestrator の失敗モードの筆頭に挙がる
- **Skill Graphs の Reliability Ceiling**: skill を atoms（単一目的プリミティブ）/ molecules（explicit chaining）/ compounds（人間が driver する playbook）の 3 層に分け、composition を runtime 判断でなく skill 側に明示的に埋め込む。compound が 8-10 molecules を超えると信頼性が $0.9^n$ で指数減衰する
- **Self-Rejection Rule と Subagent Count Ceiling**: 新しい subagent を追加する前に「既存 agent/skill の責務拡張で吸収できないか」を必ず確認する self-rejection ルールと、40-50 個を超えると router 精度が崩壊するという個数の警戒ラインは、個別 agent のコピーよりメタ原則として文書化する方が投資対効果が高い
- **Distribution vs Escalation**: Subagent（分散・context 隔離）と Advisor（エスカレーション・実行阻害の解消）は異なる問題を解く直交した設計軸である。タスクを専門サブタスクに分割できるか／Executor が行き詰まっているか／context 汚染を避ける必要があるか、の 3 質問で使い分ける

## 実践的な適用

dotfiles リポジトリでは3種のサブエージェントパターンが実装済みである。Sync は `/review` での 2〜4 エージェント並列起動・結果統合、Async は `claude -p` 子プロセス（`/research`, `/autonomous`）、Scheduled は `autoevolve-runner.sh` cron ジョブ（毎日 3:00）が対応する。Depth-1 原則はエージェント設計で厳守しており、サブエージェントは Agent ツールを持たない。マルチモデル統合（Claude + Codex + Gemini）は能力特性に基づくルーティング（`claude-hooks` Rust `user-prompt`）で実現されており、Codex はレビュー・設計相談、Gemini は 1M コンテキスト分析に役割分担している。Sequential プロトコルへの移行は現在 Gap として認識されており、Implicit Coordinator パターンからの昇格が課題である。Advisor Consultation（中間相談プロトコル）は `<agent_delegation>` のトップダウン委譲を補う形で採用済みであり、Managed Agents 相当の Hybrid Architecture（計画/推論層と実行/検証層の分離）は将来の参照設計として文書化されている。

## 関連概念

- [harness-engineering](harness-engineering.md) — ハーネス設計とエージェント協調のインフラ基盤
- [context-management](context-management.md) — エージェント間コンテキスト分離と圧縮
- [long-running-agents](long-running-agents.md) — 長時間自律タスクの管理と安全機構
- [parallel-agent-orchestration](parallel-agent-orchestration.md) — worktree を使った並列実行・Awareness Summary・Pre-Merge Conflict Detection の実践パターン

## ソース

- [Three Sub-Agent Patterns Analysis](../../research/2026-03-12-subagent-patterns-analysis.md) — Sync/Async/Scheduled の3パターン分類とコンテキスト圧縮が真のROI
- [Multi-Agent Scaling Analysis](../../research/2026-03-23-multi-agent-scaling-analysis.md) — Google/Anthropic/Cognition の3視点からスケーリング特性を検証。エラー増幅率の定量データあり
- [Hierarchical MAS Theory Analysis](../../research/2026-03-26-hierarchical-mas-theory-analysis.md) — トポロジ圧縮・スコープ分離・検証ゲートによる失敗指数削減の数理理論
- [Self-Organizing LLM Agents Analysis](../../research/2026-04-02-self-organizing-llm-agents-analysis.md) — 25,000+ タスクの大規模実験。Sequential プロトコルの優位性と能力閾値効果
- [Single-Agent vs Multi-Agent Thinking Budget (Stanford, arXiv:2604.02460)](../../research/2026-04-08-sas-vs-mas-thinking-budget-analysis.md) — SAS対MAS論文を分析、委譲判断基準にDPI根拠明文化を提案
- [Subagents in Claude Code (Anthropic公式ブログ)](../../research/2026-04-08-subagents-claude-code-analysis.md) — 公式サブエージェント指南を分析、レビュー強制と可観測性を追加
- [Launching Claude Managed Agents (Anthropic Blog)](../../research/2026-04-09-claude-managed-agents-analysis.md) — Managed Agentsを分析、Hybrid構成など5タスク採用
- [The Advisor Strategy (Claude Blog)](../../research/2026-04-10-advisor-strategy-analysis.md) — Advisor戦略記事を分析、中間相談プロトコルなど3件採用
- [Mixture of Experts Explained (Amit Shekhar)](../../research/2026-04-11-moe-article-analysis.md) — MoEをハーネスに類推、粒度崩壊ガードレール等3件実装
- [Multi-Agent Coordination Patterns: Five Approaches (Anthropic Blog)](../../research/2026-04-11-multi-agent-coordination-patterns-analysis.md) — 5協調パターンを分析、Context Budgetなど6タスク採用
- [Hermesパーソナルアナリスト活用体験記 分析](../../research/2026-04-14-hermes-personal-analyst-analysis.md) — Hermesアナリスト記事分析、大半既存資産で充足、情報源拡張のみ追加
- [Hermes Fleet共有メモリ構築記事 分析](../../research/2026-04-17-hermes-fleet-shared-memory-analysis.md) — Hermes Fleet記事分析、Qdrant/mem0導入見送り、secret監査等4件採用
- [Skill Graphs 2.0 — atoms/molecules/compounds 3層合成モデル](../../research/2026-04-23-skill-graphs-2.0-absorb-analysis.md) — Skill Graphs記事を分析、composition depth計測とADR追加を採用
- [How to build a Deep Researcher (Akshay Pachaar)](../../research/2026-04-24-deep-researcher-absorb-analysis.md) — Deep Researcher記事分析、query3軸・LLM選別等をresearch skillに統合
- [google/skills + ADK 2.0 Multi-Agent Orchestration Patterns](../../research/2026-04-24-google-skills-adk2-absorb-analysis.md) — google/skills 13個全採択、ADK 2.0パターンは強化不要と判定
- [Codex CLI を Claude Code 並みに最適化 absorb分析](../../research/2026-04-27-codex-claude-parity-absorb-analysis.md) — Codex最適化4項目を分析、agents/MCP同期等6件採用
- [Codex vs Claude Code 役割分担 absorb分析 (Codex Studio)](../../research/2026-04-29-codex-vs-claudecode-role-split-absorb-analysis.md) — Codex/Claude Code役割分担記事を分析、注記1件のみ採用
- [OpenAI Symphony/ClawSweeper orchestration absorb分析](../../research/2026-04-29-symphony-clawsweeper-absorb-analysis.md) — OpenAI orchestration OSSを分析、Janitor既存TODO消化等3件採用
- [Continually Improving Cursor's Agent Harness absorb分析](../../research/2026-04-30-cursor-harness-absorb-analysis.md) — Cursorハーネス改善記事を分析、11手法全て既存カバーで採用0件
- [Kimi K2.6+Opus 4.7+GPT-5.5 3モデルスタック absorb分析](../../research/2026-04-30-three-model-stack-absorb-analysis.md) — 3モデルコスト削減記事を分析、model debt watch行1件のみ採用
- [30 Claude Code Sub-Agents I Actually Use in 2026 absorb分析](../../research/2026-05-02-30-subagents-2026-absorb-analysis.md) — 30サブエージェント記事を分析、メタ原則2件+強化2件採用
- [Distribution vs Escalation: Subagents or Advisors absorb分析](../../research/2026-05-04-distribution-vs-escalation-absorb-analysis.md) — Subagent/Advisor使い分け記事を分析、決定表等5件統合
- [The 9 Claude Agents That Work While You Sleep (Nav Toor/ECC)](../../research/2026-05-13-9-overnight-agents-absorb-analysis.md) — 9件のovernight agent提案をrole mismatchで全棄却、ECCのみ記録
- [How to Build a Claude Agent Team in 7 Steps (Twitter)](../../research/2026-05-25-claude-agent-teams-7steps-absorb-analysis.md) — Agent Team記事はほぼAlready、cmuxとの境界注記のみ採用
- [7-agent Software Factory (Sai Rahul)](../../research/2026-05-27-sairahul-7agent-software-factory-absorb-analysis.md) — 7エージェント分業記事、新規手法2件も前提不一致で不採用
- [14 Claude Code sub-agents, 4 survived (60日実験記録)](../../research/2026-05-30-14-subagents-4-survived-absorb-analysis.md) — 60日14サブエージェント実験記事、アンチパターン等軽微採用
- [You're Not Slow. You're Single-Threaded: 300 Agents (Kimi)](../../research/2026-05-30-single-threaded-300-agents-absorb-analysis.md) — Kimi300エージェント群記事、並列主張は全て既存確認済
- [4-Agent Pipeline (Planner→Coder→Tester→Reviewer) (zodchixquant)](../../research/2026-05-31-4-agent-pipeline-absorb-analysis.md) — 4エージェント固定パイプラインを分析、Tester境界1件のみ採用しほぼ不採用
- [A harness for every task: dynamic workflows in Claude Code](../../research/2026-06-03-dynamic-workflows-absorb-analysis.md) — Workflow tool記事分析、意図的不採用維持・リンク切れ2件修正
- [The Self-Improving Loop: 300-agent swarm on Kimi K2.6](../../research/2026-06-18-kimi-k26-self-improving-swarm-loop-absorb-analysis.md) — Kimi swarm記事はほぼrehash、Cost-Arbitrageのみbest-of-nガイドに採用
- [How to Build Your First Team of AI Agents Using Claude (Khairallah)](../../research/2026-06-20-khairallah-agent-team-intro-absorb-analysis.md) — エージェントチーム入門記事は既存30+件と完全rehash、採用0
- [The Self-Verifying Loop: 300 agents, 4,000 steps (Kimi K2.6)](../../research/2026-06-20-kimi-k26-self-verifying-loop-absorb-analysis.md) — Kimiベンダー第2弾記事も全rehash、採用0確定
- [Model Council: How to get Fable-level intelligence back (weeklyaiops)](../../research/2026-06-20-weeklyaiops-model-council-absorb-analysis.md) — モデル評議会マーケ記事は全11手法rehash、採用0
