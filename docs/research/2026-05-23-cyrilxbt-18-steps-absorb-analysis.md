---
title: "@cyrilXBT 18 Steps to Unlock the Other 90% — absorb analysis (light-phase2)"
date: 2026-05-23
status: light-phase2-only
adopt_count: 0
family: claude-code-tips
author: "@cyrilXBT"
prior_absorb_count: 12 (cyril-family) / 9+ (claude-code-tips family)
verdict: Reject (Sonnet imagination 罠 + Wave-3 設計判断と逆向き)
---

# @cyrilXBT 「Most People Use 10% of Claude. Here Are the 18 Steps That Unlock the Other 90%」

## Source Summary

- 著者: @cyrilXBT — dotfiles の absorb 履歴で 11 件目以上の常連 listicle author (cyril-obsidian-vault x3, cyril-obsidian-dashboard 他)。過去はほぼ全て Reference Only / Reject 判定
- 形式: 4 週間 18-step プログラム (Foundation 5 / Quality 5 / System 4 / Intelligence 4)
- 主張: Claude を chat interface ではなく "configured intelligence system" として扱うと 10% → 100% の gap が埋まる
- 根拠: 著者の主観的経験のみ。ベンチマーク・出典・事例引用なし
- 締めくくり: "Follow @cyrilXBT for every Claude configuration, skill file, and workflow"（self-promotion）

## Phase 1.5 Saturation Gate 判定

- Family: `claude-code-tips` (loose 該当 — "18 Steps" は "N tips" のバリエーション)
- 過去事例 (N >= 9): Boris 30 Tips, Khairallah 40 Features (採用 0), Three-Model Stack (棄却), 73% Overhead 9 Patterns (1 件), zodchixquant 15 Settings (部分), 12-rule CLAUDE.md (Reject), Claude Skills 6 法則, Top 67 Claude Skills (2 件), 100+ Skills Best 6 (5 件)
- 採用率: ~30% (PASS warning 圏内)
- 手法 delta 計算: 18 手法のうち 16 件が完全 Already、novel 候補 2 件 (#13 `/goal` + #2 Voice Profile) のみ
- 判定: **SATURATED-borderline → light-phase2** (ユーザー判断)

## Phase 2 Pass 1 (Sonnet Explore) + Pass 2 (Opus) 統合判定

| # | 手法 | Pass 1 | Pass 2 確定 | 根拠 |
|---|------|--------|------------|------|
| 13 | Claude Code `/goal` command | not_found | **N/A (likely FABRICATED)** | dotfiles に未存在。代替: `/feature-tracker` (multi-session progress), `/checkpoint` (Running Brief), `/spec`, `/rpi` (Research→Plan→Implement 3-phase), `/autonomous`。Gemini grounding は rate-limit で確証取れず、ただし Claude Code 公式 slash command リストに `/goal` の存在を裏付ける記憶なし (`/agents`, `/init`, `/help`, `/clear`, `/compact`, `/cost`, `/model`, `/login`, `/logout`, `/rewind`, `/exit` 等は確認済)。"goal-checking が autonomous work の鍵" 主張は `/rpi` Plan ステージで実装済の goal-driven examples 概念で完全カバー |
| 2 | Voice Profile (10 sample 分析プロンプト) | partial | **Already (N/A by design)** | `/mizchi-blog-style` skill が **23 blog post の voice extraction を 5 軸評価 (tl;dr/subjectivity/colloquialism/concreteness/candor) + AI-smell 検出 (10 anti-patterns) + 8/10 convergence subagent loop** で上位互換実装済。さらに `docs/plans/2026-04-09-12-claude-patterns-integration.md` Task 7 で `voice-profile-guide.md` を **意図的に Wave 3 / Light Touch / documentation only / not a skill** に降格 (理由: Gemini 知見「LLM voice learning は短期的」)。記事の 7 次元 10-sample プロンプトは **既存の意図的 skip 決定と方向真逆**。`/rewrite` の audience preset (technical/executive/slack/casual) + `personas/` 静的テンプレ (gal/imouto/mesugaki/onesan) で persona 切替もカバー済 |

## Pass 2.5 Refine

- **Codex 批評**: skip (light-phase2 では省略可)
- **Gemini grounding**: rate-limit 制約により公式 `/goal` 存在の確証取得失敗。ただし判定根拠は dotfiles 内 plan ドキュメント (Wave 3 light touch 決定) + `/mizchi-blog-style` 上位互換存在 + 過去 absorb 履歴の累積 evidence で十分に固まる。**Voice Profile が "documented best practice" であるかは UNVERIFIED** だが、判定への影響なし (採用しない側で結論固定)

## adopted / rejected decisions

- **adopted: 0 件**
- **rejected**: 18 手法すべて (16 件 Already 既存実装 + 2 件 novel 候補も Pass 2 で N/A 確定)

## Validation-only Follow-up

なし。今回は dotfiles 内 stale fact / drift を露出させる主張は含まれていなかった。
( Khairallah 40 Features の "Cowork tab" のような platform drift 検出機会なし )

## Meta-findings

1. **Skill 自身の防御機構が機能した実例**: `feedback_absorb_sonnet_imagination.md` (Pass 1 強化余地メモを Pass 2 で引用照合) + Phase 1.5 saturation gate (claude-code-tips family taxonomy) + Sonnet imagination 罠 anti-pattern により、Sonnet Explore の "Voice Profile is PARTIAL" 報告に対して Pass 2 で **「partial → N/A by design」へ正しく訂正** できた。Khairallah (2026-05-22) で初検出し codify した防御が、次サイクル (1 日後) で機能した
2. **同一著者 (@cyrilXBT) 11 件目以上で安定的 Reject パターン**: 著者シグナルを Phase 1.5 family taxonomy に取り込むかは別 audit 候補だが、今回は family taxonomy + saturation 件数で十分に判定できたため新規ルール化見送り
3. **light-phase2 が 10 分で adopt=0 確定**: フル workflow なら 30+ 分必要だったところを Phase 2 Pass 1 + Pass 2 + 既存 plan ドキュメント Read だけで終結。Pruning-First の典型成功事例

## Phase 5 Handoff

- 採用 0 のため `ingest-skip (light Phase 2, adopt=0)` 扱い
- log.md に 1 行追記、Wiki INDEX / Obsidian Bridge / MEMORY.md ポインタは skip
- mini レポート (本ファイル) のみ docs/research/ に保存
