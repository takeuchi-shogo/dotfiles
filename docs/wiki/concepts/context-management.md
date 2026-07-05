---
title: コンテキスト管理
topics: [memory]
sources: [2026-03-18-cursor-self-summarization-analysis.md, 2026-03-20-agent-engineering-practices-analysis.md, 2026-04-02-claude-code-memory-system-explained-analysis.md, 2026-04-17-claude-code-session-mgmt-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 21
confidence: established
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
- **Coordinator Context Budget**: 並列サブエージェントの件数管理が Orchestrator パターン最大の失敗モード。5件で消費60-70%、15件で90%超に達する実測があり、件数上限とsummary層挿入の閾値が必要
- **Advisor-Executor パターン（中間相談プロトコル）**: 実行系モデルが常時上位モデルに相談するのではなく、困難を検知した時だけボトムアップで相談を発火させる設計。相談を疎にすることでコンテキスト消費とコストを抑えつつ性能を引き上げる
- **失敗学習ループの「記録しない基準」**: 記憶の価値は網羅的な記録量ではなく、実戦で複数回再発したものだけを昇格させる pruning 基準にある。「機能の存在」は「機能の有効性」を保証せず、認知負荷は機能の数ではなくエントリ数で増える
- **Prompt Cache の3層TTL**: subscriptionは1時間、API既定は5分、サブエージェント（Task tool）は常に5分とTTLが異なる。この違いを混同すると不要な中断を招き、モデル切替やCLAUDE.md編集のタイミングによってもキャッシュ破棄の挙動が変わる
- **Signal Density（選別原則）**: コンテキストの質を決めるのは情報量ではなく信号密度で、「短時間で再取得できる情報は保存しない」という判定がその実装になる。ただし pruning ロジックが「古い順」など機械的な基準に依存すると、実際のファイル構造（前半がコア知識、後半が肥大化した索引など）と前提がずれ、signalを消してnoiseを残す逆効果になりうる
- **File-based Memoryのスケーラビリティ限界**: ファイル数が1000未満ではfile-based memoryがレイテンシ・recall精度でVector DBより有利だが、1000を超えるとrecall精度が70%まで低下しVector DBが優位に転じる

## Context Constitution（原則体系）

Letta AI の "Memory-as-Harness" 研究では、コンテキスト管理の原則を **Context Constitution**（7原則）として明文化することを提唱している。単発のポリシーファイルに散逸させるのではなく、統合的な憲法として一箇所に集約することで、エージェントが自分の動作制約を明示的に参照できるようにする。

7原則の骨子:
1. **Cheapest Layer First** — 安い層（Working memory）が高価な層（Full Compaction）の発動を防ぐ
2. **Proactive > Reactive** — 消失を検知してから対処するのではなく、消失前に重要情報を退避する
3. **4分類保存先決定** — Working/Procedural/Episodic/Semantic の区分に従って保存先を決める
4. **PreCompact flush** — 圧縮前に key decisions をメモリにフラッシュする
5. **PostCompact verification** — 圧縮後に Plan re-grounding と状態検証を実施する
6. **Compaction survival priorities の明示** — どの情報が圧縮を生き残るべきかを事前定義する
7. **Memory gardening** — セッション中に定期的にメモリを整理してノイズを除去する

このリポジトリでは `.config/claude/references/context-constitution.md` として7原則を実装済み。

## Proactive vs Reactive コンテキスト管理

従来のReactive管理（コンテキスト超過→アラート→対処）に対し、Proactiveアプローチはコンテキストが逼迫する前に先手を打つ。具体的には:

- **PreCompact flush**: `pre-compact-save.js` がコンパクション前に key decisions をメモリへフラッシュ（圧縮2回目以降で発動するリマインダーを追加済み）
- **PostCompact verification**: `post-compact-verify.js` がコンパクション後に Plan re-grounding + memory gardening + session health チェックを実行
- **Background memory subagents**: セッション中にリアルタイムでメモリ管理を担う専用サブエージェントパターン（将来的な拡張候補）

## 実践的な適用

このリポジトリでは`pre-compact-save.js`がコンテキスト圧縮時の3段階ガイダンスと圧縮回数追跡を担い、Brevity Principleセクションで~1,000トークン目標を明示している。`output-offload.py`が大きな出力をファイルに退避してコンテキスト消費を抑制する。MEMORY.mdは現在157行で上限余裕があるが、description品質がSonnetフィルタの精度に直結するため全ファイルのdescription品質監査が重要。`context-compaction-policy.md`と`resource-bounds.md`に閾値とカウンター定数が定義されている。`context-constitution.md`に7原則をまとめた統合ドキュメントを整備し、ProactiveなPreCompact/PostCompactフックが稼働している。

## 関連概念

- [agent-memory](agent-memory.md) — エージェントのメモリシステムの設計と種別
- [context-engineering](context-engineering.md) — コンテキストを意図的に設計するアプローチ
- [long-running-agents](long-running-agents.md) — セッション跨ぎのコンテキスト継続戦略
- [parallel-agent-orchestration](parallel-agent-orchestration.md) — Narrow Context Principle（コンテキストが狭いほど品質が上がる）の実践とサブエージェントへの最小入力セット設計

## セッション管理・Context Rot

1Mトークンのコンテキストウィンドウは理論上の上限であり、実運用では **Context Rot**（コンテキスト汚染）が早期に発生する。Anthropicの実測では 300-400k トークン付近でマルチホップ推論の精度が劣化し始める（タスク依存）。

### 5択ブランチポイント（Every Turn）

各ターン開始時に5つの選択肢から行動を選ぶ:
1. **継続（Continue）** — そのまま次のステップへ
2. **コンパクション（/compact）** — コンテキストを圧縮しつつ続行。指示付きで要約方針を制御可能
3. **クリア（/clear）** — セッションをリセットし fresh start。簡潔なブリーフィングを自作する
4. **Rewind（/rewind）** — 誤った方向に進んだ際に分岐点まで戻る。エラー訂正より有効
5. **サブエージェント委譲** — タスクをサブエージェントに渡してコンテキストを切り離す

### Compact vs Clear の使い分け

| シナリオ | 推奨 |
|----------|------|
| 累積したノイズをリセットしたい | `/compact [steering指示]` |
| 完全に別タスクへ切り替える | `/clear` + brief作成 |
| 誤方向に進んでいることに気づいた | `/rewind` |
| コンテキストが巨大なサブタスクを実行 | サブエージェント委譲（Mental Test: 独立したタスクか？） |

### Subagent Mental Test

サブエージェント委譲の判断基準（Mental Test）: 「このタスクはコンテキスト全体なしで完了できるか？」 → Yes なら委譲してコンテキストを保護する。

### Task Boundary（グレーゾーン）

同一セッションを継続すべきか、新セッションに切り替えるべきかが曖昧なケース:
- 関連する後続タスク（例: テスト→デバッグ）は継続が有効な場合が多い
- コンテキストの 40% 以上が前タスクの残滓なら `/clear` + brief が優勢
- 判断コストが高い場合は `/compact` でひとまず圧縮し、その後の精度で判断する

## Context Design 5層モデル（i3design 記事由来）

久保星哉 (i3design) の「組織的なAI活用を阻む最大のハードルはコンテキストデザインだった」では、コンテキストを **5層のインフラスタック** として捉える視点を提示している。

| 層 | 名称 | 主な関心事 |
|----|------|------------|
| 1 | **Infrastructure** | MCP・コネクター・ツール接続の維持・Connector drift 対策 |
| 2 | **Creation** | コンテキスト生成品質（Telemetry 信号品質・tacit→rule トレース） |
| 3 | **Distribution** | コンテキストの配布・cwd-aware profile・動的ルーティング |
| 4 | **Governance** | 鮮度管理・Hook 陳腐化検知・予算管理・MCP 台帳 |
| 5 | **Execution** | エージェント実行時の信号品質・smoke-test・skill-local lock |

このモデルが示す核心的な洞察は「コンテキストを**単なる設定**ではなく**インフラ**として管理する」ことであり、特に Governance 層の Hook 陳腐化リスク（条件付き実行の欠如）と Infrastructure 層の Connector drift（接続の静かな劣化）が実運用上の主な障害になりやすい。

このリポジトリでは `references/context-constitution.md`（Governance）・`scripts/policy/`（Infrastructure）・cwd-aware profile 設計（Distribution）が各層に対応している。詳細は [分析レポート](../../research/2026-04-17-context-design-absorb-analysis.md) と [実装プラン](../../plans/2026-04-17-context-design-absorb-plan.md) を参照。

## ソース

- [Cursor Self-Summarization](../../research/2026-03-18-cursor-self-summarization-analysis.md) — RLベースの自己要約で~1,000トークン要約が50%エラー削減を実証
- [Agent Engineering Practices](../../research/2026-03-20-agent-engineering-practices-analysis.md) — コンテキスト4層分離・3種圧縮戦略・記憶4分類の体系的整理
- [Claude Code Memory System Explained](../../research/2026-04-02-claude-code-memory-system-explained-analysis.md) — Claude Code内部の5層メモリアーキテクチャをソースマップ逆コンパイルから解析
- [Letta: Memory-as-Harness](../../research/2026-04-04-letta-memory-as-harness-analysis.md) — Context Constitution（7原則）・PreCompact flush・PostCompact verification・Proactive管理パターン
- [Claude Code: Session Management & 1M Context](../../research/2026-04-17-claude-code-session-mgmt-analysis.md) — Context Rot 300-400k threshold・Every Turn 5択ブランチポイント・Rewind workflow・Compact vs Clear 使い分け・Subagent Mental Test
- [Context Design 5層モデル（久保星哉/i3design）](../../research/2026-04-17-context-design-absorb-analysis.md) — コンテキストを5層インフラスタックとして管理する視点。Connector drift・Hook 陳腐化・Telemetry 品質・cwd-aware profile の統合設計
- [The Advisor Strategy (Claude Blog)](../../research/2026-04-10-advisor-strategy-analysis.md) — Advisor戦略記事を分析、中間相談プロトコルなど3件採用
- [Claude Code from Source 設計原則 周辺知見補完 (Gemini調査)](../../research/2026-04-10-claude-code-design-principles-analysis.md) — CC設計原則の業界動向・脆弱性をGemini調査で補完
- [Claude Code from Source 全18章リバースエンジニアリング分析](../../research/2026-04-10-claude-code-from-source-analysis.md) — CC全18章を分析、Tier1/2統合しTier3は記録のみ
- [Multi-Agent Coordination Patterns: Five Approaches (Anthropic Blog)](../../research/2026-04-11-multi-agent-coordination-patterns-analysis.md) — 5協調パターンを分析、Context Budgetなど6タスク採用
- [pepabo「Claude Code 失敗学習ループ」吸収分析（あたに, GMOペパボ）](../../research/2026-04-11-pepabo-failure-learning-loop-analysis.md) — pepabo記事、3層メモリの認知負荷是正とpruning優先方針を部分採用
- [A good AGENTS.md is a model upgrade (Slava Zhenylenko, Augment)](../../research/2026-04-23-agents-md-patterns-absorb-analysis.md) — AGENTS.md記事分析、sprawl監査等7タスク採用(module化棄却)
- [How to build a Deep Researcher (Akshay Pachaar)](../../research/2026-04-24-deep-researcher-absorb-analysis.md) — Deep Researcher記事分析、query3軸・LLM選別等をresearch skillに統合
- [Subagent Context Fork absorb分析 (aitmpl系記事)](../../research/2026-04-27-subagent-context-fork-absorb-analysis.md) — Subagent context fork記事を分析、fork機能非採用・観測3件採用
- [Claude Code Overhead 9 Patterns absorb分析](../../research/2026-05-04-claude-code-overhead-9patterns-absorb-analysis.md) — Claude Codeオーバーヘッド9パターンを分析、skill tax削減等5件採用
- [I Tried 100+ Claude Code Skills, These 6 Are Best absorb分析](../../research/2026-05-06-100-skills-best6-absorb-analysis.md) — 厳選skill 6選記事を分析、Review独立再現フェーズ等5件採用
- [How Anthropic Engineers Actually Save Tokens](../../research/2026-05-22-anthropic-engineers-token-savings-absorb-analysis.md) — プロンプトキャッシュ戦略を検証しTTL三層表を追加
- [7-agent Software Factory (Sai Rahul)](../../research/2026-05-27-sairahul-7agent-software-factory-absorb-analysis.md) — 7エージェント分業記事、新規手法2件も前提不一致で不採用
- [@damidefi Delete 90% of Your Obsidian Notes](../../research/2026-05-31-damidefi-delete-90-vault-absorb-analysis.md) — Vault削除記事のsignal density原則を分析、MEMORY.mdを223→154行に圧縮
- [Zero Trust for AI Agents (Anthropic eBook, 2026-05-18)](../../research/2026-05-31-zero-trust-ai-agents-absorb-analysis.md) — Zero Trust eBookを分析、暗号ID等はN/A、Agent-BOM-lite等3件をL規模で全採用
- [私の最強のMac開発環境2026 (tyPhoon, Nix+mise)](../../research/2026-06-02-typhoon-nix-mise-absorb-analysis.md) — Nix+mise記事を検証、mise未活用のランタイム二重管理事故を発見し統合
