"""AutoEvolve experiment tracker.

実験の記録、ステータス管理、効果測定を行う。
改善サイクルで作成された変更（ブランチ）を追跡し、
マージ後の効果を learnings データから測定する。

Usage:
    python experiment_tracker.py record --category errors --hypothesis "..." --branch autoevolve/errors-2026-03-10 --files f1.md f2.md
    python experiment_tracker.py list [--status pending_review]
    python experiment_tracker.py measure <exp-id>
"""

import argparse
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path


def _get_data_dir() -> Path:
    """データディレクトリを遅延評価で返す。

    テスト時に AUTOEVOLVE_DATA_DIR を差し替えられるよう、
    呼び出しごとに環境変数を読む。
    """
    return Path(
        os.environ.get(
            "AUTOEVOLVE_DATA_DIR",
            os.path.join(os.environ.get("HOME", ""), ".claude", "agent-memory"),
        )
    )


def _registry_path() -> Path:
    """実験レジストリファイルのパスを返す。"""
    return _get_data_dir() / "experiments" / "experiment-registry.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_registry() -> list[dict]:
    """レジストリから全実験を読み込む。"""
    path = _registry_path()
    if not path.exists():
        return []
    experiments = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    experiments.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return experiments


def _save_registry(experiments: list[dict]) -> None:
    """レジストリに全実験を書き戻す。"""
    path = _registry_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for exp in experiments:
            f.write(json.dumps(exp, ensure_ascii=False) + "\n")


def _generate_id(category: str) -> str:
    """実験IDを生成する。形式: exp-YYYY-MM-DD-{category}-{seq:03d}"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prefix = f"exp-{today}-{category}"

    # 既存実験から同日・同カテゴリの最大連番を取得
    experiments = _load_registry()
    seq = 0
    for exp in experiments:
        eid = exp.get("id", "")
        if eid.startswith(prefix):
            try:
                s = int(eid.rsplit("-", 1)[-1])
                seq = max(seq, s)
            except (ValueError, IndexError):
                pass
    seq += 1
    return f"{prefix}-{seq:03d}"


def record_experiment(
    category: str,
    hypothesis: str,
    branch: str,
    files_changed: list[str],
    proposal_type: str | None = None,
    target_skill: str | None = None,
    failure_evidence: dict | None = None,
    validation_result: dict | None = None,
    outcome_reason: str | None = None,
    related_proposals: list[str] | None = None,
) -> dict:
    """新しい実験を記録する。

    Args:
        category: 実験カテゴリ (errors, quality, workflow, architecture)
        hypothesis: 仮説の説明
        branch: 実験ブランチ名
        files_changed: 変更されたファイルのリスト
        proposal_type: EvoSkill 提案種別 ("create" | "edit" | "deprecate")
        target_skill: EvoSkill 対象スキル名
        failure_evidence: EvoSkill 失敗エビデンス
        validation_result: EvoSkill バリデーション結果
        outcome_reason: EvoSkill 結果理由
        related_proposals: EvoSkill 関連提案IDリスト

    Returns:
        記録された実験の dict
    """
    exp_id = _generate_id(category)
    now = _now_iso()

    experiment = {
        "id": exp_id,
        "category": category,
        "hypothesis": hypothesis,
        "branch": branch,
        "files_changed": files_changed,
        "status": "pending_review",
        "created_at": now,
        "updated_at": now,
    }

    # EvoSkill H schema fields (optional)
    for key, val in [
        ("proposal_type", proposal_type),
        ("target_skill", target_skill),
        ("failure_evidence", failure_evidence),
        ("validation_result", validation_result),
        ("outcome_reason", outcome_reason),
        ("related_proposals", related_proposals),
    ]:
        if val is not None:
            experiment[key] = val

    # レジストリに追記
    path = _registry_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(experiment, ensure_ascii=False) + "\n")

    return experiment


def list_experiments(status: str | None = None) -> list[dict]:
    """実験一覧を返す。

    Args:
        status: フィルタするステータス (None なら全て)

    Returns:
        実験の list[dict]
    """
    experiments = _load_registry()
    if status is not None:
        experiments = [e for e in experiments if e.get("status") == status]
    return experiments


def update_status(exp_id: str, status: str) -> None:
    """実験のステータスを更新する。

    Args:
        exp_id: 実験ID
        status: 新しいステータス (pending_review, merged, rejected, reverted)
    """
    experiments = _load_registry()
    for exp in experiments:
        if exp["id"] == exp_id:
            exp["status"] = status
            exp["updated_at"] = _now_iso()
            if status == "merged":
                exp["merged_at"] = _now_iso()
            break
    _save_registry(experiments)


def record_cross_impact(exp_id: str, cross_impact: dict) -> None:
    """実験のクロスカテゴリ影響を記録する。

    Args:
        exp_id: 実験ID
        cross_impact: カテゴリ -> {before, after, note} の dict
    """
    experiments = _load_registry()
    for exp in experiments:
        if exp["id"] == exp_id:
            exp["cross_impact"] = cross_impact
            exp["updated_at"] = _now_iso()
            break
    _save_registry(experiments)


def build_proposer_context(
    target_skill: str,
    limit: int = 20,
    archive_days: int = 60,
) -> str:
    """対象スキル関連のフィードバック履歴を Proposer 注入用テキストに整形。

    Args:
        target_skill: 対象スキル名
        limit: 直近エントリの最大件数
        archive_days: これ以上古いエントリはサマリー化

    Returns:
        markdown テーブル形式のフィードバック履歴
    """
    registry_path = _registry_path()
    if not registry_path.exists():
        return "_フィードバック履歴なし_"

    entries = []
    with open(registry_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if entry.get("target_skill") == target_skill or (
                entry.get("category") == "skills"
                and target_skill in " ".join(entry.get("files_changed", []))
            ):
                entries.append(entry)

    if not entries:
        return f"_{target_skill} に関連するフィードバック履歴なし_"

    entries.sort(key=lambda e: e.get("created_at", ""), reverse=True)

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=archive_days)
    cutoff_iso = cutoff.isoformat()

    recent = [e for e in entries if e.get("created_at", "") >= cutoff_iso][:limit]
    archived = [e for e in entries if e.get("created_at", "") < cutoff_iso]

    lines = ["## フィードバック履歴", ""]
    if recent:
        lines.append("| ID | 提案 | 結果 | delta | 理由 |")
        lines.append("|---|---|---|---|---|")
        for e in recent:
            exp_id = e.get("id", "?")
            hypothesis = e.get("hypothesis", "?")[:40]
            status = e.get("status", "?")
            vr = e.get("validation_result", {})
            delta = vr.get("ab_delta", "-")
            reason = (
                e.get("outcome_reason", "-")[:30] if e.get("outcome_reason") else "-"
            )
            lines.append(f"| {exp_id} | {hypothesis} | {status} | {delta} | {reason} |")

    if archived:
        lines.append("")
        lines.append(
            f"_+ {len(archived)} 件のアーカイブ済みエントリ（{archive_days} 日以上前）_"
        )

    return "\n".join(lines)


def measure_effect(exp_id: str) -> dict:
    """マージ済み実験の効果を測定する。

    マージ日の前後7日間の learnings データを比較し、
    イベント数の増減から効果を判定する。

    判定基準:
        - <=−20%: keep (効果あり)
        - >=+20%: discard (悪化)
        - その他: neutral

    Args:
        exp_id: 実験ID

    Returns:
        {verdict, before_count, after_count, change_pct} の dict
    """
    experiments = _load_registry()
    exp = None
    for e in experiments:
        if e["id"] == exp_id:
            exp = e
            break

    if exp is None:
        return {"verdict": "insufficient_data", "error": "experiment not found"}

    merged_at_str = exp.get("merged_at")
    if not merged_at_str:
        return {"verdict": "insufficient_data", "error": "experiment not yet merged"}

    merged_at = datetime.fromisoformat(merged_at_str)
    category = exp["category"]

    # learnings データを読む
    learnings_path = _get_data_dir() / "learnings" / f"{category}.jsonl"
    if not learnings_path.exists():
        return {"verdict": "insufficient_data", "error": "no learnings data"}

    before_window_start = merged_at - timedelta(days=7)
    after_window_end = merged_at + timedelta(days=7)

    before_count = 0
    after_count = 0

    with open(learnings_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            ts_str = entry.get("timestamp")
            if not ts_str:
                continue

            try:
                ts = datetime.fromisoformat(ts_str)
            except (ValueError, TypeError):
                continue

            if before_window_start <= ts < merged_at:
                before_count += 1
            elif merged_at <= ts <= after_window_end:
                after_count += 1

    # データ不足判定
    if before_count == 0 and after_count == 0:
        return {"verdict": "insufficient_data", "before_count": 0, "after_count": 0}

    # 変化率計算
    if before_count == 0:
        change_pct = 100.0 if after_count > 0 else 0.0
    else:
        change_pct = ((after_count - before_count) / before_count) * 100.0

    # 判定
    if change_pct <= -20.0:
        verdict = "keep"
    elif change_pct >= 20.0:
        verdict = "discard"
    else:
        verdict = "neutral"

    return {
        "verdict": verdict,
        "before_count": before_count,
        "after_count": after_count,
        "change_pct": round(change_pct, 1),
    }


def export_tsv() -> str:
    """全実験を autoresearch の results.tsv 風フラット TSV で出力する。"""
    experiments = _load_registry()
    lines = ["date\tcategory\tid\tstatus\thypothesis\tchange_pct\tverdict\tfiles"]
    for exp in experiments:
        date = exp.get("created_at", "")[:10]
        category = exp.get("category", "")
        exp_id = exp.get("id", "")
        status = exp.get("status", "")
        hypothesis = exp.get("hypothesis", "").replace("\t", " ")[:80]
        change_pct = ""
        verdict = ""
        if status == "merged":
            result = measure_effect(exp_id)
            verdict = result.get("verdict", "")
            cp = result.get("change_pct")
            change_pct = f"{cp}" if cp is not None else ""
        files = ",".join(exp.get("files_changed", []))
        lines.append(
            f"{date}\t{category}\t{exp_id}\t{status}\t{hypothesis}\t{change_pct}\t{verdict}\t{files}"
        )
    return "\n".join(lines)


def status_summary() -> str:
    """実験のステータスサマリーを返す。"""
    experiments = _load_registry()
    if not experiments:
        return "実験データなし"
    counts: dict[str, int] = {}
    for exp in experiments:
        s = exp.get("status", "unknown")
        counts[s] = counts.get(s, 0) + 1
    parts = [f"{k}: {v}" for k, v in sorted(counts.items())]
    return f"全 {len(experiments)} 件 — " + ", ".join(parts)


def main():
    """CLI エントリポイント。"""
    parser = argparse.ArgumentParser(
        description="AutoEvolve experiment tracker",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # record サブコマンド
    record_parser = subparsers.add_parser("record", help="Record a new experiment")
    record_parser.add_argument("--category", required=True, help="Experiment category")
    record_parser.add_argument(
        "--hypothesis", required=True, help="Hypothesis description"
    )
    record_parser.add_argument("--branch", required=True, help="Experiment branch name")
    record_parser.add_argument(
        "--files", nargs="+", required=True, help="Changed files"
    )

    # list サブコマンド
    list_parser = subparsers.add_parser("list", help="List experiments")
    list_parser.add_argument("--status", default=None, help="Filter by status")

    # measure サブコマンド
    measure_parser = subparsers.add_parser("measure", help="Measure experiment effect")
    measure_parser.add_argument("exp_id", help="Experiment ID")

    # export-tsv サブコマンド
    subparsers.add_parser("export-tsv", help="Export all experiments as TSV")

    # status サブコマンド
    subparsers.add_parser("status", help="Show experiment status summary")

    # measure-all サブコマンド
    subparsers.add_parser("measure-all", help="Measure all merged experiments")

    # proposer-context サブコマンド
    proposer_ctx = subparsers.add_parser(
        "proposer-context", help="Build proposer context for a skill"
    )
    proposer_ctx.add_argument("--skill", required=True, help="Target skill name")
    proposer_ctx.add_argument("--limit", type=int, default=20)

    args = parser.parse_args()

    if args.command == "record":
        exp = record_experiment(
            category=args.category,
            hypothesis=args.hypothesis,
            branch=args.branch,
            files_changed=args.files,
        )
        print(json.dumps(exp, indent=2, ensure_ascii=False))

    elif args.command == "list":
        exps = list_experiments(status=args.status)
        for exp in exps:
            status_mark = {
                "pending_review": "⏳",
                "merged": "✅",
                "rejected": "❌",
                "reverted": "↩️",
            }.get(exp.get("status", ""), "?")
            print(
                f"{status_mark} {exp['id']} [{exp['status']}] {exp['hypothesis'][:60]}"
            )

    elif args.command == "measure":
        result = measure_effect(args.exp_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "export-tsv":
        print(export_tsv())

    elif args.command == "status":
        print(status_summary())

    elif args.command == "measure-all":
        exps = list_experiments(status="merged")
        if not exps:
            print("測定対象の merged 実験がありません")
        for exp in exps:
            result = measure_effect(exp["id"])
            verdict = result.get("verdict", "?")
            change = result.get("change_pct", "N/A")
            print(f"{exp['id']}: {verdict} (change: {change}%)")

    elif args.command == "proposer-context":
        print(build_proposer_context(args.skill, args.limit))


if __name__ == "__main__":
    main()
