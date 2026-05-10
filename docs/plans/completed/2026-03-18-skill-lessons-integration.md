---
status: active
last_reviewed: 2026-04-23
---

# Skill Lessons Integration — Anthropic 記事知見の適用

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** "Lessons from Building Claude Code: How We Use Skills" 記事の知見を dotfiles のスキル群に適用し、スキル品質・発火精度・安全性を向上させる

**Architecture:** 7つのタスクで構成。各タスクは1つの改善軸に対応。Task 1 と Task 2 は review/SKILL.md を共有するため順序依存（Task 1 → Task 2）。それ以外は独立してコミット可能。On Demand Hooks → Gotchas → Description 最適化 → スキル使用計測 → Progressive Disclosure → Runbook → メモリ保存の順で実装。

**Tech Stack:** Markdown (SKILL.md), Shell scripts (hooks), Python (計測 hook), JSON (settings.json)

**着想元:** [Lessons from Building Claude Code: How We Use Skills](https://www.anthropic.com/engineering/claude-code-skills) — Anthropic 公式ブログ

---

## File Structure

```
.config/claude/skills/
├── review/SKILL.md                    # Modify: On Demand Hook + Gotchas
├── autonomous/SKILL.md                # Modify: Gotchas
├── webapp-testing/SKILL.md            # Modify: Gotchas
├── research/SKILL.md                  # Modify: Gotchas
├── codex-review/SKILL.md              # Modify: Gotchas
├── edge-case-analysis/SKILL.md        # Modify: Description + Progressive Disclosure
├── edge-case-analysis/references/     # Create: パターンカタログ
│   └── boundary-patterns.md
├── search-first/SKILL.md              # Modify: Reference Files セクション追加
├── search-first/references/           # Create: 検索戦略ガイド
│   └── strategies.md
├── spike/SKILL.md                     # Modify: Reference Files セクション追加
├── spike/templates/                   # Create: プロトタイプテンプレート
│   └── spike-scaffold.md
├── hook-debugger/                     # Create: Runbook スキル
│   ├── SKILL.md
│   └── scripts/
│       └── check-hook-health.sh
└── (multiple skills)                  # Modify: Description 最適化

.config/claude/scripts/
└── learner/
    └── skill-usage-tracker.py         # Create: スキル使用計測 hook

.config/claude/settings.local.json     # Modify: hooks 追加

docs/research/
└── 2026-03-18-skill-lessons-analysis.md  # Create: 記事分析レポート
```

---

### Task 1: On Demand Hooks の導入

記事の最大知見。スキルが active な時だけ有効になるフックを主要スキルに追加する。

**Files:**
- Modify: `.config/claude/skills/review/SKILL.md`

- [ ] **Step 1: review スキルに On Demand Hook を追加**

`review/SKILL.md` の frontmatter に `hooks:` を追加。レビュー実行中に意図しない自動修正（Edit/Write）が走るのを防止する read-only ガード:

```yaml
---
name: review
description: >
  コード変更のレビューを実行。変更規模に応じてレビューアーを自動選択・並列起動し、結果を統合する。
  コード変更後の Review 段階で使用、または /review で手動起動。
  言語固有チェックリストは references/review-checklists/ に配置。code-reviewer のプロンプトに注入して使用。
allowed-tools: Read, Bash, Grep, Glob, Agent
hooks:
  PreToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: prompt
          prompt: >
            [REVIEW GUARD] /review スキル実行中です。レビュー中にコードを直接修正してはいけません。
            指摘事項はレビュー出力に含め、修正はユーザーが判断した後に行ってください。
            このツール呼び出しを本当に実行する必要がありますか？レビュー出力テンプレートへの書き込みのみ許可されます。
---
```

- [ ] **Step 2: 動作確認**

Run: スキル一覧で review の hooks が認識されるか確認
```bash
grep -A 10 'hooks:' ~/.claude/skills/review/SKILL.md
```
Expected: hooks 定義が表示される

- [ ] **Step 3: Commit**

```bash
git add .config/claude/skills/review/SKILL.md
git commit -m "✨ feat(review): add on-demand PreToolUse hook to prevent edits during review"
```

---

### Task 2: 上位5スキルに Gotchas セクション追加

記事が「スキルの中で最も価値が高いコンテンツ」と断言した Gotchas セクションを追加。

**Files:**
- Modify: `.config/claude/skills/webapp-testing/SKILL.md`
- Modify: `.config/claude/skills/autonomous/SKILL.md`
- Modify: `.config/claude/skills/research/SKILL.md`
- Modify: `.config/claude/skills/codex-review/SKILL.md`
- Modify: `.config/claude/skills/review/SKILL.md` (Task 1 完了後に実施)

- [ ] **Step 1: webapp-testing の Common Pitfalls を Gotchas に統合拡充**

既存の `## Common Pitfalls` セクション（152行目付近）を `## Gotchas` にリネームし、以下の項目を追加で統合する。
既存の4項目（CSS セレクタ回避、snapshot 必須、`-i` 推奨、close 必須）はそのまま残す:

```markdown
## Gotchas

- **Don't** use CSS selectors when `@ref` from snapshot is available — refs are more reliable
- **Don't** skip `snapshot` and guess element positions — always observe first
- **Do** use `snapshot -i` when you only care about interactive elements (faster, less noise)
- **Do** close the browser when done (`agent-browser close`) to free resources
- **snapshot が空**: ページのロード完了前に snapshot を取ると空になる。`agent-browser wait` でロード完了を待つこと
- **@ref の寿命**: ページ遷移やDOMの大きな変更で @ref は無効化される。操作前に必ず再 snapshot
- **ポート競合**: `npm run dev` が既にバックグラウンドで走っている場合、2重起動でポート競合する。`lsof -i :3000` で確認
- **file:// プロトコル制限**: file:// URL では CORS やいくつかの Web API が動作しない。localStorage 等のテストは http:// で
- **タイムアウト**: agent-browser のデフォルトタイムアウトは短い。SPA の初期ロードが遅い場合は明示的に wait を入れる
```

- [ ] **Step 2: autonomous に Gotchas 追加**

```markdown
## Gotchas

- **run.lock 残存**: セッション異常終了時に `.autonomous/{name}/run.lock` が残り、再実行がブロックされる。手動で `rm` が必要
- **worktree のクリーンアップ**: 並列タスク完了後に `git worktree remove` を忘れると、ディスクを圧迫し、ブランチが残る
- **claude -p のコンテキスト制限**: ヘッドレスセッションは会話コンテキストが短い。executor-prompt.md に必要な情報を全て含めること
- **共有状態の書き込み競合**: 並列タスクが同じファイルを編集すると、マージコンフリクトが発生する。worktree 隔離を徹底
- **セッション数の爆発**: MAX_SESSIONS を設定しないと、分解したタスク数だけセッションが生まれる。推奨: 5以下
```

- [ ] **Step 3: research に Gotchas 追加**

```markdown
## Gotchas

- **並列セッションの出力衝突**: 複数の claude -p が同じ `.research/{name}/` に書き込むとファイル破損する。サブタスクごとにサブディレクトリを分ける
- **MCP タイムアウト**: WebSearch/WebFetch は外部依存。タイムアウト時はフォールバック（内蔵知識ベースの回答）を使う
- **Gemini の hallucination**: Google Search grounding があっても Gemini は事実と異なる情報を返すことがある。クロスバリデーション必須
- **レポート肥大化**: サブタスクが多すぎると統合レポートが巨大になる。3-5 サブタスクが最適
- **言語プロトコル**: CLI への指示は英語、ユーザーへの報告は日本語。混在させるとモデルの出力品質が下がる
```

- [ ] **Step 4: codex-review に Gotchas 追加**

```markdown
## Gotchas

- **レート制限**: Codex CLI は API レート制限に引っかかることがある。429 エラー時は 30秒待って再試行
- **日本語コメントの扱い**: reasoning_effort=xhigh でも日本語コメント内の意図を誤解することがある。レビュー指摘が的外れな場合はスキップ
- **--skip-git-repo-check 必須**: dotfiles のような symlink リポジトリでは git repo 検出に失敗するため、常にこのフラグが必要
- **大きすぎる diff**: 500行超の diff は Codex のコンテキストを圧迫する。`--stat` で概要を先に確認し、ファイル単位で分割レビューを検討
- **2>/dev/null の副作用**: エラー出力を捨てているため、Codex CLI 自体のエラー（認証切れ等）が見えなくなる。問題時は外して実行
```

- [ ] **Step 5: review に Gotchas 追加**

```markdown
## Gotchas

- **staged vs unstaged の混同**: `git diff --cached` はステージ済みのみ、`git diff` は未ステージのみ、`git diff HEAD` は両方を含む。レビュー対象に応じて使い分けること
- **レビュアー起動の順序依存**: Agent ツールで並列起動する際、全レビュアーを1メッセージにまとめないと逐次実行になる
- **言語チェックリストの Read 忘れ**: code-reviewer にチェックリストを注入し忘れると、汎用レビューしか行われない。Step 2 の言語判定を省略しないこと
- **信頼度フィルタの閾値**: confidence 80未満のフィルタが厳しすぎると、有効な指摘も消える。初回は閾値なしで実行し、ノイズを見てから調整
- **codex-reviewer との重複**: code-reviewer と codex-reviewer が同じ指摘をすることがある。Synthesis ステップで重複排除すること
```

- [ ] **Step 6: Commit**

```bash
git add .config/claude/skills/webapp-testing/SKILL.md \
       .config/claude/skills/autonomous/SKILL.md \
       .config/claude/skills/research/SKILL.md \
       .config/claude/skills/codex-review/SKILL.md \
       .config/claude/skills/review/SKILL.md
git commit -m "📝 docs(skills): add Gotchas sections to top 5 skills

Based on Anthropic's 'Lessons from Building Claude Code' article insight
that Gotchas are 'the highest-signal content in any skill'."
```

---

### Task 3: Description フィールドのトリガー条件最適化

記事: 「description は要約ではなく、モデルがスキャンするトリガー条件」。

**Files:**
- Modify: `.config/claude/skills/edge-case-analysis/SKILL.md`
- Modify: `.config/claude/skills/check-health/SKILL.md`
- Modify: `.config/claude/skills/spike/SKILL.md`
- Modify: `.config/claude/skills/eureka/SKILL.md`
- Modify: `.config/claude/skills/continuous-learning/SKILL.md`
- Modify: `.config/claude/skills/debate/SKILL.md`

- [ ] **Step 1: 各スキルの description をトリガー条件ベースに書き換え**

以下の6スキルの description を「何をするか」から「いつ発火すべきか」に重点を移す。
**注意**: Before テキストは概要。実装時は必ず実ファイルの frontmatter を Read して確認すること。

**edge-case-analysis** — 現在の description（2行）の末尾に Triggers/Do-NOT-use を追加:
```yaml
description: >
  実装前に異常系・境界値・nil パスを強制的に洗い出す。M/L 規模のタスクで Plan → Implement の間に挟む。
  移行タスク、新機能実装、バグ修正のいずれでも使用。
  Triggers: 'エッジケース', '境界値', 'nilチェック', '異常系', 'what if', '壊れるケース',
  'edge case', 'boundary', 'corner case', 'error path'.
  Do NOT use for S規模タスク(typo修正、1行変更) — オーバーキル。
```

**check-health** — 現在の description の末尾に追加:
```yaml
description: >
  ドキュメント鮮度・コード乖離・参照整合性をチェックする。M/Lタスクの Plan ステージで自動実行、または手動で /check-health で実行。
  Triggers: 'ドキュメント古い', 'doc outdated', '参照切れ', 'broken reference', 'stale docs',
  'ヘルスチェック', 'health check', '整合性', 'consistency check'.
  Use BEFORE starting investigation on unfamiliar code areas.
```

**spike** — 現在の description を書き換え:
```yaml
description: >
  プロトタイプファースト開発。worktree で隔離し、最小実装 → Product Validation まで行う。
  Triggers: '試してみたい', 'プロトタイプ', 'POC', 'proof of concept', 'まず動かしてみる',
  'spike', '実験', 'feasibility', 'これって可能？', 'quick test'.
  Do NOT use when spec is clear and ready for production — use /rpi or /epd instead.
  テスト・lint 不要。
```

**eureka** — 現在の description を書き換え:
```yaml
description: >
  技術ブレイクスルーを構造化テンプレートで即座に記録する。問題→洞察→実装→指標→再利用パターン。
  Triggers: 'これは発見だ', 'eureka', 'ブレイクスルー', 'breakthrough', 'TIL',
  '今日学んだこと', '予想外の解決策', 'aha moment', '重要な知見'.
  発見の鮮度が高いうちに記録し、AutoEvolve learnings と連携。/eureka で手動起動。
```

**continuous-learning** — 現在の description を書き換え:
```yaml
description: >
  Auto-detect and record reusable patterns from corrections, debugging, and repeated work.
  Triggers: user corrections ('no not that', 'instead do', 'don't do X'), recurring patterns (same fix applied 2+ times),
  new project conventions discovered during work, debugging insights worth preserving.
  Do NOT use for one-off fixes or task-specific context — use memory system instead.
```

**debate** — 現在の description を書き換え:
```yaml
description: >
  複数AIモデル(Codex/Gemini)に同じ質問を投げ、独立した視点を収集・統合する。
  Triggers: 'AとBどちらが良い', 'トレードオフ', 'trade-off', '比較して', 'pros and cons',
  'この設計の問題点', 'セカンドオピニオン', 'second opinion', '技術選定', 'which is better'.
  Do NOT use for factual questions with clear answers — use WebSearch or gemini skill instead.
```

- [ ] **Step 2: Commit**

```bash
git add .config/claude/skills/edge-case-analysis/SKILL.md \
       .config/claude/skills/check-health/SKILL.md \
       .config/claude/skills/spike/SKILL.md \
       .config/claude/skills/eureka/SKILL.md \
       .config/claude/skills/continuous-learning/SKILL.md \
       .config/claude/skills/debate/SKILL.md
git commit -m "✨ feat(skills): optimize description fields as trigger conditions

Add explicit Triggers/Do-NOT-use patterns to 6 skill descriptions.
Article insight: 'The description field is for the model' — it's a
trigger condition, not a summary."
```

---

### Task 4: スキル使用頻度トラッキング hook

記事は「PreToolUse フックでスキル使用をログ」と紹介。AutoEvolve の分析対象にも接続する。

**Files:**
- Create: `.config/claude/scripts/learner/skill-usage-tracker.py`
- Modify: `.config/claude/settings.local.json` (hooks 追加)

- [ ] **Step 1: スキル使用トラッカースクリプトを作成**

```python
#!/usr/bin/env python3
"""Skill usage tracker — logs which skills are invoked and when.

Listens on PreToolUse for Skill tool calls, records to JSONL for AutoEvolve analysis.
"""
import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = data.get("tool_name", "")
    if tool_name != "Skill":
        return

    tool_input = data.get("tool_input", {})
    skill_name = tool_input.get("skill", "unknown")

    # Log to JSONL
    log_dir = Path(os.environ.get(
        "AUTOEVOLVE_DATA_DIR",
        os.path.expanduser("~/.claude/agent-memory")
    )) / "metrics"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "skill-usage.jsonl"

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "skill": skill_name,
        "args": tool_input.get("args", ""),
        "cwd": os.getcwd(),
    }

    with open(log_file, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: settings.local.json に hooks キーを追加**

現在の settings.local.json は `env` のみ。`hooks` キーと `PreToolUse` 配列を追加する。
settings.local.json の完全な After 状態:

```json
{
  "env": {
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "80",
    "DISABLE_COST_WARNINGS": "1"
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Skill",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/scripts/learner/skill-usage-tracker.py"
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 3: 動作確認**

Run: 任意のスキルを起動し、ログが記録されるか確認
```bash
cat ~/.claude/agent-memory/metrics/skill-usage.jsonl | tail -3
```
Expected: `{"timestamp": "...", "skill": "...", ...}` 形式の JSONL エントリ

- [ ] **Step 4: Commit**

```bash
git add .config/claude/scripts/learner/skill-usage-tracker.py \
       .config/claude/settings.local.json
git commit -m "✨ feat(harness): add skill usage tracking hook

PreToolUse hook that logs Skill tool invocations to JSONL.
Feeds into AutoEvolve analysis for skill retirement decisions.
Article insight: 'PreToolUse hook for logging skill usage'."
```

---

### Task 5: Progressive Disclosure 拡充

現状 27% → 主要スキルにファイルシステムベースのコンテキスト分離を追加。

**Files:**
- Modify: `.config/claude/skills/edge-case-analysis/SKILL.md`
- Create: `.config/claude/skills/edge-case-analysis/references/boundary-patterns.md`
- Modify: `.config/claude/skills/search-first/SKILL.md`
- Create: `.config/claude/skills/search-first/references/strategies.md`
- Modify: `.config/claude/skills/spike/SKILL.md`
- Create: `.config/claude/skills/spike/templates/spike-scaffold.md`

- [ ] **Step 1: edge-case-analysis に references/ を追加**

`edge-case-analysis/references/boundary-patterns.md` を作成:

```markdown
# Boundary Pattern Catalog

edge-case-analysis スキルが参照するパターンカタログ。
Claude は必要に応じてこのファイルを Read する。

## 数値境界

| パターン | チェック項目 |
|---------|------------|
| ゼロ値 | 0, 0.0, -0 |
| 最大/最小値 | INT_MAX, INT_MIN, MAX_SAFE_INTEGER |
| オーバーフロー | 加算・乗算の結果が型の範囲を超える |
| 浮動小数点精度 | 0.1 + 0.2 !== 0.3 |

## 文字列境界

| パターン | チェック項目 |
|---------|------------|
| 空文字列 | "", null, undefined の区別 |
| Unicode | 絵文字, ZWJ シーケンス, RTL テキスト |
| 超長文字列 | バッファ制限, 表示崩れ |
| 特殊文字 | SQL/HTML/Shell メタ文字 |

## コレクション境界

| パターン | チェック項目 |
|---------|------------|
| 空コレクション | [], {}, nil map |
| 単一要素 | off-by-one の温床 |
| 大量要素 | メモリ, ページネーション |
| 重複要素 | Set vs List の挙動差 |

## 時間・状態境界

| パターン | チェック項目 |
|---------|------------|
| タイムゾーン | UTC ↔ JST 変換, DST |
| 日付境界 | 月末, 閏年, 年末 |
| 同時実行 | race condition, deadlock |
| 状態遷移 | 無効な遷移パス, 再入可能性 |

## nil/null パス

| パターン | チェック項目 |
|---------|------------|
| Optional unwrap | nil dereference |
| Map lookup miss | zero value vs not found |
| JSON null | null vs missing key vs "" |
| DB NULL | NULL vs empty string vs default |
```

`edge-case-analysis/SKILL.md` の末尾に参照セクションを追加:

```markdown
## Reference Files

- `references/boundary-patterns.md` — 境界値パターンカタログ。分析の網羅性チェックに使用
```

- [ ] **Step 2: search-first に references/ を追加**

`search-first/references/strategies.md` を作成:

```markdown
# Search Strategies Guide

search-first スキルが参照する検索戦略ガイド。

## パッケージレジストリ検索

| 言語 | レジストリ | 検索コマンド |
|-----|----------|------------|
| TypeScript | npm | `npm search {keyword}` / npmjs.com |
| Python | PyPI | `pip search` (廃止) → pypi.org で検索 |
| Go | pkg.go.dev | `go list -m all` / pkg.go.dev |
| Rust | crates.io | `cargo search {keyword}` |

## 品質評価シグナル

| シグナル | 良い | 注意 |
|---------|-----|------|
| メンテナンス | 直近3ヶ月以内にリリース | 1年以上更新なし |
| 依存数 | 少ない（<10） | 依存ツリーが深い（>50） |
| ライセンス | MIT, Apache 2.0, BSD | GPL（伝播に注意）, SSPL |
| TypeScript | 型定義同梱 or @types あり | 型なし |
| テスト | CI バッジあり | テストなし |

## MCP サーバー検索

1. `settings.json` の `mcpServers` セクションを確認
2. MCP マーケットプレイスを WebSearch
3. GitHub で `mcp-server-{keyword}` を検索
```

`search-first/SKILL.md` の末尾に参照セクションを追加:

```markdown
## Reference Files

- `references/strategies.md` — パッケージレジストリ・MCP・品質評価の検索戦略ガイド
```

- [ ] **Step 3: spike に templates/ を追加**

`spike/templates/spike-scaffold.md` を作成:

````markdown
# Spike Scaffold Template

## {spike-name}

**仮説:** {何を検証するか}
**成功基準:** {どうなったら仮説が正しいと言えるか}
**制限時間:** {最大何分で切り上げるか}

### 最小実装

```
{最小限のコードや設定}
```

### 検証手順

1. {手順1}
2. {手順2}
3. {手順3}

### 結果

- [ ] 仮説は正しかった → `/epd` で本実装へ
- [ ] 仮説は部分的に正しかった → 修正して再 spike
- [ ] 仮説は誤りだった → pivot or abandon
````

`spike/SKILL.md` の末尾に参照セクションを追加:

```markdown
## Reference Files

- `templates/spike-scaffold.md` — spike 開始時にコピーして使うテンプレート
```

- [ ] **Step 4: Commit**

```bash
git add .config/claude/skills/edge-case-analysis/ \
       .config/claude/skills/search-first/ \
       .config/claude/skills/spike/
git commit -m "📝 docs(skills): add progressive disclosure references to 3 skills

Add boundary-patterns catalog, search strategies guide, and spike scaffold template.
Each skill's SKILL.md now has a Reference Files section pointing to the new resources.
Article insight: 'Think of the entire file system as context engineering'."
```

---

### Task 6: Runbook スキル — hook-debugger

記事のカテゴリ GAP を埋める最初の Runbook スキル。hook が期待通り発火しない時の診断手順。

**Files:**
- Create: `.config/claude/skills/hook-debugger/SKILL.md`
- Create: `.config/claude/skills/hook-debugger/scripts/check-hook-health.sh`

- [ ] **Step 1: hook-debugger SKILL.md を作成**

```markdown
---
name: hook-debugger
description: >
  Hook が期待通り発火しない・エラーになる時の診断 Runbook。ログ確認→正規表現検証→手動実行→修正の手順を案内。
  Triggers: 'hook が動かない', 'hook not firing', 'hook error', 'フック デバッグ',
  'hook debug', 'PostToolUse が発火しない', 'PreToolUse が効かない'.
  Do NOT use for hook の新規作成 — use /update-config skill instead.
allowed-tools: Read, Bash, Grep, Glob
---

# Hook Debugger — Runbook

Hook が期待通り動作しない時の体系的な診断手順。

## Symptom → Action マッピング

| 症状 | 最も可能性の高い原因 | 確認手順 |
|-----|-------------------|---------|
| hook が発火しない | matcher パターン不一致 | Step 1 → Step 2 |
| hook がエラーで失敗 | スクリプトのパーミッション or 構文エラー | Step 3 |
| hook の出力が無視される | JSON 出力形式の不備 | Step 4 |
| hook が遅すぎる | タイムアウト設定不足 | Step 5 |

## Step 1: Hook 登録状況の確認

```bash
# settings.json / settings.local.json の hooks を一覧
./scripts/check-hook-health.sh
```

## Step 2: Matcher パターンの検証

```bash
# matcher が意図したツール名にマッチするか確認
# 注意: \b は日本語(Unicode)で誤動作する → (?=[^a-zA-Z0-9]|$) を使う
echo "Bash" | grep -P "^(Edit|Write)$"  # マッチしない例
echo "Edit" | grep -P "^(Edit|Write)$"  # マッチする例
```

よくあるミス:
- `Bash(git commit)` — `*` ワイルドカードが必要: `Bash(git commit *)`
- `Edit|Write` — 正しい。パイプは OR として機能する
- `Bash(npm .*)` — matcher は正規表現ではなくグロブパターン

## Step 3: スクリプトの手動実行

```bash
# スクリプトに実行権限があるか
ls -la ~/.claude/scripts/{layer}/{script-name}

# 手動で実行してエラーを確認
echo '{"tool_name":"Bash","tool_input":{"command":"echo test"}}' | \
  python3 ~/.claude/scripts/{layer}/{script-name}
```

## Step 4: JSON 出力形式の確認

PostToolUse / PreToolUse のスクリプトは JSON を stdout に出力する必要がある:

```json
// PreToolUse — ブロックする場合
{"decision": "block", "reason": "理由"}

// PreToolUse — 許可する場合（何も出力しない or）
{"decision": "allow"}

// PostToolUse — 追加コンテキストを返す場合
{"additionalContext": "補足情報"}
```

SessionStart は plain text を stdout に出力する（JSON ではない）。

## Step 5: タイムアウトの確認

デフォルトタイムアウトを超えるとスクリプトは kill される:

```bash
# タイムアウト値を確認
grep -A 5 'timeout' ~/.claude/settings.json ~/.claude/settings.local.json
```

## Gotchas

- **shebang 行**: `#!/usr/bin/env python3` がないと実行環境が不定になる
- **stdin の消費**: PreToolUse/PostToolUse は stdin から JSON を読む。`input()` で先に読むと `json.load(sys.stdin)` が空になる
- **PATH の違い**: hook 実行時の PATH はユーザーのシェルと異なる場合がある。フルパス推奨
- **並行実行**: 同じイベントに複数の hook が登録されている場合、実行順序は保証されない
- **SKILL.md hooks vs settings.json hooks**: SKILL.md の hooks はスキルが active な時のみ有効。settings.json はグローバル
```

- [ ] **Step 2: check-hook-health.sh スクリプトを作成**

```bash
#!/usr/bin/env bash
# Hook health check — 登録された hook の状態を一覧表示
set -euo pipefail

SETTINGS_FILES=(
    "$HOME/.claude/settings.json"
    "$HOME/.claude/settings.local.json"
)

echo "=== Hook Registration Status ==="
echo ""

for f in "${SETTINGS_FILES[@]}"; do
    if [[ -f "$f" ]]; then
        echo "📄 $f"
        # Extract hook events and count
        python3 -c "
import json, sys
with open('$f') as fh:
    data = json.load(fh)
hooks = data.get('hooks', {})
if not hooks:
    print('  (no hooks)')
else:
    for event, entries in hooks.items():
        print(f'  {event}: {len(entries)} hook(s)')
        for e in entries:
            matcher = e.get('matcher', '(all)')
            for h in e.get('hooks', []):
                cmd = h.get('command', h.get('prompt', '(prompt)'))[:60]
                print(f'    - [{matcher}] {cmd}')
" 2>/dev/null || echo "  (parse error)"
        echo ""
    fi
done

echo "=== Script Permission Check ==="
echo ""
find "$HOME/.claude/scripts" -name "*.py" -o -name "*.sh" -o -name "*.js" 2>/dev/null | while read -r script; do
    if [[ -x "$script" ]]; then
        echo "  ✅ $script"
    else
        echo "  ⚠️  $script (not executable)"
    fi
done
```

- [ ] **Step 3: スクリプトに実行権限を付与**

```bash
chmod +x .config/claude/skills/hook-debugger/scripts/check-hook-health.sh
```

- [ ] **Step 4: Commit**

```bash
git add .config/claude/skills/hook-debugger/
git commit -m "✨ feat(skills): add hook-debugger runbook skill

First Runbook-type skill filling the category gap identified in the
Anthropic skills article. Provides systematic diagnosis for hook issues."
```

---

### Task 7: 記事分析レポートとメモリ保存

分析結果を永続化し、今後の参照に使えるようにする。

**Files:**
- Create: `docs/research/2026-03-18-skill-lessons-analysis.md`
- Create: `~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/skill_lessons_integration.md` (git 管理外)
- Modify: `~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/MEMORY.md` (git 管理外)

- [ ] **Step 1: 記事分析レポートを保存**

`docs/research/2026-03-18-skill-lessons-analysis.md` に以下の内容で作成:

```markdown
# Anthropic "Lessons from Building Claude Code: How We Use Skills" 分析レポート

**日付:** 2026-03-18
**ソース:** Anthropic 公式ブログ

## 記事の9スキルカテゴリ

1. Library & API Reference — 内部/外部ライブラリの正しい使い方
2. Product Verification — コードの正しさを検証する手段
3. Data Fetching & Analysis — データ・モニタリングスタック接続
4. Business Process & Team Automation — 反復ワークフローの自動化
5. Code Scaffolding & Templates — フレームワークボイラープレート生成
6. Code Quality & Review — コード品質とレビュー強制
7. CI/CD & Deployment — フェッチ・プッシュ・デプロイ
8. Runbooks — 症状→調査→レポートの構造化手順
9. Infrastructure Operations — ルーチンメンテナンスとオペレーション

## 7つのベストプラクティス

1. **Don't State the Obvious** — Claude が既に知っていることは書かない
2. **Build a Gotchas Section** — 「スキルの中で最も価値が高いコンテンツ」
3. **Use the File System & Progressive Disclosure** — スキルはフォルダ、ファイルシステム全体がコンテキストエンジニアリング
4. **Avoid Railroading Claude** — 情報は与えるが、状況に応じた柔軟性を持たせる
5. **The Description Field Is For the Model** — 要約ではなくトリガー条件
6. **Memory & Storing Data** — `${CLAUDE_PLUGIN_DATA}` でスキル内データ蓄積
7. **On Demand Hooks** — スキルが active な時のみ有効なフック

## dotfiles との照合結果

| カテゴリ | 充足度 | 該当スキル数 |
|---------|--------|------------|
| Library & API Reference | 充実 | 6 |
| Product Verification | 充実 | 3 |
| Data Fetching & Analysis | 中程度 | 3 |
| Business Process & Team Automation | 充実 | 5 |
| Code Scaffolding & Templates | 中程度 | 3 |
| Code Quality & Review | 非常に充実 | 5 |
| CI/CD & Deployment | 中程度 | 2 |
| Runbooks | **GAP** | 0 → 1 (hook-debugger) |
| Infrastructure Operations | GAP (dotfiles の性質上限定的) | 0 |

## 実装した改善

1. On Demand Hooks — review スキルに PreToolUse ガード追加
2. Gotchas — 上位5スキルに追加
3. Description 最適化 — 6スキルにトリガー条件パターン追加
4. スキル使用計測 — PreToolUse hook でスキル起動ログ
5. Progressive Disclosure — 3スキルに references/templates 追加
6. Runbook — hook-debugger スキル新規作成

## 今後の検討事項

- 他スキルへの Gotchas 追加の段階的拡大
- スキル使用ログに基づく退役判断の自動化（AutoEvolve 連携）
- Memory & Storing Data パターンの review/daily-report への適用
```

- [ ] **Step 2: メモリファイルを作成**

`~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/skill_lessons_integration.md`:

```markdown
---
name: skill_lessons_integration
description: Anthropic "Lessons from Building Claude Code: How We Use Skills" 記事の知見と dotfiles への適用状況
type: reference
---

Anthropic 公式ブログ記事 (2026-03) の知見。9スキルカテゴリ分類、On Demand Hooks、Gotchas セクション、
Description-as-trigger、スキル使用計測、Progressive Disclosure、Memory & Storing Data の7ベストプラクティス。

**適用レポート**: `docs/research/2026-03-18-skill-lessons-analysis.md`
**実装計画**: `docs/plans/2026-03-18-skill-lessons-integration.md`
```

- [ ] **Step 3: MEMORY.md にポインタ追加**

`~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/MEMORY.md` の末尾に以下を追加:

```markdown
## Anthropic Skills 記事統合（2026-03-18 追加）

- [skill_lessons_integration.md](skill_lessons_integration.md) — "Lessons from Building Claude Code: How We Use Skills" の9カテゴリ・7ベストプラクティス。On Demand Hooks、Gotchas、Description-as-trigger 等の適用状況
- 分析レポート: `docs/research/2026-03-18-skill-lessons-analysis.md`
```

**注意**: メモリファイルは `~/.claude/projects/` 配下にあり dotfiles リポジトリの git 管理外。コミット不要。

- [ ] **Step 4: 記事分析レポートのみ Commit**

```bash
git add docs/research/2026-03-18-skill-lessons-analysis.md
git commit -m "📝 docs(research): add Anthropic skill lessons analysis report"
```
