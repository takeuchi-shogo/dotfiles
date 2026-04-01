---
source: "I read every line of Claude Code's memory source" (Mubit blog)
date: 2026-04-02
status: integrated
---

## Source Summary

Claude Code のメモリシステム内部実装（22ソースファイル）の詳細分析記事。

**主張**: FS ベースのメモリシステムは洗練されているが、200行インデックス上限・PIDロック・非決定論的リコール・サイレント失敗など構造的限界がある。

**手法/知見**:
1. MEMORY.md: 200行/25KB ハードキャップ（`MAX_ENTRYPOINT_LINES`, `MAX_ENTRYPOINT_BYTES`）
2. メモリファイル: 200個キャップ（`MAX_MEMORY_FILES`）
3. セッション当たり 26K トークン（200K の 13%）をメモリに消費
4. pendingContext 単一スロット: rapid message で中間コンテキスト消失
5. PID+mtime ロック: flock() 不使用、60分 stale window
6. Sonnet 側クエリ: セマンティックリコール、失敗時 `return []`（サイレント）
7. メモリ鮮度: 0-1日は警告なし、検証は助言のみ
8. sanitizePath 衝突: プロジェクト間メモリ混入の可能性
9. ensureMemoryDirExists: EACCES/ENOSPC をサイレントに飲む
10. 抽出エージェント: Sonnet、createAutoMemCanUseTool で権限制限

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | pendingContext 単一スロット | N/A | 内部実装の制約。ユーザー側で対処不可 |
| 2 | PID+mtime ロック競合 | N/A | 同上 |
| 3 | sanitizePath 衝突 | N/A | dotfiles 単一リポジトリでリスクなし |
| 4 | ensureMemoryDirExists サイレント失敗 | N/A | OS レベルの監視領域 |
| 5 | Sonnet リコール非決定論的失敗 | Partial | 検知手段なし。外部から対処困難 |
| 6 | メモリ鮮度 0-1日警告なし | Already | staleness-detector.py + check-health で対応済み |

### Already 強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|------------|-------------|--------|------|
| A | memory-archive.py (500行閾値) | ハード上限200行。500行は到達不能 | 閾値180行に変更 | 強化実施 |
| B | memory-status (行数チェック) | バイトサイズ25KB未監視 | バイトサイズチェック追加 | 強化実施 |
| C | feedback_memory_style.md | 26K tokens/session。18KBで安全圏 | 現状で対策済み | 強化不要 |
| D | context-compaction-policy.md | メモリトークンコスト意識 | feedback_instruction_cost.md でカバー | 強化不要 |
| E | staleness-detector.py | メモリファイル自体の鮮度未対象 | 30日未更新ファイル検出追加 | 強化実施 |

## Integration Decisions

取り込み: A, B, E（全て S 規模）
スキップ: 1-4（N/A）, 5（外部から対処困難）, C, D（強化不要）

## Changes Made

1. `memory-archive.py`: MEMORY_THRESHOLD 500→180, MEMORY_BYTES_THRESHOLD 23000 追加, ARCHIVE_KEEP_LINES 200→150
2. `memory-status/SKILL.md`: Capacity Check セクション（バイトサイズ表示）追加, Stale Memory Files セクション（30日未更新検出）追加, Health Check テーブル更新
