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
