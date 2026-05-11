---
name: check-health
description: >
  ドキュメント鮮度・コード乖離・参照整合性をチェックする。M/Lタスクの Plan ステージで自動実行、または手動で /check-health で実行。
  Triggers: 'ドキュメント古い', 'doc outdated', '参照切れ', 'broken reference', 'stale docs',
  'ヘルスチェック', 'health check', '整合性', 'consistency check'.
  Use BEFORE starting investigation on unfamiliar code areas.
origin: self
metadata:
  pattern: reviewer
---

# Health Check

プロジェクトのドキュメント健全性を検査する。

## 実行内容

1. **コード・ドキュメント乖離チェック** — 直近のコミットでコード変更があったのにドキュメントが更新されていないか
2. **ドキュメント鮮度チェック** — 30日以上更新されていないドキュメントを検出
3. **参照整合性チェック** — ドキュメント内のファイル参照が実在するか
4. **スキルベンチマーク鮮度チェック** — 30日以上ベンチマーク未実施のスキルを検出

## 手順

### Step 1: チェック実行

以下の2つのスクリプトを Bash で実行する:

```bash
python3 $HOME/.claude/scripts/lifecycle/context-drift-check.py --commits 10 --json 2>/dev/null || true
```

```bash
python3 $HOME/.claude/scripts/lifecycle/doc-garden-check.py 2>/dev/null || true
```

### Step 2: 結果分析

- 警告がなければ「Health Check: 問題なし」と報告
- 警告があれば内容をサマリーし、必要に応じて `doc-gardener` エージェントへの委譲を提案

### Step 3: スキルベンチマーク鮮度チェック

```bash
python3 -c "
import json
from pathlib import Path
from datetime import datetime, timedelta

learnings_path = Path.home() / '.claude/agent-memory/learnings/skill-benchmarks.jsonl'
skills_dir = Path.home() / '.claude/skills'
threshold = datetime.now() - timedelta(days=30)

benchmarked = {}
if learnings_path.exists():
    for line in learnings_path.read_text().splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        skill = entry.get('skill', '')
        date_str = entry.get('date', '')
        if skill and date_str:
            benchmarked[skill] = date_str

stale = []
for skill_dir in sorted(skills_dir.iterdir()):
    if not skill_dir.is_dir() or not (skill_dir / 'SKILL.md').exists():
        continue
    name = skill_dir.name
    last_bench = benchmarked.get(name)
    if not last_bench:
        stale.append(f'  - {name}: ベンチマーク未実施')
    elif datetime.strptime(last_bench, '%Y-%m-%d') < threshold:
        stale.append(f'  - {name}: 最終ベンチマーク {last_bench} (30日超)')

if stale:
    print(f'スキルベンチマーク鮮度 ({len(stale)} 件):')
    print('\n'.join(stale))
    print('  → /skill-audit でベンチマークを実行してください')
else:
    print('スキルベンチマーク: 全て最新 ✓')
" 2>/dev/null || true
```

### Step 3.5: 未文書化サブシステム検出

Codified Context 論文 Case Study 3 の知見: ドキュメント検索が0件を返すこと自体が「未文書化サブシステム」の発見シグナル。

```bash
python3 -c "
from pathlib import Path
src_dirs = [Path(c) for c in ['src','app','lib','pkg','internal','cmd'] if Path(c).is_dir()]
if not src_dirs:
    print('ソースディレクトリなし — スキップ'); exit(0)
modules = set()
for s in src_dirs:
    for c in s.iterdir():
        if c.is_dir() and not c.name.startswith(('.','_','node_modules')): modules.add(c.name)
doc_dirs = [Path('docs'), Path('.claude/references'), Path('references')]
documented = set()
for d in doc_dirs:
    if d.is_dir():
        for f in d.rglob('*.md'): documented.add(f.stem.lower().replace('-','').replace('_',''))
undoc = [m for m in sorted(modules) if not any(m.lower().replace('-','').replace('_','') in d for d in documented)]
if undoc:
    print(f'未文書化サブシステム ({len(undoc)} 件):')
    for m in undoc: print(f'  - {m}')
    print('  → document-factory エージェントで spec 生成を検討')
else:
    print('全サブシステム文書化済み ✓')
" 2>/dev/null || true
```

### Step 3.6: メモリ矛盾スキャン

メモリファイル間の矛盾候補を自動検出する。

```bash
python3 $HOME/.claude/scripts/learner/contradiction-scanner.py 2>/dev/null || true
```

矛盾候補が検出された場合:
- `[CONTRADICTION_CANDIDATE]` タグの内容をユーザーに報告
- `/improve` での解消を提案
- `references/contradiction-mapping.md` の解決フローに従う

### Step 3.7: MCP サーバートークンコストチェック

接続中の MCP サーバーが不要なコンテキストを消費していないか確認する。

ユーザーに `/mcp` コマンドの実行を提案し、以下を確認:
- 未使用の MCP サーバーが接続されていないか
- 各サーバーのトークン消費量が妥当か（セッションコンテキストの 15% 超は要注意）
- 不要なサーバーは切断を推奨

### Step 3.8: User-facing change → docs drift rubric

> 出典: Warp `oz-skills/docs-update` (2026-05-06 absorb) を rubric として移植。
> 24h commit scan を自動実行する代わりに、health check の判定軸を 1 本追加する。

直近コミットに **user-facing change** のシグナルがあるのに対応する公開ドキュメントが更新されていない場合、警告を出す。

User-facing change のシグナル（diff から検出する）:

| シグナル | 検出方法 | 対応すべき docs |
|----------|---------|----------------|
| CLI 引数 / flag の追加・削除・rename | `--help` 出力に影響、bin スクリプト diff | README, `--help` テキスト, man |
| 公開 API の signature 変更 | export された関数 / type / route の diff | API リファレンス, 型定義, OpenAPI |
| 環境変数 / config key の追加・削除 | `.env.example` / config schema diff | README, env reference |
| breaking change (semver major) | CHANGELOG / commit に `BREAKING CHANGE` | CHANGELOG, migration guide |
| skill / command / agent の追加・削除・rename | `.claude/skills/`, `.claude/commands/`, `.claude/agents/` diff | MEMORY.md, CLAUDE.md, README |

```bash
# 直近 N 件のコミットから user-facing change シグナルを抽出（参考スニペット）
git log --since="7 days ago" --pretty=format:"%h %s" -- \
  '*.md' '.claude/**' 'README*' 'CHANGELOG*' \
  'package.json' 'go.mod' 'Cargo.toml' \
  '.env.example' 'config/*.{yaml,yml,json,toml}' \
  | head -30

# user-facing シグナル（CLI flag, API signature 変更）
git diff --since="7 days ago" --stat -- 'cmd/' 'bin/' 'src/' 'lib/' 2>/dev/null | tail -10
```

判定:
- 上記シグナル検出かつ docs 未更新 → 「ドキュメント更新を推奨する変更があります」と警告
- 警告内容には変更ファイル、推奨更新先、関連 commit を含める
- 修正は `doc-gardener` agent または手動で対応（自動 PR 化はしない — Warp の docs-update は team CI 前提）

判定軸の Anti-pattern:
- 内部リファクタを user-facing と誤判定する → 「export されている」「README に名前が出る」「help テキストに出る」のいずれかが必要
- skill description 軽微な typo を昇格扱いにする → 振る舞い変更があるかで判定する

### Step 4: 深刻な問題への対応

参照が壊れている場合は `doc-gardener` エージェントに修正を委譲する:

```
Agent tool → subagent_type: doc-gardener
prompt: "doc-garden-check が以下の問題を検出しました: {warnings}. 修正してください。"
```

スキルベンチマークが古い場合は `/skill-audit` の実行を提案する。

## Skill Assets

- レポートテンプレート: `templates/health-report.md`
- 鮮度判定基準: `references/staleness-criteria.md`

## Anti-Patterns

| NG | 理由 |
|----|------|
| 警告を無視して実装に進む | 古いドキュメントに基づく実装は silent failure を招く |
| 全ファイルを毎回チェックする | 変更対象の関連ファイルに絞る。全スキャンは /audit を使う |
| ヘルスチェック結果を修正せずに閉じる | 検出だけでは価値がない。修正または Issue 化まで行う |
