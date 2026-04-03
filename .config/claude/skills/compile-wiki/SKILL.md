---
name: compile-wiki
description: >
  docs/research/ の分析レポート群を概念ベースの wiki にコンパイルする。
  レポート横断で概念を抽出・統合し、docs/wiki/concepts/ に記事を生成、INDEX.md を自動更新する。
  Karpathy "LLM Knowledge Bases" アプローチに基づくナレッジベースパイプライン。
  Triggers: 'wiki コンパイル', 'compile-wiki', 'ナレッジベース', 'knowledge base', '概念抽出', 'wiki 更新', 'wiki 生成'.
  Do NOT use for: 単一記事の要約（直接回答で十分）、外部記事の統合（use /absorb）、Obsidian ナレッジ管理（use /obsidian-knowledge）。
allowed-tools: Read, Write, Edit, Bash(ls:*), Bash(wc:*), Bash(git diff:*), Glob, Grep, Agent, AskUserQuestion
argument-hint: compile | update | index | lint
metadata:
  pattern: pipeline
---

# /compile-wiki — Research Wiki Compiler

docs/research/ の 130+ 分析レポートを概念ベースの wiki にコンパイルする。

## サブコマンド

| コマンド | 説明 |
|---------|------|
| `compile` (デフォルト) | 全件スキャン → 概念抽出 → 記事生成 → INDEX 生成 |
| `update` | git diff ベースの差分更新（変更/追加レポートのみ再処理） |
| `index` | INDEX.md のみ再生成（概念記事は触らない） |
| `lint` | wiki の品質チェック（矛盾・欠損・接続・鮮度） |

## Phase 1: Scan & Extract

### 1.1 レポート一覧取得

```
Glob: docs/research/*.md
```

全件をリスト化し、総数をユーザーに報告する。
(`*-analysis.md` だけでなく `*-deep-survey.md`, `*-investigation.md` 等も含む)

`update` サブコマンドの場合:
```bash
# docs/wiki/INDEX.md の Last compiled 日付を基準にする（なければ全件）
git log --since="$(grep 'Last compiled' docs/wiki/INDEX.md | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' || echo '2020-01-01')" --name-only --pretty=format: -- docs/research/*.md | sort -u
```
変更/追加されたレポートのみを対象とする。変更がなければ「更新対象なし」で終了。

### 1.2 メタデータ抽出

Explore エージェントを並列起動し、各レポートからメタデータを抽出する。
1エージェントあたり最大 30 ファイルをバッチ処理（130 ファイルなら 5 エージェント）。

各レポートから抽出する情報:
- **title**: レポートのタイトル（H1 or frontmatter の source）
- **date**: 分析日（ファイル名 or frontmatter）
- **status**: integrated / analyzed / planned（frontmatter、なければ "unknown"）
- **topics**: トピック分類 1-3 個（`references/topic-taxonomy.md` に従う）
- **key_concepts**: キー概念リスト（3-8 個、名詞句で統一）
- **one_line_summary**: 1行サマリ（50文字以内）

### 1.3 概念マップ構築

抽出結果を集約し、概念マップを構築する:
1. 全レポートの key_concepts をフラット化
2. 同義語・類似概念をグルーピング（例: "サブエージェント" と "sub-agent" は同一）
3. 各概念に関連レポートを紐付け
4. 概念リストをユーザーにプレビュー表示

**Checkpoint**: 概念リスト（名前 + 関連レポート数）をユーザーに提示し、承認を得る。
不要な概念の除外や追加があればここで調整する。

## Phase 2: Compile

### 2.1 概念記事生成

承認された概念リストに基づき、各概念の記事を生成する。

各概念について:
1. 関連レポートの該当セクションを Read で取得
2. `templates/concept-article.md` のテンプレートに従って記事を生成
3. `docs/wiki/concepts/{concept-slug}.md` に Write

記事の品質基準:
- 概要は 2-4 文で概念の本質を捉える
- 主要な知見は箇条書き 5-10 項目
- ソースへの相対パスリンクが正しい（`../../research/YYYY-MM-DD-slug-analysis.md`）
- 関連概念への標準 markdown リンク（`[概念名](concept-slug.md)`）

### 2.2 バックリンク挿入

全概念記事を走査し、相互参照を挿入する:
- 概念 A の記事内で概念 B に言及している場合、B の「関連概念」セクションに A へのリンクを追加
- リンクは標準 markdown: `[概念名](concept-slug.md) — 関連の説明`

## Phase 3: Index

### 3.1 INDEX.md 生成

`templates/wiki-index.md` に従って `docs/wiki/INDEX.md` を生成する:
- トピック別に概念記事をグルーピング
- 全レポートの一覧テーブル（日付、タイトル、トピック、関連概念リンク）
- 統計サマリ（レポート数、概念数、トピック数）

### 3.2 完了報告

生成結果をユーザーに報告:
- 生成された概念記事数
- トピック別の概念分布
- 新規 vs 更新（update サブコマンドの場合）

## `index` サブコマンド

Phase 3 のみを実行する。`docs/wiki/concepts/` 内の既存記事を走査して INDEX.md を再生成する。
概念記事の内容は変更しない。

## `lint` サブコマンド

`docs/wiki/concepts/*.md` を対象に 4 種類の品質チェックを実行し、レポートを出力する。
ファイルの書き換えは行わない（read-only）。

### Check 1: 矛盾検出

1. `Glob: docs/wiki/concepts/*.md` で全記事を取得する
2. 各記事から主張（断言文）をリスト化する
3. 同一トピックについて異なる記事が矛盾する主張をしていないか比較する
   - 例: 一方が「depth-1 が最適」と主張し、他方が「再帰的サブエージェントが必要」と主張する場合
4. 疑わしい矛盾を `file:section` 参照付きで列挙する

### Check 2: 欠損概念検出

1. 全記事本文を走査し、他の概念への言及（名詞句・専門用語）を収集する
2. `docs/wiki/concepts/` に対応する `{slug}.md` が存在しない概念をリストアップする
3. 3 記事以上で言及されているが記事が存在しない概念を「欠損候補」としてフラグする

### Check 3: 接続提案

1. 各記事のキーワード・トピックを抽出する
2. 記事ペアを比較し、共通キーワードが 2 つ以上あるにもかかわらず相互リンクがないペアを検出する
3. リンク追加を提案する（追加先の記事名と想定アンカーテキストを明示）

### Check 4: 鮮度チェック

1. 各記事の `Sources` セクションからリンク先レポートの日付（ファイル名プレフィックス `YYYY-MM-DD`）を収集する
2. 全ソースが現在日付から 30 日以上前の記事を「陳腐化候補」としてフラグする
3. `docs/research/` に同一トピックの新しいレポート（記事のソース日付より新しいもの）があれば、そのパスを添えて報告する

### 出力フォーマット

```
## Wiki Lint Report

### 矛盾検出
- [contradiction] {file-a}.md vs {file-b}.md — {主張Aの要約} ↔ {主張Bの要約}

### 欠損概念
- [missing] "{概念名}" — {N} 記事で言及、専用記事なし

### 接続提案
- [link] {file-a}.md ↔ {file-b}.md — {共通キーワードの説明}

### 鮮度チェック
- [stale] {file}.md — 最新ソース {YYYY-MM-DD}、関連新規レポート: {path}
```

各セクションに該当がない場合は `（問題なし）` と表示する。
レポート末尾に「チェック対象記事数・指摘総数」のサマリ行を付ける。

## Anti-Patterns

| NG | 理由 |
|----|------|
| 130 ファイルを1エージェントで処理 | トークン予算超過。必ずバッチ分割 |
| レポート本文をそのままコピー | 概念記事は複数レポートの統合。コピペは不可 |
| Obsidian wiki リンク `[[]]` を使用 | GitHub 表示で非対応。標準 markdown リンクを使う |
| 概念の粒度が細かすぎる | 1レポートにしか出ない概念は記事化しない（2+レポートで共有される概念のみ） |
| INDEX.md を手動編集 | 次回 compile/index で上書きされる |

## Gotchas

- 旧形式レポート（frontmatter なし）と新形式（YAML frontmatter あり）が混在する。両方をパースできるようにする
- ファイル名から日付を抽出する際は `YYYY-MM-DD` プレフィックスを使う
- `update` サブコマンドでは既存の概念記事を破壊せず、追記・更新のみ行う
- 概念スラッグは kebab-case で統一（例: `multi-agent-coordination`）
- バックリンク挿入は冪等であること。既に存在するリンクは重複追加しない。`compile`/`update` の繰り返し実行で同じリンクが増殖しないよう確認する
- `docs/research/` 内の非レポートファイル（README 等）が混入した場合、frontmatter やヘッダーがなければスキップする

## フィードバック連携

以下のスキルから wiki への自動フィードバックをサポートする:

### /research → wiki
`/research` 完了後、出力レポートが `docs/research/` に保存された場合:
- `/compile-wiki update` で差分更新を提案
- 新しい概念が既存記事に関連する場合、関連概念セクションへのリンク追加を提案

### /eureka → wiki
`/eureka` で発見記録が `breakthroughs/` に保存された場合:
- 関連する概念記事の「主要な知見」セクションへの追記を提案
- 該当する概念がない場合は新規概念候補としてフラグ

### セッション Q&A → wiki
セッション中に wiki にない重要知見が得られた場合:
- 「この知見を wiki に追加しますか？」と提案
- 承認されたら最も関連する概念記事に追記、または新規概念記事を生成
