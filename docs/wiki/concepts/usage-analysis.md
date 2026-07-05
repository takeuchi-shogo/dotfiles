---
title: 使用実態分析
topics: [skill, evaluation]
sources:
  - 2026-05-09-skill-inventory-vs-usage.md
  - 2026-05-09-skill-usage-tally.md
updated: 2026-07-05
confidence: emerging
source_count: 2
last_validated: 2026-07-05
---

# 使用実態分析

## 概要

skill/agentのインベントリ（存在するもの）と実際のセッショントランスクリプト（使われたもの）を突き合わせ、死蔵・過小利用・過剰利用を可視化する棚卸し手法。「登録されているが誰も使わない」ものを削除候補として特定する一方、手動起動（slash command）と自動起動（Skillツール）では使用頻度の分布が異なるため、単一の指標だけで判断しないことが要点になる。

## 主要な知見

- 172件のインベントリに対し、PC全体のトランスクリプト1972ファイル・225,339行を横断集計し、DEAD（0回使用かつ経過30日超）15件、UNDER-USED（1-2回）15件、RECENT SKIP（30日以内で未使用）107件、WELL-USED（3回以上）35件に分類した [EXTRACTED, conf=90]
- DEAD判定は「使用回数0件かつage 30日超」を基準にする。30日という猶予を置くことで、導入直後で単に使う機会がなかっただけのskillを誤って削除候補に含めない [EXTRACTED, conf=85]
- WELL-USED上位はcommit/gemini/absorb/reviewなど、日常ワークフローに組み込まれたコアツールに集中し、使用頻度の分布は極端に偏る（上位数件が大半の呼び出しを占める） [EXTRACTED, conf=80]
- 同じskillでも手動起動（slash command）と自動起動（Skillツール経由）の頻度は乖離する。例えば`/absorb`は手動77回に対し自動起動16回というように、ユーザー主導とAI主導は別の分布を持つため、片方の集計だけでは使用実態を見誤る [EXTRACTED, conf=80]
- コマンドごとに時間帯分布（朝/昼/夕方/深夜）に偏りがあり、作業習慣を反映する指標として使える。例えば/commitは夕方から夜に集中し、/absorbは朝に偏る [EXTRACTED, conf=65]
- RECENT SKIP（30日以内で未使用）は削除候補ではなく「様子見」の保留区分として扱う。DEADと同列に即削除すると、導入間もない機能を時期尚早に切り捨てるリスクがある [INFERRED, conf=70]

## 実践的な適用

dotfilesではskill-audit skillでのA/Bベンチマークや、`skillListingBudgetFraction`によるskill説明の自動折り畳み判断（PR #70）の前提データとして、この種の横断集計が使われている。未使用61件を`skillOverrides`で抑制し、トークン量を約18kから11k/セッションへ削減した実績がある。

## 関連概念

- [skill-conflict-resolution.md](skill-conflict-resolution.md) — 使用実態の把握はskill同士の競合検出とも接続する

## ソース

- [Skill/Agent Inventory × Usage Cross-Reference レポート](../../research/2026-05-09-skill-inventory-vs-usage.md) — 172スキル/エージェントの使用状況を横断集計、死蔵15件検出
- [Skill / Slash Command Usage Tally レポート](../../research/2026-05-09-skill-usage-tally.md) — 200セッションのスラッシュコマンド使用頻度を集計
