# Project Context MCP Server Template

プロジェクト固有のコンテキストを Claude Code に提供する MCP サーバーのテンプレート。

## セットアップ

### 1. テンプレートをコピー

```bash
cp -r ~/.claude/references/mcp-server-template/ ./mcp-context/
cd mcp-context
```

### 2. SUBSYSTEMS を設定

`server.py` の `SUBSYSTEMS` と `AGENTS` を編集:

```python
SUBSYSTEMS = {
    "auth": {
        "paths": ["src/auth/", "src/middleware/auth.ts"],
        "description": "認証・認可",
        "key_files": ["src/auth/provider.ts", "src/auth/types.ts"],
    },
    "api": {
        "paths": ["src/api/", "src/routes/"],
        "description": "API エンドポイント",
        "key_files": ["src/api/router.ts"],
    },
}
```

### 3. インストール & 起動

```bash
pip install -e .
# or
pip install mcp[cli]
mcp run server.py
```

### 4. Claude Code に登録

`.mcp.json` に追加:

```json
{
  "mcpServers": {
    "project-context": {
      "command": "python3",
      "args": ["mcp-context/server.py"]
    }
  }
}
```

## 提供ツール

| ツール | 説明 |
|--------|------|
| `list_subsystems` | 設定済みサブシステム一覧 |
| `get_subsystem_overview` | サブシステムの概要・ファイル構成・最近の変更 |
| `get_key_file` | キーファイルの読み取り |
| `search_codebase` | コードベース検索（rg/grep） |
| `get_recent_changes` | 最近の git 変更 |
| `get_agent_info` | プロジェクト固有エージェント情報 |
| `check_context_drift` | ドキュメント更新漏れの検出 |

## カスタマイズ

- `SUBSYSTEMS`: プロジェクトのサブシステム定義。パス、説明、キーファイルを設定
- `AGENTS`: プロジェクト固有のエージェント定義
- `PROJECT_ROOT`: プロジェクトルートパス（デフォルトは server.py の親の親ディレクトリ）

## ファクトリーエージェントとの連携

`constitution-factory` や `agent-factory` がプロジェクトセットアップ時にこのテンプレートをコピーし、プロジェクトに合わせてカスタマイズする。
