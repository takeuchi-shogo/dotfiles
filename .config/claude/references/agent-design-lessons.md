---
status: reference
last_reviewed: 2026-04-23
---

# Lessons from Building Claude Code: Seeing like an Agent

出典: Anthropic Thariq (@trq212) — 2026年2月
元記事の要約と、自分の設定への適用記録。

---

## 核心メッセージ

**「エージェントの目線で見ろ（See like an Agent）」**

ツール設計は科学ではなくアート。モデルの能力を観察し、出力を読み、実験を繰り返す。

---

## 5つの教訓

### 1. ツールはモデルが「自然に呼びたくなる」形にする

AskUserQuestion ツールの変遷:
- プレーンテキスト質問 → 摩擦が大きい
- マークダウン出力形式を指定 → 出力が不安定（Claude が形式を守らない）
- 専用ツール化 → **Claude が喜んで呼ぶようになった**

> "Even the best designed tool doesn't work if Claude doesn't understand how to call it."

**適用**: スキルの `description` フィールドが自動選択のキー。曖昧な description は Claude が正しくルーティングできない原因になる。

### 2. モデルが進化したらツールを見直す

TodoWrite → Task Tool への進化:
- 初期 Claude: Todo リストがないと迷子になる → 5ターンごとにリマインダー注入
- 現在の Claude: Todo に縛られて柔軟性が下がる → Task Tool（依存関係・サブエージェント連携）に置き換え

> "As model capabilities increase, the tools that your models once needed might now be constraining them."

**適用**: 6段階ワークフローの全段階強制 → S/M/L 規模別スケーリングに変更済み。定期的にスキル・ルールが「今のモデルにとって制約になっていないか」を見直す。

### 3. Progressive Disclosure で機能追加、ツール追加なし

Claude Code のツール数: ~20個。新ツール追加のハードルは高い。

Claude Code Guide Agent の事例:
- 問題: Claude が自分自身（Claude Code）の使い方を知らない
- 案1: システムプロンプトに全情報 → コンテキスト劣化、本業（コード書き）の邪魔
- 案2: ドキュメントリンクを渡す → Claude が大量に読み込む
- 解決: **専用サブエージェント**を作り、質問時だけ呼ばれるようにした

> "We were able to add things to Claude's action space without adding a tool."

**適用**: CLAUDE.md をコア原則のみ（69行）にスリム化し、詳細は `references/workflow-guide.md` に分離済み。スキルの3層ローディング（metadata → SKILL.md → references/）も同じ思想。

### 4. RAG → Grep → スキルの段階的文脈構築

初期: RAG ベクターDB → 脆弱でセットアップが重い、Claude に文脈が「与えられる」だけ
現在: Grep + スキルファイルの再帰的読み込み → Claude が「自分で」文脈を構築する

> "Claude went from not really being able to build its own context, to being able to do nested search across several layers of files."

**適用**: 自分の設計（ルーティングファイル → モジュール指示 → データファイル）は公式チームと同じ思想。

### 5. 少数のモデルに絞る

> "This is also why it's useful to stick to a small set of models to support that have a fairly similar capabilities profile."

ツール設計はモデルの能力に依存するため、対応モデルが増えると設計が発散する。

**適用**: settings.json で `model: opus` に統一、エージェントは `model: sonnet` に統一。triage-router のみ `haiku`。この3モデル体制を維持する。

---

## Breadcrumb Pattern（Codified Context より）

出典: "Codified Context: Infrastructure for AI Agents in a Complex Codebase" (Vasilopoulos, 2026)

AI が既に知っている概念には **Breadcrumb**（最小限のヒント）で十分。プロジェクト固有の情報のみ **Full Prose** で詳細に記述する。

### 5つのパターン

| パターン | 説明 | 例 |
|---------|------|---|
| **Terse Tables** | 属性・制約をテーブルで圧縮 | `\| field \| type \| constraint \|` |
| **Keyword Clusters** | 関連キーワードをカンマ区切りで列挙 | `React, RSC, App Router, Suspense` |
| **Shorthand References** | 規約名やパターン名だけで参照 | `Follow Effective Go. Use table-driven tests.` |
| **Compact Signatures** | 関数シグネチャだけで API を伝える | `func (s *Service) Create(ctx, req) (*Resp, error)` |
| **Trigger-Word Lists** | エージェントの起動条件をキーワードで列挙 | `Use when: build fails, type error, dependency issue` |

### 使い分けルール

```
if AI が一般的に知っている概念 (React, Go, REST, OWASP etc.):
    → Breadcrumb（パターン名、キーワード、参照先だけ）
    例: "Follow OWASP Top 10. Use parameterized queries."

elif プロジェクト固有の概念 (独自の命名規約、ビジネスロジック, 内部API):
    → Full Prose（詳細な説明、コード例、理由）
    例: "werrors.New は toplevel で使うな。stack trace が初期化時のものになる。"

elif 両方の要素がある (一般概念 + プロジェクト固有の変形):
    → Breadcrumb + 差分のみ Full Prose
    例: "Follow conventional commits. 絵文字プレフィックス必須: ✨ feat:, 🐛 fix:"
```

### 適用チェックリスト

- [ ] エージェントの description に Trigger-Word Lists を使っているか
- [ ] CLAUDE.md のコア原則は Shorthand References で十分では
- [ ] ルールファイルに React/Go の基礎知識を書いていないか（Breadcrumb で済む）
- [ ] プロジェクト固有の命名規約は Full Prose で書いてあるか
- [ ] テーブル化できる情報がダラダラ書かれていないか（Terse Tables へ）
- [ ] workflow-guide.md のルーティングテーブルは Terse Tables を活用しているか

### 既存設定への適用状況

| 対象 | 現状 | 改善案 |
|------|------|--------|
| エージェント description | ✅ Trigger-Word Lists 使用中 | — |
| CLAUDE.md コア原則 | ✅ Shorthand References | — |
| workflow-guide.md ルーティング | ✅ Terse Tables | — |
| golang-reviewer | ✅ Full Prose（プロジェクト固有） | — |
| 言語チェックリスト (ts/py/go/rs) | references/ に移行済み（プレフィックス軽量化） | — |
| rules/ | 要確認 | 一般知識→Breadcrumb に短縮可能か |

---

## Agent Sizing Guidelines（Codified Context 論文）

論文の 108,000 行 C# プロジェクトでの実測に基づく、エージェントサイジング指針。

### 2 クラスモデル

| クラス | 行数目安 | ドメイン知識比率 | 用途 |
|-------|---------|---------------|------|
| **Higher-capability** | 300-1,200行（平均 711行） | ~65% | 複雑ドメイン（ネットワーク同期、座標変換、アーキテクチャ） |
| **Standard** | 100-400行（平均 327行） | ~50% | 集中タスク（レビュー、リント、フォーマット） |

### ドメイン知識の構成要素

エージェントのドメイン知識は以下の 4 要素で構成する（行動指示と区別）:

| 要素 | 説明 | 例 |
|-----|------|---|
| **Symptom-Cause-Fix テーブル** | デバッグセッションから蒸留した故障パターン | `Desync on crits → Using local time → GetSyncedTime()` |
| **コードパターン** | do this / don't do this のコード例（ファイルパス付き） | `werrors.New は toplevel 禁止` |
| **Correctness Pillars** | ドメインの正しさを保証する不変条件 | `Same seed, Same counter, Same time` |
| **Known Failure Modes** | 過去に発生した具体的な障害と根本原因 | `古い仕様が deprecated パスへの配線を招いた` |

### エージェント作成の経験的ヒューリスティック

論文での最初のエージェント作成は、**デバッグセッション失敗率が最も高い 2 ドメイン**から。upfront 設計ではなく、観察された失敗パターンから駆動される:

```
if 同一ドメインの説明を 2 回以上繰り返した:
    → そのドメイン知識をエージェント仕様に codify

if デバッグが extended session で未解決:
    → 専門エージェントを作成して再スタートする方が速い
```

### 定量的ベンチマーク（論文 Table 3）

| 指標 | 値 |
|-----|---|
| プロジェクト規模 | 108,000 行 C# |
| Knowledge-to-Code Ratio | 24.2%（26,200 行 / 108,256 行） |
| T1 Constitution | 1 ファイル / ~660 行 / 0.6% |
| T2 Agents | 19 ファイル / ~9,300 行 / 8.6% |
| T3 Knowledge Base | 34 ファイル / ~16,250 行 / 15.0% |
| メンテナンスコスト | ~1-2 時間/週（5分/セッション + 30-45分/隔週レビュー） |
| メタインフラ overhead | 全プロンプトの 4.3% |

---

## 設計チェックリスト（定期見直し用）

- [ ] 各スキルの description は Claude が正確にルーティングできる精度か
- [ ] モデルアップデート後、既存のスキル・ルールが制約になっていないか
- [ ] CLAUDE.md に「たまにしか使わない情報」が混入していないか
- [ ] 新機能は Progressive Disclosure（サブエージェント、参照ファイル）で追加できないか
- [ ] Claude の出力を観察して「使いにくそうなツール」がないか

---

## Ralph Loop（関連知見）

Dan (@d4m1n) が公開した長時間 AI エージェント自動化ワークフロー。

### コンセプト
- **1タスク = 1セッション** でコンテキストウィンドウの劣化を回避
- 状態はファイルシステム + git に保持（コンテキストウィンドウではない）
- Docker サンドボックス内で Claude Code を繰り返し起動

### 構造
```
.agent/
├── PROMPT.md      # メインのイテレーション指示
├── SUMMARY.md     # プロジェクト概要
├── STEERING.md    # 実行中の方向修正（人間が編集可能）
├── tasks.json     # タスク一覧
├── tasks/         # 個別タスク仕様
└── logs/          # 進捗ログ
```

### ループの仕組み
```bash
for i in $(seq 1 $N); do
  docker sandbox run claude "PROMPT.md を読んで次のタスクをやれ"
  # AIが実装・テスト・コミットして終了 → 次のループ（フレッシュなコンテキスト）
done
```

### 向き不向き
- 向いている: MVP、テスト自動化、マイグレーション、ボイラープレート
- 向いていない: ピクセルパーフェクトなデザイン、斬新なアーキテクチャ、セキュリティクリティカル

### 核心の洞察
> 人間の役割は「コードを書く人」から「要件を明確に定義する人」に変わる。PRD の品質がそのまま成果物の品質になる。

### インストール
```bash
npx @pageai/ralph-loop  # プロジェクトルートで実行
```

Claude Code の機能ではなく、外部のオーケストレーション層。CLI エージェントは交換可能（Codex, Gemini CLI 等）。

---

## Self-Rejection Rule Pattern

出典: 30-subagents-2026 absorb (T5)。記事 "30 Claude Code Sub-Agents I Actually Use in 2026" から抽出した novel な prompt design pattern。

エージェント自身に「自分の出力をチェックして再生成を強制する明示的な reject rule」を埋め込む。後段の reviewer に依存せず、agent prompt 内で品質ゲートを完結させる。

### 例

| Agent | Reject 条件 |
|-------|------------|
| spec-writer | success metric が vanity (page views, time on page) ならリジェクト → action metric に書き直す |
| edge-cases | 「null チェック」単独で具体シナリオがない edge case はリジェクト |
| counterargument | 反論が edge case のみで本質を突いていなければリジェクト |
| decision-log | options が 2-3 個揃わない「I just decided」記録はリジェクト |
| methodology-critic | pre-registration がない experimental claim を `strong` 評価しない |
| daily-plan | must-ship が longest focus window に収まらないなら plan 自体をリジェクト |

### 既存実装

- `code-reviewer.md` の COMPLETION CONTRACT (Findings/Scores/Verdict 3 セクション必須) は self-reject 系の先例
- 他 33 subagent の大半には体系化されていない

### 適用ガイドライン

- **新規 subagent / skill 設計時**: 「この agent が出力すべきでない悪い形」を 1-3 個明示する
- **既存 prompt 強化時**: 全展開ではなく、reviewer 系・generator 系の高 stakes agent に限定して導入する（Pruning-First）
- **Static-checkable rules は外に出す**: linter/hook で表現できるものは prompt に書かず mechanism に寄せる（CLAUDE.md 原則）。reject rule は agent の意味判断にしか書けないものに限る

---

## Subagent Count Ceiling

出典: 30-subagents-2026 absorb (メタ発見、Gemini grounding)。

### 経験則

- 50+ subagent を持つ harness では triage 性能が劣化する (Gemini 報告: 9/10 → 5/10、auto-delegation の精度低下 + token cost 増加)
- 個別の subagent description が「似ている」ほど、description-based router の判別が崩れる
- Single-purpose 原則を守った狭い agent ほど、数が増えると相互の境界が曖昧になる

### 現状

- dotfiles の `.config/claude/agents/` 実数: **33 個** (2026-05-02 時点)
- 警戒ラインまで残り **17 個**
- 直近 absorb で新規 subagent を追加していないのは正解 (例: 30-subagents-2026 absorb は採用 0 件)

### ガード

- 新規 subagent 追加前に **既存 33 個との責務重複チェック**を行う
- 既存 subagent の prompt 拡張で達成できる場合、新規追加より優先する (Pruning-First)
- 50 個に近づいた段階で削除候補を `/skill-audit` で洗い出す (Build to Delete 原則)
- subagent 数の単純集計は `ls .config/claude/agents/*.md | wc -l` で随時確認できる
