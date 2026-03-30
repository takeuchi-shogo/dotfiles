---
source: https://github.com/samber/cc-skills-golang
date: 2026-03-30
status: integrated
---

## Source Summary

**主張**: Go 開発の AI スキルは「原子的・遅延ロード・評価駆動」で設計すべき。35スキルで全体エラー率を 54% → 98% に改善（+44pp）。

**手法**:
- **Lazy-loaded atomic skills**: description (~100 tok) でトリガー判定、SKILL.md (~2.5K tok) をオンデマンドロード、reference/ で深掘り
- **Mode-based behavior**: coding / review / audit モードを1スキル内で切り替え
- **Overridable design**: 会社スキルが `supersedes samber/cc-skills-golang@golang-naming` と宣言して上書き
- **Ultrathink triggers**: security / debugging / benchmark で自動的に深い思考モードを起動
- **Eval-driven quality**: 各スキルを assertion ベースで測定し、error rate gap を公開（3141 assertions）

**根拠**: Claude Opus 4.6 で 12 evals × 2 configs = 24 subagents による自動評価。スキルなし 54% → スキルあり 98%。

**前提条件**: Claude Code またはAgent Skills 互換ツール。Go プロジェクト。スキルの description トークンが常時ロードされる（35スキルで ~3K tok）。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Go troubleshooting methodology (Golden Rules, pprof, Delve, GODEBUG) | Partial | golang-pro にバグパターン表あり。体系的デバッグ方法論なし |
| 2 | Go modernize checklist (バージョン別移行ガイド) | Gap | go-idioms-checklist に Go 1.21+ 言及あるが体系的移行チェックリストなし |
| 3 | Ultrathink auto-trigger (security/debug/benchmark) | Gap | エージェント定義に ultrathink 指定なし |
| 4 | Overridable skill mechanism | Gap | スキルにオーバーライド宣言なし |
| 5 | Eval-driven skill metrics | Gap | スキル効果の定量測定なし |
| 6 | Go project layout guide | Gap | Go 固有のプロジェクト構造ガイドなし |
| 7 | Go CI pipeline template | Gap | Go 固有の CI 設定ガイドなし |
| 8 | samber library skills (lo, oops, slog) | N/A | samber 個人ライブラリへの依存は不要 |
| 9 | Lazy-loaded atomic skill architecture | N/A | agent+reference 方式で統合済み。35スキル追加は description トークン増大のデメリット |

### Already 項目の強化分析

| # | 既存の仕組み | samber が示すポイント | 判定 |
|---|-------------|---------------------|------|
| A1 | golang-pro (エラー処理) | single handling rule 強調 | Already (強化不要) — go-idioms-checklist §6 でカバー |
| A2 | golang-reviewer (16 review points) | audit モード（並列サブエージェント） | Already (強化可能) — audit モード追加 |
| A3 | golang-pro (並行処理) | Worker Pool, Fan-out/Fan-in 詳細 | Already (強化不要) — go-idioms-checklist §7-8 で十分 |
| A4 | golang-pro (パフォーマンス) | pprof セットアップ手順 | Already (強化可能) — pprof 実行フロー追加 |
| A5 | review-checklists/go.md (GO-1〜17) | 各分野 20-30 項目 | Already (強化不要) — 深掘りは go-idioms-checklist が担当 |

## Integration Decisions

全項目取り込み:

1. **[Partial → 統合]** Go troubleshooting methodology → golang-pro に Golden Rules + Quick Decision Tree + Red Flags 追加、pprof/Delve は reference に分離
2. **[Gap → 統合]** Go modernize checklist → references/go-modernize-checklist.md 新設
3. **[Gap → 統合]** Ultrathink auto-trigger → golang-pro, golang-reviewer に追加
4. **[Gap → 統合]** Go project layout guide → references/go-project-layout.md 新設
5. **[Gap → 統合]** Go CI pipeline template → references/go-ci-pipeline.md 新設
6. **[Gap → 将来]** Eval-driven skill metrics → 大規模タスク、別途検討（/skill-audit スキルと連携）
7. **[強化]** golang-reviewer audit モード追加
8. **[強化]** golang-pro pprof 実行フロー追加（references/go-pprof-guide.md）

スキップ:
- Overridable skill mechanism — 現時点で会社スキルとの衝突がないため
- samber library skills — 個人ライブラリ依存は不要
- Lazy-loaded atomic architecture — 既存の agent+reference 方式を維持

## Plan

### Wave 1: Reference files（並列、依存なし）
- T3: references/go-modernize-checklist.md 新設 (S)
- T5: references/go-project-layout.md 新設 (S)
- T6: references/go-ci-pipeline.md 新設 (S)
- T8: references/go-pprof-guide.md 新設 (S)

### Wave 2: Agent updates（Wave 1 の reference 参照が必要）
- T2: golang-pro に troubleshooting methodology 追加 (M)
- T4: golang-pro, golang-reviewer に ultrathink trigger 追加 (S)
- T7: golang-reviewer に audit モード追加 (S)

### Wave 3: Metadata
- T9: MEMORY.md にポインタ追記 (S)
