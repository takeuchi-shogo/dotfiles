"""ChatAnthropic ファクトリ。LLM プロバイダをここに隔離し、差し替え可能にする。"""

from langchain_anthropic import ChatAnthropic

from . import config


def make_llm(temperature: float = 0.0) -> ChatAnthropic:
    """ChatAnthropic を生成。

    ANTHROPIC_API_KEY は環境変数から読まれる
    （CLI が起動時に local .env をロードする）。
    """
    return ChatAnthropic(
        model=config.MODEL,
        temperature=temperature,
        max_tokens=config.MAX_TOKENS,
    )
