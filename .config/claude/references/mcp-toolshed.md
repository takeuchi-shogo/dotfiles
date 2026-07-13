---
status: reference
last_reviewed: 2026-04-23
---

# MCP Toolshed - サーバーカタログ

利用可能な MCP サーバーの用途別分類と、プロジェクト種別ごとの推奨セット。

## 推奨上限

**同時有効化は 3 サーバーまで**（5 サーバーで約 55K tokens のオーバーヘッド → 3 サーバーで約 33K tokens）。
必要なサーバーのみ有効化し、不要になったら無効化する。

## カタログ

### Docs: context7

- **用途**: ライブラリの最新ドキュメント・コード例の取得
- **トークンコスト**: 低（クエリ単位）
- **利用シーン**: 外部ライブラリの API 確認、バージョン固有の仕様調査

### Docs: x-docs

- **用途**: X API 公式ドキュメントの検索・参照
- **トークンコスト**: 低（URL-based MCP、認証不要）
- **利用シーン**: X API v2 エンドポイント仕様、OAuth スコープ、レート制限の確認
- **URL**: `https://docs.x.com/mcp`
- **備考**: Claude / Codex 両方に定義。`enabledMcpjsonServers` で有効化済み

### API: xapi

- **用途**: X API の呼び出し（投稿検索、ユーザー lookup、ブックマーク、トレンド等）
- **トークンコスト**: 中（hosted MCP + xurl bridge）
- **利用シーン**: X 上のデータ取得、API 動作確認
- **セットアップ**:
  1. [X Developer Portal](https://developer.x.com/) で OAuth 2.0 有効な App を作成
  2. Redirect URI `http://localhost:8080/callback` を登録
  3. シェルに `CLIENT_ID` / `CLIENT_SECRET` を export（git 管理外）
  4. Claude: `enabledMcpjsonServers` に `"xapi"` を追加
  5. Codex: `.codex/config.toml` の `[mcp_servers.xapi]` で `enabled = true`
- **初回起動**: ブラウザ OAuth ログインあり。`startup_timeout_sec = 300` 推奨
- **公式**: <https://docs.x.com/tools/mcp>

### Browser: agent-browser CLI（MCP 不要）

- **用途**: ブラウザ操作、UI テスト、スクリーンショット取得、ネットワーク分析
- **トークンコスト**: 低（`snapshot -i -c` で ~28K tokens、MCP Tax なし）
- **利用シーン**: E2E テスト、UI バグ再現、Diff による状態変化検出、ネットワーク監視
- **備考**: Bash 経由で CLI 実行。MCP サーバー枠を消費しない

### Search: brave-search

- **用途**: Web 検索、ローカル検索
- **トークンコスト**: 低（検索結果サマリ）
- **利用シーン**: 技術調査、エラーメッセージの検索、最新情報の取得

### Design: figma

- **用途**: Figma デザインデータの取得、コンポーネント情報の抽出
- **トークンコスト**: 中（デザインノードのメタデータ）
- **セットアップ**: [Figma セクション](#figma-mcp-連携) を参照
- **利用シーン**: デザイン→コード変換、デザインシステム同期、UI 実装の仕様確認

### DB: 各種（将来拡張）

- **用途**: データベースへの読み取りクエリ
- **利用シーン**: スキーマ調査、データ確認

## プロジェクト種別ごとの推奨セット

| プロジェクト種別 | 推奨サーバー | 理由 |
|-----------------|-------------|------|
| Web App | context7, brave-search + agent-browser CLI | ドキュメント参照 + 調査 + UI テスト（CLI、MCP 枠不要） |
| CLI Tool | context7, brave-search | ドキュメント参照 + 調査 |
| Library | context7, brave-search | API 互換性確認 + 類似ライブラリ調査 |
| Mobile | context7, figma | ドキュメント参照 + デザイン連携 |

## MCP サーバー追加時のチェックリスト

### 設定ソースの切り分け

- `claude mcp add/remove` で管理する user/global scope の登録先は `~/.claude.json`。CLI 登録を消すときは `claude mcp remove <name>` を使い、repo の `.mcp.json` を編集して解決しようとしない
- project scope の MCP 定義は引き続き repo root の `.mcp.json` と `.config/claude/settings.json` `enabledMcpjsonServers` で管理する

新しい MCP サーバーを追加する前に確認:

- [ ] **必要性**: 既存ツール（Bash, Grep, WebFetch 等）で代替できないか
- [ ] **トークンコスト**: ツール定義だけで何 tokens 消費するか（目安: 1 サーバー ≈ 11K tokens）
- [ ] **セキュリティ**: 認証情報の管理方法、データ送信先の確認
- [ ] **同時有効数**: 追加後も 3 サーバー以内に収まるか
- [ ] **メンテナンス**: サーバーの更新頻度、破壊的変更のリスク

## Figma MCP 連携

### セットアップ

1. Figma Personal Access Token を取得:
   - Figma > Settings > Personal access tokens > Generate new token
2. 環境変数に設定:
   ```bash
   export FIGMA_ACCESS_TOKEN="your-token-here"
   ```
3. MCP サーバー設定に追加（`settings.json`）

### トークンコスト目安

- ファイル一覧取得: 低
- ノード詳細取得: 中（ノード数に比例）
- 画像エクスポート: 高（バイナリデータ）

### 利用シーン

- デザインファイルからコンポーネント構造を抽出してコード生成
- デザイントークン（色、フォント、スペーシング）の自動取得
- UI 実装とデザインの差分検出
