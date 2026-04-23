---
status: active
last_reviewed: 2026-04-23
---

# Harness Engineering 導入設計

## 概要

OpenAI のハーネスエンジニアリング記事から5つの改善を dotfiles に取り入れる。
全て Hook 自動型（Approach 2: 検出は Hook、実行はサブエージェント）で実装。

## 全体アーキテクチャ

```
hooks (軽量検出)              agents (重い実行)           references (知識)
─────────────────         ─────────────────         ─────────────────
doc-garden-check.py   →   doc-gardener agent    ←   (既存 docs)
error-to-codex.py(拡張)   (hook内で完結)         ←   error-fix-guides.md
golden-check.py       →   golden-cleanup agent  ←   golden-principles.md
(手動起動)            →   ui-observer agent     ←   (webapp-testing skill)
plan-lifecycle.py         (hook内で完結)             (docs/plans/ 構造)
```

## 新規作成ファイル

| 種別      | ファイル                                   | トリガー                       |
| --------- | ------------------------------------------ | ------------------------------ |
| Hook      | `scripts/doc-garden-check.py`              | SessionStart                   |
| Hook      | `scripts/golden-check.py`                  | PostToolUse (Edit\|Write)      |
| Hook      | `scripts/plan-lifecycle.py`                | PostToolUse (Bash: git commit) |
| Agent     | `agents/doc-gardener.md`                   | hook 提案時に手動起動          |
| Agent     | `agents/golden-cleanup.md`                 | hook 提案時に手動起動          |
| Agent     | `agents/ui-observer.md`                    | 手動起動                       |
| Reference | `references/golden-principles.md`          | golden-check.py が参照         |
| Reference | `references/error-fix-guides.md`           | error-to-codex.py が参照       |
| Directory | `docs/plans/{active,completed,tech-debt}/` | plan-lifecycle.py が管理       |

## 既存ファイルの変更

- `scripts/error-to-codex.py` → error-fix-guides.md の修正指示を注入
- `settings.json` → hooks に新規 hook 追加

---

## 1. doc-gardening（ドキュメント鮮度管理）

### Hook: `scripts/doc-garden-check.py` (SessionStart)

3種の判定を軽量に実行:

- **A) git diff ベース** (~10ms): 直近10コミットで変更されたファイルに対応するドキュメントの最終更新日を比較
- **B) タイムスタンプベース** (~5ms): references/, rules/ 配下で 30日以上更新なしのファイルを検出
- **C) 内容マッチング** (~50ms): ドキュメント内のファイルパス参照が実際に存在するか検証

### Agent: `agents/doc-gardener.md`

- サブエージェントとして起動し、陳腐化ドキュメントを読み込み→修正案を生成
- memory: user / tools: Read, Write, Edit, Bash, Glob, Grep

---

## 2. エラーメッセージへの修正指示注入

### 既存 `scripts/error-to-codex.py` の拡張

- 現状: エラー検出 → 「codex-debugger を使えます」と提案
- 拡張: `references/error-fix-guides.md` を参照し、パターンに合致するエラーには具体的な修正手順を注入

### Reference: `references/error-fix-guides.md`

エラーパターン → 原因 → 修正手順のマッピング。hook は起動時に一度パースしてマッチング時に注入。

---

## 3. ゴールデンプリンシプル + 自動クリーンアップ

### Reference: `references/golden-principles.md`

自動検証可能な具体パターンを列挙（GP-001〜）。rules/ はエージェント向け指示として別管理。

### Hook: `scripts/golden-check.py` (PostToolUse: Edit|Write)

変更されたファイルの diff を取得し、golden-principles.md のパターンと軽量マッチング。逸脱検出時に警告。

### Agent: `agents/golden-cleanup.md`

コードベース全体をスキャンし、逸脱を一覧化。修正案を提示（自動修正はユーザー確認後）。

---

## 4. フルオブザーバビリティ（UI Observer）

### Agent: `agents/ui-observer.md`

- Playwright MCP をサブエージェント内に閉じ込め、メインコンテキストを消費しない
- tools: Read, Bash, Glob, Grep + Playwright MCP tools
- webapp-testing スキルを skills: で読み込み
- triage-router にルーティングルールを追加

Hook は不要。手動起動のみ。

---

## 5. 計画のファーストクラスアーティファクト管理

### ディレクトリ構造

```
docs/plans/
├── active/          ← 現在進行中
├── completed/       ← 完了済み
├── tech-debt/       ← 技術的負債
├── (既存5ファイルはそのまま残す)
```

### Hook: `scripts/plan-lifecycle.py` (PostToolUse: Bash)

git commit メッセージに計画ファイル名への参照があるかチェック。
active/ 内の計画に関連コミットが溜まったら completed/ への移動を推奨。

---

## 決定事項

- 実行モデル: Hook 自動型（Approach 2: 検出は Hook、実行はサブエージェント）
- doc-gardening 判定: A/B/C 全部入れて運用で調整
- ゴールデンプリンシプル: rules/ とは別管理（golden-principles.md）
- 計画管理: docs/plans/ にサブディレクトリ追加（既存ファイルは移動しない）
- Playwright: サブエージェント限定でコンテキスト消費を防止
