# Anthropic "Lessons from Building Claude Code: How We Use Skills" 分析レポート

**日付:** 2026-03-18
**ソース:** Anthropic 公式ブログ

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

## 7つのベストプラクティス

1. **Don't State the Obvious** — Claude が既に知っていることは書かない
2. **Build a Gotchas Section** — 「スキルの中で最も価値が高いコンテンツ」
3. **Use the File System & Progressive Disclosure** — スキルはフォルダ、ファイルシステム全体がコンテキストエンジニアリング
4. **Avoid Railroading Claude** — 情報は与えるが、状況に応じた柔軟性を持たせる
5. **The Description Field Is For the Model** — 要約ではなくトリガー条件
6. **Memory & Storing Data** — `${CLAUDE_PLUGIN_DATA}` でスキル内データ蓄積
7. **On Demand Hooks** — スキルが active な時のみ有効なフック

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
| Runbooks | **GAP → 解消** | 0 → 1 (hook-debugger) |
| Infrastructure Operations | GAP (dotfiles の性質上限定的) | 0 |

## 実装した改善

1. **On Demand Hooks** — review スキルに PreToolUse ガード追加（レビュー中の Edit/Write 防止）
2. **Gotchas** — 上位5スキル（webapp-testing, autonomous, research, codex-review, review）に追加
3. **Description 最適化** — 6スキル（edge-case-analysis, check-health, spike, eureka, continuous-learning, debate）にトリガー条件パターン追加
4. **スキル使用計測** — PreToolUse hook でスキル起動を JSONL にログ（AutoEvolve 連携）
5. **Progressive Disclosure** — 3スキル（edge-case-analysis, search-first, spike）に references/templates 追加
6. **Runbook** — hook-debugger スキル新規作成（カテゴリ GAP 解消）

## 今後の検討事項

- 他スキルへの Gotchas 追加の段階的拡大
- スキル使用ログに基づく退役判断の自動化（AutoEvolve 連携）
- Memory & Storing Data パターンの review/daily-report への適用
- On Demand Hooks の他スキルへの展開（/careful, /freeze パターン）
