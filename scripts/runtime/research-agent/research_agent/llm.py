"""ChatAnthropic ファクトリ。LLM プロバイダをここに隔離し、差し替え可能にする。"""

from langchain_anthropic import ChatAnthropic

from . import config


def make_llm() -> ChatAnthropic:
    """ChatAnthropic を生成。

    ANTHROPIC_API_KEY は環境変数から読まれる
    （CLI が起動時に local .env をロードする）。
    temperature は渡さない。Sonnet 5.5 は既定以外の sampling 値を 400 で拒否する。
    """
    return ChatAnthropic(
        model=config.MODEL,
        max_tokens=config.MAX_TOKENS,
    )
