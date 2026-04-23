---
status: active
last_reviewed: 2026-04-23
---

# Multi-Agent Coordination Patterns

> 出典: Anthropic "Multi-agent coordination patterns: Five approaches and when to use them" (Cara Phillips et al., 2026-04-10)
> 詳細分析: `docs/research/2026-04-11-multi-agent-coordination-patterns-analysis.md`

協調パターンを 5 つの原型に分類し、各パターンの失敗モード・termination 条件・当セットアップでの対応アセットを一箇所に集約する。

**原則: Orchestrator-Subagent から始める**。問題特性で示唆されるだけで他パターンに evolve しない。観測された限界（情報ボトルネック、context overflow、逐次化ボトルネック）に応じてのみ移行する。

---

## パターン比較表

| パターン | 構造 | 解く問題 | 主な失敗モード | 第一選択の場面 |
|---|---|---|---|---|
| **Generator-Verifier** | 生成→評価→フィードバック | 品質クリティカルな出力 | 曖昧な評価基準、無限ループ、Reward Hacking | TDD、コードレビュー、completion-gate |
| **Orchestrator-Subagent** | 親が計画・委譲・統合 | 並列可能な独立サブタスク | 情報ボトルネック、逐次実行、coordinator context overflow | デフォルト（最初にこれ） |
| **Agent Teams** | 永続ワーカーが共有キューから claim | 長時間・独立・コンテキスト蓄積 | 厳格な task independence、セッション揮発 | 大規模移行、クロスレイヤー同時開発 |
| **Message Bus** | イベント駆動 pub/sub | 複数ソースからの非同期イベント | router 精度依存、silent failure | セキュリティ運用、複数アラート |
| **Shared State** | 永続ストア経由の分散協調 | 中央集権の解除、協調リサーチ | 重複作業、予測不能な結果、concurrent write collision | 協調リサーチ、memory sync |

---

## Pattern 1: Generator-Verifier

**定義**: 1 つのエージェント（Generator）が成果物を生成し、別のエージェント（Verifier）が明示的な評価基準で判定してフィードバックするループ。

**失敗モード**:

- **曖昧な評価基準**: Verifier の判定が主観に流れると無限ループ
- **Reward Hacking**: Generator が Verifier の採点関数を学習して表面上パスするだけの成果物を返す
- **Convergence Stall**: Generator と Verifier が同じ誤認識を共有して収束しない

**Termination 条件**: MAX_RETRIES、明示的 PASS/NEEDS_FIX/BLOCK verdict、ralph-loop max-iterations。

### 当セットアップでの対応

| アセット | 役割 |
|---|---|
| `references/review-loop-patterns.md` | Review-Fix サイクル、Oscillation detection |
| `references/review-consensus-policy.md` | 合意コスト、Outlier 検出、Reward Hacking Mitigation |
| `scripts/policy/completion-gate.py` | MAX_RETRIES=2 の Evaluator-Optimizer 実装 |
| `.claude/skills/ralph-loop/` | max-iterations=100 の自律ループ |
| `.claude/agents/code-reviewer.md`, `codex-reviewer.md` | Verifier ペア（異種シグナル） |

### Evolution シグナル（このパターンの外に出る）

- Generator / Verifier の役割分離が現状の review ループで不要になっている → シングルエージェントで完結
- Reward Hacking が観測される → Reward Hacking Mitigation セクションに従い人間監査 N サイクル毎

---

## Pattern 2: Orchestrator-Subagent **(当セットアップの基本形)**

**定義**: 親エージェント（Orchestrator）がタスクを分解し、サブエージェント群（Worker）に委譲し、結果を統合する。最もシンプルで広範に使える。

**失敗モード**:

- **Information Bottleneck**: サブエージェントの発見が要約時に失われる
- **Coordinator Context Overflow**: 並列サブエージェントが 5-10 を超えると親のコンテキストが逼迫
- **Sequential Bottleneck**: 全サブエージェントが親を経由するため逐次化
- **Never Delegate Understanding 違反**: 統合（synthesis）を委譲すると浅い結論になる

**Termination 条件**: 全サブエージェント完了、親の統合完了、タスク規模判定による早期終了。

### 当セットアップでの対応

| アセット | 役割 |
|---|---|
| `CLAUDE.md <agent_delegation>` | Opus は判断・統合、実作業は委譲する原則 |
| `references/subagent-delegation-guide.md` | Sync/Async/Scheduled パターン、Parallelizability Gate、Coordinator Context Budget |
| `references/agent-orchestration-map.md` | 4 フェーズコーディネーション（Research / Synthesis / Implementation / Verification） |
| `scripts/policy/agent-router.py` | キーワードベースの委譲先推奨（hook） |
| `.claude/agents/triage-router.md` | 不明瞭タスクの種別判定 |
| `references/workflow-guide.md` | タスク規模 S/M/L と委譲戦略 |

### Evolution シグナル

観測シグナルに応じて別パターンに evolve する（いずれか 2 つ以上が継続的に観測されたら移行検討）:

| シグナル | 移行先 | 根拠 |
|---|---|---|
| 並列サブエージェント数が常に 10+ / coordinator context > 70% | **Sequential Protocol** (Dochkina 2026) or **Agent Teams** | 情報ボトルネック解消 |
| サブエージェントが互いの発見を必要とする | **Agent Teams** (SendMessage ピア通信) | 直接通信で統合コストを削減 |
| 役割固定が柔軟性を損ねる | **Sequential Protocol** | 役割自律で 14% 向上 (Dochkina 2026) |
| 長時間タスクで親がブロックされる | **cmux Worker** (Async) or **Agent Teams** | 並行実行 |

> **数値の段階性**: 並列度 **7+** は Coordinator Context Budget の Danger ゾーンで `summary 層挿入` を試すシグナル（パターン内の対処）。**10+** はそれでも改善しないときの**パターン自体の切替**シグナル。詳細: `references/subagent-delegation-guide.md § Coordinator Context Budget`

---

## Pattern 3: Agent Teams

**定義**: コーディネーター（Lead）が永続ワーカーを spawn し、ワーカーは共有タスクキューから claim して実行、ピア間で直接通信（SendMessage）し、セッション内でコンテキストを蓄積する。

**失敗モード**:

- **Task Independence 違反**: 同一ファイル編集 → マージコンフリクト確定
- **Session Ephemeral**: Agent Teams はセッションと生死を共にする（`/resume` 不可）。セッション死亡 = チーム消滅
- **Teammate Briefing 不足**: spawn prompt が薄いと teammate は凡庸な結果を返す
- **Lead が自分で実装**: delegate mode OFF で Lead が作業を始めると最も多い失敗

**Termination 条件**: 全 teammate のタスク完了、Lead の統合完了、セッション終了（チーム消滅）。

### 当セットアップでの対応

| アセット | 役割 |
|---|---|
| `references/cmux-ecosystem.md` | cmux-team 4 層（Master → Manager pull → Conductor → Agent） |
| `references/subagent-vs-cmux-worker.md` | サブエージェント / cmux Worker の使い分け |
| `references/subagent-delegation-guide.md § サブエージェント vs Agent Teams` | 判断基準（Green/Yellow/Red 適性） |
| `references/task-registry-schema.md` | Async/Scheduled の lifecycle 追跡スキーマ |
| `scripts/lib/task_registry.py` | register/update_status/list_active の実装 (133行) |
| `scripts/runtime/agent-invocation-logger.py` | PostToolUse:Agent hook による全呼び出し観測 (→ `agent-invocations.jsonl`) |
| `skills/autonomous/scripts/run-session.sh` | task_registry を実際に呼ぶセッションランナー |

> **棲み分け注記**: `task-registry.jsonl` は明示的 lifecycle 追跡（register → running → completed）、`agent-invocations.jsonl` は全 Agent 呼び出しの観測ログ（skill-audit / cascade 分析用）。詳細は `references/task-registry-schema.md § agent-invocations.jsonl との棲み分け` を参照。

### Evolution シグナル

- セッション揮発が問題になる → `/checkpoint` で中間成果を保全、または Agent Teams を諦めて Orchestrator-Subagent + 永続 task registry に戻す
- Lead の統合コストが過大 → teammate 数を 5 以下に抑える、または Shared State で統合を分散

---

## Pattern 4: Message Bus

**定義**: イベントソース（複数）が pub/sub バスにメッセージを流し、ルーターエージェントが重要度分類して各ハンドラエージェントに振り分ける。エージェント同士は疎結合で、同期的な呼び出し関係を持たない。

**失敗モード**:

- **Router 精度依存**: 分類ミスが silent failure を生む
- **デバッグ困難**: イベント発火順序とハンドラ実行順序が非同期で追跡しにくい
- **前提ズレ（当セットアップ特有）**: hooks は Claude Code **プロセス内**の fan-out であり、複数エージェント間の**非同期 pub/sub ではない**

**Termination 条件**: 各ハンドラが独立に完了。バス自体は永続。

### 当セットアップでの対応（前提ズレのため限定的）

| アセット | 役割 |
|---|---|
| `.config/claude/settings.json (hooks)` | PreToolUse / PostToolUse / UserPromptSubmit / Stop / SubagentStop の多段 event-driven |
| `scripts/runtime/session_observer_router.py` | セッションイベントのルーティング |
| `scripts/policy/agent-router.py` | キーワードベース推奨 |

> **注記**: これらは Claude Code プロセス内のイベント fan-out であり、記事が指す multi-agent pub/sub とは前提が異なる。真の Message Bus（複数独立プロセスの非同期協調）は当セットアップの具体的必要性がないため実装しない。記事の Message Bus フレームで dotfiles を語る場合は、この前提ズレを必ず明示すること。

### Evolution シグナル

- 独立イベントソースが複数生まれた場合（例: 複数リポジトリの CI、Slack、cron）に検討。現状は該当なし。

---

## Pattern 5: Shared State

**定義**: 中央コーディネーター不在で、複数エージェントが永続ストア（memory, vector DB, tasklist 等）を介して協調する。協調的リサーチで有効。

**失敗モード**:

- **重複作業**: エージェント同士の認識ズレで同じタスクを複数回実行
- **予測不能な結果**: termination 条件の管理が難しく、reactive loop に陥る
- **Concurrent Write Collision**: 複数エージェントの同時書き込みで last-write-wins
- **Reactive Loop**: 他エージェントの出力に反応して無限に走り続ける

**Termination 条件**: 明示的な termination policy（例: N イテレーション上限、外部トリガー）。

### 当セットアップでの対応

| アセット | 役割 |
|---|---|
| `references/cc-7-layer-memory-model.md` Layer 7 | Cross-Agent Communication 層の位置づけ |
| `scripts/runtime/sync-memory-to-vault.sh` | agent-memory ↔ Obsidian Vault の単方向同期 |
| `references/task-registry-schema.md` | 共有タスクキューの schema |
| `~/.claude/agent-memory/` | 各エージェントの永続知識ストア |

> **並行書き込みリスク**: 現状は単方向・非同期同期で競合リスクが低いが、並列度が上がると last-write-wins 問題が顕在化する。詳細は `references/cc-7-layer-memory-model.md § Concurrent Write Constraints` を参照。

### Evolution シグナル

- 並列度 N=5 以上で書き込み競合が観測された場合 → CRDT 採用検討、または書き込み先を agent 毎に partition
- 現状は reactive loop のリスク低（明示トリガー起動のみ）

---

## Pattern Selection Framework

```
問題特性からパターンを選ぶ:

品質クリティカルで明示的評価基準がある?
  → Generator-Verifier

並列可能なサブタスクで親が統合できる?
  → Orchestrator-Subagent    ★ デフォルトはこれ

長時間 / 独立 / コンテキスト蓄積が必要?
  → Agent Teams
  （ただし session ephemeral に注意）

複数の非同期イベントソースからのトリアージ?
  → Message Bus
  （hooks fan-out とは別物。当セットアップで真の用途なし）

中央集権せず永続ストア経由で協調したい?
  → Shared State
  （concurrent write 対策が必須）

迷ったら?
  → Orchestrator-Subagent から始める
```

### Scaffolding > Model 原則との整合

> CLAUDE.md `<core_principles>`: Scaffolding > Model — 協調プロトコル選択が品質差異の 44%、モデル選択は ~14%

パターン選択（scaffolding）がモデル選択よりも品質に与える影響が大きい。適切なパターンを選ぶことは Opus vs Sonnet を選ぶより重要。

---

## Sequential Protocol (Dochkina 2026) — Orchestrator-Subagent の発展形

> 出典: Dochkina 2026 "Drop the Hierarchy and Roles" — 25,000+ タスクで実証。Sequential (固定順序 + 役割自律) が Coordinator (集中型) を **+14%**、Shared (完全自律) を **+44%** 上回る。

Orchestrator-Subagent の失敗モード「情報ボトルネック + 役割固定」への処方箋。パターン 2 の発展形として位置づける。

**原則**: 事前に役割を割り当てない。ミッション・プロトコル・高能力モデルを与え、役割は自律的に決めさせる。

### 適用判断

詳細は以下 2 箇所にまたがる:

- `references/agent-orchestration-map.md § 3.5 Sequential Protocol 検討`
- `references/subagent-delegation-guide.md § Sequential Protocol` および `§ Sequential Protocol 移行判断基準`

### 前提条件（boundary conditions）

Dochkina 2026 の実験条件を個人 harness に直接適用するときの誤解を避けるため、以下を明記:

| 条件 | Dochkina 実験 | 個人 harness (dotfiles) |
|---|---|---|
| 役割プール | 5000+ | 10-20 の専門エージェント |
| タスク数 | 25,000+ | 1 セッションで 1-10 タスク |
| 並列度 | 高 | 1-3 並列が主 |
| 役割動的選択 | 自動 | 半自動（agent-router.py + 人間判断） |

**個人 harness での適用範囲**: Sequential の「構造最小・役割自律」原則は `/review` の並列起動、`/research` のサブタスク分解、EPD フェーズ内の作業分担に適用可能。ただし 14% の改善幅は実測されておらず、記事の数字をそのまま転用しない。

---

## 参照

- `references/subagent-delegation-guide.md` — パターン 2/3 の実装詳細
- `references/agent-orchestration-map.md` — 全体俯瞰 + フェーズ設計
- `references/cmux-ecosystem.md` — パターン 3 (Agent Teams) の cmux 実装
- `references/review-consensus-policy.md` — パターン 1 (Generator-Verifier) の合意ポリシー
- `references/cc-7-layer-memory-model.md` — パターン 5 (Shared State) の Layer 7
- `references/task-registry-schema.md` — パターン 3/5 の永続ストア schema
- `references/workflow-guide.md` — タスク規模判定と委譲戦略
- `docs/research/2026-04-11-multi-agent-coordination-patterns-analysis.md` — 元記事の Gap Analysis
