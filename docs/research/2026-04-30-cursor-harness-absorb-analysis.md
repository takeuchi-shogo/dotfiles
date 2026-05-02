---
source: "https://cursor.com/blog/continually-improving-agent-harness"
title: "Continually Improving Cursor's Agent Harness"
author: "Stefan Heule & Jediah Katz (Cursor Engineering)"
date: 2026-04-30
fetched: 2026-05-01
status: analyzed
accepted_count: 0
source-trust: "Trusted (Cursor 公式エンジニアリングブログ)"
---

# Continually Improving Cursor's Agent Harness — Absorb Analysis

## 目次

1. [Source Summary](#source-summary)
2. [Gap Analysis (Pass 1 + Pass 2)](#gap-analysis)
3. [Phase 2.5: Refine (Codex + Gemini 批評)](#phase-25-refine)
4. [Phase 3: Triage](#phase-3-triage)
5. [Phase 4: Plan](#phase-4-plan)
6. [教訓・メタ知見](#教訓メタ知見)
7. [Related](#related)

---

## Source Summary

**主旨**: ハーネスは「ソフトウェアと同じ」継続改善の対象であり、定量・定性シグナルとオンライン実験のループで運用する。Cursor チームが 6 章構成で具体的実践を解説した公式エンジニアリングブログ。

**11 手法**:

1. Dynamic context window — 静的 prefill から tool-based 動的 pull へ
2. Keep Rate metric — 提案コード残存率によるハーネス品質測定
3. LM-based satisfaction signal — ユーザー応答の LM 分類によるオンライン評価
4. Online experiments / A-B test — 大規模ユーザーシグナルを用いた統計的実験
5. Tool error taxonomy — InvalidArguments / UnexpectedEnvironment / ProviderError / UserAborted / Timeout の 5 分類
6. Anomaly detection alerts on errors — error rate 異常検知アラート
7. Per-model harness customization — OpenAI=patch、Claude=string-replace の format 切替
8. New model onboarding cycle — offline eval → dogfood → prompt tune の段階的導入
9. Context anxiety mitigation — コンテキスト枯渇への積極的対処
10. In-conversation model switching — cache penalty 軽減のための会話内切替
11. Multi-agent specialization — planner / fast-editor / debugger 役割分担

**前提条件**: 専任エンジニアリングチーム、大量ユーザーシグナル (オンライン実験基盤)、IDE 統合 (terminal session pull)、Cursor 固有の内部 routing/format 切替機構。

---

## Gap Analysis

### Pass 1 + Pass 2 統合テーブル

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Dynamic context window | N/A | IDE 固有機能 (terminal session pull)。dotfiles は CLI 中心で context pull は tool use で代替済 |
| 2 | Keep Rate metric | N/A (重複) | `harness-everything-absorb-plan.md` Gap A で plan 済。本 absorb での重複採用は YAGNI |
| 3 | LM-based satisfaction signal | N/A | 大量ユーザー応答が前提。`friction-events.jsonl` + AutoEvolve で代替済 |
| 4 | Online A/B test | N/A | 大量ユーザー前提。統計的有意性を確保できる規模がない。cross-model delta は既存 |
| 5 | Tool error taxonomy | Already (強化不要) | `failure-taxonomy.md` に 21 FM + 4 HFM が存在。記事の 5 分類は FM-007/009/013 に分散吸収済 |
| 6 | Anomaly detection alerts | N/A | `observability-signals.md` で「個人 dotfiles では ritualization=dead weight」と明示棄却済 |
| 7 | Per-model harness customization | Already (強化不要) | dotfiles は両モデルを Edit tool 経由で使う (Cursor は内部で format 切替)。R-002 で役割分離済 |
| 8 | New model onboarding cycle | Already (強化可能、Watch 行のみ) | `model-debt-register.md` R-001~R-005 + `cross-model-insights.md` で「dogfood→観察→debt 登録」サイクル運用中。formal stage 化は ritualization 寄り |
| 9 | Context anxiety mitigation | Already (強化不要) | `cross-model-insights.md` 2026-03-25 既記載 (Sonnet 4.5 75-80%、Opus 4.6 改善、Anthropic 出典)。autocompact/reset で技術的解決済 |
| 10 | In-conversation model switching | N/A | dotfiles は切替頻度低 + checkpoint で代替。cache penalty 問題は発生頻度低 |
| 11 | Multi-agent specialization | Already (強化不要) | 31 agents + 5 coordination patterns で成熟。planner/editor/debugger 分担は既存 specialist agent で実現済 |

---

## Phase 2.5: Refine

### Codex 批評 (codex:codex-rescue)

- **実行結果**: stdout 清潔取得失敗 (空レスポンス)
- **代替手順**: Opus が以下のファイルを直接精読し、Pass 2 の「強化可能」判定を検証:
  - `failure-taxonomy.md`: 21 FM + 4 HFM 確認 → 記事の 5 分類は FM-007/009/013 で分散吸収済。強化不要
  - `cross-model-insights.md`: Context anxiety 2026-03-25 既記載確認。強化不要
  - `model-debt-register.md`: R-001~R-005 の debt サイクル確認。formal onboarding stage 化は ritualization 寄り → Watch 行のみなら可だが R-005 を本日追加直後、model-debt-register.md 肥大化リスクあり
  - `harness-everything-absorb-plan.md`: Keep Rate が Gap A で既に plan 済。重複採用 N/A

- **Pass 2 修正結果 (4 件格下げ)**:
  - #5 Tool error taxonomy: Already (強化可能) → Already (強化不要)
  - #9 Context anxiety: Already (強化可能) → Already (強化不要)
  - #11 Multi-agent: Already (強化可能) → Already (強化不要)
  - #8 New model onboarding: Already (強化可能) → Already (強化可能、Watch 行のみ) に留まるが、model-debt-register.md 肥大化リスクで採用保留

- **結論**: 採用 0 件が MEMORY.md `feedback_absorb_thoroughness.md` および Learn/Build/Skip absorb の前例パターンに整合

### Gemini 補完 (gemini-explore、Google Search grounding)

- **推奨 3 件**:
  1. Tool error taxonomy (5 分類の追加)
  2. LM-based satisfaction (月 1-2 回の軽量版)
  3. Context Rot 防止 (記事に未言及の Gemini 持ち込み)

- **全 3 件棄却**:
  1. Tool error taxonomy: `failure-taxonomy.md` の 21 FM 存在を Gemini が把握していない。表層的推奨
  2. LM-based satisfaction: `friction-events.jsonl` + AutoEvolve で代替済。Gemini 自身も「測定コスト逆転」リスクを警告しており自己矛盾
  3. Context Rot 防止: 記事に未言及の Gemini 持ち込み項目 + autocompact/reset で技術的解決済

- **出典信頼性**:
  - Cursor Blog のみ独立確認可能
  - 「Anthropic Skill Audits」「Aider Benchmarks Plus」は具体的 URL なしで信頼性低い
  - 「1 桁台削減」は実装可能 (Aider Benchmarks Plus 30-50% 参照、Gemini) — Cursor 固有でなく転移性高いとの指摘あり

- **ベンダーバイアス注記**: Gemini は「実装可能・転移性高い」方向に楽観的推奨。dotfiles での実際の代替機構を把握していない前提での推奨が多い

---

## Phase 3: Triage

**ユーザー選択**: **採用 0 件 (分析レポートのみ)**

**理由**:
- 記事の 11 手法は全て既存仕組みに吸収済または不適用
- 直近 5 本の harness-engineering absorb で採用数が 6 → 3 → 1 → 4 → 0 と飽和傾向
- Watch 行 1 件追加も `model-debt-register.md` の肥大化リスクあり (R-005 を本日追加したばかり)
- 3-month review (2026-Q3) で再検討

---

## Phase 4: Plan

**採用なし。**

変更ファイル: なし

---

## 教訓・メタ知見

1. **累積 absorb 後の同テーマ記事は採用率極端に低い**: 5 本目の harness-engineering absorb で 0 件は飽和の自然な帰結。dotfiles の harness が成熟している証拠でもある

2. **Already (強化可能) → Already (強化不要) の格下げが最も価値が高い**: Phase 2.5 で Pass 2 の「強化可能」判定 4 件をファイル直接精読で剥がす。Codex 実行失敗時でも Opus 直接検証が信頼性高い

3. **Codex 失敗時の Opus 直接検証が効果的**: stdout 空レスポンスでも実ファイル精読により「強化案がノイズ」を 4 件特定。ファイル精読ルートは Codex/Gemini 並列批評より正確なケースあり

4. **Gemini の表層的推奨は要警戒**: `failure-taxonomy.md` の 21 FM を把握せずに「分類追加すべき」と推奨するパターン。実ファイル状態を見ないとノイズが多い。Gemini 自身の自己矛盾 (LM-based satisfaction の「測定コスト逆転」警告) も観察された

5. **dotfiles vs Cursor の前提相違が支配的**: 「大量ユーザーシグナル」「オンライン実験基盤」「専任エンジニアリングチーム」「IDE 統合固有機能」を持たない個人 harness では 7/11 の手法が N/A。記事の質が高くても適用可能性は前提差で決まる

6. **Watch 行 mechanism の活用余地はあった**: R-006 New model onboarding cycle Watch を入れる選択肢はあったが、model-debt-register.md 直後の肥大化リスクを考慮して 0 件採用 (Pruning-First 完徹)。次の Q3 review で再評価

---

## Related

- `references/failure-taxonomy.md` — 21 FM + 4 HFM。記事の 5 分類を吸収済
- `references/model-debt-register.md` — R-001~R-005 の debt サイクル。onboarding watch 候補
- `references/cross-model-insights.md` — Context anxiety 2026-03-25 記載済
- `references/observability-signals.md` — anomaly detection 棄却根拠 (個人 dotfiles では ritualization)
- `docs/plans/active/2026-04-19-harness-everything-absorb-plan.md` — Keep Rate が Gap A で plan 済
- `docs/research/2026-04-24-harness-engineering-absorb-analysis.md` — 同系統の harness 記事 (AlphaSignal、採用 3 件)
- `docs/research/2026-04-29-self-healing-harness-absorb-analysis.md` — 同系統の harness 記事 (CREAO、採用 4 件)
- `docs/research/2026-04-30-three-model-stack-absorb-analysis.md` — Watch 行 mechanism の先行事例 (R-005)
