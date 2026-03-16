# Qodo 式レビュー強化 + Eval パイプライン実稼働 — 実装プラン

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recall 向上（観点別エージェント + 信頼度3層化 + dedup）と eval パイプライン実稼働を実現し、Before/After で定量比較する

**Architecture:** 既存の code-reviewer + codex-reviewer を維持しつつ、edge-case-hunter と cross-file-reviewer を追加。信頼度を3層化（Critical/Important/Watch）し、セマンティック dedup + 信頼度ブーストを統合ステップに追加。eval テストケースを 10→30 に拡充し、Recall/Precision/F1 を計測する

**Tech Stack:** Claude Code agents (Markdown), Python (eval scripts), JSONL (data)

**Spec:** `docs/superpowers/specs/2026-03-16-qodo-review-enhancement-design.md`

---

## Chunk 1: Eval パイプライン拡充 + ベースライン計測

### Task 1: eval テストケース拡充 (10→30)

**Files:**
- Modify: `.config/claude/scripts/eval/reviewer-eval-tuples.json`

- [ ] **Step 1: 追加テストケース 20 件を作成**

既存 10 件は FM-001, FM-002, FM-004, FM-005, FM-010 のみカバー。
FM-003 (境界値), FM-006 (レースコンディション), FM-007 (クロスファイル), FM-008 (エラーハンドリング), FM-009 (リソースリーク) が欠落。
Go 10 / TypeScript 10 / Python 10 の言語バランスになるよう追加。

追加テストケースの一覧:

```json
[
  {
    "id": "eval-011",
    "language": "go",
    "failure_mode": "FM-003",
    "severity": "high",
    "expected_reviewer": "edge-case-hunter",
    "description": "Off-by-one in slice bounds",
    "code": "func getLastN(items []string, n int) []string {\n\treturn items[len(items)-n-1:]\n}"
  },
  {
    "id": "eval-012",
    "language": "typescript",
    "failure_mode": "FM-003",
    "severity": "high",
    "expected_reviewer": "edge-case-hunter",
    "description": "Empty array not handled",
    "code": "function getAverage(nums: number[]): number {\n  const sum = nums.reduce((a, b) => a + b, 0);\n  return sum / nums.length;\n}"
  },
  {
    "id": "eval-013",
    "language": "python",
    "failure_mode": "FM-003",
    "severity": "medium",
    "expected_reviewer": "edge-case-hunter",
    "description": "Zero-length string not guarded",
    "code": "def first_char(s: str) -> str:\n    return s[0]"
  },
  {
    "id": "eval-014",
    "language": "go",
    "failure_mode": "FM-006",
    "severity": "critical",
    "expected_reviewer": "code-reviewer",
    "description": "Goroutine leak from unbuffered channel",
    "code": "func process(items []int) {\n\tch := make(chan int)\n\tfor _, item := range items {\n\t\tgo func(v int) {\n\t\t\tch <- v * 2\n\t\t}(item)\n\t}\n\t// only reads first result\n\tfmt.Println(<-ch)\n}"
  },
  {
    "id": "eval-015",
    "language": "typescript",
    "failure_mode": "FM-006",
    "severity": "high",
    "expected_reviewer": "code-reviewer",
    "description": "Race condition on shared mutable state",
    "code": "let counter = 0;\nasync function increment() {\n  const current = counter;\n  await delay(10);\n  counter = current + 1;\n}\nPromise.all([increment(), increment(), increment()]);"
  },
  {
    "id": "eval-016",
    "language": "python",
    "failure_mode": "FM-006",
    "severity": "high",
    "expected_reviewer": "code-reviewer",
    "description": "Thread-unsafe shared list mutation",
    "code": "import threading\nresults = []\ndef worker(item):\n    results.append(process(item))\nthreads = [threading.Thread(target=worker, args=(i,)) for i in range(100)]\nfor t in threads: t.start()\nfor t in threads: t.join()"
  },
  {
    "id": "eval-017",
    "language": "go",
    "failure_mode": "FM-007",
    "severity": "high",
    "expected_reviewer": "cross-file-reviewer",
    "description": "Function signature changed but caller not updated",
    "code": "// user.go - signature changed from (id string) to (id string, includeDeleted bool)\nfunc GetUser(id string, includeDeleted bool) (*User, error) {\n\t// ...\n\treturn &User{}, nil\n}\n\n// handler.go - still using old signature\n// user, err := GetUser(r.URL.Query().Get(\"id\"))"
  },
  {
    "id": "eval-018",
    "language": "typescript",
    "failure_mode": "FM-007",
    "severity": "high",
    "expected_reviewer": "cross-file-reviewer",
    "description": "Exported type changed but consumers not updated",
    "code": "// types.ts - field renamed from 'name' to 'displayName'\nexport interface User {\n  id: string;\n  displayName: string; // was: name\n  email: string;\n}\n\n// profile.tsx - still using old field name\n// <h1>{user.name}</h1>"
  },
  {
    "id": "eval-019",
    "language": "python",
    "failure_mode": "FM-007",
    "severity": "medium",
    "expected_reviewer": "cross-file-reviewer",
    "description": "Config key renamed but reader not updated",
    "code": "# config.py - key changed from 'db_url' to 'database_url'\nDEFAULT_CONFIG = {\n    'database_url': 'sqlite:///db.sqlite3',\n    'debug': False,\n}\n\n# app.py - still reading old key\n# db_url = config.get('db_url')"
  },
  {
    "id": "eval-020",
    "language": "go",
    "failure_mode": "FM-008",
    "severity": "high",
    "expected_reviewer": "code-reviewer",
    "description": "Error context lost in wrapping",
    "code": "func loadConfig(path string) (*Config, error) {\n\tdata, err := os.ReadFile(path)\n\tif err != nil {\n\t\treturn nil, errors.New(\"failed to load config\")\n\t}\n\treturn parseConfig(data)\n}"
  },
  {
    "id": "eval-021",
    "language": "typescript",
    "failure_mode": "FM-008",
    "severity": "high",
    "expected_reviewer": "code-reviewer",
    "description": "Error message misleading - swallows original error",
    "code": "async function saveUser(user: User): Promise<void> {\n  try {\n    await db.insert(user);\n  } catch (e) {\n    throw new Error('Failed to save user');\n  }\n}"
  },
  {
    "id": "eval-022",
    "language": "python",
    "failure_mode": "FM-008",
    "severity": "medium",
    "expected_reviewer": "code-reviewer",
    "description": "Retry without backoff or max attempts",
    "code": "def fetch_data(url: str) -> dict:\n    while True:\n        try:\n            return requests.get(url).json()\n        except requests.RequestException:\n            time.sleep(1)"
  },
  {
    "id": "eval-023",
    "language": "go",
    "failure_mode": "FM-009",
    "severity": "critical",
    "expected_reviewer": "code-reviewer",
    "description": "File handle not closed on error path",
    "code": "func processFile(path string) error {\n\tf, err := os.Open(path)\n\tif err != nil {\n\t\treturn err\n\t}\n\tdata, err := io.ReadAll(f)\n\tif err != nil {\n\t\treturn err // f is not closed!\n\t}\n\tf.Close()\n\treturn process(data)\n}"
  },
  {
    "id": "eval-024",
    "language": "typescript",
    "failure_mode": "FM-009",
    "severity": "high",
    "expected_reviewer": "code-reviewer",
    "description": "EventListener not removed causing memory leak",
    "code": "function setupTracker(element: HTMLElement) {\n  const handler = (e: MouseEvent) => track(e.clientX, e.clientY);\n  element.addEventListener('mousemove', handler);\n  // no cleanup function returned\n}"
  },
  {
    "id": "eval-025",
    "language": "python",
    "failure_mode": "FM-009",
    "severity": "high",
    "expected_reviewer": "code-reviewer",
    "description": "Database connection not closed in error path",
    "code": "def query_users(db_url: str) -> list:\n    conn = sqlite3.connect(db_url)\n    cursor = conn.cursor()\n    cursor.execute('SELECT * FROM users')\n    results = cursor.fetchall()\n    conn.close()\n    return results  # if execute raises, conn leaks"
  },
  {
    "id": "eval-026",
    "language": "go",
    "failure_mode": "FM-010",
    "severity": "critical",
    "expected_reviewer": "code-reviewer",
    "description": "Inverted boolean condition",
    "code": "func isAuthorized(user *User, resource string) bool {\n\tif !user.HasRole(\"admin\") || !user.HasPermission(resource) {\n\t\treturn true // should be false\n\t}\n\treturn false\n}"
  },
  {
    "id": "eval-027",
    "language": "typescript",
    "failure_mode": "FM-010",
    "severity": "high",
    "expected_reviewer": "code-reviewer",
    "description": "Short-circuit evaluation logic error",
    "code": "function canAccess(user: User | null, isPublic: boolean): boolean {\n  return user != null && isPublic || user?.isAdmin;\n  // missing parentheses: should be (user != null && isPublic) || user?.isAdmin\n}"
  },
  {
    "id": "eval-028",
    "language": "python",
    "failure_mode": "FM-010",
    "severity": "high",
    "expected_reviewer": "code-reviewer",
    "description": "Mutable default argument",
    "code": "def add_item(item: str, items: list = []) -> list:\n    items.append(item)\n    return items"
  },
  {
    "id": "eval-029",
    "language": "go",
    "failure_mode": "FM-001",
    "severity": "critical",
    "expected_reviewer": "code-reviewer",
    "description": "Nil map write panic",
    "code": "func collectTags(items []Item) map[string]int {\n\tvar counts map[string]int\n\tfor _, item := range items {\n\t\tfor _, tag := range item.Tags {\n\t\t\tcounts[tag]++ // nil map write\n\t\t}\n\t}\n\treturn counts\n}"
  },
  {
    "id": "eval-030",
    "language": "python",
    "failure_mode": "FM-005",
    "severity": "critical",
    "expected_reviewer": "security-reviewer",
    "description": "Command injection via subprocess",
    "code": "import subprocess\ndef run_lint(filename: str) -> str:\n    result = subprocess.run(f'eslint {filename}', shell=True, capture_output=True, text=True)\n    return result.stdout"
  }
]
```

各テストケースを既存の `tuples` 配列に追加する。

- [ ] **Step 2: テストケースの FM カバレッジを検証**

Run: `python3 -c "import json; data=json.load(open('.config/claude/scripts/eval/reviewer-eval-tuples.json')); fms=set(t['failure_mode'] for t in data['tuples']); print(f'FMs covered: {sorted(fms)}'); print(f'Total: {len(data[\"tuples\"])}'); langs={t['language'] for t in data['tuples']}; print(f'Languages: {sorted(langs)}')" `

Expected: FM-001〜FM-010 全カバー、Total: 30、Languages: go, python, rust, typescript

- [ ] **Step 3: コミット**

```bash
git add .config/claude/scripts/eval/reviewer-eval-tuples.json
git commit -m "✨ feat: expand reviewer eval tuples from 10 to 30 cases"
```

---

### Task 2: eval 実行スクリプトに出力パースロジック追加

**Files:**
- Modify: `.config/claude/scripts/eval/run_reviewer_eval.py`

- [ ] **Step 1: `parse_findings()` 関数を追加**

`run_single_eval()` の戻り値に `findings_count` (指摘総数) と `matched_fms` (マッチした FM リスト) を追加。

```python
import re

# FM keyword mapping for output parsing
FM_KEYWORDS: dict[str, list[str]] = {
    "FM-001": ["nil", "null", "undefined", "optional", "NullPointer", "nil pointer", "nil map"],
    "FM-002": ["silent", "swallow", "empty catch", "bare except", "ignored error", "_ ="],
    "FM-003": ["off-by-one", "boundary", "empty array", "zero-length", "empty string", "index out"],
    "FM-004": ["any type", "unsafe cast", "type assertion", "as unknown"],
    "FM-005": ["injection", "SQL", "XSS", "command injection", "shell=True", "innerHTML"],
    "FM-006": ["race condition", "goroutine leak", "shared state", "thread-unsafe", "concurrent"],
    "FM-007": ["signature change", "caller not updated", "interface mismatch", "import broken"],
    "FM-008": ["error context", "error message", "retry without", "backoff", "infinite retry"],
    "FM-009": ["resource leak", "not closed", "defer", "memory leak", "cleanup", "close()"],
    "FM-010": ["inverted", "logic error", "condition", "short-circuit", "mutable default"],
}


def parse_findings(output: str) -> dict:
    """Parse reviewer output to extract finding count and matched FMs."""
    # Count findings: lines with [MUST], [CONSIDER], [NIT], or file:line patterns
    finding_pattern = re.compile(
        r"(\[(?:MUST|CONSIDER|NIT|\d+)\]|[\w./]+:\d+\s*[—\-])"
    )
    findings = finding_pattern.findall(output)
    findings_count = len(findings)

    # Match FMs by keyword presence
    output_lower = output.lower()
    matched_fms: list[str] = []
    for fm, keywords in FM_KEYWORDS.items():
        if any(kw.lower() in output_lower for kw in keywords):
            matched_fms.append(fm)

    return {"findings_count": findings_count, "matched_fms": matched_fms}
```

- [ ] **Step 2: `run_single_eval()` を更新**

`detected = expected_fm in output` の行を以下に置換:

```python
    parsed = parse_findings(output)
    detected = expected_fm in parsed["matched_fms"]
    return {
        "eval_id": eval_id,
        "description": description,
        "expected_fm": expected_fm,
        "expected_reviewer": expected_reviewer,
        "status": "completed",
        "detected": detected,
        "pass": detected,
        "findings_count": parsed["findings_count"],
        "matched_fms": parsed["matched_fms"],
        "output_length": len(output),
    }
```

- [ ] **Step 3: `generate_summary()` に Recall/Precision/F1 を追加**

サマリーに全体 Recall/Precision/F1 セクションを追加:

```python
    # After existing per-FM table
    total_expected = len(completed)  # 1 FM per tuple
    total_detected = len(passed)     # detected = Recall numerator
    total_findings = sum(r.get("findings_count", 0) for r in completed)
    total_matched = sum(len(r.get("matched_fms", [])) for r in completed if r["pass"])

    recall = total_detected / total_expected if total_expected else 0
    precision = total_matched / total_findings if total_findings else 0
    f1 = 2 * recall * precision / (recall + precision) if (recall + precision) else 0

    lines.extend([
        "",
        "## Overall Metrics",
        "",
        f"- **Recall**: {recall:.1%} ({total_detected}/{total_expected})",
        f"- **Precision**: {precision:.1%} ({total_matched}/{total_findings})",
        f"- **F1**: {f1:.1%}",
    ])
```

- [ ] **Step 4: テスト（ドライラン）**

Run: `cd /Users/takeuchishougo/dotfiles && python3 .config/claude/scripts/eval/run_reviewer_eval.py --dry-run`
Expected: `Loaded 30 eval tuples` + 30 行の dry_run 結果

- [ ] **Step 5: コミット**

```bash
git add .config/claude/scripts/eval/run_reviewer_eval.py
git commit -m "✨ feat: add finding parser with Recall/Precision/F1 to eval runner"
```

---

### Task 3: 集約ベンチマークスクリプト新規作成

**Files:**
- Create: `.config/claude/scripts/eval/aggregate_benchmark.py`

- [ ] **Step 1: `aggregate_benchmark.py` を作成**

```python
#!/usr/bin/env python3
"""Aggregate reviewer eval results and generate Before/After comparison report.

Usage:
    python3 aggregate_benchmark.py --baseline results/baseline.json --current results/current.json
    python3 aggregate_benchmark.py --single results/2026-03-16-reviewer-eval.json
"""

import argparse
import json
import sys
from pathlib import Path


def compute_metrics(results: list[dict]) -> dict:
    """Compute Recall/Precision/F1 from eval results."""
    completed = [r for r in results if r["status"] == "completed"]
    if not completed:
        return {"recall": 0, "precision": 0, "f1": 0, "count": 0}

    detected = sum(1 for r in completed if r.get("pass"))
    total_expected = len(completed)
    total_findings = sum(r.get("findings_count", 0) for r in completed)
    total_correct = sum(
        len(r.get("matched_fms", [])) for r in completed if r.get("pass")
    )

    recall = detected / total_expected if total_expected else 0
    precision = total_correct / total_findings if total_findings else 0
    f1 = (
        2 * recall * precision / (recall + precision)
        if (recall + precision)
        else 0
    )

    return {
        "recall": round(recall, 4),
        "precision": round(precision, 4),
        "f1": round(f1, 4),
        "count": len(completed),
        "detected": detected,
        "total_findings": total_findings,
    }


def compute_per_fm(results: list[dict]) -> dict[str, dict]:
    """Compute per-FM detection rate."""
    completed = [r for r in results if r["status"] == "completed"]
    fm_stats: dict[str, dict] = {}
    for r in completed:
        fm = r["expected_fm"]
        if fm not in fm_stats:
            fm_stats[fm] = {"total": 0, "detected": 0}
        fm_stats[fm]["total"] += 1
        if r.get("pass"):
            fm_stats[fm]["detected"] += 1
    for stats in fm_stats.values():
        stats["rate"] = (
            round(stats["detected"] / stats["total"], 4)
            if stats["total"]
            else 0
        )
    return fm_stats


def format_single_report(metrics: dict, per_fm: dict[str, dict]) -> str:
    """Format a single benchmark report."""
    lines = [
        "# Reviewer Benchmark Report",
        "",
        "## Overall Metrics",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Recall | {metrics['recall']:.1%} |",
        f"| Precision | {metrics['precision']:.1%} |",
        f"| F1 | {metrics['f1']:.1%} |",
        f"| Cases | {metrics['count']} |",
        "",
        "## Per-FM Detection Rate",
        "",
        "| FM | Total | Detected | Rate |",
        "|----|-------|----------|------|",
    ]
    for fm, stats in sorted(per_fm.items()):
        lines.append(
            f"| {fm} | {stats['total']} | {stats['detected']} | {stats['rate']:.0%} |"
        )
    return "\n".join(lines)


def format_comparison_report(
    baseline_m: dict,
    current_m: dict,
    baseline_fm: dict[str, dict],
    current_fm: dict[str, dict],
) -> str:
    """Format a Before/After comparison report."""
    def delta(cur: float, base: float) -> str:
        d = cur - base
        sign = "+" if d >= 0 else ""
        return f"{sign}{d:.1%}"

    lines = [
        "# Reviewer Benchmark: Before/After Comparison",
        "",
        "## Overall Metrics",
        "",
        "| Metric | Baseline | Current | Delta |",
        "|--------|----------|---------|-------|",
        f"| Recall | {baseline_m['recall']:.1%} | {current_m['recall']:.1%} | {delta(current_m['recall'], baseline_m['recall'])} |",
        f"| Precision | {baseline_m['precision']:.1%} | {current_m['precision']:.1%} | {delta(current_m['precision'], baseline_m['precision'])} |",
        f"| F1 | {baseline_m['f1']:.1%} | {current_m['f1']:.1%} | {delta(current_m['f1'], baseline_m['f1'])} |",
        "",
        "## Per-FM Comparison",
        "",
        "| FM | Baseline Rate | Current Rate | Delta |",
        "|----|---------------|--------------|-------|",
    ]
    all_fms = sorted(set(list(baseline_fm.keys()) + list(current_fm.keys())))
    for fm in all_fms:
        b_rate = baseline_fm.get(fm, {}).get("rate", 0)
        c_rate = current_fm.get(fm, {}).get("rate", 0)
        lines.append(f"| {fm} | {b_rate:.0%} | {c_rate:.0%} | {delta(c_rate, b_rate)} |")

    # Success criteria check
    recall_delta = current_m["recall"] - baseline_m["recall"]
    precision_delta = current_m["precision"] - baseline_m["precision"]
    f1_delta = current_m["f1"] - baseline_m["f1"]

    lines.extend([
        "",
        "## Success Criteria",
        "",
        f"- Recall +10pt: {'PASS' if recall_delta >= 0.10 else 'FAIL'} ({delta(current_m['recall'], baseline_m['recall'])})",
        f"- Precision -5pt max: {'PASS' if precision_delta >= -0.05 else 'FAIL'} ({delta(current_m['precision'], baseline_m['precision'])})",
        f"- F1 +5pt: {'PASS' if f1_delta >= 0.05 else 'FAIL'} ({delta(current_m['f1'], baseline_m['f1'])})",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate benchmark results")
    parser.add_argument("--single", help="Single result JSON for standalone report")
    parser.add_argument("--baseline", help="Baseline result JSON for comparison")
    parser.add_argument("--current", help="Current result JSON for comparison")
    parser.add_argument(
        "--output", default=None, help="Output path (default: stdout)"
    )
    args = parser.parse_args()

    if args.single:
        with open(args.single) as f:
            results = json.load(f)
        metrics = compute_metrics(results)
        per_fm = compute_per_fm(results)
        report = format_single_report(metrics, per_fm)
    elif args.baseline and args.current:
        with open(args.baseline) as f:
            baseline = json.load(f)
        with open(args.current) as f:
            current = json.load(f)
        report = format_comparison_report(
            compute_metrics(baseline),
            compute_metrics(current),
            compute_per_fm(baseline),
            compute_per_fm(current),
        )
    else:
        parser.error("Provide --single or both --baseline and --current")
        return

    if args.output:
        Path(args.output).write_text(report + "\n")
        print(f"Report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 動作確認**

Run: `python3 .config/claude/scripts/eval/aggregate_benchmark.py --help`
Expected: ヘルプ出力が正常表示

- [ ] **Step 3: コミット**

```bash
git add .config/claude/scripts/eval/aggregate_benchmark.py
git commit -m "✨ feat: add aggregate benchmark script for Before/After comparison"
```

---

### Task 4: ベースライン計測

- [ ] **Step 1: 現行構成でフル eval 実行**

Run: `cd /Users/takeuchishougo/dotfiles && python3 .config/claude/scripts/eval/run_reviewer_eval.py`

これには時間がかかる（30 件 × 最大 60 秒 = 最大 30 分）。
結果は `scripts/eval/results/YYYY-MM-DD-reviewer-eval.json` に保存される。

- [ ] **Step 2: ベースライン結果をコピー**

```bash
cp .config/claude/scripts/eval/results/$(date +%Y-%m-%d)-reviewer-eval.json \
   .config/claude/scripts/eval/results/baseline-eval.json
```

- [ ] **Step 3: ベースラインレポート生成**

Run: `python3 .config/claude/scripts/eval/aggregate_benchmark.py --single .config/claude/scripts/eval/results/baseline-eval.json --output .config/claude/scripts/eval/results/baseline-report.md`

- [ ] **Step 4: コミット**

```bash
git add .config/claude/scripts/eval/results/baseline-eval.json .config/claude/scripts/eval/results/baseline-report.md
git commit -m "📊 chore: record baseline reviewer eval results"
```

---

## Chunk 2: 新エージェント + レビュースキル改善

### Task 5: `edge-case-hunter` エージェント作成

**Files:**
- Create: `.config/claude/agents/edge-case-hunter.md`

- [ ] **Step 1: エージェント定義ファイルを作成**

```markdown
---
name: edge-case-hunter
description: 境界値・異常系・nil パス・空コレクション・ゼロ値など「正常系では通らないパス」の検出に特化したレビューエージェント。エッジケースの見逃しを防ぐ。
tools: Read, Bash, Glob, Grep
model: sonnet
memory: user
maxTurns: 10
---

# Edge Case Hunter

## あなたの役割

コード変更に潜む「エッジケース」を専門的に検出するレビュアー。
正常系のテストでは通らないが、本番環境で発生しうる異常系パスを洗い出す。

## レビュー手順

1. `git diff` で変更差分を確認する
2. 変更されたファイルを Read で読んでコンテキストを理解する
3. 以下のチェック項目に沿って分析する
4. 指摘はファイルパスと行番号を `ファイルパス:行番号` 形式で明記する

## チェック項目

### 1. 空・nil・ゼロ値

入力やコレクションが空の場合に安全に動作するか。

- 空配列/空マップへの操作（`.length`, `.reduce()`, 添字アクセス）
- nil/null/undefined の dereference
- ゼロ値での除算
- 空文字列の処理（`s[0]`, `.split()`, `.trim()` の結果）
- 指摘例: "L12 で nums が空配列の場合、`nums.length` が 0 になりゼロ除算が発生"

### 2. 境界値

範囲の端で正しく動作するか。

- off-by-one エラー（スライス、ループ、配列インデックス）
- 整数オーバーフロー / アンダーフロー
- 最大値・最小値での挙動（`INT_MAX`, `Number.MAX_SAFE_INTEGER`）
- 負数入力の考慮
- 指摘例: "L8 の `items[len(items)-n-1:]` は n=0 の場合に範囲外アクセスになる"

### 3. 文字列・エンコーディング

文字列処理が多様な入力に耐えるか。

- Unicode/マルチバイト文字列での `.length` と実際の文字数の不一致
- 制御文字・改行・タブの混入
- 空白のみの文字列
- パス区切り文字の OS 差異

### 4. 日時・タイムゾーン

日時処理が正しいか。

- 月末（28日/29日/30日/31日）、閏年
- タイムゾーンの暗黙の前提（UTC vs ローカル）
- 日付をまたぐ処理
- サマータイムの考慮

### 5. 並行処理

並行・非同期処理のレースコンディション。

- 共有状態への同時書き込み
- goroutine/thread のリーク（終了条件の欠如）
- デッドロックの可能性
- fire-and-forget のエラー消失

### 6. リソース・I/O

外部リソースとのやり取りの異常系。

- ファイル不在・パーミッションエラーの考慮
- ネットワークタイムアウト・切断
- ディスク容量不足
- 同時オープンファイル数の上限

## 深刻度の判定基準

| 深刻度 | 基準 |
|--------|------|
| CRITICAL | パニック/クラッシュを引き起こす（nil dereference, index out of range） |
| HIGH | 不正な結果を返す（off-by-one, ゼロ除算で NaN） |
| MEDIUM | 特定条件でのみ発生し、デバッグが困難 |
| LOW | 理論上は起きうるが実害は限定的 |

## 出力フォーマット

各指摘に confidence score (0-100) を付与する。

```
## Edge Case Analysis

### CRITICAL
- [95] `file.go:12` — nil map への書き込みで panic。`counts` の初期化が必要
  → `counts := make(map[string]int)` で初期化

### HIGH
- [85] `utils.ts:8` — 空配列で `reduce` の初期値なしにより TypeError
  → 初期値を指定するか、空チェックを追加

（該当なし: "Edge Case Analysis: PASSED"）
```
```

- [ ] **Step 2: コミット**

```bash
git add .config/claude/agents/edge-case-hunter.md
git commit -m "✨ feat: add edge-case-hunter agent for boundary/nil path detection"
```

---

### Task 6: `cross-file-reviewer` エージェント作成

**Files:**
- Create: `.config/claude/agents/cross-file-reviewer.md`

- [ ] **Step 1: エージェント定義ファイルを作成**

```markdown
---
name: cross-file-reviewer
description: 変更が他ファイルに与える影響（インターフェース不整合、シグネチャ変更の未追従、import 破損）を検出するレビューエージェント。2ファイル以上の変更時に起動。
tools: Read, Bash, Glob, Grep
model: sonnet
memory: user
maxTurns: 12
---

# Cross-File Reviewer

## あなたの役割

複数ファイルにまたがるコード変更の「ファイル間整合性」を専門的に検出するレビュアー。
単一ファイルレビューでは見えない、ファイル境界をまたいだ不整合を発見する。

## レビュー手順

1. `git diff --name-only` で変更ファイル一覧を取得
2. `git diff` で全変更差分を確認
3. 変更ファイル間の依存関係を分析
4. Grep/Glob で変更された関数・型・定数の参照元を検索
5. 指摘はファイルパスと行番号を `ファイルパス:行番号` 形式で明記

## チェック項目

### 1. 関数シグネチャの不整合

関数の引数・戻り値が変更された場合、全呼び出し元が更新されているか。

- 引数の追加・削除・型変更
- 戻り値の型変更
- デフォルト引数の追加
- 検出方法: `Grep` で関数名を検索し、呼び出しパターンを確認

### 2. 型・インターフェースの不整合

型定義が変更された場合、全実装と全参照が更新されているか。

- フィールド名の変更（rename）
- 必須フィールドの追加
- フィールドの削除
- 型パラメータの変更
- 検出方法: `Grep` で型名を検索し、フィールドアクセスパターンを確認

### 3. Export / Import の不整合

モジュール境界の変更が参照側に反映されているか。

- export の追加・削除
- export 名の変更
- デフォルトエクスポートから名前付きエクスポートへの変更
- 検出方法: `Grep` で import 文を検索

### 4. 設定値・定数の不整合

設定キーや定数が変更された場合、参照箇所が更新されているか。

- 設定キーの rename
- 環境変数名の変更
- 定数値の変更が依存箇所に影響しないか
- 検出方法: `Grep` でキー名・定数名を検索

### 5. DB スキーマ・API コントラクトの不整合

データスキーマやAPIが変更された場合の整合性。

- カラム名の変更 → クエリ側の未対応
- APIレスポンス形状の変更 → クライアント側の未対応
- マイグレーションとコードの整合性

## 深刻度の判定基準

| 深刻度 | 基準 |
|--------|------|
| CRITICAL | コンパイルエラー/ランタイムエラーを引き起こす（型不一致、undefined field） |
| HIGH | 静的型チェックでは検出されないが実行時に問題になる |
| MEDIUM | 機能は動くが意図と異なる結果になる可能性 |
| LOW | 将来の変更で問題になる可能性 |

## 出力フォーマット

各指摘に confidence score (0-100) を付与する。

```
## Cross-File Analysis

### CRITICAL
- [95] `handler.go:23` → `user.go:5` — GetUser() のシグネチャが (string, bool) に変更されたが、handler.go の呼び出しは旧シグネチャのまま
  → handler.go:23 を `GetUser(id, false)` に更新

### HIGH
- [88] `profile.tsx:15` → `types.ts:3` — User.name が displayName に変更されたが、profile.tsx は user.name を参照
  → user.displayName に変更

（該当なし: "Cross-File Analysis: PASSED"）
```
```

- [ ] **Step 2: コミット**

```bash
git add .config/claude/agents/cross-file-reviewer.md
git commit -m "✨ feat: add cross-file-reviewer agent for interface consistency checks"
```

---

### Task 7: 信頼度3層化 + dedup + ブースト — reviewer-routing.md 更新

**Files:**
- Modify: `.config/claude/skills/review/references/reviewer-routing.md`

- [ ] **Step 1: 信頼度スコア表を3層に更新**

`reviewer-routing.md` の「信頼度スコアリング」セクションを更新。

`### フィルタリングルール` の内容を以下に置換:

```markdown
### フィルタリングルール（3層分類）

| 層 | スコア | ラベル | 扱い |
|----|--------|--------|------|
| Critical | 90-100 | 修正必須 | BLOCK 判定の根拠 |
| Important | 80-89 | 検討推奨 | NEEDS_FIX 判定の根拠 |
| Watch | 60-79 | 要注意 | 表示するが判定に影響しない。フィードバック収集用 |

以下の指摘は **自動除外** する（レポートに含めない）:

1. **confidence < 60** の指摘
2. **既存コードの問題**（diff の追加行以外への指摘）
3. **linter/formatter が検出すべき問題**（インデント、セミコロン等）
4. **純粋なスタイル nitpick**（命名規則の好み等、CLAUDE.md に明記がない限り）
```

- [ ] **Step 2: プロンプトへの追記セクションを更新**

信頼度フィルタのプロンプト指示を更新:

```markdown
### プロンプトへの追記

各レビューアーへのプロンプトに以下を追加:

\```
各指摘には confidence score (0-100) を付与してください。
60未満の指摘は報告不要です。
既存コード（diff の追加行以外）への指摘は除外してください。
linter/formatter が検出すべき問題は除外してください。

フォーマット例:
- [95] `file.ts:42` — NullPointerException の可能性。`user` が undefined の場合に crash
- [82] `api.go:128` — エラーが握り潰されている。`err` を返すべき
- [65] `utils.py:33` — 空リスト入力時の挙動が未定義。`if not items: return []` を検討
\```
```

- [ ] **Step 3: `edge-case-hunter` と `cross-file-reviewer` をルーティング表に追加**

コアレビューアーセクションの末尾に追加:

```markdown
### edge-case-hunter

- **subagent_type**: `edge-case-hunter`
- **観点**: 境界値、nil/null パス、空コレクション、ゼロ値、レースコンディション
- **起動条件**: 50行以上の変更で常に起動
- **信頼度スコア**: 60以上の指摘を報告

### cross-file-reviewer

- **subagent_type**: `cross-file-reviewer`
- **観点**: 関数シグネチャ変更の未追従、型不整合、export/import 破損、設定値変更の未追従
- **起動条件**: 変更ファイルが2つ以上の場合のみ起動
- **信頼度スコア**: 60以上の指摘を報告
```

- [ ] **Step 4: コミット**

```bash
git add .config/claude/skills/review/references/reviewer-routing.md
git commit -m "✨ feat: add 3-tier confidence, edge-case-hunter/cross-file-reviewer routing"
```

---

### Task 8: `/review` スキル本体更新

**Files:**
- Modify: `.config/claude/skills/review/SKILL.md`

- [ ] **Step 1: Step 2 スケーリング表を更新**

SKILL.md の `### レビュアー構成（行数ベース）` テーブルを以下に置換:

```markdown
| 変更規模 | 構成                                                                                                                                              |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| ~10行    | レビュー省略（Verify のみ）                                                                                                                       |
| ~50行    | `code-reviewer`（言語チェックリスト注入）+ `codex-reviewer` + `edge-case-hunter`（3並列）+ `cross-file-reviewer`（2+ファイル時のみ追加）           |
| ~200行   | `code-reviewer`（言語チェックリスト注入）+ `codex-reviewer` + `edge-case-hunter` + `golang-reviewer`（Go変更時）+ `cross-file-reviewer`（2+ファイル時） |
| 200行超  | 上記全て + スペシャリスト                                                                                                                         |
```

- [ ] **Step 2: Step 4 統合ルールにセマンティック dedup + ブーストを追加**

`統合ルール:` セクションの項目1を以下に置換:

```markdown
1. **セマンティック重複排除**: 同一ファイル ±10行以内 + 同一 failure_mode の指摘は最高信頼度の1件に統合。統合元は「(他 N 件のレビューアーも同様の指摘)」と注記
2. **信頼度ブースト**: 複数の独立したレビューアーが同じ問題を指摘した場合、信頼度を `max(scores) + 5`（上限100）に引き上げ
3. **対立検出**: 同じ箇所で矛盾する指摘がある場合、両方残して `[CONFLICT]` タグを付与
4. **重要度順**: Critical → Important → Watch の順に整理
5. **アクション明示**: 各指摘に対して「修正必須」「検討推奨」「要注意」を付与
6. **判定**: Critical が1件以上 → BLOCK。Important が3件以上 → NEEDS_FIX。それ以外 → PASS。Watch は判定に影響しない
7. **信頼度フィルタ**: confidence < 60 の指摘を除外
8. **既存コード除外**: diff の追加行以外への指摘を除外
9. **linter 重複除外**: フォーマッター・linter が検出すべき問題を除外
10. **戦略的整合性**: spec file 存在時、product-reviewer の「spec 不整合」指摘は Critical として扱う
```

- [ ] **Step 3: コミット**

```bash
git add .config/claude/skills/review/SKILL.md
git commit -m "✨ feat: integrate edge-case-hunter, cross-file-reviewer, 3-tier confidence, dedup"
```

---

### Task 9: review-output テンプレート更新

**Files:**
- Modify: `.config/claude/skills/review/templates/review-output.md`

- [ ] **Step 1: Watch 層セクションを追加**

`### Suggestion（参考）` セクションの後に Watch 層を追加:

```markdown
### Watch（要注意 — 参考情報）

> confidence 60-79 の指摘。判定 (PASS/NEEDS_FIX/BLOCK) には影響しない。
> フィードバックにより将来の閾値調整に活用される。

- **[{score}]** **[{レビューアー名}]** `{file}:{line}` — {指摘内容}
  → {推奨修正}
```

- [ ] **Step 2: 重要度マッピング表を更新**

```markdown
| レビューアーの表現                                   | 統合後の重要度 | スコア条件 |
| ---------------------------------------------------- | -------------- | ---------- |
| MUST, Critical, CRITICAL, 90-100                     | **Critical**   | ≥90        |
| CONSIDER, Important, HIGH, 80-89                     | **Important**  | ≥80        |
| Watch, MEDIUM, 60-79                                 | **Watch**      | ≥60        |
| （60未満はフィルタ済みのため出力しない）              | —              | <60 除外   |
```

- [ ] **Step 3: 判定ルールを更新**

```markdown
- **PASS**: Critical・Important の指摘なし。Watch のみ、または指摘なし
- **NEEDS_FIX**: Important が3件以上。修正後に再レビュー推奨
- **BLOCK**: Critical が1件以上。修正必須
```

- [ ] **Step 4: コミット**

```bash
git add .config/claude/skills/review/templates/review-output.md
git commit -m "✨ feat: add Watch tier to review output template"
```

---

## Chunk 3: 改善後計測 + 比較

### Task 10: 改善後の eval 実行 + 比較レポート生成

- [ ] **Step 1: 改善後構成でフル eval 実行**

Run: `python3 .config/claude/scripts/eval/run_reviewer_eval.py`

結果: `scripts/eval/results/YYYY-MM-DD-reviewer-eval.json`

- [ ] **Step 2: 結果をコピー**

```bash
cp .config/claude/scripts/eval/results/$(date +%Y-%m-%d)-reviewer-eval.json \
   .config/claude/scripts/eval/results/current-eval.json
```

- [ ] **Step 3: Before/After 比較レポート生成**

```bash
python3 .config/claude/scripts/eval/aggregate_benchmark.py \
  --baseline .config/claude/scripts/eval/results/baseline-eval.json \
  --current .config/claude/scripts/eval/results/current-eval.json \
  --output .config/claude/scripts/eval/results/comparison-report.md
```

- [ ] **Step 4: 結果を確認し、成功基準を検証**

レポートの Success Criteria セクションで:
- Recall +10pt: PASS/FAIL
- Precision -5pt max: PASS/FAIL
- F1 +5pt: PASS/FAIL

- [ ] **Step 5: コミット**

```bash
git add .config/claude/scripts/eval/results/
git commit -m "📊 chore: record post-improvement reviewer eval results with comparison"
```

---

### Task 11: evaluator_metrics.py に Watch フィードバック対応追加

**Files:**
- Modify: `.config/claude/scripts/lib/evaluator_metrics.py`

- [ ] **Step 1: `_build_feedback_map()` を拡張**

Watch 層の outcome（`watch_useful`, `watch_noise`）を処理できるようにする:

```python
def _build_feedback_map(feedback: list[dict]) -> dict[str, str]:
    """Build a mapping from finding_id to outcome.

    Supports outcomes: accepted, ignored, watch_useful, watch_noise.
    """
    return {
        entry["finding_id"]: entry["outcome"]
        for entry in feedback
        if "finding_id" in entry and "outcome" in entry
    }
```

- [ ] **Step 2: `_compute_accuracy_by()` で Watch 層カウントを追加**

```python
    for finding in findings:
        # ... existing code ...
        if key not in groups:
            groups[key] = {
                "total": 0, "accepted": 0, "ignored": 0,
                "watch_useful": 0, "watch_noise": 0,
            }

        outcome = feedback_map[finding_id]
        groups[key]["total"] += 1
        if outcome == "accepted":
            groups[key]["accepted"] += 1
        elif outcome == "ignored":
            groups[key]["ignored"] += 1
        elif outcome == "watch_useful":
            groups[key]["watch_useful"] += 1
        elif outcome == "watch_noise":
            groups[key]["watch_noise"] += 1
```

- [ ] **Step 3: テスト実行**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest tests/scripts/test_evaluator_metrics.py -v`
Expected: 既存テスト 9 件が PASS

- [ ] **Step 4: コミット**

```bash
git add .config/claude/scripts/lib/evaluator_metrics.py
git commit -m "✨ feat: add watch_useful/watch_noise outcome support to evaluator_metrics"
```
