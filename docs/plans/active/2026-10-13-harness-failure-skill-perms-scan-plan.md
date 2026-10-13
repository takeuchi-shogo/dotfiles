---
success_criteria:
  - "failure→skill 手順が skill-audit または harness-contract に文書化され、no evidence/no merge が明示"
  - "deny-rules-catalog + permission-audit が agent-dedicated / least-privilege 前提のチェックを持つ"
  - "run-security-scan.sh と /security-scan が FP/dedup + 半自動再現ステージを持つ"
  - "関連 pytest / validate-configs が通る"
---

# Harness: failure→skill / perms / security scan

## Goal
dotfiles agent harness に 3 点を追加する（1 PR、マージしない）。

## Success Criteria
- 上記 success_criteria を満たす
- ソースから読めない内容は発明せず PR に caveat を書く

## Scope
触る:
- `.config/claude/skills/skill-audit/` または `docs/agent-harness-contract.md`
- `.config/claude/references/deny-rules-catalog.md`
- `scripts/lifecycle/permission-audit.py` (+ tests)
- `scripts/runtime/nightly/run-security-scan.sh`
- `.config/claude/commands/security-scan.md`
- `.config/claude/scripts/policy/agentshield-filter.py` (+ tests)

触らない:
- cccc gate / PR #274 周辺（master に既マージ）
- settings.json の deny 件数変更（catalog 件数 drift を起こさない）

## Constraints
- ソース未読内容を捏造しない
- DENY/ALLOW/ASK ヘッダ件数は settings.json と一致維持
- 日本語 PR 説明、do not merge

## Decision Log
- failure→skill: skill-audit に手順 + harness-contract に merge 基準（「No proof, no merge」）
- 12 rules: 画像から OCR/vision で読めた範囲のみ採用（02/10/11 中心）。残りも読めたが本 PR の必須は 02 と 10
- perms: Speaker Deck の「既定=ユーザー権限」「できること/届く範囲/鍵」「代理実行優先」を audit チェックに落とす
- security-scan: Cybozu Logos 概要の 5 段階を既存 AgentShield パイプラインに段階ラベル + dedup + 再現チェックとして追加

## Sources (read)
- https://x.com/distortgeekin/status/2109637916922159360 (+ image)
- https://x.com/dkfj/status/2109473604069195827
- https://speakerdeck.com/nrinetcom/seisei-ai-jidai-no-to-pa-misshon-sekkei
- https://blog.cybozu.io/entry/logos-overview
- https://blog.cybozu.io/entry/logos-harness-horos
- https://x.com/_stakaya/status/2109430957992550497
