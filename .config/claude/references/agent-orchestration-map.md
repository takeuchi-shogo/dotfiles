---
status: reference
last_reviewed: 2026-04-23
---

# Agent Orchestration Map

Claude Code エージェントシステムの全体構造と委譲フローを俯瞰する。

---

## 1. Implicit Coordinator Pattern

明示的な "orchestrator" エージェントは存在しない。代わりに以下の3層で暗黙に協調する:

| 層 | 担当 | 役割 |
|---|---|---|
| **Coordinator** | Claude Code 本体 | タスク解釈、規模判定、エージェント選択、結果統合 |
| **Router** | hooks (agent-router.py, file-pattern-router.py) | キーワード・ファイルパターンから委譲先を自動推奨 |
| **Classifier** | triage-router エージェント | 不明瞭なタスクの種別判定、最適エージェントへルーティング |

Claude Code 本体が全ての意思決定権を持ち、hooks は「推奨」のみ行う（強制しない）。

### Coordinator の中核教義: "Never delegate understanding"

> Claude Code 本体 Ch10 "Tasks, Coordination, and Swarms" より。
> CC 本体のコーディネーターは 3 ツール (Agent / SendMessage / TaskStop) のみを持ち、
> 370 行のシステムプロンプトで "Never delegate understanding" を中核教義として指示している。
> Opus (= Coordinator) が synthesis を自分で行うことが、マルチエージェント品質の最大因子。

**原則**: Opus は「判断・計画・統合」を自分でやり、「作業」を委譲する。
以下は**サブエージェントに絶対に委譲してはいけない**:

| 委譲不可 | 理由 |
|---------|------|
| タスクの解釈・要件の再確認 | サブエージェントは親の文脈を持たない。誤解の増幅 |
| 複数の調査結果の統合 | 統合こそが Opus の付加価値。丸投げすると浅い結論になる |
| ユーザーへの質問の判断 | "何を聞くか" は親の情報状態に依存する |
| リスク判断・撤退判断 | 部分情報からの判断は hallucination を招く |
| 最終レポートの要約 | サブエージェントはトーンを揃えられない |

逆に、以下は**積極的に委譲する**:

| 委譲推奨 | 委譲先 |
|---------|-------|
| ファイル探索・grep | Sonnet Explore |
| 定型実装・テスト作成 | Sonnet / 専門エージェント |
| URL 取得 + 要約 | Haiku |
| 外部リサーチ / 1M 分析 | Gemini |
| リスク分析のセカンドオピニオン | Codex |

### 4 フェーズコーディネーションパターン

CC 本体の coordinator prompt が規定する 4 フェーズは、任意のマルチエージェントワークフロー
（/epd, /rpi, /research, /absorb）のテンプレートとして転用できる:

| フェーズ | 担当 | やること | やらないこと |
|---------|------|----------|--------------|
| **Research** | サブエージェント群（並列可） | ファイル探索・調査・データ収集 | 統合・結論出し |
| **Synthesis** | **Coordinator (Opus) のみ** | 複数調査結果を 1 つの理解に統合、矛盾の解消、優先順位付け | サブエージェント委譲、ユーザー質問を後回し |
| **Implementation** | サブエージェント群（並列可） | Synthesis の決定に従って変更を実行 | 設計判断（Synthesis で確定済み） |
| **Verification** | 専門サブエージェント | テスト実行、レビュー、edge case 検証 | 修正（発見した問題は Coordinator に返す） |

**Synthesis フェーズはサブエージェントに丸投げしない**。これが "Never delegate understanding" の実践的な意味。

---

## 2. 3層モデルマップ

```
┌─────────────────────────────────────────────────┐
│  Claude Code (Opus/Sonnet/Haiku)                │
│  ─ 計画・実装・レビュー統合・ユーザー対話      │
│                                                  │
│  ┌──────────────┐    ┌──────────────────┐       │
│  │ Subagents    │    │ Skills           │       │
│  │ (agents/)    │    │ (/review, /epd…) │       │
│  └──────┬───────┘    └────────┬─────────┘       │
└─────────┼─────────────────────┼──────────────────┘
          │                     │
    ┌─────▼─────┐         ┌────▼─────┐
    │ Codex CLI │         │ Gemini   │
    │ 深い推論  │         │ 1M分析   │
    │ リスク分析│         │ リサーチ │
    └───────────┘         └──────────┘
```

### 委譲判断

| 条件 | 委譲先 |
|---|---|
| 設計判断・リスク分析・深い推論 | Codex (`codex-plan-reviewer`, `codex-reviewer`, `codex-debugger`) |
| 大規模コード分析・外部リサーチ・マルチモーダル | Gemini (`gemini-explore`) |
| ドメイン特化タスク | 専門サブエージェント（下記参照） |
| Claude の 200K で十分なタスク | Claude Code 本体で直接処理 |

---

## 3. Hook → Agent 起動マップ

| Hook | トリガー | 推奨/起動するエージェント |
|---|---|---|
| `agent-router.py` | タスクキーワード検出 | 各専門エージェント（additionalContext で推奨） |
| `file-pattern-router.py` | ファイルパターン検出 | 対応する専門エージェント（.md → doc-gardener 等） |
| `error-to-codex.py` | Bash エラー検出 | `codex-debugger`（エラー分析） |
| `suggest-gemini.py` | 大規模分析キーワード | `gemini-explore`（1M コンテキスト活用） |
| `post-test-analysis.py` | テスト失敗 | `test-analyzer`（失敗分析） |
| `golden-check.py` | コード変更 | `golden-cleanup`（GP 逸脱検出） |
| `doc-garden-check.py` | ドキュメント変更 | `doc-gardener`（陳腐化検出） |
| `completion-gate.py` | タスク完了宣言 | 検証ワークフロー強制 |

---

## 3.5 Sequential Protocol 検討 (Dochkina 2026)

25,000+ タスクの実験で、**Sequential（固定順序 + 役割自律）が Coordinator を 14%、Shared を 44% 上回る**ことが示された。

| プロトコル | 品質 | 当セットアップの対応 |
|---|---|---|
| **Coordinator** (集中型) | 0.767 | 現状の Implicit Coordinator |
| **Sequential** (固定順序+役割自律) | **0.875** | → 移行候補 |
| Shared (完全自律) | 0.503 | Agent Teams の一部 |

### 現アーキテクチャへの示唆

1. **レビューチェーン**: 既に Parallelization パターン（並列起動→統合）で高品質。Sequential 化の余地は小さい
2. **EPD / autonomous フロー**: Spec → Build → Review は Prompt Chaining だが、各フェーズ内で「順序は固定・役割は自律」にすると品質向上の可能性
3. **能力閾値**: 強いモデル (Claude Opus/Sonnet) には自律度を高め、弱いモデルには構造を多く与える

### 適用ガイドライン

- 現在の Coordinator パターンを破壊する必要はない。**既存のオーケストレーションパターン内で Sequential の原則（最小構造+最大役割自律）を適用する**
- 詳細: `subagent-delegation-guide.md` § Sequential Protocol

### 移行判断シグナル

> 出典: Anthropic "Multi-agent coordination patterns" (2026-04-10) — Orchestrator-Subagent から Sequential への移行は段階的判断

Implicit Coordinator から Sequential 原則への移行は、観測シグナルに基づく:

| 移行検討シグナル（2 つ以上で検討） | 移行しない条件 |
|---|---|
| Coordinator context > 70% を継続観測 | 並列性が本質的（独立ファイルレビュー） |
| サブエージェント結果の情報損失が繰り返される | 逐次依存がない |
| 役割固定が柔軟性を損なう（事前 role に合わないタスクが頻出） | 5 分以内で完了する見込み |
| サブエージェント数が常に 7+ で summary 層でも改善しない | セキュリティ制約あり（db-reader 等） |

### Dochkina 2026 boundary conditions

論文の +14% / +44% 改善幅は dotfiles に直接転用できない:

| 条件 | Dochkina | dotfiles |
|---|---|---|
| 役割プール | 5000+ | 10-20 |
| タスク数 | 25,000+ | 1 セッション 1-10 |
| 並列度 | 高 | 1-3 |

**結論**: 数値ではなく **構造原則**（最小構造 + 最大役割自律）のみを転用する。

詳細な移行 3 ステップと boundary conditions: `subagent-delegation-guide.md § Sequential Protocol 移行判断基準`

---

## 4. Agent 依存グラフ

### レビューチェーン (`/review` スキル)

```
/review (スキル)
  ├── code-reviewer        ← 常時（変更規模に応じて起動）
  ├── codex-reviewer       ← ~100行以上の変更
  ├── edge-case-hunter     ← ロジック変更時
  ├── silent-failure-hunter ← エラーハンドリング変更時
  ├── cross-file-reviewer  ← 2ファイル以上の変更
  ├── comment-analyzer     ← ドキュメント追加時
  ├── type-design-analyzer ← 新規型定義時
  ├── golang-reviewer      ← Go コード変更時
  ├── product-reviewer     ← spec file 存在時
  └── design-reviewer      ← UI ファイル変更時
```

### タスクルーティング (triage-router)

```
triage-router
  ├── backend-architect         ← API/DB 設計
  ├── nextjs-architecture-expert ← Next.js
  ├── frontend-developer        ← React/UI
  ├── golang-pro                ← Go 実装
  ├── typescript-pro            ← TS 実装
  ├── test-engineer             ← テスト作成
  ├── debugger                  ← バグ調査
  ├── security-reviewer         ← セキュリティ
  └── build-fixer               ← ビルドエラー
```

### リサーチチェーン (`/research` スキル)

```
/research (スキル)
  ├── claude -p (並列ヘッドレス)  ← 文献調査
  ├── gemini-explore             ← 大規模分析・外部リサーチ
  └── codex exec                 ← 設計批評・深い推論
```

---

## 5. Feedback & Recovery Paths

| 失敗シナリオ | 回復パス |
|---|---|
| レビュー指摘 | Implement に戻り修正 → 再レビュー |
| テスト失敗 | `debugger` → 根本原因特定 → 修正 → 再テスト |
| Bash エラー | `error-to-codex.py` → `codex-debugger` で深い分析 |
| デバッグ膠着 | 専門エージェント作成 → 新セッションで再試行（G5 heuristic） |
| コンテキスト枯渇 | サブエージェントに委譲 / `/checkpoint` → 新セッション |
| Plan 破綻 | `codex-plan-reviewer` で再分析 → Plan 修正 → Decision Log 記録 |

---

## 6. 運用ガイドライン

詳細は `workflow-guide.md` のエージェント委譲パターンを参照。
