"""AutoEvolve experiment tracker.

実験の記録、ステータス管理、効果測定を行う。
改善サイクルで作成された変更（ブランチ）を追跡し、
マージ後の効果を learnings データから測定する。

Usage:
    python experiment_tracker.py record --category errors \
        --hypothesis "..." --branch autoevolve/errors-2026-03-10 \
        --files f1.md f2.md
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
    source_domain: str | None = None,
    transfer_efficacy: float | None = None,
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
        source_domain: 改善の元ドメイン（別ドメインからの転移の場合）
        transfer_efficacy: 転移効率 (0.0-1.0、元ドメインでの delta に対する比率)

    Returns:
        記録された実験の dict
    """
    if transfer_efficacy is not None and not (0.0 <= transfer_efficacy <= 1.0):
        raise ValueError(
            f"transfer_efficacy must be in [0.0, 1.0], got {transfer_efficacy}"
        )

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
        ("source_domain", source_domain),
        ("transfer_efficacy", transfer_efficacy),
    ]:
        if val is not None:
            experiment[key] = val

    # レジストリに追記
    path = _registry_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(experiment, ensure_ascii=False) + "\n")

    return experiment


def list_experiments(
    status: str | None = None,
    transfers_only: bool = False,
) -> list[dict]:
    """実験一覧を返す。

    Args:
        status: フィルタするステータス (None なら全て)
        transfers_only: True なら転移実験のみ返す

    Returns:
        実験の list[dict]
    """
    experiments = _load_registry()
    if status is not None:
        experiments = [e for e in experiments if e.get("status") == status]
    if transfers_only:
        experiments = [e for e in experiments if e.get("source_domain") is not None]
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


def select_next_target(
    degraded_skills: list[str],
) -> str | None:
    """ラウンドロビンで次の改善対象スキルを選定。

    直近の H で最も長く改善されていないスキルを優先。
    全対象を 1 回ずつ探索してから 2 周目へ。

    Args:
        degraded_skills: degraded/failing スキル名リスト

    Returns:
        次の対象スキル名。対象がなければ None
    """
    if not degraded_skills:
        return None

    registry_path = _registry_path()
    if not registry_path.exists():
        return degraded_skills[0]

    last_proposed: dict[str, str] = {}
    with open(registry_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            skill = entry.get("target_skill")
            if skill and skill in degraded_skills:
                ts = entry.get("created_at", "")
                if ts > last_proposed.get(skill, ""):
                    last_proposed[skill] = ts

    never_proposed = [s for s in degraded_skills if s not in last_proposed]
    if never_proposed:
        return never_proposed[0]

    return min(last_proposed, key=last_proposed.get)


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
    category = exp.get("category", "")

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


def compute_cqs() -> dict:
    """全実験から Cumulative Quality Score を計算する。

    merged 実験の measure_effect() verdict に基づくスコア:
      keep: +10 * abs(change_pct) / 100
      discard: -15
      neutral: -2

    5件未満の場合は insufficient_data を返す。

    Returns:
        {"cqs": float, "total_experiments": int, "breakdown": {...}}
    """
    experiments = _load_registry()
    merged = [e for e in experiments if e.get("status") == "merged"]

    if len(merged) < 5:
        return {
            "cqs": 0.0,
            "total_experiments": len(merged),
            "status": "insufficient_data",
            "breakdown": {"keep": 0, "discard": 0, "neutral": 0},
        }

    cqs = 0.0
    breakdown = {"keep": 0, "discard": 0, "neutral": 0, "insufficient_data": 0}

    for exp in merged:
        result = measure_effect(exp["id"])
        verdict = result.get("verdict", "insufficient_data")
        if verdict == "keep":
            change_pct = abs(result.get("change_pct", 0))
            cqs += 10 * change_pct / 100
            breakdown["keep"] += 1
        elif verdict == "discard":
            cqs -= 15
            breakdown["discard"] += 1
        elif verdict == "neutral":
            cqs -= 2
            breakdown["neutral"] += 1
        else:
            breakdown["insufficient_data"] += 1

    return {
        "cqs": round(cqs, 2),
        "total_experiments": len(merged),
        "status": "ok",
        "breakdown": breakdown,
    }


def check_regression(exp_id: str, min_sessions: int = 3) -> dict:
    """merged 実験後の品質回帰を検出する。

    判定ロジック:
    1. merged 後 min_sessions セッション以上経過していること（安定化待ち）
    2. merged 後の error_rate が merged 前より 20% 以上増加
    3. OR: merged 後に同カテゴリの discard が 2 件以上発生
    4. OR: CQS が merged 時点から -5 以上低下

    Args:
        exp_id: 検査対象の実験ID
        min_sessions: 安定化待ちの最小セッション数

    Returns:
        {"regression": bool, "reason": str, "suggestion": str}
    """
    experiments = _load_registry()
    exp = None
    for e in experiments:
        if e["id"] == exp_id:
            exp = e
            break

    if exp is None:
        return {"regression": False, "reason": "experiment not found", "suggestion": ""}

    if exp.get("status") != "merged":
        return {"regression": False, "reason": "not merged", "suggestion": ""}

    merged_at_str = exp.get("merged_at")
    if not merged_at_str:
        return {
            "regression": False,
            "reason": "no merged_at timestamp",
            "suggestion": "",
        }

    merged_at = datetime.fromisoformat(merged_at_str)
    category = exp.get("category", "")

    # Check 1: 安定化待ち — merged 後のセッション数を確認
    metrics_path = _get_data_dir() / "metrics" / "session-metrics.jsonl"
    if not metrics_path.exists():
        return {
            "regression": False,
            "reason": "session-metrics not found",
            "suggestion": "",
        }
    post_merge_sessions = 0
    with open(metrics_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                ts_str = entry.get("timestamp", "")
                if not ts_str:
                    continue
                ts = datetime.fromisoformat(ts_str)
                if ts > merged_at:
                    post_merge_sessions += 1
            except (json.JSONDecodeError, ValueError, TypeError):
                continue

    if post_merge_sessions < min_sessions:
        return {
            "regression": False,
            "reason": (
                f"insufficient sessions after merge"
                f" ({post_merge_sessions}/{min_sessions})"
            ),
            "suggestion": "",
        }

    # Check 2: error_rate 増加
    effect = measure_effect(exp_id)
    if effect.get("verdict") == "discard":
        change_pct = effect.get("change_pct", 0)
        return {
            "regression": True,
            "reason": f"error_rate increased by {change_pct}% after merge",
            "suggestion": f"revert {exp_id}",
        }

    # Check 3: 同カテゴリの discard が 2 件以上
    post_merge_discards = 0
    for other in experiments:
        if other.get("category") != category:
            continue
        if other.get("status") != "merged":
            continue
        if other.get("id") == exp_id:
            continue
        other_result = measure_effect(other.get("id", ""))
        if other_result.get("verdict") == "discard":
            other_merged = other.get("merged_at", "")
            if not other_merged:
                continue
            try:
                other_dt = datetime.fromisoformat(other_merged)
                if other_dt > merged_at:
                    post_merge_discards += 1
            except (ValueError, TypeError):
                continue

    if post_merge_discards >= 2:
        return {
            "regression": True,
            "reason": (
                f"{post_merge_discards} discards in category '{category}' after merge"
            ),
            "suggestion": f"revert {exp_id}",
        }

    # Check 4: CQS の大幅低下は compute_cqs() のスナップショット比較が必要
    # 現時点では CQS は累積値のため、単一実験の影響を分離するのは困難
    # 将来的に CQS スナップショットを導入した場合に追加する

    return {"regression": False, "reason": "no regression detected", "suggestion": ""}


def transfer_report() -> str:
    """転移効率の集計レポートを生成する。

    source_domain が記録されている実験の転移効率を集計し、
    ドメインペアごとの平均転移効率を出力する。

    Returns:
        markdown テーブル形式のレポート
    """
    experiments = _load_registry()
    transfers = [e for e in experiments if e.get("source_domain") is not None]

    if not transfers:
        return "転移データなし"

    # ドメインペア別集計
    pair_stats: dict[tuple[str, str], list[float]] = {}
    for exp in transfers:
        source = exp["source_domain"]
        target = exp.get("category", "unknown")
        efficacy = exp.get("transfer_efficacy")
        if efficacy is not None:
            pair = (source, target)
            pair_stats.setdefault(pair, []).append(efficacy)

    if not pair_stats:
        return "転移効率データなし（source_domain はあるが transfer_efficacy が未記録）"

    lines = [
        "## 転移効率レポート",
        "",
        "| source | target | avg_efficacy | count |",
        "|--------|--------|-------------|-------|",
    ]
    for (source, target), values in sorted(pair_stats.items()):
        avg = sum(values) / len(values)
        lines.append(f"| {source} | {target} | {avg:.2f} | {len(values)} |")

    return "\n".join(lines)


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
    """実験のステータスサマリーを返す（CQS 付き）。"""
    experiments = _load_registry()
    if not experiments:
        return "実験データなし"
    counts: dict[str, int] = {}
    for exp in experiments:
        s = exp.get("status", "unknown")
        counts[s] = counts.get(s, 0) + 1
    parts = [f"{k}: {v}" for k, v in sorted(counts.items())]
    summary = f"全 {len(experiments)} 件 — " + ", ".join(parts)

    cqs_result = compute_cqs()
    if cqs_result["status"] == "insufficient_data":
        summary += (
            f"\nCQS: N/A (データ不足: {cqs_result['total_experiments']}/5 merged)"
        )
    else:
        b = cqs_result["breakdown"]
        summary += (
            f"\nCQS: {cqs_result['cqs']} "
            f"(keep:{b['keep']} discard:{b['discard']}"
            f" neutral:{b['neutral']})"
        )
    return summary


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
    list_parser.add_argument(
        "--transfers", action="store_true", help="Show only transfer experiments"
    )

    # measure サブコマンド
    measure_parser = subparsers.add_parser("measure", help="Measure experiment effect")
    measure_parser.add_argument("exp_id", help="Experiment ID")

    # export-tsv サブコマンド
    subparsers.add_parser("export-tsv", help="Export all experiments as TSV")

    # status サブコマンド
    subparsers.add_parser("status", help="Show experiment status summary")

    # measure-all サブコマンド
    subparsers.add_parser("measure-all", help="Measure all merged experiments")

    # next-target サブコマンド
    next_target = subparsers.add_parser(
        "next-target", help="Select next evolution target (round-robin)"
    )
    next_target.add_argument(
        "--skills", required=True, help="Comma-separated degraded skill names"
    )

    # check-regression サブコマンド
    check_reg = subparsers.add_parser(
        "check-regression",
        help="Check for quality regression after merge",
    )
    check_reg.add_argument("exp_id", help="Experiment ID")
    check_reg.add_argument(
        "--min-sessions",
        type=int,
        default=3,
        help="Min sessions after merge",
    )

    # transfer-report サブコマンド
    subparsers.add_parser("transfer-report", help="Show transfer efficacy report")

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
        exps = list_experiments(status=args.status, transfers_only=args.transfers)
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

    elif args.command == "next-target":
        skills = [s.strip() for s in args.skills.split(",")]
        result = select_next_target(skills)
        print(result or "NO_TARGET")

    elif args.command == "check-regression":
        result = check_regression(args.exp_id, args.min_sessions)
        if result["regression"]:
            print(f"[ROLLBACK SUGGESTED] {args.exp_id}: {result['reason']}")
        else:
            print(f"OK: {result['reason']}")

    elif args.command == "transfer-report":
        print(transfer_report())

    elif args.command == "proposer-context":
        print(build_proposer_context(args.skill, args.limit))


if __name__ == "__main__":
    main()
