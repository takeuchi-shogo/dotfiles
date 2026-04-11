---
source: "https://claude.com/blog/multi-agent-coordination-patterns"
date: 2026-04-10
status: integrated
---

# Multi-agent coordination patterns: Five approaches and when to use them

**著者**: Cara Phillips (with Eugene Yang, Jiri De Jonghe, Samuel Weller, Erik Schluntz)
**出典**: Anthropic Blog
**公開日**: 2026-04-10

## Source Summary

**主張**: 最もシンプルなマルチエージェントパターン（Orchestrator-Subagent）から始めて、観測された限界に応じて進化させる。5 パターン — Generator-Verifier, Orchestrator-Subagent, Agent Teams, Message Bus, Shared State — それぞれが異なる協調問題を解き、複雑性・オーバーヘッド・失敗モードのトレードオフが異なる。

**手法**:
- **Generator-Verifier**: 明示的な評価基準に基づくフィードバックループ。品質クリティカルな出力向き。曖昧な品質基準と無限ループのリスク
- **Orchestrator-Subagent**: リードエージェントが計画・委譲・統合。最もシンプルで広範。情報ボトルネックと逐次実行が限界
- **Agent Teams**: コーディネーターが永続ワーカーを spawn、ワーカーが共有キューからタスクを claim して文脈を蓄積。並列・独立・長時間タスク向き。タスク独立性が厳格に要求される
- **Message Bus**: イベント駆動アーキテクチャ。複数ソースからのアラート → トリアージエージェントが重要度分類する例。router 精度がクリティカル、silent failure のデバッグ困難
- **Shared State**: 永続ストアを介して複数エージェントが協調（中央コーディネーターなし）。協調的リサーチ向き。重複作業・予測不能な結果・reactive loop のリスク
- **Pattern Selection Framework**: 問題特性 → パターンのマッピング。**原則: Orchestrator-Subagent から始めろ**
- **Feedback Loop Management**: termination condition が必須
- **Context Accumulation**: Agent Teams は assignment を跨いで文脈を蓄積
- **Information Bottleneck Mitigation**: Message Bus / Shared State で中央化を回避
- **Task Independence Requirement**: Agent Teams で厳守

**根拠**: Claude Code の background search における Orchestrator-Subagent、コードレビューシステム、コードベース移行の Agent Teams、セキュリティ運用の Message Bus 等の実例。定量指標の提示はなし。

**前提条件**: 明示的な評価基準（Generator-Verifier）、明確なタスク分解境界（Orchestrator-Subagent）、厳格なタスク独立性（Agent Teams）、イベントソース安定性と router 精度（Message Bus）、termination と reactive loop 管理（Shared State）。

## Gap Analysis (Pass 1 + 2 + Phase 2.5 補正後確定版)

| # | 手法 | 判定 | 関連ファイル | 詳細 |
|---|------|------|-------------|------|
| 1 | Generator-Verifier | Partial | `.config/claude/references/review-loop-patterns.md`, `scripts/policy/completion-gate.py`, `references/review-consensus-policy.md` | ralph-loop + completion-gate (MAX_RETRIES=2, ralph-loop max-iterations=100) + PASS/NEEDS_FIX/BLOCK 明示基準で実装済み。Generator/Verifier の明示的役割分離は未実装 |
| 2 | Orchestrator-Subagent | Already → **強化可能** | `.config/claude/CLAUDE.md (<agent_delegation>)`, `references/subagent-delegation-guide.md`, `references/agent-orchestration-map.md` | Opus=判断、Sonnet/Haiku/Codex/Gemini/Managed Agents 委譲。triage-router + agent-router.py。"Never delegate understanding" 教義文書化済み。**Coordinator Context Budget（件数上限・summary 層挿入）の明示なし — Gemini 指摘による強化候補** |
| 3 | Agent Teams（永続キュー） | Partial (weak) | `references/cmux-ecosystem.md`, `references/subagent-delegation-guide.md`, `references/task-registry-schema.md` | cmux-team 4層（Master→Manager pull→Conductor→Agent）と SendMessage ピア通信設計あり。**Codex の所見: task-registry.jsonl はスキーマだけ実在し、実ランタイムファイル未発見 → 「永続キュー実装済み」とは言えない** |
| 4 | Message Bus | Partial（前提ズレ注記） | `.config/claude/settings.json (hooks)`, `scripts/runtime/session_observer_router.py`, `scripts/policy/agent-router.py` | PreToolUse/PostToolUse/UserPromptSubmit/Stop/SubagentStop による多段 event-driven 代替あり。ただし **hooks は Claude Code プロセス内の fan-out であり、複数エージェント間の非同期 pub/sub ではない**（前提ズレ） |
| 5 | Shared State | Partial | `references/cc-7-layer-memory-model.md (Layer 7)`, `scripts/runtime/sync-memory-to-vault.sh`, `references/task-registry-schema.md` | agent-memory/ + Obsidian Vault 同期 + task-registry.jsonl で非同期・単方向の共有知識ストアあり。**リアルタイム多エージェント同時読み書き・CRDT による collision 解決は未実装（Gemini 指摘）** |
| 6 | Pattern Selection Framework | Already → **強化可能** | `references/subagent-delegation-guide.md`, `references/agent-orchestration-map.md`, `references/workflow-guide.md` | Sync/Async/Scheduled 判断 + サブエージェント vs Agent Teams 適性 + Plasticity Spectrum で意思決定マトリクス文書化済み。**5-pattern 統合ビュー（記事の中核フレーム）がない — 分散した情報を統合する価値あり** |
| 7 | Feedback Loop Management | Already → **強化可能** | `scripts/policy/completion-gate.py`, `references/review-loop-patterns.md`, `references/workflow-guide.md` | MAX_RETRIES=2 + ralph-loop 100 + Self-Evolution Cap=3 で termination 条件あり。**Reward Hacking（Verifier パス狙いの偽出力）検知ルール + 定期的人間監査が未定義 — Gemini 指摘** |
| 8 | Context Accumulation | Partial | `references/subagent-delegation-guide.md (fork_context policy)`, `references/cc-7-layer-memory-model.md`, `references/subagent-vs-cmux-worker.md` | fork_context=true/false 制御 + cmux Worker セッション内保持 + feature-tracker learning。**セッションを跨いだ同一 Worker 継続は未実装（Agent Teams は /resume 不可と明記）** |
| 9 | Information Bottleneck Mitigation | Partial | `references/subagent-delegation-guide.md`, `references/agent-orchestration-map.md (Sequential Protocol)`, `references/subagent-vs-cmux-worker.md` | SendMessage ピア通信 + Awareness Summary あり。**Awareness Summary 生成が Orchestrator 独占で、直接エージェント間通信に完全置換できていない。Dochkina 2026 の Sequential Protocol（Orchestrator を 14% 上回る）は移行候補として文書化のみ** |
| 10 | Task Independence Requirement | Already（強化不要） | `.claude/skills/autonomous/SKILL.md`, `references/subagent-delegation-guide.md`, `references/session-pool-guide.md` | git worktree 3層隔離（ファイル・環境変数・プロセス）+ run.lock + コンフリクト検出で完全 |
| 11 | Sequential Protocol 移行判断基準 | Gap | `references/agent-orchestration-map.md (Sequential Protocol 検討)` | Dochkina 2026 で 14% 向上実測あり、現状「検討中」と記述のみで具体的な移行シグナル・判断基準が未定義（Gemini 指摘） |

## Phase 2.5 Refinement Log (Codex + Gemini 並列批評)

### Codex（partial result — プロセス途中で停止）
- **task-registry.jsonl 実ランタイム未発見**: スキーマ（`references/task-registry-schema.md`）は存在するが、実ファイル書き込みが見つからず → Agent Teams 判定を `Partial → Partial (weak)` に格下げ

### Gemini（Google Search grounding + 周辺知識）

1. **Orchestrator context overflow**: 5 sub → 60-70%, 15 sub → 90%+ → #2 を `Already → 強化可能` に格上げ
2. **Generator-Verifier の Reward Hacking**: Verifier パス狙いの偽出力、人間監査の必要性 → #7 を `Already → 強化可能` に格上げ
3. **Sequential Protocol（Dochkina 2026）**: Orchestrator を 14% 上回る。役割自動選択。新規 Gap #11 として追加
4. **Message Bus 前提ズレ**: hooks fan-out ≠ multi-agent pub/sub → #4 に注記追加
5. **Shared State の CRDT 必要性**: concurrent write collision リスク、LangGraph state graph が近い → #5 に注記追加
6. **Time-Reversibility 欠落**: 記事には言及なし、LangGraph Checkpointing 参考。現状困っていないため見送り

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1 | Generator-Verifier 役割分離 | スキップ | 現状の ralph-loop で機能十分、複雑性見合わず |
| 3 | Agent Teams 永続キュー実ランタイム化 | **採用（中優先）** | 設計のみで実装空白は実用リスク、最小 Manager pull 実装で解消 |
| 4 | Message Bus 実装 | スキップ | 当セットアップで具体的必要性なし、前提ズレ注記のみ |
| 5 | Shared State 制約の明示 | **採用（中優先）** | agent-memory 同時書き込みの race condition リスクを文書化 |
| 8 | Context Accumulation | スキップ | Agent Teams 実装と連動、単独取り込み不可 |
| 9 | Information Bottleneck | スキップ | #2 強化でカバー |
| 11 | Sequential Protocol 移行判断基準 | **採用（高優先）** | Dochkina 2026 の 14% 実測に対し判断基準が空白 |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 2 | Coordinator Context Budget 明記 | **採用（高優先）** | Context overflow は Orchestrator-Subagent の最大の失敗モード、閾値定義は高 ROI |
| 6 | 5-Pattern 統合ビュー新設 | **採用（高優先）** | 記事の中核フレームで分散情報を統合、ナビゲーション改善 |
| 7 | Reward Hacking 検知ルール | **採用（中優先）** | ralph-loop の信頼性を底上げする予防策 |
| 10 | Task Independence | 強化不要 | 現状で記事要件を完全充足 |

## Plan

### Wave 1: 高優先（Top 3）

#### Task 1: 5-Pattern 統合ビュー新設
- **Files**: `.config/claude/references/multi-agent-coordination-patterns.md` (NEW)
- **Changes**: 記事の 5 パターンを起点に、各パターンの定義・失敗モード・当セットアップでの対応アセット（ファイルパスリンク）をマトリクス化
- **Size**: S

#### Task 2: Coordinator Context Budget 明記
- **Files**: `.config/claude/references/subagent-delegation-guide.md`
- **Changes**: "Coordinator Context Budget" セクションを追加。並列サブエージェント件数目安（5 で警戒、15 で summary 層強制）、Context 消費率モニタリングのガイドライン
- **Size**: S

#### Task 3: Sequential Protocol 移行判断基準
- **Files**: `.config/claude/references/subagent-delegation-guide.md`, `.config/claude/references/agent-orchestration-map.md`
- **Changes**: 「Orchestrator-Subagent → Sequential Protocol 切替シグナル」セクション追加。観測シグナル（context overflow、coordinator bottleneck、情報損失）と Dochkina 2026 の前提（役割固定度、タスク種別）を明記
- **Size**: M

### Wave 2: 中優先

#### Task 4: Reward Hacking 検知ルール
- **Files**: `.config/claude/references/review-consensus-policy.md`
- **Changes**: "Reward Hacking Mitigation" セクション追加。Verifier 基準の periodic update + 人間監査タイミング（N サイクル毎）を定義
- **Size**: S

#### Task 5: Agent Teams 実ランタイム化（最小）
- **Files**: `.config/claude/scripts/runtime/task-registry-writer.py` (NEW), settings.json hooks 追加
- **Changes**: task-registry.jsonl の実ランタイム書き込みを有効化。Async/Scheduled サブエージェントの invocation を記録
- **Size**: M
- **依存**: Task 1（パターン統合ビューに反映）

#### Task 6: Shared State 制約の明示
- **Files**: `.config/claude/references/cc-7-layer-memory-model.md`
- **Changes**: Layer 7 に "Concurrent Write Constraints" を追記。agent-memory 同時書き込みの race condition リスク、CRDT 採用検討のメモ（現状未実装の明記）
- **Size**: S

### タスク依存関係

```
Task 1 (5-Pattern View) ──┬── Task 2 (Context Budget)     → 独立
                          ├── Task 3 (Sequential Protocol) → 独立
                          ├── Task 4 (Reward Hacking)      → 独立
                          ├── Task 5 (Agent Teams Runtime) → Task 1 完了後にリンク更新
                          └── Task 6 (Shared State)        → 独立
```

### 規模推定

- **Wave 1**: S + S + M = S〜M 規模（3 ファイル）
- **Wave 2**: S + M + S = M 規模（3 ファイル + hooks 1 エントリ）
- **合計**: L 規模（6 ファイル超、hook 追加、新規スクリプト）

## Handoff

- プランは `docs/plans/2026-04-11-multi-agent-coordination-patterns-integration.md` に保存される
- Wave 1 は同一セッション実行可能、Wave 2 は新セッションで `/rpi` 推奨
- Codex Spec/Plan Gate 対象（M 規模以上）

## Notes

- Codex プロセスは Phase 2.5 で途中終了（pid 14808 消失、ログ 120 行で停止）。主要な論点は Gemini の批評と Codex の部分出力（task-registry 空白指摘）でカバー済みと判断
- Gemini 指摘の Time-Reversibility（LangGraph Checkpointing）は現状の運用で困っていないため本プランから除外
- 記事の前提「Orchestrator-Subagent から始めろ」自体は既存の agent_delegation セクションと整合、反論（Dochkina 2026）は Task 3 で補正
