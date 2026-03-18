---
name: developer-onboarding
description: 開発者プロファイルを対話で構築し、type:user メモリとして保存する。初回セットアップまたはプロファイル更新に使用。
triggers:
  - "onboarding"
  - "自己紹介"
  - "プロファイル構築"
  - "知ってほしい"
---

# Developer Onboarding — プロファイル構築インタビュー

開発者としてのあなたを知るための構造化インタビュー。回答は `type: user` メモリとして保存され、全セッションで参照される。

## Workflow

```
Read existing user memories → Identify gaps → Interview (2-3 questions at a time) → Save as user memories
```

## Phase 1: 既存プロファイル確認

1. 既存の `type: user` メモリファイルを Glob で検索
2. 既にカバーされている領域を把握
3. ギャップのある領域からインタビューを開始

## Phase 2: インタビュー

AskUserQuestion で 2-3 問ずつ質問する。サーベイではなく対話。短い回答でも押さない。

### カバーする領域（自然な流れで、順序は固定しない）

**開発スタイル & 哲学**
- プランナーかビルダーか？設計重視 or プロトタイプ重視？
- TDD派？型安全重視？テストカバレッジの考え方
- コードの美学 — 簡潔さ重視 or 明示性重視？
- 嫌いなコードパターン、アンチパターン

**技術スタック**
- メイン言語、フレームワーク、得意領域
- 興味のある技術、学習中の技術
- 使い慣れたツール（エディタ、ターミナル、Git ワークフロー）

**作業スタイル**
- 典型的な1日のスケジュール（起床、集中時間帯、休憩パターン）
- 深い集中 or コンテキストスイッチング型？
- マルチタスクの傾向

**AI との協業スタイル**
- Claude にどう振る舞ってほしいか（簡潔 or 詳細、提案的 or 実行的）
- イラっとする AI の振る舞い
- 意思決定の委譲範囲 — どこまで AI に任せるか

**現在のフォーカス**
- 今取り組んでいるプロジェクト・目標
- 短期的な優先事項
- 長期的なキャリア/技術目標

**コミュニケーション**
- 好みのトーン（カジュアル、フォーマル、技術的）
- 説明のレベル（要点のみ or 背景も含めて）
- フィードバックの受け取り方

## Phase 3: メモリ保存

インタビュー完了後、領域ごとに個別の user メモリファイルを作成:

```
memory/
  user_dev_style.md        # 開発スタイル & 哲学
  user_tech_stack.md       # 技術スタック & ツール
  user_work_patterns.md    # 作業スタイル & スケジュール
  user_ai_collaboration.md # AI との協業スタイル
  user_current_focus.md    # 現在のフォーカス & 目標
  user_communication.md    # コミュニケーション好み
```

各ファイルのフォーマット:
```markdown
---
name: {descriptive name}
description: {one-line description for relevance matching}
type: user
---

{structured content from interview}
```

MEMORY.md にポインタを追記する。

## Phase 4: サマリ

保存したメモリの概要をユーザーに提示し、追加・修正がないか確認する。

## Rules

- 事実のみ保存。推測しない
- 短い回答を受けたら深追いしない — Daily Drip が埋める
- 既存メモリと重複する場合は更新で対応
- 10分以内に完了することを目指す
- ユーザーが「もういい」と言ったら即座に Phase 3 へ
