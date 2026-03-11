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
| code-reviewer-ma/mu | ✅ Full Prose（プロジェクト固有） | — |
| 言語チェックリスト (ts/py/go/rs) | references/ に移行済み（プレフィックス軽量化） | — |
| rules/ | 要確認 | 一般知識→Breadcrumb に短縮可能か |

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
