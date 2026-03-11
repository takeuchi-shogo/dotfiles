---
name: check-health
description: ドキュメント鮮度・コード乖離・参照整合性をチェックする。M/Lタスクの Plan ステージで自動実行、または手動で /check-health で実行。
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

### Step 4: 深刻な問題への対応

参照が壊れている場合は `doc-gardener` エージェントに修正を委譲する:

```
Agent tool → subagent_type: doc-gardener
prompt: "doc-garden-check が以下の問題を検出しました: {warnings}. 修正してください。"
```

スキルベンチマークが古い場合は `/skill-audit` の実行を提案する。
