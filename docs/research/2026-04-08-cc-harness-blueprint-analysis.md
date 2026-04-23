---
status: active
last_reviewed: 2026-04-23
---

# Claude Code Harness Blueprint 分析レポート

> 記事: "How I built harness for my agent using Claude Code leaks"
> 分析日: 2026-04-08
> ステータス: 統合完了（7項目取り込み）

## 記事概要

Claude Code の内部アーキテクチャ（55ディレクトリ、331モジュール）を分析し、エージェントハーネスの4層フレームワーク（Model Weights, Context, Harness, Infrastructure）を提唱。18の具体的手法を抽出。

### 主張
- 3層モデル（Weights/Context/Harness）は不十分。4層目の Infrastructure（マルチテナンシー、RBAC、リソース隔離、状態永続化、分散協調）が必要
- SWE-agent: インターフェース変更のみで64%改善（ただしGemini検証により複合効果の推定値の可能性）
- CC ソースはリーク（v2.1.88）であり公式公開ではない

## ギャップ分析結果

### 判定サマリ
- **exists (7)**: Tool Concurrency, Prompt Cache, CLAUDE.md Hierarchy, Sub-Agent Isolation, Worktree Isolation, Task Coordination, Extension Mechanisms — すべて強化不要
- **Partial (7)**: Micro-Loop規律, Context Injection Policy, Context Collapse, Progressive Trust, CC内部Retry/Budgeting, UI Trust原則 — 全7項目を取り込み
- **N/A (4)**: Async Generator, DI, Streaming Tool Executor, Layer 4 Infrastructure — CC内部実装または単一ユーザー設定にスコープ外

### Codex 批評の核心
「implementation inaccessible ≠ design principle inapplicable」
— CC内部で実装を触れないことと、設計原則として学べないことは別の主張。この指摘により N/A 6項目中2項目（Five-Phase Loop, Context Injection）を Partial に修正。

### Gemini 補完知見
- SWE-agent 64%は複合効果の推定値の可能性
- CC ソースはリーク版（v2.1.88）
- Context Rot, False Claims Rate 上昇 — いずれも既に resource-bounds.md に反映済み
- Hyperagents, PAI, AlphaLab, DGM-H — いずれも既に docs/plans/ に統合プラン存在

## 統合プラン（実行済み）

| # | 項目 | 対象ファイル | 変更内容 |
|---|------|------------|---------|
| 1 | マイクロループ規律 | workflow-guide.md | Agent Micro-Loop セクション追加 |
| 2 | コンテキスト注入ポリシー | context-constitution.md | P8: Task-Scoped Context Injection 追加 |
| 3 | Context Collapse | compact-instructions.md | 3種→4種に更新 |
| 4 | Progressive Trust | workflow-guide.md | Permission Progressive Trust 追加 |
| 5 | CC内部リトライ戦略 | resource-bounds.md | 参照情報セクション追加 |
| 6 | Tool Result Budgeting | resource-bounds.md | 参照情報セクション追加 |
| 7 | UI Trust原則 | workflow-guide.md | Visibility→Trust→Autonomy 追加 |

## 総評

記事の大部分は既存の CC アーキテクチャ分析（2026-04-01）と重複。新規知見は限定的だが、Codex の批評「N/A ≠ 学べない」により、CC 内部パターンを harness レベルの設計原則として抽出する価値を再認識。特にマイクロループ規律とコンテキスト注入ポリシーは実用的な追加。
