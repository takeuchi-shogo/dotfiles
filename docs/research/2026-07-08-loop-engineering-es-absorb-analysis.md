---
title: "Cómo crear Loops en Fable 5 (angeldot_/X, スペイン語) — absorb analysis"
date: 2026-07-08
source:
  title: "Cómo crear Loops en Fable 5 — DEJA DE HACER PROMPTS. EMPIEZA A DISEÑAR LOOPS."
  author: angeldot_ (X)
  url: https://x.com/angeldot_/status/2074528618630574393
  type: x-post
status: reference-only
family: loop-engineering
saturation: "SATURATED-pure-rehash (N=16, delta=0) — user continue でフル workflow 実行"
adopted: 0
validation-only: 2
---

# Cómo crear Loops en Fable 5 — absorb 分析 (採用 0)

## 結論

loop-engineering family **N=16 件目**、全 10 手法が named prior で rehash (delta=0)。Saturation Gate は skip 推奨だったが user が continue を選択、フル workflow (Phase 2 Sonnet Explore + Phase 2.5 Codex) を実行した結果も**記事採用 0** で予測どおり。本記事は 2026-06-12 fable5-14steps absorb (同一 Anthropic 素材 — Parameter Golf 6×・Continual Learning Bench 0.839/0.700/0.364・73%/17% まで数値一致) と 2026-06-17 kumai_yu loops absorb (6 ブロックリスト逐語一致) の**スペイン語再パッケージ (三次ソース)**。

continue の価値は validation-only 2 件の発掘のみ: (1) "Outcomes" 語彙欠落の索引補強 (2) /goal pilot 26 日未消化の露出。

## Source Summary (主張)

- プロンプト単位の作業は終わり、検証可能な目標+独立ジャッジで回る自律ループ (Loop Engineering) を設計せよ
- 手法: /goal (検証可能条件+独立ジャッジ) / CMA Outcomes+rubric / 実行者≠検証者 / メモリ5レベル+MEMORY.md 3セクション (PROBADO/VERIFICADO/ABIERTO) / VISION/ARCHITECTURE/RULES.md / 閉→開ループ / 6ブロック (automations/worktrees/skills/MCP/subagents/memory) / ターン上限必須 / 4レシピ (code/research/content/sales) / 理解を手放すな
- 数値: Parameter Golf 6× 改善、CLB 0.839/0.700/0.364、診断検証率 73%/17% — **fable5-14steps で UNVERIFIED 判定済み、据え置き**

## Phase 1.5: per-method 照合台帳 (全 10 手法 → prior 名指し、delta=0)

| # | current 手法 | verdict | matched_prior (ファイル名 + 引用 + 同等性) |
|---|---|---|---|
| 1 | /goal (検証可能条件+独立ジャッジ+自動ターン) | rehash | `2026-06-12-fable5-14steps` #5「/goal \| Gap→Partial→pilot のみ採用」— 同一機能。T3 で `scheduling-decision-table.md` に /goal 行 + pilot 条件を採用実装済 |
| 2 | Outcomes+ルーブリック (CMA, max_iterations) | rehash | `2026-06-12-fable5-14steps` Fact-check + #9「Routines API/GitHub trigger \| deferred by pilot gate」— /goal・Outcomes・CMA の実在確認と pilot gate 判断済。Parameter Golf の 9 criteria rubric も同レポートの例と同一 |
| 3 | 実行者≠検証者 (独立コンテキスト verifier) | rehash | `2026-06-12-fable5-14steps` #6「verifier ≠ self-critique \| Generator-Verifier + Codex Review Gate で model-family diversity 達成済」+ `2026-06-14-opik` #2「Separate checker (not self-grading)」 |
| 4 | メモリ5レベル + MEMORY.md 3セクション (PROBADO/VERIFICADO/ABIERTO) | rehash | `2026-06-12-fable5-14steps` #10+11「5段階メモリ進行 + STATE.md 構造 \| 採用」— T1 `verification_status` (verified/hypothesis/stale/retracted) として実装済。VERIFICADO/ABIERTO 区別 = verified/hypothesis と同一 |
| 5 | VISION/ARCHITECTURE/RULES コンテキストファイル | rehash | `2026-06-17-loops-with-claude`「Skills (手順マニュアル) \| skills/ 100+ + tan-thin-harness」— 「プロジェクト知識を一度書いてループ毎に読ませる」同一ブロック。ADR-0002 Progressive Disclosure 3層が同機能 |
| 6 | 閉ループ→開ループ (quality gate 確立後に開放) | rehash | `2026-06-17-loops-with-claude`「Autonomy ladder (4段階) \| governance-levels.md 4段階と同型」— quality gate が機能してから自律度を上げる同一原則 |
| 7 | 6ブロック (automations/worktrees/skills/MCP/subagents/memory) | rehash | `2026-06-17-loops-with-claude` Source Summary「6部品 (automations/worktrees/skills/connectors/sub-agents/memory)」— 同一リスト、同レポート台帳で 6 行個別に rehash 立証済 |
| 8 | ターン上限を条件に必ず含める (emergency brake) | rehash | `2026-06-14-opik` #3「Exit before loop (done/max-iter/budget) \| ralph-loop --max-iterations 100」+ `2026-06-17-loops-with-claude`「Hard stop (Ralph Wiggum)」 |
| 9 | 4 loop recipes (code/research/content/sales) | rehash | `2026-06-17-loops-with-claude`「Loop = recursive goal \| ralph-loop」— 骨子 (目標→行動→検証→修正→反復) が同一で用途別言い換え。content/sales は dev harness に N/A |
| 10 | 「同じループで理解が深まる人と手放す人」 | rehash | `2026-06-17-loops-with-claude`「caveat: cognitive surrender / two-people-opposite \| comprehension-debt-policy.md」— 同一の two-people メタファー |

## Phase 2: 判定テーブル (Pass 1 Sonnet Explore + Pass 2)

Pass 1 で過去レポート引用ファイルの現存を全確認 (10 グループ中 8 exists / 2 partial、not_found 0)。Doom-Loop 検知が探索中に実際に 2 回発火し、resource-bounds.md の実稼働を直接確認。

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | /goal | Already (注記: pilot 未消化) | `scheduling-decision-table.md` Step 6.5 に pilot 条件文書化済 (bound 必須・撤退判定つき)。**pilot 実行は 06-12 から未消化** |
| 2 | Outcomes+rubric (CMA) | N/A (deferred 維持) | CMA 自体が Phase 0-3 pilot gate で deferred。"Outcomes" の語が references に 0 件 → validation-only #1 |
| 3 | 実行者≠検証者 | Already | `multi-agent-coordination-patterns.md` Pattern 1 Generator-Verifier + Codex Review Gate (異種モデル)。失敗モード定義まであり記事より精緻 |
| 4 | メモリ5レベル+3セクション | Already | `memory-schema.md` verification_status 4値 + `handoff-template.md` §3.7 — 同一ソースから 06-12 採用実装済 |
| 5 | VISION/ARCHITECTURE/RULES | Already (別構造) | ADR-0002 Progressive Disclosure 3層 (CLAUDE.md→references→rules、IFScale 根拠つき) が上回る |
| 6 | 閉→開ループ | Already | `governance-levels.md` 4段階 + 定量昇格条件 (承認率>80% 等)。記事は定性的で下回る |
| 7 | 6ブロック | Already | mcp-toolshed / subagent-delegation-guide / worktree playbook / managed-agents-scheduling 全既存 |
| 8 | ターン上限 | Already | `resource-bounds.md` Doom-Loop (20 fingerprints/3 repeats/300s cooldown) + ralph-loop `--max-iterations` |
| 9 | 4レシピ | Already / N/A | code=ralph-loop+review-loop+implement-loop、research=deep-research (組み込み)。content/sales は N/A |
| 10 | 理解債務 | Already | `comprehension-debt-policy.md` (Osmani 出典明記で既 absorb) |

## Phase 2.5 (Codex 単独 — Gemini は sunset で degraded)

`codex exec --sandbox read-only` (gpt-5.5, xhigh) の批評。結論「採用 0 は妥当」:

- **見落とし**: 手法漏れなし。"Outcomes" は語彙の discoverability 問題であって手法 Gap ではない
- **過小評価の修正**: /goal を「Already」でなく「**既採用だが pilot 未消化の follow-up**」に精緻化。06-12 T3 採用から 26 日、撤退判定の前提となる 2-3 回の試行がゼロ
- **前提の誤り**: 記事は Fable/CMA 前提の playbook。個人 dotfiles + Claude/Codex hybrid harness には content/sales recipe / CMA product semantics がズレる
- **優先度**: 最優先は /goal pilot の決着 (記事採用ではなく既存未消化項目の closure)。次点は Outcomes 用語 alias (索引補強、採用カウント外)
- 検証根拠: Codex が rg で live references の Outcomes 0 件・scheduling-decision-table.md:87 の pilot 条件・fable5-14steps レポート採用記録を独立確認

## Phase 3: Triage 結果

- 記事由来の採用候補: **0 件** (Gap/Partial なし、Already 強化可能なし)
- validation-only #1 (Outcomes alias): **実施** — user 承認
- validation-only #2 (/goal pilot pending): **レポート記録のみ** — user 選択 (Issue 化せず、次の適合タスクで自然に消化)
- 後処理: Wiki INDEX 更新 + Obsidian Literature Note 保存 — user 承認

## Validation-only Follow-up

| # | 対象 | drift/gap 内容 | 対応 |
|---|------|--------------|------|
| 1 | `.config/claude/references/managed-agents-scheduling.md` | CMA 公式用語 "Outcomes" が references 全体で grep 0 件 (機能は deferred 判断済みだが語彙欠落で将来の Saturation Gate / search-first の recall を下げる) | Routine Prompt Rubric 節に用語 alias 1 行追記 (実施済、本 absorb の PR に同梱) |
| 2 | `/goal` pilot (scheduling-decision-table.md Step 6.5) | 06-12 T3 採用から 26 日未消化。撤退判定 (2-3 回試して差分価値なしなら不採用確定) の前提となる試行がゼロのまま | 記録のみ。次の「単発・長時間・測定可能・turn bound を書けるタスク」で 1 回試し、Step 6.5 の撤退条件で決着させる |

## 教訓 (family-level)

- **三次再パッケージ (Anthropic 素材 → EN listicle → ES 紹介) は構造的に採用 0**。一次素材の absorb (fable5-14steps) が実装済みなら、言語を変えた紹介記事は per-method 台帳が数分で delta=0 を立証する
- continue の残余価値は validation-only の発掘 (語彙欠落・pending pilot の露出) に限られる。kumai_yu (06-17) の continue と同一パターンで 2 例目 — 今後の同 family pure-rehash は skip 選択の確度が上がった
