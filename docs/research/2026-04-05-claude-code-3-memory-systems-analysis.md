---
source: "You're using 1 of 3 memory systems in Claude Code (Article/Video by Artem)"
date: 2026-04-05
status: analyzed
---

## Source Summary

Claude Code の3層メモリシステムについての解説記事。

**主張**: CLAUDE.md だけではメモリ管理が不十分。Auto-memory（MEMORY.md + 個別ファイル）と Auto-dream（24h バックグラウンド統合）を組み合わせることで、使うほど賢くなる自己改善ループが構築できる。

**手法**:
1. CLAUDE.md — 手動管理のペルソナ・ルール・プリファレンス
2. Auto-memory — MEMORY.md インデックス + 個別メモリファイル（user/feedback/project/reference）
3. Auto-dream — 24時間ごとのバックグラウンド統合（メモリの統合・剪定・日付変換）
4. Retrospective スキル — セッション終了時にサブエージェントで会話を分析
5. Dynamic Dashboard — Obsidian で人生の各領域をダッシュボード化
6. Symlink to Obsidian — メモリファイルを Obsidian Bases で可視化

**根拠**: フライホイール効果 — 使うほどデータが蓄積しエージェント精度が向上。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | CLAUDE.md | Already | Progressive Disclosure + `<important if>` 条件付きタグ |
| 2 | Auto-memory | Already | 4タイプ、30+件運用中 |
| 3 | Auto-dream | Partial | `/improve`（AutoEvolve）が類似機能。組み込み auto-dream は有効化状況不明 |
| 4 | Retrospective | Already | `/analyze-tacit-knowledge` で3層抽出 |
| 5 | Dynamic Dashboard | Partial | Obsidian 連携あり、領域別ダッシュボードは未実装 |
| 6 | Obsidian Bases 可視化 | Partial | `sync-memory-to-vault.sh` で同期済み、Bases テーブルビュー未設定 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|-------------|---------------|--------|
| 1 | Progressive Disclosure CLAUDE.md | 「CLAUDE.md 肥大化」→ 既に解決済み | 強化不要 |
| 2 | Auto-memory 30+件 | 「メモリ陳腐化」→ `/improve` + `memory-archive.py` で対応済み | 強化不要 |
| 4 | `/analyze-tacit-knowledge` | 記事の retrospective はスキル更新も提案 → 既に `/improve` に分離 | 強化不要（分離設計の方が健全） |

## Integration Decisions

取り込み対象:
- [x] T1: Auto-dream 有効化確認・`/improve` との棲み分け記録
- [x] T2: Obsidian Bases メモリビュー作成
- [x] T3: Dynamic Dashboard テンプレート作成

## Plan

### T1: Auto-dream 有効化（S）
- Claude Code `/memory` で auto-dream を有効化（手動操作）
- `/improve` との棲み分けを MEMORY.md に記録

### T2: Obsidian Bases メモリビュー（S）
- `08-Agent-Memory/` 配下を name/type/description でテーブル表示する Bases 設定ノート作成

### T3: Dynamic Dashboard テンプレート（M）
- 領域別ダッシュボード（開発、コンテンツ、学習、健康）のテンプレートを Vault に作成
- Dataview/Bases クエリ付き
