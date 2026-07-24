---
title: "Graph Engineering: build 1000+ agent loops in one window (0xCodila) — absorb analysis"
date: 2026-07-25
source:
  title: "Graph Engineering: build 1000+ agent loops in one window, from one prompt (full 5-step course)"
  author: 0xCodila (Substack)
  url: https://substack.com/@0xcodila
  type: newsletter
  note: "本文はユーザー貼り付けの全文を一次ソースとして使用。併記された Google Drive PDF は未取得"
status: light-phase2-only
family: multi-agent-orchestration (主) / loop-engineering (副) — cross-family
saturation: "SATURATED-but-novel (N>=17, 採用率 ~20% 境界, delta=3 全て ambiguous) — user light-phase2 選択"
adopted: 1
validation-only: 0
---

# Graph Engineering (0xCodila) — absorb 分析 (light-phase2, 採用 1)

## 結論

3日前に absorb 済みの @0xRafy 記事 (`2026-07-22-graph-engineering-0xrafy`) と同一の「loop の次は graph engineering」era リブランド。ただし著者が違い、**Claude Code の dynamic workflows を実際に叩く手順書** + **Bun の Zig→Rust 移植という実コスト事例** という具体性が加わっている。

12 手法中 9 が named prior の rehash、3 が ambiguous (判断基準・preflight の言語化)。light Phase 2 で 3 件を検証し、**採用 1 件 (S, 1行+1句)** — `subagent-delegation-guide.md` の Agent Teams 適性フィルターに「探索対象が未確定な調査」の Red 行を追加。

## Source Summary

- **主張**: 直線的なマルチステップ agent は「本当は待つ必要のないステップ」を待たせている。仕事の形を graph (node=思考単位 / edge=データ依存) として設計し、独立部分を fan-out・edge に verifier を挟み・worker を隔離せよ
- **手法**: 12 — loop→graph era 移行 + Goodhart 則 / 偽 edge 剥がし / dynamic workflows 構築手順 / `s` で保存・名前で再実行 / コスト構造 (協調は安い・agent 本体は高い) / 上限 1000 agent・同時16 / verifier は clean context の別ノード / worker 隔離 (worktree, Bun 事例) / fan-out 前の3問 / 6レシピ / anchors (実走テスト・証拠ベース verifier・凍結ルール) / graph 非適用の4条件
- **根拠**: Bun の Zig→Rust 移植 (約50 workflow / ピーク64 agent / 535k→100万行 / 11日 / 約$165k / 人間の設計・監視必須、simonwillison.net 2026-07-08)。定量ベンチはなし
- **前提条件**: Claude Code v2.1.154+ / Max・Team・Enterprise は既定 ON、Pro は `/config` で有効化

## Phase 1.5: per-method 照合台帳 (全12手法、delta=3)

| # | current 手法 | verdict | matched_prior (ファイル + 引用 + 同等性) |
|---|---|---|---|
| 1 | loop→graph era 移行 + Goodhart 則 (単一指標ループの劣化) | rehash | `2026-07-22-graph-engineering-0xrafy` #3「4時代区分 (prompt→context→loop→graph)」+ `2026-04-11-multi-agent-coordination-patterns` 強化採用「Reward Hacking 検知ルール」— era framing と指標ゲーミング批判の双方が名指しで既出 |
| 2 | 偽 edge 剥がし (「and then」ごとに "次段は前段の出力を読むか" を問う) | **ambiguous** | 近接は `0xrafy` #2「Node/Edge/Router/State 4プリミティブ」(Edge=出力→入力の依存) だが、*偽 edge を剥がす判定テスト* として 1:1 名指しできず半 novel に倒した |
| 3 | dynamic workflows 構築手順 (v2.1.154+ / プロンプト → plan 承認 → `/workflows`) | rehash | `2026-06-03-dynamic-workflows` #10「Workflow tool JS harness ＝ Gap (意図的非採用)」+ `2026-05-31-32-hacks` の deliberate non-adopt |
| 4 | `s` で `~/.claude/workflows` に保存し名前で再実行 | rehash | `2026-06-03-dynamic-workflows` 12パターンの「save-as-skill」 |
| 5 | コスト構造 (協調は安い / agent 本体は高い、20件から始めろ) | rehash | `2026-06-03-dynamic-workflows` #7「token budget \| Partial \| effort level の間接制御」+ `2026-07-08-agentic-os`「budget (cost-gate)」 |
| 6 | 上限 1000 agent / 同時16 | rehash | 同上 #10 の Workflow tool 仕様。手法でなくプラットフォーム事実 (tool description に毎セッション自動注入される値と一致) |
| 7 | verifier は clean context の別ノード (自己検証禁止・実信号で判定) | rehash | `2026-07-08-agentic-os` 原則2「Nothing grades its own homework」+ `2026-07-08-loop-engineering-es` #3「実行者≠検証者 — Codex Review Gate で model-family diversity 達成済」+ `0xrafy` #7「Loop with Gate (Builder≠Reviewer)」 |
| 8 | worker 隔離 (グループ別 worktree / 共有 git コマンド禁止、Bun 事例) | rehash | `2026-06-03-dynamic-workflows` #4「worktree isolation \| Already \| spike/dispatch/best-of-n-guide」 |
| 9 | fan-out 前の3問 (どこで作業 / 結果をどう merge / 2つが食い違ったら) | **ambiguous** | 近接は `2026-04-11-multi-agent-coordination-patterns` #5「Shared State — 制約明示を採用済」だが、*事前宣言させる preflight* としては名指し不可 |
| 10 | 6レシピ (security sweep / deep-research / module 移植 / 規模ルーティング型 diff review / 定期 scan / 2ラウンド空振りまで探索) | rehash | `2026-06-03-dynamic-workflows` #1 fan-out / #2 loop-until-done / #5 adversarial / #3 model routing + `/review` の tier ルーティング。既出パターンの適用例集 |
| 11 | anchors (実走テスト / 証拠ベース verifier / optimizer が触れない凍結ルール) | rehash | `2026-07-08-agentic-os`「憲法」Already + `family_lessons_improvement_loop` の RSI governance + `superpowers:verification-before-completion`「evidence before assertions」 |
| 12 | graph 非適用の4条件 (小規模 / 逐一承認したい / 探索的 / 真に逐次) | **ambiguous** | dotfiles 側の「Workflow tool 非採用」は既出だが、それは*決定*であって*一般的な非適用条件の判定表*ではない。prior 手法として名指し不可 |

判定: **SATURATED-but-novel (delta=3、純 novel 0 / 全て ambiguous)** → user が light-phase2 を選択。

## Phase 2 (light): ambiguous 3 件のみ検証

Pass 1 (Sonnet Explore) + Pass 2 (Opus 判定):

| # | 記事の主張 | 判定 | 既存 |
|---|---|---|---|
| 2 | 偽 edge を剥がす判定テスト | **Already (強化不要)** | `references/subagent-delegation-guide.md:46`「**発見の影響** \| 一方の発見が他方の作業を変えない → 分割する \| 一方の発見で他方のアプローチが変わる → 同一エージェントに留める」+ `:52-69` Task Parallelizability Gate。記事の "and then" 問答と同一判定を、Google Research 実証 (並列可能 +81% / 逐次推論 -70%) つきで既に持つ |
| 9 | fan-out 前の3問 | **Already (別形で全問カバー、統合は不採用)** | 作業場所 → `:298-306` Clean モード最小入力セット item2「worktree パス + ブランチ名」を必須入力化 / merge → `:598` Lead 統合 + `cmux-ecosystem.md:119` conductor 統合 / 不一致 → `cmux-ecosystem.md:132`「多数決・無制限ラリーは品質を上げない（収束して見える誤答を作る）」+ `skills/debate/SKILL.md:166`「多数＝正しいではない。論拠の質で判断する」。さらに Red 行「同一ファイル編集 \| マージコンフリクト確定。**例外なし**」が記事の Bun 失敗事例を構造的に封じている。3問を1枚の preflight チェックリストに再集約するのは instruction DRY 違反 → **不採用** |
| 12 | graph 非適用条件の判定表 | **Partial → 1条件を追加採用** | Red 表 `:548-551` に「逐次依存 / 同一ファイル編集 / 単一セッションで完了可能 / トークンコスト重視」の4行 + `model-routing.md:62`「Workflow はオーバーキル」+ `subagent-vs-cmux-worker.md:33`「途中で人間が介入したい → cmux Worker」。記事4条件のうち3つは既存。**欠落は「何を探すか未確定な探索」** — しかも Green 行が「大規模 read-only 探索 \| Teams 入門に最適」と書いており、境界が曖昧なまま fleet を推奨する形になっていた |

Gap 0 / Partial 1 → フル workflow への自動昇格なし。Phase 2.5 (Codex + Gemini) は light flag により省略。

## Triage / Adopted

**採用 1 件 (S 規模、1 ファイル、1行追加 + 1句限定)**

`.config/claude/references/subagent-delegation-guide.md` Agent Teams 適性フィルター:

```diff
-| **Green（推奨）** | 大規模 read-only 探索（調査・リサーチ・コンテキスト収集） | ファイル衝突ゼロ。Teams 入門に最適 |
+| **Green（推奨）** | 大規模 read-only 探索（**探索対象が言語化済み**の調査・リサーチ・コンテキスト収集） | ファイル衝突ゼロ。Teams 入門に最適 |
+| **Red（非推奨）** | 探索対象が未確定な調査（何を探すかまだ言語化できない） | fleet は最初の分割方針に固定され、方針転換のたびに全 teammate が無駄になる。単一エージェントで steer し、対象が言語化できてから fan-out する |
```

根拠: 記事の "You don't know what you're looking for yet — exploratory work wants one agent you can steer, not a fleet committed to a plan before you understand the problem"。CLAUDE.md の「仕様が曖昧なまま実装しない (`/spec` or `/spike`)」は*実装*の話で、*fan-out 判断*の軸は別。Bun 事例 ($165k / 人間の設計・監視必須) がコスト側の裏付け。

**不採用**: 他 11 手法。うち #9 は「全問カバー済み + 再集約は DRY 違反」という積極的不採用。

Validation-only: **なし**。上限値 (1000 agent / 同時16) は Workflow tool description の記載と一致し、dotfiles 側に stale な数値記述は見つからなかった。

## 教訓 (family-level)

- **同一 era リブランドが3日で2本届く段階に入った**。0xRafy (07-22) と 0xCodila (07-25) は主題・framing・引用元 (Steinberger / Osmani 系譜) まで重なる。この family は著者ベースで短絡してよい水準に近い
- **ただし 0xRafy 版が delta=1 / 採用0 で、0xCodila 版は delta=3 / 採用1**。差分の出どころは *抽象度*: 0xRafy は「4プリミティブ」の概念整理、0xCodila は「使うな」の negative criteria と実コスト事例。**同 family でも negative criteria を書いた記事は照合先が薄く、delta が出やすい** — 既存 harness の判定表は「使う条件」に偏りがちなため
- 採用の 1 行も新規機構ではなく、**既存の判定表に欠けていた 1 行の境界条件**。飽和 family の正しい収穫の形はこれ
