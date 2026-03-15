# E2E テストツール選定ガイド

Ref: Harness Engineering Best Practices 2026 (逆瀬川)

## トークン効率比較

| ツール | 同一タスクのトークン消費 | 効率倍率 |
|--------|------------------------|----------|
| Playwright MCP | ~114,000 tokens | 1x (基準) |
| Playwright CLI | ~27,000 tokens | **4x** |
| agent-browser | ~5,500 chars | **5.7x** |

## 用途別推奨

| 用途 | 推奨ツール | 理由 |
|------|-----------|------|
| セルフテストループ | Playwright CLI or agent-browser | トークン効率が決定的に重要 |
| テストスイート生成 | Playwright MCP (サブエージェント) | Planner/Generator/Healer 構成 |
| 探索的テスト | agent-browser | ref 方式でセレクタの壊れにくさ |
| 長時間セッション | Playwright CLI | MCP Tax の累積を回避 |

## Playwright CLI の使い方

MCP ツールではなく Bash 経由で Playwright を直接操作:
```bash
npx playwright test           # テスト実行
npx playwright codegen <url>  # テストコード生成
npx playwright show-trace     # トレース表示
```

## agent-browser (Vercel Labs)

```bash
npx agent-browser             # Rust CLI、コールドスタートなし
```
- ref 方式でセレクタを参照（CSS/XPath より堅牢）
- 2026年1月リリース、まだ荒い部分あり

## 判断基準

- **MCP Tool Search でオンデマンドロード**している場合は MCP Tax 緩和済み
- **長時間セッション**（コンパクション2回以上）なら CLI 推奨
- **テスト生成**目的なら MCP の Planner/Generator が有利
- **CI 実行**には生成済みテストファイルを直接実行（MCP 不要）

## アクセシビリティツリー = ユニバーサルインターフェース

全てのE2Eツールの共通原則: アクセシビリティツリー経由でUI操作。
- Web: Playwright / agent-browser
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
