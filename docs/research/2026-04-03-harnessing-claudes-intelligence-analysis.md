---
source: https://claude.com/blog/harnessing-claudes-intelligence
date: 2026-04-03
status: integrated
---

## Source Summary

Anthropic 公式ブログ（Lance Martin, 2026-04-02）。Claude アプリケーション設計の3パターンを提唱:

1. **Claude が既に理解しているツールを使う** — Bash + テキストエディタが万能基盤
2. **「何をやめられるか」を問う** — オーケストレーション・コンテキスト管理・永続化を Claude に委譲
3. **ハーネスで慎重に境界を設定** — キャッシュ最適化、宣言的ツール、セキュリティ境界

主要データ: BrowseComp code execution 45.3%→61.6%, Compaction Opus 4.6=84%, Memory folder 60.4%→67.2%

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Bash + テキストエディタ基盤 | N/A | CC 本体が実装 |
| 2 | Code execution オーケストレーション | Already | output-offload.py |
| 3 | Skills progressive disclosure | Already | YAML frontmatter + オンデマンド読込 |
| 4 | Context editing | Already | auto-compaction + context-compaction-policy.md |
| 5 | Subagents コンテキスト分離 | Already | subagent-delegation-guide.md + worktree |
| 6 | Compaction 永続化 | Already | 7層メモリ + pre-compact-save.js |
| 7 | Memory folder | Already | auto memory + checkpoint + HANDOFF.md |
| 8 | キャッシュヒット最大化 | Already | compact-instructions.md |
| 9 | 宣言的ツール境界 | Already | policy hooks + careful/freeze |
| 10 | Dead weight 定期除去 | Partial | Build to Delete 原則はあるが実行手順なし |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|------------|--------------|--------|
| 6 | Compaction fallback 3回→警告 | Opus 4.6 compaction 品質 84% | 閾値 3→4 に緩和 |
| 8 | キャッシュ破壊テーブル | ツール動的変更の記載なし | 行追加 |

## Integration Decisions

全項目を取り込み:

1. ✅ Dead weight scan protocol 新規作成 (`references/dead-weight-scan-protocol.md`)
2. ✅ `/improve` Step 5 陳腐化チェックに dead weight scan を統合
3. ✅ `compact-instructions.md` にツール動的変更の行を追加
4. ✅ `context-compaction-policy.md` の compaction 閾値を Opus 4.6 向けに緩和（3→4）
