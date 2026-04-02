# Resource Bounds（リソース制限定数一覧）

全 hook の閾値と定数を一元管理。変更時はこのファイルと対応する Rust ソースの両方を更新すること。
着想元: arXiv:2603.05344 (OpenDev) — "Lazy Loading and Bounded Growth"

## 検出系

| 定数 | 値 | ソース | 根拠 |
|---|---|---|---|
| Doom-Loop Window | 20 fingerprints | `post_any.rs` | OpenDev 準拠。件数ベース（時間ではなく） |
| Doom-Loop Threshold | 3 repeats | `post_any.rs` | OpenDev 準拠。false positive と検出速度のバランス |
| Doom-Loop Cooldown | 300s | `post_any.rs` | 同じ警告のスパム防止 |
| Exploration Spiral Threshold | 5 consecutive reads | `post_any.rs` | OpenDev 準拠 |
| Edit Loop Threshold | 3 edits / 10min | `post_edit.rs` | 同一ファイルの修正ループ検出 |
| Edit Loop Window | 10 min | `post_edit.rs` | 短すぎると正常な反復を誤検出 |
| Context Pressure Warning | 80% | `post_any.rs` | autocompact=80% に合わせる |
| Context Pressure Critical | 90% | `post_any.rs` | OpenDev 準拠 |
| Context Pressure Emergency | 95% | `post_any.rs` | OpenDev: 99% → 95% に前倒し |
| Context Pressure Stale | 60s | `post_any.rs` | statusline 更新間隔考慮 |

## 出力制御系

| 定数 | 値 | ソース | 根拠 |
|---|---|---|---|
| Output Offload Lines | 150 lines | `post_bash.rs` | OpenDev: 8000 文字。行数ベースで直感的に |
| Output Offload Chars | 6000 chars | `post_bash.rs` | トークン消費の実測値ベース |
| Artifact Index Max Lines | 1000 entries | `post_any.rs` | セッション内のファイル操作上限 |

## 安全弁系

| 定数 | 値 | ソース | 根拠 |
|---|---|---|---|
| Completion Gate Max Retries | 2 | `completion-gate.py` | 無限ループ防止 |
| Edit Counter Compact Suggestion | 30 / 50 edits | `post_edit.rs` | 経験値 |
| Max Recent Edits (loop buffer) | 20 entries | `post_edit.rs` | メモリ効率 |
| Golden Warning Cooldown | 300s | `post_edit.rs` | 同一警告のスパム防止 |
| Checkpoint Edit Threshold | 15 edits | `post_edit.rs` | 十分な変更量で自動保存 |
| Checkpoint Time Threshold | 30 min | `post_edit.rs` | 時間ベースの自動保存 |
| Checkpoint Cooldown | 5 min | `post_edit.rs` | 連続保存を防止 |
| Max Checkpoints | 5 files | `post_edit.rs` | ディスク使用量制限 |

## セッション管理系

| 定数 | 値 | ソース | 根拠 |
|---|---|---|---|
| Compaction Counter Warning | 3 compactions | `pre-compact-save.js` | Cursor 実証: 複数回圧縮で品質劣化。新セッション推奨 |
| Compaction Counter TTL | 2 hours | `pre-compact-save.js` | Session State TTL に合わせる |
| Session State TTL | 2 hours | 全 hook 共通 | セッション寿命の想定上限 |
| Search-First Session TTL | 2 hours | `pre_tool.rs` | セッション TTL に合わせる |

## AutoEvolve Failure Mode コード

| FM | 説明 | importance | 検出元 |
|---|---|---|---|
| FM-005 | Golden Principles 違反 | 0.8 | `post_edit.rs` |
| FM-006 | Permission denied | 0.9 | `events.rs` |
| FM-007 | Module not found | 0.5 | `events.rs` |
| FM-008 | TypeError/ReferenceError | 0.5 | `events.rs` |
| FM-009 | Memory/timeout/segfault | 1.0/0.6 | `events.rs` |
| FM-010 | Security/injection | 0.9 | `events.rs` |
| FM-011 | Doom-Loop detected | 0.7 | `post_any.rs` |
| FM-012 | Exploration Spiral | 0.5 | `post_any.rs` |
| FM-013 | Context Pressure ≥90% | 0.8 | `post_any.rs` |

## Error Recovery 6 分類

| カテゴリ | 検出パターン | リカバリ指示 |
|---|---|---|
| PermissionDenied | `permission denied`, `EACCES` | chmod / 代替パス提示 |
| FileNotFound | `No such file`, `ENOENT` | Glob で正しいパス検索 |
| EditMismatch | `file has changed`, `content mismatch` | Read → Edit リトライ |
| SyntaxError | `SyntaxError`, `parse error` | エラー行 Read → 修正 |
| RateLimit | `rate limit`, `429` | 別タスク切り替え |
| Timeout | `timeout`, `ETIMEDOUT` | コマンド分割 / background |

## False Claims Rate と反復劣化

> 出典: Claude Code v2.1.88 内部コメント (Capybara v4→v8)、"The Harness Wars Begin" (2026-04)

| バージョン | False Claims Rate | 備考 |
|-----------|------------------|------|
| Capybara v4 | 16.7% | ベースライン |
| Capybara v8 | 29-30% | 反復改善で悪化。構造的限界の可能性 |

**設計含意:**
- 長タスク（8+ ツール呼び出し）では false claims が累積する。verification 頻度を上げる
- completion-gate の MAX_RETRIES=2 はこの劣化を前提とした設計
- 「モデルが賢くなれば解決する」は危険な仮定。ハーネス側の検証を緩めない

## Compaction 後の Re-grounding チェックポイント

> 出典: Claude Code 内部アーキテクチャ分析 (2026-04-01)、"The Harness Wars Begin"

Auto-compaction は ~167K トークン（200K モデル）で発火し、20K トークンの summary に圧縮される。
**圧縮で失われるもの**: 中間推論チェーン、ツール出力の詳細、ファイル内容、意思決定の根拠。

**Re-grounding ルール:**
1. compaction 後に重要な判断をする前に、関連ファイルを **再読み込み** する（summary を信じない）
2. compaction 後に Plan がある場合、Plan ファイルを **再読み込み** して現在位置を確認する
3. 3回目の compaction で **新セッション推奨**（既存: Compaction Counter Warning = 3）
4. compaction 直後のレビュー verdict は信頼度を 1段階下げて扱う

## 1M コンテキスト利用時の調整

2026年3月時点で Claude Opus 4.6 / Sonnet 4.6 が 1M トークンコンテキストに対応。Opus 4.6 は MRCR v2 で 78.3%（長文検索タスクでフロンティアモデル最高スコア）を達成しており、長文コンテキストでの性能劣化が大幅に緩和されている。

**200K → 1M での閾値調整ガイドライン:**

| レベル | 200K 基準 | 1M 利用時の目安 | 備考 |
|--------|----------|---------------|------|
| Normal | 〜60% | 〜40% | 通常運用。閾値は比例ではなく保守的に設定 |
| Warning | 60-80% | 40-60% | Subagent 委譲を検討。compact 準備 |
| Critical | 80-90% | 60-75% | 新規ファイル読み込み抑制。compact 推奨 |
| Emergency | 90%+ | 75%+ | 即座に compact or セッション区切り |

**注意:**
- 1M でも Context Rot は発生する。閾値の緩和は「余裕が増える」であって「品質劣化がなくなる」ではない
- セッションを短く保つ原則は 1M でも変わらない（1セッション1タスク）
- 不要な場合は `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` で 200K に制限可能

出典: 逆瀬川 "Coding Agent Workflow 2026", Chroma Research "Context Rot", Morph "What Is Context Rot?"
