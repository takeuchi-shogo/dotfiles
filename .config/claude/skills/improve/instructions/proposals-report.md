# Proposals & Report (Phase 3 / Phase 5)

## Phase 3: 改善提案の生成

Phase 2 (Coverage Matrix + Codex Deep Analysis) の統合結果で **改善機会** が見つかったカテゴリに対して、
**Agent ツールで `autoevolve-core` (phase: improve) エージェントを起動** する。

各カテゴリに対して:

```
以下のカテゴリの改善を実施してください:

カテゴリ: {カテゴリ名}
Coverage Matrix 結果: {Phase 2a の該当カテゴリ}
Codex Deep Analysis: {Phase 2b の補強 findings}

improve-policy.md の方針に従い、autoevolve/* ブランチで変更を実装してください。

【必須】各提案に以下のフィールドを含めること（Rule 43）:
- serves_principles: どの core principle を推進するか
- tension_with: どの principle と緊張関係にあるか
- pre_mortem: この提案が失敗する場合の最も可能性が高い原因
- blast_radius: direct + indirect
- evidence_chain: data_points, confidence, specific_refs, reasoning, counter_evidence
- rollback_plan: 復旧手順
```

**注意**:
- 改善機会がないカテゴリは起動しない
- 複数カテゴリに改善機会がある場合は、優先度の高いものから順に起動する
- 1 サイクルで最大 3 ファイルの変更制約を守る
- 必須フィールドが欠落した提案は Phase 4 に進めない（Rule 43）

### 改善提案のテスト可能性

> AutoAgent (2026-04): タスクエージェントが自身のテスト/検証を自動生成し、品質を自己保証。

各提案に対して、以下のテスト戦略を含めること:
- **検証コマンド**: 改善が期待通り機能していることを確認する具体的なコマンドまたは手順
- **回帰テスト**: 改善によって既存機能が壊れていないことを確認する方法
- テスト不可能な提案（例: プロンプトの微調整）は、次回の `/improve` での before/after 比較を計画に含める

**提案生成後**: Phase 4 (Adversarial Gate) に進む。
`instructions/phase4-adversarial-gate.md` を Read して実行。

## Phase 5: レビューレポートの生成

Phase 4 (Adversarial Gate) の結果を統合し、以下のフォーマットでユーザーに報告する:

```markdown
# /improve レポート — YYYY-MM-DD

## TL;DR — Top Actions

> ROBUST 判定の提案のみ。3 件以下に絞る。

1. [ROBUST] {提案概要} — 根拠: {1文} / 効果: {1文}
2. ...

## 前回 /improve からの変化

- 前回提案の実施状況: N/M 完了
- 効果測定結果: ...

## Cycle Time 統計

> friction 検出→/improve 実行の elapsed time（observation→improvement パス）。

<!-- improve-history.jsonl の cycle_time_hours が null でないエントリ数で分岐 -->

**データ蓄積中** (N/3 件): 統計計算には最低 3 サイクルのデータが必要です。
- 今回の cycle time: {cycle_time_hours} 時間（{cycle_start} → {cycle_end}）

<!-- データ 3 件以上の場合 -->

| 指標 | 値 |
|------|---|
| 今回 | {cycle_time_hours} h |
| 平均 | {mean} h |
| 中央値 | {median} h |
| P90 | {p90} h |
| トレンド | {前回比: 改善/横ばい/悪化} |

> ボトルネック: {最も cycle time に寄与している要因の分析}

## Coverage Matrix 結果

| カテゴリ | Codex 品質判定 | ANSWERED | INSUFFICIENT | 主要 findings |
|---------|---------------|----------|-------------|--------------|
| errors | THOROUGH | 4/5 | 1/5 | ... |
| quality | ADEQUATE | 3/4 | 1/4 | ... |
| skills | THOROUGH | 4/4 | 0/4 | ... |
| agents | SHALLOW→ADEQUATE | 2/3 | 1/3 | ... |
| environment | NOT_APPLICABLE | - | - | データ要件未達 |

## 全提案一覧

| ID | 提案 | Serves | Tension | Codex Rating | Loop | Action |
|----|------|--------|---------|-------------|------|--------|
| 001 | ... | KISS | - | ROBUST | 1/1 | 推奨 |
| 002 | ... | DRY | YAGNI | VULNERABLE→ROBUST | 2/2 | 推奨(精錬済) |
| 003 | ... | - | KISS | FATAL_FLAW | 1/1 | 却下 |

## Adversarial Review 詳細

### IMP-001: {提案概要}
- **Codex 判定**: ROBUST
- **原則違反**: なし
- **考慮漏れ**: なし
- **証拠の弱さ**: 軽微（サンプルサイズに注意）
- **Pre-mortem**: 十分
- **代替案**: 検討済み、現提案が最適

### IMP-002: {提案概要}
- **Codex 判定**: VULNERABLE → ROBUST (精錬済)
- **初回指摘**: blast_radius に X の間接依存が含まれていない
- **精錬対応**: indirect に X を追加、影響分析を実施

### IMP-003: {提案概要}
- **Codex 判定**: FATAL_FLAW
- **理由**: KISS 原則に反する。既存の hook で対処可能

## Blind Spot Declaration

以下の領域は今回の分析でカバーできていません:
- {INSUFFICIENT_DATA だったカテゴリと理由}
- {Codex が指摘した missing_proposals}

## 知識ベースの健全性

- learnings サイズ: OK / 警告
- insights 数: N 件
- MEMORY.md: N 行 / 200行制限
- 昇格候補: N 件

## 次回への申し送り

- {Codex の missing_proposals}
- {INSUFFICIENT_DATA の解消に必要なデータ}
- {VULNERABLE のまま残った提案の追加検証事項}
```
