"""パス・閾値・モデル等の定数。環境変数で上書き可能なものは os.environ 経由。"""

import os
from pathlib import Path

HOME = Path.home()

# データ（全て gitignore、~/.cache 配下 = tech-researcher 流儀）
CACHE_DIR = Path(
    os.environ.get("RESEARCH_AGENT_CACHE", HOME / ".cache" / "research-agent")
)
EXPERIENCE_DIR = (
    CACHE_DIR / "experience"
)  # memory-vec 新ソース research-experience の root
REPORTS_DIR = CACHE_DIR / "reports"
CHECKPOINT_DB = CACHE_DIR / "checkpoints.db"

# memory-vec 経験RAG 基盤
MEMORY_VEC_DIR = HOME / ".claude" / "skill-data" / "memory-vec"
MEMORY_VEC_QUERY = MEMORY_VEC_DIR / "query.ts"
MEMORY_VEC_REINDEX = MEMORY_VEC_DIR / "reindex.ts"
EXPERIENCE_SOURCE = "research-experience"

# LLM（ChatAnthropic。差し替えは llm.py で隔離）
MODEL = os.environ.get("RESEARCH_AGENT_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = 4096

# ループ / 品質ガード
MAX_ITERATIONS = 6  # 暴走ガード（§25 落とし穴②）
EXPERIENCE_SCORE_THRESHOLD = 0.7  # これ以上 & grounding pass で persist 候補
REFLECTION_WINDOW = 3  # episodic memory に保つ reflection 数
EXPERIENCE_TOPK = 3  # 起動時に注入する類似成功軌跡数

# arXiv（キー不要）と fetch の SSRF 強化。https 必須（平文 MITM で偽論文を注入されない）
ARXIV_API = "https://export.arxiv.org/api/query"
ALLOWED_FETCH_HOSTS = frozenset({"arxiv.org", "www.arxiv.org", "export.arxiv.org"})
FETCH_TIMEOUT = 15  # 接続/読み取り timeout（秒）
FETCH_MAX_BYTES = 2_000_000  # 読み取りサイズ上限
FETCH_ALLOWED_CONTENT_TYPES = (
    "text/html",
    "text/plain",
    "application/pdf",
    "application/xml",
)
