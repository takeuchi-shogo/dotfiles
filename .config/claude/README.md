# Claude Code 設定

dotfiles リポジトリで管理する Claude Code のグローバル設定。
symlink 経由で `~/.claude/` に展開され、全プロジェクトで共有される。

## アーキテクチャ概要

```
                        ┌─────────────────────────────────┐
                        │         Claude Code CLI          │
                        │        (Orchestrator)            │
                        └────────┬────────────┬────────────┘
                                 │            │
              ┌──────────────────┤            ├──────────────────┐
              ▼                  ▼            ▼                  ▼
     ┌────────────┐    ┌────────────┐  ┌──────────┐    ┌────────────┐
     │   Hooks    │    │   Skills   │  │  Agents  │    │  Plugins   │
     │ (18 scripts)│    │ (20+ defs) │  │(35 specs)│    │ (7 enabled)│
     └─────┬──────┘    └─────┬──────┘  └────┬─────┘    └────────────┘
           │                 │               │
           ▼                 ▼               ▼
     ┌──────────┐    ┌──────────┐    ┌──────────────┐
     │ AutoEvolve│    │ Commands │    │  外部 CLI    │
     │  データ   │    │(10 cmds) │    │ Codex/Gemini │
     └──────────┘    └──────────┘    └──────────────┘
```

### 3層モデル連携

| 層                 | モデル                 | 役割                                     | 委譲ルール                   |
| ------------------ | ---------------------- | ---------------------------------------- | ---------------------------- |
| **Orchestrator**   | Claude Opus            | 全体制御、コード生成、レビュー統合       | -                            |
| **Deep Reasoning** | Codex CLI (gpt-5.4)    | 設計・推論・複雑なデバッグ               | `rules/codex-delegation.md`  |
| **Large Context**  | Gemini CLI (1M tokens) | 大規模分析・外部リサーチ・マルチモーダル | `rules/gemini-delegation.md` |

---

## ディレクトリ構造

```
.config/claude/
├── CLAUDE.md                     # グローバル指示書 (毎ターン読み込み)
├── README.md                     # ← このファイル
├── settings.json                 # メイン設定 (hooks, permissions, model)
├── settings.local.json           # ローカルオーバーライド
├── statusline.sh                 # ステータスライン表示スクリプト
│
├── agents/                       # サブエージェント定義 (35個)
├── commands/                     # カスタムコマンド (10個)
├── skills/                       # 再利用可能なスキル (20+)
├── rules/                        # 言語・ドメイン別ルール (13個)
├── references/                   # 参照ドキュメント (8個)
├── scripts/                      # Hook スクリプト (18個)
└── docs/
    └── research/                 # Gemini/Codex の出力保存先
```

### Symlink マッピング

dotfiles → home への個別 symlink で接続:

```
~/.claude/agents              → dotfiles/.config/claude/agents
~/.claude/commands            → dotfiles/.config/claude/commands
~/.claude/scripts             → dotfiles/.config/claude/scripts
~/.claude/settings.json       → dotfiles/.config/claude/settings.json
~/.claude/settings.local.json → dotfiles/.config/claude/settings.local.json
~/.claude/statusline.sh       → dotfiles/.config/claude/statusline.sh
~/.claude/CLAUDE.md           → dotfiles/.config/claude/CLAUDE.md
```

> **注意**: `references/` は個別 symlink されていない。スクリプトからは `Path(__file__).resolve().parent.parent / "references"` で参照する。

---

## サブエージェント (35個)

タスクの種類に応じて専門エージェントに委譲する。`triage-router` が最適なエージェントを推薦。

### コードレビュー系 (7エージェント + 4言語チェックリスト)

| エージェント            | 専門領域           | 用途                                                |
| ----------------------- | ------------------ | --------------------------------------------------- |
| `code-reviewer`         | 汎用レビュー       | 品質・セキュリティ・保守性の総合チェック（言語チェックリスト注入対応） |
| `code-reviewer-ma`      | 簡潔スタイル       | 直接的なシニアエンジニアスタイルのレビュー          |
| `code-reviewer-mu`      | 教育的スタイル     | 丁寧・建設的・教育的なレビュー                      |
| `codex-reviewer`        | 深い推論           | Codex CLI を活用した ~100行以上のセカンドオピニオン |
| `comment-analyzer`      | コメント品質       | ドキュメント・コメントの正確性と保守性分析          |
| `silent-failure-hunter` | エラーハンドリング | サイレント障害・不適切な catch/fallback の検出      |
| `test-analyzer`         | テスト品質         | テストカバレッジ・エッジケース・テスト設計の分析    |

言語固有チェックリスト（`references/review-checklists/`）:

| ファイル          | 対象拡張子              | 観点                                              |
| ----------------- | ----------------------- | ------------------------------------------------- |
| `typescript.md`   | `.ts/.tsx/.js/.jsx`     | 型安全性・React パターン・Node.js                 |
| `python.md`       | `.py`                   | 型ヒント・Pythonic イディオム・例外設計           |
| `go.md`           | `.go`                   | Effective Go・エラーハンドリング・並行処理        |
| `rust.md`         | `.rs`                   | 所有権・ライフタイム・unsafe 最小化               |

### アーキテクチャ・設計系 (4個)

| エージェント                 | 役割                                                             |
| ---------------------------- | ---------------------------------------------------------------- |
| `backend-architect`          | RESTful API・マイクロサービス・DB スキーマ・スケーラビリティ設計 |
| `nextjs-architecture-expert` | Next.js App Router・Server Components・パフォーマンス最適化      |
| `context-factory`            | プロジェクトサブシステムの仕様書・コンテキスト文書を自動生成     |
| `type-design-analyzer`       | 型設計のカプセル化・不変条件・型安全性を評価                     |

### 実装・デバッグ系 (6個)

| エージェント         | 役割                                                              |
| -------------------- | ----------------------------------------------------------------- |
| `build-fixer`        | ビルドエラー・型エラーを最小 diff で修正 (リファクタリングしない) |
| `debugger`           | 体系的な根本原因分析                                              |
| `codex-debugger`     | Codex CLI の深い推論によるエラー分析                              |
| `frontend-developer` | React コンポーネント・レスポンシブデザイン・アクセシビリティ      |
| `golang-pro`         | Go の goroutine・channel・interface パターン                      |
| `typescript-pro`     | TypeScript の高度な型システム・ジェネリクス・条件型               |

### メンテナンス・品質系 (4個)

| エージェント        | 役割                                               |
| ------------------- | -------------------------------------------------- |
| `doc-gardener`      | ドキュメントの鮮度検出と修正                       |
| `golden-cleanup`    | Golden Principles (GP-001〜005) 違反スキャン       |
| `security-reviewer` | OWASP Top 10 の深掘り脆弱性分析                    |
| `test-engineer`     | テスト戦略設計・テストスイート作成・カバレッジ分析 |

### インフラ・データ系 (2個)

| エージェント         | 役割                                                     |
| -------------------- | -------------------------------------------------------- |
| `safe-git-inspector` | Git 履歴の読み取り専用調査 (blame, log, diff, show のみ) |
| `db-reader`          | DB の読み取り専用クエリ (SELECT, SHOW, DESCRIBE のみ)    |

### リサーチ・ルーティング系 (4個)

| エージェント           | 役割                                              |
| ---------------------- | ------------------------------------------------- |
| `gemini-explore`       | Gemini CLI の 1M コンテキストを活用した大規模分析 |
| `triage-router`        | タスク分類と最適エージェント推薦                  |
| `agent-factory`        | 新しいエージェント定義ファイルの自動生成          |
| `constitution-factory` | プロジェクト固有 CLAUDE.md の自動生成             |

### AutoEvolve 系 (3個)

| エージェント         | 役割                                                           |
| -------------------- | -------------------------------------------------------------- |
| `autoevolve`         | セッションデータを元に設定変更を `autoevolve/*` ブランチに提案 |
| `autolearn`          | パターン分析、プロジェクトプロファイル生成                     |
| `knowledge-gardener` | 知識ベースの重複排除・陳腐化除去・昇格提案                     |

### その他 (1個)

| エージェント  | 役割                                                   |
| ------------- | ------------------------------------------------------ |
| `ui-observer` | Playwright によるUI観察 (EXPLORE モードのみ、変更不可) |

---

## カスタムコマンド (10個)

`/command` で呼び出すスラッシュコマンド。

| コマンド           | 説明                                                     | タスク規模 |
| ------------------ | -------------------------------------------------------- | ---------- |
| `/commit`          | conventional commit + 絵文字プレフィックスでコミット作成 | S          |
| `/review`          | 変更規模に応じてレビューアーを自動選択・並列起動         | M-L        |
| `/pull-request`    | PR 作成 (ブランチ push + タイトル/本文自動生成)          | S          |
| `/improve`         | AutoEvolve 改善サイクルの手動実行                        | L          |
| `/fix-issue`       | GitHub Issue を起点にした自動修正ワークフロー            | M-L        |
| `/rpi`             | Research → Plan → Implement の3フェーズ体系的実行        | L          |
| `/security-review` | 直近の変更に対する OWASP Top 10 セキュリティレビュー     | M          |
| `/challenge`       | 直前の変更を分析し、エレガント版再設計・厳しいレビュー   | M          |
| `/check-context`   | コンテキストウィンドウ使用率とセッション状態の確認       | S          |
| `/memory-status`   | メモリシステムの状態・使用量サマリー                     | S          |

---

## スキル (20+)

スキルは知識ベース+ワークフロー定義。エージェントが `skills:` で読み込んで使用する。

### コア

| スキル                           | 説明                                                            |
| -------------------------------- | --------------------------------------------------------------- |
| `review`                         | レビューアー自動ルーティング + テンプレートベースのレビュー出力 |
| `search-first`                   | 実装前に既存ツール/ライブラリ/パターンを検索                    |
| `ai-workflow-audit`              | AI workflow を監査し、skill / memory / script への昇格先を決める |
| `verification-before-completion` | 完了前の必須検証 (実コマンドで証拠を確認)                       |
| `continuous-learning`            | セッション中の修正・デバッグから再利用パターンを自動記録        |
| `skill-creator`                  | 新規スキル定義の作成ガイド                                      |

### ドメイン専門

| スキル                 | 説明                                               |
| ---------------------- | -------------------------------------------------- |
| `senior-architect`     | システムアーキテクチャ設計・技術選定               |
| `senior-backend`       | バックエンド API 設計・DB 最適化・セキュリティ     |
| `senior-frontend`      | React/Next.js コンポーネント設計・パフォーマンス   |
| `react-best-practices` | 40+ ルールの React パフォーマンス最適化ガイド      |
| `webapp-testing`       | Playwright ベースの Web アプリ E2E テスト          |
| `frontend-design`      | 高品質な UI デザインとプロダクショングレードの実装 |

### 外部モデル連携

| スキル         | 説明                                                   |
| -------------- | ------------------------------------------------------ |
| `codex`        | Codex CLI 実行 (設計・推論・リファクタリング)          |
| `codex-review` | Codex CLI による read-only レビュー + CHANGELOG 生成   |
| `gemini`       | Gemini CLI 実行 (大規模分析・リサーチ・マルチモーダル) |

### 生産性

| スキル                | 説明                                     |
| --------------------- | ---------------------------------------- |
| `daily-report`        | 全プロジェクト横断の日報生成             |
| `create-pr-wait`      | PR 作成→CI 監視→失敗時自動修正→再 push   |
| `interviewing-issues` | 曖昧な Issue を4段階インタビューで明確化 |

### Obsidian 連携

| スキル                 | 説明                                       |
| ---------------------- | ------------------------------------------ |
| `obsidian-vault-setup` | Obsidian Vault の AI 第二の脳セットアップ  |
| `obsidian-knowledge`   | Vault 内ナレッジの検索・整理・リンク       |
| `obsidian-content`     | Vault コンテキストを活用したコンテンツ生成 |

---

## Hooks システム (18スクリプト)

Claude Code のライフサイクルイベントにフックしてスクリプトを自動実行。

### イベントフロー

```
SessionStart ─→ session-load.js          セッション復元
               → context-drift-check.py   master からの乖離チェック
               → doc-garden-check.py       ドキュメント鮮度チェック

UserPromptSubmit ─→ agent-router.py       最適エージェント推薦

PreToolUse ─→ pre-commit-check.js         コミットメッセージ検証 (git commit 時)
             → suggest-gemini.py           大規模リサーチ時に Gemini 提案 (WebSearch 時)

PostToolUse ─→ auto-format.js             自動フォーマット (Edit/Write 時)
              → suggest-compact.js         コンテキスト逼迫時にコンパクト提案
              → golden-check.py            Golden Principles 違反チェック
              → error-to-codex.py          Bash エラー検出→codex-debugger 提案
              → post-test-analysis.py      テスト結果分析
              → plan-lifecycle.py          計画の進捗追跡

PreCompact ─→ pre-compact-save.js         コンパクト前にセッション保存

Stop/SessionEnd ─→ session-save.js        セッション状態保存
                  → session-learner.py     学習データを jsonl にフラッシュ

Notification ─→ macOS 通知 + サウンド
```

### 共有モジュール

| モジュール          | 役割                                       |
| ------------------- | ------------------------------------------ |
| `session_events.py` | イベントの emit / flush / 永続化の共通基盤 |

---

## ルール (13個)

`rules/` 配下のルールは Claude Code が自動的に条件に応じて読み込む。

### 共通ルール

| ファイル                   | 適用場面                       |
| -------------------------- | ------------------------------ |
| `common/code-quality.md`   | DRY, SOLID, 保守性             |
| `common/error-handling.md` | エラーハンドリングパターン     |
| `common/security.md`       | セキュリティベストプラクティス |
| `common/testing.md`        | テスト戦略・カバレッジ         |

### 言語別ルール

| ファイル        | 対象                                        |
| --------------- | ------------------------------------------- |
| `typescript.md` | TypeScript 型安全性、React パターン         |
| `react.md`      | React コンポーネント設計、hooks             |
| `go.md`         | Go イディオム、エラーハンドリング、並行処理 |
| `rust.md`       | Rust 所有権、ライフタイム、安全性           |
| `test.md`       | テスト構造・命名規則                        |
| `proto.md`      | Protocol Buffers                            |

### モデル委譲ルール

| ファイル               | 役割                                  |
| ---------------------- | ------------------------------------- |
| `codex-delegation.md`  | Codex CLI に委譲するタイミングと方法  |
| `gemini-delegation.md` | Gemini CLI に委譲するタイミングと方法 |
| `config.md`            | 設定管理ルール                        |

---

## リファレンス (8個)

`references/` は詳細ドキュメント。必要時にのみ参照される (Progressive Disclosure)。

| ファイル                    | 内容                                                                                          |
| --------------------------- | --------------------------------------------------------------------------------------------- |
| `workflow-guide.md`         | 6段階ワークフロー詳細、エージェントルーティング表、メモリシステム、トークン予算               |
| `golden-principles.md`      | GP-001〜005: 共有ユーティリティ、境界バリデーション、枯れた技術、エラーハンドリング、型安全性 |
| `improve-policy.md`         | AutoEvolve の改善方針・制約・禁止事項                                                         |
| `error-fix-guides.md`       | エラーパターン→根本原因→修正のマッピング (JS/TS/Go/Python/Rust)                               |
| `agent-design-lessons.md`   | エージェント設計のパターンと教訓                                                              |
| `readability-principles.md` | コード可読性の原則                                                                            |
| `claudeignore-template.md`  | .claudeignore テンプレート                                                                    |
| `mcp-server-template/`      | MCP サーバーの Python 実装テンプレート                                                        |

---

## プラグイン (7個)

`settings.json` の `enabledPlugins` で有効化:

| プラグイン          | 提供元                  | 機能                                             |
| ------------------- | ----------------------- | ------------------------------------------------ |
| `superpowers`       | superpowers-marketplace | worktree, 並列エージェント, TDD 等のワークフロー |
| `frontend-design`   | claude-code-plugins     | 高品質 UI デザイン生成                           |
| `pr-review-toolkit` | claude-code-plugins     | PR レビュー用の専門エージェント群                |
| `code-simplifier`   | claude-plugins-official | コードの簡素化・リファクタリング                 |
| `playground`        | claude-plugins-official | インタラクティブ HTML プレイグラウンド生成       |
| `gopls-lsp`         | claude-plugins-official | Go LSP サポート                                  |
| `datadog`           | kw-marketplace          | Datadog 連携                                     |

---

## MCP サーバー (3個)

| サーバー     | 用途                                                 |
| ------------ | ---------------------------------------------------- |
| `playwright` | Web アプリのブラウザ操作・スクリーンショット・テスト |
| `context7`   | ライブラリの最新ドキュメント・コード例の取得         |
| `deepwiki`   | DeepWiki からのナレッジ検索                          |

---

## AutoEvolve システム

[karpathy/autoresearch](https://github.com/karpathy/autoresearch) に着想を得た自律改善システム。
セッションデータを自動収集・分析し、設定自体を改善する提案を生成する。

### 全体像

```
セッション中                   セッション終了             オンデマンド / 定期
┌──────────────┐             ┌──────────────┐         ┌───────────────┐
│ error-to-    │──emit──┐    │ session-     │         │  /improve     │
│ codex.py     │        │    │ learner.py   │         │  コマンド     │
├──────────────┤        ▼    │  (flush)     │         └───┬───────────┘
│ golden-      │──emit──▶tmp │──▶ jsonl     │             │
│ check.py     │       file  └──────────────┘             ▼
└──────────────┘                                   ┌──────────────┐
                                                   │  autolearn   │→ insights/
                  ~/.claude/agent-memory/           ├──────────────┤
                  ├── learnings/*.jsonl             │  knowledge-  │→ 整理・昇格
                  ├── metrics/                     │  gardener    │
                  ├── insights/                    ├──────────────┤
                  └── logs/autoevolve.log           │  autoevolve  │→ autoevolve/*
                                                   └──────────────┘   ブランチ
                                                          ▲
                                                   improve-policy.md
                                                   (人間が方向を操る)
```

### 4層ループ

| 層                   | トリガー                      | やること                            |
| -------------------- | ----------------------------- | ----------------------------------- |
| **セッション**       | Stop / SessionEnd hook        | エラー・品質指摘を jsonl に自動記録 |
| **日次**             | daily-report skill            | 「今日の学び」セクションで振り返り  |
| **オンデマンド**     | `/improve` コマンド           | 分析 → 整理 → 設定改善提案          |
| **バックグラウンド** | `autoevolve-runner.sh` (cron) | 深夜に自律改善、朝レビュー          |

### データフロー

```
生データ (jsonl)
  → 3回以上出現 → insights/ に整理 (autolearn)
  → 確信度高 → MEMORY.md に追記 (knowledge-gardener が提案)
  → 汎用性高 → skill / rule に昇格 (人間が承認)
```

### 安全機構

- 設定変更は `autoevolve/*` ブランチで作業 (master 直接変更禁止)
- 1サイクル最大3ファイルの変更制限
- 変更後にテスト通過を確認
- 人間レビュー後にのみ merge

### セキュリティ境界

| Git 管理 (公開OK)                | ローカルのみ (非公開)       |
| -------------------------------- | --------------------------- |
| エージェント定義、スキル、ルール | learnings/\*.jsonl (生ログ) |
| hook ロジック、improve-policy.md | metrics/ (セッション統計)   |
| autoevolve の diff・履歴         | logs/ (実行ログ)            |

---

## ワークフロー

タスク規模に応じてプロセスをスケールする:

| 規模  | 例                       | 必須段階                                                   |
| ----- | ------------------------ | ---------------------------------------------------------- |
| **S** | typo 修正、1行変更       | Implement → Verify                                         |
| **M** | 関数追加、バグ修正       | Plan → Implement → Test → Verify                           |
| **L** | 新機能、リファクタリング | Plan → Implement → Test → Review → Verify → Security Check |

```
Plan → Implement → Test → Review → Verify → Security Check → Commit
失敗時: テスト/レビュー/検証/セキュリティ指摘 → Implement に戻る
```

レビューの並列数は変更規模でスケール:

| 変更行数 | レビューアー数 |
| -------- | -------------- |
| ~10行    | 省略           |
| ~50行    | 1つ            |
| ~200行   | 2つ            |
| 200行超  | 4並列          |

---

## Progressive Disclosure 設計

コンテキストウィンドウを効率的に使うための階層設計:

| 層           | ファイル      | 読み込みタイミング     | 目安サイズ  |
| ------------ | ------------- | ---------------------- | ----------- |
| **常時**     | `CLAUDE.md`   | 毎ターン               | ~69行       |
| **条件付き** | `rules/`      | 対象言語のコード変更時 | 各20-50行   |
| **必要時**   | `references/` | 明示的参照時           | 各100-300行 |
| **スキル**   | `skills/`     | コマンド実行時         | 各50-200行  |

---

## 使い方

```bash
# 改善サイクルを手動で回す
/improve

# 改善の方向性を変える
vim ~/.claude/references/improve-policy.md

# バックグラウンドで実行
~/.claude/scripts/autoevolve-runner.sh

# cron で毎日自動実行
# crontab -e
# 0 3 * * * ~/.claude/scripts/autoevolve-runner.sh

# 提案されたブランチを確認
git branch --list "autoevolve/*"
git diff master..autoevolve/YYYY-MM-DD

# ログを確認
cat ~/.claude/agent-memory/logs/autoevolve.log
```
