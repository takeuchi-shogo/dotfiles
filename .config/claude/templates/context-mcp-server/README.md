# Project Context MCP Server Template

Codified Context 論文 (Vasilopoulos, 2026, arXiv:2602.20478v1) に基づくプロジェクト固有の知識検索サーバー。

## 5 Tools

| Tool | 用途 |
|------|------|
| `list_subsystems()` | 文書化されたサブシステム一覧 |
| `get_files_for_subsystem(key)` | 特定サブシステムの詳細 |
| `find_relevant_context(task)` | タスクに関連するドキュメント検索 |
| `search_context_documents(query)` | ドキュメント全文検索 |
| `suggest_agent(task)` | タスクに最適なエージェント推薦 |

## セットアップ

1. `/init-project` の L 規模セットアップで自動コピーされる
2. `KNOWLEDGE_DIRS` をプロジェクトのドキュメントディレクトリに合わせて編集
3. `.claude/settings.json` の `mcpServers` に登録

## 設計判断

- **Keyword matching** を採用（論文もこの方式）。Embedding-based retrieval は将来の改善項目
- **In-memory index** で起動時にスキャン。ファイル数 100 以下のプロジェクトでは十分
- **Advisory only** — 検索結果を返すだけで、エージェントの行動を強制しない
