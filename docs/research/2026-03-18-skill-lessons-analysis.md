---
status: active
last_reviewed: 2026-04-23
---

# Anthropic "Lessons from Building Claude Code: How We Use Skills" 分析レポート

**日付:** 2026-03-18
**ソース:** Anthropic 公式ブログ
**ステータス:** V2 統合完了

## 記事の9スキルカテゴリ

1. Library & API Reference — 内部/外部ライブラリの正しい使い方
2. Product Verification — コードの正しさを検証する手段
3. Data Fetching & Analysis — データ・モニタリングスタック接続
4. Business Process & Team Automation — 反復ワークフローの自動化
5. Code Scaffolding & Templates — フレームワークボイラープレート生成
6. Code Quality & Review — コード品質とレビュー強制
7. CI/CD & Deployment — フェッチ・プッシュ・デプロイ
8. Runbooks — 症状→調査→レポートの構造化手順
9. Infrastructure Operations — ルーチンメンテナンスとオペレーション

## 9つのベストプラクティス

1. **Don't State the Obvious** — Claude が既に知っていることは書かない
2. **Build a Gotchas Section** — 「スキルの中で最も価値が高いコンテンツ」
3. **Use the File System & Progressive Disclosure** — スキルはフォルダ、ファイルシステム全体がコンテキストエンジニアリング
4. **Avoid Railroading Claude** — 情報は与えるが、状況に応じた柔軟性を持たせる
5. **Think through the Setup (config.json)** — ユーザー固有設定を config.json に保存し、初回セットアップを案内
6. **The Description Field Is For the Model** — 要約ではなくトリガー条件
7. **Memory & Storing Data** — `${CLAUDE_PLUGIN_DATA}` や安定フォルダでスキル内データ蓄積
8. **Store Scripts & Generate Code** — コンポーザブルなスクリプト/テンプレートでClaude のターンを構成に集中
9. **On Demand Hooks** — スキルが active な時のみ有効なフック

## dotfiles との照合結果

| カテゴリ | 充足度 | 該当スキル数 |
|---------|--------|------------|
| Library & API Reference | 充実 | 6 |
| Product Verification | 充実 | 3 |
| Data Fetching & Analysis | 中程度 | 3 |
| Business Process & Team Automation | 充実 | 5 |
| Code Scaffolding & Templates | 中程度 | 3 |
| Code Quality & Review | 非常に充実 | 5 |
| CI/CD & Deployment | 中程度 | 2 |
| Runbooks | 解消済み | 1 (hook-debugger) |
| Infrastructure Operations | N/A (dotfiles の性質上限定的) | 0 |

## V1 実装改善 (初回統合)

1. **On Demand Hooks** — review スキルに PreToolUse ガード追加（レビュー中の Edit/Write 防止）
2. **Gotchas** — 上位5スキル（webapp-testing, autonomous, research, codex-review, review）に追加
3. **Description 最適化** — 6スキル（edge-case-analysis, check-health, spike, eureka, continuous-learning, debate）にトリガー条件パターン追加
4. **スキル使用計測** — PreToolUse hook でスキル起動を JSONL にログ（AutoEvolve 連携）
5. **Progressive Disclosure** — 3スキル（edge-case-analysis, search-first, spike）に references/templates 追加
6. **Runbook** — hook-debugger スキル新規作成（カテゴリ GAP 解消）

## V2 実装改善 (再分析・デルタ統合)

V1 で未分析だった2件 (Think through the Setup, Store Scripts & Generate Code) と未実施の検討事項を対応。

### Task 1: Description 最適化 (残り6スキル)

summary-focused → trigger-focused に修正:
- obsidian-content, ui-ux-pro-max, obsidian-vault-setup, obsidian-knowledge, dev-insights, digest
- パターン: "Use when {trigger}. Triggers: '...'. Do NOT use for: {混同スキル}."

### Task 2: Gotchas セクション拡大 (10スキル)

新規追加:
- codex (5件), gemini (5件), skill-creator (5件), github-pr (5件)
- senior-architect (5件), senior-backend (5件), senior-frontend (5件)
- dev-ops-setup (4件), skill-audit (4件), obsidian-vault-setup (4件)
- **累計 Gotchas 対応スキル: 35/54**

### Task 3: On Demand Hooks 展開 (新規2スキル)

- `/careful` — 全 Bash コマンドに確認プロンプト。本番操作時の安全装置
- `/freeze` — Edit/Write に確認プロンプト。デバッグ時の不要修正防止
- **累計 On Demand Hooks スキル: 3 (review, careful, freeze)**

### Task 4: Templates 追加 (5スキル, 6ファイル)

Store Scripts & Generate Code パターンの適用:
- spec: `templates/prompt-as-prd-template.md`
- timekeeper: `templates/daily-plan-template.md`, `templates/evening-review-template.md`
- daily-report: `templates/daily-report-template.md`
- digest: `templates/literature-note-template.md`
- research: `templates/research-report-template.md`

### Task 5: Memory & Storing Data パターン (3スキル)

`~/.claude/skill-data/{skill-name}/` に append-only JSONL で蓄積:
- daily-report: `history.jsonl` (日報メタデータ, 前日比差分)
- review: `reviews.jsonl` (レビュー結果, AutoEvolve 連携)
- timekeeper: `sessions.jsonl` (計画/振り返り履歴, 完了率追跡)

## ベストプラクティス適合状況 (V2 完了後)

| # | ベストプラクティス | V1 | V2 | 現状 |
|---|-------------------|----|----|------|
| 1 | Don't State the Obvious | ✅ | — | 対応済み |
| 2 | Build a Gotchas Section | 5スキル | +10スキル | 35/54 スキル対応 |
| 3 | Progressive Disclosure | 3スキル | +5スキル(templates) | フォルダ活用率 56% |
| 4 | Avoid Railroading Claude | ✅ | — | 対応済み |
| 5 | Think through the Setup | 未分析 | 分析済み | N/A (CLAUDE_PLUGIN_DATA 未提供) |
| 6 | Description = Trigger | 6スキル | +6スキル | 30/54 → 対応率向上 |
| 7 | Memory & Storing Data | 未実施 | 3スキル導入 | `~/.claude/skill-data/` 規約確立 |
| 8 | Store Scripts & Generate Code | 未分析 | 6テンプレート追加 | templates 活用率向上 |
| 9 | On Demand Hooks | 1スキル | +2スキル | 3スキル (review, careful, freeze) |

## 今後の検討事項

- Gotchas 未対応の残り19スキルへの段階的追加
- CLAUDE_PLUGIN_DATA が利用可能になった場合の skill-data 規約の移行
- config.json セットアップパターンの具体的適用（CLAUDE_PLUGIN_DATA 前提）
- スキル使用ログに基づく退役判断の自動化（AutoEvolve 連携）
