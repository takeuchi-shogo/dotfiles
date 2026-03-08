"""AutoEvolve session event collector.

セッション中のイベントを一時ファイルに蓄積し、
セッション終了時に jsonl にフラッシュする共有モジュール。

Usage (from other hooks):
    from session_events import emit_event
    emit_event("error", {"message": "TypeError", "command": "npm test"})
"""
import json
import logging
import os
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path


def _get_data_dir() -> Path:
    """データディレクトリを遅延評価で返す。

    テスト時に AUTOEVOLVE_DATA_DIR を差し替えられるよう、
    呼び出しごとに環境変数を読む。
    """
    return Path(os.environ.get(
        "AUTOEVOLVE_DATA_DIR",
        os.path.join(os.environ.get("HOME", ""), ".claude", "agent-memory"),
    ))


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
    """セッション中のイベントを一時ファイルに追記する。"""
    logger = _setup_logger()
    try:
        path = _temp_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = {"timestamp": _now_iso(), "category": category, **data}
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        brief = str(data.get("message", data.get("rule", "")))[:80]
        logger.debug("emit: %s - %s", category, brief)
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
