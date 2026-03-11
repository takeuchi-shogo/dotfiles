# Three Sub-Agent Patterns Analysis — dotfiles リポジトリ照合レポート

> **原文**: "Three sub-agent patterns you need for your agentic system"
> **分析日**: 2026-03-12
> **対象**: dotfiles リポジトリの Claude Code ハーネスシステム

## 記事の3パターン概要

| パターン | 説明 | ユースケース |
|---|---|---|
| **Sync** | 親がブロックして結果を待つ | データ参照、分析、次ステップに必要な情報 |
| **Async** | 発火して忘れる、完了時にユーザーに直接報告 | リサーチ、レポート生成、長時間タスク |
| **Scheduled** | 将来の特定時刻に実行 | フォローアップ、定期チェック、リマインダー |

## 記事の核心メッセージ

1. **コンテキスト圧縮が真のROI** — 並列性ではなくコンテキスト管理が本質
2. **Generic > Specialized** — 特化エージェントのルーティング層が複雑化する
3. **Two tools, not one** — モデルはパラメータ最適化よりツール選択が得意
4. **Depth-1** — サブエージェントはサブエージェントを生まない
5. **フレーミング差異** — Sync は簡潔に、Async は詳細に

## dotfiles との照合

### 既に実装されているもの

| 記事のパターン | dotfiles の対応実装 | 成熟度 |
|---|---|---|
| Sync（ブロッキング委譲） | Agent ツール — `/review` で 2-4 エージェント並列起動、結果を統合 | **高** |
| Async（ファイア＆フォーゲット） | `claude -p` 子プロセス（`/research`, `/autonomous`）, `session_events.emit_event()` | **中** |
| Scheduled（後で実行） | `autoevolve-runner.sh` cron ジョブ（毎日 3:00）, `/daily-report` | **低〜中** |
| コンテキスト圧縮 | `output-offload.py`（150行超を退避）, `suggest-compact.js`（30/50編集で警告）, トークン予算管理 | **高** |
| 深度制限（Depth-1） | サブエージェントは Agent ツールを持たない設計 | **高** |
| Generic > Specialized | review-checklists/ への統合（37→33エージェント削減）、Progressive Disclosure | **中〜高** |

### dotfiles が記事を超えている部分

| 記事の限界 | dotfiles の実装 |
|---|---|
| 失敗ハンドリングは Inngest 任せ | completion-gate.py の Ralph Loop + MAX_RETRIES=2、autonomous の budget cap + max sessions |
| Specialization vs Generic の二項対立 | 段階的な特化: 汎用 code-reviewer にチェックリスト注入 + コンテンツベース specialist 自動追加 |
| 単一チャネルルーティング | マルチモデル統合（Claude + Codex + Gemini）のモデル間委譲ルーティング |
| 学習・自己改善に言及なし | AutoEvolve 4層ループ（記事の "Self-iterating agents" は future work、dotfiles は実装済み） |
| セキュリティ制約に言及なし | protect-linter-config.py、golden-check.py、constraints-library.md (C-001〜C-010) |

### 改善機会

#### A. 統一されたサブエージェントインターフェース（優先度: 高）

- 3つの仕組みがバラバラ: Agent ツール（sync）、`claude -p`（async）、cron（scheduled）
- **対策**: `references/subagent-delegation-guide.md` — 選択基準 + フレーミングテンプレート

#### B. フレーミング指示の体系化（優先度: 高、Aに統合）

- Sync は「簡潔に、親が統合する」、Async は「詳細に、ユーザーへの最終回答」
- **対策**: 標準フレーミングテンプレートをガイドに含める

#### C. Async の「報告」メカニズム（優先度: 中）

- `/autonomous` の完了通知が未構造化（task_list.md の手動確認に依存）
- **対策**: タスク完了イベントの構造化、Notification hook 活用検討

#### D. 動的スケジューリング（優先度: 中）

- Scheduled が cron 固定、セッション内からの動的起動がない
- **対策**: CronCreate を活用した scheduled task スキル化

## 推奨アクション

| 優先度 | アクション | 根拠 |
|---|---|---|
| **高** | `references/subagent-delegation-guide.md` 作成 | 暗黙知の明文化。スキル/エージェント全体の一貫性向上 |
| **中** | `/autonomous` の完了通知イベント構造化 | Async パターンの「報告」部分の強化 |
| **中** | 動的スケジューリングのスキル化 | Scheduled パターンのセッション内対応 |
| **低** | エージェント数の統合検討 | 33→25 統合可能だが緊急性低 |
