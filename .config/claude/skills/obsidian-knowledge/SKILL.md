---
name: obsidian-knowledge
description: "Obsidian Vault のナレッジ整理・検索・リンク化を行う。ノート検索、bulk タグ変更、リンク候補発見、Literature → Permanent Note 昇格、MOC 自動生成、意思決定の判断材料を vault から集約。Triggers: 'ノート検索', 'タグ整理', 'リンク候補', 'MOC生成', 'パーマネントノート', 'Vault整理', 'ナレッジ整理', 'ノート整理', '関連ノート探して', 'リンク追加', 'permanent note 化', '意思決定の判断材料', 'decision brief', '判断材料を集めて'. Do NOT use for: コンテンツ生成 (use obsidian-content)、Vault 初期セットアップ (use obsidian-vault-setup)、Markdown syntax/properties/callouts (defer to obsidian:obsidian-markdown)、CLI commands (defer to obsidian:obsidian-cli)、Literature Note 作成 (use /digest)、思考の壁打ち・意思決定の構造化 (use /think decision)。"
origin: self
user-invocable: true
metadata:
  pattern: tool-wrapper
  chain:
    upstream: ["/digest (Literature Note 作成)", "/note (Inbox 保存)"]
    downstream: ["obsidian:obsidian-cli (CLI 操作)", "obsidian:obsidian-markdown (記法)"]
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
- `/obsidian-knowledge machine-learningのMOCを作って`

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

### 6. MOC 生成（Map of Content）

**トリガー**: 「MOC」「マップ」「目次」「Map of Content」を含む指示

**手順**:
1. CLAUDE.md を読んで Vault 構成を把握
2. Agent ツール（subagent_type: Explore）で `04-Galaxy/` と `05-Literature/` をスキャン:
   - 各ノートのタグ・タイトル・リンク・要約を収集
3. トピック特定:
   - 指定あり → そのトピックのノートを抽出
   - 指定なし → タグ頻度でトップクラスターを一覧表示し、AskUserQuestion でユーザーに選んでもらう
4. クラスター内のノートをサブトピックでグループ化
5. 各ノートの1行サマリーを生成
6. MOC テンプレートに整形してプレビュー表示
7. AskUserQuestion で確認後、Write で保存:
   - 保存先: `03-Resources/MOC-{topic-slug}.md`
8. memory.md を更新

**出力フォーマット**:
```
---
created: "{YYYY-MM-DD}"
tags:
  - type/moc
  - "topic/{トピック}"
---

# {トピック} Map of Content

## 概要

{このトピックの1-2文の説明}

## ノート一覧

### {サブトピック1}
- [[ノートA]] — 要約1文
- [[ノートB]] — 要約1文

### {サブトピック2}
- [[ノートC]] — 要約1文

## 関連 MOC

- [[MOC-関連トピック]]
```

### 7. メンテナンス（Maintenance）

**トリガー**: 「メンテナンス」「maintenance」「健全性」「ヘルスチェック」を含む指示

**手順**:
1. CLAUDE.md を読んで Vault 構成を把握
2. `vault-maintenance.sh` を `--dry-run` で実行し、結果を取得:
   ```bash
   OBSIDIAN_VAULT_PATH="<vault_path>" ~/.claude/scripts/runtime/vault-maintenance.sh --dry-run
   ```
3. 結果をユーザーに見やすく表示:
   - 孤立ノート数、リンク切れ数、Stale Seed 数、重複候補数
   - 各カテゴリの詳細リスト
4. AskUserQuestion で対処を確認:
   - 孤立ノート → リンク候補を提案（Link Discovery と連携）
   - リンク切れ → 修正候補を提案（類似ファイル名検索）
   - Stale Seed → アーカイブ or 育成を提案
   - 重複 → マージ候補を提示
5. 承認されたアクションを実行

### 8. 意思決定フィード（Decision Feeder）

**トリガー**: 「意思決定の判断材料」「judgment material」「decision brief」「判断材料を集めて」を含む指示 + 決定内容の記述

**目的**: 意思決定を「記録」する前に、その決定に関連する蓄積ノートが何を知っているかを vault 全体から surface し、support / challenge / nuance に分類して brief 化する。記録は `/decision`、思考の構造化は `/think decision` が担当し、本機能は **判断材料の収集** に特化する。

**手順**:
1. ユーザーから決定内容（例: 「ライブラリ A と B どちらを採用するか」）を受け取る
2. Agent ツール（subagent_type: Explore）で `04-Galaxy/` `03-Resources/` `05-Literature/` を中心に vault をスキャン:
   - 明示タグ一致だけでなく、**その決定に thoughtful な人が考慮するであろう**意味的関連ノートを拾う
3. 各関連ノートを Read し、決定との関係を分類:
   - **Supports** — 決定の一方を支持する根拠
   - **Challenges** — 決定に反論・複雑化する観点
   - **Adds nuance** — 前提・制約・トレードオフを補足する情報
4. brief に統合して提示:
   ```
   ## Decision Brief: [決定の記述]

   ### Supports
   - [[ノートA]] — 何が関連するか / なぜ支持するか

   ### Challenges
   - [[ノートB]] — 何が決定を複雑化するか

   ### Adds nuance
   - [[ノートC]] — 補足する前提・制約

   ### 蓄積ノートが示す総合的な見立て
   {vault 内の情報だけを根拠にした 2-3 文}
   ```
5. **重要な制約**: **vault 外の情報を加えない**。一般知識や推測で brief を補完しない。「蓄積ノートが何を知っているか」だけを surface する（記事 Active Decision Feeder の核心原則）。vault に関連ノートがゼロなら「該当ノートなし」と正直に報告する
6. 必要に応じて `/decision`（記録）や `/think decision`（構造化思考）への連携を提案

**前提と限界**: 数十ノート以上が蓄積された vault で効果を発揮する。蓄積が薄い段階では surface できる材料が少ない。

## memory.md 更新

各操作後、`.claude/memory.md` に実行した操作のサマリーを追記する。

## Skill Assets

- `templates/moc-template.md` — Map of Content template (core concepts, related topics, open questions, sources)
