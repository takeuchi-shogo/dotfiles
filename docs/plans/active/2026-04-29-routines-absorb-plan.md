---
plan_id: 2026-04-29-routines-absorb
status: active
created: 2026-04-29
source_analysis: docs/research/2026-04-29-yamadashy-routines-perf-tuning-absorb-analysis.md
size: L
estimated_files: 13
priority: A>B>E>F>C>D
---

# Integration Plan: yamadashy Routines & Perf Tuning Absorb

## Overview

| Field | Value |
|-------|-------|
| Source | https://zenn.dev/yamadashy/articles/claude-code-routines-perf-tuning |
| Analysis | `docs/research/2026-04-29-yamadashy-routines-perf-tuning-absorb-analysis.md` |
| Total Tasks | 6 (A, B, E, F, C, D) |
| Estimated Size | L (13 ファイル、うち 1 新規) |
| Priority | A > B > E > F > C > D |

---

## Tasks

### Task A: Improvement Vectors matrix (P0)

| Field | Value |
|-------|-------|
| Size | M (3 ファイル) |
| Dependencies | なし (最初に実装) |
| Branch | `autoevolve-vectors-matrix` |

**Changes:**

1. **Edit `.config/claude/references/improve-policy.md`**
   - 新セクション「## Improvement Vectors」を追加
   - 標準 5 軸を定義: `clarity` / `brevity` / `accuracy` / `coverage` / `consistency`
   - 設計: 標準 5 軸 + freeform tags の hybrid (将来拡張時の硬直化を防止)
   - 全提案が 1 つ以上の vector に属することを必須化する Rule を追記

2. **Edit `.config/claude/agents/autoevolve-core.md`**
   - PROPOSE phase の proposal スキーマに `improvement_vectors[]` を必須フィールドとして追加
   - フィールド記述例: `improvement_vectors: ["clarity", "brevity"]` または `improvement_vectors: ["custom:error-handling"]`

3. **Edit `.config/claude/skills/improve/SKILL.md`**
   - Phase 3 PROPOSE セクションの proposal 必須フィールド一覧に `improvement_vectors[]` を追加
   - 「vectors なき提案は PROPOSE 段階でリジェクト」を明記

**受入条件**: 任意の `/improve --dry-run` 出力で全提案に `improvement_vectors` フィールドが含まれること。

---

### Task B: End-to-End Improvement Floor (P0)

| Field | Value |
|-------|-------|
| Size | M (2 ファイル) |
| Dependencies | Task A (vectors を holdout 評価軸として参照) |
| Branch | `autoevolve-e2e-floor` |

**Changes:**

1. **Edit `.config/claude/references/improve-policy.md`**
   - 新 Rule (Rule 49 想定) "End-to-End Improvement Floor" を追加
   - Multi-condition 定義:
     ```
     PASS conditions (全て満たすこと):
     (1) holdout pass_rate delta ≥ +1pp
     (2) regression-suite で新規失敗 0 件
     (3) gaming-detector.py で Goodhart フラグなし
     ```
   - LLM 品質文脈での 2% 直輸入不可の理由を注釈: 分散・評価者ブレ・Goodhart
   - 既存の accept_rate 条件との関係を明確化 (accept_rate は Convergence Check 専用、E2E floor は ROBUST 判定専用)

2. **Edit `.config/claude/skills/improve/SKILL.md`**
   - Phase 4 ADVERSARIAL GATE の ROBUST 判定の必要条件として E2E floor の 3 条件を追加
   - 1 つでも条件未達なら ROBUST 不可であることをレポートで明示するよう指示

**受入条件**: 1 つでも条件未達なら ROBUST 不可となり、レポートに未達条件が明示される。

---

### Task E: 成果属性メタデータ (P1)

| Field | Value |
|-------|-------|
| Size | M (3 ファイル) |
| Dependencies | Task A (vectors), Task B (holdout_delta) |
| Branch | `autoevolve-outcome-metadata` |

**Changes:**

1. **Edit `.config/claude/agents/autoevolve-core.md`**
   - commit message footer に JSON メタデータ必須化
   - フォーマット:
     ```json
     {
       "improvement_vectors": ["clarity", "brevity"],
       "holdout_delta": {"pass_rate": "+1.2pp", "eval_tuples": 42},
       "regression_summary": {"new_failures": 0, "gaming_flags": 0}
     }
     ```

2. **Edit `.config/claude/skills/improve/instructions/proposals-report.md`**
   - メタデータフォーマット仕様セクションを追加
   - 各フィールドの型定義と必須/任意区分を明記

3. **Edit `.config/claude/references/improve-policy.md`**
   - Rule 1 (single-commit) に「成果属性メタデータ必須」を追記
   - メタデータなき commit は autoevolve 由来として認識されないことを明示

**受入条件**: `autoevolve/*` commit log で全自動生成 commit にメタデータ JSON が埋め込まれていること。

---

### Task F: Plateau 多軸検出 (P1)

| Field | Value |
|-------|-------|
| Size | S-M (2 ファイル) |
| Dependencies | Task B (holdout 軸の標準化) |
| Branch | `autoevolve-plateau-multiaxis` |

**Changes:**

1. **Edit `.config/claude/skills/improve/SKILL.md`**
   - Convergence Check セクションを拡張
   - 真の plateau 判定条件 (多軸 AND):
     ```
     (1) accept_rate ≤ 0.30 (直近 10 提案)
     (2) holdout pass_rate 直近 3 サイクル横ばい ±0.5pp
     (3) 全 MDE カテゴリで delta ≤ MDE
     ```
   - 段階運用: Phase 1 = 1 軸でも条件充足で警告、Phase 2 = 3 軸全充足で確定 plateau
   - Trajectory Scoring への言及: 最終出力だけでなく過程 (中間 proposal 品質) も plateau 指標に含めることを推奨

2. **Edit `.config/claude/references/improve-policy.md`**
   - Rule 2 (Convergence) の既存条件を多軸条件に同期更新
   - 段階運用 (Phase 1/Phase 2) の定義を追記

**受入条件**: 模擬 plateau データで多軸条件のうち 1 つでも未達なら警告が抑止される (Phase 1 挙動)。

---

### Task C: _dashboard.md sparkline (P2)

| Field | Value |
|-------|-------|
| Size | S-M (2 ファイル、うち 1 新規 script) |
| Dependencies | なし (並列可) |
| Branch | `autoevolve-dashboard-sparkline` |

**Changes:**

1. **Write `.config/claude/scripts/benchmark/dashboard_generator.py`** (新規)
   - `improve-history.jsonl` の直近 N 件 (デフォルト 20) を読み込み
   - Markdown 表 + ASCII sparkline (▁▂▃▄▅▆▇█) を `runs/_dashboard.md` に出力
   - 可視化対象メトリクス: `adoption_rate` / `cycle_time` / `eval_tuple_count`
   - 引数: `--history <path>` `--output <path>` `--window <n>`

2. **Edit `.config/claude/skills/improve/SKILL.md`**
   - Phase 5 REPORT 末尾に dashboard_generator.py 実行ステップを 1 行追加:
     ```bash
     python .config/claude/scripts/benchmark/dashboard_generator.py --history runs/improve-history.jsonl --output runs/_dashboard.md
     ```

**受入条件**: 模擬 `improve-history.jsonl` を入力として `_dashboard.md` が生成され、sparkline で 3 メトリクスの傾向が一目で確認できること。

---

### Task D: Routines pilot 仕様化 (P3)

| Field | Value |
|-------|-------|
| Size | S (1 ファイル) |
| Dependencies | なし (並列可、ただし実機 pilot は別セッション) |
| Branch | `autoevolve-routines-pilot-spec` |

**Changes:**

1. **Edit `.config/claude/references/managed-agents-scheduling.md`**
   - Phase 1 試行手順を具体化するセクション「## Routines Pilot: Daily Health Check」を追加
   - 内容:
     - (a) Daily Health Check の cloud Routines 化コマンド例 (2h interval 設定)
     - (b) 1 週間並行運転時の比較メトリクス定義 (local cron vs cloud Routines の実行成功率・遅延分布)
     - (c) ロールバック手順 (Routines 無効化 → local cron 再有効化)
     - (d) 結果記録テンプレート (`runs/routines-pilot-YYYY-MM-DD.md`)
   - Mac sleep 耐性の問題 (local cron は sleep 中断を受ける) を注記

**受入条件**: 仕様ドキュメントだけで、別セッションで実機 pilot を開始できる完結性を持つこと。

---

## Execution Order

```
順序 1 (直列):
  Task A (vectors matrix)
    ↓ 依存
  Task B (E2E floor)
    ↓ 依存
  Task E (outcome metadata)
    ↓ 依存
  Task F (plateau multiaxis)

順序 2 (並列、順序 1 と独立):
  Task C (dashboard sparkline)
  Task D (routines pilot spec)
```

推奨実行: A → B → E → F を 1 セッション、C + D を別セッションまたは後続セッション。

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| A の vectors を 5 軸に固定すると将来拡張が硬直 | M | 標準 5 軸 + freeform tags の hybrid 設計で拡張コストを最小化 |
| B の Anti-Gaming check が誤検知 → ROBUST が出にくくなる | H | gaming-detector.py の閾値は既存値を継承、変更しない |
| E のメタデータ要求が autoevolve-core の token 消費を増加 | L | JSON は 200–300 token 程度、許容範囲内 |
| F の plateau 多軸条件が厳しすぎて警告が出なくなる | M | 段階運用 (Phase 1: 1 軸でも警告、Phase 2: 多軸で確定) |
| C の dashboard_generator.py がメンテ負債化 | L | Build to Delete 設計: 将来 AutoEvolve が内包したら削除 |

---

## Pre-mortem

- **A 硬直**: vectors を Enum に固定すると 半年後に追加コスト高。→ freeform tags を hybrid で許容
- **B 誤検知**: gaming-detector の False Positive が多いと改善が詰まる。→ 既存閾値継承、変更は別 ADR
- **E token 増加**: JSON footer が長いと context 圧迫。→ JSON は minified、200-300 token 上限を明記
- **F 過厳格**: 3 軸全充足 plateau は実際には稀。→ Phase 1 警告を先に出し、ユーザーが判断できる設計
- **C メンテ**: sparkline script が更新されず陳腐化。→ SKILL.md の実行コマンドに版管理なし = 削除しやすい設計

---

## Rollback

- 各 Task は独立した branch で進める
- A+B 完了後に E+F → C → D の順でマージ
- 各 Task でテスト失敗があれば直前の commit に revert
- gaming-detector.py 誤検知が続く場合は Task B の E2E floor を advisory (非 gate) モードに降格

---

## Completion Criteria

| Task | Done when |
|------|-----------|
| A | `/improve --dry-run` 出力に全提案の improvement_vectors が含まれる |
| B | ROBUST 判定が 3 条件の AND になり、未達条件がレポートに表示される |
| E | autoevolve/* commit の footer に JSON メタデータが含まれる |
| F | 模擬 plateau データで Phase 1/2 段階警告が正しく動作する |
| C | 模擬 history から _dashboard.md + sparkline が生成される |
| D | managed-agents-scheduling.md に pilot 手順が完結している |
