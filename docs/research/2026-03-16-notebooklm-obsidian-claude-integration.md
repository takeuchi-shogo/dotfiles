---
status: active
last_reviewed: 2026-04-23
---

# NotebookLM + Claude Code + Obsidian 統合ワークフロー調査レポート

**調査日**: 2026-03-16
**トリガー**: 「5つのノートシステムを全部使え」「Collect, Compress, Connect」「NotebookLMで2分でコアアイデアを得る」

---

## Executive Summary

- **NotebookLM は API を持たない**（Consumer版）。Enterprise版のみ管理APIあり。非公式 CLI ツール `notebooklm-py` と AutoContent API が代替手段
- **YouTube → 構造化ノート** の最適解は **yt-dlp + Claude Code** または **Gemini CLI** で、NotebookLM は手動ワークフローとして優秀
- **5つのノートシステム** のハイブリッド運用は実践者が多く、「各システムが制御するオブジェクトが異なる」という原則が確認された
- **Claude Code + Obsidian** の "AI Second Brain" は 2025-2026 年のトレンド。MCP 経由の Vault 直接操作が主流
- **既存 dotfiles 基盤** は既にハイブリッドシステム (IPARAG + Zettelkasten) を実装済み。**MOC 自動生成**と**YouTube→Literature Note パイプライン**が最大のギャップ

---

## 1. NotebookLM: 機能・API・連携可能性

### 現在の機能 (2026年3月時点)

| 機能 | 詳細 |
|------|------|
| **ソース対応** | PDF, Google Docs, Slides, Web URL, YouTube URL, テキスト, 音声ファイル |
| **Audio Overview** | ソースから AI ポッドキャスト風音声を自動生成 |
| **Mind Map** | インタラクティブなマインドマップ生成 |
| **Study Guide** | フラッシュカード、クイズ、学習ガイド生成 |
| **Gemini 連携** | 2025年12月〜 Gemini アプリからノートブック直接アクセス可能 |
| **出力言語選択** | 生成テキストの言語指定可能 |
| **エクスポート** | フラッシュカード: Markdown/プレーンテキスト、マインドマップ: 編集可能形式、レポート: 構造付き保存 |

### API 状況

| 層 | API | 用途 |
|----|-----|------|
| **Consumer (無料/Plus)** | ❌ なし | 手動操作のみ |
| **Enterprise** | ✅ REST API (Pre-GA) | ノートブック CRUD、共有管理。POST/GET/DELETE。OAuth 2.0 認証 |
| **非公式** | `notebooklm-py` (CLI) | プログラマティックアクセス（非公式） |
| **サードパーティ** | AutoContent API | NotebookLM 風の要約・ポッドキャスト生成 API |

**結論**: Consumer 版は API なし。自動化するなら NotebookLM を経由せず、直接 Gemini API や Claude を使う方が現実的。

### Sources
- [NotebookLM Enterprise API](https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks)
- [NotebookLM API availability discussion](https://discuss.ai.google.dev/t/how-to-access-notebooklm-via-api/5084)
- [AutoContent API](https://autocontentapi.com/blog/does-notebooklm-have-an-api)
- [NotebookLM 2025 updates](https://workspaceupdates.googleblog.com/2025/03/new-features-available-in-notebooklm.html)

---

## 2. 5つのノートシステム × Obsidian ハイブリッド実践

### 各システムの「制御対象」

| システム | 制御対象 | Obsidian での実装 |
|---------|---------|------------------|
| **PARA** | フォルダ構造 (actionability) | Projects/Areas/Resources/Archive フォルダ |
| **Zettelkasten** | 個々のノート (atomic knowledge) | 1アイデア1ノート + `[[wikilinks]]` |
| **LYT / MOC** | ナビゲーション (hub notes) | テーマ別の索引ノート (Map of Content) |
| **Johnny Decimal** | 番号体系 (addressability) | `00-09`, `10-19` 等の番号付きフォルダ |
| **Evergreen Notes** | ノート成熟度 (quality lifecycle) | `#status/seed` → `#status/growing` → `#status/evergreen` |

### 実践者のハイブリッドパターン

**Hybrid Hacker のシステム** (最も包括的な事例):

```
📁 Journaling/          ← 日次キャプチャ (入口)
📁 PARA/
├── Projects/           ← 期限付きプロジェクト
├── Areas/              ← 継続的な責任領域
├── Resources/          ← 興味別の参考資料
└── Archive/            ← 完了したもの
📁 Neurons/             ← Zettelkasten (知識原子)
├── Fleeting Notes/     ← 一時的な思いつき
├── Literature Notes/   ← 読書・記事からの抽出
└── Evergreen Notes/    ← 成熟した永続的知識
📁 Humans/              ← 人物データベース
📁 System/              ← テンプレート・インフラ
```

- PARA が「行動可能性」でフォルダを分類
- Zettelkasten が「知識の原子化」でノートを構造化
- Johnny Decimal が番号体系で「住所」を付与
- 日次ジャーナルが入口 → PARA or Neurons に振り分け

**JoJoDe (Johnny Decimal + Zettelkasten)**:
- `[Project].[Area].[Category].[Item]` 形式の ID
- Inbox に一旦入れてから `Ctrl+M` で適切な場所に移動
- Obsidian の DataViewJS プラグインと連携

**Obsidian Starter Kit** (有料テンプレート):
- PARA + Zettelkasten + Johnny Decimal + GTD を統合
- 10ノートから10,000+ノートまでスケール

### 現在の dotfiles との差分

| 要素 | dotfiles (IPARAG) | ハイブリッドベストプラクティス | ギャップ |
|------|-------------------|-------------------------------|---------|
| フォルダ | ✅ 00-06 プレフィックス | PARA + JD 番号 | 小 |
| ノート | ✅ 永続ノート + 文献ノート | Fleeting → Literature → Evergreen | ⚠️ Fleeting Notes 未定義 |
| ナビゲーション | ❌ なし | MOC (テーマ別索引) | **大きなギャップ** |
| 成熟度 | ✅ タグあり | 自動昇格提案 | ⚠️ 手動のみ |

### Sources
- [Hybrid Hacker: How I Take Notes in Practice](https://hybridhacker.email/p/how-i-take-notes-in-practice)
- [JoJoDe: Johnny Decimal + Zettelkasten for Obsidian](https://github.com/furryablack/jojode)
- [Obsidian Starter Kit](https://obsidianstarterkit.com)
- [PARA + Zettelkasten Obsidian Forum](https://forum.obsidian.md/t/how-can-para-and-zettelkasten-workflow-live-together/3570?page=3)

---

## 3. Collect → Compress → Connect パイプライン

### ツール別の役割マッピング

```
[Collect]                    [Compress]              [Connect]
─────────────────────────    ──────────────────      ─────────────────
Readwise Reader              NotebookLM              Smart Connections
  ├── Kindle highlights      Claude Code             Obsidian Graph View
  ├── Web highlights         Gemini CLI              MOC 自動生成
  ├── RSS feeds              Progressive Summarize   Dataview クエリ
  ├── YouTube transcripts    Readwise AI Chat        Spaced Repetition
  ├── Podcast transcripts
  └── Twitter/X bookmarks
                    ↓              ↓                      ↓
              05-Literature    04-Galaxy              03-Resources/MOC-*.md
```

### 主要ツールと Obsidian 連携

**Readwise Reader** (Collect の中核):
- Kindle ハイライト、Web ハイライト、RSS、YouTube 字幕、ポッドキャスト、Twitter/X を一元収集
- Obsidian へ自動同期 (Readwise Official プラグイン)
- 2025年〜 AI チャット機能追加: ハイライトに質問・コンテキスト取得

**Smart Connections** (Connect の中核):
- RAG ベースで Vault 全体と対話
- ローカル/クラウドモデル対応
- ノート間の類似度自動検出

**Copilot** (Compress + Connect):
- Claude, GPT, Gemini, ローカルモデル対応
- Vault QA: ノートに基づく質問応答
- マルチモデル柔軟性

**Obsidian → Anki パイプライン** (Connect → Retention):
- AI でノートからフラッシュカード自動生成
- Spaced Repetition で記憶定着

### 実践者の事例: Stefan Imhoff (2025)
- Obsidian + Readwise + AI の3層システム
- 「ノート管理のオーバーヘッドを 30-40% → 10% 以下に削減」
- Agent スキルにワークフローをエンコード

### 現在の dotfiles との統合ポイント

| パイプライン段階 | 既存アセット | 追加すべきもの |
|-----------------|-------------|--------------|
| **Collect** | `/research` スキル (WebSearch) | Readwise 連携、`/digest` スキル |
| **Compress** | AutoEvolve (コード知識の圧縮) | ノート知識の AI 要約 |
| **Connect** | `obsidian-knowledge` (リンク発見) | MOC 自動生成、Smart Connections |

### Sources
- [Stefan Imhoff: My 2025 Note-Taking System](https://www.stefanimhoff.de/note-taking-obsidian-readwise-ai/)
- [Obsidian AI Second Brain Guide 2026](https://www.nxcode.io/resources/news/obsidian-ai-second-brain-complete-guide-2026)
- [Obsidian Skills for AI Agents](https://addozhang.medium.com/obsidian-skills-empowering-ai-agents-to-master-obsidian-knowledge-management-8b4f6d844b34)
- [Obsidian to Anki AI Pipeline](https://earezki.com/ai-news/2026-02-20-stop-copy-pasting-notes-building-an-ai-powered-pipeline-from-obsidian-to-anki/)
- [Obsidian AI Explained 2025](https://www.eesel.ai/blog/obsidian-ai)

---

## 4. YouTube → 構造化ノート変換: ツール比較

| 手法 | 品質 | 速度 | コスト | 自動化 | Obsidian 連携 |
|------|------|------|--------|--------|-------------|
| **NotebookLM** | ★★★★★ (引用付き、深い分析) | 手動2-3分 | 無料/Plus | ❌ API なし | ❌ コピペ必要 |
| **Gemini CLI** | ★★★★ (1M コンテキスト) | 自動1-2分 | API 課金 | ✅ 完全自動化可 | ✅ ファイル直接書き込み |
| **yt-dlp + Claude Code** | ★★★★ (カスタマイズ自在) | 自動1-2分 | API 課金 | ✅ 完全自動化可 | ✅ 直接書き込み |
| **Whisper + LLM** | ★★★★★ (字幕なし動画も対応) | 5-10分 | Whisper無料 + LLM課金 | ✅ スクリプト化可 | ✅ 出力フォーマット自由 |
| **youtube-transcript-api + Gemini** | ★★★ (字幕ベース) | 自動30秒 | API 課金 | ✅ 完全自動化可 | ✅ 出力フォーマット自由 |
| **Readwise Reader** | ★★★ (ハイライト中心) | 自動 | $7.99/月 | ✅ Obsidian 自動同期 | ★★★★★ 最高 |

### 推奨: `/digest` スキル実装案

```
YouTube URL
    │
    ├── [字幕あり] yt-dlp --write-sub → transcript.txt
    │       or youtube-transcript-api
    │
    ├── [字幕なし] Whisper or Gemini multimodal
    │
    ▼
Claude Code で構造化
    ├── 要約 (3-5文)
    ├── キーアイデア (箇条書き)
    ├── 引用 (タイムスタンプ付き)
    └── パーマネントノート候補
    │
    ▼
05-Literature/lit-{author}-{title}.md (既存テンプレート準拠)
    + 04-Galaxy へのリンク候補提示
```

### Sources
- [YouTube to Notes with Gemini](https://www.polarnotesai.com/prompts/youtube-to-notes/)
- [youtube-transcript-notes (GitHub)](https://github.com/BJB0/youtube-transcript-notes)
- [NotebookLM + YouTube study process](https://www.eviltester.com/blog/eviltester/productivity/notebooklm-and-youtube-study-process/)
- [ChatGPT vs Gemini vs NotebookLM comparison](https://www.ekamoira.com/blog/chatgpt-summarize-youtube-videos)
- [NotebookLM audio and YouTube support](https://blog.google/technology/ai/notebooklm-audio-video-sources/)

---

## 5. AI Second Brain 統合事例

### Claude Code + Obsidian (2025-2026 のメインストリーム)

**Noah Vincent のオリジナル手法**:
- CLAUDE.md に Vault のコンテキスト (名前、役割、興味、ライティングスタイル) を記述
- memory.md でセッション間の状態永続化
- Skills で繰り返しワークフローをコマンド化
- MCP で外部ツール (Things3, Tana) と連携

**NxCode 2026 ガイド** (最も包括的):
- MCP 経由で Claude Code が Vault を直接読み書き
- `obsidian-mcp-server` をインストールし settings.json で接続
- Context Engineering: 一貫した命名、YAML frontmatter、atomic notes、wikilinks
- プラグイン: Smart Connections, Templater, Dataview, Calendar

**複数の再実装者**:
- Sonny Huynh, Hugo Sequier, noqta.tn 等が Claude Code + Obsidian の実装記事を公開
- 共通パターン: CLAUDE.md + memory.md + Skills + MCP

### NotebookLM + Obsidian の組み合わせ

現状は**手動ブリッジ**が主流:
1. NotebookLM でソース (YouTube, PDF, Web) を処理
2. 要約・キーアイデアをコピー
3. Obsidian に Literature Note として手動作成

**自動化の壁**: NotebookLM に API がないため、プログラマティックな連携は困難。

### 3ツール統合の理想形

```
[NotebookLM]              [Claude Code]              [Obsidian]
 手動 intake               自動処理エンジン            永続ストレージ
 ・YouTube 視聴             ・構造化                   ・Zettelkasten
 ・PDF 精読                 ・リンク発見                ・MOC
 ・深い探索                 ・テンプレート適用           ・Graph View
                            ・成熟度管理
     │                          │                         │
     └── コピペ or /digest ──→   └── 直接ファイル書き込み ──→ │
```

**現実的な推奨**:
- **深い探索・理解** → NotebookLM (手動、無料、高品質)
- **自動パイプライン** → Claude Code + Gemini CLI (API ベース)
- **永続化・接続** → Obsidian (ローカルファースト、プレーンテキスト)

### 代替スタックとの比較

| スタック | 強み | 弱み |
|---------|------|------|
| **Obsidian + Claude Code** | 最大の柔軟性、ベンダーロックインなし、プレーンテキスト | セットアップ労力 |
| **Notion AI** | チーム協作、DB統合 | ベンダーロックイン、プレーンテキストでない |
| **Tana + AI** | ストラクチャードデータ、Supertags | クローズドフォーマット |
| **Logseq + LLM** | アウトライナー + ブロック参照 | AI 統合が限定的 |
| **Capacities** | オブジェクト指向ナレッジ管理 | 新しい、エコシステム小 |
| **Mem.ai** | AI ファーストの設計 | 自己ホスティング不可 |

### 2025-2026 の新興パターン

1. **MCP (Model Context Protocol)**: AI → ツール間の標準プロトコル。Obsidian MCP Server で Claude が Vault 直接操作
2. **Agent-based PKM**: ノートが「自己更新」する世界。Claude Code Skills でワークフロー自動化
3. **Context > Prompts**: CLAUDE.md にコンテキストを蓄積 → 毎回のプロンプト不要
4. **Agentic Note-Taking**: 情報収集 → 構造化 → リンク → 成熟を AI が自律的に実行

### Sources
- [NxCode: Obsidian AI Second Brain 2026 Guide](https://www.nxcode.io/resources/news/obsidian-ai-second-brain-complete-guide-2026)
- [Noah Vincent: AI Second Brain with Obsidian + Claude Code](https://noahvnct.substack.com/p/how-to-build-your-ai-second-brain)
- [Sonny Huynh: AI-Powered Second Brain](https://sonnyhuynhb.medium.com/i-built-an-ai-powered-second-brain-with-obsidian-claude-code-heres-how-b70e28100099)
- [Claude and Obsidian Second Brain (Towards AI)](https://pub.towardsai.net/from-notes-to-knowledge-the-claude-and-obsidian-second-brain-setup-37af4f47486f)
- [noqta.tn: AI Second Brain 2026](https://noqta.tn/en/blog/ai-second-brain-obsidian-claude-personal-os-2026)
- [Obsidian + Second Brain Productivity 2026](https://calmops.com/productivity/obsidian-second-brain-productivity-2026/)

---

## 6. アクションアイテム: dotfiles 基盤への統合提案

### 即効性 HIGH

| # | 施策 | 工数 | 効果 |
|---|------|------|------|
| 1 | **`/digest` スキル作成** | M | YouTube/Web URL → Literature Note 自動生成。yt-dlp + Claude Code |
| 2 | **MOC 自動生成を `/obsidian-knowledge` に追加** | S | 04-Galaxy のタグ・リンク分析 → `03-Resources/MOC-*.md` 生成 |
| 3 | **Fleeting Notes 層の追加** | S | テンプレートに `04-Galaxy/fleeting/` 追加。日次ジャーナル → Fleeting → Literature → Evergreen |

### 中期 MEDIUM

| # | 施策 | 工数 | 効果 |
|---|------|------|------|
| 4 | **Evergreen 成熟パイプライン** | M | リンク数・更新頻度でスコアリング → 昇格候補提示 |
| 5 | **Readwise 連携調査** | S | Readwise → Obsidian 同期設定。Kindle/Web/YouTube の自動 Collect |
| 6 | **NotebookLM 手動ワークフロー文書化** | S | Playbook 化: 深い探索時の NotebookLM → コピペ → `/digest` フロー |

### 長期 LOW

| # | 施策 | 工数 | 効果 |
|---|------|------|------|
| 7 | **Smart Connections プラグイン評価** | M | RAG ベースの Vault 対話。Claude Code 外でも知識検索 |
| 8 | **Obsidian MCP Server 導入** | L | Claude Code から Vault 直接操作 (現在はファイルシステム直接) |
