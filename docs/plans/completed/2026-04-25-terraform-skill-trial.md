# terraform-skill@antonbabenko-terraform Trial

Status: rolled-back (2026-09-06)
Enabled: 2026-04-25
Evaluate-by: 2026-05-25 (30 days)
Outcome: invocations = 0 のまま評価期限を超過 (`docs/research/2026-05-09-skill-inventory-vs-usage.md:117`
で usage=0 / age=15d を記録)。下の Rollback Conditions 1 番目に該当したため
`settings.json` の `enabledPlugins` と `extraKnownMarketplaces` から削除した。
Plugin: `terraform-skill@antonbabenko-terraform`
Source: `github.com/antonbabenko/terraform-skill`

## Rationale

Terraform/OpenTofu 作業（モジュール review、CI 設定、state 操作）で静的検証・failure-mode 診断を行うため。既存の汎用レビューアーでは IaC 特有の identity churn / blast radius / state corruption を拾いきれない。

## Evaluation Criteria

- **Useful invocations/month**: ≥ 3
- **False positive rate**: < 30%
- **Instruction budget cost**: システムプロンプト追加 ≤ 200 tokens

## Rollback Conditions

次のいずれかで disable → `settings.json` の `enabledPlugins` から削除し、`extraKnownMarketplaces.antonbabenko-terraform` も削除:

- 2026-05-25 時点で invocations = 0
- Upstream repo がアーカイブ・削除される
- plugin が意図しないコマンド実行・ネットワーク通信を行う

## References

- Review: NEEDS_FIX → PASS（marketplace キー `antonbabenko` → `antonbabenko-terraform` にリネーム、trial plan 文書化）
- Harness Stability policy: `references/harness-stability.md`
