"""経験RAG（§12.3-C）: 成功軌跡を memory-vec で意味検索 / 成功軌跡を persist。

memory-vec（sqlite-vec + MiniLM）の query.ts / reindex.ts を subprocess で呼ぶ。
失敗時は空で degrade（コールドスタート・reindex 失敗でも本流を止めない）が、
degrade は stderr にログして observable にする（silent failure を作らない）。
"""

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from . import config

_NODE = ["node", "--experimental-strip-types", "--no-warnings"]


@dataclass
class SuccessTrajectory:
    """persist 対象の成功軌跡（引数集約 = GP-007）。"""

    question: str
    approach: str
    score: float
    model: str
    reflections: list[str] = field(default_factory=list)
    sources: list[dict] = field(default_factory=list)


def _log(msg: str) -> None:
    print(f"[research-agent] {msg}", file=sys.stderr)


def retrieve(question: str, k: int | None = None) -> list[str]:
    """research-experience ソースから類似成功軌跡 top-k の本文（先頭部）を返す。"""
    k = k or config.EXPERIENCE_TOPK
    if not config.MEMORY_VEC_QUERY.exists():
        return []
    try:
        proc = subprocess.run(
            [
                *_NODE,
                str(config.MEMORY_VEC_QUERY),
                question,
                "--source",
                config.EXPERIENCE_SOURCE,
            ],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        _log(f"experience retrieve degraded (query failed): {e}")
        return []
    if proc.returncode != 0:
        _log(f"experience retrieve degraded (query rc={proc.returncode})")
        return []
    try:
        hits = json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError) as e:
        _log(f"experience retrieve degraded (bad JSON): {e}")
        return []
    out: list[str] = []
    for hit in hits[:k]:
        p = hit.get("path") if isinstance(hit, dict) else None
        if p and Path(p).exists():
            out.append(Path(p).read_text(encoding="utf-8")[:2000])
    return out


def format_for_prompt(experiences: list[str]) -> str:
    """retrieve した経験を system prompt 注入用の few-shot 文字列に整形する。"""
    if not experiences:
        return ""
    joined = "\n\n---\n\n".join(experiences)
    return "過去の類似調査で有効だったアプローチ（参考）:\n\n" + joined


def persist(traj: SuccessTrajectory) -> Path:
    """成功軌跡を experience .md に書き出し reindex を起動する（Tier 3 = --save 時）。

    先頭2000字が embed されるため要約（Approach）を前出し。frontmatter に汚染追跡
    フィールド（model/score/created_at/sources）を持つ（codex #4）。
    """
    config.EXPERIENCE_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    slug = re.sub(r"[^a-z0-9]+", "-", traj.question.lower()).strip("-")[:40] or "exp"
    stamp = now.strftime("%Y%m%d%H%M%S")
    src_block = "\n".join(
        f"  - url: {s.get('url', '')}\n    grounding: {s.get('grounding', '')}"
        for s in traj.sources
    )
    refl_block = "\n".join("- " + r for r in traj.reflections) or "- (なし)"
    body = (
        f"---\nquestion: {traj.question}\noutcome: success\nscore: {traj.score}\n"
        f"model: {traj.model}\ncreated_at: {now.isoformat()}\nsources:\n{src_block}\n"
        f"---\n## Approach (what worked)\n{traj.approach}\n\n"
        f"## Reflections / pitfalls avoided\n{refl_block}\n"
    )
    path = config.EXPERIENCE_DIR / f"{stamp}-{slug}.md"
    path.write_text(body, encoding="utf-8")
    _reindex()
    return path


def _reindex() -> None:
    """memory-vec を fire-and-forget で再索引（完了を待たない）。

    full rebuild は本番全 source で ~86s かかるため同期待ちしない。新 experience は
    次回 reindex 完了後（次セッションの Stop hook 等）に検索へ反映される。
    """
    if not config.MEMORY_VEC_REINDEX.exists():
        _log("reindex skipped (reindex.ts not found)")
        return
    try:
        subprocess.Popen(
            [*_NODE, str(config.MEMORY_VEC_REINDEX)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError as e:
        _log(f"reindex spawn degraded: {e}")
