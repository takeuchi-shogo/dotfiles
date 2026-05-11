---
status: active
last_reviewed: 2026-04-23
---

# Team Harness Template (dotfiles 同梱) 実装プラン

- **Date**: 2026-04-23
- **Scope**: L (6-10 ファイル, templates 新設 + skill 拡張)
- **Origin**: `/absorb` of `anothervibecoder-s/claudecode-harness` → N/A 判定した team 固有パターンを dotfiles に同梱する提案
- **Related Research**: `docs/research/2026-04-23-team-harness-template-analysis.md` (Phase 5 で作成予定)

## Goal

個人 dotfiles harness の蓄積を「team 開発時に使えるプロジェクト立ち上げキット」として同梱し、既存 team project (本業 Next.js+Go+Connect+GCP/AWS / 副業 Next.js+tRPC+Hasura+AWS) の CLAUDE.md 未整備を解消する経路を作る。

### 非目標 (Non-Goals)

- dotfiles 個人 harness の team 転用 (例: scripts/policy/ の hook を team repo にインストール) — やらない
- Claude Code 非採用 team 用テンプレ作成 — 対象外
- 全 tech stack 網羅 — 本業/副業の 2 variant のみ。他案件は base + 手動カスタマイズで吸収

## Success Criteria

- [ ] `templates/team-project/base/` から新規 team project に `cp -R` で即座にセットアップ開始できる (7 ファイル揃う)
- [ ] `variants/nextjs-go-connect-gcpaws/` と `variants/nextjs-trpc-hasura-aws/` が base に concrete example を追加し、facts.md / ADR / OWNERSHIP に「書き始めの痛み」を下げる現実的な例を提供している
- [ ] `references/team-harness-patterns.md` が個人 harness の仕組み (scripts/policy/completion-gate.py 等) と team 仕組み (CODEOWNERS + branch protection 等) の翻訳マップを提示している
- [ ] `/init-project --team` で templates/team-project/base/ を current repo に展開できる
- [ ] `/init-project --team --apply-to <existing-dir>` で既存 project を Read → gap 判定 → diff 提示 → 承認後書き込みのフローが記述されている (実装は skill ドキュメント + 既存 factory agent 委譲で十分、新 script は書かない)
- [ ] MEMORY.md に 1 行ポインタがあり、将来 /absorb や /init-project から参照される

## Validation

- `task validate-configs` が pass (harness contract 遵守)
- `task validate-symlinks` が pass
- 手動: 仮 project に `cp -R templates/team-project/base/ /tmp/fake-team/` して placeholder 置換がしやすい形式か確認
- 手動: `--apply-to` フローの指示を読んで、既存 team repo (本業 repo の CLAUDE.md 空の状態を想定) に適用できるか思考実験で通す

## Decision Log

| # | Decision | Rationale | Alternative rejected |
|---|----------|-----------|--------------------|
| D1 | **template は 1 本でなく base + variants** | 案件ごとスタックが変わる (Next.js+Go vs Next.js+tRPC+Hasura) | 1 本に汎用化 → placeholder 過多で書き始めの痛みが大きい |
| D2 | **2-sign-off は hook でなく CODEOWNERS + branch protection** | dotfiles の Python hook は team repo に持ち込めない。GitHub native 機構が永続的 | team repo に hook コピー → 維持コスト + 権限問題 |
| D3 | **`--apply-to` は新 script を書かず skill + factory agent 委譲** | Build to Delete 原則、機能の大半は既存 /init-project + document-factory agent に展開可能 | 専用 script 新設 → dead weight リスク |
| D4 | **プロトタイプ先行 (ユーザー選択)** | 年 1 回程度の使用頻度。磨き上げは実運用フィードバックを受けてから | 先に完璧な spec + Codex Plan Gate → 使われない可能性あるものに過剰投資 |
| D5 | **Codex Plan Gate は実装後の Review Gate として実施** | プロトタイプ先行だが L 規模 + harness 変更のため、実装後に必ず codex-reviewer + code-reviewer 並列 | skip → CLAUDE.md の L ワークフロー違反 |

## Tasks

1. **templates/team-project/base/CLAUDE.md.tpl** — team CLAUDE.md テンプレ (S)
2. **base 支援ファイル 6 本** (docs/facts.md.tpl, docs/zones/OWNERSHIP.md.tpl, docs/decisions/0000-template.md, docs/security/auth-payment-policy.md.tpl, .github/CODEOWNERS.tpl, README.md) (M)
3. **variants/nextjs-go-connect-gcpaws/** — 本業向け差分 (S)
4. **variants/nextjs-trpc-hasura-aws/** — 副業向け差分 (S)
5. **templates/team-project/APPLY.md + references/team-harness-patterns.md** — 適用手順と知識ベース (M)
6. **init-project skill 拡張** — SKILL.md に --team / --apply-to セクション + references/team-templates.md (M)
7. **MEMORY.md ポインタ追記** (S)
8. **docs/research/2026-04-23-team-harness-template-analysis.md** — 分析レポート (Phase 5 で Sonnet に委譲) (S)
9. **Codex Review Gate** — 実装完了後に codex-reviewer + code-reviewer 並列 (M)

## Reversible Decision — Rollback 条件

- 実装後 6 ヶ月 (2026-10-23) 時点で 1 度も使われていなければ `templates/team-project/` と `references/team-harness-patterns.md` を削除候補に (`references/harness-stability.md` の 30 日ルールより長めに設定、team 立ち上げが年 1 回想定のため)
- 使われた場合は variants を追加する方向に拡張

## Out of Scope (将来検討)

- Hasura / tRPC v11 / Connect RPC 等のバージョン更新に追随するメンテナンス運用
- 他スタック variant (Ruby on Rails, Python FastAPI, Rust Axum 等)
- team repo 向けの継続的な CLAUDE.md 改善ループ (個人 AutoEvolve の team 版)
