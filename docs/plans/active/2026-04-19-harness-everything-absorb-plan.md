---
status: active
last_reviewed: 2026-04-23
---

# Harnesses Are Everything — 統合実装プラン

- **作成日**: 2026-04-19
- **ソース分析**: docs/research/2026-04-19-harness-everything-absorb-analysis.md
- **採択タスク**: 6件 (Q1, Q2, Q3, M1, M2, L1)
- **実行順**: Wave 1 (Q1→Q3 逐次) → Wave 2 (M1+M2 並列) → Wave 3 (L1)

---

## Wave 1: Quick wins (S規模、依存なし)

### Q1: Task 9 — Harness Commit 弱めた版明文化

**目的**: 「ハーネスを安易に切り替えない」を「30日評価なしに捨てない」に弱めた版として明文化。実験速度を殺さず安定性を確保する。

**変更するファイル**:
- `dotfiles/.config/claude/references/harness-stability.md` (新規作成)
- `dotfiles/.config/claude/CLAUDE.md` (条件付きブロック追加)

**主要な変更内容**:

`references/harness-stability.md`:
```markdown
# Harness Stability Policy

## 原則: 30日評価なしに捨てない

ハーネスの構成要素（hooks, skills, agents, references）を削除・置換する前に:
1. 最低 30 日の実運用データを収集する
2. dead-weight-scan.py で使用頻度を計測する
3. 代替案が同等以上の効果を発揮することを確認する

## 例外

- セキュリティ上の問題が発覚した場合: 即時削除
- 明らかに未使用 (0 invocations in 30 days): dead-weight scan で検出後に削除可

## 背景

「切り替えない」の強制は実験速度を殺す。「30日評価」が撤退条件を客観化する。
```

`CLAUDE.md` の `<important if="you are modifying hooks, scripts, settings.json">` ブロック内に追記:
```
- Harness Stability: `references/harness-stability.md`。hooks/skills/agents の削除は30日評価後。
```

**検証方法**:
- `task validate-configs` が通ること
- CLAUDE.md の `<important if>` ブロックが既存フォーマットと一致すること

**撤退条件**: CLAUDE.md の行数が 140 行を超える場合は参照のみにして本文には追加しない

---

### Q2: Task 2 — Human-written 明示方針 追記

**目的**: system prompt の中で「人間が書いた部分」と「自動生成・フック注入された部分」の区別を明示する方針を整備する。品質保証の盲点を解消。

**変更するファイル**:
- `dotfiles/.config/claude/references/system-prompt-policy.md` (新規作成)

**主要な変更内容**:

```markdown
# System Prompt Policy

## 区分

| 区分 | 例 | 更新者 |
|------|-----|--------|
| Human-written | CLAUDE.md 本文、references/*.md | 人間 (ユーザー) |
| Hook-injected | golden-check 出力、plan-lifecycle 出力 | hooks (自動) |
| Auto-generated | MEMORY.md 自動追記、skill descriptions | AutoEvolve / tools |

## 方針

- Human-written セクションは `/improve` や AutoEvolve が**直接書き換えない**
- Hook-injected コンテンツは PreToolUse/PostToolUse コールバックで注入し、CLAUDE.md には含めない
- Auto-generated は `<!-- auto-generated -->` コメントで明示する (Markdown の場合)

## 品質保証

- Human-written 部分の変更は必ず Codex Review Gate を通す
- Auto-generated 部分の意図しない肥大化は measure-instruction-budget.py で検出する
```

**検証方法**:
- ファイルが `dotfiles/.config/claude/references/` に配置されていること
- `task validate-configs` が通ること

**撤退条件**: 既存の references/ ファイルと内容が重複する場合は既存ファイルに統合

---

### Q3: Task 3 — CLI progressive disclosure 追記

**目的**: `--help` ファーストの方針を CLAUDE.md に明記し、ツール発見の順序（CLI → Skills → MCP）を明文化する。

**変更するファイル**:
- `dotfiles/.config/claude/CLAUDE.md` (1行追記)
- `dotfiles/.config/claude/references/cli-discovery.md` (新規作成)

**主要な変更内容**:

`CLAUDE.md` の `<core_principles>` 内に追記:
```
- **CLI-first discovery**: ツール使用前に `--help` で引数・サブコマンドを確認。発見順: CLI → Skills → MCP
```

`references/cli-discovery.md`:
```markdown
# CLI Discovery Policy

## 発見順序

1. **CLI `--help`**: 新しいツールを使う前に必ず `--help` を確認する
2. **Skills**: Claude Code スキルで対応できるか確認する (`/skill-name`)
3. **MCP**: 専用 MCP server が存在するか確認する

## 理由

Progressive Disclosure 設計: 詳細は必要になったときだけ露出する。
CLI は最も軽量で副作用のない探索手段。

## 例

```bash
# Good: まず help を見る
gh --help
gh pr --help

# Good: サブコマンド発見後に実行
gh pr list --state open
```
```

**検証方法**:
- CLAUDE.md の行数が増加しすぎていないこと (上限 140 行)
- `task validate-configs` が通ること

**撤退条件**: CLAUDE.md が 140 行を超える場合は cli-discovery.md への参照のみにする

---

## Wave 2: Medium tasks (M規模、並列実行可)

### M1: Task A — 総量 instruction budget 計測スクリプト

**目的**: 「常時露出する指示の総量」を正確に計測する。本文行数だけでなく、description・hook注入・MCP tool定義を含む真の総量を把握し、Stanford Lost in the Middle 問題（2000トークン超で遵守率20-30%低下）を予防する。

**変更するファイル**:
- `dotfiles/scripts/policy/measure-instruction-budget.py` (新規作成)
- `dotfiles/.config/claude/settings.json` の `golden-check` hook に統合 (既存拡張)

**主要な変更内容**:

`scripts/policy/measure-instruction-budget.py`:
```python
#!/usr/bin/env python3
"""
Measure total instruction budget exposed to the model per session.

Categories:
  - claude_md: CLAUDE.md content (always exposed)
  - references: referenced .md files loaded in session
  - hook_injected: PreToolUse/PostToolUse hook outputs
  - mcp_descriptions: MCP tool descriptions (from settings.json)
  - skill_descriptions: loaded skill descriptions

Output: JSONL to ~/.claude/logs/instruction-budget-{date}.jsonl
Threshold: warn if total > 6000 tokens (approx. 2000 token safe zone x3 for headroom)
"""

import json
import sys
from pathlib import Path
from datetime import date

THRESHOLD_TOKENS = 6000
CHARS_PER_TOKEN = 4  # rough estimate

def measure_claude_md(claude_dir: Path) -> dict:
    """Measure CLAUDE.md character count."""
    claude_md = claude_dir / "CLAUDE.md"
    chars = len(claude_md.read_text()) if claude_md.exists() else 0
    return {"source": "claude_md", "chars": chars, "tokens_est": chars // CHARS_PER_TOKEN}

def measure_mcp_descriptions(settings_path: Path) -> dict:
    """Measure MCP tool description total from settings.json."""
    # Load mcpServers and sum tool description lengths
    ...

def measure_hook_outputs(log_dir: Path) -> dict:
    """Estimate hook injection size from recent session logs."""
    ...

def main():
    claude_dir = Path.home() / ".claude"
    results = {
        "date": date.today().isoformat(),
        "components": [
            measure_claude_md(claude_dir),
            measure_mcp_descriptions(claude_dir / "settings.json"),
        ],
    }
    total_tokens = sum(c["tokens_est"] for c in results["components"])
    results["total_tokens_est"] = total_tokens
    results["status"] = "warn" if total_tokens > THRESHOLD_TOKENS else "ok"

    log_path = claude_dir / "logs" / f"instruction-budget-{date.today()}.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a") as f:
        f.write(json.dumps(results, ensure_ascii=False) + "\n")

    if results["status"] == "warn":
        print(f"[WARN] instruction budget {total_tokens} tokens > {THRESHOLD_TOKENS} threshold", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

`settings.json` の golden-check 拡張:
- `scripts/policy/measure-instruction-budget.py` を PreCompact フックから呼び出す
- 閾値超過時は WARN を出力（block はしない、初期は観測のみ）

**検証方法**:
- `python3 scripts/policy/measure-instruction-budget.py` が JSONL を出力すること
- `logs/instruction-budget-*.jsonl` に結果が記録されること
- THRESHOLD 超過時に exit code 1 を返すこと

**撤退条件**: MCP tool定義の取得が不安定な場合は claude_md + references のみの計測に縮小

---

### M2: Task B — dead-weight scan 実測タスク化

**目的**: references/・skills/・agents/ の増殖ファイルを検出し、使用頻度の低いファイルを特定する。instruction budget の隠れた消費源を排除し、AutoEvolve Phase 1 の削除提案に根拠を与える。

**変更するファイル**:
- `dotfiles/scripts/lifecycle/dead-weight-scan.py` (新規作成)
- AutoEvolve の日次ループから呼び出せるよう `scripts/lifecycle/` に配置

**主要な変更内容**:

`scripts/lifecycle/dead-weight-scan.py`:
```python
#!/usr/bin/env python3
"""
Dead-weight scan: detect rarely-referenced files in references/, skills/, agents/.

Algorithm:
  1. List all .md files in target directories
  2. Count references (grep) in CLAUDE.md, MEMORY.md, settings.json, other .md files
  3. Check last-modified date
  4. Flag as dead-weight if: ref_count == 0 AND last_modified > 30 days ago

Output:
  - JSONL: ~/.claude/logs/dead-weight-{date}.jsonl
  - Stdout: table of flagged files with ref_count and age_days

Integration:
  - AutoEvolve Phase 1 reads this output to generate deletion proposals
  - Proposals go to /improve workflow, never auto-delete
"""

import json
import subprocess
from pathlib import Path
from datetime import date, datetime, timedelta

SCAN_DIRS = [
    Path.home() / ".claude" / "references",
    Path.home() / ".claude" / "skills",
    Path.home() / ".claude" / "agents",
]
REFERENCE_ROOTS = [
    Path.home() / ".claude" / "CLAUDE.md",
    Path.home() / ".claude" / "projects" / "-Users-takeuchishougo-dotfiles" / "memory" / "MEMORY.md",
    Path.home() / ".claude" / "settings.json",
]
DEAD_WEIGHT_AGE_DAYS = 30

def count_references(target: Path, roots: list[Path]) -> int:
    """Count how many root files reference the target file by name."""
    stem = target.stem
    count = 0
    for root in roots:
        if root.exists():
            result = subprocess.run(
                ["grep", "-c", stem, str(root)],
                capture_output=True, text=True
            )
            count += int(result.stdout.strip() or 0)
    return count

def scan() -> list[dict]:
    results = []
    cutoff = datetime.now() - timedelta(days=DEAD_WEIGHT_AGE_DAYS)
    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for f in scan_dir.glob("**/*.md"):
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            age_days = (datetime.now() - mtime).days
            ref_count = count_references(f, REFERENCE_ROOTS)
            is_dead = ref_count == 0 and mtime < cutoff
            results.append({
                "file": str(f),
                "ref_count": ref_count,
                "age_days": age_days,
                "is_dead_weight": is_dead,
            })
    return results

def main():
    results = scan()
    dead = [r for r in results if r["is_dead_weight"]]

    log_path = Path.home() / ".claude" / "logs" / f"dead-weight-{date.today()}.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    if dead:
        print(f"[dead-weight-scan] {len(dead)} files flagged:")
        for r in dead:
            print(f"  {r['file']} (refs={r['ref_count']}, age={r['age_days']}d)")
    else:
        print("[dead-weight-scan] No dead-weight files detected.")

if __name__ == "__main__":
    main()
```

**検証方法**:
- `python3 scripts/lifecycle/dead-weight-scan.py` が JSONL を出力すること
- dead_weight フラグが正しく付与されること（手動でダミーファイルを作成して確認）
- AutoEvolve の日次ループから `subprocess` 経由で呼び出せること

**撤退条件**: grep ベースの参照カウントが誤検知を多発する場合は ref_count 閾値を 2 以下に緩和

---

### M2 追加 subtask (2026-04-24, AlphaSignal "Harness Engineering" absorb 由来)

**ソース**: `docs/research/2026-04-24-harness-engineering-absorb-analysis.md`
**背景**: AlphaSignal 記事と 2026-04-19 harness-everything absorb の重複度が高く、独自 contribution 3 点 (Reasoning Sandwich 定量データ / Opus 4.7 dead-weight 吸収 / ThoughtWorks 4 軸分類) のみ採択。Codex 批評で M2 subtask merge が最小衝突と判定された。

#### M2-A: Reasoning Sandwich 手動チェックリスト pin

**目的**: Codex Spec/Plan Gate + Review Gate 呼び出し時の stage 別 reasoning budget 推奨を 1 箇所に pin。自動配分ではなく手動チェックリストとする。

**変更するファイル**: `.config/claude/references/model-routing.md` (末尾に section 追加)

**主要な変更内容**:
```markdown
## Stage 別 Reasoning Budget 推奨 (任意チェックリスト)

出典: LangChain Terminal Bench 2.0 (GPT-5.2-Codex)。
- 全段 max reasoning: 53.9%
- Reasoning Sandwich (plan=high, build=reduced, verify=high): 66.5% (+13.7pt)

| Stage | 推奨 reasoning effort | 理由 |
|-------|----------------------|------|
| Plan / Spec | high | 全体構造・失敗モード抽出に深い推論が要る |
| Build / Implement | medium | 決定後の生成は深い推論が過剰 (53.9% の罠) |
| Verify / Review | high | エッジケース検出・批評に深い推論が効く |

**使い方**: Codex Spec/Plan Gate は `-c reasoning_effort=high`、Review Gate は `-c reasoning_effort=high`、Implement は medium 以下で十分。強制ではなく任意の参考。
```

**検証方法**: `.config/claude/references/model-routing.md` を開いて section が読める、Codex 呼び出しで参照できる

**撤退条件**: チェックリストが無視される/混乱を招く場合は section を削除

---

#### M2-B: dead-weight-scan に `superseded_by_model` タグ追加 (最優先)

**目的**: Opus 4.7 の self-verification により harness の一部が model capability に吸収されるリスクを追跡。dead-weight-scan の output JSONL に「どの model version で superseded になったか」を記録できるようにする。

**変更するファイル**: `scripts/lifecycle/dead-weight-scan.py` (M2 本体実装時に組み込み)

**主要な変更内容**:
- output JSONL schema に `superseded_by_model: <version> | null` field 追加 (既定 null)
- `~/.claude/logs/superseded-registry.jsonl` に手動タグ (`{file, superseded_by_model, reason, tagged_at}`) を追記する運用を開始
- scan 時はこの registry を lookup し、該当ファイルには tag を付けて出力
- AutoEvolve Phase 1 の削除提案で、`superseded_by_model` が付いているものは「model 吸収による削除候補」として表示

**Opus 4.7 release 時点での tagging 対象 (初期)**:
- evaluator 系 skill/hook (別途 capability overlap を精査)
- product-reviewer / design-reviewer / edge-case-hunter のどれかに overlap があるかは、次回 /improve で検討

**検証方法**:
- `dead-weight-scan.py` 実行で JSONL に `superseded_by_model` field が含まれること
- registry に手動で 1 件追記し、scan 出力に反映されること

**撤退条件**: `superseded_by_model` タグが手動運用に繋がらない場合は、model version から自動推論する仕組みに差し替え検討 (将来タスク)

---

#### M2-C: ADR-0006 に ThoughtWorks 4 軸分類 Appendix 追加

**目的**: ADR-0006 の 3 分類 (Deterministic Block / Semantic Advisory / Human Judgment) と直交する、harness 全体の設計語彙として ThoughtWorks の 4 軸分類を追加する。

**変更するファイル**: `docs/adr/0006-hook-philosophy.md` (末尾に Appendix 追加)

**主要な変更内容**:
```markdown
## Appendix: ThoughtWorks 4 軸分類との関係 (2026-04-24 追加)

Birgitta Böckeler (ThoughtWorks) は harness controls を 2 軸で分類する:
- **Guide (before) vs Sensor (after)**: agent が動く前の制約か、動いた後の観測か
- **Computational (deterministic) vs Inferential (LLM-based)**: 機械判定か意味判定か

本 ADR の 3 分類は「hook を追加すべきか」の採用基準であり、4 軸分類は「どんな種類の制御か」の設計語彙で、直交する。

### マッピング例

| 本 ADR の 3 分類 | 4 軸象限 | 例 |
|-----------------|----------|-----|
| Deterministic Block | Computational × Guide/Sensor | `protect-linter-config.py` (Guide)、`golden-check.py` (Sensor) |
| Semantic Advisory | Inferential × Guide/Sensor | `codex-reviewer` (Sensor)、`suggest-gemini.py` (Guide) |
| Human Judgment | (axis 外) | Karpathy 4 原則、instruction 埋め込み |

### 使いどころ

- harness 全体の **抜け漏れ監査** には 4 軸分類が有効 (「Computational Guide が 0 個になっていないか」等)
- 個別 hook の **追加判断** には本 ADR の 3 分類を使う
```

**検証方法**: ADR-0006 を開いて Appendix が読める、他の ADR からも参照可能

**撤退条件**: 4 軸分類が 3 分類と混乱する場合は Appendix を削除し、単なる reference として残す

---

## Wave 3: Large task (L規模、M2完了後)

### L1: Task 7 — reviewer calibration メトリクス

**目的**: レビューアー（codex-reviewer, code-reviewer, security-reviewer）の判断精度を TPR（True Positive Rate）と TNR（True Negative Rate）で追跡する。「レビューが効いているか」を定量化し、adversary pipeline 追加の判断根拠にする。

**前提**: M2 (dead-weight scan) 完了後。JSONL ログ基盤が安定していること。

**変更するファイル**:
- `dotfiles/scripts/learner/reviewer-calibration.py` (新規作成)
  - 既存 scripts/learner/ 配下にファイルなし（2026-04-19 時点）、scripts/runtime/ の brevity-benchmark.py パターンを参考にする
- `dotfiles/.config/claude/logs/reviewer-calibration-{date}.jsonl` (出力先)

**主要な変更内容**:

`scripts/learner/reviewer-calibration.py`:
```python
#!/usr/bin/env python3
"""
Reviewer Calibration: track TPR/TNR for codex-reviewer, code-reviewer, security-reviewer.

Data source:
  - ~/.claude/logs/session-*.jsonl: review invocations and outcomes
  - Ground truth: human override events (user accepted/rejected reviewer verdict)

Metrics:
  - TPR (True Positive Rate): reviewer flagged issue → human confirmed it was real
  - TNR (True Negative Rate): reviewer passed → no issue found later
  - Precision: flagged / (flagged + false alarms)

Output:
  - JSONL: ~/.claude/logs/reviewer-calibration-{date}.jsonl
  - Rolling 30-day window per reviewer

Algorithm:
  1. Load session logs from last 30 days
  2. Extract review events: {reviewer, verdict, outcome}
     - verdict: "block" | "pass"
     - outcome: "confirmed" | "rejected_by_human" | "unknown"
  3. Compute TPR = confirmed_blocks / all_blocks
  4. Compute TNR = clean_passes / all_passes
  5. Flag reviewers with TPR < 0.5 or TNR < 0.7 for calibration review

Calibration trigger:
  - If TPR < 0.5: reviewer is generating false alarms → tighten criteria
  - If TNR < 0.7: reviewer is missing real issues → widen criteria
  - Output suggestions to /improve workflow (never auto-modify reviewer config)
"""

import json
from pathlib import Path
from datetime import date, datetime, timedelta
from collections import defaultdict

WINDOW_DAYS = 30
TPR_WARN_THRESHOLD = 0.5
TNR_WARN_THRESHOLD = 0.7

REVIEWERS = ["codex-reviewer", "code-reviewer", "security-reviewer"]

def load_review_events(log_dir: Path, window_days: int) -> list[dict]:
    """Load review events from session JSONL logs."""
    cutoff = datetime.now() - timedelta(days=window_days)
    events = []
    for log_file in sorted(log_dir.glob("session-*.jsonl")):
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        if mtime < cutoff:
            continue
        with log_file.open() as f:
            for line in f:
                try:
                    record = json.loads(line)
                    if record.get("type") == "review_event":
                        events.append(record)
                except json.JSONDecodeError:
                    continue
    return events

def compute_metrics(events: list[dict]) -> dict:
    """Compute TPR/TNR per reviewer."""
    stats = defaultdict(lambda: {"tp": 0, "fp": 0, "tn": 0, "fn": 0})
    for e in events:
        reviewer = e.get("reviewer", "unknown")
        verdict = e.get("verdict")  # "block" | "pass"
        outcome = e.get("outcome")  # "confirmed" | "rejected_by_human" | "unknown"
        if verdict == "block" and outcome == "confirmed":
            stats[reviewer]["tp"] += 1
        elif verdict == "block" and outcome == "rejected_by_human":
            stats[reviewer]["fp"] += 1
        elif verdict == "pass" and outcome == "confirmed":
            stats[reviewer]["fn"] += 1
        elif verdict == "pass" and outcome in ("rejected_by_human", "unknown"):
            stats[reviewer]["tn"] += 1

    results = {}
    for reviewer, s in stats.items():
        total_blocks = s["tp"] + s["fp"]
        total_passes = s["tn"] + s["fn"]
        tpr = s["tp"] / total_blocks if total_blocks > 0 else None
        tnr = s["tn"] / total_passes if total_passes > 0 else None
        results[reviewer] = {
            "tpr": tpr,
            "tnr": tnr,
            "counts": s,
            "tpr_warn": tpr is not None and tpr < TPR_WARN_THRESHOLD,
            "tnr_warn": tnr is not None and tnr < TNR_WARN_THRESHOLD,
        }
    return results

def main():
    log_dir = Path.home() / ".claude" / "logs"
    events = load_review_events(log_dir, WINDOW_DAYS)

    metrics = compute_metrics(events)
    output = {
        "date": date.today().isoformat(),
        "window_days": WINDOW_DAYS,
        "reviewers": metrics,
        "event_count": len(events),
    }

    out_path = log_dir / f"reviewer-calibration-{date.today()}.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("a") as f:
        f.write(json.dumps(output, ensure_ascii=False) + "\n")

    # Print summary
    for reviewer, m in metrics.items():
        warns = []
        if m["tpr_warn"]:
            warns.append(f"TPR={m['tpr']:.2f} < {TPR_WARN_THRESHOLD} (false alarms high)")
        if m["tnr_warn"]:
            warns.append(f"TNR={m['tnr']:.2f} < {TNR_WARN_THRESHOLD} (missing issues)")
        if warns:
            print(f"[WARN] {reviewer}: {', '.join(warns)}")
        else:
            tpr_str = f"{m['tpr']:.2f}" if m["tpr"] is not None else "N/A"
            tnr_str = f"{m['tnr']:.2f}" if m["tnr"] is not None else "N/A"
            print(f"[OK] {reviewer}: TPR={tpr_str}, TNR={tnr_str}")

if __name__ == "__main__":
    main()
```

**検証方法**:
- `python3 scripts/learner/reviewer-calibration.py` がエラーなく動作すること
- ログが空の場合でも正常終了すること（event_count=0 で出力）
- JSONL 出力が `logs/reviewer-calibration-*.jsonl` に記録されること
- ダミーの review_event レコードを session ログに挿入してメトリクス計算を確認

**撤退条件**:
- session ログに `review_event` タイプが記録されていない場合（ログ形式が異なる場合）は、ログスキーマを調査してから再実装する
- 30日間でイベント数 < 10 の場合はメトリクスの信頼性が低いため警告のみにする

---

## ステータス管理

| タスク | ステータス | 完了日 |
|--------|-----------|--------|
| Q1 | pending | - |
| Q2 | pending | - |
| Q3 | pending | - |
| M1 | done | 2026-04-19 |
| M2 | done | 2026-04-19 |
| L1 | done | 2026-04-19 |

## 保留判断

- **adversary pipeline stage**: L1 (reviewer calibration) の結果を見て判断。TPR < 0.3 が複数レビューアーで続く場合に採用検討
- **LangGraph/State-Graph 移行**: 現状 dotfiles 規模では過剰。hooks の状態管理が複雑化した時点で再評価
