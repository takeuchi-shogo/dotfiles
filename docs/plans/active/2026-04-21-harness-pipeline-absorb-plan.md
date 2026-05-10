---
source: "Article: How I got banned from GitHub due to my harness pipeline (2026-04)"
analysis: "docs/research/2026-04-21-harness-pipeline-absorb-analysis.md"
date: 2026-04-21
status: active
size: L
success_criteria:
  - "fix-issue skill に Reproduce-first step が追加され、`## Reproduce First` セクションが Workflow の 4 番目 (修正計画の前) に挿入される"
  - "`docs/plans/active/*.md` の `success_criteria:` 形式を記載する schema reference が作成され、PLANS.md からリンクされる"
  - "checkpoint → docs/plans/active → completion-gate の wiring が `references/resume-anchor-contract.md` として明文化される"
  - "Plan→Implement 境界で /grill-interview を示唆する advisory hook (`.config/claude/scripts/policy/plan-implement-bridge.py`) が追加され、PostToolUse で PLANS.md 変更検知時のみ発火する"
  - "model-routing.md に「End-to-End Completion > Per-Call Efficiency」design principle 節が追加される"
  - "references/memory-schema.md に session-independent durable state の運用ガイダンス (MCP state vs session memory の境界) が追記される"
  - "references/high-risk-change-patterns.md に「load-bearing judgment」節が追加される (interactive hook は作らず instruction 方式)"
  - "task validate-configs と task validate-symlinks が pass する"
---

# Harness Pipeline Article absorb 統合プラン

## Goal

記事「How I got banned from GitHub」から、solo dotfiles 文脈に翻訳できる 7 項目を取り込む。

**記事の本質を翻訳した核心:**
「attestation is scarce」→「reproduce-first attestation before polish」
(Codex + Gemini 双方が最優先と判定)

**棄却した項目:**
- 13-stage pipeline 全体コピー / 大量 OSS PR 自動化（context 不一致 + 2026 legal shift）
- git-push velocity soft-warning hook（premise mismatch; file-proliferation-guard で十分）
- CLA-style signoff flow（OSS 特有、solo dotfiles に不要）
- expert amplification 明文化（Stanford HAI 2026 データが逆結果を示すため保留）

## Scope

### 触るファイル（7 タスク、9 ファイル）

#### Task A (最優先): fix-issue に reproduce-first step
- `.config/claude/skills/fix-issue/SKILL.md` — Workflow に `## 4. Reproduce First` 節を挿入

#### Task B: resume anchor 統一
- `.config/claude/references/resume-anchor-contract.md` — 新規作成。success_criteria schema + checkpoint/plans/completion-gate wiring
- `PLANS.md` — Required Sections に reference link を追加
- `.config/claude/skills/checkpoint/SKILL.md` — resume anchor 言及に link 追加

#### Task C: Plan→Implement 境界で interview auto-suggest
- `.config/claude/scripts/policy/plan-implement-bridge.py` — 新規作成。PostToolUse hook
- `.config/claude/settings.json` — hook 登録

#### Task D + #12: model-routing.md 更新（2 タスク統合）
- `.config/claude/references/model-routing.md` — 「End-to-End Completion Principle」節を追加

#### Task #2: MCP session-independent state 明文化
- `.config/claude/references/memory-schema.md` — session-independent durable state の運用ガイダンス追記

#### Task #8: Load-bearing judgment
- `.config/claude/references/high-risk-change-patterns.md` — 「Load-bearing judgment」節を追記（interactive hook は作らず、instruction で対応）

### 触らないファイル

- 既存 hook スクリプト（動作変更なし、新規 advisory hook は Task C の 1 つのみ）
- `dotfiles/CLAUDE.md` — 既存 core_principles は温存
- `docs/plans/active/` 配下の既存 plan（success_criteria 未記載でも validation 失敗にしない）

## Constraints

### 壊してはいけない挙動

- 既存 hook 全て動作無変更（Task C の新規 advisory hook のみ追加、block はしない）
- 既存 Plan ファイル群の success_criteria 未記載を soft warning に留める
- completion-gate.py の現在の挙動は維持（wiring 明文化のみ）

### 互換性・承認条件

- **Reproduce-first step (Task A)**: instruction で表現。hook 化はしない（Karpathy ADR-0006 に従い「判断を要するゲート」は instruction 方式）
- **Load-bearing judgment (Task #8)**: 同じく instruction 方式。interactive hook は approval fatigue リスクのため棄却
- **resume anchor contract (Task B)**: documentation only。既存 plan に対する retroactive 強制なし
- **plan-implement-bridge hook (Task C)**: advisory のみ、exit 0 で block しない

### 2026 platform context への対応

- GitHub BAN リスクは本計画の範囲外（solo dotfiles は外部 push 少頻度）
- ただし Task A の reproduce-first は、将来 OSS 貢献する際のクオリティゲートとしても機能

## Stages

### Stage 1: 最優先タスク（Task A + D + #12）【S 規模 3 タスク】

**Task A — fix-issue reproduce-first**:
1. `skills/fix-issue/SKILL.md` の Workflow セクションを編集
2. 現在の `### 3. ブランチ作成` と `### 4. 修正計画` の間に `### 4. Reproduce First` を挿入
3. 既存ステップの番号を繰り下げ
4. Important 節に「再現できなければ修正しない（stop, re-scope）」を追加

**Task D + #12 — model-routing.md end-to-end principle**:
1. 既存 model-routing.md を読む
2. 「Design Principles」相当の節に「End-to-End Completion > Per-Call Efficiency」パラグラフを追加
3. 根拠として「失敗した pipeline を短く完走させる > 全 stage を最適化して途中で止まる」を明記

**Verify**: `task validate-configs` pass

### Stage 2: resume anchor (Task B)【M 規模】

1. `references/resume-anchor-contract.md` 新規作成
   - success_criteria schema（frontmatter field, 1 行 string array）
   - checkpoint → plans → completion-gate の依存関係図
   - HANDOFF.md との関係
2. `PLANS.md` Required Sections に「[resume anchor contract](/.config/claude/references/resume-anchor-contract.md)」へのリンク追加
3. `skills/checkpoint/SKILL.md` の該当箇所に link 追加

**Verify**: 既存 plan ファイル（4 個）が success_criteria 記載済みであることを確認（grep）

### Stage 3: Plan→Implement bridge hook (Task C)【M 規模】

1. `scripts/policy/plan-implement-bridge.py` 新規作成
   - PostToolUse(Edit|Write) で PLANS.md / docs/plans/active/*.md 変更を検知
   - 変更内容が Success Criteria 節の追加/変更なら、`/grill-interview` 実行を advisory 提案
   - exit 0 で block しない
2. `settings.json` の hooks に追加
3. `task validate-configs` pass

**Verify**: sample として PLANS.md に dummy edit → hook が advisory message を出すこと

### Stage 4: 参照ドキュメント追記（Task #2 + #8）【S 規模 2 タスク】

**Task #2 — memory-schema session-independent guidance**:
1. 既存 memory-schema.md を読む
2. 「Session-Independent Durable State」節を追加
   - session memory（揮発）vs MCP state（永続）の境界
   - どんな state を MCP に逃がすべきか判断基準

**Task #8 — high-risk-change-patterns load-bearing**:
1. 既存 high-risk-change-patterns.md を読む
2. 「Load-Bearing Judgment」節を追加
   - どんなコード/構造が load-bearing か（判断基準）
   - 触る前に user に確認する条件
   - instruction のみ（hook 化はしない）

**Verify**: `task validate-configs` pass

### Stage 5: Codex Review Gate

- 7 タスク全体を codex-plan-reviewer + codex-reviewer で並列レビュー
- Karpathy ADR-0006 の hook philosophy に沿っているか確認（新規 hook は Task C の 1 つのみ）

## Rollback

各 Stage ごとに独立コミットにする。任意の Stage を revert 可能。

- Stage 1: `git revert <sha>` で fix-issue / model-routing を元に戻す
- Stage 2: resume-anchor-contract.md を削除、PLANS.md link を除去
- Stage 3: plan-implement-bridge.py 削除、settings.json から hook 削除
- Stage 4: memory-schema / high-risk-change-patterns の追記節のみ削除

## Out of Scope

- 13-stage pipeline の workflow 化 → 将来別 plan で検討
- GitHub Issue body を source-of-truth にする feature-tracker 拡張 → 需要が出たら別 plan
- expert amplification 明文化 → Stanford HAI 2026 データを精査した上で別 plan
- velocity soft-warning hook → file-proliferation-guard で既に十分

## References

- Analysis: `docs/research/2026-04-21-harness-pipeline-absorb-analysis.md`
- Precedent: `docs/plans/active/2026-04-20-karpathy-absorb-plan.md` (同様の philosophical absorb パターン)
- ADR: `docs/adr/0006-hook-philosophy.md` (新規 hook は advisory に留める哲学)
