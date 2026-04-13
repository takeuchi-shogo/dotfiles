"""brevity-benchmark のサマリ出力モジュール。"""

from __future__ import annotations

from typing import Optional

from _brevity_types import (
    BOLD,
    CYAN,
    DIM,
    ENCODING_NAME,
    GREEN,
    RESET,
    YELLOW,
    PromptResult,
)
from _brevity_runner import format_tokens


# ── 集計ヘルパー ─────────────────────────────────────────────


def _avg_reduction(
    results: list[PromptResult], lang: str, from_arm: str, to_arm: str
) -> Optional[float]:
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
    return sum(values) / len(values) if values else None


def _pass_warn(actual: float, claim: float, tolerance: float = 5.0) -> str:
    if actual >= claim - tolerance:
        return f"{GREEN}PASS{RESET}"
    return f"{YELLOW}WARN{RESET}"


# ── ブロック出力 ─────────────────────────────────────────────


def _print_lang_block(
    results: list[PromptResult],
    lang: str,
    label: str,
    ult_claim: Optional[float] = None,
) -> None:
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
        print(f"  default -> standard: {CYAN}-{std:.1f}%{RESET}")
    if ult is not None:
        v = f"{CYAN}-{ult:.1f}%{RESET}"
        if ult_claim is not None:
            pw = _pass_warn(ult, ult_claim)
            print(f"  default -> ultra:    {v}  (claim: -{ult_claim:.0f}%)  {pw}")
        else:
            print(f"  default -> ultra:    {v}")
    print()


def _fmt_arm(r: PromptResult, arm: str) -> str:
    from _brevity_types import RED  # noqa: PLC0415

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


# ── メイン出力 ───────────────────────────────────────────────


def _print_ja_en_comparison(results: list[PromptResult]) -> None:
    ja_ult = _avg_reduction(results, "ja", "default", "ultra")
    en_ult = _avg_reduction(results, "en", "default", "ultra")
    if ja_ult is None or en_ult is None:
        return

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


def _print_per_prompt_table(results: list[PromptResult]) -> None:
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
        print(
            f"  {r.prompt_id:<18} {r.lang:<4}"
            f" {default_str} {_fmt_arm(r, 'lite')}"
            f" {_fmt_arm(r, 'standard')} {_fmt_arm(r, 'ultra')}"
        )

    print()
    print(f"  {DIM}token count: tiktoken {ENCODING_NAME}{RESET}")
    print(
        f"  {DIM}claims: caveman ~68% (en), genshijin ~80% (ja), JA+12pt vs EN{RESET}"
    )
    print()


def print_summary(results: list[PromptResult]) -> None:
    """サマリテーブルを stdout に出力する。"""
    print(f"\n{BOLD}{'=' * 60}")
    print("  Brevity Benchmark Results")
    print(f"{'=' * 60}{RESET}\n")

    _print_lang_block(results, "ja", "Japanese prompts", ult_claim=80.0)
    _print_lang_block(results, "en", "English prompts", ult_claim=68.0)
    _print_ja_en_comparison(results)
    _print_per_prompt_table(results)
