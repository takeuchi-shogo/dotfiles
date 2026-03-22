#!/usr/bin/env -S uv run --with pyyaml python3
"""Claude Code セットアップ自己評価クイズ CLI."""

import argparse
import random
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML が必要です: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

QUESTIONS_DIR = Path(__file__).parent / "questions"

PROFILES = {
    "beginner": {
        "count": 10,
        "weights": {"beginner": 6, "intermediate": 3, "advanced": 1},
    },
    "intermediate": {
        "count": 20,
        "weights": {"beginner": 3, "intermediate": 10, "advanced": 7},
    },
    "advanced": {
        "count": 30,
        "weights": {"beginner": 3, "intermediate": 9, "advanced": 18},
    },
}

DIFFICULTY_LABELS = {"beginner": "初級", "intermediate": "中級", "advanced": "上級"}


def load_questions(categories: list[str] | None = None) -> list[dict]:
    """YAML ファイルから問題を読み込む."""
    questions = []
    for path in sorted(QUESTIONS_DIR.glob("*.yaml")):
        with open(path) as f:
            data = yaml.safe_load(f)
        if categories and data["category"] not in categories:
            continue
        for q in data["questions"]:
            q["category_label"] = data["label"]
        questions.extend(data["questions"])
    return questions


def select_questions(questions: list[dict], profile: str) -> list[dict]:
    """プロファイルに応じた重み付きサンプリング."""
    cfg = PROFILES[profile]
    by_diff: dict[str, list[dict]] = {
        "beginner": [],
        "intermediate": [],
        "advanced": [],
    }
    for q in questions:
        by_diff[q["difficulty"]].append(q)

    selected = []
    for diff, target in cfg["weights"].items():
        pool = by_diff[diff]
        random.shuffle(pool)
        selected.extend(pool[:target])

    random.shuffle(selected)
    return selected[: cfg["count"]]


def run_quiz(questions: list[dict]) -> None:
    """対話型クイズを実行."""
    total = len(questions)
    correct = 0
    results = []

    print(f"\n{'=' * 50}")
    print(f"  Claude Code セルフクイズ ({total} 問)")
    print(f"{'=' * 50}\n")

    for i, q in enumerate(questions, 1):
        diff_label = DIFFICULTY_LABELS[q["difficulty"]]
        print(f"Q{i}/{total} [{diff_label}] [{q['category_label']}]")
        print(f"  {q['question']}\n")
        for key in ("a", "b", "c", "d"):
            print(f"    {key}) {q['choices'][key]}")
        print()

        while True:
            ans = input("  回答 (a/b/c/d): ").strip().lower()
            if ans in ("a", "b", "c", "d"):
                break
            print("  a, b, c, d のいずれかを入力してください。")

        is_correct = ans == q["answer"]
        if is_correct:
            correct += 1
            print("  -> 正解!\n")
        else:
            print(f"  -> 不正解。正解は {q['answer']}) {q['choices'][q['answer']]}")
            print(f"     {q['explanation']}\n")

        results.append({"question": q, "user_answer": ans, "correct": is_correct})

    print(f"{'=' * 50}")
    print(f"  結果: {correct}/{total} ({correct * 100 // total}%)")
    print(f"{'=' * 50}\n")

    by_cat: dict[str, list[bool]] = {}
    for r in results:
        cat = r["question"]["category_label"]
        by_cat.setdefault(cat, []).append(r["correct"])

    print("カテゴリ別:")
    for cat, scores in sorted(by_cat.items()):
        cat_correct = sum(scores)
        cat_total = len(scores)
        bar = "#" * cat_correct + "." * (cat_total - cat_correct)
        print(f"  {cat:<16} [{bar}] {cat_correct}/{cat_total}")

    print()
    if correct * 100 // total >= 80:
        print("素晴らしい! セットアップを深く理解しています。")
    elif correct * 100 // total >= 50:
        print("基礎は固まっています。間違えた分野を重点的に復習しましょう。")
    else:
        print("references/ と skills/ を読み直すことをお勧めします。")


def main() -> None:
    parser = argparse.ArgumentParser(description="Claude Code セルフクイズ")
    parser.add_argument(
        "profile",
        nargs="?",
        default="intermediate",
        choices=PROFILES.keys(),
        help="難易度プロファイル (default: intermediate)",
    )
    parser.add_argument(
        "--category", "-c", action="append", help="カテゴリで絞り込み (複数指定可)"
    )
    parser.add_argument(
        "--list-categories", action="store_true", help="利用可能なカテゴリを表示"
    )
    args = parser.parse_args()

    if args.list_categories:
        for path in sorted(QUESTIONS_DIR.glob("*.yaml")):
            with open(path) as f:
                data = yaml.safe_load(f)
            print(
                f"  {data['category']:<20} {data['label']} ({len(data['questions'])}問)"
            )
        return

    questions = load_questions(args.category)
    if not questions:
        print("問題が見つかりません。", file=sys.stderr)
        sys.exit(1)

    selected = select_questions(questions, args.profile)
    try:
        run_quiz(selected)
    except (KeyboardInterrupt, EOFError):
        print("\n\nクイズを中断しました。")
        sys.exit(0)


if __name__ == "__main__":
    main()
