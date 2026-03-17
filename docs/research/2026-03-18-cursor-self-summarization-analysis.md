---
source: https://cursor.com/blog/self-summarization
date: 2026-03-18
status: integrated
---

## Source Summary

Cursor が RL ベースの「self-summarization」手法を発表。モデル自身がコンテキスト圧縮時に何を残すべきかを学習する。
プロンプトベースの圧縮（5,000+ トークン）と比較して、~1,000 トークンの簡潔な要約で 50% エラー削減を実証。
170 ターン、100K+ トークンのタスク（make-doom-for-mips）を1セッションで完走。

**核心的知見**: 短く構造化された要約が長い指示付き要約より優れる。

## Gap Analysis

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | コンテキスト圧縮ガイダンス | Already | `pre-compact-save.js` で 3 段階ガイダンス |
| 2 | プラン状態の引き継ぎ | Already | アクティブプラン検出+進捗出力 |
| 3 | 固定閾値トリガー | Already | autocompact=80%, Context Pressure 80/90/95% |
| 4 | 圧縮回数の追跡 | **Gap** | edit counter のみ、compaction counter なし |
| 5 | 簡潔さの原則 | **Partial** | ガイダンスはあるが簡潔さの明示的指針なし |
| 6 | Offloaded outputs 退避 | Already | `output-offload.py` |
| 7 | Edit/Doom loop 検出 | Already | 記事を超える対策 |
| 8 | セッション分割 | Already | `/autonomous` + `/checkpoint` |
| 9 | RL 自己要約学習 | N/A | Cursor 社内パイプライン固有 |

## Integration Decisions

- [Gap] 圧縮回数カウンター → 採用。`pre-compact-save.js` に実装
- [Partial] 簡潔さ原則 → 採用。Brevity Principle セクションとして追加

## Changes Made

1. `scripts/runtime/pre-compact-save.js`:
   - compaction counter 追加（セッション TTL 2h でリセット）
   - `compaction_number` を state に追加
   - Brevity Principle ガイダンス追加（~1,000 トークン目標）
   - 3 回以上の圧縮で新セッション移行を推奨する警告追加
2. `references/resource-bounds.md`:
   - Compaction Counter Warning / TTL 定数を追記
