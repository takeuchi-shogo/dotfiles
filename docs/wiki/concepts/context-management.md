---
title: コンテキスト管理
topics: [memory]
sources: [2026-03-18-cursor-self-summarization-analysis.md, 2026-03-20-agent-engineering-practices-analysis.md, 2026-04-02-claude-code-memory-system-explained-analysis.md, 2026-04-17-claude-code-session-mgmt-analysis.md]
updated: 2026-04-17
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

## ソース

- [Cursor Self-Summarization](../../research/2026-03-18-cursor-self-summarization-analysis.md) — RLベースの自己要約で~1,000トークン要約が50%エラー削減を実証
- [Agent Engineering Practices](../../research/2026-03-20-agent-engineering-practices-analysis.md) — コンテキスト4層分離・3種圧縮戦略・記憶4分類の体系的整理
- [Claude Code Memory System Explained](../../research/2026-04-02-claude-code-memory-system-explained-analysis.md) — Claude Code内部の5層メモリアーキテクチャをソースマップ逆コンパイルから解析
- [Letta: Memory-as-Harness](../../research/2026-04-04-letta-memory-as-harness-analysis.md) — Context Constitution（7原則）・PreCompact flush・PostCompact verification・Proactive管理パターン
- [Claude Code: Session Management & 1M Context](../../research/2026-04-17-claude-code-session-mgmt-analysis.md) — Context Rot 300-400k threshold・Every Turn 5択ブランチポイント・Rewind workflow・Compact vs Clear 使い分け・Subagent Mental Test
