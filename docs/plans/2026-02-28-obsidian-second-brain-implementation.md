---
status: active
last_reviewed: 2026-04-23
---

# Obsidian AI第二の脳 — 実装計画

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** dotfilesにObsidian Vault テンプレートと3つのClaude Codeスキルを追加し、「AI第二の脳」ワークフローを実現する

**Architecture:** dotfiles/.config/claude/skills/ に3つのスキル（SKILL.md形式）を配置。templates/obsidian-vault/ にVaultテンプレートを配置。既存のsymlink構成で自動的に ~/.claude/skills/ に反映される。

**Tech Stack:** Claude Code Skills (Markdown), Obsidian (Markdown vault), dotfiles (symlink management)

---

## Task 1: ブログ和訳を保存

**Files:**
- Create: `docs/blog-translations/2026-02-28-obsidian-ai-second-brain.md`

**Step 1: ディレクトリ確認**

Run: `ls docs/`
Expected: `plans/ reports/ templates/` が存在（blog-translations/ はまだない）

**Step 2: 和訳記事を保存**

`docs/blog-translations/2026-02-28-obsidian-ai-second-brain.md` にブログの日本語翻訳を保存する。

元記事: Noah Vincent「How to Build Your AI Second Brain Using Obsidian + Claude Code」
- 構造: 見出し・段落を原文に忠実に維持
- 冒頭にメタデータ（原文URL、著者、翻訳日）を付与
- 技術用語（Obsidian, Claude Code, MCP, Zettelkasten等）は原文のまま

**Step 3: Commit**

```bash
git add docs/blog-translations/2026-02-28-obsidian-ai-second-brain.md
git commit -m "📝 docs: add Japanese translation of Obsidian AI Second Brain blog"
```

---

## Task 2: Obsidian Vault テンプレート作成

**Files:**
- Create: `templates/obsidian-vault/CLAUDE.md`
- Create: `templates/obsidian-vault/.claude/memory.md`
- Create: `templates/obsidian-vault/00-Inbox/.gitkeep`
- Create: `templates/obsidian-vault/01-Projects/.gitkeep`
- Create: `templates/obsidian-vault/02-Areas/.gitkeep`
- Create: `templates/obsidian-vault/03-Resources/.gitkeep`
- Create: `templates/obsidian-vault/04-Galaxy/_templates/permanent-note.md`
- Create: `templates/obsidian-vault/05-Literature/_templates/literature-note.md`
- Create: `templates/obsidian-vault/06-Archive/.gitkeep`

**Step 1: ディレクトリ構造を作成**

Run: `mkdir -p templates/obsidian-vault/{.claude,00-Inbox,01-Projects,02-Areas,03-Resources,04-Galaxy/_templates,05-Literature/_templates,06-Archive}`

**Step 2: CLAUDE.md テンプレートを作成**

`templates/obsidian-vault/CLAUDE.md` に以下の構成で作成:

```markdown
# Obsidian Vault — AI Second Brain

## Identity

<!-- ここにあなたの情報を記入 -->
- 名前: [YOUR_NAME]
- 役割: [YOUR_ROLE]
- 関心分野: [YOUR_INTERESTS]

## Vault Architecture

このVaultは IPARAG + Zettelkasten メソッドで構成されている。

| フォルダ | 目的 |
|---------|------|
| 00-Inbox | 未整理ノートの一時置き場。キャプチャしたらここに入れる |
| 01-Projects | アクティブなプロジェクト。完了期限があるもの |
| 02-Areas | 継続的に管理する領域。健康、財務、キャリア等 |
| 03-Resources | リファレンス・参考資料。いつか使うかもしれない情報 |
| 04-Galaxy | Zettelkasten パーマネントノート。自分の言葉で書いた知識の原子 |
| 05-Literature | 読書・動画・記事のノート。ソースからの抽出 |
| 06-Archive | 完了・非アクティブ項目 |

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
- `#topic/xxx` — トピック別タグ

## Linking Rules

- パーマネントノートは最低1つの既存ノートにリンクする
- `[[ノート名]]` でリンク。エイリアスは `[[ノート名|表示名]]`
- リンクの理由を簡潔に書く（なぜ関連するか）
- 孤立ノートは定期的にリンク候補を探す

## Writing Style

<!-- ここにあなたのスタイルを記入 -->
- トーン: [CASUAL/FORMAL/MIXED]
- 言語: [ja/en/mixed]
- 禁止: ジェネリックなAI臭い表現、曖昧な結論

## Active Projects

<!-- Claudeが自動更新する -->
- (まだプロジェクトなし)
```

**Step 3: memory.md テンプレートを作成**

`templates/obsidian-vault/.claude/memory.md` に以下を作成:

```markdown
# Vault Memory

<!-- Claudeが各セッション後に自動更新する -->

## 最新セッション

(まだセッションなし)

## 確立されたパターン

(まだなし)

## 進行中のプロジェクト

(まだなし)
```

**Step 4: パーマネントノート テンプレートを作成**

`templates/obsidian-vault/04-Galaxy/_templates/permanent-note.md`:

```markdown
---
created: {{date:YYYY-MM-DD}}
tags:
  - type/permanent
  - status/seed
  - topic/
links: []
source: ""
---

# {{title}}

## 主張

<!-- このノートの核となるアイデアを1-2文で -->

## 詳細

<!-- 自分の言葉で展開 -->

## 関連ノート

- [[]] — 関連の理由
```

**Step 5: 文献ノート テンプレートを作成**

`templates/obsidian-vault/05-Literature/_templates/literature-note.md`:

```markdown
---
created: {{date:YYYY-MM-DD}}
tags:
  - type/literature
  - topic/
source:
  title: ""
  author: ""
  url: ""
  type: "" # book/article/video/podcast
---

# {{title}}

## ハイライト

-

## 自分の考え

<!-- ハイライトから何を学んだか -->

## パーマネントノート候補

<!-- このソースから生まれそうなパーマネントノートのアイデア -->
- [ ]
```

**Step 6: .gitkeep ファイルを作成**

Run: `touch templates/obsidian-vault/{00-Inbox,01-Projects,02-Areas,03-Resources,06-Archive}/.gitkeep`

**Step 7: Commit**

```bash
git add templates/obsidian-vault/
git commit -m "✨ feat: add Obsidian Vault template for AI Second Brain"
```

---

## Task 3: `/obsidian-vault-setup` スキル作成

**Files:**
- Create: `.config/claude/skills/obsidian-vault-setup/SKILL.md`

**Step 1: スキルファイルを作成**

`.config/claude/skills/obsidian-vault-setup/SKILL.md` に以下を作成:

```markdown
---
name: obsidian-vault-setup
description: 新しい Obsidian Vault を「AI第二の脳」としてセットアップする。テンプレートからフォルダ構造を作成し、CLAUDE.md をカスタマイズする。
---

# Obsidian Vault Setup

新しい Obsidian Vault を Claude Code と連携する「AI第二の脳」としてセットアップする。

## 前提条件

- Claude Code が Obsidian Vault のディレクトリ内で起動されていること
- テンプレートが `~/dotfiles/templates/obsidian-vault/` に存在すること

## 処理手順

### Step 1: 現在のディレクトリを確認

Bash で `pwd` を実行し、Obsidian Vault のルートにいることを確認する。
既にフォルダ構成が存在する場合は Step 3 にスキップ。

### Step 2: テンプレートからフォルダ構成をコピー

```bash
cp -r ~/dotfiles/templates/obsidian-vault/* .
cp -r ~/dotfiles/templates/obsidian-vault/.claude .
```

コピー後、Glob でフォルダ構成が正しく作成されたことを確認する。

### Step 3: ユーザーインタビュー

AskUserQuestion を使って以下を順番に聞く（1つずつ）:

1. 「このVaultの主な用途は何ですか？」
   - ナレッジマネジメント（Zettelkasten）
   - コンテンツ作成（ブログ、ニュースレター）
   - プロジェクト管理
   - 学習・研究
   - 複合（上記の組み合わせ）

2. 「あなたの名前と役割を教えてください」（自由入力）

3. 「主な関心分野やトピックは？」（自由入力）

4. 「ライティングスタイルの好みは？」
   - カジュアル（友人に話すような）
   - フォーマル（論文・ビジネス調）
   - ミックス（内容による）

5. 「主に使う言語は？」
   - 日本語
   - 英語
   - 日英混合

### Step 4: CLAUDE.md をカスタマイズ

回答を基に `CLAUDE.md` の `[PLACEHOLDER]` 部分を書き換える:

- `[YOUR_NAME]` → ユーザーの名前
- `[YOUR_ROLE]` → ユーザーの役割
- `[YOUR_INTERESTS]` → 関心分野
- `[CASUAL/FORMAL/MIXED]` → ライティングスタイル
- `[ja/en/mixed]` → 言語設定

用途に応じて追加セクションを書く:
- コンテンツ作成 → 「Content Pipeline」セクション追加
- プロジェクト管理 → 「Project Workflow」セクション追加

### Step 5: memory.md を初期化

`.claude/memory.md` に初期セッションの記録を書く:

```markdown
## 最新セッション

### YYYY-MM-DD: Vault 初期セットアップ
- Vault 構造を作成
- CLAUDE.md をカスタマイズ
- 用途: [ユーザーの回答]
- 言語: [ユーザーの回答]
```

### Step 6: キャリブレーション

Vault 全体を Glob/Read でスキャンし、以下を確認:
- フォルダ構成が正しいか
- CLAUDE.md が正しくカスタマイズされたか
- テンプレートファイルが配置されているか

確認結果をユーザーに報告し、セットアップ完了を宣言する。

## 完了条件

- [ ] フォルダ構成（00-Inbox 〜 06-Archive）が存在する
- [ ] CLAUDE.md がカスタマイズされている
- [ ] .claude/memory.md が初期化されている
- [ ] テンプレートファイルが配置されている
```

**Step 2: Commit**

```bash
git add .config/claude/skills/obsidian-vault-setup/
git commit -m "✨ feat: add /obsidian-vault-setup skill"
```

---

## Task 4: `/obsidian-knowledge` スキル作成

**Files:**
- Create: `.config/claude/skills/obsidian-knowledge/SKILL.md`

**Step 1: スキルファイルを作成**

`.config/claude/skills/obsidian-knowledge/SKILL.md` に以下を作成:

```markdown
---
name: obsidian-knowledge
description: Obsidian Vault 内のナレッジを検索・整理・リンクする。ノート検索、タグ一括変更、リンク候補発見、文献ノートからパーマネントノート生成。
---

# Obsidian Knowledge Manager

Vault 内のナレッジを管理する。自然言語で指示を受けて、検索・整理・リンク・合成を行う。

## 前提条件

- Claude Code が Obsidian Vault のルートで起動されていること
- CLAUDE.md が存在し、Vault の構成が記述されていること

## 引数の解釈

引数なし → インタラクティブモード（何をしたいか聞く）
引数あり → 自然言語コマンドとして解釈

例:
- `/obsidian-knowledge 潜在意識についてのノートを5つ探して`
- `/obsidian-knowledge タグ #old-tag を #new-tag に変更して`
- `/obsidian-knowledge リンクされるべきノートを見つけて`
- `/obsidian-knowledge この文献ノートからパーマネントノートを作って`

## 機能

### 1. ノート検索（Search）

**トリガー**: 「探して」「見つけて」「検索」を含む指示

**手順**:
1. CLAUDE.md を読んで Vault 構成を把握
2. Agent ツール（subagent_type: Explore）でVaultをスキャン:
   - Grep でキーワード・トピックに一致するファイルを特定
   - Glob でフォルダ内のファイル一覧を取得
3. 関連ファイルを Read で読み込み
4. 各ノートのサマリー（タイトル、核となるアイデア、タグ、リンク）を返す

**出力フォーマット**:
```
### 検索結果: [トピック]

1. **[ノートタイトル]** (`04-Galaxy/filename.md`)
   - 要約: ...
   - タグ: #topic/xxx
   - リンク: [[関連ノート1]], [[関連ノート2]]

2. ...
```

### 2. タグ管理（Tag）

**トリガー**: 「タグ」「tag」を含む指示

**手順**:
1. Grep で対象タグを含むすべてのファイルを検索
2. ファイル一覧と件数をユーザーに表示
3. AskUserQuestion で確認:「N件のファイルのタグを変更します。実行しますか？」
4. 承認後、Edit ツールで各ファイルのタグを更新
5. 変更結果のサマリーを表示

### 3. リンク発見（Link Discovery）

**トリガー**: 「リンク」「link」「つながり」を含む指示

**手順**:
1. Agent ツール（subagent_type: Explore）で Galaxy フォルダ全体をスキャン
2. 各ノートのキーワード・トピックを抽出
3. コンテンツの類似性を分析し、リンクされていないが関連するノートペアを特定
4. リンク候補をリスト表示:
   ```
   - [[ノートA]] ↔ [[ノートB]]: [関連の理由]
   ```
5. AskUserQuestion でどのリンクを追加するか確認
6. 承認されたリンクを Edit で追加

### 4. ノート合成（Synthesize）

**トリガー**: 「作って」「生成」「合成」「パーマネントノート」を含む指示

**手順**:
1. ソースとなる文献ノートを Read で読み込み
2. ハイライトとメモを抽出
3. CLAUDE.md のライティングスタイルに従って、パーマネントノートを生成:
   - テンプレート（`04-Galaxy/_templates/permanent-note.md`）に準拠
   - 核となるアイデアを自分の言葉で書く
   - 既存の関連ノートを Grep で検索してリンク
4. 生成したノートをプレビュー表示
5. AskUserQuestion で確認後、Write で保存
6. memory.md を更新

### 5. テーマ分析（Theme Analysis）

**トリガー**: 「テーマ」「クラスター」「分析」を含む指示

**手順**:
1. Agent ツール（subagent_type: Explore）で Galaxy 全体をスキャン
2. タグ・リンク・コンテンツからテーマクラスターを抽出
3. 可視化:
   ```
   テーマ: [テーマ名]
   ├── [[ノート1]] (evergreen)
   ├── [[ノート2]] (growing)
   └── [[ノート3]] (seed)
   関連テーマ: [テーマX], [テーマY]
   ```

## memory.md 更新

各操作後、`.claude/memory.md` に実行した操作のサマリーを追記する。
```

**Step 2: Commit**

```bash
git add .config/claude/skills/obsidian-knowledge/
git commit -m "✨ feat: add /obsidian-knowledge skill for vault knowledge management"
```

---

## Task 5: `/obsidian-content` スキル作成

**Files:**
- Create: `.config/claude/skills/obsidian-content/SKILL.md`

**Step 1: スキルファイルを作成**

`.config/claude/skills/obsidian-content/SKILL.md` に以下を作成:

```markdown
---
name: obsidian-content
description: Obsidian Vault 全体のコンテキストを活用してコンテンツを生成する。ニュースレター、ブログ記事、ツイートスレッド等。ノートを検索し、ライティングスタイルに従って生成。
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

## [本文セクション × N]
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

🧵 [スレッドテーマ]

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
```

**Step 2: Commit**

```bash
git add .config/claude/skills/obsidian-content/
git commit -m "✨ feat: add /obsidian-content skill for vault-based content creation"
```

---

## Task 6: 全体の検証

**Step 1: ファイル構成の確認**

Run: `find templates/obsidian-vault -type f | sort`
Expected: テンプレートファイル一覧が正しく表示される

Run: `ls .config/claude/skills/obsidian-*/SKILL.md`
Expected: 3つのスキルファイルが表示される

**Step 2: スキルの構文確認**

各 SKILL.md の YAML frontmatter が正しいか確認:
- `name` フィールドが存在する
- `description` フィールドが存在する
- `---` で正しく囲まれている

**Step 3: 最終コミット（必要な場合）**

未コミットの変更があれば最終コミット。

---

## 並列実行可能なタスク

- Task 1（和訳保存）は独立 → 並列可能
- Task 2（テンプレート）は独立 → 並列可能
- Task 3-5（スキル3つ）は相互に独立 → 並列可能
- Task 6（検証）は Task 1-5 の完了後
