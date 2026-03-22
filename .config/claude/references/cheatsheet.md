# Claude Code クイックリファレンス

## スラッシュコマンド一覧

### 主要コマンド

| コマンド | 説明 | 使用例 |
|---|---|---|
| `/commit` | conventional commit + 絵文字でコミット作成 | `/commit`, `/commit --amend` |
| `/review` | コード変更のレビュー（並列レビューアー自動選択） | `/review`, `/review main` |
| `/rpi` | Research → Plan → Implement の3フェーズ実行 | `/rpi 認証機能を追加` |
| `/spec` | 仕様書を生成（曖昧な要件を構造化） | `/spec ユーザー管理API` |
| `/spike` | プロトタイプで技術検証 | `/spike WebSocket 接続` |
| `/epd` | EPD 統合ワークフロー（不確実性が高い場合） | `/epd 新規決済連携` |
| `/checkpoint` | 作業状態を手動保存（中断・再開用） | `/checkpoint` |
| `/improve` | AutoEvolve 改善サイクルをオンデマンド実行 | `/improve` |

### リサーチ系

| コマンド | 説明 | 使用例 |
|---|---|---|
| `/research` | 構造的なリサーチ実行 | `/research OAuth2 ベストプラクティス` |
| `/absorb` | 外部知見をメモリ・設定に統合 | `/absorb <URL>` |
| `/check-health` | ドキュメント鮮度・参照整合性を確認 | `/check-health` |
| `/check-context` | コンテキストウィンドウ使用量を確認 | `/check-context` |

### セッション管理

| コマンド | 説明 | 使用例 |
|---|---|---|
| `/timekeeper` | 作業時間の管理・計測 | `/timekeeper` |

### ユーティリティ

| コマンド | 説明 | 使用例 |
|---|---|---|
| `/persona` | ペルソナ切り替え | `/persona senior-architect` |
| `/onboarding` | 初期プロファイル設定 | `/onboarding` |
| `/profile-drip` | 1日1問でプロファイルを漸進的に構築 | `/profile-drip` |
| `/security-review` | セキュリティ観点のコードレビュー | `/security-review` |
| `/autonomous` | 自律実行モード（worktree 並列） | `/autonomous タスクリスト` |
| `/recall` | メモリから過去の知見を検索 | `/recall hook 設計` |
| `/pull-request` | PR 作成 | `/pull-request` |

---

## キーボードショートカット

| キー | 動作 |
|---|---|
| `Ctrl+C` | 実行中のツール呼び出しを中断 |
| `Ctrl+D` | セッションを終了 |
| `Esc` | 入力中のテキストをクリア |
| `Tab` | ファイルパス・コマンドの自動補完 |
| `/` | スラッシュコマンド入力を開始 |
| `↑` / `↓` | 入力履歴のナビゲーション |

---

## 権限モード

| モード | 動作 | 用途 |
|---|---|---|
| **Plan** | 読み取り専用。ファイル変更不可 | 計画立案・調査フェーズ |
| **Default** | 各ツール呼び出し時にユーザー確認 | 通常作業（デフォルト） |
| **AcceptEdits** | ファイル編集（Edit/Write）は自動承認 | 信頼できるコード変更作業 |
| **Auto** | 全ツール呼び出しを自動承認 | 反復的な大量作業 |
| **BypassPermissions** | サンドボックス内で全操作を自動承認 | CI/CD パイプライン向け |

> 切り替え: セッション開始時に `--dangerously-skip-permissions` (BypassPermissions) 等のフラグで指定

---

## コンテキスト管理

| 状況 | 閾値 | 対応 |
|---|---|---|
| 通常 | ~70% | そのまま作業継続 |
| 警告 | 80% | `/compact` の実行を検討 |
| 危険 | 90% | `/compact` を実行、または新セッション開始 |
| 緊急 | 95% | 即座に `/compact` 実行。未保存作業を `/checkpoint` で保存 |

### 自動保護機構

- **PreCompact hook**: `/compact` 実行前に `session-save` + `half-clone` を自動実行
- **Compaction 回数警告**: 3回以上の圧縮で品質劣化 → 新セッション推奨
- **Checkpoint 自動保存**: 15編集 or 30分経過で自動トリガー

### コマンド

```
/check-context    # 現在の使用量・セッション状態を確認
/compact          # コンテキストを圧縮
/checkpoint       # 作業状態を手動保存
```

---

## モデル選択マトリクス

| タスク種別 | 推奨モデル | 理由 |
|---|---|---|
| 複雑な設計・推論 | Opus | 深い思考が必要 |
| 日常的なコーディング | Sonnet | 速度とコストのバランス |
| 簡単な質問・補完 | Haiku | 高速・低コスト |
| 大規模コードベース分析 | Gemini CLI | 1M コンテキスト |
| 設計レビュー・リスク分析 | Codex CLI | 深い推論 (reasoning effort: high/xhigh) |

### 現在の設定

```jsonc
// settings.json
"model": "opus[1m]"        // メインモデル
"effortLevel": "high"      // 推論努力レベル
"language": "japanese"      // 応答言語
```

### マルチモデル委譲

```
Claude Code (Opus) ── サブエージェント委譲
    ├── codex exec "..."   # 設計・推論・リスク分析
    └── gemini "..."       # 1M 分析・リサーチ・マルチモーダル
```

---

## よく使うスキル TOP 10

| # | スキル | 説明 | トリガー |
|---|---|---|---|
| 1 | `/commit` | conventional commit + 絵文字でコミット作成 | 手動 |
| 2 | `/review` | 変更規模に応じたレビューアー自動選択・並列実行 | 手動 / hook |
| 3 | `/rpi` | Research → Plan → Implement の体系的実行 | 手動 |
| 4 | `/spec` | 仕様書生成（曖昧 → 構造化） | 手動 |
| 5 | `/spike` | プロトタイプ作成・技術検証 | 手動 |
| 6 | `/epd` | EPD 統合ワークフロー | 手動 |
| 7 | `/absorb` | 外部知見（論文・記事）をメモリに統合 | 手動 |
| 8 | `/checkpoint` | 作業状態の保存・復元 | 手動 / 自動 |
| 9 | `search-first` | 実装前に既存解決策を検索 | 自動（hook） |
| 10 | `/improve` | AutoEvolve 改善サイクル | 手動 |

---

## トラブルシューティング

| 問題 | 原因 | 対処 |
|---|---|---|
| コンテキスト溢れ | トークン上限に接近 | `/compact` 実行。3回超なら新セッション開始 |
| hook が発火しない | 正規表現 or パス不一致 | `/hook-debugger` で診断。日本語は `\b` ではなく `(?=[^a-zA-Z0-9]\|$)` を使用 |
| MCP 接続失敗 | サーバー未起動 or 設定不備 | `settings.json` の `enabledMcpjsonServers` を確認、サーバー再起動 |
| ビルド/テストエラー | コード起因 | debugger エージェントに委譲。生ログ・スタックトレースを直接分析 |
| 編集ループ | 同一ファイルを繰り返し修正 | `stagnation-detector` が自動検出（3編集/10分で警告） |
| commit 失敗 | pre-commit hook エラー | hook の指摘を修正し、**新規コミットを作成**（`--amend` しない） |
| サブエージェント暴走 | コンテキスト不足 | `subagent-monitor` が自動監視。`/checkpoint` 後に再委譲 |
| 権限拒否 | deny リスト該当 | `settings.json` の `permissions.deny` を確認。`rm -rf`, `sudo` 等は常に拒否 |

### 安全弁（自動保護）

| 検出器 | 閾値 | 動作 |
|---|---|---|
| Doom-Loop | 20指紋中3回繰り返し | 警告 + 再プラン提案 |
| Exploration Spiral | 5回連続 Read（Edit/Write なし） | 行動を促す通知 |
| Edit Loop | 同一ファイル3編集/10分 | 警告 |
| File Proliferation Guard | Write 時 | 不要なファイル生成を防止 |
| Completion Gate | Stop 時 | 完了条件を検証 |
