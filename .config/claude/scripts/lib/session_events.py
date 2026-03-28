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
import sys
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
    except Exception as exc:
        # ロガーセットアップ自体が失敗しても hook をクラッシュさせない
        print(f"[session-events] logger setup failed: {exc}", file=sys.stderr)

    return logger


def _temp_path() -> Path:
    return _get_data_dir() / "current-session.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


_CONFIG_VERSION_CACHE: str | None = None


def compute_config_version() -> str:
    """設定ファイル群の SHA-256 先頭12文字を返す。

    対象: ~/.claude/{CLAUDE.md, settings.json, references/improve-policy.md}
    ファイルが存在しない場合はスキップする。全ファイル不在時は空文字。
    """
    import hashlib

    global _CONFIG_VERSION_CACHE  # noqa: PLW0603
    if _CONFIG_VERSION_CACHE is not None:
        return _CONFIG_VERSION_CACHE

    claude_dir = Path.home() / ".claude"
    targets = [
        claude_dir / "CLAUDE.md",
        claude_dir / "settings.json",
        claude_dir / "references" / "improve-policy.md",
    ]
    h = hashlib.sha256()
    found = False
    for target in targets:
        try:
            content = target.read_bytes()
            h.update(content)
            found = True
        except OSError:
            continue
    _CONFIG_VERSION_CACHE = h.hexdigest()[:12] if found else ""
    return _CONFIG_VERSION_CACHE


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
            "config_version": compute_config_version(),
        }
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        brief = str(data.get("message", data.get("rule", "")))[:80]
        logger.debug("emit: %s [i=%.1f] - %s", category, importance, brief)
    except Exception as exc:
        try:
            logger.error("emit failed: %s", exc)
        except Exception as log_exc:
            print(
                f"[session-events] emit failed: {exc} (log also failed: {log_exc})",
                file=sys.stderr,
            )


def read_session_events() -> list[dict]:
    """current-session.jsonl を非破壊で読み取る。

    flush_session() と異なりファイルを削除しない。
    セッション途中のフック (stagnation-detector 等) が参照する。
    """
    logger = _setup_logger()
    path = _temp_path()
    if not path.exists():
        return []
    events = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        logger.debug(
                            "read_session: skipped corrupt line: %s", line[:80]
                        )
                        continue
    except OSError as exc:
        logger.warning("read_session: failed to read %s: %s", path, exc)
        return []
    return [_normalize_event(e) for e in events]


def build_state_descriptor() -> dict:
    """EvoX の φ(D) に相当する統合状態要約。

    current-session.jsonl を非破壊で読み、スコア統計・進捗・多様性を計算する。
    stagnation-detector と session-learner が使用。
    """
    events = read_session_events()
    if not events:
        return {
            "score_stats": {
                "total_events": 0,
                "error_count": 0,
                "avg_importance": 0.0,
                "high_importance_count": 0,
            },
            "progress": {"steps_since_last_error": 0, "error_rate": 0.0},
            "diversity": {"unique_command_types": 0, "total_commands": 0},
        }

    importances = [e.get("importance", 0.5) for e in events]
    error_events = [e for e in events if e.get("category") == "error"]

    error_indices = [i for i, e in enumerate(events) if e.get("category") == "error"]
    steps_since_last_error = (
        (len(events) - 1 - error_indices[-1]) if error_indices else len(events)
    )

    commands = [e.get("command", "") for e in events if e.get("command")]
    unique_commands = len({parts[0] for cmd in commands if (parts := cmd.split())})

    return {
        "score_stats": {
            "total_events": len(events),
            "error_count": len(error_events),
            "avg_importance": round(sum(importances) / len(importances), 2),
            "high_importance_count": sum(1 for i in importances if i >= 0.8),
        },
        "progress": {
            "steps_since_last_error": steps_since_last_error,
            "error_rate": round(len(error_events) / len(events), 2),
        },
        "diversity": {
            "unique_command_types": unique_commands,
            "total_commands": len(commands),
        },
    }


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
                    except Exception as log_exc:
                        print(
                            f"[session-events] flush log failed: {log_exc}",
                            file=sys.stderr,
                        )
                    continue
    path.unlink(missing_ok=True)
    # Normalize Rust hook nested format to flat format for all downstream consumers
    events = [_normalize_event(e) for e in events]
    try:
        logger.info("flush: %d events collected", len(events))
    except Exception as exc:
        print(f"[session-events] flush info log failed: {exc}", file=sys.stderr)
    return events


def append_to_learnings(filename: str, data: dict) -> None:
    """learnings/ ディレクトリに jsonl エントリを追記する。"""
    logger = _setup_logger()
    try:
        path = _get_data_dir() / "learnings" / f"{filename}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = {"timestamp": _now_iso(), **data}
        entry.setdefault("tier", "raw")
        entry.setdefault("score", 0.0)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        brief = str(data.get("message", data.get("rule", "")))[:80]
        logger.debug("append learnings/%s: %s", filename, brief)
    except Exception as exc:
        try:
            logger.error("append_to_learnings failed: %s", exc)
        except Exception as log_exc:
            print(
                "[session-events] append_to_learnings failed:"
                f" {exc} (log also failed: {log_exc})",
                file=sys.stderr,
            )


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
        except Exception as log_exc:
            print(
                f"[session-events] append_to_metrics failed: {exc} (log: {log_exc})",
                file=sys.stderr,
            )


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
        except Exception as log_exc:
            print(
                f"[session-events] emit_skill_event failed: {exc} (log: {log_exc})",
                file=sys.stderr,
            )


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
    """セッション中のイベントからスキルの複合スコアを計算する (1-10 スケール)。

    Rust hook (events.rs) と Python hook (session_events.py) の
    両方のイベント形式に対応する（_normalize_event で統一）。

    retroactive_scorer.py と同じ 1-10 スケールで統一。
    スコア計算:
      base = 5.0
      + 1.5 (エラーなし)
      + 1.0 (テスト全パス)
      + 0.5 (GP違反なし)
      + 0.5 (レビュー Critical/Important なし)
      - 1.5/件 (エラー発生, 最大 -4.5)
      - 2.5 (テスト失敗)
      - 0.5/件 (GP違反, 最大 -2.0)
      - 1.0/件 (レビュー Critical/Important, 最大 -3.0)
    → clamp(1.0, 10.0)
    """
    normalized = [_normalize_event(e) for e in session_events]
    score = 5.0  # ベースライン (retroactive_scorer と同一)

    errors = [e for e in normalized if e.get("category") == "error"]
    if not errors:
        score += 1.5
    else:
        score -= min(1.5 * len(errors), 4.5)

    test_failures = [e for e in normalized if e.get("test_passed") is False]
    if not test_failures:
        score += 1.0
    else:
        score -= 2.5

    gp_violations = [
        e
        for e in normalized
        if e.get("category") == "quality" and e.get("rule", "").startswith("GP-")
    ]
    if not gp_violations:
        score += 0.5
    else:
        score -= min(0.5 * len(gp_violations), 2.0)

    review_criticals = [
        e
        for e in normalized
        if e.get("category") == "quality"
        and e.get("review_severity") in ("critical", "important")
    ]
    if not review_criticals:
        score += 0.5
    else:
        score -= min(1.0 * len(review_criticals), 3.0)

    return max(1.0, min(10.0, round(score, 1)))


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


def emit_review_scores(
    reviewer: str,
    scores: dict[str, str],
    metadata: dict | None = None,
) -> None:
    """次元別レビュースコアを review-scores.jsonl に記録する。

    Args:
        reviewer: レビューアー名 (e.g. "code-reviewer")
        scores: 次元→スコア (e.g. {"correctness": "4/5", ...})
        metadata: 追加情報 (e.g. {"weakest": "maintainability"})
    """
    append_to_learnings(
        "review-scores",
        {
            "reviewer": reviewer,
            "scores": scores,
            **(metadata or {}),
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
