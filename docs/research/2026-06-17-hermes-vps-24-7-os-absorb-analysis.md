---
title: "I Turned Hermes Agent Into an Operation System (Hermes VPS Complete Guide)"
source: https://zenn.dev/sora_biz/articles/hermes-vps-complete-guide
author: sora_biz (Zenn)
date: 2026-06-17
type: absorb-analysis
family: personal-agent-os / hermes (self-evolving 隣接)
status: reference-only
adopted: 0
verdict: SATURATED-pure-rehash (delta=0)。continue 選択でフル検証 (Phase 2-5 + Codex/Gemini) → 採用0確認
---

# Hermes VPS 24/7 OS Complete Guide — absorb 分析

## Source Summary

Nous Research の OSS agent "Hermes" を $6/mo VPS (no GPU, API 呼び出しのみ) で
chat 窓でなく **24/7 OS** として運用する operator playbook。著者は Zenn の
creator-monetization 系。記事自身が「Hermes は Claude Code と complementary,
not competing。Claude Code is daily driver, Hermes is 24/7 infra」と明言。

手法10個:
1. 24/7 OS reframe (chat 窓 → 持続 OS)
2. SOUL.md = charter/identity を最初に書く (#1 beginner mistake)
3. /goal = judge model が done と言うまで multi-turn 追求
4. 3 crons (reactive → proactive)
5. profiles = specialist team + model routing
6. token economics = per-task モデル振り分けで 10x コスト差
7. skill compounding = 20+ skill 書くと ~40% 速い
8. Telegram remote = スマホから全操作
9. profile sharing via git
10. honest limits = weekly skill review / 弱い skill 削除 / long session drift → /compress

## Saturation Gate (Phase 1.5)

- **Hermes 記事の4本目**。過去3本: `2026-04-14 personal-analyst` (採用あり) /
  `2026-04-17 Fleet-shared-memory` (採用あり) / `2026-05-31 eval-loop` (delta=0 採用0)
- "OS reframe / compounding" 角度の直近3件が連続採用0:
  `2026-06-14 Opik` (delta=0) / `2026-05-31 Hermes eval-loop` (delta=0) /
  `2026-05-21 Cyril Personal OS`
- 正式 taxonomy のキーワード閾値 (obsidian/skill-graphs/harness/cc-tips) は未達だが、
  実態は Hermes + personal-agent-os + self-evolving クラスタで明確に飽和。
  「該当 family なし PASS」は暗黙フォールバックになるため、判断が割れる点を明示の上
  per-method 台帳で立証。
- ユーザー選択: **continue** (台帳照合の疑い解消 + 別ツール運用知見のフル検証)

## per-method 照合台帳 (delta=0 の立証)

| # | current 手法 | verdict | matched_prior |
|---|---|---|---|
| 1 | 24/7 OS reframe | rehash | `2026-05-21 Cyril Personal OS` "Personal OS reframe" + nightly launchd/autonomous skill。持続 OS 運用 reframe で同一 |
| 2 | SOUL.md (charter) | rehash | `2026-06-12 fable5-14steps` + CLAUDE.md Foundation/Role/core_principles。identity 固定 doc。SOUL.md は Hermes 固有名 |
| 3 | /goal (judge until done) | rehash | `2026-06-12 fable5-14steps` T3 scheduling-decision-table /goal 行で**明示採用済** + review-loop/implement-loop |
| 4 | 3 crons | rehash | `2026-04-14 Hermes personal analyst` morning-briefing 統合 + `2026-05-28 Codex Research Agent` morning-briefing family |
| 5 | profiles (specialist team) | rehash | `2026-04-24 google/skills ADK2` "Coordinator-Specialist 全 Already" + model-routing.md + 21 agents |
| 6 | token economics (10x) | rehash | `2026-06-12 fable5-14steps` T2 Model Safety Boundary + model-routing.md tier 表 (Fable/Opus/Sonnet/Haiku) |
| 7 | skill compounding (40%) | rehash | skill-graphs family "compound" + promote-learnings/patterns.jsonl。40% は UNVERIFIED 数値 |
| 8 | Telegram remote | rehash → N/A | discord plugin (configure/access) + notify-discord.sh + cmux-remote。媒体差 + 後述 security posture |
| 9 | profile sharing via git | rehash | `project_claude_plugins_provisioning` (task claude:plugins) + dotfiles 自体が git 共有 |
| 10 | honest limits | rehash | run-skill-audit.sh (毎週木) + harness-stability.md (30日評価) + skillListingBudget + compact |

**全10手法 rehash → delta = 0**。実装詳細 ($6 VPS / no GPU / Hermes install) は別ツールのデプロイで N/A。

## Phase 2 判定 (Pass1 8 exists / 2 partial → 精査で全 Already/N/A)

- partial だった (3) /goal: fable5-14steps で採用済・**意図的に pilot 扱い** → Already
- partial だった (8) remote: Discord 片方向通知 + discord plugin で双方向到達可 →
  Codex 指摘で **N/A by security posture / scope mismatch** に修正 (下記)

## Phase 2.5 (Codex + Gemini 並列)

**Codex (gpt-5.5, xhigh)**: 「実装採用 0 は妥当」と明言。精緻化:
- (8) は Already でなく **Partial but non-adopt / N/A by security posture** が正確
  (Telegram「全操作」は認証/承認/監査ログ/kill switch を伴う双方向リモコンで、片方向通知 + 監視とは別物)
- (4) 前提誤り: VPS 常駐 Hermes ≠ ローカル Mac + nightly launchd。可用性モデルが違う
  (Mac は sleep/GUI/認証/ローカル state 依存)。"24/7 infra" をそのまま Gap 軸にすると scope mismatch
- (10) に「弱い skill を消す基準 + 削除後に速くなったか」の KPI 測定が差分という示唆
  → **記事原文は "review weekly, delete weak" のみで速度 KPI は記事 backed でない**。
  過去の計測系死蔵教訓 (observe ログ / eval orphan / regression-gate.py) + ponytail YAGNI で非採用

**Gemini (周辺知識、楽観バイアス込みで割引)**:
- "TokenMix.ai / Build Fast With AI 独立検証" "40% は TokenMix.ai ベンチマークで裏付け"
  → **出典不明、hallucination 懸念。数値は UNVERIFIED のまま扱う**
- 有効な指摘: Hermes は別ツールで補完的、**skill 蓄積はドメイン依存で非転移**
  (開発 skill ≠ リサーチ業務高速化)、VPS 管理 + 外部 I/O のセキュリティコスト
  → dotfiles に別途 Hermes を立てる ROI は低い

## Decision: 採用 0

全10手法 rehash が Codex/Gemini クロス検証で確定。Gap 0、強化余地なし。
Codex「採用0妥当」+ Gemini「別途 Hermes 立てる ROI 低」で両者支持。

修正1点: **(8) Telegram remote: Already → N/A by security posture (scope mismatch)**。
ローカル Mac には「スマホから全操作する対象の 24/7 agent」が不在 +
双方向起動チャンネルは攻撃面で意図的に片方向通知に留めている。必要なら discord plugin で到達可 (媒体差)。

## Next-time anchor

- **Hermes ツール記事は4本中 N+1 が rehash 確定パターン** (eval-loop 5/31 → 本記事 6/17)。
  次回 Hermes / "Personal OS reframe" / "agent as OS" framing は Phase 1 で著者・ツール検出 →
  reference-only 短絡可 (Cyril の「著者ベース短絡」と同型)。
- creator-monetization 系 (Zenn sora_biz 等) の "$X/mo で N時間節約" playbook は構造的低収率。
- Hermes / personal-agent-os の概念核 (持続運用 / charter / judge-loop / model routing /
  compounding / 通知) は dotfiles で全実装済。残差は常に「別ツールのデプロイ詳細」= N/A。
