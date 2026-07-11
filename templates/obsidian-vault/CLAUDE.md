# Obsidian Vault — AI Second Brain

## Identity

<!-- ここにあなたの情報を記入（/obsidian-vault-setup スキルで自動カスタマイズ可能） -->
- 名前: takeuchishougo
- 役割: ソフトウェアエンジニア
- 関心分野: AI エージェント設計、Claude Code ハーネスエンジニアリング、Go、開発者生産性

## Vault Architecture

このVaultは IPARAG + Zettelkasten メソッドで構成されている。

### Design Rationale (IPARAG vs One-Folder)

flat 単一フォルダ設計 (例: cyrilXBT "One-Folder Life System") を採用しない根拠:

- **Filing decision は `00-Inbox` で既に遅延化されている** — capture 時の filing 判断コストは Inbox 集約で解消済。flat 化はこのコストを「naming convention 設計コスト」に置換するだけで根本解決にならない
- **PARA は actionability-based の意味分割** — Projects (期限あり) / Areas (継続) / Resources (参照) / Archive (非アクティブ) は属性ではなく **責務** の境界。flat 化すると status property だけで擬似復元することになり、純粋な意味劣化
- **Galaxy (Zettelkasten) は独立 namespace が必須** — atomic note 同士の dense linking は他層から隔離されている方が wikilink graph の信頼性が高い。flat 化すると daily/literature/project ノートと混在し graph が雑音化
- **chronological + type filtering は frontmatter + Dataview で代替済** — flat の主目的（日付ソート + type filter）は `06-Archive` 以外の各フォルダ内で `type`/`date`/`status` property + Dataview クエリにより実現可能 (Obsidian Bases が GA 化した時点で Bases への移行を検討する)
- **大規模 vault でのファイルシステム特性** — 単一フォルダに大量ファイルを置くと OS のディレクトリ走査と Obsidian indexer のパス解決コストが O(N) で増加する。IPARAG の階層は OS / Obsidian indexer 双方の境界フィルタを活用できる (具体的な閾値は環境依存で未計測)

→ 現時点の設計判断では flat への移行は意味的・性能的に劣化を招く。将来 Obsidian Bases の GA・Zettelkasten 手法の変化・新しい indexer 実装などの **前提変化があった場合は本セクションの各論拠を個別に再検証する**。前提が同じなら再審不要。

| フォルダ | 目的 |
|---------|------|
| 00-Inbox | 未整理ノートの一時置き場。キャプチャしたらここに入れる。capture と棚卸し対象レポート専用 — daily note は置かない (07-Daily へ) |
| 01-Projects | アクティブなプロジェクト。完了期限があるもの |
| 02-Areas | 継続的に管理する領域。健康、財務、キャリア等 |
| 03-Resources | リファレンス・参考資料。いつか使うかもしれない情報 |
| 04-Galaxy | Zettelkasten パーマネントノート。自分の言葉で書いた知識の原子 |
| 05-Literature | 読書・動画・記事のノート。ソースからの抽出 |
| 06-Archive | 完了・非アクティブ項目 |
| 07-Daily | 統合 daily note。morning briefing (自動生成)・timekeeper の plan/review が `YYYY-MM-DD.md` に、日報が `YYYY-MM-DD-report.md` に集約される |
| 08-Agent-Memory | Claude Code の memory が自動同期される。エージェントの蓄積知識 |

## Naming Conventions

- パーマネントノート: `YYYYMMDDHHMMSS-kebab-case-title.md`
- 文献ノート: `lit-著者名-タイトル略称.md`
- プロジェクトノート: `proj-プロジェクト名/YYYY-MM-DD-topic.md`
- タグ: `#category/subcategory` 形式

## Tagging System

- `#status/seed` — アイデア段階
- `#status/growing` — 発展中
- `#status/evergreen` — 成熟したノート
- `#type/permanent` — パーマネントノート
- `#type/literature` — 文献ノート
- `#type/project` — プロジェクトノート
- `#type/moc` — Map of Content（テーマ別索引）
- `#topic/xxx` — トピック別タグ

## Linking Rules

- パーマネントノートは最低1つの既存ノートにリンクする
- `[[ノート名]]` でリンク。エイリアスは `[[ノート名|表示名]]`
- リンクの理由を簡潔に書く（なぜ関連するか）
- 孤立ノートは定期的にリンク候補を探す

## Writing Style

<!-- ここにあなたのスタイルを記入 -->
- トーン: MIXED
- 言語: ja
- 禁止: ジェネリックなAI臭い表現、曖昧な結論

## Active Projects

<!-- Claudeが自動更新する -->
- (まだプロジェクトなし)
