---
date: 2026-05-04
task: T1 — Skill 常時 description tax 半減 (107 skill Tier 分類)
status: draft
scope: ~/.claude/skills/*/SKILL.md frontmatter description, scripts/policy/measure-instruction-budget.py
references:
  - docs/research/2026-05-04-claude-code-overhead-9patterns-absorb-analysis.md
  - .claude/skills/skill-audit/SKILL.md (Step 0.5: Usage Tier Classification)
  - references/harness-stability.md (30 日評価ポリシー)
  - references/reversible-decisions.md (撤退条件)
---

# Skill Tier Pruning Spec

## Goal

107 個の skill の SKILL.md frontmatter `description` が常時システムプロンプトに展開され、
実測 **8,070 token (description のみ)** / 推定 12,283 token (frontmatter 全体) の常時 tax を発生させている。
本 spec は description tax を **8,070 → 4,000 token (半減)** とする運用ポリシーを定義する。

## Tier 定義

skill-audit Step 0.5 (Usage Tier Classification) と整合。`skill-executions.jsonl` の過去 30 日実行回数に基づく:

| Tier | 基準 (過去 30 日) | description 上限ガイド | アクション |
|------|------------------|---------------------|-----------|
| **Dominant** | 全実行の 40% 以上 | 250 char (≈ 60 token) | Expert Collapse 兆候、役割重複監査 |
| **Weekly** | 4 回以上 (Dominant 未満) | 250 char | 維持・優先改善対象 |
| **Monthly** | 1〜3 回 | 200 char (≈ 50 token) | 現状維持、改善は低優先 |
| **Unused** | 0 回 | 100 char (≈ 25 token) | 30 日評価後に description 短縮 |

`skill-executions.jsonl` 不在時は Tier 分類をスキップし、5D Quality + description 長のみで判定する。

## 削減目標

| 指標 | 現状 (2026-05-04) | 目標 | 達成判定 |
|------|------------------|------|---------|
| skill_descriptions 累計 token | 8,070 | 4,000 | `measure-instruction-budget.py` 出力で確認 |
| 1 skill 平均 description char | 302 | 150 | 全件平均 |
| description ≥ 500 char の skill 数 | TBD (要 audit) | 0 | top-10 audit で削減 |

## 運用ポリシー

1. **計測の継続化**: `scripts/policy/measure-instruction-budget.py` が `skill_descriptions` カテゴリを毎回ログ
2. **削除しない**: harness-stability.md の 30 日評価ポリシーに従い、Unused tier も即削除しない
3. **段階的短縮**: Unused → Monthly → Weekly の順で description を上限ガイド以下に reduce
4. **月次レビュー**: `/skill-audit` で Tier レポート出力 (`docs/benchmarks/YYYY-MM-DD-audit.md`)
5. **新規追加スキルへの強制**: skill-creator で新規生成時は上限ガイドを Soft Limit として警告 (本 spec の範囲外、将来タスク)

## 撤退条件 (reversible-decisions.md 準拠)

以下のいずれかに該当した場合、本 spec を revert または再評価する:

- **誤発火率の悪化** *(観測手段が整い次第適用)*: 半減実施後にスキル誤発火率 (description で本来の skill が trigger しない) が **20% 以上悪化**。現時点では `skill-executions.jsonl` を baseline とした誤発火率測定ロジックは未実装。本撤退条件は測定基盤実装後に有効化する
- **観測不能化**: `skill-executions.jsonl` 統計が取得不能になる場合 → spec の Tier 分類部分を再評価
- **手動短縮の負荷**: 1 ヶ月で 5 skill 未満しか短縮できない場合 → 自動化検討 or spec 縮小

## 計測コマンド

```bash
python3 ~/.claude/scripts/policy/measure-instruction-budget.py
```

期待出力 (新カテゴリ追加後):

```
[instruction-budget] total=NNNN tokens, status={ok|warn}
  claude_md: ~1500 tokens
  mcp_descriptions: ~0 tokens
  hook_injected: ~NNN tokens
  skill_descriptions: ~8000 tokens (107 skills)   <-- 本 spec の対象
  references (advisory): ~NNNNN tokens (NN files)
  output: ~/.claude/logs/instruction-budget-YYYY-MM-DD.jsonl
```

## Out of Scope

- スキルの即時削除 (harness-stability 違反)
- description の即時短縮 (本 spec はポリシー化と計測のみ。実短縮作業は別タスク化)
- skill-executions.jsonl のスキーマ変更
- skill-creator 側の上限警告機構 (将来タスク)

## Verification

1. `measure-instruction-budget.py` の出力に `skill_descriptions` 行が含まれること
2. 本 spec の参照が `skill-audit/SKILL.md` Step 0.5 に追加されていること
3. 撤退条件に至る前に削減目標 (4,000 token) を 6 ヶ月以内に達成すること (継続観測)
