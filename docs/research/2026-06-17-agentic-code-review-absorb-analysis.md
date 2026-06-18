---
title: Agentic Code Review — absorb analysis
date: 2026-06-17
source:
  type: article (essay)
  title: Agentic Code Review
  note: テキスト直貼り (URL なし)。Sean Goedecke 系の essay 調
family: code-review-best-practices
saturation: PASS (warning) — 高収率 family の N+1 件目、重複領域
adopted: 1
status: implemented
---

# Agentic Code Review — absorb analysis

## 主張 (Phase 1)

コードを書くのが速く安くなり、エンジニアリングの難所が「書く」から「信頼してよいか判断する」= レビューに移った。レビューの設計は **blast radius (壊れたときの被害 × コード寿命 × 理解必要人数)** に完全に依存する。solo / no-users と enterprise / 10年もの は別問題を解いている。経済原則は普遍: 書くのは安くなったが、理解は同じだけ高いまま。

## Saturation Gate (Phase 1.5)

- **family**: `code-review-best-practices` (MEMORY 追跡、N≈10: agents-md-review / findy-readability / harness-human-review / google-eng-practices x2 / openclaw / cursor-auto-review / 6-stages / servant-engineering ...)
- **採用率**: 高 (Google eng-practices 13件全採用 / 6-stages 2件 / servant-engineering 8件全マージ) → 20% 大幅超
- **判定**: PASS (warning)。Step 4.5 連続reject trend = 直近2件とも採用あり、不発火。Step 7 Stale-Plan Audit = 直近3件すべて30日未満 → audit skip

## ギャップ分析 (Phase 2)

essay 寄りで、主張の骨格は dotfiles に既に厚く実装済み。

| # | 手法 | 判定 | 根拠 |
|---|------|------|------|
| 1 | リスクで tier 化 (author でなく risk) | Already | `review/SKILL.md` Step 0 `review-tier.py` + `reviewer-routing.md` (light/standard/deep)。記事の主張そのもの |
| 2 | 異種AIレビュアー (model-family diversity) | Already | `codex-reviewer` (異 family 必須) + 200行超 3-way triangulation |
| 3 | **test変更の精査 (assertion 書き換え)** | **Partial→Gap → 採用** | 後述 |
| 4 | intake bar (evidence before review) | Partial≈Already / N-A (solo) | Pre-PR Chain + `[TESTS NOT RUN]` gate で proof-it-ran は既存。intent 提出は弱いが作者=本人で低価値 |
| 5 | 小さい PR/commit | Already | `github-pr` 300行 split |
| 6 | circuit-breaker / 受信PR triage | N/A | solo に incoming PR queue 無し (team-scale 専用) |
| 7 | human owns merge / AI=sensor not verdict | Partial (prose) | `NEEDS_HUMAN_REVIEW` 機構 + Negative Signal Review Rule は既存。原則の明文化が無いだけ=mechanism は満たし済 |
| 8 | prompt injection (untrusted input → LLM) | Already | `security-reviewer` 4d/4e + `injection-rules.md` R1-R10 + UNTRUSTED INPUT BOUNDARY |
| 9 | mutation testing | N/A (YAGNI) | `autocover/SKILL.md` が既に「任意（ツール導入時のみ）」と明記。個人 harness に infra 構築は overkill |

## Phase 2.5 (Refine) — Codex 失敗 / Gemini は grounding 無し自己批評

skill 必須の第二意見:
- **Codex (cmux worker `w-1781648628`)**: broad grep + web search に wander、1.4MB 出力したまま明確な verdict なく停止 (codex_attention_depth の既知 failure)。**未取得**。副産物として #9 が既存スタンス (autocover 任意明記) と一致することを確認
- **Gemini (gemini-explore)**: API quota 枯渇で Google Search grounding 不可。grounding 無しの自己批評を最終的に return (404s)。不採用 #4 intake bar / #7 AI=sensor は **私の判定に同意**。採用 #3 は妥当だが「リファクタ大量変更と AI drift の区別 heuristic が要る」→ 4c の誤検出絞り込み3条件で対処済

### Gemini の唯一の反論 (#9 mutation testing) → 検討して棄却

Gemini「cargo-mutants 等で solo でも軽量導入できるかも、overkill 判断は時期尚早」。**判定維持 (N/A)**:
1. Gemini 自身が grounding 無しで「導入事例未確認・推測」と明言 — 投機的採用は absorb anti-pattern
2. `autocover/SKILL.md` が既に mutation testing を optional 参照済
3. **採用した 4c こそ、この failure mode (assertion を壊れた挙動に書き換え) に対する mutation testing の軽量代替**。同じバグを review-prompt レベルで安く捕まえるため、重い mutation infra を別建てするのは YAGNI

異種 family の独立検証が要る設計判断では cmux 手動が要る (Codex 不達 + Gemini quota の二重失敗)。S規模1件への過剰処理を避け、Pass 2 判定 (記事原文照合 + Sonnet file-level evidence で立証済) で続行した。

## 採用 (Phase 3-4)

### #3 test-change diff-delta 精査ルール (S規模, 1ファイル)

**gap の本質**: 既存 `test-analyzer` 4b (Tautological Testing 検出) は「テスト単体の質」を静的に見る。記事の failure mode「agent が挙動を変えた後、壊れた挙動に合わせて assertion を書き換える」は tautological ではない (もっともらしい assertion が誤った挙動を encode するだけ) ので **4b では捕まらない**。捕まえる signal は **diff-delta = 既存 assertion の改変 + 同一 diff の挙動変更**。

**実装**: `.config/claude/agents/test-analyzer.md` に section **4c. アサーション書き換え検出** を追加。
- 「新規テスト追加」でなく「既存 assertion 改変」かつ「同一 diff に非テスト挙動変更」→ flag、test diff を先に読む
- 各改変 assertion が「正しい挙動を encode しているか (単に *通る* だけでないか)」を検証
- 誤検出絞り込み: 純粋 test リファクタ (非テスト挙動変更なし) / spec が assertion 変更を要求 / 期待値が厳しくなる方向、は flag を下げる

## 不採用 (理由)

- #4 intake bar / #7 AI=sensor 原則: mechanism は既存、追加は prose のみで solo では低価値
- #6 circuit-breaker: solo に incoming PR queue 無く N/A
- #9 mutation testing: YAGNI、autocover が既に任意扱い
