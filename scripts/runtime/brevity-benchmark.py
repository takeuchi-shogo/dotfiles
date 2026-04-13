#!/usr/bin/env python3
"""Brevity Benchmark — caveman / genshijin 主張を実測検証するスクリプト

検証対象:
  - caveman: 英語 brevity で ~68% トークン削減
  - genshijin: 日本語 brevity で ~80% 削減
  - 主張3: 日本語は英語より 12pt (68%→80%) 追加削減可能

同一プロンプトを 4 条件 (default / lite / standard / ultra) で
`claude -p` に sequential 実行し、tiktoken (o200k_base) で出力トークン数を計測する。

Usage:
  brevity-benchmark.py --prompt "Python の async/await を説明して"
  brevity-benchmark.py --file prompts.jsonl
  brevity-benchmark.py --prompt "..." --output .skill-eval/brevity/results.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# サブモジュールを同一ディレクトリから解決するためパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from _brevity_runner import run_benchmark  # noqa: E402
from _brevity_summary import print_summary  # noqa: E402
from _brevity_types import DEFAULT_PROMPTS, DIM, RED, RESET  # noqa: E402

# ── CLI ──────────────────────────────────────────────────────

_HELP_OUTPUT = (
    "結果 JSON の出力先 (デフォルト: .skill-eval/brevity/{timestamp}/results.json)"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="brevity-benchmark.py",
        description=(
            "caveman / genshijin の brevity 削減主張を実測検証。\n"
            "4条件 (default/lite/standard/ultra) で claude -p を実行し、\n"
            "tiktoken でトークン数を計測してサマリを出力する。"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  brevity-benchmark.py --prompt 'Python の async/await を説明して'\n"
            "  brevity-benchmark.py --file prompts.jsonl\n"
            "  brevity-benchmark.py --output .skill-eval/brevity/results.json\n"
            "\n"
            "JSONL format (--file):\n"
            '  {"id": "my-prompt", "prompt": "...", "lang": "ja"}\n'
            '  {"id": "my-prompt2", "prompt": "...", "lang": "en"}\n'
        ),
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--prompt", metavar="TEXT", help="単一プロンプトをベンチマーク")
    group.add_argument(
        "--file",
        metavar="JSONL",
        type=Path,
        help="複数プロンプトを JSONL ファイルから読み込み",
    )
    parser.add_argument(
        "--output", metavar="PATH", type=Path, default=None, help=_HELP_OUTPUT
    )
    parser.add_argument(
        "--lang",
        choices=["ja", "en"],
        default="ja",
        help="--prompt 使用時の言語指定 (default: ja)",
    )
    parser.add_argument(
        "--id",
        metavar="ID",
        default="prompt",
        help="--prompt 使用時のプロンプト ID (default: prompt)",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="stderr など追加情報を表示"
    )
    return parser


def load_prompts_from_file(path: Path) -> list[dict]:
    """JSONL ファイルからプロンプトリストを読み込む。"""
    if not path.exists():
        sys.exit(f"{RED}ERROR{RESET}: ファイルが見つかりません: {path}")

    prompts: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                sys.exit(f"{RED}ERROR{RESET}: JSONL パース失敗 (line {lineno}): {e}")
            if "prompt" not in entry:
                msg = f"line {lineno} に 'prompt' キーがありません: {entry}"
                sys.exit(f"{RED}ERROR{RESET}: {msg}")
            entry.setdefault("id", f"prompt-{lineno}")
            entry.setdefault("lang", "ja")
            prompts.append(entry)

    if not prompts:
        sys.exit(f"{RED}ERROR{RESET}: JSONL ファイルが空です: {path}")
    return prompts


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.prompt:
        prompts = [{"id": args.id, "prompt": args.prompt, "lang": args.lang}]
    elif args.file:
        prompts = load_prompts_from_file(args.file)
    else:
        prompts = DEFAULT_PROMPTS
        msg = "引数未指定のためデフォルトプロンプトセット (6件) を使用します。"
        print(f"{DIM}{msg}{RESET}")

    results = run_benchmark(prompts, args.output, verbose=args.verbose)
    print_summary(results)


if __name__ == "__main__":
    main()
