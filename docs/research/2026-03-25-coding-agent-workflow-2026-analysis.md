---
source: https://nyosegawa.com/posts/coding-agent-workflow-2026/
author: 逆瀬川ちゃん (@gyakuse)
date: 2026-03-25
published: 2026-03-14
status: integrated
---

## Source Summary

Coding Agent 時代の開発ワークフローを包括的にまとめた記事（31分読了）。Agentic Engineering の潮流から、4つのワークフロー（Harper Reed式/SDD/RPI/Superpowers）、品質テクニック（Context Engineering, TDD, マルチエージェント, Best-of-N）、インフラ（CLAUDE.md設計, Skills, Hooks, Worktree, Ralph Loop）、著者の実践（アイデアドリブン開発, 8時間自動ラン）までを体系化。

**主張**: 2026年の開発は3層（プロジェクトワークフロー / 実装テクニック / インフラ）で設計し、フィードバックループを決定論的に閉じ、人間は構造化されたポイントで介入する。

**手法** (主要20項目):
1. 4 Workflows: Harper Reed式 Brainstorm→Plan→Execute / SDD(Spec-Driven) / RPI(Research→Plan→Implement) / Superpowers(方法論エンコーディング)
2. Context Engineering: Context Packing, Progressive Disclosure, ファイルシステム外部メモリ, Todo注意管理, 失敗状態保持
3. Context Rot対策: セッション短縮, Subagent活用, compact, 不要ファイル回避, 1Mコンテキスト活用
4. TDD × Coding Agent: Red-Green-Refactor + tdd-guard hookによる順序強制
5. マルチエージェント分業: Orchestrator + 専門Agent + API境界事前合意
6. Best-of-N並列戦略: N並列worktree→結果比較→最良選択/合成
7. AI on AI Review: モデルミュージカルチェア, クロスレビュー, レイヤー分離
8. 失敗モード: ハルシネーション, 無限ループ, 過剰生成, 偽完了, Agent Drift, 確率的カスケード, Comprehension Debt
9. Agent-Nativeコード設計: Grep-able命名, collocated tests, 機能単位モジュール化, テスト=報酬信号, API境界明確化
10. CLAUDE.md/AGENTS.md設計: Progressive Disclosure, 60-150行, Vercel 8KB=100%パス率
11. Skills 3段階ローディング: L1メタデータ(100tok) / L2指示書(<5000tok) / L3リソース(無制限)
12. Hooks/Linter: PostToolUse自動実行, Factory.ai 7カテゴリlint, Nick Tuneドメインイベント
13. Git Worktree並列実行
14. MCP vs CLI: Coding AgentではCLI+Skillsが最適解
15. Ralph Loop + 長時間セッション設計
16. GitHub Agentic Workflows: Continuous Triage/Documentation/Test/Quality
17. セキュリティ: OWASP Top 10, 権限最小化, MCPサプライチェーン
18. Symphony: Issue駆動の自律オーケストレーション
19. 著者のワークフロー: アイデアドリブン開発, Patrol Agent巡回, 8時間自動ラン
20. Lefthook pre-commitガード: AGENTS.md行数, パス実在, docs鮮度

**根拠**: Anthropic Cコンパイラ事例(16並列/10万行), HumanLayer 300k LOC Rust(1日で1週間分), Vercel Next.js 16 実証(8KB AGENTS.md=100%パス率), Best-of-N成功確率(4並列で68%, 8並列で90%)

**前提条件**: Claude Code / Codex / Cursor等のコーディングエージェント利用環境。決定論的テスト・Linter・CIが整備されていること。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | TDD Guard hook (テスト→実装順序の強制) | Partial | completion-gate.py は事後テスト実行のみ。superpowers:tdd スキルは存在するが hook 強制なし |
| 2 | Agent-Native コード設計ガイドライン (5原則統合) | Partial | 原則が code-reviewer, workflow-guide に散在。統合参照ドキュメントなし |
| 3 | Lefthook pre-commit ガード拡張 (行数/パス/鮮度) | Partial | format/lint/commit-msg 実装済み。3ガード未実装 |
| 4 | GitHub Agentic Workflows (CI/CDエージェント連携) | Gap | .github/ なし。/dev-cycle で Issue起点フローはあるが CI/CD 連携なし |
| 5 | Best-of-N 実行時自動化 (並列→比較→選択) | Partial | プランニング段階のみ (workflow-guide §1.0)。実行時自動比較ツールなし |
| 6 | Patrol Agent + 通知集約 (セッション巡回→一括通知) | Gap | /schedule で cron は可能。巡回・停止検出・通知集約なし |
| 7 | Linear Walkthrough 自動生成 | Partial | comprehension-debt-policy.md で Design Rationale 必須。自動 Walkthrough 生成なし |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す知見 | 強化案 |
|---|-------------|---------------|--------|
| A1 | Context Rot対策 (resource-bounds.md) | 1M コンテキスト対応で余裕拡大 | resource-bounds.md を 1M 対応に再校正 |
| A2 | Hooks/Linter (PostToolUse, lefthook) | Factory.ai 7カテゴリlint体系 | 既存ルールを7カテゴリで再分類、欠落補強 |
| A3 | 失敗モード (failure-taxonomy FM-001〜019) | 確率的カスケード定量モデル | FM-020 Probabilistic Cascade 追加 |
| A4 | マルチエージェント (subagent-delegation-guide) | 共有ファイル=並列の前提条件 | 共有ファイル検出→直列化ルール追加 |
| A5 | CLAUDE.md設計 (compact-instructions.md) | Vercel 8KB=100%パス率実証 | 実証データを根拠として追記 |
| A6 | セキュリティ (mcp-audit.py) | MCPサプライチェーン攻撃リスク | 未知MCPの初回利用時警告追加 |
| A7 | AI on AI Review (stagnation-detector.py) | モデルミュージカルチェア | エラー反復→自動モデル切替提案の明示化 |

## Integration Decisions

全 14 項目を取り込み。3フェーズに分割して実行。

## Plan

`docs/plans/2026-03-25-coding-agent-workflow-integration.md` 参照
