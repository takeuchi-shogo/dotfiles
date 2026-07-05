---
title: Obsidian統合
topics: [tooling, memory]
sources: [2026-03-22-obsidian-agent-persistent-memory-analysis.md, 2026-03-23-claude-obsidian-ai-employee-analysis.md, 2026-03-16-notebooklm-obsidian-claude-integration.md, 2026-04-05-claude-code-3-memory-systems-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 15
confidence: established
---

# Obsidian統合

## 概要

ObsidianはMarkdownベースのナレッジベースツールで、AIエージェントの永続メモリ基盤として活用できる。MCP経由でClaude CodeにVaultへの直接読み書きアクセスを付与することで、セッション跨ぎのコンテキスト喪失を解消し「記憶を持つAIエージェント」を実現する。dotfilesはすでにCLAUDE.md + MEMORY.md + Progressive Disclosureによる高度なメモリ構造を持ち、Obsidian統合はその可視化・同期・複利成長レイヤーとして機能する。

## 主要な知見

- **単一コンテキストファイル原則** — `user.md`をVault rootに配置し毎セッション自動読み込みする設計は、dotfilesのCLAUDE.md + MEMORY.mdパターンと等価
- **自動メモリループ** — 通話文字起こし（Fathom）→ Zapier → Vault書き戻しで複利的コンテキスト充実。手動`/digest`との対比
- **Obsidian MCPサーバー** — NodeパッケージでClaude CodeにVault直接読み書きを付与。`settings.json`への`obsidian-mcp`設定が統合点
- **Smart Connections** — バックリンクと埋め込みから知識グラフを自動構築。手動MOC生成との補完関係
- **NotebookLM APIなし問題** — Consumer版は非公開API。自動化はGemini API / Claude Codeで代替が現実的
- **ハイブリッドノートシステム** — 5ノートシステム（IPARAG + Zettelkasten）の各要素が制御するオブジェクトは異なる
- **複利効果** — 毎セッションVaultが成長 → AIコンテキストが自動充実。AutoEvolve 4層ループと同じ設計原則
- **セキュリティ原則** — サンドボックスモード・権限最小化・デフォルトスキル削除。dotfilesのhooks/deny rulesと対応
- **同期は「配線」がないと発火しない** — メモリ→Vault同期スクリプト自体が存在しても、Stop hookに未登録なら学習成果はcron待ちか手動編集時にしか流れない。18ファイルのバックログで実際に検出された。「部品は揃っているが接続されていない」は本概念の再発パターン
- **Vault用CLAUDE.mdは薄く、判断基準は別ファイルに逃がす** — .claude/commands・rules・skillsの3層分離（薄いCLAUDE.md+厚いrules/、動詞+名詞命名、1コマンド1タスク、禁止より推奨の規範的フレーミング）はVault側のCLAUDE.mdにも適用でき、root肥大化を防ぐ
- **信念の矛盾照合はVault全文でなく仮説欄限定で行う** — 保存済みの信念・仮説との矛盾検出は価値があるが、Vault全体を常時スキャンすると誤検出とコンテキスト肥大を招く。thinking-context.mdの仮説欄など明示実行時・狭いスコープに限定するのが安全設計
- **Vaultの構造選択は「なぜそうしないか」を明文化して飽和ガードにする** — IPARAG多フォルダ vs フラット単一フォルダのような設計論争は、選ばなかった側の理由（actionability分類・独立namespaceが必要なノートタイプの存在・大規模化での検索性能劣化）を明文化しておくと、類似記事が繰り返し現れても再検討コストがゼロになる
- **フィードバックループは自動更新でなく「差分提案+人間承認」に留める** — 定期ブリーフィングに軽量な注釈欄（useful/noise/missing）を設け、週次で頻出パターンを集計してcontext更新を"提案"する設計は有効。ただしAIが注釈を自動更新すると手動負担増による形骸化やnoise混入のリスクがあるため、提案止まり・ユーザー承認制を守る
- **キャプチャとその後の活用は別工程として設計する** — ノートを取る瞬間（capture）と、後で意思決定・執筆・会話に使う瞬間（use）を混同すると、蓄積されるだけで使われないVaultになる。任意入力のキャプチャテンプレート（関連ノート・想定用途・浮かぶ疑問など）と、意思決定時にVaultを検索してSupports/Challenges/Adds nuanceに分類する仕組みを分けて持つと機能しやすい
- **Vaultも「attention budget」問題を抱える** — CLAUDE.mdの肥大化が性能を下げるのと同じ理屈で、Vault内の索引・ノート量が増えすぎるとAIが参照するときのsignalが薄まる。定期的なsignal-density監査（rareタグ・命名規約違反・stale化したノートの棚卸し）と、archive-before-delete（即削除せず一定期間archiveに退避）の組み合わせで対処する。ただしpruning mechanismを実装しただけでは足りず、hookへの再接続を怠ると閾値超過が放置される
- **creator-monetization型のsecond brain記事は構造的に低収率** — フォロワー数KPIを持つコンテンツクリエイターが書く「AIがVaultを完全に理解する」系の記事は、有料SaaS前提・裏付けデータなしの逸話ベースが多く、繰り返し似た主張が再パッケージされる。反面教師として、Vaultは「AIが常時reasoning inputとして読む」ものではなく「memory→Vaultの一方向同期スナップショット」と位置づける設計の方が、dotfilesの実運用とは整合する

## 実践的な適用

dotfilesでの現状と計画：

| 機能 | 現状 | 方針 |
|------|------|------|
| 単一コンテキストファイル | CLAUDE.md + MEMORY.md（Already） | 強化不要 |
| メモリ→Vault同期 | `sync-memory-to-vault.sh` → `08-Agent-Memory/`（Already） | Dataview テーブルビューで可視化済み |
| Obsidian MCPサーバー | settings.jsonに設定済み（Already） | MCP 経由で読み書き可能 |
| 領域別ダッシュボード | `02-Areas/` に4領域（Development/Learning/Content/Health）（Already） | Dataview クエリで動的更新 |
| メモリテーブルビュー | `08-Agent-Memory/Agent Memory Overview.md`（Already） | type/description/synced_at でテーブル表示 |
| 自動ブリーフィング | `/morning`手動のみ（Partial） | 自動配信を計画 |
| 知識グラフ | `/obsidian-knowledge`で手動生成 | バックグラウンド自動化は将来 |
| 24/7アーキテクチャ | ローカルセッションのみ（Gap） | 常時稼働マシン不要のため保留 |
| Stop hookでのVault同期 | `sync-memory-to-vault.sh`をStop hookに登録済み（Already） | セッション終了時に自動発火、cron待ちのバックログを解消 |
| 信念の矛盾照合 | `/think`にthinking-context.md仮説欄との矛盾候補抽出ステップを追加（Already） | Vault全文スキャンは行わず狭いスコープを維持 |
| 意思決定フィード | `obsidian-knowledge`にVaultスキャン→Supports/Challenges/Adds nuance分類機能を追加（Already） | `/decision`（記録）・`/think decision`（構造化）と責務分離 |
| キャプチャテンプレート | `00-Inbox/_templates/capture.md`で関連ノート・想定用途を任意記入（Already） | `/note`の即時性は維持しつつ活用文脈を残す |
| Vaultのsignal-density監査 | `vault-maintenance.sh`にrareタグ・命名規約違反チェックを追加（Already） | dry-run専用、自動修正はしない |

`docs/wiki/concepts/obsidian-integration.md`関連のVault CLAUDE.mdには「なぜIPARAG多フォルダを選び単一フォルダ化しないか」の設計根拠を明文化済み（`templates/obsidian-vault/CLAUDE.md`）。

`docs/plans/2026-03-16-obsidian-knowledge-pipeline-design.md`でナレッジパイプライン設計が進行中。`/obsidian-vault-setup`スキルによりZettelkasten + PARAハイブリッド構成を整備済み。

## 関連概念

- [エージェントメモリ](agent-memory.md) — 3層メモリスコープ（user/project/local）との対応
- [ナレッジパイプライン](knowledge-pipeline.md) — 外部情報のVault取り込みフロー
- [コンテキストエンジニアリング](context-engineering.md) — Progressive Disclosureとの統合点

## ソース

- [Obsidianエージェント永続メモリ](../../research/2026-03-22-obsidian-agent-persistent-memory-analysis.md) — セッション跨ぎコンテキスト保持の手法とGap分析
- [Claude + Obsidian = AI従業員](../../research/2026-03-23-claude-obsidian-ai-employee-analysis.md) — 構造化ナレッジベースと自動メモリループの設計パターン
- [NotebookLM + Obsidian + Claude統合調査](../../research/2026-03-16-notebooklm-obsidian-claude-integration.md) — ツール選択の現実解とハイブリッドノートシステムの原則
- [Obsidian + Claude Code is the New Meta 分析](../../research/2026-04-09-obsidian-claude-code-meta-analysis.md) — Obsidian統合記事を分析、Vault自動メンテナンス等採用
- [Full AI Stack Using Only Claude 分析](../../research/2026-04-10-claude-full-ai-stack-2026-analysis.md) — Claude単体AIスタック記事を分析、Obsidian同期hookのみ採用
- [Modified Karpathy Method セカンドブレイン分析](../../research/2026-04-14-karpathy-second-brain-modified-analysis.md) — Karpathy法改変記事分析、frontmatterでなく_drafts分離方式で採用
- [Obsidian × Claude Code .claudeディレクトリ設計分析](../../research/2026-04-21-obsidian-claudecode-absorb-analysis.md) — Obsidianのcommands/skills設計を分析、Inbox連携等5タスクを採用
- [Obsidian Knowledge Vault構築分析](../../research/2026-05-08-cyril-obsidian-vault-absorb-analysis.md) — Obsidian Vault構築法を分析、矛盾検出等3件のみ採用
- [Obsidian Dashboard That Shows Everything分析](../../research/2026-05-19-cyril-obsidian-dashboard-absorb-analysis.md) — Obsidianダッシュボード記事はEoD整合修正のみ採用
- [One Folder運用システム分析](../../research/2026-05-22-cyril-one-folder-absorb-analysis.md) — フラットVault構造記事を検証しIPARAG選択理由を文書化
- [Claude ObsidianセカンドブレインDamidefi分析](../../research/2026-05-23-damidefi-claude-obsidian-second-brain-absorb-analysis.md) — second brain記事は採用0、creator-monetization型構造を確認
- [Obsidian Vault整理術分析](../../research/2026-05-25-cyrilxbt-organize-vault-absorb-analysis.md) — Vault整理記事からrare-tag監査とnaming checkを採用
- [Codex Research Agent Workflow分析](../../research/2026-05-28-codex-research-agent-workflow-absorb-analysis.md) — 朝ブリーフ記事、注釈欄と週次差分提案など3件採用
- [Turn Every Note Into Something You Actually Use分析](../../research/2026-05-30-cyrilxbt-notes-into-output-absorb-analysis.md) — ノート活用術記事、キャプチャ規約と意思決定フィード採用
- [Delete 90% of Your Obsidian Notes分析](../../research/2026-05-31-damidefi-delete-90-vault-absorb-analysis.md) — Vault削除記事のsignal density原則を分析、MEMORY.mdを223→154行に圧縮
