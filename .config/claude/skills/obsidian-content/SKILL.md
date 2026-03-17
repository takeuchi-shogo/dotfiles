---
name: obsidian-content
description: Obsidian Vault 全体のコンテキストを活用してコンテンツを生成する。ニュースレター、ブログ記事、ツイートスレッド等。ノートを検索し、ライティングスタイルに従って生成。
metadata:
  pattern: generator
---

# Obsidian Content Creator

Vault 全体のナレッジを活用して、ユーザーのライティングスタイルでコンテンツを生成する。

## 前提条件

- Claude Code が Obsidian Vault のルートで起動されていること
- CLAUDE.md が存在し、ライティングスタイルが定義されていること
- 04-Galaxy/ にパーマネントノートが存在すること

## 引数の解釈

引数なし → インタラクティブモード
引数あり → トピックとして解釈

例:
- `/obsidian-content 潜在意識についてのニュースレター`
- `/obsidian-content AIツールの比較ブログ記事`
- `/obsidian-content 朝のルーティンについてのツイートスレッド`

## 処理手順

### Step 1: トピックとフォーマットの確定

引数からトピックを抽出する。フォーマットが指定されていない場合は AskUserQuestion で聞く:

- ニュースレター
- ブログ記事
- ツイートスレッド
- 自由形式（フォーマット指定）

### Step 2: Vault スキャン（並列）

Agent ツールを **3つ並列** で起動し、関連コンテンツを収集:

**Agent 1** (subagent_type: Explore):
「04-Galaxy/ 内で [トピック] に関連するパーマネントノートを検索し、各ノートのタイトル・要約・ファイルパスをリストで返してください」

**Agent 2** (subagent_type: Explore):
「05-Literature/ 内で [トピック] に関連する文献ノートを検索し、ハイライトとソース情報をリストで返してください」

**Agent 3** (subagent_type: Explore):
「01-Projects/ と 03-Resources/ 内で [トピック] に関連する過去のコンテンツやアウトラインを検索し、ファイルパスと概要をリストで返してください」

### Step 3: コンテキスト統合

3つのエージェントの結果を統合し、最も関連性の高いノートを選定する:
- Galaxy ノート: 核となるアイデアの素材
- Literature ノート: 引用・事例の素材
- 過去コンテンツ: スタイル・構成の参考

選定したノートを Read で読み込む（最大10ファイル）。

### Step 4: コンテンツ生成

CLAUDE.md の Writing Style セクションに従って生成する。

**フォーマット別の構成**:

#### ニュースレター
```markdown
---
title: ""
subject_lines:
  - ""
  - ""
  - ""
preview_text: ""
tags: [type/newsletter, topic/xxx]
date: YYYY-MM-DD
---

# [タイトル]

[導入: フックとなる文]

## [セクション1]
...

## [セクション2]
...

## まとめ
...

---
参考ノート: [[ノート1]], [[ノート2]]
```

#### ブログ記事
```markdown
---
title: ""
description: ""
tags: [type/blog, topic/xxx]
date: YYYY-MM-DD
status: draft
---

# [タイトル]

## はじめに
...

## [本文セクション x N]
...

## まとめ
...

---
参考ノート: [[ノート1]], [[ノート2]]
```

#### ツイートスレッド
```markdown
---
tags: [type/tweet-thread, topic/xxx]
date: YYYY-MM-DD
---

1/ [フック]

2/ [本文]

...

N/ [まとめ + CTA]

---
参考ノート: [[ノート1]], [[ノート2]]
```

### Step 5: プレビューと保存

1. 生成したコンテンツをプレビュー表示
2. AskUserQuestion:「この内容で保存しますか？修正点はありますか？」
3. 修正がある場合は修正して再表示
4. 承認後、Write で適切なフォルダに保存:
   - ニュースレター → `01-Projects/newsletters/`
   - ブログ → `01-Projects/blog/`
   - ツイート → `01-Projects/tweets/`
   - その他 → `01-Projects/content/`
5. フォルダが存在しない場合は Bash で `mkdir -p` で作成

### Step 6: memory.md 更新

`.claude/memory.md` に以下を追記:
- 生成日時
- トピック
- フォーマット
- 使用したソースノート
- 保存先パス

## 品質チェック

生成前に以下を確認:
- CLAUDE.md の Writing Style に違反していないか
- ジェネリックなAI臭い表現を使っていないか
- ソースノートの内容を正確に反映しているか
- リンク切れがないか
