---
title: "6 Workflows, 6 Lessons, 60 Days with Hermes Analyst (0xJeff) — absorb analysis"
date: 2026-06-02
source:
  title: "6 Workflows, 6 Lessons, 60 Days with Hermes Analyst"
  author: 0xJeff
  type: blog/newsletter (vendor — Hermes)
status: light-phase2-only
family: harness-engineering
saturation: SATURATED-borderline (N=12+, delta=1)
adopted: 1
related:
  - docs/superpowers/specs/2026-05-31-learned-promotion-loop-design.md
  - .config/claude/skills/promote-learnings/SKILL.md
  - docs/research/2026-05-31-hermes-eval-loop-absorb-analysis.md
  - docs/research/2026-04-14-hermes-personal-analyst-analysis.md
---

# Hermes 60 Days / 6 Lessons — absorb analysis (light-phase2)

## Source Summary

著者 0xJeff が personal investment/data analyst agent "Hermes" を 60 日運用した教訓。中核命題: **"building an agent is 90% architecture, 10% AI"** — 失敗はモデルの知能ではなくアーキテクチャ(ツール同士の競合)に起因する。6 lessons:

1. **Provider 1本化** — 5-6 provider を渡り歩いたが毎回 2-3 セッションのデバッグコスト。model matters less、1 provider に固定し direct API が得。
2. **tools/skills 優先** — skill が多すぎても少なすぎるより良い。Hermes は recurring workflow を検出して skill を自動生成。ユーザーの仕事は「正しいツールを指す」こと。
3. **memory persistence** — native memory (User/Memory/Soul.md) + external memory provider (Hindsight) の併用。reflect はコスト高、time-sensitive cron には recall。
4. **feedback loop (6-step)** — 出力→誤り指摘→具体修正→permanent rule に encode→次回 tighter→反復。**未解決問題: echo chamber / self-reinforcing loop**(出力が既存保有銘柄に gravitate)。
5. **x402** — agentic wallet で premium tool を従量課金アクセス(crypto)。
6. **skill bundling** — 巨大プロンプトを directory 化 (SKILL.md ~100行 + references/ + scripts/)。~500 token load で 5000+ token の再説明を節約。

## Phase 1.5 Saturation Gate

- Family: `harness-engineering` (中核命題が family thesis 同一)。N=12+、直近の同系 Hermes/harness content は reject 寄り (Cursor harness 採用0 / How To Fix AI Slop-Hermes 採用0 delta=0)。
- 手法 delta = 1 → **SATURATED-borderline** → ユーザー選択で **light-phase2**。

## Pass 1 / Pass 2 判定 (novel 論点のみ: echo-chamber guard)

| Lesson | 手法 | 判定 | 根拠 |
|---|---|---|---|
| 1 | Provider 1本化 | Already | `model-routing.md` / マルチモデル連携 |
| 2 | tools/skills 優先 + skill 自動生成 | Already | `promote-learnings` / `retrospective-codify` / skill-creator |
| 3 | native + external memory | Already | 7層メモリ / Obsidian bridge |
| 4 | 6-step feedback loop → permanent rule | Already (機構) | `feat/learned-promotion-loop` / learned 昇格ループ本体 |
| **4b** | **echo chamber / self-reinforcing loop** | **Gap** | 昇格ループは `importance` 降順 + 完全一致 dedup のみ。semantic に近い learned の反復昇格 / monoculture を抑制する仕組みなし。部品 (`contradiction-scanner.py` / `submodular_selection.py` / `diversity-selection-guide.md`) は存在するが**昇格ゲートに未配線** |
| 5 | x402 agentic wallet | N/A | crypto 特化、coding harness に無関係 |
| 6 | skill bundling = directory 化 | Already | Progressive Disclosure / skill-archetypes (absorb skill 自身が directory 構造) |

Pass 2 規律確認: lesson 4b は **article-backed**(原文 "haven't solved this yet" を引用)。Sonnet imagination ではない。

## Adopted (1件, S規模, design note のみ)

ユーザー選択: **A (design note のみ)**。稼働前のため自動ガードは YAGNI、設計段階の risk として codify に留める。

1. `docs/superpowers/specs/2026-05-31-learned-promotion-loop-design.md` に **リスク3 (echo chamber / self-reinforcing)** + watch 条件 + 未解決事項を追記。
2. `.config/claude/skills/promote-learnings/SKILL.md` step 3 に **「多様性チェック (echo chamber 抑制)」** heuristic を1項追加。

**Watch 条件**(これを観測したら `contradiction-scanner.py` / `submodular_selection.py` の昇格ゲート統合を M 規模で起票): (a) 同一 scope の learned が 3 連続バッチ以上昇格を占有、または (b) 矛盾/反証 learned が恒常 reject。

## Rejected / N/A

- Lesson 1,2,3,4,6 — Already (既存カバー濃厚)。
- Lesson 5 (x402) — N/A (crypto 特化)。
- 自動ガード配線 (Option B) — YAGNI で見送り (稼働前、echo chamber 未観測)。watch トリガーで再検討。

## メタ教訓

- harness-engineering family は飽和。Hermes/0xJeff vendor content は2件連続で採用0圏 (delta=0)。本件は delta=1 で1件採用に届いたが、それは「記事が未解決と認めた問題が、たまたま現ブランチの構築中機構に直接該当した」から。記事の novelty ではなく **dotfiles 側のタイミング** が採用を生んだ。
- light-phase2 が正しく機能: フル workflow (Phase 2.5 Codex+Gemini) を回さず S規模 design note で着地。
