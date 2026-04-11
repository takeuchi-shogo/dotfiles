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
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── 依存チェック ────────────────────────────────────────

try:
    import tiktoken
except ImportError:
    sys.exit(
        "tiktoken required. Install with: pip install tiktoken\n"
        "  or: uv pip install tiktoken"
    )

# ── 定数・カラーコード ───────────────────────────────────

# 個人環境の優先パス。無ければ get_claude_bin() で PATH から解決。
CLAUDE_BIN_DEFAULT = "/Users/takeuchishougo/.local/bin/claude"
_claude_bin_cache: Optional[str] = None

RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

ENCODING_NAME = "o200k_base"

ARM_SLEEP_SEC = 1.0  # arm 間の sleep
PROMPT_SLEEP_SEC = 2.0  # プロンプト間の sleep
TIMEOUT_SEC = 120  # claude 呼び出し per-arm タイムアウト

# 内容妥当性検証: default の 5% 未満のトークンしか返さない異常応答を警告する閾値。
# ultra 条件で claude が「理解不能です」等の1文だけ返した場合の偽陽性防止。
MIN_CONTENT_RATIO = 0.05

# ── brevity システムメッセージ ───────────────────────────
# concise.md の強度グラデーションに合わせ lite/standard/ultra を段階化する。
# lite = Drop リスト（英語 + 日本語フィラー）のみ
# standard = lite + 体言止め + 助詞圧縮
# ultra = standard + 箇条書き + 接続詞削除

_BASE_BREVITY = (
    "Remove filler, hedging, and pleasantries from your response. "
    "No preamble, no recap, no trailing summary."
)
_JA_DROP_LIST = (
    "日本語フィラー（なるほど、確認しました、それでは、まず）、"
    "クッション語（〜と思います、〜かもしれません、もしかして、〜っぽい）、"
    "結果要約（以上のように、つまり、要するに）も削除する。"
)
_JA_STRUCT_BREVITY = (
    "日本語応答では: 敬語を体言止めに変換し、文脈から自明な助詞を省略する。"
)

SYSTEM_PROMPTS: dict[str, str] = {
    "default": "",  # システムプロンプト追加なし
    "lite": f"{_BASE_BREVITY} {_JA_DROP_LIST}",
    "standard": f"{_BASE_BREVITY} {_JA_DROP_LIST} {_JA_STRUCT_BREVITY}",
    "ultra": (
        f"{_BASE_BREVITY} {_JA_DROP_LIST} {_JA_STRUCT_BREVITY} "
        "箇条書き優先、接続詞削除、一文一事実。"
    ),
}

ARM_ORDER = ["default", "lite", "standard", "ultra"]

# ── デフォルトプロンプトセット ───────────────────────────

DEFAULT_PROMPTS: list[dict] = [
    {"id": "ja-cors", "prompt": "CORS エラーの原因と対処を教えて", "lang": "ja"},
    {
        "id": "ja-loop",
        "prompt": "JavaScript のイベントループを説明して",
        "lang": "ja",
    },
    {
        "id": "ja-auth",
        "prompt": "認証トークンの検証でバグが出ている。原因の候補は？",
        "lang": "ja",
    },
    {
        "id": "en-cors",
        "prompt": "Explain the cause and fix for CORS errors",
        "lang": "en",
    },
    {
        "id": "en-loop",
        "prompt": "Explain the JavaScript event loop",
        "lang": "en",
    },
    {
        "id": "en-auth",
        "prompt": "Auth token validation has a bug. What are likely causes?",
        "lang": "en",
    },
]

# ── データ構造 ────────────────────────────────────────────


@dataclass
class ArmResult:
    tokens: int
    char_count: int
    reduction_pct: Optional[float] = None  # default arm には None


@dataclass
class PromptResult:
    prompt_id: str
    lang: str
    prompt_text: str
    arms: dict[str, ArmResult] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)


# ── ヘルパー関数 ─────────────────────────────────────────


def format_tokens(n: int) -> str:
    """token 数を人間が読みやすい形式にフォーマット。"""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def count_tokens(text: str) -> int:
    """tiktoken (o200k_base) でテキストのトークン数を返す。"""
    enc = tiktoken.get_encoding(ENCODING_NAME)
    return len(enc.encode(text))


def get_claude_bin() -> str:
    """claude バイナリパスを解決してキャッシュする。

    優先順位:
      1. CLAUDE_BIN_DEFAULT のハードコードパス
      2. PATH 上の `claude`（`which claude` で解決）

    見つからなければ sys.exit で終了。
    """
    global _claude_bin_cache
    if _claude_bin_cache is not None:
        return _claude_bin_cache

    p = Path(CLAUDE_BIN_DEFAULT)
    if p.exists():
        _claude_bin_cache = str(p)
        return _claude_bin_cache

    # PATH 上も探す
    which_result = subprocess.run(
        ["which", "claude"],
        capture_output=True,
        text=True,
        check=False,
    )
    if which_result.returncode == 0 and which_result.stdout.strip():
        _claude_bin_cache = which_result.stdout.strip()
        return _claude_bin_cache

    sys.exit(
        f"{RED}ERROR{RESET}: claude CLI が見つかりません。\n"
        f"  試行したパス: {CLAUDE_BIN_DEFAULT}\n"
        f"  PATH 上にも 'claude' がありません。\n"
        "  Claude Code をインストールしてください。"
    )


def sanitize_stderr(text: str) -> str:
    """stderr から秘密情報らしきパターンをマスクする。ログ出力前に必ず通す。"""
    patterns = [
        r"(token|session|auth|key|secret|api[-_]?key)\s*[:=]\s*\S+",
        r"Bearer\s+\S+",
    ]
    for pat in patterns:
        text = re.sub(pat, r"[REDACTED]", text, flags=re.IGNORECASE)
    return text


def run_claude(
    prompt: str, system_prompt: str, timeout: int = TIMEOUT_SEC
) -> tuple[str, str]:
    """claude -p を実行し (stdout, stderr) を返す。

    system_prompt が空の場合は --append-system-prompt を付与しない。
    non-zero exit 時は RuntimeError を raise する（stderr は sanitize される）。
    タイムアウト時は TimeoutExpired を raise する。

    Security:
      - shell=False (list 形式) でシェルインジェクションは防がれる
      - `--` セパレータでプロンプトがオプションとして誤解釈されるのを防ぐ
      - `--dangerously-skip-permissions` は benchmark 自動実行のため必須
    """
    cmd = [get_claude_bin(), "-p", "--dangerously-skip-permissions"]
    if system_prompt:
        cmd += ["--append-system-prompt", system_prompt]
    # `--` 以降はすべて位置引数として解釈される
    cmd += ["--", prompt]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,  # returncode を自前で見るため False
    )
    if result.returncode != 0:
        err_msg = sanitize_stderr((result.stderr or "").strip())[:300]
        raise RuntimeError(f"claude CLI failed (exit {result.returncode}): {err_msg}")
    return result.stdout, result.stderr


def save_raw_response(run_dir: Path, prompt_id: str, arm: str, text: str) -> None:
    """生レスポンスをファイルに保存する。"""
    run_dir.mkdir(parents=True, exist_ok=True)
    out_path = run_dir / f"{prompt_id}-{arm}.txt"
    out_path.write_text(text, encoding="utf-8")


# ── コア計測ロジック ─────────────────────────────────────


def benchmark_prompt(
    entry: dict,
    run_dir: Path,
    verbose: bool = False,
) -> PromptResult:
    """単一プロンプトを 4 アームで計測する。"""
    prompt_id = entry.get("id", "prompt")
    prompt_text = entry["prompt"]
    lang = entry.get("lang", "ja")

    result = PromptResult(
        prompt_id=prompt_id,
        lang=lang,
        prompt_text=prompt_text,
    )

    print(
        f"\n{BOLD}[{prompt_id}]{RESET} ({lang}) {DIM}{prompt_text[:60]}...{RESET}"
        if len(prompt_text) > 60
        else f"\n{BOLD}[{prompt_id}]{RESET} ({lang}) {DIM}{prompt_text}{RESET}"
    )

    default_tokens: Optional[int] = None

    for arm in ARM_ORDER:
        sys_prompt = SYSTEM_PROMPTS[arm]
        print(f"  {CYAN}{arm:<10}{RESET}", end="", flush=True)

        try:
            stdout, stderr = run_claude(prompt_text, sys_prompt)
        except subprocess.TimeoutExpired:
            msg = f"timeout after {TIMEOUT_SEC}s"
            result.errors[arm] = msg
            print(f" {RED}TIMEOUT{RESET}")
            time.sleep(ARM_SLEEP_SEC)
            continue
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            result.errors[arm] = msg
            print(f" {RED}ERROR{RESET}: {msg}")
            time.sleep(ARM_SLEEP_SEC)
            continue

        if not stdout.strip():
            msg = f"empty response (stderr: {stderr.strip()[:100]})"
            result.errors[arm] = msg
            print(f" {YELLOW}EMPTY{RESET}: {msg}")
            time.sleep(ARM_SLEEP_SEC)
            continue

        # 保存
        save_raw_response(run_dir, prompt_id, arm, stdout)

        tokens = count_tokens(stdout)
        char_count = len(stdout)

        # 削減率計算
        reduction_pct: Optional[float] = None
        if arm == "default":
            default_tokens = tokens
        elif default_tokens and default_tokens > 0:
            reduction_pct = round((1 - tokens / default_tokens) * 100, 1)

        arm_result = ArmResult(
            tokens=tokens,
            char_count=char_count,
            reduction_pct=reduction_pct,
        )
        result.arms[arm] = arm_result

        # 進捗表示
        color = (
            GREEN
            if (reduction_pct or 0) >= 60
            else YELLOW
            if (reduction_pct or 0) >= 30
            else DIM
        )
        pct_str = (
            f" {color}-{reduction_pct:.1f}%{RESET}" if reduction_pct is not None else ""
        )
        print(f" {format_tokens(tokens):>6} tokens ({char_count:>5} chars){pct_str}")

        if verbose and stderr.strip():
            print(f"    {DIM}stderr: {stderr.strip()[:80]}{RESET}")

        if arm != ARM_ORDER[-1]:
            time.sleep(ARM_SLEEP_SEC)

    return result


def run_benchmark(
    prompts: list[dict],
    output_path: Optional[Path],
    verbose: bool = False,
) -> list[PromptResult]:
    """全プロンプトのベンチマークを実行し結果を返す。"""
    get_claude_bin()  # 起動時に解決（見つからなければ sys.exit）

    # 実行ディレクトリ作成
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path(".skill-eval/brevity") / timestamp

    print(f"\n{BOLD}{'=' * 60}")
    print("  Brevity Benchmark")
    print(f"{'=' * 60}{RESET}")
    print(
        f"  prompts: {len(prompts)}, arms: {len(ARM_ORDER)}, encoding: {ENCODING_NAME}"
    )
    print(f"  run_dir: {run_dir}")

    all_results: list[PromptResult] = []

    for i, entry in enumerate(prompts):
        result = benchmark_prompt(entry, run_dir, verbose=verbose)
        all_results.append(result)

        if i < len(prompts) - 1:
            time.sleep(PROMPT_SLEEP_SEC)

    # JSON 出力
    if output_path is None:
        output_path = run_dir / "results.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    serializable = []
    for r in all_results:
        d = {
            "prompt_id": r.prompt_id,
            "lang": r.lang,
            "prompt_text": r.prompt_text,
            "arms": {arm: asdict(ar) for arm, ar in r.arms.items()},
        }
        if r.errors:
            d["errors"] = r.errors
        serializable.append(d)

    output_path.write_text(
        json.dumps(serializable, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n{DIM}results saved: {output_path}{RESET}")

    return all_results


# ── サマリテーブル ───────────────────────────────────────


def _avg_reduction(
    results: list[PromptResult], lang: str, from_arm: str, to_arm: str
) -> Optional[float]:
    """指定言語・アーム間の平均削減率を返す。"""
    values: list[float] = []
    for r in results:
        if r.lang != lang:
            continue
        if from_arm not in r.arms or to_arm not in r.arms:
            continue
        from_tokens = r.arms[from_arm].tokens
        to_tokens = r.arms[to_arm].tokens
        if from_tokens > 0:
            values.append((1 - to_tokens / from_tokens) * 100)
    if not values:
        return None
    return sum(values) / len(values)


def _pass_warn(actual: float, claim: float, tolerance: float = 5.0) -> str:
    """主張との比較結果を PASS/WARN で返す。"""
    if actual >= claim - tolerance:
        return f"{GREEN}PASS{RESET}"
    return f"{YELLOW}WARN{RESET}"


def _print_lang_block(
    results: list[PromptResult],
    lang: str,
    label: str,
    std_claim: Optional[float] = None,
    ult_claim: Optional[float] = None,
) -> None:
    """日本語 or 英語プロンプトのサマリブロックを出力する。"""
    lang_results = [r for r in results if r.lang == lang]
    if not lang_results:
        return

    print(f"{BOLD}{label} (n={len(lang_results)}):{RESET}")
    lite = _avg_reduction(results, lang, "default", "lite")
    std = _avg_reduction(results, lang, "default", "standard")
    ult = _avg_reduction(results, lang, "default", "ultra")

    if lite is not None:
        print(f"  default -> lite:     {CYAN}-{lite:.1f}%{RESET}")
    if std is not None:
        v = f"{CYAN}-{std:.1f}%{RESET}"
        if std_claim is not None:
            pw = _pass_warn(std, std_claim)
            print(f"  default -> standard: {v}  (claim: -{std_claim:.0f}%)  {pw}")
        else:
            print(f"  default -> standard: {v}")
    if ult is not None:
        v = f"{CYAN}-{ult:.1f}%{RESET}"
        if ult_claim is not None:
            pw = _pass_warn(ult, ult_claim)
            print(f"  default -> ultra:    {v}  (claim: -{ult_claim:.0f}%)  {pw}")
        else:
            print(f"  default -> ultra:    {v}")
    print()


def _fmt_arm(r: PromptResult, arm: str) -> str:
    """per-prompt テーブル用の 1 セル文字列を返す。"""
    if arm in r.errors:
        return f"{RED}{'ERR':>8}{RESET}"
    if arm not in r.arms:
        return f"{'N/A':>8}"
    ar = r.arms[arm]
    pct = (
        f"-{ar.reduction_pct:.0f}%"
        if ar.reduction_pct is not None
        else f"{format_tokens(ar.tokens):>5}"
    )
    return f"{pct:>8}"


def print_summary(results: list[PromptResult]) -> None:
    """サマリテーブルを stdout に出力する。

    主張マッピング:
      - 日本語 ultra = 80% (genshijin 原著値)
      - 英語 ultra  = 68% (caveman 原著の Full モード相当)
      - standard は原著に独立した主張値がないため claim なし (参考値のみ表示)
    """
    print(f"\n{BOLD}{'=' * 60}")
    print("  Brevity Benchmark Results")
    print(f"{'=' * 60}{RESET}\n")

    _print_lang_block(results, "ja", "Japanese prompts", ult_claim=80.0)
    _print_lang_block(results, "en", "English prompts", ult_claim=68.0)

    # ── JA vs EN 比較 ──
    ja_ult = _avg_reduction(results, "ja", "default", "ultra")
    en_ult = _avg_reduction(results, "en", "default", "ultra")
    if ja_ult is not None and en_ult is not None:
        diff = ja_ult - en_ult
        sign = "+" if diff >= 0 else ""
        pw = _pass_warn(diff, 12.0)
        ja_v = f"{CYAN}-{ja_ult:.1f}%{RESET}"
        en_v = f"{CYAN}-{en_ult:.1f}%{RESET}"
        print(f"{BOLD}Japanese vs English (ultra):{RESET}")
        print(
            f"  JA {ja_v} vs EN {en_v}  "
            f"=> JA {sign}{diff:.1f}pt more reduction  (claim: +12pt)  {pw}"
        )
        print()

    # ── プロンプト別詳細 ──
    print(f"{BOLD}Per-prompt detail:{RESET}")
    header = (
        f"  {'ID':<18} {'lang':<4}"
        f" {'default':>8} {'lite':>8} {'standard':>8} {'ultra':>8}"
    )
    print(header)
    print(f"  {'-' * (len(header) - 2)}")

    for r in results:
        default_str = (
            f"{format_tokens(r.arms['default'].tokens):>8}"
            if "default" in r.arms
            else f"{'N/A':>8}"
        )
        lite_s = _fmt_arm(r, "lite")
        std_s = _fmt_arm(r, "standard")
        ult_s = _fmt_arm(r, "ultra")
        print(f"  {r.prompt_id:<18} {r.lang:<4} {default_str} {lite_s} {std_s} {ult_s}")

    print()
    print(f"  {DIM}token count: tiktoken {ENCODING_NAME}{RESET}")
    claims = "caveman ~68% (en), genshijin ~80% (ja), JA+12pt vs EN"
    print(f"  {DIM}claims: {claims}{RESET}")
    print()


# ── CLI ──────────────────────────────────────────────────

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
    group.add_argument(
        "--prompt",
        metavar="TEXT",
        help="単一プロンプトをベンチマーク",
    )
    group.add_argument(
        "--file",
        metavar="JSONL",
        type=Path,
        help="複数プロンプトを JSONL ファイルから読み込み",
    )
    parser.add_argument(
        "--output",
        metavar="PATH",
        type=Path,
        default=None,
        help=_HELP_OUTPUT,
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
        "--verbose",
        action="store_true",
        help="stderr など追加情報を表示",
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
            if "id" not in entry:
                entry["id"] = f"prompt-{lineno}"
            if "lang" not in entry:
                entry["lang"] = "ja"
            prompts.append(entry)

    if not prompts:
        sys.exit(f"{RED}ERROR{RESET}: JSONL ファイルが空です: {path}")

    return prompts


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # プロンプトリスト決定
    if args.prompt:
        prompts = [{"id": args.id, "prompt": args.prompt, "lang": args.lang}]
    elif args.file:
        prompts = load_prompts_from_file(args.file)
    else:
        # デフォルトプロンプトセット
        prompts = DEFAULT_PROMPTS
        msg = "引数未指定のためデフォルトプロンプトセット (6件) を使用します。"
        print(f"{DIM}{msg}{RESET}")

    # ベンチマーク実行
    results = run_benchmark(prompts, args.output, verbose=args.verbose)

    # サマリ出力
    print_summary(results)


if __name__ == "__main__":
    main()
