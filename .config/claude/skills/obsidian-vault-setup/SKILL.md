---
name: obsidian-vault-setup
description: "Use when setting up a new Obsidian Vault as an 'AI second brain'. Creates folder structure from templates and customizes CLAUDE.md. Triggers: 'Vault 作りたい', 'Obsidian セットアップ', 'new vault', '第二の脳'. Do NOT use for: 既存 Vault のコンテンツ生成 (use obsidian-content), ナレッジ整理 (use obsidian-knowledge). .base/.canvas file formats → defer to obsidian plugin skills."
origin: self
metadata:
  pattern: generator
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

回答を基に `CLAUDE.md` の placeholder 部分を書き換える:

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

## Gotchas

- **template collision**: 既存 Vault にテンプレートを適用すると既存ファイルを上書きする可能性。バックアップ確認
- **sync conflict**: iCloud/Dropbox 同期中に Vault 構造を変更すると競合ファイルが発生。同期を一時停止してから実行
- **plugin 互換性**: テンプレートが前提とする Obsidian プラグインがインストールされているか確認
- **CLAUDE.md のパス**: Vault 内の CLAUDE.md はプロジェクト CLAUDE.md と混同しやすい。用途を明記

## Skill Assets

- `references/plugin-recommendations.md` — Obsidian plugin recommendations (Essential, Knowledge Management, Writing, AI Integration)
