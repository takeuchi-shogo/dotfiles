# SkillRL 統合設計 — AutoEvolve 自己改善スキルの強化

**Date**: 2026-03-17
**Status**: Approved (Spec Review Passed)
**Approach**: B (モジュール分離型)
**Source**: SkillRL (arXiv:2602.08234) + cognee-skills 分析

## Summary

SkillRL 論文の知見を既存 AutoEvolve パイプラインに統合し、スキルの自己改善能力を強化する。
5つの改善を3つの新規モジュール + 4つの既存ファイル変更で実現する。

## Goals

1. **成功蒸留**: 成功セッションから再利用可能な戦略パターンを抽出（SkillRL 最大インパクト: +28.2%）
2. **階層分類**: スキルを general / domain に自動分類し、進化トリガーの精度を向上
3. **率ベーストリガー**: 回数ベース（5回以上）に加え、成功率ベースの進化トリガーを追加
4. **Learnings 圧縮**: 類似イベントのマージと陳腐化エントリのアーカイブ（SkillRL: 10-20x 圧縮）
5. **Cold-Start 蒸留**: 新スキル作成時に蓄積データからシードを生成

## Non-Goals

- グラフDB / embedding ベースのセマンティック検索（SkillRL はこれなしで SOTA 達成）
- RL ベースのモデル微調整（Claude Code はプロンプト/設定レベルで運用）
- 完全自動ロールバック（SkillRL の加算方式に倣い、既存の manual review gate を維持）

## Architecture

### 新規ファイル（3個）

| ファイル | 責務 |
|---------|------|
| `scripts/lib/skill_distiller.py` | 成功蒸留 + 階層分類 + Learnings 圧縮 |
| `scripts/lib/skill_metrics.py` | タスクタイプマッピング + 成功率計算 + 進化トリガー判定 |
| `scripts/lib/skill_bootstrap.py` | Cold-Start Teacher 蒸留（蓄積データからスキルシード生成） |

### 既存ファイル変更（4個）

| ファイル | 変更内容 |
|---------|---------|
| `scripts/lib/skill_amender.py` | 閾値定数を `HEALTH_THRESHOLDS` として export（DRY: skill_metrics から参照） |
| `scripts/learner/session-learner.py` | 成功蒸留トリガー + task_type フィールド追加（2箇所） |
| `agents/autoevolve-core.md` | Phase 1 に率ベース分析、Phase 2 に率ベーストリガー、Phase 3 に圧縮（3セクション） |
| `skills/skill-creator/SKILL.md` | Cold-Start 蒸留ステップ追加（1セクション） |

**設計判断**: 当初 `session_events.py` の `emit_skill_event` に task_type 推論を追加する案だったが、
`session_events.py` → `skill_metrics.py` → `storage.py` の循環依存リスクを避けるため、
`session-learner.py` の `process_session()` 内で `skill-executions` への書き出し時に
task_type を付与する方式に変更。

### データフロー

```
Session End
    │
    ├─ session-learner.py
    │   ├─ (既存) errors/quality/patterns → learnings/*.jsonl
    │   ├─ (既存+拡張) skill-executions.jsonl (+ task_type フィールド)
    │   └─ (新規) skill_distiller.distill_session()
    │         └─ [outcome == clean_success のみ] → success-strategies.jsonl
    │
    v
/improve 実行時
    │
    ├─ Phase 1: Analyze
    │   ├─ (既存) エラーパターン分析
    │   └─ (新規) skill_metrics.compute_success_rates()
    │           └─ skill_distiller.classify_scope()
    │
    ├─ Phase 2: Improve
    │   ├─ (既存) 回数ベーストリガー (5回以上)
    │   └─ (新規) 率ベーストリガー (成功率 < 0.6) [OR 併用]
    │
    └─ Phase 3: Garden
        ├─ (既存) 重複排除、陳腐化除去
        └─ (新規) skill_distiller.compress_learnings()

/skill-creator 実行時
    └─ skill_bootstrap.generate_skill_seed()
```

## Module Details

### skill_distiller.py

#### distill_session(summary: dict) -> list[dict]

clean_success セッションから3種の戦略を蒸留:

1. **スキル選択パターン**: タスクタイプ × 発火スキル × 成功
2. **ツール使用パターン**: 使用ツール集合の記録
3. **エラー回避パターン**: 過去に失敗したカテゴリでの clean_success → 差分を記録

**呼び出し元**: `session-learner.py` の `process_session()` 内、スキル実行データ集計の後:

```python
# process_session() 末尾に追加
if summary["outcome"] == "clean_success" and skill_invocations:
    try:
        from skill_distiller import distill_session
        strategies = distill_session(summary)
        for s in strategies:
            append_to_learnings("success-strategies", s)
        logger.info("session-learner: %d success strategies distilled", len(strategies))
    except Exception as e:
        logger.error("session-learner: distill failed: %s", e)
```

`distill_session` は `summary` の `_events`, `_errors`, `_patterns` 内部キーに依存してよい
（`build_session_summary()` の戻り値構造は安定している）。

**task_type の追加**: 同じ `process_session()` 内の既存スキル実行ループ:

```python
for inv in skill_invocations:
    skill_name = inv.get("skill_name", "")
    # ... 既存コード ...
    from skill_metrics import infer_task_type
    task_type = inv.get("task_type") or infer_task_type([skill_name])

    append_to_learnings("skill-executions", {
        # ... 既存フィールド全て維持 ...
        "task_type": task_type,  # 新規追加
    })
```

**戻り値スキーマ** (`timestamp` は含めない — `append_to_learnings` が自動付与):

```json
{
  "strategy_type": "skill_selection | tool_usage | error_avoidance",
  "task_type": "feature",
  "project": "webapp-a",
  "skills_used": ["brainstorming", "review"],
  "tools_used": ["Edit", "Bash", "Grep"],
  "context": "...",
  "related_past_failures": []
}
```

出力先: `learnings/success-strategies.jsonl`

#### classify_scope(skill_name: str, data_dir: Path) -> str

skill-executions.jsonl のプロジェクト分布から自動判定:

- 3+ プロジェクト → `"general"`
- 1-2 プロジェクト → `"domain"`
- 実行5回未満 → `"unknown"`

**制約注記**: `project` フィールドは `Path(cwd).name`（ディレクトリ末尾）のため、
異なるパスで同名ディレクトリがある場合に誤判定の可能性あり。これは既存の session-learner の制約。

#### compress_learnings(data_dir: Path, target: str) -> int

類似イベントのマージ:

1. 同一 message → 最新のみ残す（count 付き）
2. 同一 failure_mode × project → 代表1件に集約
3. 60日以上前 + insights 反映済み → アーカイブ

**バックアップ方針**:
- 命名規則: `{target}.jsonl.{YYYYMMDDTHHMMSS}.bak`（タイムスタンプ付き）
- 保持: 最新3世代。4つ目以降の古い .bak は自動削除
- 書き込み: temp file → `os.replace()` で atomic に置換
- 圧縮前後の件数を logger.info で出力

**排他制御の前提**: `/improve` はユーザーが手動実行するため、
session-learner（SessionEnd hook）と同時実行されない前提。
仕様上 atomic write で安全性を担保するが、明示的なファイルロックは設けない。

対象: errors, quality, recovery-tips のみ。
success-strategies, skill-executions は圧縮しない（トレンド分析に必要）。

### skill_metrics.py

#### TASK_TYPE_MAP

スキル名 → タスクタイプの静的マッピングテーブル:

| タスクタイプ | スキル例 |
|------------|---------|
| review | review, codex-review, security-review |
| feature | brainstorming, spike, epd, frontend-design, rpi |
| bugfix | fix-issue, systematic-debugging |
| refactor | simplify, challenge |
| docs | spec, obsidian-content, obsidian-knowledge |
| test | test-driven-development |
| infra | init-project, update-config, setup-background-agents |
| other | (デフォルト) |

prefix 対応: `"review:security-review"` → prefix `"review"` を優先使用

**メンテナンス**: マッピングにないスキル名が来た場合、`"other"` にフォールバックしつつ
`logger.warning("unmapped skill: %s", name)` を出力し更新を促す。

#### infer_task_type(skill_names: list[str]) -> str

複数スキル使用時は最頻出タスクタイプを返す。

#### compute_success_rates(data_dir, group_by) -> list[SuccessRate]

group_by = "skill" | "task_type" でグループ別成功率を算出。

**閾値**: `skill_amender.HEALTH_THRESHOLDS` を参照（DRY）:
- healthy: rate >= 0.6
- degraded: rate 0.4-0.6 or trend <= -0.15
- failing: rate < 0.4

`compute_success_rates` は集計と判定を行うが、閾値定数は `skill_amender.py` に
一元管理し、`from skill_amender import HEALTH_THRESHOLDS` で参照する。

#### check_evolution_triggers(data_dir, min_executions) -> list[EvolutionTrigger]

率ベースの進化トリガーを検出。既存の回数ベースと OR 併用。

### skill_bootstrap.py

#### generate_skill_seed(skill_name, description, data_dir) -> dict

蓄積データから新スキルの初期コンテンツのシードを生成:

- `related_strategies`: success-strategies.jsonl からキーワードマッチ
- `common_tools`: 関連タスクタイプで使われるツール
- `failure_patterns`: 避けるべきパターン（errors.jsonl + recovery-tips.jsonl）
- `suggested_steps`: 類似スキルからの類推
- `similar_skills`: AP-1 チェック兼用

初期実装はキーワードマッチ。外部 CLI 依存なし。

## Testing

| モジュール | テストファイル | 主要ケース |
|-----------|-------------|-----------|
| skill_distiller | test_skill_distiller.py | clean_success 蒸留 / failure スキップ / 圧縮+バックアップ+世代管理 / 空データ安全性 |
| skill_metrics | test_skill_metrics.py | マッピング正引き / prefix 対応 / unmapped warning / 成功率計算 / unknown 判定 / トリガー判定 |
| skill_bootstrap | test_skill_bootstrap.py | 関連戦略検索 / 類似スキル検出 / データなしフォールバック |
| (統合) | test_session_learner.py に追加 | process_session → distill_session E2E フロー / task_type フィールド付与 |

テスト隔離: `AUTOEVOLVE_DATA_DIR` 環境変数で一時ディレクトリに差し替え。

## Error Handling

- 全公開関数は try/except でラップ。hook をクラッシュさせない
- 失敗時は `logger.error()` で記録し、空のデフォルト値を返す
- 既存パターン（session_events.py, session-learner.py）に準拠

## Backward Compatibility

- `skill-executions.jsonl`: task_type フィールド追加。既存エントリは `.get("task_type", "other")` で安全に読める
- `success-strategies.jsonl`: 新規ファイルなので互換性の問題なし
- `compress_learnings`: atomic write + 3世代バックアップで安全に圧縮

## Acceptance Criteria

1. clean_success セッション（スキル invocation 1件以上）終了時に、success-strategies.jsonl に 1件以上のエントリが追加される
2. `/improve` 実行時に、skill_metrics がスキル別・タスクタイプ別の成功率を `list[SuccessRate]` として返す
3. skill-executions.jsonl に 10件以上のエントリがあるスキルで成功率 < 0.6 の場合、`check_evolution_triggers` が非空リストを返す
4. 同一 message のエントリが 3件ある learnings ファイルに対し、`compress_learnings` 実行後に同 message は 1件（count >= 3）になり、タイムスタンプ付き .bak が作成される
5. `generate_skill_seed` が `related_strategies`, `common_tools`, `failure_patterns`, `suggested_steps`, `similar_skills` キーを含む dict を返す
6. 全テスト（単体 + 統合）が PASSED
7. 既存の session-learner / autoevolve フローが regression なく動作する

## Spec Review Findings (Addressed)

| 区分 | 指摘 | 対応 |
|------|------|------|
| CRITICAL | `emit_skill_event` 変更仕様不足 | `session-learner.py` 側で task_type 付与に変更。擬似コード追記 |
| CRITICAL | `session-learner.py` 統合詳細不足 | 呼び出し擬似コード + 条件分岐を明記 |
| CRITICAL | `compress_learnings` データ安全性 | タイムスタンプ付きバックアップ + 3世代保持 + atomic write |
| SUGGESTION | `assess_health` 責務重複 | `HEALTH_THRESHOLDS` を `skill_amender.py` に一元管理 |
| SUGGESTION | timestamp 二重付与 | `distill_session` の戻り値から timestamp を除外 |
| SUGGESTION | 受入基準定量化 | 基準 1,3,4 を定量的に書き換え |
| SUGGESTION | 統合テスト不在 | `test_session_learner.py` への統合テスト追加を明記 |
| SUGGESTION | `TASK_TYPE_MAP` メンテナンス | unmapped スキルに logger.warning を出力 |
| SUGGESTION | `classify_scope` 制約 | project フィールドの制約を注記 |
