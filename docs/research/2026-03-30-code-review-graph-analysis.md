---
source: https://github.com/tirth8205/code-review-graph
date: 2026-03-30
status: integrated
---

## Source Summary

**主張**: Claude Code はタスクごとにコードベース全体を再読込しトークンを浪費している。Tree-sitter で構造グラフを構築し、変更の blast radius のみを読ませることで平均 8.2x のトークン削減を実現。

**手法**:
1. Tree-sitter AST → SQLite グラフ（ノード=関数/クラス/import、エッジ=呼び出し/継承/テスト）
2. Blast radius 分析（変更→依存→呼び出し元→テストの逆引き、recall 100%）
3. インクリメンタル更新（SHA-256 ハッシュ、2,900 ファイルで < 2秒）
4. MCP サーバー経由で 21 ツール提供（impact radius, review context, query graph, semantic search, community detection, flow tracing, refactoring）
5. Risk-scored change detection（diff→関数マッピング→セキュリティキーワード→リスクスコア）
6. Community detection（Leiden algorithm）+ アーキテクチャ概要自動生成
7. Execution flow tracing（エントリポイント→呼び出しチェーン、criticality ソート）
8. Session hints（ツール呼び出し履歴→インテント推論→次アクション提案）
9. MCP Prompts（5 ワークフロー: review, architecture, debug, onboard, pre-merge）
10. Auto-update hooks（PostToolUse/SessionStart/PreCommit）

**根拠**: 6 リポジトリ・13 コミットでベンチマーク。express 以外で大幅トークン削減。

**前提条件**: Python 3.10+, uv, Tree-sitter 対応言語, MCP 対応ツール

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Tree-sitter AST → SQLite 構造グラフ | Gap | cross-file-reviewer は Grep でアドホック検索、永続グラフなし |
| 2 | Blast radius 自動算出 | Partial | cross-file-reviewer PRE_ANALYSIS が手動 Grep で実施、グラフベースではない |
| 3 | インクリメンタル更新 | Gap | 毎セッションでゼロから Grep 検索 |
| 4 | MCP ツール（21 tools） | Gap | 構造グラフ系 MCP ツールなし |
| 5 | Risk-scored change detection | Partial | /review が変更規模で判断、関数レベルリスクスコアなし |
| 6 | Community detection | Gap | 未実装 |
| 7 | Execution flow tracing | Gap | Grep ベースの callers/callees のみ |
| 8 | Session hints | N/A | hook + skill で workflow 制御、MCP ヒント方式は設計思想が異なる |
| 9 | Auto-update hooks | N/A | 既存 hook 体系と衝突リスク |
| 10 | MCP Prompts | N/A | /review, /audit, debugging スキルでカバー済み |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|-------------|---------------|--------|
| A1 | cross-file-reviewer の Grep blast radius | 間接依存（A→B→C）を見落とす | CRG の get_impact_radius で depth=2+ の間接依存を補完 |
| A2 | /review の変更規模ベース判断 | ファイル数/行数だけではリスク不十分 | detect_changes の risk score を review 判断材料に追加 |

## Integration Decisions

- Gap #1-7: 全て取り込み（code-review-graph パッケージのインストール + MCP 設定で一括解決）
- Already A1-A2: 全て取り込み（cross-file-reviewer + review スキルの改修）
- N/A #8-10: スキップ（既存 hook/skill 体系との衝突回避）

## Plan

| # | タスク | 対象 | 規模 |
|---|--------|------|------|
| T1 | code-review-graph インストール設定 | Brewfile / setup script | S |
| T2 | MCP サーバー設定追加 | settings.json | S |
| T3 | cross-file-reviewer CRG 統合 | agents/cross-file-reviewer.md | S |
| T4 | review スキル risk score 統合 | skills/review/ | S |
| T5 | CRG リファレンス作成 | references/code-review-graph-guide.md | M |
| T6 | 分析レポート + MEMORY.md | docs/research/, memory | S |
