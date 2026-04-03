# Topic Taxonomy

`/compile-wiki` がレポートを分類するためのトピック体系。

## トピック一覧

| ID | トピック名 | 説明 | キーワード例 |
|----|-----------|------|-------------|
| `harness` | ハーネス設計 | エージェントハーネス、hook 体系、ポリシー実行 | harness, hook, policy, golden-check, completion-gate |
| `agent` | エージェント設計 | マルチエージェント、サブエージェント、協調パターン | agent, multi-agent, subagent, delegation, routing |
| `claude-code` | Claude Code | Claude Code 固有の機能、アーキテクチャ、プラグイン | claude-code, command, plugin, CLAUDE.md |
| `memory` | メモリ・コンテキスト | メモリシステム、コンテキスト最適化、知識管理 | memory, context, compaction, knowledge, recall |
| `skill` | スキル設計 | スキル作成、チェイニング、評価、ループ | skill, chaining, eval, loop, SKILL.md |
| `security` | セキュリティ | プロンプトインジェクション、検証、安全性 | security, injection, validation, OWASP, trust |
| `ml-rl` | 機械学習・強化学習 | RLHF、進化戦略、サンプリング、推論 | RL, RLHF, evolution, sampling, reasoning |
| `coding` | コーディング | 開発パターン、コードレビュー、品質管理 | coding, review, quality, TDD, refactor |
| `evaluation` | 評価・観測 | エージェント評価、モニタリング、ベンチマーク | eval, benchmark, observability, metrics |
| `tooling` | ツール・エコシステム | MCP、Obsidian、CI/CD、ターミナル、外部ツール連携 | mcp, obsidian, otel, cmux, ghostty, buf, ci, cd |
| `productivity` | 生産性 | ワークフロー最適化、ベストプラクティス | workflow, productivity, best-practice, guide |

## 分類ルール

1. 各レポートに **1-3 トピック** を割り当てる（主トピック1 + 副トピック0-2）
2. ファイル名のキーワードを第一判断基準とし、内容で補正する
3. 複数トピックに該当する場合、より具体的なトピックを主トピックとする
4. 新しいトピックが必要な場合はこのファイルに追記してから使用する
