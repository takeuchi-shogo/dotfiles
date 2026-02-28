# Obsidian + Claude Code「AI第二の脳」設計ドキュメント

## 概要

Noah Vincent のブログ記事「How to Build Your AI Second Brain Using Obsidian + Claude Code」を参考に、dotfilesリポジトリにObsidian Vault テンプレートと3つのClaude Codeスキルを追加する。

## 背景

- ブログの核心: AIに永続コンテキストを与えることで、ジェネリックな出力を排除する
- CLAUDE.md + memory.md でセッションをまたいだ知識の蓄積
- Skillsで繰り返しワークフローをコマンド化
- 既存のdotfiles設定（13エージェント、14スキル、6コマンド）に統合する

## 成果物

### 1. Obsidian Vault テンプレート

**配置**: `templates/obsidian-vault/`

```
templates/obsidian-vault/
├── CLAUDE.md                    # Vault用AIコンテキスト
├── .claude/
│   └── memory.md                # セッションログ（空テンプレート）
├── 00-Inbox/                    # 未整理ノートの一時置き場
├── 01-Projects/                 # アクティブなプロジェクト
├── 02-Areas/                    # 継続的に管理する領域
├── 03-Resources/                # リファレンス・参考資料
├── 04-Galaxy/                   # Zettelkasten パーマネントノート
│   └── _templates/
│       └── permanent-note.md
├── 05-Literature/               # 読書・動画・記事のノート
│   └── _templates/
│       └── literature-note.md
└── 06-Archive/                  # 完了・非アクティブ項目
```

#### CLAUDE.md の構成

1. **Identity**: Vaultオーナーの情報（名前、役割、関心分野）
2. **Vault Architecture**: フォルダ構成と各ディレクトリの目的
3. **Naming Conventions**: ファイル命名規則
4. **Tagging System**: タグの階層構造と使い方
5. **Linking Rules**: Zettelkastenリンクの規則
6. **Writing Style**: トーン、文体、禁止パターン
7. **Templates**: ノート種類ごとのテンプレート参照
8. **Active Projects**: 現在進行中のプロジェクト一覧

#### memory.md の構成

- セッション日時
- 実行したアクション
- 下した決定
- 次回の継続ポイント
- 学んだパターン

### 2. スキル: `/obsidian-vault-setup`

**目的**: 新しいObsidian Vaultを「AI第二の脳」としてセットアップする

**ステップ**:
1. テンプレートフォルダ構造を指定パスにコピー
2. ユーザーにインタビュー（名前、プロジェクト、関心分野、ライティングスタイル）
3. 回答を基にCLAUDE.mdをカスタマイズ
4. memory.mdを初期化
5. Vault構造を読んで初期キャリブレーション
6. セットアップ完了を確認

### 3. スキル: `/obsidian-knowledge`

**目的**: Vault内のナレッジを検索・整理・リンクする

**機能**:
- **検索**: 自然言語でGalaxy/Literature内のノートを検索し、ソースとサマリーを返す
- **タグ管理**: タグの一括変更、タクソノミー更新
- **リンク発見**: コンテンツ解析でリンクされるべきノート候補を提案
- **ノート合成**: 文献ノートからパーマネントノートを生成（ハイライト読み込み→コンセプト合成→フォーマット→リンク）
- **テーマ分析**: 複数ノートにまたがるテーマのつながりを発見

**実装**:
- サブエージェント（Explore）でVaultを高速スキャン
- Grep/Globで関連ファイルを特定
- Read でコンテンツを解析
- Write/Edit でノートを作成・更新

### 4. スキル: `/obsidian-content`

**目的**: Vault全体のコンテキストを活用してコンテンツを生成する

**ステップ**:
1. トピックを受け取る
2. サブエージェントをパラレル起動:
   - Galaxy内の関連パーマネントノートを検索
   - 過去のコンテンツ（同トピック）を検索
   - Literature notesから関連ハイライトを検索
3. 収集したコンテキストを統合
4. CLAUDE.mdのライティングルールに従ってコンテンツ生成
5. メタデータ（タイトル、タグ、日付）付きで正しいフォルダに保存
6. memory.mdを更新

**出力形式**:
- ニュースレター
- ブログ記事
- ツイートスレッド
- その他（ユーザー指定のフォーマット）

### 5. ブログ和訳

**配置**: `docs/blog-translations/2026-02-28-obsidian-ai-second-brain.md`

## 実装の優先順位

1. ブログ和訳を保存
2. Vault テンプレート作成
3. `/obsidian-vault-setup` スキル作成
4. `/obsidian-knowledge` スキル作成
5. `/obsidian-content` スキル作成

## 技術的な考慮事項

- スキルはすべて `.config/claude/skills/` に配置（既存symlinkで自動反映）
- Vault テンプレートは `templates/` に配置（手動コピーまたはスキルで展開）
- 既存のエージェント（Explore, general-purpose）を活用
- MCP追加は不要（ファイル直接アクセスで十分）
