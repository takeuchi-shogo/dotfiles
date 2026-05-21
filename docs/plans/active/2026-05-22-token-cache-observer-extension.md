---
status: completed
size: M
created: 2026-05-22
completed: 2026-05-22
source: docs/research/2026-05-22-anthropic-engineers-token-savings-absorb-analysis.md (T9)
---

> **完了 (2026-05-22)**: 実装は `session_observer_parse.py` (_LOW_RATIO_THRESHOLD=0.30, _CACHE_CREATE_STREAK_LIMIT=3, ratio計算, warning発火) + `session_observer_fmt.py` (表示拡張) + `session-observer.py` (entry pointでreset呼出し) + `tests/runtime/test_session_observer_cache_ratio.py` で完了。`/review` で edge-case 修正 (pure-input no-op, 負の値クランプ) も統合済。

# Token Cache Observer Extension

session_observer に既存実装される `cache_read/cache_create` 抽出を活用し、ratio 監視と連続 cache_create 警告を追加する。新規 dashboard は作らず、既存 observer を強化する方針。

## Goal

cache hit ratio が低下した時に early warning を出す。`/clear` をいつ打つべきか、または model switch が頻繁すぎないかを観測可能にする。Codex 推奨 (2026-05-21 review) で「最初から別 dashboard を増やすのは過剰」のため、既存 observer 拡張に閉じる。

## Scope

### In scope
- `session_observer_parse.py` の cache_read/cache_create を集計し、ratio (= cache_read / (cache_read + cache_create + input)) を計算
- `session_observer_fmt.py` で ratio を統計表示に追加
- 連続 cache_create > 3 ターン or ratio < 30% で warning フィールドを追加
- 既存の出力構造を壊さないよう **追加** のみ (削除・rename は禁止)

### Out of scope
- 別 dashboard UI (HTML / web) を作る
- token-dashboard (nateherkai) のような外部ツール統合
- リアルタイム alerting (Slack 等) — 当面は session 終了時の post-hoc 表示でよい

## Files to Touch

| File | 変更内容 | 規模 |
|------|---------|------|
| `.config/claude/scripts/runtime/session_observer_parse.py` | cache ratio 計算ロジック追加 (line 121-122 周辺) | S |
| `.config/claude/scripts/runtime/session_observer_fmt.py` | ratio + warning フィールド表示 (line 99-100 周辺) | S |
| `.config/claude/references/resource-bounds.md` | Cache hit ratio threshold (30%) を「検出系」テーブルに追加 | XS |
| 新規 test: `tests/runtime/test_session_observer_cache_ratio.py` | ratio 計算と warning 発火条件のユニットテスト | S |

## Validation

- [ ] 既存 session_observer の出力フォーマットが壊れていない (snapshot test)
- [ ] cache_read=0, cache_create=0 のセッション (新規 cold start) で divide-by-zero しない
- [ ] ratio = 80%+ なら warning なし、< 30% かつ連続 cache_create > 3 で warning フィールド出力
- [ ] resource-bounds.md に新規閾値が記載され、`task validate-configs` が通る

## Decision Log

### Why not separate dashboard

Codex review (2026-05-21): 「最初から別 dashboard を増やすのは過剰。既存 observer を活かして比率・連続 cache_create 警告まで作るなら価値がある」。新規 UI は YAGNI、まず metric を観測可能にするだけで運用可能性を判定する。

### Why ratio threshold = 30%

ベースラインデータがないため初期値は **暫定値**。記事著者の主張「cache read が高ければ winning」を機械的に判定するには、まず 30% を下限としてアラートを出し、実測で調整する。閾値ロジックは `resource-bounds.md` に集約して mechanism 化する。

### Retreat criteria

- 2 週間運用して warning が一度も発火しない → threshold が緩すぎる、または cache 状況が常に健全。閾値を 50% に引き上げて再評価
- 毎セッション warning が出る → false positive 多すぎ、metric 設計から見直し
- 既存 observer の出力が乱れる → revert (`git revert`) で即座に rollback

## References

- 出典: `docs/research/2026-05-22-anthropic-engineers-token-savings-absorb-analysis.md` (T9)
- Codex review: 2026-05-21 (task-mpg0cxic-z5lvrk) — "session_observer ベースで cache read/create 比率の軽量レポート化。新規 dashboard は後回し"
- 既存実装の確認:
  - `session_observer_parse.py:121-122` で cache_read/cache_create 抽出
  - `session_observer_fmt.py:99-100` で表示中
- 関連 reference: `references/resource-bounds.md § Prompt Cache TTL 三層`
