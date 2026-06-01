---
name: agents-best-practices-absorb-analysis
description: DenisSergeevitch/agents-best-practices (provider-neutral Agent Skill) の /absorb light-phase2 分析。harness-engineering family 飽和につき手法採用 0、reference pointer のみ記録。
type: absorb-analysis
date: 2026-06-02
status: light-phase2-only
family: harness-engineering
adopt_count: 0
decision: reference-pointer-only
source: https://github.com/DenisSergeevitch/agents-best-practices
---

# /absorb 分析: agents-best-practices (provider-neutral Agent Skill)

## Source Summary

- **対象**: `DenisSergeevitch/agents-best-practices` (GitHub, MIT, ⭐1,486 / fork 124, 6 commits)
- **正体**: 実行コードゼロの **単一 Agent Skill** (`SKILL.md` + 16 reference markdown、`file_policy: markdown-only`)。Codex / Claude Code / その他 Agent-Skill ランタイムで動作
- **主張**: 「エージェントハーネス = モデルを囲む control plane。モデルは提案、ハーネスが検証・認可・実行・記録・観測を返す」。コーディングは1ドメインに過ぎず、research/finance/legal/support/ops/sales/healthcare/業務自動化に同じランタイム規律を適用する
- **手法 (8 非交渉原則)**: ①harness acts not model ②全 tool call に result 必須 (denial/timeout/abort も観測) ③risk-class で permission path を変える ④draft/commit 分離 ⑤context は built not dumped + 信頼境界ラベル ⑥long-running は budget (step/time/token/cost/tool-call) ⑦skill/connector は progressive disclosure ⑧repeated failure → harness feature (validator/tool/doc/eval/policy)
- **インストール**: `npx skills add DenisSergeevitch/agents-best-practices -g` または `~/.claude/skills/` へ git clone
- **取得経路**: gh API (git tree + contents base64 decode で full markdown 取得、引用 faithfulness 確保)

## Saturation Gate (Phase 1.5)

- **family**: `harness-engineering` (キーワード hit: harness / scaffold / control plane で 3+)
- **N**: ≥5 (AlphaSignal Harness / Harness Pipeline BAN / Cursor harness / Self-Healing / Harness Blueprint / Tan thin-harness。Cursor absorb 時点で「harness-engineering 5本目」と記録)
- **採用率トレンド**: 全体 ~30% で PASS(warning) だが **直近2件連続 reject** (Cursor harness=採用0 / Hermes=採用0) → Step 4.5 連続 reject trend 副ガード発火
- **delta**: borderline (≈1)。8原則本体は dotfiles に深く実装済み (MEMORY.md に "Humans steer, agents execute" がそのまま存在)。唯一の novel 角度は「provider-neutral × 非コーディング多ドメイン × installable SKILL.md という成果物の形」
- **user choice**: light-phase2 (novel 3点のみ Phase 2 検証、Phase 2.5 省略)

## Phase 2 Judgment (light, novel 3点)

| # | novel 論点 | 判定 | 根拠 |
|---|---|---|---|
| 1 | provider-neutral × 非コーディング多ドメイン MVP-blueprint | **Partial (Gap寄り)** | `docs/agent-harness-contract.md` は **Claude Code 専用**。OpenAI/Anthropic/互換API 横断 framing と research/finance/legal 等の非コーディングドメイン向け MVP agent blueprint 生成は dotfiles 不在。記事 `mvp-agent-blueprint.md`(535行)+ 出力テンプレートが空白を埋める |
| 2 | coverage-audit (トピック網羅マトリクス自己検証) | **Already (強化不要)** | `/skill-audit` の 5D スキャン(Safety/Completeness/Executability/Maintainability/Cost) + description 衝突検出 + Usage Tier、+ `references/decision-tables-index.md` 索引でカバー。記事 coverage-audit.md の topic→file→gap マトリクスに新規 artifact 不要 |
| 3 | external skill installable 管理 | **Already (強化不要)** | `skills-lock.json` v2 で provenance(commit_sha/tree_sha/computedHash) + `origin: external/forked` 分類が実装済み。`npx skills add` 配布フレームは既存 skills.sh 運用範疇で、記事の手法ではない |

**8原則本体**: 全て Already (governance-levels / context-constitution / core principle "失敗→capability gap→durable artifact" / progressive disclosure / budget 機構)。飽和分野の予想通り。

## Decisions

- **adopt: 0 件** — 手法はすべて Already、#1 のみ Partial だが「手法コピー」ではなく「この skill 自体が空白を埋める成果物」性質
- **user choice: reference pointer のみ** — インストールせず MEMORY.md「外部参照 (未 absorb)」に1行記録。Pruning-First 遵守 (90% 既実装のスキルを 66→67 個目に追加して router noise を増やさない)
- **install を見送った理由**: dotfiles harness は意図的に Claude-specific。provider-neutral スキルは既存 harness 知識と ~90% overlap し description 衝突・ルーター劣化リスク (MEMORY.md の Skill bloat 懸念)。非コーディング/多プロバイダ設計は routine でなく occasional → reference tier が適切

## 取り出すべきタイミング (reference pointer の使い道)

以下のとき本リポジトリ (or `npx skills add`) を参照する:
- `/init-project --team` で**チーム/他者向け**エージェントハーネスを設計するとき
- **非コーディングドメイン** (support/finance/ops 等) のエージェント MVP を設計するとき
- **OpenAI/互換API** を含む multi-provider ハーネスを設計するとき (dotfiles の Codex/Gemini は委譲 subtool 扱いで、横断設計 framing は持たない)

## メタ学習

- harness-engineering family は dotfiles で最飽和。「provider-neutral な harness ベストプラクティス集」は構造的に採用率が低い (中核原則が既に core_principles + references に codify 済み)
- ただし「成果物の形が違う」記事 (installable skill / 多ドメイン適用) は、手法 delta が低くても **dotfiles 固有の境界 (Claude-specific / coding-focused) を可視化する** 価値がある。今回 #1 で agent-harness-contract.md が Claude 専用であることが明示的に確認された (drift ではなく意図的境界)
