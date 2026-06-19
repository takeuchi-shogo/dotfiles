---
source: "https://github.com/anthropics/knowledge-work-plugins (Anthropic 公式)"
date: 2026-06-20
status: analyzed
adoption: 0
family: anthropic-knowledge-work-plugins (新規, N=1)
phase_2_5: skipped (domain mismatch, user 承認)
---

## Source Summary

**主張**: Claude を職能別の専門家エージェントに変えるには (1) ドメイン知識を組織のプレイブック・用語・ツール・リスク基準に合わせてコード化し、(2) スキル (自動) と明示コマンド (手動) を組み合わせて協業を設計し、(3) 外部ツールを MCP で統合して情報ループを閉じる。これらを Markdown + JSON + MCP の軽量 file-based 形式で実装し、各組織が自社ワークフローに合わせカスタマイズ可能に保つ。

**正体**: Anthropic 公式の **knowledge worker 向けロール別プラグイン市場**。Claude Cowork (Claude Code 互換) 向け。「Claude をあなたの職務の専門家に変える」もの = **非エンジニアの業務向け**で、開発者ハーネスとは対象が根本的に異なる。

**手法 (プラグイン横断)**:
- 16+ ドメインプラグイン: sales / customer-support / product-management / marketing / legal / finance / data / enterprise-search / bio-research / engineering / operations / design / human-resources / small-business / pdf-viewer / productivity + partner-built (apollo / brand-voice / slack / zoom / common-room)
- メタ層: cowork-plugin-management (create-cowork-plugin / cowork-plugin-customizer)
- プラグイン規約: `.claude-plugin/plugin.json` manifest + `skills/*/SKILL.md` (legacy `commands/` より優先) + `.mcp.json` + `${CLAUDE_PLUGIN_ROOT}`
- 2層メモリ (CLAUDE.md working + memory/ deep), Markdown タスク追跡, playbook-codified 判断基準, research-first ワークフロー, plain-English workflow router (smb-router), always-pause-before-action, `~~category` プレースホルダ + CONNECTORS.md (ツール非依存配布), progressive disclosure (SKILL.md <3000 words + references/)

**根拠**: Anthropic 公式リポジトリで Cowork 本体設計と統合。実運用の職務観察に基づきドメイン知識をコード化、MCP 標準で外部ツール相互運用性を確保。

**前提条件**: Claude Cowork / Claude Code ユーザーで**対応する職務を持つ人・チーム**向け。各プラグインは組織カスタマイズ前提 (デフォルトは汎用・US 法務基準)。Finance/Legal/Bio は資格者の最終確認が前提。

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | ドメインプラグイン 16+ (sales/legal/finance/HR/marketing/CS/PM/data/ops/design/bio/SMB/pdf) | N/A | Claude Code で営業/法務/財務業務をしない。職務ミスマッチ |
| 2 | `~~category` プレースホルダ + CONNECTORS.md (外部組織配布用ツール非依存化) | N/A | 公式 skill 自身が「外部配布時のみ使え、デフォルトでは使うな」と明記。プラグインを外部配布しない |
| 3 | 業務 SaaS MCP 統合 (HubSpot/Snowflake/Workday 等) | N/A | `docs/audit/connector-inventory.md` で MCP 管理済だが業務 SaaS は不要 |

## Already Strengthening Analysis (Pass 2: 強化チェック — 転用可能メタパターン)

Sonnet Explore で per-method 照合。転用可能な 8 メタパターン中 7 が Already (多くは dotfiles 先行)、1 が Partial だが別アプローチ。

| # | 既存の仕組み | 記事の手法 | dotfiles vs 公式 | 判定 |
|---|---|---|---|---|
| S1 | `marketplaces/*/marketplace.json` で plugin vendoring | `.claude-plugin/plugin.json` 規約 | dotfiles 先行 (meta-marketplace パターン) | 強化不要 |
| S2 | `skills/skill-creator/SKILL.md` (5フェーズ + full-package eval + blind comparison) | create-cowork-plugin (5フェーズ guided) | dotfiles の方が踏み込む | 強化不要 |
| S3 | `references/cc-7-layer-memory-model.md` + `memory-schema.md` | 2層メモリ (CLAUDE.md + memory/) | dotfiles が 7層に拡張 + verification_status | 強化不要 |
| S4 | `references/design-skill-routing.md` + `cwd-routing-matrix.md` | smb-router (NL→skill) | 手作業グリッド。規模的に十分 | 強化不要 |
| S5 | `careful` skill + `completion-gate.py` + `agency-safety-framework.md` | always-pause-before-action | dotfiles が多層防御で production 運用中 | 強化不要 |
| S6 | `developer-onboarding` skill + `/onboarding` | `start` onboarding skill | 同等 | 強化不要 |
| S7 | `CLAUDE.md` (130行) + `references/` (40+) + `docs/adr/` | thin-thick / progressive disclosure | 同等以上 | 強化不要 |
| S8 | `docs/audit/connector-inventory.md` (MCP drift + fallback catalog) | `~~placeholder` + CONNECTORS.md | 別アプローチ (lock-in 把握 + fallback 確保 vs 配布用抽象化) | partial / N/A (配布しない) |

## Integration Decisions

**採用 = 0。** これは「ハーネス工学の知見記事」ではなく「他職種向けドメインプラグインの市場」。職務ミスマッチでドメインプラグインは全 N/A、転用可能なメタ層は全て dotfiles に存在し多くは公式規約より先行。`~~placeholder` 配布パターンは公式自身が「外部配布時のみ」と限定する N/A。

Phase 2.5 (Codex+Gemini refine) は domain mismatch で採用 0 がほぼ確定のため user 承認のもと省略。

## Validation-only Follow-up

採用 0 だが、このリポジトリは公式規約との整合性を validate した:

| 対象 | 公式規約 | dotfiles の状態 | 結論 |
|------|---------|----------------|------|
| プラグイン構成 | `.claude-plugin/plugin.json` + `skills/*/SKILL.md` (legacy `commands/` 非推奨) | marketplace.json で vendoring、skill-creator は SKILL.md ベース | **整合 (drift なし)**。dotfiles の `commands/` (slash command) は公式も「still works」と認める有効パターン |
| SKILL.md 規約 | 三人称 description + trigger phrases、命令形 body、<3000 words、progressive disclosure | skill-writing-principles.md で同等以上に codify 済 | **整合・先行** |
| メモリ | 2層 (CLAUDE.md + memory/) | 7層 + verification_status | **先行** |
| dual-audience | "Nontechnical output — frame in terms of what plugin does, not file paths" | `dual-audience-cli-guide.md` | **整合** |

→ actionable な drift は無し。dotfiles のメタパターンは Anthropic 公式 Cowork 規約と整合 (むしろ先行) していることが確認できた。

## Family-level 教訓 (次回の role-plugin 記事用)

- **family: anthropic-knowledge-work-plugins (新規, N=1)**。ロール別ドメインプラグイン (営業/法務/財務/HR 等) を Cowork 向けに提供する市場。
- 開発者ハーネス (dotfiles) にとっては**構造的に職務ミスマッチ** — ドメインプラグインは N/A、転用可能なメタ層 (プラグイン規約/スキル作成/メモリ/ルーティング/確認ゲート/onboarding/thin-thick) は既に dotfiles 実装済で多くは公式先行。
- 次回同 family (別のロールプラグイン記事 / Cowork プラグイン集) が来たら Phase 1 で「ドメインプラグイン市場 = メタ層のみ照合、ドメインは N/A」と即判定して短絡可能。
- 副次的価値: ① dotfiles メタパターンが公式規約と整合・先行している validation ② 将来ロール別プラグインが要れば installable な公式ソース。

## Plan

なし (採用 0)。
