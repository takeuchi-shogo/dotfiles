---
source: himanshustwts "Claude Code's Memory System Explained" (X/Twitter thread, 2026-04-01)
date: 2026-04-02
status: integrated
---

## Source Summary

**主張**: Claude Code のメモリは5層アーキテクチャで、モデルにメモリ管理を任せきりにしない厳格なハーネス設計がある。フォーマット強制・Sonnet フィルタ・サンドボックス・削除ポリシーすべてがハーネス側で制御されている。

**手法**:
1. 5層メモリ（会話履歴 / Session Memory / CLAUDE.md / Auto-memory / Team Memory）
2. Forked subagent によるバックグラウンド抽出（prompt cache 共有、5ターン制限、サンドボックス）
3. `hasMemoryWritesSince()` による重複防止（メイン/バックグラウンド相互排他）
4. MEMORY.md をインデックスとして常時ロード（200行/25KB上限）
5. Sonnet による関連性フィルタリング（frontmatter description のみで判定、top 5選択）
6. 4メモリタイプ（user/feedback/project/reference）
7. 1日超のメモリに staleness warning 自動注入
8. AutoDream 統合（24h + 5セッション、4フェーズ: Read→Gather→Merge→Prune）
9. メモリパスセキュリティ（グローバル設定のみ、traversal攻撃防止）

**根拠**: instructkr/claude-code npm ソースマップからの逆コンパイル分析

**前提条件**: Claude Code CLI の内部実装。ユーザーが直接変更できるのは description 品質と MEMORY.md サイズのみ。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | 5層メモリ（Session Memory, AutoDream） | N/A | 内部実装。tengu フラグで制御、ユーザー設定不可 |
| 2 | Forked subagent でのバックグラウンド抽出 | N/A | 内部動作 |
| 3 | `hasMemoryWritesSince()` 重複防止 | N/A | 内部動作 |
| 4 | メモリパスセキュリティ | N/A | 内部動作 |
| 5 | Staleness warning（1日超で注入） | N/A | 内部動作 |
| 6 | Sonnet フィルタ（description のみで判定、top 5） | Partial | 仕組みは内部だが description の書き方が検索精度に直結 |
| 7 | MEMORY.md 200行/25KB 上限 | Partial | 上限認識済み。現在157行で余裕あり |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す知見 | 強化案 |
|---|-------------|--------------|--------|
| A1 | 4メモリタイプ + frontmatter | description が Sonnet の唯一の判断材料 | 全ファイルの description 品質監査 |
| A2 | MEMORY.md インデックス運用 | 常時ロード = 全ターンでトークン消費 | 行数監査 + 圧縮機会の特定 |
| A3 | 04-01 内部アーキテクチャ分析 | Sonnet フィルタ詳細 + AutoDream 4フェーズが新情報 | 既存レポートに追記 |

## Integration Decisions

全項目を選択して統合:

1. **メモリ description 品質監査** — 52ファイル中5件を改善
   - `telos_mission.md`: 「ユーザーのミッション」→「個人ミッション声明 — AI協業×生産性最大化。/morning, /timekeeper で参照」
   - `telos_strategies.md`: 「目標達成の戦略」→「TELOS 戦術層 — Scaffolding>Model, Build to Delete, KISS。日次判断基準」
   - `reference_skillsmp.md`: 「マーケットプレイス」→「外部スキル検索・採用の起点。ベンチマーク、インスパイア源」
   - `feedback_absorb_already_deepdive.md`: より具体的な表現に改善
   - `feedback_memory_style.md`: トークン効率の観点を明示
2. **MEMORY.md サイズ確認** — 157行/200行、圧縮不要
3. **分析レポート追記** — §15.5〜15.8 を既存レポートに追加、メモリファイルに Phase 4 追記

## Key Takeaway

記事の多くは Claude Code の内部実装であり、ユーザーが直接変更できない。
唯一のアクショナブルな知見は **「description が Sonnet による検索の唯一の判断材料」** という点。
これに基づき、全52メモリファイルの description 品質を監査し、5件を改善した。
