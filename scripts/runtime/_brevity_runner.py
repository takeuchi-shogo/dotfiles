"""brevity-benchmark の実行系モジュール。

run_claude, benchmark_prompt, run_benchmark, save_raw_response を提供する。
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import tiktoken
except ImportError:
    sys.exit(
        "tiktoken required. Install with: pip install tiktoken\n"
        "  or: uv pip install tiktoken"
    )

from _brevity_types import (
    ARM_ORDER,
    ARM_SLEEP_SEC,
    BOLD,
    CLAUDE_BIN_DEFAULT,
    CYAN,
    DEFAULT_MODEL,
    DIM,
    ENCODING_NAME,
    GREEN,
    PROMPT_SLEEP_SEC,
    RED,
    RESET,
    SYSTEM_PROMPTS,
    TIMEOUT_SEC,
    YELLOW,
    ArmContext,
    ArmResult,
    PromptResult,
)

_claude_bin_cache: Optional[str] = None


# ── ヘルパー ─────────────────────────────────────────────────


def format_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def count_tokens(text: str) -> int:
    enc = tiktoken.get_encoding(ENCODING_NAME)
    return len(enc.encode(text))


def get_claude_bin() -> str:
    global _claude_bin_cache
    if _claude_bin_cache is not None:
        return _claude_bin_cache

    p = Path(CLAUDE_BIN_DEFAULT)
    if p.exists():
        _claude_bin_cache = str(p)
        return _claude_bin_cache

    which_result = subprocess.run(
        ["which", "claude"], capture_output=True, text=True, check=False
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
    patterns = [
        r"(token|session|auth|key|secret|api[-_]?key)\s*[:=]\s*\S+",
        r"Bearer\s+\S+",
    ]
    for pat in patterns:
        text = re.sub(pat, r"[REDACTED]", text, flags=re.IGNORECASE)
    return text


def save_raw_response(run_dir: Path, prompt_id: str, arm: str, text: str) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / f"{prompt_id}-{arm}.txt").write_text(text, encoding="utf-8")


# ── Claude 呼び出し ──────────────────────────────────────────


def run_claude(
    prompt: str,
    system_prompt: str,
    model: str = DEFAULT_MODEL,
    timeout: int = TIMEOUT_SEC,
) -> tuple[str, str]:
    """claude -p を実行し (stdout, stderr) を返す。"""
    cmd = [get_claude_bin(), "-p", "--dangerously-skip-permissions", "--model", model]
    if system_prompt:
        cmd += ["--append-system-prompt", system_prompt]
    cmd += ["--", prompt]

    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, check=False
    )
    if result.returncode != 0:
        err_msg = sanitize_stderr((result.stderr or "").strip())[:300]
        raise RuntimeError(f"claude CLI failed (exit {result.returncode}): {err_msg}")
    return result.stdout, result.stderr


# ── アーム計測 ───────────────────────────────────────────────


def _compute_reduction(tokens: int, default_tokens: Optional[int]) -> Optional[float]:
    if default_tokens and default_tokens > 0:
        return round((1 - tokens / default_tokens) * 100, 1)
    return None


def _print_arm_progress(
    arm: str, tokens: int, char_count: int, reduction_pct: Optional[float]
) -> None:
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


def _run_arm(ctx: ArmContext, arm: str, default_tokens: Optional[int]) -> Optional[int]:
    """1アームを実行し、更新された default_tokens を返す。"""
    sys_prompt = SYSTEM_PROMPTS[arm]
    print(f"  {CYAN}{arm:<10}{RESET}", end="", flush=True)

    try:
        stdout, stderr = run_claude(ctx.prompt_text, sys_prompt)
    except subprocess.TimeoutExpired:
        ctx.result.errors[arm] = f"timeout after {TIMEOUT_SEC}s"
        print(f" {RED}TIMEOUT{RESET}")
        time.sleep(ARM_SLEEP_SEC)
        return default_tokens
    except Exception as exc:  # noqa: BLE001
        ctx.result.errors[arm] = str(exc)
        print(f" {RED}ERROR{RESET}: {exc}")
        time.sleep(ARM_SLEEP_SEC)
        return default_tokens

    if not stdout.strip():
        msg = f"empty response (stderr: {stderr.strip()[:100]})"
        ctx.result.errors[arm] = msg
        print(f" {YELLOW}EMPTY{RESET}: {msg}")
        time.sleep(ARM_SLEEP_SEC)
        return default_tokens

    save_raw_response(ctx.run_dir, ctx.result.prompt_id, arm, stdout)
    tokens = count_tokens(stdout)
    char_count = len(stdout)

    if arm == "default":
        default_tokens = tokens
        reduction_pct = None
    else:
        reduction_pct = _compute_reduction(tokens, default_tokens)

    ctx.result.arms[arm] = ArmResult(
        tokens=tokens, char_count=char_count, reduction_pct=reduction_pct
    )
    _print_arm_progress(arm, tokens, char_count, reduction_pct)

    if ctx.verbose and stderr.strip():
        print(f"    {DIM}stderr: {stderr.strip()[:80]}{RESET}")

    if arm != ARM_ORDER[-1]:
        time.sleep(ARM_SLEEP_SEC)

    return default_tokens


def benchmark_prompt(entry: dict, run_dir: Path, verbose: bool = False) -> PromptResult:
    """単一プロンプトを 4 アームで計測する。"""
    prompt_id = entry.get("id", "prompt")
    prompt_text = entry["prompt"]
    lang = entry.get("lang", "ja")

    result = PromptResult(prompt_id=prompt_id, lang=lang, prompt_text=prompt_text)
    print(
        f"\n{BOLD}[{prompt_id}]{RESET} ({lang}) {DIM}{prompt_text[:60]}...{RESET}"
        if len(prompt_text) > 60
        else f"\n{BOLD}[{prompt_id}]{RESET} ({lang}) {DIM}{prompt_text}{RESET}"
    )

    ctx = ArmContext(
        prompt_text=prompt_text, run_dir=run_dir, verbose=verbose, result=result
    )
    default_tokens: Optional[int] = None
    for arm in ARM_ORDER:
        default_tokens = _run_arm(ctx, arm, default_tokens)

    return result


# ── ベンチマーク実行 ─────────────────────────────────────────


def _serialize_results(all_results: list[PromptResult]) -> list[dict]:
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
    return serializable


def run_benchmark(
    prompts: list[dict],
    output_path: Optional[Path],
    verbose: bool = False,
) -> list[PromptResult]:
    """全プロンプトのベンチマークを実行し結果を返す。"""
    get_claude_bin()

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

    if output_path is None:
        output_path = run_dir / "results.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(_serialize_results(all_results), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n{DIM}results saved: {output_path}{RESET}")

    return all_results
