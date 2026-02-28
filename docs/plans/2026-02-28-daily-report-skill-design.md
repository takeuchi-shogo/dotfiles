# Daily Report Skill 設計書

## 概要

Claude Code のスラッシュコマンド `/daily-report` で、1日の全セッションを横断的にまとめた日報を自動生成するスキル。

## 要件

- 全プロジェクト横断でセッションを集約
- 同じテーマの複数セッションを「やったこと」単位でまとめる
- 日本語で出力
- `~/daily-reports/YYYY-MM-DD.md` に保存

## データソース

```
~/.claude/projects/*/sessions-index.json  ← 軽量インデックス（まずここから）
~/.claude/projects/*/*.jsonl              ← 詳細（必要に応じて）
```

### sessions-index.json のエントリ構造

```json
{
  "sessionId": "uuid",
  "fullPath": "/path/to/*.jsonl",
  "firstPrompt": "最初のユーザーメッセージ",
  "summary": "セッションのサマリー",
  "messageCount": 7,
  "created": "2026-01-04T04:03:13.201Z",
  "modified": "2026-01-04T04:04:54.863Z",
  "gitBranch": "master",
  "projectPath": "/Users/.../project-name"
}
```

### JSONL のユーザーメッセージ構造

```json
{
  "type": "user",
  "message": { "role": "user", "content": "メッセージ本文" },
  "timestamp": "2026-02-12T14:23:25.511Z",
  "sessionId": "uuid",
  "gitBranch": "master"
}
```

## 処理フロー

```
1. 引数パース: 日付指定 or デフォルト（今日）
2. セッション収集: ~/.claude/projects/*/sessions-index.json を全スキャン
3. 日付フィルタ: created/modified が対象日に該当するエントリを抽出
4. JSONL 詳細取得: 該当セッションの JSONL からユーザーメッセージを抽出
   - 各セッション先頭10メッセージ程度に制限（トークン節約）
5. グルーピング: projectPath + gitBranch で関連セッションをまとめる
6. サマリー生成: Claude がストーリー単位で日本語サマリーを生成
7. ファイル出力: ~/daily-reports/YYYY-MM-DD.md に保存
```

## 関連セッションの紐付けロジック

1. **同じ projectPath + 同じ gitBranch** → 同じ作業としてグルーピング
2. **summary / firstPrompt の内容類似** → Claude の判断で統合
3. グループごとに時系列で並べ、作業の流れを再構成

## コマンドインターフェース

```
/daily-report           → 今日の日報を生成
/daily-report yesterday → 昨日の日報を生成
/daily-report 2026-02-25 → 指定日の日報を生成
```

## 出力フォーマット

```markdown
# 日報 - YYYY-MM-DD

## プロジェクト別

### <プロジェクト名>

#### <やったこと 1>（ブランチ: feature/xxx）
- セッション1 (10:00-10:45): 要件整理、設計ブレスト
- セッション2 (14:00-15:30): 実装完了、テスト追加
- 成果: ○○機能が完成

#### <やったこと 2>
- セッション3 (16:00-16:30): バグ調査→修正
- 成果: APIタイムアウト問題を解決

### <別プロジェクト名>
...

## 今日のまとめ
- N セッション / N プロジェクト
- 主な成果: ...
```

## ファイル構成

```
.config/claude/skills/daily-report/SKILL.md   ← スキル本体（1ファイル）
```

## 技術的考慮事項

- sessions-index.json は内部フォーマットのため、将来変更される可能性がある
- JSONL の読み取りはトークンを消費するため、メッセージ数を制限する
- セッション数が多い日は jq + head でプリフィルタする

---

# Daily Report Skill 実装計画

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** `/daily-report` スラッシュコマンドで全プロジェクト横断の日報を生成するスキルを作成する

**Architecture:** スキルファイル（SKILL.md）1つのみ。Bash で sessions-index.json を収集・フィルタし、JSONL からユーザーメッセージを抽出。Claude がサマリーを生成して Markdown ファイルに保存する。

**Tech Stack:** Claude Code Skill (Markdown), Bash (jq), Write tool

---

### Task 1: SKILL.md の作成

**Files:**
- Create: `.config/claude/skills/daily-report/SKILL.md`

**Step 1: スキルファイルを作成**

SKILL.md に以下を含める:
- frontmatter（name, description）
- 処理フローの指示（セッション収集 → フィルタ → JSONL 読み取り → グルーピング → サマリー生成 → ファイル出力）
- 出力フォーマットのテンプレート
- 引数の解釈ルール（today/yesterday/YYYY-MM-DD）

**Step 2: 動作確認**

Run: `/daily-report` をこのセッション内で実行して動作確認
Expected: `~/daily-reports/YYYY-MM-DD.md` が生成される

**Step 3: コミット**

```bash
git add .config/claude/skills/daily-report/SKILL.md
git commit -m "✨ feat: add daily-report skill for cross-project session summary"
```

### Task 2: ~/daily-reports ディレクトリの初期化

**Files:**
- Create: `~/daily-reports/.gitkeep`（任意）

**Step 1: ディレクトリ作成**

スキル内で `~/daily-reports/` が存在しなければ自動作成する（SKILL.md の指示に含める）
