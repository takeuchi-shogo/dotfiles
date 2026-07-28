---
title: "Lessons from building Claude Code: How we use skills (Anthropic) — absorb analysis"
date: 2026-07-27
source:
  title: "Lessons from building Claude Code: How we use skills"
  author: Thariq Shihipar (Anthropic, Claude Code team)
  url: https://claude.com/blog/lessons-from-building-claude-code-how-we-use-skills
  published: 2026-06-03
  type: vendor-blog
  note: "defuddle 経由で full markdown 取得 (18,343 bytes)。C1 オーバーライド適用"
status: analyzed
family: "skill-authoring (taxonomy 未登録の de-facto family, N=7)"
saturation: "PASS (warning: 重複領域) — 採用率 >= 20% (prior の status は implemented/integrated/completed が並ぶ)"
adopted: 4
rejected: 2
degraded: "Phase 2.5 は Codex のみ。Gemini は IneligibleTierError (UNSUPPORTED_CLIENT) で実行不能"
---

# Anthropic「Lessons from building Claude Code: How we use skills」— absorb 分析 (採用 4, reject 2)

## 結論

記事そのものからの新規手法は薄い。15 手法のうち 11 件が Already で、うち 5 件は dotfiles の実装が記事より先行している (description の negative triggers、SkillNet 5 関係 + composition depth check、skill usage tier + budget collapse、Gotchas coverage scan、archetype 別ディレクトリ表)。

一方で **記事の framing が dotfiles 側の実装乖離を 1 件露出させた**。記事が on-demand hooks の実例として挙げた `careful` / `freeze` は dotfiles に実在するが、その description が実装の強制力を過大表示していた。これが今回の最大の収穫で、記事の主張 #8 (「description はモデル向けの trigger 記述である」) が自分の Guard 型 skill で破れていたという形の自己検出になっている。

## Source Summary

**主張**: skill は「markdown ファイル」ではなくフォルダ (scripts / assets / data / hooks を含む)。Anthropic 社内で数百の skill を運用した結果、9 カテゴリに分類でき、良い skill は 1 カテゴリに収まる。複数カテゴリに跨る skill は agent を混乱させる。

**手法** (15 件):

1. 9-category taxonomy (library/API reference, product verification, data fetching & analysis, business process automation, code scaffolding, code quality & review, CI/CD & deployment, runbooks, infra operations)
2. Verification skill への重点投資 (「engineer が 1 週間かけて verification skill を磨く価値がある」「最も測定可能なインパクトがあった」)。video 録画 / 各ステップでの programmatic assertion
3. Don't state the obvious — Claude が既定でできることを書かない
4. Gotchas セクション = 最高シグナル。実際の失敗点から育て続ける
5. ファイルシステム全体を progressive disclosure として使う (references/ assets/ scripts/)
6. Railroading 回避 — skill は再利用されるので指示を過度に具体化しない
7. Setup フロー — `config.json` に設定を保持、未設定なら user に聞く、AskUserQuestion で構造化
8. Description はモデル向けに書く — 要約ではなく「いつ発火すべきか」の記述
9. Skill 自身の memory (append-only log / JSON / SQLite)、`${CLAUDE_PLUGIN_DATA}`
10. scripts / helper library を同梱し Claude には composition をさせる
11. On-demand hooks — skill 起動中だけ有効な session スコープ hook (実例として `/careful` と `/freeze`)
12. 配布 — repo checkin (`./.claude/skills`) vs plugin marketplace。スケールしたら marketplace
13. Marketplace ガバナンス — 中央委員会を置かず、sandbox フォルダ → traction → PR で昇格
14. Skill composition — ネイティブな依存管理はまだ無い。名前で参照すればモデルが呼ぶ
15. 計測 — PreToolUse hook で skill 使用をログ。popular な skill と **undertriggering** な skill を見つける

**根拠**: Anthropic 社内で数百 skill が稼働。verification skill が品質に最も効いたという内部観測。

**前提条件**: 数百 skill 規模の組織、複数チーム、marketplace 運用あり。

## Phase 1.5 Saturation Gate

`references/topic-family-saturation.md` の登録 4 family はいずれも閾値未満:

| Family | hit | 閾値 | 判定 |
|---|---|---|---|
| `skill-graphs` | 1 (skill composition) | 2+ | 未達 |
| `harness-engineering` | 2 (hook, scaffold) | 3+ | 未達 |
| `claude-code-tips` | 1 (tips) | 2+ | 未達 |
| `obsidian-second-brain` | 0 | 3+ | 未達 |

ただし `docs/research/` に skill-authoring 系 absorb が 7 件実在するため、「family なし」で暗黙 PASS させず de-facto family として集計した (安全側ルール: silently に family なし扱いは暗黙フォールバック)。

- N = 7: anthropic-complete-guide-building-skills (2026-05-23), google-skills-adk2, mattpocock-skills, skill-md-15min-guide, claude-skills-six-laws, warp-oz-skills, skill-graphs-2.0
- 採用率: >= 20% (frontmatter status が implemented / integrated / completed。直近 prior は `adoption: 5 / rejected: 5`、自己申告 family 採用率 ~70%)
- **判定: PASS (warning — 重複領域)**。直近 prior が「採用基準を通常より 1 段階厳しく」と設定済みなので今回も同基準を適用した

**taxonomy 更新の提案**: `skill-authoring` family を `references/topic-family-saturation.md` に登録する価値がある (N=7 で累積実績の条件を満たす)。キーワード案: `skill`, `SKILL.md`, `skill description`, `progressive disclosure`, `gotchas` のうち 3 つ以上。ただし本 absorb のスコープ外なので提案のみ。

## Phase 2 判定テーブル (Phase 2.5 反映後)

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|---|---|---|
| 1 | 9-category taxonomy | **Partial (縮小)** | 3 種の taxonomy が並立 — `references/skill-inventory.md` 4分類 / `skill-creator/references/planning-guide.md` 公式3分類 / `skill-writing-principles.md` の category enum 10種。9 分類そのものの導入は instruction DRY 違反。delta は「主用途 1 つに収まらない skill = 分割候補」という診断のみ |
| 2 | Verification skill 重点投資 | **N/A 寄り Partial** | `skill-archetypes.md` に Product Verification archetype は明文化済だが例が全て仮想。engineer-week 投資は数百 skill 組織の前提。実在の acceptance contract が繰り返し必要になるまで作らない |
| 15 | undertriggering 計測 | **Partial** | `scripts/policy/skill-tracker.py` + `settings.json` PostToolUse (matcher: Skill) が発火した skill を記録 → `skill-audit` の usage tier (Dominant/Weekly/Monthly/Unused)。「呼ばれるべきだったのに呼ばれなかった」は計測外 |
| 13 | marketplace ガバナンス | **N/A** | 単一ユーザー、自前 marketplace なし。近縁は `references/harness-stability.md` の 30 日評価 (撤退側) と `promote-learnings` |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 判定 |
|---|---|---|---|
| 3 | Non-obviousness gate (`skill-creator/references/validation-checklist.md:46`, `skill-writing-principles.md` 原則2) | なし | Already (強化不要) |
| 4 | `## Gotchas` + `skill-audit` Gotchas Coverage Scan | **coverage 20/105 = 19%**。scan 自身が「Guard 型 (freeze, careful 等) を最優先追加対象」と定めているのに未実行 | **Already (強化可能)** |
| 5 | 3-level loading (`skill-writing-guide.md:34-52`) + archetype 別ディレクトリ表 | なし | Already (強化不要) |
| 6 | micromanage vs taste-encoding 象限 (`skill-writing-guide.md:63-113`) | なし (railroading と同義) | Already (強化不要) |
| 7 | `config.json` + `required_setup` + AskUserQuestion (`skill-writing-principles.md:178-196`) | なし (出典が同じ Anthropic 2026-04) | Already (強化不要) |
| 8 | description = trigger + negative triggers + outcomes rubric | なし (dotfiles が先行) | Already (強化不要) |
| 9b | `${CLAUDE_PLUGIN_DATA}` | Codex 指摘で **Gap → Already (条件付き)** に降格。plugin uninstall で削除される領域なので `~/.claude/skill-data/{skill}/` の一律置換は不適切。plugin 化する skill に限り採用 | Already (条件付き) |
| 10 | 9 skill が `scripts/` 同梱 (skill-creator が代表) | なし | Already (強化不要) |
| 11 | `careful` / `freeze` の frontmatter hooks | **description が実装を過大表示** (下記) | **欠陥検出 → 修正済** |
| 12 | vendored + `scripts/lifecycle/claude-plugins-sync.sh` | なし | Already (強化不要) |
| 14 | SkillNet 5関係 (`skill-inventory.md:105-161`) + composition depth check (compound ceiling) | なし (dotfiles が先行) | Already (強化不要) |

## Phase 2.5 Refine

**Gemini: 実行不能**。`IneligibleTierError` / `reasonCode: UNSUPPORTED_CLIENT` (Gemini Code Assist for individuals sunset)。memory `feedback_gemini_cli_sunset.md` の既知条件と一致。周辺知識補完 (他プロジェクト事例 / 未言及のトレードオフ / 新しい代替手法) は**未取得**。

**Codex (gpt-5.6-terra, xhigh, read-only)**: 4 点の指摘のうち 3 点を実ファイルで検証し採用した。

| Codex 指摘 | 検証 | 反映 |
|---|---|---|
| 過大評価: 9b は Gap でなく条件付き Already。`${CLAUDE_PLUGIN_DATA}` は plugin uninstall で削除される | 未検証 (公式 docs の主張。採用しない方向の指摘なのでリスク低) | Gap → Already (条件付き) に降格 |
| 過小評価: Gotchas coverage は 19% (20/105) で強化不要判定は誤り | ✅ `ls */SKILL.md \| wc -l` = 105、`rg -l '^##+ *Gotchas'` = 20 | Already(強化不要) → Already(強化可能)、T2 として採用 |
| 過小評価: `careful` / `freeze` は "Blocks" と説明する一方、実装は全 Bash / 全 Edit・Write への `type: prompt` で決定論的 block ではない | ✅ frontmatter 実物で確認 | T1 として採用・修正済 |
| 見落とし: #15 は発火回数だけでなく期待場面で呼ばれなかった undertriggering を測るのが記事の趣旨 | ✅ 記事原文に "popular or are undertriggering compared to our expectations" | Already(強化不要) → Partial、T3 として採用 |
| 見落とし: `docs/research/2026-04-11-skills-for-claude-code-ultimate-guide-analysis.md` という更に古い prior がある | 未追跡 (今回の判定を覆す指摘ではない) | Saturation Gate の N に未計上。次回の family 登録時に含める |

## 欠陥検出: careful / freeze の description ↔ 実装の乖離

記事が on-demand hooks の実例として挙げた 2 skill が dotfiles に実在するが、description が実装より強い保証を主張していた。

```
careful  description (旧): "Blocks rm -rf, DROP TABLE, force-push, kubectl delete via PreToolUse guard"
         実装:             matcher "Bash" + type: prompt   ← コマンド判別なし。全 Bash に確認プロンプト
freeze   description (旧): "prevents accidental file modifications outside target area"
                           "Blocks Edit/Write with a confirmation guard"
         実装:             matcher "Edit|Write" + type: prompt   ← ディレクトリスコープなし
```

本文側 (`## How It Works` / `## Gotchas`) は当時から正直だった。乖離していたのは **description = モデルが読む trigger フィールド** だけで、これは記事の主張 #8 がまさに扱っている場所である。`/careful` を起動したモデルが「`rm -rf` は機構的に止まる」と誤認しうる状態で、core principle の「暗黙フォールバック・モック・NO-OP 絶対禁止」「境界では Fail Fast」に触る。

なお記事側も同じ表現 (`blocks rm -rf, DROP TABLE, force-push, kubectl delete` / `blocks any Edit/Write that's not in a specific directory`) を使っているため、**記事が描く careful/freeze は dotfiles の実装より強い**。記事の記述を仕様として読むなら実装が未達、dotfiles の実装を正とするなら description が誤り。今回は後者として扱った (ユーザー判断)。

## Phase 3 Triage 結果

| ID | タスク | 規模 | 判定 |
|---|---|---|---|
| T1 | `careful` / `freeze` の description を実装に合わせる + Gotchas に強制力の実態を明記 | S | **採用・実施済** |
| T2 | `skill-audit` の Gotchas Coverage Scan を実行し、Guard 型 + Usage Tier Weekly 以上に `## Gotchas` を追加 | M | **採用 (プラン化)** |
| T3 | undertriggering 計測を `skill-tracker.py` に追加 (description の trigger 語がセッションに出現したが該当 skill 未発火の検出) | M | **採用 (プラン化)** |
| T4 | category 跨ぎ診断を `skill-audit` に追加 (9 分類は導入しない。「主用途が 1 つに収まらない skill は分割候補」の診断のみ) | S | **採用 (プラン化)** |
| — | 9-category taxonomy の導入 | — | **Reject** — 既に 3 taxonomy が並立。4 つ目の追加は instruction DRY 違反 |
| — | Verification skill への engineer-week 投資 | — | **Reject** — 数百 skill 組織の前提。dotfiles 固有の acceptance contract が繰り返し必要になった時点で archetype を使って小さく作る (Codex 推奨) |

## 実施済 (T1)

- ブランチ: `fix/careful-freeze-description-drift`
- `.config/claude/skills/careful/SKILL.md` — description 1 行差し替え + Gotchas に `hard block ではない` を追加
- `.config/claude/skills/freeze/SKILL.md` — description 2 行差し替え + Gotchas に `hard block ではない・スコープ指定もできない` を追加
- 検証: `task validate-configs` ok / Claude Code の skill listing が新 description で再読込されることを確認 (frontmatter パース成功の決定的証拠)
- 未実施: commit / PR (ユーザー指示待ち)

## 残タスク

T2 / T3 / T4 のプラン: `docs/plans/active/2026-07-27-skill-observability-plan.md`

## 未取得・未検証

- **Gemini 周辺知識補完**: 実行不能 (IneligibleTierError)。他プロジェクトでの採用事例・記事が言及しないトレードオフ・より新しい代替手法は未取得
- `${CLAUDE_PLUGIN_DATA}` の plugin uninstall 時削除挙動: Codex の主張のみ。公式 docs 未確認 (採用しない方向なのでブロッカーではない)
- `docs/research/2026-04-11-skills-for-claude-code-ultimate-guide-analysis.md` の内容: Saturation Gate の N に未計上
