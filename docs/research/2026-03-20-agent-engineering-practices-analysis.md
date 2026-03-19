---
source: "你不知道的 Agent：原理、架构与工程实践" (Agent Engineering Practices - Chinese article)
date: 2026-03-20
status: integrated
---

## Source Summary

**主張**: Agent の安定性はモデル性能よりも Harness（テスト・検証・制約インフラ）で決まる。コンテキスト工学・ツール設計・記憶統合・評測の基礎工学を固めることが最優先。

**手法**:
- Harness 優先（自動検証＋明確目標）
- コンテキスト4層分離（常駐/オンデマンド/ランタイム注入/記憶）
- 3種圧縮戦略（スライディングウィンドウ/LLM要約/ツール結果置換）
- ACI ツール設計（パラメータ層防錯、返回フォーマットパラメータ化）
- Tool Search（動的ツール発見）
- Programmatic Tool Calling（中間結果をコード内で流転）
- Tool Use Examples（各ツールに1-5個の実例）
- 記憶4分類（作業記憶/手続き/エピソード/意味記憶）
- 50%閾値自動統合 + 失敗時アーカイブフォールバック
- Initializer + Coding Agent パターン（跨セッション長期タスク）
- タスク状態の外部化（JSON進捗管理、単一 in_progress 制約）
- マルチAgent JSONL inbox プロトコル
- 子Agent 深度制限 + 最小システムプロンプト
- 評測: コード評分器 > モデル評分器、transcript + outcome 両面評価
- 「eval を先に直す」原則
- イベントストリーム基盤の可観測性

**根拠**: OpenAI Codex（100万行/5ヶ月）、Anthropic C コンパイラ実験（$20K/2週間）、Karpathy Autoresearcher

**前提条件**: 高検証可能タスク（コード生成・編集）で最も有効。弱検証タスクではモデル上限が重要。

## Gap Analysis

| # | 手法 | 判定 | 説明 |
|---|------|------|------|
| 1 | Harness 優先 | Already | completion-gate.py, verification-before-completion |
| 2 | コンテキスト4層分離 | Partial | 3層実装済み。オンデマンド層の体系化不足 |
| 3 | 3種圧縮戦略 | Partial | output-offload.py のみ。LLM要約なし |
| 4 | ACI ツール設計 | Partial | パラメータガードあり。原則未明文化 |
| 5 | Tool Search | N/A | Claude Code プラットフォームの ToolSearch で対応済み |
| 6 | Programmatic Tool Calling | Partial | hooks でのプログラム的処理あり |
| 7 | Tool Use Examples | Partial | 一部エージェントにドキュメント的な例あり |
| 8 | 記憶4分類 | Gap | retention ベースの分類のみ |
| 9 | 50%閾値自動統合 | Partial | 500行閾値でアーカイブ |
| 10 | Initializer + Coding Agent | Already | checkpoint_recover.py |
| 11 | タスク状態外部化 | Partial | task_registry.py あり。単一 in_progress 制約なし |
| 12 | JSONL inbox プロトコル | Gap | マルチAgent間の構造化通信なし |
| 13 | 子Agent 深度制限 | Partial | maxTurns のみ |
| 14 | 評測: code grader > model | Partial | FM検出あり。原則未明文化 |
| 15 | eval を先に直す | Partial | 方法論あり。プロセス未定着 |
| 16 | イベントストリーム可観測性 | Already | session_events.py |
| 17 | Prompt Caching | N/A | プラットフォーム側機能 |

## Integration Decisions

全 Gap/Partial 項目を取り込み。以下8タスクを実行:

1. [Gap→Integrated] 記憶4分類マッピング → memory-safety-policy.md に対照表追加
2. [Gap→Integrated] JSONL inbox プロトコル → subagent-framing.md にプロトコル仕様追加
3. [Partial→Integrated] 圧縮戦略 → compact-instructions.md 新規作成
4. [Partial→Integrated] ACI ツール設計原則 → references/aci-tool-design.md 新規作成
5. [Partial→Integrated] eval 優先原則 → workflow-guide.md にセクション追加
6. [Partial→Integrated] タスク単一 in_progress 制約 → task_registry.py に制約追加
7. [Partial→Integrated] 子Agent 最小プロンプト原則 → subagent-framing.md に追加
8. [Partial→Integrated] Tool Use Examples 原則 → aci-tool-design.md に含める
