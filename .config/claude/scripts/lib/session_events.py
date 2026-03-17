"""AutoEvolve session event collector.

セッション中のイベントを一時ファイルに蓄積し、
セッション終了時に jsonl にフラッシュする共有モジュール。

Usage (from other hooks):
    from session_events import emit_event
    emit_event("error", {"message": "TypeError", "command": "npm test"})
"""

import json
import logging
import re
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

from storage import get_data_dir as _storage_get_data_dir


IMPORTANCE_RULES: list[tuple[str, re.Pattern, float, str]] = [
    # --- Code quality failures (FM-001~010) ---
    ("high", re.compile(r"EACCES|Permission denied", re.I), 0.9, "FM-006"),
    ("high", re.compile(r"segfault|SIGSEGV|OOM|out of memory", re.I), 1.0, "FM-009"),
    ("high", re.compile(r"GP-002"), 0.8, "FM-005"),
    ("high", re.compile(r"GP-003"), 0.8, "FM-003"),
    ("high", re.compile(r"GP-004"), 0.8, "FM-002"),
    ("high", re.compile(r"GP-005"), 0.8, "FM-004"),
    ("high", re.compile(r"GP-001"), 0.8, "FM-003"),
    ("high", re.compile(r"security|vulnerability|injection", re.I), 0.9, "FM-010"),
    (
        "medium",
        re.compile(r"Cannot find module|ModuleNotFoundError", re.I),
        0.5,
        "FM-007",
    ),
    ("medium", re.compile(r"TypeError.*(?:undefined|null|nil)", re.I), 0.5, "FM-001"),
    ("medium", re.compile(r"TypeError|ReferenceError", re.I), 0.5, "FM-008"),
    ("medium", re.compile(r"timeout|ETIMEDOUT", re.I), 0.6, "FM-009"),
    ("low", re.compile(r"(?<!\w)warning(?:s)?(?:\s*:|\s)", re.I), 0.2, ""),
    ("low", re.compile(r"deprecated", re.I), 0.3, ""),
    # --- Agent behavior failures (FM-011~015, AgentRx-inspired) ---
    (
        "high",
        re.compile(r"incomplete.+plan|uncompleted.+step|plan.+adherence", re.I),
        0.8,
        "FM-011",
    ),
    (
        "medium",
        re.compile(
            r"No such file or directory|ENOENT|404 Not Found|does not exist", re.I
        ),
        0.6,
        "FM-012",
    ),
    (
        "medium",
        re.compile(r"tool.+misinterpret|output.+misread|re-?running same", re.I),
        0.6,
        "FM-013",
    ),
    (
        "high",
        re.compile(r"intent.+misalign|違う|そうじゃな|ではなく|not what I asked", re.I),
        0.8,
        "FM-014",
    ),
    (
        "high",
        re.compile(
            r"premature.+action|without.+confirm|確認なし.+実行|dangerous.+without",
            re.I,
        ),
        0.9,
        "FM-015",
    ),
]

BASE_IMPORTANCE: dict[str, float] = {
    "error": 0.5,
    "quality": 0.6,
    "pattern": 0.4,
    "correction": 0.7,
}

RULE_CONFIDENCE = 0.8
BASE_CONFIDENCE = 0.5


def compute_importance(category: str, data: dict) -> tuple[float, float, str]:
    """ルールベースで importance, confidence, failure_mode を計算する。"""
    searchable = " ".join(str(v) for v in data.values())
    for _level, pattern, score, fm in IMPORTANCE_RULES:
        if pattern.search(searchable):
            return score, RULE_CONFIDENCE, fm
    base = BASE_IMPORTANCE.get(category, 0.5)
    return base, BASE_CONFIDENCE, ""


def _get_data_dir() -> Path:
    """データディレクトリを遅延評価で返す。

    テスト時に AUTOEVOLVE_DATA_DIR を差し替えられるよう、
    呼び出しごとに環境変数を読む。
    """
    return _storage_get_data_dir()


def _setup_logger() -> logging.Logger:
    """AutoEvolve用ロガーを初期化する。

    ログ先: {data_dir}/logs/autoevolve.log
    ローテーション: 1MB x 3世代
    """
    logger = logging.getLogger("autoevolve")
    if logger.handlers:  # 既に設定済みなら再設定しない
        return logger

    logger.setLevel(logging.DEBUG)

    try:
        log_dir = _get_data_dir() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        handler = RotatingFileHandler(
            log_dir / "autoevolve.log",
            maxBytes=1_000_000,  # 1MB
            backupCount=3,
            encoding="utf-8",
        )
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    except Exception:
        # ロガーセットアップ自体が失敗しても hook をクラッシュさせない
        pass

    return logger


def _temp_path() -> Path:
    return _get_data_dir() / "current-session.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def emit_event(category: str, data: dict) -> None:
    """セッション中のイベントを一時ファイルに追記する（スコア付き）。

    data に failure_mode / failure_type を含めると優先される。
    含めない場合は IMPORTANCE_RULES から自動判定する。
    """
    logger = _setup_logger()
    try:
        importance, confidence, auto_fm = compute_importance(category, data)
        failure_mode = data.pop("failure_mode", None) or auto_fm
        failure_type = data.pop("failure_type", "generalization")
        path = _temp_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": _now_iso(),
            "category": category,
            **data,
            "importance": round(importance, 2),
            "confidence": round(confidence, 2),
            "failure_mode": failure_mode,
            "failure_type": failure_type,
            "scored_by": "rule",
            "promotion_status": "pending",
        }
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        brief = str(data.get("message", data.get("rule", "")))[:80]
        logger.debug("emit: %s [i=%.1f] - %s", category, importance, brief)
    except Exception as exc:
        try:
            logger.error("emit failed: %s", exc)
        except Exception:
            pass


def flush_session() -> list[dict]:
    """一時ファイルのイベントを全て読み出し、ファイルを削除する。"""
    logger = _setup_logger()
    path = _temp_path()
    if not path.exists():
        return []
    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    try:
                        logger.warning("flush: skipped corrupt line: %s", line[:120])
                    except Exception:
                        pass
                    continue
    path.unlink(missing_ok=True)
    # Normalize Rust hook nested format to flat format for all downstream consumers
    events = [_normalize_event(e) for e in events]
    try:
        logger.info("flush: %d events collected", len(events))
    except Exception:
        pass
    return events


def append_to_learnings(filename: str, data: dict) -> None:
    """learnings/ ディレクトリに jsonl エントリを追記する。"""
    logger = _setup_logger()
    try:
        path = _get_data_dir() / "learnings" / f"{filename}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = {"timestamp": _now_iso(), **data}
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        brief = str(data.get("message", data.get("rule", "")))[:80]
        logger.debug("append learnings/%s: %s", filename, brief)
    except Exception as exc:
        try:
            logger.error("append_to_learnings failed: %s", exc)
        except Exception:
            pass


def emit_review_finding(finding: dict) -> None:
    """レビュー指摘を review-findings.jsonl に保存する。

    finding には以下を含む:
      id, reviewer, file, line, confidence, failure_mode, finding, failure_type
    """
    append_to_learnings("review-findings", finding)


def emit_review_feedback(finding_id: str, outcome: str, reason: str = "") -> None:
    """レビュー指摘に対するフィードバック（accepted/ignored）を記録する。

    outcome: "accepted" | "ignored" | "manual_rejected"
    """
    append_to_learnings(
        "review-feedback",
        {
            "finding_id": finding_id,
            "outcome": outcome,
            "reason": reason,
        },
    )


def read_pending_findings() -> list[dict]:
    """未処理のレビュー指摘を読み込む。"""
    findings_path = _get_data_dir() / "learnings" / "review-findings.jsonl"
    feedback_path = _get_data_dir() / "learnings" / "review-feedback.jsonl"
    if not findings_path.exists():
        return []
    resolved_ids: set[str] = set()
    if feedback_path.exists():
        with open(feedback_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        resolved_ids.add(entry.get("finding_id", ""))
                    except json.JSONDecodeError:
                        continue
    pending = []
    with open(findings_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    if entry.get("id", "") not in resolved_ids:
                        pending.append(entry)
                except json.JSONDecodeError:
                    continue
    return pending


def append_to_metrics(data: dict) -> None:
    """metrics/ ディレクトリにセッションメトリクスを追記する。"""
    logger = _setup_logger()
    try:
        path = _get_data_dir() / "metrics" / "session-metrics.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = {"timestamp": _now_iso(), **data}
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        project = data.get("project", "unknown")
        total = data.get("total_events", 0)
        logger.info("metrics: %s - %d events", project, total)
    except Exception as exc:
        try:
            logger.error("append_to_metrics failed: %s", exc)
        except Exception:
            pass


def emit_skill_event(event_type: str, data: dict) -> None:
    """スキルライフサイクルイベントを記録する。

    event_type: "invocation" | "outcome"
    data には skill_name を必須で含む。
    """
    if "skill_name" not in data:
        raise ValueError("skill_name is required in data")
    logger = _setup_logger()
    try:
        path = _temp_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": _now_iso(),
            "category": "skill",
            "type": event_type,
            **data,
        }
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        logger.debug("skill_event: %s %s", event_type, data.get("skill_name"))
    except Exception as exc:
        try:
            logger.error("emit_skill_event failed: %s", exc)
        except Exception:
            pass


def _normalize_event(event: dict) -> dict:
    """Rust hook のネスト形式（data キー）をフラット化する。

    Rust events.rs: {"category": "error", "data": {"message": ..., "command": ...}}
    Python session_events.py: {"category": "error", "message": ..., "command": ...}
    両形式を統一して扱えるようにする（CRIT-001 修正）。

    トップレベルキー（category, importance 等）は data 内の同名キーで
    上書きされない（トップレベル優先）。
    """
    if "data" in event and isinstance(event["data"], dict):
        normalized = dict(event["data"])
        normalized.update({k: v for k, v in event.items() if k != "data"})
        return normalized
    return event


def compute_skill_score(session_events: list[dict], skill_name: str) -> float:
    """セッション中のイベントからスキルの複合スコアを計算する。

    Rust hook (events.rs) と Python hook (session_events.py) の
    両方のイベント形式に対応する（_normalize_event で統一）。

    スコア計算:
      base = 0.5
      + 0.5 (タスク正常完了 = デフォルト想定)
      - 0.3/件 (エラー発生)
      - 0.5 (テスト失敗)
      - 0.2/件 (レビュー Critical/Important)
      - 0.1/件 (GP違反)
    → clamp(0.0, 1.0)
    """
    normalized = [_normalize_event(e) for e in session_events]
    score = 1.0  # base(0.5) + completion(0.5)

    errors = [e for e in normalized if e.get("category") == "error"]
    score -= 0.3 * len(errors)

    test_failures = [e for e in normalized if e.get("test_passed") is False]
    if test_failures:
        score -= 0.5

    gp_violations = [
        e
        for e in normalized
        if e.get("category") == "quality" and e.get("rule", "").startswith("GP-")
    ]
    score -= 0.1 * len(gp_violations)

    review_criticals = [
        e
        for e in normalized
        if e.get("category") == "quality"
        and e.get("review_severity") in ("critical", "important")
    ]
    score -= 0.2 * len(review_criticals)

    return max(0.0, min(1.0, round(score, 2)))


def emit_repeated_topic(
    topic: str, file_patterns: list[str], session_count: int
) -> None:
    """Emit a repeated_topic event when the same domain knowledge appears 3+ times.

    Based on Codified Context paper G4: "If you explained it twice, write it down."
    """
    emit_event(
        "pattern",
        {
            "type": "repeated_topic",
            "topic": topic,
            "file_patterns": file_patterns,
            "session_count": session_count,
            "suggestion": "codify as reference or agent specification",
        },
    )


def emit_proposal_verdict(
    skill_name: str,
    hypothesis: str,
    verdict: str,  # "keep" | "revert"
    metric_before: float,
    metric_after: float,
    iteration: int,
    extra: dict | None = None,
) -> None:
    """AutoEvolve --evolve ループの提案判定結果を記録する。

    autoresearch パターン: 各イテレーションの keep/revert を追跡し、
    accept rate でエージェントの提案品質を定量化する。
    """
    delta = round(metric_after - metric_before, 4)
    emit_event(
        "proposal",
        {
            "type": "verdict",
            "skill_name": skill_name,
            "hypothesis": hypothesis,
            "verdict": verdict,
            "metric_before": metric_before,
            "metric_after": metric_after,
            "delta": delta,
            "iteration": iteration,
            **(extra or {}),
        },
    )


def emit_skill_step(
    skill_name: str,
    step: int,
    outcome: str,
    data: dict | None = None,
) -> None:
    """スキル内の個別ステップの成否を記録する。

    Args:
        skill_name: スキル名
        step: ステップ番号 (1-indexed)
        outcome: "success" | "failed" | "skipped"
        data: 追加情報 (error_ref, tool_name 等)
    """
    emit_skill_event(
        "step_outcome",
        {
            "skill_name": skill_name,
            "step": step,
            "outcome": outcome,
            **(data or {}),
        },
    )
