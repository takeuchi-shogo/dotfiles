---
name: digest
description: "Use when converting NotebookLM output text into structured Obsidian Literature Notes. Paste YouTube/article summaries and it auto-infers metadata, saves to 05-Literature/. Triggers: 'NotebookLM', '文献ノート', 'Literature Note', 'YouTube要約を保存', '記事をVaultに'. Do NOT use for: ナレッジ整理 (use obsidian-knowledge), コンテンツ生成 (use obsidian-content)."
metadata:
  pattern: generator
---

# Digest — NotebookLM → Literature Note

NotebookLM やその他のソースから得た要約テキストを、Obsidian の Literature Note に構造化して保存する。

## 前提条件

- Claude Code が Obsidian Vault のルートで起動されていること
- CLAUDE.md が存在し、Vault の構成が記述されていること
- `05-Literature/` フォルダが存在すること

## 引数の解釈

引数なし → インタラクティブモード（テキストの貼り付けを促す）
引数あり → そのテキストを NotebookLM 出力として処理

例:
- `/digest` — 対話的にテキスト入力を求める
- `/digest [貼り付けたテキスト]` — 貼り付けられたテキストを直接処理

## 処理手順

### Step 1: Vault 検出

1. カレントディレクトリの `CLAUDE.md` を Read で読み込む
2. Vault 構成（フォルダ構造、命名規則、タグシステム）を把握する
3. `CLAUDE.md` が見つからない場合は AskUserQuestion で Vault ルートのパスを聞く:
   「Obsidian Vault のルートパスを教えてください（CLAUDE.md が存在するディレクトリ）」

### Step 2: テキスト取得

引数がない場合は AskUserQuestion でテキストを求める:

「NotebookLM の出力テキストを貼り付けてください（YouTube 動画の要約、記事のサマリーなど）」

引数がある場合はそのテキストをソースとして使用する。

### Step 3: メタデータ自動推論

テキストの内容を分析して以下のメタデータを推論する:

| フィールド | 推論方法 |
|-----------|---------|
| **title** | テキスト冒頭のタイトル行、または主題から推論 |
| **author** | 著者名・チャンネル名・話者名を抽出 |
| **url** | テキスト中の URL を抽出（なければ空欄） |
| **source_type** | `video` / `article` / `book` / `podcast` をコンテキストから判定 |
| **language** | テキストの言語を判定（`ja` / `en` / `mixed`） |
| **topic_tags** | 内容から 1〜3 個のトピックタグを生成（`topic/xxx` 形式） |

推論できない項目は空欄のまま残し、Step 5 のプレビューでユーザーに確認する。

### Step 4: 構造化

テキストを以下の構造に変換する:

1. **ハイライト**: テキストの要点をバレットポイントに整理
   - 元テキストの情報を忠実に反映する
   - 冗長な表現を簡潔にまとめるが、意味は変えない
   - 1 ハイライトにつき 1〜2 文で簡潔に
2. **パーマネントノート候補**: ハイライトの中から、独立したパーマネントノートとして発展させられるアイデアをチェックボックス付きでリストアップ
   - 各候補に「なぜパーマネントノートにできそうか」の簡潔な理由を付記

### Step 5: プレビューと確認

生成した Literature Note 全文をプレビュー表示する。

次に AskUserQuestion で確認:

「この内容で保存しますか？修正点があれば教えてください（メタデータの修正、ハイライトの追加・削除など）」

- 修正が指示された場合は修正を反映して再度プレビュー
- 承認されたら Step 6 へ進む

### Step 6: 保存と関連ノート検索

1. ファイル名を生成: `lit-{author}-{title-slug}.md`
   - `author`: 著者名（ローマ字またはそのまま）
   - `title-slug`: タイトルをケバブケースに変換（日本語はそのまま短縮）
   - 例: `lit-tiago-forte-building-a-second-brain.md`
   - 例: `lit-中田敦彦-お金の大学.md`
2. Write で `05-Literature/` に保存
3. 保存後、Grep で `04-Galaxy/` と `05-Literature/` 内の関連ノートを検索:
   - トピックタグが一致するノート
   - タイトルやキーワードが関連するノート
4. 関連ノートが見つかった場合はリスト表示:
   ```
   ### 関連ノート
   - [[ノート名]] (04-Galaxy/) — 関連の理由
   - [[ノート名]] (05-Literature/) — 関連の理由
   ```

## 出力テンプレート

```markdown
---
created: "{YYYY-MM-DD}"
tags:
  - type/literature
  - "topic/{推論されたトピック1}"
  - "topic/{推論されたトピック2}"
source:
  title: "{推論されたタイトル}"
  author: "{推論された著者名}"
  url: "{抽出された URL}"
  type: video
---

# {タイトル}

## ハイライト

- ハイライト 1
- ハイライト 2
- ハイライト 3

## 自分の考え

<!-- 後で自分の考えを追記 -->

## パーマネントノート候補

- [ ] {アイデア 1} — パーマネントノートにできそうな概念
- [ ] {アイデア 2} — パーマネントノートにできそうな概念
```

## Templates

- `templates/literature-note-template.md` — Obsidian Literature Note テンプレート

## 使用例

### 例 1: YouTube 動画の要約

```
ユーザー: /digest
AI: NotebookLM の出力テキストを貼り付けてください。
ユーザー: (NotebookLM で生成した YouTube 動画の要約を貼り付け)
AI: (メタデータを推論してプレビュー表示)
    → title: "Building a Second Brain"
    → author: "Tiago Forte"
    → source_type: video
    → tags: topic/pkm, topic/productivity
    この内容で保存しますか？
ユーザー: OK
AI: 05-Literature/lit-tiago-forte-building-a-second-brain.md に保存しました。
    関連ノート:
    - [[20260101120000-zettelkasten-method]] (04-Galaxy/) — PKM 手法の比較
```

### 例 2: 記事の要約（引数付き）

```
ユーザー: /digest [NotebookLM で生成した記事要約テキスト...]
AI: (テキストを解析してメタデータを推論)
    → title: "How to Take Smart Notes"
    → author: "Sönke Ahrens"
    → source_type: article
    → tags: topic/zettelkasten, topic/writing
    この内容で保存しますか？
ユーザー: author を "ゼンケ・アーレンス" に修正して
AI: (修正を反映して再プレビュー)
ユーザー: OK
AI: 05-Literature/lit-ゼンケ・アーレンス-how-to-take-smart-notes.md に保存しました。
```

## Skill Assets

- メタデータ推論ルール: `references/metadata-inference.md`
- 文献ノートテンプレート: `templates/literature-note-template.md` (既存)
