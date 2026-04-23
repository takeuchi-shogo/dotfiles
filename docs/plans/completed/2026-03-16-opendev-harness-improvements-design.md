---
status: active
last_reviewed: 2026-04-23
---

# OpenDev 論文ベースのハーネス改善設計

**日付**: 2026-03-16
**着想元**: arXiv:2603.05344 "Building Effective AI Coding Agents for the Terminal" (Nghi D. Q. Bui, OpenDev)
**規模**: L（複数モジュール変更、Rust バイナリ拡張）

---

## Goal

OpenDev 論文の 5 つのクロスカッティング課題（Context Pressure, Behavioral Steering, Safety, LLM Imprecision, Bounded Growth）から、現在の dotfiles ハーネスにない改善を取り込む。

## Scope

### In Scope

1. **Doom-Loop Detection** — 同一ツール＋同一引数の繰り返し検出（Rust, post-any）
2. **Exploration Spiral Detection** — 読み取り専用ツールの連続使用検出（Rust, post-any）
3. **Context Pressure Monitor** — コンテキストウィンドウ段階的圧迫の自動検出（Rust post-any + statusline 連携）
4. **Artifact Index** — セッション中のファイル操作追跡（Rust, post-any → JSONL）
5. **Error Recovery 6 分類** — エラーカテゴリ別リカバリテンプレート（Rust, post-bash 拡張）
6. **Resource Bounds Reference** — 全定数と根拠の一元化ドキュメント（Markdown）

### Out of Scope

- Thinking Phase Separation（Claude Code の extended thinking で対応）
- Shadow Git Snapshots（Claude Code built-in undo で対応）
- Dual-Memory Architecture（autocompact が within-session を管理）
- Lazy MCP Tool Discovery（Claude Code が独自管理）
- Per-Tool-Type Summarization（将来検討。今回は Artifact Index で基盤を作る）

## Constraints

- `claude-hooks` Rust バイナリに統合（Python スクリプトは追加しない）
- 既存の `post-edit` / `post-bash` の責務は変更しない
- 全 PostToolUse hook の追加レイテンシは 5ms 以内
- 状態ファイルは `~/.claude/session-state/` に統一、2 時間 TTL
- 定数は Rust 定数として定義（`resource-bounds.md` に根拠を文書化）

## Architecture

### データフロー

```
CLAUDE CODE
  │
  ├─ PostToolUse(Edit|Write) → claude-hooks post-edit  (既存: format, golden, checkpoint)
  ├─ PostToolUse(Bash)       → claude-hooks post-bash   (既存: offload, error, test, plan)
  │                              └─ Error 6分類拡張 ← 変更
  ├─ PostToolUse(*)          → claude-hooks post-any    ← 新規
  │                              ├─ Doom-Loop Detection
  │                              ├─ Exploration Spiral Detection
  │                              ├─ Context Pressure Monitor
  │                              └─ Artifact Index Writer
  │
  └─ statusline              → context-pressure.json    ← 新規（定期書き出し）
                                    ↑ post-any が読む
```

### 新規状態ファイル

| ファイル | 書き手 | 読み手 | 形式 |
|---|---|---|---|
| `doom-loop.json` | post-any | post-any | `{fingerprints: [{hash, tool, ts}], lastReset}` |
| `exploration-tracker.json` | post-any | post-any | `{consecutive_reads, last_action_ts, warned, lastReset}` |
| `context-pressure.json` | statusline | post-any | `{used_pct: f64, ts}` |
| `artifact-index.jsonl` | post-any | review/checkpoint | `{ts, tool, action, file}` per line |

### settings.json 変更

PostToolUse に全ツール対象の hook エントリを追加:

```json
{
  "hooks": [{
    "type": "command",
    "command": "$HOME/dotfiles/tools/claude-hooks/target/release/claude-hooks post-any",
    "timeout": 5,
    "statusMessage": "Observing..."
  }]
}
```

---

## 検出ロジック詳細

### 1. Doom-Loop Detection

**アルゴリズム**:
1. 各ツール呼び出しで `(tool_name, hash(key_args))` のフィンガープリント生成
2. スライディングウィンドウ（直近 20 件）に追加
3. 同一フィンガープリント 3 回以上 → 警告注入

**フィンガープリント key_args**:

| ツール | ハッシュ対象 |
|---|---|
| Bash | command 先頭 50 文字 + 出力最終行 |
| Edit | file_path + old_string 先頭 100 文字 |
| Read | file_path |
| Grep | pattern + path |
| Glob | pattern |
| Write | file_path |
| その他 | tool_name + tool_input JSON 先頭 200 文字 |

**定数**: WINDOW=20, THRESHOLD=3, COOLDOWN=300s

**FM**: FM-011 (importance 0.7)

### 2. Exploration Spiral Detection

**アルゴリズム**:
1. ツールを 2 分類: 読み取り系（Read, Grep, Glob, WebFetch, WebSearch）/ 行動系（Edit, Write, Bash, Agent, Skill）
2. 読み取り系が連続 5 回以上 → 警告注入
3. 行動系でリセット。1 スパイラル 1 警告。

**定数**: THRESHOLD=5, 1 スパイラル 1 警告

**FM**: FM-012 (importance 0.5)

### 3. Context Pressure Monitor

**データソース**: statusline が `context-pressure.json` に `used_pct` を書き込む

**段階**:

| 閾値 | アクション |
|---|---|
| <70% | なし |
| 70% | stderr ログのみ |
| 80% | additionalContext: 「offset/limit 指定、出力フィルタ推奨」 |
| 90% | additionalContext: 「サブエージェント委譲 or /compact 推奨」 |
| 95% | additionalContext: 「即座に /checkpoint → 新セッション推奨」 |

各閾値は 1 セッション 1 回のみ警告。

**FM**: FM-013 (importance 0.8, ≥90% のみ)

### 4. Artifact Index

**記録対象**:

| ツール | action |
|---|---|
| Read | read |
| Edit | modified |
| Write | created / modified |
| Bash | executed（ファイル操作系コマンドのみ） |
| Grep/Glob | searched |

**サイズ制御**: modified/created は全件保持、read/searched は直近 100 件。合計 1000 エントリで先頭切り捨て。

### 5. Error Recovery 6 分類（post-bash 拡張）

| カテゴリ | 検出パターン | リカバリ指示 |
|---|---|---|
| PermissionDenied | `permission denied`, `EACCES` | chmod / 代替策提示 |
| FileNotFound | `No such file`, `ENOENT` | パス確認 + Glob 検索指示 |
| EditMismatch | `file has changed`, `content mismatch` | 再 Read → リトライ指示 |
| SyntaxError | `SyntaxError`, `parse error` | エラー行 Read → 修正指示 |
| RateLimit | `rate limit`, `429` | 別タスクへの切り替え推奨 |
| Timeout | `timeout`, `ETIMEDOUT` | コマンド分割 / バックグラウンド実行提案 |

既存の error-fix-guides.md 参照ロジックは維持。分類は追加レイヤー。

### 6. Resource Bounds Reference

`references/resource-bounds.md` に全定数・閾値・根拠を一元化。

---

## Validation

- [ ] `cargo build --release` 成功
- [ ] `cargo test` 全テスト通過
- [ ] 各検出ロジックの単体テスト（Doom-Loop, Exploration Spiral, Context Pressure）
- [ ] 実際のセッションで post-any が正常に発火することを確認
- [ ] 既存の post-edit / post-bash が影響を受けないことを確認
- [ ] statusline → context-pressure.json の書き込みを確認
- [ ] artifact-index.jsonl にエントリが記録されることを確認

## Risks

| リスク | 緩和策 |
|---|---|
| post-any の毎回実行によるレイテンシ | timeout=5ms。状態 I/O は小さな JSON。ベンチマーク検証 |
| Doom-Loop の false positive | COOLDOWN=300s でスパム抑制。フィンガープリントの粒度調整 |
| Context Pressure の statusline 依存 | context-pressure.json が古い場合はスキップ（30s 以上古いデータは無視） |
| Artifact Index の肥大化 | 1000 エントリキャップ + read/searched は 100 件制限 |

## Decision Log

| 日時 | 決定 | 代替案 | 却下理由 |
|---|---|---|---|
| 2026-03-16 | Approach A: 新 post-any モジュール | B: 既存分散統合, C: 共有状態ハイブリッド | B: ツール横断パターン検出不可, C: 状態一貫性が複雑 |
| 2026-03-16 | Rust で全実装 | Python, ハイブリッド | 全 PostToolUse 発火のためレイテンシ重視。既存 Rust インフラに乗る |
| 2026-03-16 | Context Pressure は statusline 連携 | API token count 直接取得 | Claude Code hooks に prompt_tokens は渡されない。statusline が唯一のソース |
