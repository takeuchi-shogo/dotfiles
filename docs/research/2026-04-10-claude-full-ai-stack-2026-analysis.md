---
source: "cyrilXBT blog post \"How to Build a Full AI Stack Using Only Claude in 2026 (Full Course)\""
date: 2026-04-10
status: integrated
---

# How to Build a Full AI Stack Using Only Claude in 2026 — Absorb Analysis

> Analyzed: 2026-04-10
> Source: cyrilXBT blog post "How to Build a Full AI Stack Using Only Claude in 2026 (Full Course)"
> Source type: Blog post / content creator article

## TL;DR

記事は「Claude を単一ツールとして使い切る 6 層スタック（Coding/Research/Writing/Automation/Knowledge/Product）」を提唱。
このセットアップは既に 85-90% カバー済み。核心未回収の 1 点のみ統合: **セッション終了時の Obsidian 自動同期 hook**。

## 記事の主張（構造化抽出）

- **Thesis**: 2026年はツール数ではなく1つのツールの深掘りが差を生む
- **6 Layers**: L1 Claude Code + CLAUDE.md / L2 Web Search daily research / L3 Claude Projects / L4 Multi-agent / L5 Obsidian integration / L6 Vercel+Supabase+Stripe
- **Evidence**: 個人 builder の週末プロダクト実装
- **Assumptions**: 個人 builder / content creator 向け。API アクセスと自動化基盤を前提

## ギャップ分析（Phase 2 + 2.5 修正後）

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Claude Code + CLAUDE.md | Already | `.config/claude/CLAUDE.md` + references/ 30+、Progressive Disclosure、Codex Review Gate |
| 2 | Web Search 日次リサーチ | Partial（再定義） | `/research` + `auto-morning-briefing.sh` あり。不足は Web Search でなく cron 可観測性と失敗時運用 |
| 3 | 永続コンテキスト | Already | 7層メモリ、agent-memory/、continuous-learning |
| 4 | マルチエージェント | Already (強化可能) | cmux Worker + /dispatch + 30+ エージェント。記事主眼の Research→Draft→QC 固定パイプラインの明文化は可能 |
| 5 | Obsidian ナレッジ | **Partial（核心未回収→統合完了）** | 部品は揃っていたが Stop hook で sync-memory-to-vault.sh が未発火だった |
| 6 | Product Building (L6) | N/A | dotfiles はメタハーネスリポジトリ。スコープ外 |

## Phase 2.5 主要批評の記録

### Codex 指摘
- L2 Partial は厳しすぎ。不足は「Web Search 不足」でなく「cron 実行の可観測性と失敗時運用」
- L4 エージェント数 ≠ 記事主眼「Research→Draft→QC 固定パイプラインの定期実行」
- L5 Obsidian 連携があっても「終了時自動要約 hook 未検証」＝価値の中心が未回収
- **最大の示唆**: 記事から学ぶべきは単一ツール信仰でなく「定時実行／成果物固定／QC を挟む」設計

### Gemini 指摘
- cyrilXBT は content creator。infrastructure builder ではない
- 単一ツール戦略はプロトタイプには真、ハーネス構築では破綻
- 見落とされたトレードオフ: API 変更、Rate limit、Context saturation、状態管理
- このセットアップは記事の先を行っている（Composability + Agent Mesh）

## Triage 結果（Phase 3）

選択: **P2 のみ** — Stop hook に Obsidian sync エントリ追加
- P1（Research→Draft→QC パイプラインの playbook 化）はスキップ — 既存 skills で実質カバー済み
- P3（反論メモ）はスキップ — 記事の情報密度が低く見合わない

## 実施内容（Phase 5）

### 変更

`/Users/takeuchishougo/dotfiles/.config/claude/settings.json` の Stop hook 配列に 1 エントリ追加（session-trace-store.py の後、session-stats.sh の前）:

```json
{
  "type": "command",
  "command": "OBSIDIAN_VAULT_PATH=\"${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}\" bash $HOME/.claude/scripts/runtime/sync-memory-to-vault.sh >> /tmp/obsidian-sync.log 2>&1 &",
  "timeout": 5
}
```

### 根本原因

`session-learner.py` が Stop hook で agent-memory/ に Python file I/O で書き込むが、これは PostToolUse hook（Write/Edit 監視）をトリガーしない。そして Stop hook には sync-memory-to-vault.sh が含まれていなかった。結果として、学習成果が Vault に流れるには cron 待ち or Claude が直接メモリファイルを編集したときだけだった。

### 検証結果

- JSON 構文 OK
- task validate-configs OK
- task validate-symlinks OK
- Dry-run: **18 ファイルのバックログを検出**（hook 欠落の物証）

### 設計ポイント

- バックグラウンド実行 (`&`) でセッション終了を遅延させない
- エラーログは `/tmp/obsidian-sync.log`
- OBSIDIAN_VAULT_PATH のフォールバック値
- mtime 比較で二重書き込みなし（PostToolUse と共存可能）

## 取り込み除外（記録）

| 項目 | 理由 |
|------|------|
| P1: Research→Draft→QC playbook | 既存 `/research` `/dispatch` `/epd` で実質カバー。playbook 重複リスク |
| P3: 反論メモ | 記事の情報密度が低く、単独メモを作るほどの価値なし。本レポート内に記録 |
| L6: Vercel/Supabase/Stripe | dotfiles はハーネスレイヤーでスコープ外 |

## Chaining

- 実セッション検証: 次回セッション終了時に `/tmp/obsidian-sync.log` と Vault の `08-Agent-Memory/` mtime を確認
- 関連記事: `docs/research/2026-03-25-cursor-claude-full-course-analysis.md`, `docs/research/2026-03-25-claude-2026-everything-guide-analysis.md`
