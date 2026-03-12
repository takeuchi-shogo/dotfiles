#!/usr/bin/env python3
"""Reviewer eval runner — Synthetic Tuple テストを実行する。

各タプルのコードをレビューエージェントに渡し、
期待される failure_mode が検出されたかを判定する。

Usage:
    python3 run_reviewer_eval.py [--tuples reviewer-eval-tuples.json] [--dry-run]

出力:
    eval/results/YYYY-MM-DD-reviewer-eval.json — 個別結果
    eval/results/YYYY-MM-DD-reviewer-eval-summary.md — サマリーレポート
"""

import argparse
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path


def load_tuples(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("tuples", [])


def run_single_eval(tuple_data: dict, dry_run: bool = False) -> dict:
    """1つのタプルに対してレビューを実行し、結果を返す。"""
    eval_id = tuple_data["id"]
    code = tuple_data["code"]
    language = tuple_data["language"]
    expected_fm = tuple_data["failure_mode"]
    expected_reviewer = tuple_data["expected_reviewer"]
    description = tuple_data["description"]

    prompt = f"""以下のコードをレビューしてください。バグやセキュリティ問題を見つけてください。

```{language}
{code}
```

各指摘には以下を含めてください:
- confidence score (0-100)
- failure_mode (FM-XXX 形式、references/failure-taxonomy.md 参照)
- 問題の説明

80未満の指摘は報告不要です。"""

    if dry_run:
        return {
            "eval_id": eval_id,
            "description": description,
            "expected_fm": expected_fm,
            "expected_reviewer": expected_reviewer,
            "status": "dry_run",
            "detected": None,
            "pass": None,
        }

    try:
        result = subprocess.run(
            [
                "claude",
                "-p",
                prompt,
                "--allowedTools",
                "Read,Grep,Glob",
                "--model",
                "sonnet",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return {
            "eval_id": eval_id,
            "description": description,
            "expected_fm": expected_fm,
            "expected_reviewer": expected_reviewer,
            "status": "error",
            "error": str(exc),
            "detected": False,
            "pass": False,
        }

    detected = expected_fm in output
    return {
        "eval_id": eval_id,
        "description": description,
        "expected_fm": expected_fm,
        "expected_reviewer": expected_reviewer,
        "status": "completed",
        "detected": detected,
        "pass": detected,
        "output_length": len(output),
    }


def generate_summary(results: list[dict], output_dir: Path) -> str:
    """サマリーレポートを生成する。"""
    total = len(results)
    completed = [r for r in results if r["status"] == "completed"]
    passed = [r for r in completed if r["pass"]]

    by_fm: dict[str, dict] = {}
    for r in completed:
        fm = r["expected_fm"]
        if fm not in by_fm:
            by_fm[fm] = {"total": 0, "passed": 0}
        by_fm[fm]["total"] += 1
        if r["pass"]:
            by_fm[fm]["passed"] += 1

    lines = [
        f"# Reviewer Eval Summary — {datetime.now().strftime('%Y-%m-%d')}",
        "",
        f"**Total**: {total} | **Completed**: {len(completed)} | "
        f"**Passed**: {len(passed)} | **Detection Rate**: "
        f"{len(passed) / len(completed) * 100:.0f}%"
        if completed
        else "N/A",
        "",
        "## Results by Failure Mode",
        "",
        "| FM | Total | Passed | Rate |",
        "|----|-------|--------|------|",
    ]
    for fm, stats in sorted(by_fm.items()):
        rate = stats["passed"] / stats["total"] * 100 if stats["total"] else 0
        lines.append(f"| {fm} | {stats['total']} | {stats['passed']} | {rate:.0f}% |")

    lines.extend(["", "## Individual Results", ""])
    for r in results:
        status = (
            "PASS"
            if r.get("pass")
            else "FAIL"
            if r["status"] == "completed"
            else r["status"].upper()
        )
        lines.append(
            f"- **{r['eval_id']}** [{status}] {r['description']} (expected: {r['expected_fm']})"
        )

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run reviewer eval tuples")
    parser.add_argument(
        "--tuples",
        default=os.path.join(os.path.dirname(__file__), "reviewer-eval-tuples.json"),
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    tuples = load_tuples(args.tuples)
    print(f"Loaded {len(tuples)} eval tuples")

    results = []
    for t in tuples:
        print(f"  Running {t['id']}: {t['description']}...", end=" ", flush=True)
        result = run_single_eval(t, dry_run=args.dry_run)
        results.append(result)
        status = (
            "PASS"
            if result.get("pass")
            else "FAIL"
            if result["status"] == "completed"
            else result["status"]
        )
        print(status)

    output_dir = Path(os.path.dirname(__file__)) / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    results_path = output_dir / f"{date_str}-reviewer-eval.json"
    summary_path = output_dir / f"{date_str}-reviewer-eval-summary.md"

    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    summary = generate_summary(results, output_dir)
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"\nResults: {results_path}")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
