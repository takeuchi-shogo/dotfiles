---
name: decision
description: >
  設計・ワークフロー決定を構造化記録する軽量決定ジャーナル。対話で5項目を収集し、
  references/decision-journal.md に追記 + Obsidian Daily Note に同期。
  Triggers: '/decision', '決定記録', 'decision journal', '判断を記録', 'ADR lite'.
  Do NOT use for: アーキテクチャ決定記録（docs/adr/ に直接書く）、思考の壁打ち（use /think）。
origin: self
allowed-tools: Read, Edit, Write, AskUserQuestion, Bash(date *)
metadata:
  pattern: collector+writer
---

# /decision — 軽量決定ジャーナル

設計判断やワークフロー変更を構造化して記録する。

## Trigger

`/decision` または「この判断を記録したい」的な発言。

## Workflow

1. **収集**: AskUserQuestion で以下の5項目を対話で収集（一度に全部聞かず、自然な会話で）
   - **状況**: 何がきっかけか
   - **選択**: 何を選んだか
   - **根拠**: なぜそれを選んだか
   - **期待結果**: 何が起きると予想するか
   - **撤回条件**: 何が起きたらこの判断を見直すか（"What would make me change my mind later?" の問い）

2. **記録**: `references/decision-journal.md` の `## ログ` セクションの先頭にエントリを追記

   フォーマット:
   ```
   ### [YYYY-MM-DD] 決定タイトル

   - **状況**: ...
   - **選択**: ...
   - **根拠**: ...
   - **期待結果**: ...
   - **撤回条件**: ...
   - **実際結果**: _（後で記入: good / bad / mixed + 1行説明）_
   ```

3. **Obsidian 同期（オプション）**: `obsidian:obsidian-cli` または `obsidian:obsidian-markdown` skill 経由で当日の Daily Note に決定サマリを追記（`mcp__obsidian__*` 直呼びは禁止 — `references/wrapper-vs-raw-boundary.md` 参照）
   - 追記内容: `## Decisions\n- [タイトル] — 選択の1行要約`
   - Daily Note が存在しない場合はスキップ（エラーにしない）

## ルール

- 可逆な小さい決定（変数名、import 順序）は記録不要と案内
- 記録すべき: ツール選定、ワークフロー変更、設計パターン選択、スキル/hook の追加・削除
- 200語以内で簡潔に。冗長な記録は後で読まれない
- 日付は `date +%Y-%m-%d` で取得
