"""brevity-benchmark の定数・設定・データ構造。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── カラーコード ─────────────────────────────────────────────

RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

# ── 実行パラメータ ───────────────────────────────────────────

CLAUDE_BIN_DEFAULT = "/Users/takeuchishougo/.local/bin/claude"
ENCODING_NAME = "o200k_base"
ARM_SLEEP_SEC = 1.0
PROMPT_SLEEP_SEC = 2.0
TIMEOUT_SEC = 120
DEFAULT_MODEL = "sonnet"
MIN_CONTENT_RATIO = 0.05

# ── brevity システムメッセージ ───────────────────────────────

_BASE_BREVITY = (
    "Remove filler, hedging, and pleasantries from your response. "
    "No preamble, no recap, no trailing summary."
)
_JA_DROP_LIST = (
    "日本語フィラー（なるほど、確認しました、それでは、まず、えーと、まあ、"
    "ちなみに、一応、基本的に、そもそも、ちょっと）、"
    "クッション語（〜と思います、〜と思われます、〜かもしれません、もしかして、〜っぽい）、"
    "敬語装飾（〜です、〜ます、〜でございます、〜させていただきます）、"
    "結果要約（以上のように、つまり、要するに）も削除する。"
)
_JA_STRUCT_BREVITY = (
    "日本語応答では: 敬語を体言止めに変換し、文脈から自明な助詞を省略する。"
)

SYSTEM_PROMPTS: dict[str, str] = {
    "default": "",
    "lite": f"{_BASE_BREVITY} {_JA_DROP_LIST}",
    "standard": f"{_BASE_BREVITY} {_JA_DROP_LIST} {_JA_STRUCT_BREVITY}",
    "ultra": (
        f"{_BASE_BREVITY} {_JA_DROP_LIST} {_JA_STRUCT_BREVITY} "
        "箇条書き優先、接続詞削除、一文一事実。"
    ),
}

ARM_ORDER = ["default", "lite", "standard", "ultra"]

# ── デフォルトプロンプトセット ───────────────────────────────

DEFAULT_PROMPTS: list[dict] = [
    {"id": "ja-cors", "prompt": "CORS エラーの原因と対処を教えて", "lang": "ja"},
    {"id": "ja-loop", "prompt": "JavaScript のイベントループを説明して", "lang": "ja"},
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
    {"id": "en-loop", "prompt": "Explain the JavaScript event loop", "lang": "en"},
    {
        "id": "en-auth",
        "prompt": "Auth token validation has a bug. What are likely causes?",
        "lang": "en",
    },
]

# ── データ構造 ───────────────────────────────────────────────


@dataclass
class ArmResult:
    tokens: int
    char_count: int
    reduction_pct: Optional[float] = None


@dataclass
class PromptResult:
    prompt_id: str
    lang: str
    prompt_text: str
    arms: dict[str, ArmResult] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)


@dataclass
class ArmContext:
    """_run_arm に渡す実行コンテキスト。引数数を削減するための集約体。"""

    prompt_text: str
    run_dir: "Path"
    verbose: bool
    result: PromptResult
