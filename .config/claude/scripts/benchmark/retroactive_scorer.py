#!/usr/bin/env python3
"""Retroactive scoring bootstrap — batch-score past skill executions.

新スキル導入時や改善開始時に、過去の実行記録からベースラインスコアを算出し
skill-executions.jsonl に追記する。

Usage:
    python retroactive_scorer.py --skill improve        # 特定スキル
    python retroactive_scorer.py --all                   # 全スキル
    python retroactive_scorer.py --skill improve --dry-run  # プレビュー
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from storage import get_data_dir, read_jsonl  # noqa: E402


def load_scoring_config() -> dict:
    """scoring-config.json を読み込む。"""
    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "references"
        / "scoring-config.json"
    )
    if not config_path.exists():
        # fallback: symlink 先
        config_path = Path.home() / ".claude" / "references" / "scoring-config.json"
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        return json.load(f)


def classify_signal(score: float, config: dict) -> str:
    """スコアを信号分類する。"""
    thresholds = config.get("outputSignal", {}).get("thresholds", {})
    if score >= thresholds.get("highSignal", 8):
        return "HIGH_SIGNAL"
    if score >= thresholds.get("contextual", 5):
        return "CONTEXTUAL"
    if score >= thresholds.get("watchlist", 3):
        return "WATCHLIST"
    return "NOISE"


def load_usage_data(data_dir: Path, skill_filter: str | None) -> list[dict]:
    """skill-executions.jsonl から未スコアリングの実行記録を取得。"""
    exec_file = data_dir / "learnings" / "skill-executions.jsonl"
    if not exec_file.exists():
        return []
    entries = [e for e in read_jsonl(exec_file) if e.get("scored_by") != "retroactive"]
    if skill_filter:
        entries = [
            e
            for e in entries
            if e.get("skill") == skill_filter or e.get("skill_name") == skill_filter
        ]
    return entries


def load_existing_scores(data_dir: Path) -> set[str]:
    """既にスコアリング済みのエントリのキーを取得。"""
    exec_file = data_dir / "learnings" / "skill-executions.jsonl"
    if not exec_file.exists():
        return set()
    existing = set()
    for entry in read_jsonl(exec_file):
        key = f"{entry.get('skill')}:{entry.get('timestamp', '')}"
        existing.add(key)
    return existing


def load_session_context(data_dir: Path, timestamp: str) -> dict:
    """セッションメトリクスから該当時刻近辺のコンテキストを取得。"""
    metrics_file = data_dir / "metrics" / "session-metrics.jsonl"
    if not metrics_file.exists():
        return {}
    for entry in read_jsonl(metrics_file):
        session_ts = entry.get("timestamp", "")
        if session_ts[:10] == timestamp[:10]:  # 同日のセッション
            return entry
    return {}


def compute_retroactive_score(usage: dict, session: dict) -> tuple[float, str]:
    """ルールベースの初期スコアを算出。

    Returns:
        (score, reason) — score は 1-10 スケール
    """
    score = 5.0  # ベースライン
    reasons = []

    # セッションにエラーがあれば減点
    error_count = session.get("errors_count", 0)
    if error_count == 0:
        score += 1.5
        reasons.append("エラーなし")
    elif error_count <= 2:
        score += 0.5
        reasons.append(f"軽微なエラー({error_count}件)")
    else:
        score -= 1.0
        reasons.append(f"エラー多発({error_count}件)")

    # セッション完了度 (outcome: "clean_success" / "recovery" / "failure")
    outcome = session.get("outcome", "")
    if outcome == "clean_success":
        score += 1.0
        reasons.append("セッション正常完了")
    elif outcome == "recovery":
        score += 0.5
        reasons.append("エラーから回復")

    # 後続修正の有無（同日に correction があれば減点）
    corrections = session.get("corrections", 0)
    if corrections > 0:
        score -= corrections * 0.5
        reasons.append(f"修正{corrections}回")

    # クランプ
    score = max(1.0, min(10.0, score))
    reason = "; ".join(reasons) if reasons else "ベースラインスコア"

    return round(score, 1), reason


def main():
    parser = argparse.ArgumentParser(description="Retroactive scoring bootstrap")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--skill", type=str, help="対象スキル名")
    group.add_argument("--all", action="store_true", help="全スキル")
    parser.add_argument("--dry-run", action="store_true", help="実際には書き込まない")
    args = parser.parse_args()

    data_dir = get_data_dir()
    config = load_scoring_config()
    existing_keys = load_existing_scores(data_dir)

    skill_filter = args.skill if not args.all else None
    usage_entries = load_usage_data(data_dir, skill_filter)

    if not usage_entries:
        print("対象スキルの実行記録が見つかりません。", file=sys.stderr)
        sys.exit(0)

    # スキルごとにグルーピング
    by_skill: dict[str, list[dict]] = {}
    for entry in usage_entries:
        skill = entry.get("skill", "unknown")
        by_skill.setdefault(skill, []).append(entry)

    new_entries: list[dict] = []

    for skill_name, entries in sorted(by_skill.items()):
        for usage in entries:
            ts = usage.get("timestamp", "")
            key = f"{skill_name}:{ts}"
            if key in existing_keys:
                continue  # 既にスコアリング済み

            session = load_session_context(data_dir, ts)
            score, reason = compute_retroactive_score(usage, session)
            signal = classify_signal(score, config)

            entry = {
                "timestamp": ts,
                "skill": skill_name,
                "score": score,
                "signal": signal,
                "reason": reason,
                "scored_by": "retroactive",
                "scored_at": datetime.now(timezone.utc).isoformat(),
            }
            new_entries.append(entry)

    if not new_entries:
        print("新規スコアリング対象なし。")
        return

    # 結果の表示
    print(f"\n{'Skill':<25} {'Score':>5} {'Signal':<14} Reason")
    print("-" * 80)
    for e in new_entries:
        print(f"{e['skill']:<25} {e['score']:>5} {e['signal']:<14} {e['reason']}")

    print(f"\n合計: {len(new_entries)} 件")

    if args.dry_run:
        print("\n(--dry-run: 書き込みをスキップ)")
        return

    # skill-executions.jsonl に追記
    exec_file = data_dir / "learnings" / "skill-executions.jsonl"
    exec_file.parent.mkdir(parents=True, exist_ok=True)
    with open(exec_file, "a") as f:
        for entry in new_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"\n{exec_file} に {len(new_entries)} 件追記しました。")


if __name__ == "__main__":
    main()
