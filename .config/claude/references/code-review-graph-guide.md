---
status: reference
last_reviewed: 2026-04-23
---

# code-review-graph MCP ガイド

Tree-sitter ベースの構造グラフを MCP 経由で提供するツール。
コードベースの関数・クラス・import をノード、呼び出し・継承・テストをエッジとして SQLite に永続化し、
変更の blast radius を自動算出する。

## セットアップ

各プロジェクトで初回のみ:

```bash
code-review-graph build    # コードベース全体をパース（500ファイルで ~10秒）
```

以降は `build_or_update_graph_tool` で差分更新（< 2秒）。

## 主要 MCP ツール

### レビュー系（/review から使用）

| ツール | 用途 |
|--------|------|
| `detect_changes_tool` | git diff → 関数マッピング → risk score 算出。review スキルの Impact Pre-scan で使用 |
| `get_impact_radius_tool` | blast radius 算出（depth=2 で間接依存込み）。cross-file-reviewer で使用 |
| `get_review_context_tool` | トークン最適化されたレビューコンテキスト生成 |
| `get_affected_flows_tool` | 変更が影響する実行フローを特定 |

### 探索系

| ツール | 用途 |
|--------|------|
| `query_graph_tool` | callers_of, callees_of, tests_for, imports_of 等のグラフクエリ |
| `semantic_search_nodes_tool` | 関数・クラスのセマンティック検索 |
| `list_flows_tool` / `get_flow_tool` | エントリポイントからの実行フロー追跡 |
| `list_communities_tool` / `get_community_tool` | コードクラスタリング（Leiden algorithm） |
| `get_architecture_overview_tool` | コミュニティ構造からアーキテクチャ概要生成 |

### リファクタリング系

| ツール | 用途 |
|--------|------|
| `refactor_tool` | rename プレビュー、dead code 検出、リファクタリング提案 |
| `find_large_functions_tool` | 行数閾値超えの関数検出 |

## 既存ワークフローとの統合

### /review スキル

Step 1.3 Impact Pre-scan で `detect_changes_tool` + `get_impact_radius_tool` を優先使用。
MCP 未接続時は従来の Grep フォールバック。

### cross-file-reviewer エージェント

PRE_ANALYSIS モードで `get_impact_radius_tool` (depth=2) を使い、間接依存（A→B→C）を検出。
DETECT モードのレビュー手順でも blast radius 情報を活用。

## 注意事項

- グラフは**プロジェクト単位**で `.code-review-graph/` に SQLite として保存される
- auto-update hooks は使わない（既存 hook 体系との衝突回避）。必要時にツール経由で更新
- 18言語対応: Python, TypeScript/TSX, JavaScript, Vue, Go, Rust, Java, Scala, C#, Ruby, Kotlin, Swift, PHP, Solidity, C/C++, Dart, R, Perl
- Impact 分析は conservative（recall 100%, precision ~38%）。over-predict する設計
