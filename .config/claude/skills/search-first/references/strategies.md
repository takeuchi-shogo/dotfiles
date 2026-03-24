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

## コミュニティパルス検索

ライブラリ選定や技術判断の前に、コミュニティの最新動向を確認する。トレーニングデータは数ヶ月遅れるため、リアルタイムの評判・問題報告・移行トレンドを WebSearch で収集する。

| ソース | 検索クエリ例 | 狙い |
|--------|-------------|------|
| Reddit | `site:reddit.com {keyword} after:2026-01` | 実ユーザーの評判・問題報告 |
| Hacker News | `site:news.ycombinator.com {keyword}` | 技術コミュニティの評価・議論 |
| X (Twitter) | `{keyword} lang:en since:2026-01-01` | リアルタイムのバズ・著名開発者の意見 |
| YouTube | `site:youtube.com {keyword} 2026` | チュートリアル・比較動画の有無 |

### いつ使うか

- 2つ以上のライブラリ/ツールの選定で迷っているとき
- 新しいフレームワーク・パターンの採用を検討するとき
- 「X はまだ使われているか？」「Y の評判は？」という判断が必要なとき

### フロー

1. 上記ソースから並列で WebSearch（`/research` スキルとの組み合わせ推奨）
2. コミュニティの **コンセンサス**（支持率）と **懸念点**（頻出する不満）を抽出
3. 結果をプラン作成時のコンテキストとして渡す

## Multi-Source Ranking (RRF)

複数の検索ソース（Grep, Glob, Obsidian MCP, WebSearch）から結果を取得した後、Reciprocal Rank Fusion (RRF) で統合ランキングする。

### RRF 式

```
RRF_score(d) = Σ 1/(k + rank_i(d))
```

- `d`: ドキュメント（ファイル/ノート/検索結果）
- `rank_i(d)`: ソース i における d の順位（1-indexed）
- `k`: 定数 = 60（高ランクと低ランクの差を平滑化）
- ソース i に d が含まれない場合、そのソースの項は 0

### 手順

1. 各ソースで独立に検索を実行し、結果をランク付け
2. 全結果の和集合に対して RRF_score を計算
3. RRF_score 降順でソートし、上位 N 件を採用

### 計算例

ファイル X が Grep で 1位、WebSearch で 3位の場合:
```
RRF_score(X) = 1/(60+1) + 1/(60+3) = 0.0164 + 0.0159 = 0.0323
```

### いつ使うか

- 3つ以上の検索ソースを並列に使った場合
- 各ソースの上位結果が大きく異なる場合（統合ランキングの価値が高い）
- 2ソース以下ではオーバーキル（目視で十分）
