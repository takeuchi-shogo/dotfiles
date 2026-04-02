# Plan: コンテキスト圧縮の頻度を削減する

## Context

Claude Code セッションでターンを跨ぐと前の会話がターミナル上から消える問題。
原因はコンテキスト圧縮（Compaction）が早期に発生していること。

`opus[1m]` (100万トークン) を使用しているが、**1ターンあたり~20Kトークンを消費** しており、
約40ターンで80%に達してコンパクションが発生する。

## 計測結果サマリー

### コンテキスト消費の内訳

| カテゴリ | サイズ | 性質 | 削減可能性 |
|----------|--------|------|-----------|
| スキル一覧 (1回目, 30 commands) | ~24 KB | 固定 system prompt | 高 |
| スキル一覧 (2回目, plugin重複) | ~16 KB | 固定 system prompt | 高 |
| CLAUDE.md | ~9 KB | 固定 system prompt | 中 |
| Deferred tools 一覧 | ~3 KB | 固定 | 低 |
| MCP instructions | ~1.5 KB | 固定 | 低 |
| **固定オーバーヘッド合計** | **~54 KB** | | |
| フック出力 (Rust, 4呼出/ターン) | ~3.5 KB | 毎ターン蓄積 | 中 |
| Python フック出力 | ~1-2 KB | 条件付き蓄積 | 中 |
| ツール結果 (Read, Bash等) | ~8 KB avg | 毎ターン蓄積 | 低 |
| アシスタント応答 | ~2-5 KB | 毎ターン蓄積 | - |

### フック出力の詳細 (Rust claude-hooks)

| フック | 出力サイズ | 発火条件 |
|--------|-----------|---------|
| post-bash (6種検出) | 1.5-2.5 KB | Bash 実行後、条件付き |
| post-edit (5種検出) | 0.9-1.6 KB | Edit/Write 後、条件付き |
| post-any (4種検出) | 0.6-1.0 KB | **全ツール後** |
| pre-edit (3種検出) | 0.3-0.9 KB | Edit/Write 前、条件付き |

### Python フック出力

| フック | 出力先 | 条件 |
|--------|--------|------|
| derivation-honesty-hook | stdout (additionalContext) | 検出時のみ |
| rationalization-scanner | stdout (additionalContext) | Agent後、検出時のみ |
| skill-suggest | stderr | Edit/Write時 |
| doc-garden-check | stdout | 条件付き |
| file-proliferation-guard | stdout | Write時、閾値超過時 |
| prompt-injection-detector | stderr | Bash時、検出時のみ |

**suppressOutput を使用しているフック: 0個** (skill-tracker/subagent-monitor は出力なし)

### 最大の消費源ランキング

1. **スキル一覧 (~40 KB)** — 120+エントリが2回注入。最大の消費源
2. **CLAUDE.md (~9 KB)** — 詳細な指示が固定で注入
3. **post-any フック (~0.6-1.0 KB × 全ツール呼び出し)** — 最も頻繁に発火
4. **post-bash/post-edit (~1.5-2.5 KB)** — 条件付きだが出力量大

## 削減戦略 (インパクト順)

### Phase 1: スキル整理 (推定 -20~25 KB、最大効果)

dotfiles プロジェクトで使う可能性が低いスキルを特定し、description を短縮または削除を検討。

**対象ファイル:**
- `.config/claude/commands/*.md` (30個)

**アプローチ:**
- 使用頻度データを取得（skill-tracker ログ、session JSONL からスキル呼び出し回数を集計）
- 低頻度スキルの description を短縮（Triggers/Do NOT use 部分がスキル一覧の大半を占める）
- プロジェクト非依存のスキルは user-level commands に移動検討

### Phase 2: プラグイン精査 (推定 -10~15 KB)

10個の有効プラグインのうち、dotfiles プロジェクトで不要なものを無効化。

**対象ファイル:**
- `.config/claude/settings.json` の `enabledPlugins`

**候補:**
- `datadog` (6スキル追加) — dotfiles で使わない
- `superpowers` (14スキル追加) — 多くが既存スキルと重複
- `discord` (2スキル追加) — 頻度次第

### Phase 3: フック出力の suppressOutput 化 (推定 -2~4 KB/ターン)

ログ目的で Claude に読ませる必要がないフック出力を抑制。

**対象ファイル:**
- `tools/claude-hooks/src/post_any.rs` — 全ツール後に発火、最頻
- `tools/claude-hooks/src/post_bash.rs`
- `tools/claude-hooks/src/post_edit.rs`
- `~/.claude/scripts/policy/derivation-honesty-hook.py`
- `~/.claude/scripts/policy/rationalization-scanner.py`
- `~/.claude/scripts/runtime/skill-suggest.py`
- `~/.claude/scripts/lifecycle/doc-garden-check.py`

**アプローチ:**
- 各フックの出力を「Claude が読んで行動を変える必要があるか」で分類
- ブロッキング (deny) → 維持
- 行動ガイダンス (context) → 維持だが文言を短縮
- 観測/ログ目的 → `suppressOutput: true` に変更、またはファイルのみに記録

**候補:**
- `artifact-index` (post_any) → イベント記録のみ、suppressOutput 可
- `exploration-spiral` 低レベル警告 → INFO は抑制、WARNING 以上のみ出力
- `doom-loop` → 検出時のみ出力（現状も条件付き、文言短縮で対応）
- `skill-suggest` → stderr 出力をやめる、またはログファイルのみ
- `derivation-honesty-hook` → 検出率が低い場合は抑制検討

### Phase 4: CLAUDE.md 圧縮 (推定 -3~4 KB)

**対象ファイル:**
- `.config/claude/CLAUDE.md`

**アプローチ:**
- `<important if="...">` ブロックの条件付きロードが機能しているか確認
- ワークフロー表やプリンシプルの文言を短縮
- 詳細な説明は `references/` に外出しし、CLAUDE.md はポインタのみにする

## 期待効果

| Phase | 削減量 | ターン数改善 |
|-------|--------|-------------|
| Phase 1 (スキル整理) | -20~25 KB 固定 | +5~7 ターン |
| Phase 2 (プラグイン精査) | -10~15 KB 固定 | +3~4 ターン |
| Phase 3 (フック suppressOutput) | -2~4 KB/ターン | +10~20 ターン (累積) |
| Phase 4 (CLAUDE.md 圧縮) | -3~4 KB 固定 | +1~2 ターン |
| **合計** | **固定 -33~44 KB、変動 -2~4 KB/ターン** | **~40 → 60+ ターン** |

## 検証方法

1. `/check-context` で変更前のコンテキスト使用量をベースライン記録
2. 各 Phase 適用後に同等の作業（ファイル編集 + Bash 5回程度）を行い使用量を比較
3. `PostCompact` ログ (`/tmp/claude-compact.log`) で圧縮頻度を前後比較
