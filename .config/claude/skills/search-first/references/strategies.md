# Search Strategies Guide

search-first スキルが参照する検索戦略ガイド。

## パッケージレジストリ検索

| 言語 | レジストリ | 検索コマンド |
|-----|----------|------------|
| TypeScript | npm | `npm search {keyword}` / npmjs.com |
| Python | PyPI | `pip search` (廃止) → pypi.org で検索 |
| Go | pkg.go.dev | `go list -m all` / pkg.go.dev |
| Rust | crates.io | `cargo search {keyword}` |

## 品質評価シグナル

| シグナル | 良い | 注意 |
|---------|-----|------|
| メンテナンス | 直近3ヶ月以内にリリース | 1年以上更新なし |
| 依存数 | 少ない（<10） | 依存ツリーが深い（>50） |
| ライセンス | MIT, Apache 2.0, BSD | GPL（伝播に注意）, SSPL |
| TypeScript | 型定義同梱 or @types あり | 型なし |
| テスト | CI バッジあり | テストなし |

## MCP サーバー検索

1. `settings.json` の `mcpServers` セクションを確認
2. MCP マーケットプレイスを WebSearch
3. GitHub で `mcp-server-{keyword}` を検索
