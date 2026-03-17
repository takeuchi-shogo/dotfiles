# SkillRL 統合設計 — AutoEvolve 自己改善スキルの強化

**Date**: 2026-03-17
**Status**: Approved
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
| `scripts/lib/session_events.py` | `emit_skill_event` に task_type 自動推論を追加（1箇所） |
| `scripts/learner/session-learner.py` | 成功蒸留トリガー + task_type フィールド追加（2箇所） |
| `agents/autoevolve-core.md` | Phase 1 に率ベース分析、Phase 2 に率ベーストリガー、Phase 3 に圧縮（3セクション） |
| `skills/skill-creator/SKILL.md` | Cold-Start 蒸留ステップ追加（1セクション） |

### データフロー

```
Session End
    │
    ├─ session-learner.py
    │   ├─ (既存) errors/quality/patterns → learnings/*.jsonl
    │   ├─ (既存) skill-executions.jsonl (+ task_type フィールド追加)
    │   └─ (新規) skill_distiller.distill_session() → success-strategies.jsonl
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

出力先: `learnings/success-strategies.jsonl`

```json
{
  "timestamp": "...",
  "strategy_type": "skill_selection | tool_usage | error_avoidance",
  "task_type": "feature",
  "project": "webapp-a",
  "skills_used": ["brainstorming", "review"],
  "tools_used": ["Edit", "Bash", "Grep"],
  "context": "...",
  "related_past_failures": []
}
```

#### classify_scope(skill_name: str, data_dir: Path) -> str

skill-executions.jsonl のプロジェクト分布から自動判定:

- 3+ プロジェクト → `"general"`
- 1-2 プロジェクト → `"domain"`
- 実行5回未満 → `"unknown"`

#### compress_learnings(data_dir: Path, target: str) -> int

類似イベントのマージ:

1. 同一 message → 最新のみ残す（count 付き）
2. 同一 failure_mode × project → 代表1件に集約
3. 60日以上前 + insights 反映済み → アーカイブ

安全策: 圧縮前にバックアップ。対象は errors, quality, recovery-tips のみ。

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

#### infer_task_type(skill_names: list[str]) -> str

複数スキル使用時は最頻出タスクタイプを返す。

#### compute_success_rates(data_dir, group_by) -> list[SuccessRate]

group_by = "skill" | "task_type" でグループ別成功率を算出。

判定閾値:
- healthy: rate >= 0.6
- degraded: rate 0.4-0.6 or trend <= -0.15
- failing: rate < 0.4

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
| skill_distiller | test_skill_distiller.py | clean_success 蒸留 / failure スキップ / 圧縮+バックアップ / 空データ安全性 |
| skill_metrics | test_skill_metrics.py | マッピング正引き / prefix 対応 / 成功率計算 / unknown 判定 / トリガー判定 |
| skill_bootstrap | test_skill_bootstrap.py | 関連戦略検索 / 類似スキル検出 / データなしフォールバック |

テスト隔離: `AUTOEVOLVE_DATA_DIR` 環境変数で一時ディレクトリに差し替え。

## Error Handling

- 全公開関数は try/except でラップ。hook をクラッシュさせない
- 失敗時は `logger.error()` で記録し、空のデフォルト値を返す
- 既存パターン（session_events.py, session-learner.py）に準拠

## Backward Compatibility

- `skill-executions.jsonl`: task_type フィールド追加。既存エントリは `.get("task_type", "other")` で安全に読める
- `success-strategies.jsonl`: 新規ファイルなので互換性の問題なし
- `compress_learnings`: バックアップ作成後に圧縮。手動復元可能

## Acceptance Criteria

1. clean_success セッション終了時に success-strategies.jsonl にエントリが追加される
2. `/improve` 実行時にスキル別・タスクタイプ別の成功率レポートが出力される
3. rate < 0.6 のスキルが進化トリガーとして検出される
4. `compress_learnings` で同一 message のエントリがマージされる
5. `generate_skill_seed` が関連データのシードを返す
6. 全テストが PASSED
7. 既存の session-learner / autoevolve フローが regression なく動作する
