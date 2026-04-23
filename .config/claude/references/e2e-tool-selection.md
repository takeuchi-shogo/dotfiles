---
status: reference
last_reviewed: 2026-04-23
---

# E2E テストツール選定ガイド

## 推奨ツール: agent-browser CLI

Rust ネイティブ実装。アクセシビリティツリー経由の ref 方式で堅牢なセレクタを提供。

```bash
npx agent-browser             # コールドスタートなし
```

## トークン効率比較

| ツール | 同一タスクのトークン消費 | 備考 |
|--------|------------------------|------|
| agent-browser `-i` | ~33,500 tokens | interactive のみ |
| agent-browser `-i -c` | ~28,000 tokens | **推奨**。`-i` 比 -16%（空要素除去） |

`-c`（compact）オプションで空の構造要素を除去し、トークン消費を削減。

## 用途別推奨

| 用途 | 推奨ツール | 理由 |
|------|-----------|------|
| UI テスト・バグ再現 | agent-browser | snapshot-first + ref 方式で堅牢 |
| 状態変化検出 | agent-browser | `diff snapshot` で変更を可視化 |
| ネットワーク分析 | agent-browser | `network requests --filter` でパターンマッチ |
| モバイル検証 | agent-browser | `-p ios` で iOS シミュレータ対応 |
| テストスイート生成 | agent-browser + test-engineer | snapshot から テストケースを生成 |
| CI 実行 | 生成済みテストファイル | MCP/CLI 不要 |

## 主要機能

| 機能 | コマンド例 |
|------|-----------|
| スナップショット | `agent-browser snapshot -i -c` |
| Diff | `agent-browser diff snapshot --baseline /tmp/before.txt` |
| ネットワーク監視 | `agent-browser network requests --filter <pattern>` |
| HAR エクスポート | `agent-browser network har /tmp/trace.har` |
| iOS シミュレータ | `agent-browser open <url> -p ios` |
| スクリーンショット | `agent-browser screenshot /tmp/shot.png --full` |

## 判断基準

- **長時間セッション**（コンパクション 2 回以上）→ CLI 推奨（MCP Tax 回避）
- **CI 実行** → 生成済みテストファイルを直接実行
- **複雑なバッチ自動化** → agent-browser の `--session` で並列セッション

## アクセシビリティツリー = ユニバーサルインターフェース

全ての E2E ツールの共通原則: アクセシビリティツリー経由で UI 操作。
- Web: agent-browser
- Mobile: mobile-mcp / XcodeBuild MCP
- Desktop: Terminator (Windows) / macos-ui-automation-mcp (macOS)
- CLI: stdout/stderr (bats-core / pexpect)

## API/バックエンド E2E: Hurl

プレーンテキスト形式の HTTP テストツール。エージェントが読み書きしやすい。

```hurl
POST http://localhost:3000/api/users
Content-Type: application/json
{
  "name": "Test User",
  "email": "test@example.com"
}
HTTP 201
[Asserts]
jsonpath "$.id" exists
```

| 特徴 | 詳細 |
|------|------|
| 形式 | プレーンテキスト（Rust バイナリ、libcurl ベース） |
| CI 統合 | ネイティブ対応、JUnit XML 出力 |
| 変数 | `--variable` でリクエスト間の状態引き継ぎ |
| 推奨用途 | REST API のスモークテスト、契約テスト |
