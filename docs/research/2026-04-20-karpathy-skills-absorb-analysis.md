---
source: "https://github.com/forrestchang/andrej-karpathy-skills/tree/main"
date: 2026-04-20
status: analyzed
---

# Karpathy Skills (andrej-karpathy-skills) absorb 分析

## Source Summary

**主張**: Andrej Karpathy が X post で挙げた LLM コーディングの 4 典型 failure パターン
(思い込み実装 / 過剰実装 / スコープ外編集 / 検証なし完了宣言) に対し、
instruction ベースの soft nudge のみで対抗する軽量スキル集。
"Hard enforcement (hooks / lint) は避け、LLM は success criteria を与えて looping
させれば exceptionally good" が根底哲学。

**手法**:

- 単一 skill `karpathy-guidelines` として 4 原則を束ねて配布
- Cursor 向け `.mdc` と Claude Code 向け `SKILL.md` の 2 系統配布
- 原則は振る舞い指針 (how to think) に留め、機械的 enforcement を置かない

**4 原則の要旨**:

1. **Think Before Coding** — 仮定の明示化、曖昧で停止、複数解釈があれば提示、反対意見を出す
2. **Simplicity First** — YAGNI 徹底。単一用途の抽象化 NG。200 行書いたら 50 行に書き直す
3. **Surgical Changes** — scope 外編集禁止、既存スタイル match、自分が作った orphan だけ削除
4. **Goal-Driven Execution** — "add X" を "write test → make pass → verify" に変換、
   強い success criteria が独立 loop を可能にする

**根拠**: Karpathy の経験則 + LLM の failure mode 観察 (論文ではなく実践知)

**前提条件**: 開発者が "senior engineer review" 観点でコードを評価できる。
Hard enforcement は儀式化 (performative compliance) を招くため採用しない。

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Think Before Coding (仮定明示/停止/複数解釈) | Already | `CLAUDE.md:7-16`, `overconfidence-prevention.md`, `EXAMPLE.md`, `/epd` Deep Interview |
| 2 | Simplicity First (YAGNI/抽象化抑制) | Already | `CLAUDE.md:18-28`, `code-quality.md:129-149`, `/simplify` skill |
| 3 | Surgical Changes (scope 外編集禁止/orphan) | Already | `CLAUDE.md:30-46`, `code-quality.md:104-115`, `change-surface-advisor.py` |
| 4 | Goal-Driven Execution (test→pass→verify 変換) | Already | `CLAUDE.md:48-66`, `trust-verification-policy.md`, `workflow-guide.md` Act→Verify→Summarize |
| 5 | "Hard enforcement NG" 方針表明 | Gap | 既存 harness が hook を多用しており、哲学的立場が未成文化 |
| 6 | 単一 skill `karpathy-guidelines` としての配布 | N/A | 同内容が `dotfiles/CLAUDE.md` に既に埋まっており重複不要 |

**Pass 1 サマリ**: 4 原則本体は既存セットアップに概ね反映済み。Karpathy スキルの
独自価値は「束ね方」と「enforcement を意図的に避ける哲学」にある。

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | 原則 1 (Think Before Coding) 実装度 75/100 | instruction で書かれているが、多モデル配布 (Codex/Cursor) していない | Codex/Cursor の AGENTS に 4 原則ポインタを追加 | 強化可能 |
| S2 | 原則 2 (Simplicity) 実装度 70/100 | /simplify skill はあるが、「200→50 行」のようなラジカルな書き直し基準は未成文 | /simplify への明示リンクで補強 (本 absorb では触らない) | 強化不要 |
| S3 | 原則 3 (Surgical) 実装度 72/100 | `change-surface-advisor.py` advisory 止まり。哲学的立場 (= block しない) が未明文化 | ADR で方針を成文化 | 強化可能 |
| S4 | 原則 4 (Goal-Driven) 実装度 85/100 | `success_criteria` を完了ゲート `completion-gate.py:330-343` が読むが、Plan の Required Sections に無い | PLANS.md Required に Success Criteria 追加 | 強化可能 |
| S5 | Hook 設計哲学の暗黙性 | 既存 hook 群の採用根拠が CLAUDE.md 各所に散在 | ADR 0006 (Hook Philosophy) で 3 分類を成文化 | 強化可能 |

全体実装度: **78/100**。文書・skill・rules は厚い。Hook 層は薄いが、
これは Karpathy 哲学上正しい。伸びしろは「配布 contract」と「Plan ↔ hook 接続」。

## Phase 2.5: Codex 批評による修正

Codex の独立レビューで判明した**過小評価していた gap**:

### 採用する指摘

1. **配布 contract の破損** — `CURSOR.md:6,14` が存在しない
   `.cursor/rules/karpathy-guidelines.mdc` と `skills/karpathy-guidelines/SKILL.md`
   を案内している。ユーザーが辿って 404 になる状態。
2. **PLANS.md ↔ completion-gate.py 未接続** — `completion-gate.py:330-343` が
   plan frontmatter の `success_criteria:` を読む実装だが、`PLANS.md:21-58` の
   Required Sections に `Success Criteria` がない。Karpathy 原則 4 を enforce
   すべき唯一の正統なゲートが fire しない状態。
3. **Codex/Cursor 側の実効移植性の見落とし** — Karpathy 4 原則は
   `dotfiles/CLAUDE.md` に commit されただけ。Codex (`.codex/AGENTS.md`)、
   Cursor (`.cursor/rules/global.mdc`)、root `AGENTS.md` には反映なし。
   マルチモデル運用をしているのに Claude のみ強化される非対称。
4. **哲学衝突の未整理** — `.config/claude/CLAUDE.md:25` の
   「static-checkable rules は mechanism に寄せる」と `:90` の
   「判断をゲート化する / 批評を成果物にする」が、Karpathy "Hard enforcement NG"
   と緊張関係にある。ADR で裁定が必要。

### 棄却する指摘 (Codex の過剰提案)

- **Pre-commit hook で仮定明示を regex enforce** — 哲学違反。儀式化を招く
- **scope 外変更の post-write hook** — semantic judgment を deterministic 化する
  無理筋。`change-surface-advisor.py` の advisory で十分
- **定量複雑度計測 (cyclomatic など)** — gaming + harness debt
- **Multi-model Verification Gate 全面導入** — 既存 Codex Review Gate (Layer 2)
  で十分
- **Plan 全タスク mandatory 化** — M/L soft section で十分、S には過剰

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1 | 4 原則本体の dotfiles/CLAUDE.md への追加 | 採用済み (事前) | 既に反映済みのため本 absorb では触らない |
| 2 | Hook 設計哲学 ADR (0006) | 採用 | 3 分類成文化で将来の hook 採否判断を安定化 |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| A | CURSOR.md 配布 contract 修正 + `.cursor/rules/global.mdc` に 4 原則反映 | 採用 | 壊れたリンクを塞ぎ、Cursor ユーザーにも原則を届ける |
| B | PLANS.md Required Sections に Success Criteria 追加 | 採用 | Karpathy 原則 4 ↔ `completion-gate.py` 接続を閉じる |
| C | Codex 側 (AGENTS.md, .codex/AGENTS.md) に 4 原則ポインタ追加 | 採用 | マルチモデル運用の非対称を解消 |
| D | Hook Philosophy ADR (docs/adr/0006-hook-philosophy.md) 新規作成 | 採用 | enforcement 哲学を成文化、既存 hook を後付けで 3 分類整理 |

## Plan

ユーザー選択: **全部** (A + B + C + D、合計規模 M, 5-6 ファイル変更)

統合プラン本体: `docs/plans/active/2026-04-20-karpathy-absorb-plan.md`

### Task A: CURSOR.md 配布 contract 修正

- **Files**: `CURSOR.md`, `.cursor/rules/global.mdc`
- **Changes**: 存在しない `.mdc` / `SKILL.md` への参照を削除し、`global.mdc` + `CLAUDE.md` に統合した 4 原則簡潔版を追記
- **Size**: S

### Task B: PLANS.md Success Criteria 追加

- **Files**: `PLANS.md`
- **Changes**: Required Sections に `## Success Criteria` を Goal 直後に挿入。Working Rules に frontmatter `success_criteria:` が `completion-gate.py` で消費されることを注記
- **Size**: S

### Task C: Codex/Cursor 配布

- **Files**: `AGENTS.md` (root), `.codex/AGENTS.md`
- **Changes**: Core Workflow に「Karpathy 4 原則は `CLAUDE.md` 参照」のポインタを追加 (本体複製は行わない = Surgical Changes)
- **Size**: M

### Task D: Hook Philosophy ADR

- **Files**: `docs/adr/0006-hook-philosophy.md` (新規), `docs/adr/README.md`
- **Changes**: 3 分類 (deterministic block / semantic advisory / human judgment) を定義。既存 hook 例: `protect-linter-config.py` (block) / `change-surface-advisor.py` (advisory) / Karpathy 4 原則 (human judgment)
- **Size**: S

## 根底哲学の所在整理

| 原則 | 配布先 | Enforcement 層 |
|------|--------|----------------|
| Think Before Coding | CLAUDE.md / overconfidence-prevention / EXAMPLE.md | human judgment (hook なし) |
| Simplicity First | CLAUDE.md / /simplify / code-quality.md | semantic advisory (/simplify) |
| Surgical Changes | CLAUDE.md / code-quality.md / change-surface-advisor.py | semantic advisory (advisor のみ、block なし) |
| Goal-Driven Execution | CLAUDE.md / trust-verification-policy / workflow-guide | deterministic block (completion-gate.py + success_criteria) |

Karpathy 原則のうち **唯一 deterministic block に繋がるのが原則 4**。
これが Task B (PLANS.md Success Criteria 必須化) の理論的根拠。
