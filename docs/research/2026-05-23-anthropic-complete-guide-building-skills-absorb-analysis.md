---
date: 2026-05-23
source: "Anthropic 公式 The Complete Guide to Building Skills for Claude (PDF, 2026-01-27 発行, 33頁)"
source_url: https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf
type: official-1st-party-guide
family: skill-building-methodology
saturation: PASS-with-warning
adoption: 5
rejected: 5
n_a: 5
status: implemented
plan: docs/plans/active/2026-05-23-skill-guide-absorb-plan.md
implemented_date: 2026-05-23
---

# Absorb Analysis: Anthropic 公式 The Complete Guide to Building Skills for Claude

## TL;DR

Anthropic 公式の Skills ガイド (PDF 33 頁、2026-01-27 発行) から 42 手法を抽出し、Codex + Gemini 並列批評を経て最終 5 件を採用した (規模 M-L)。Pass 2 の Opus 判定で false-positive Already を量産したため Codex 批評で 6 件から 3 件に絞り込み、ユーザー Triage で H10 hook 化と H39 selective の 2 件を追加して 5 件が確定した。1 次情報源として dotfiles の skill 設計優位 (5D / Gotchas / negative routing) を補強する形での統合を想定している。

---

## Source Summary

PDF は 6 章構成で skill の作成・テスト・デプロイを一貫して解説する Anthropic 公式ガイドである。

**6 chapter 構造**:
1. Introduction to Skills — skill の定義・目的・Claude との関係
2. Crafting Effective Skills — SKILL.md 設計原則、description・trigger・instructions の書き方
3. Testing & Evaluating Skills — eval 手法、3-arm 比較、human eval ガイドライン
4. Advanced Patterns — Pipeline / Guard / Gate 型、Subagent Inheritance、Micro-Skills
5. Deployment & Management — skill lifecycle、token tax、description 最適化
6. Appendix — テンプレート・チェックリスト・サンプル

**3 use case categories**: Workflow Automation / Knowledge Retrieval / MCP Enhancement

**5 Patterns**: Pipeline / Guard / Gate / Micro-Skill / Reference-Only

---

## Phase 1.5 Saturation Gate 判定

- **family**: skill-building-methodology
- **既存 absorb 件数 N**: 11 件
  - Tan 記事 / Skills for CC Ultimate Guide / PostHog / Karpathy / Skill Graphs 2.0 / SKILL.md 15min Guide / 100+ Skills Best 6 / Warp oz-skills / mattpocock / Claude Skills 6 法則 / 30 Sub-Agents
- **family 内採用率**: ~70% (高採用率 family)
- **判定**: **PASS (with warning)** — 1 次情報源 (Anthropic 公式) の優先度から続行。ただし family 飽和に近いため採用基準を通常より 1 段階厳しく設定する

---

## Phase 2 ギャップ分析テーブル

H = Hypothesis (記事から抽出した手法)。判定は Pass 2 Opus + Codex 批評後の **最終値**。

| ID | 手法 | 初期判定 | 最終判定 | 備考 |
|----|------|----------|----------|------|
| H1 | Skill description は動詞+名詞+outcome で始める | Partial | **Partial** | outcomes rubric 未実装 (→ T3) |
| H2 | trigger は positive example のみ列挙する | Already | **Already** | skill-description-template.md に記載済み |
| H3 | negative trigger (使わない条件) を明示する | Already | **Already** | negative-routing として skill-invocation-patterns.md に実装済み |
| H4 | Gotchas セクションで失敗パターンを列挙する | Already | **Already** | dotfiles SKILL.md テンプレートに存在 |
| H5 | tool scoping で不要ツールを除外する | Already | **Already** | skill-patterns.md に記載済み |
| H6 | 5D Quality Score (clarity/trigger/scope/test/doc) | Already | **Already** | skill-audit SKILL.md Step 0 に実装済み |
| H7 | SKILL.md 全体をコンテキストに読み込む (skill folder load) | Already | **Partial→Already修正** | Codex: run_eval.sh は SKILL.md append のみ、folder load 未実装 (→ T1) |
| H8 | instructions は numbered steps で書く | Already | **Already** | 既存テンプレートのデフォルト形式 |
| H9 | examples セクションで good/bad を示す | Already | **Already** | feedback_bad_example_pattern.md + テンプレート済み |
| H10 | README.md を skill folder に置かない | Not_found | **Not_found** | lefthook hook 未実装 (→ H10 hook 化) |
| H11 | skill lifecycle: active / deprecated / archived 管理 | Already | **Already** | skill-inventory.md に tier 管理あり |
| H12 | eval は baseline vs skill の 2-arm が最低ライン | Partial | **Partial** | run_eval.sh は 2-arm だが terse variant なし |
| H13 | 3-arm eval (skill vs terse vs baseline) が gold standard | Partial | **Partial→Partial維持** | aggregate.py に `--three-arm` フラグ未実装 (→ T1.2) |
| H14 | human eval ガイドライン (Likert 5 点) | Already | **Already** | skill-test-cases.yaml に Likert 形式あり |
| H15 | eval dataset は skill ごとに 10-20 ケース | Already | **Already** | skill-test-cases.yaml 構造が対応 |
| H16 | 全 skill に `## Critical` section を top に置く | N/A | **N/A** | knowledge skill に強要は不適切。Pipeline/Guard のみ選択適用 (→ H39 selective) |
| H17 | skill folder 構造: SKILL.md / scripts / references / assets | Partial | **Partial** | skill-creator で生成するが eval でロードしていない (→ T1.1) |
| H18 | subagent inheritance: 親コンテキストを子に渡す形式 | N/A | **N/A** | Anthropic 公式ドキュメントに存在確認できず (Gemini grounding 要注意) |
| H19 | description token budget: enabled skill * description ≦ 1500 字 | Partial | **Partial** | token tax の概念は absorb 済みだが自動計測ツール未実装 (→ T2) |
| H20 | skill の use-case category 分類 (Doc/Workflow/MCP-Enhance/Ref) | Partial | **Partial→確認** | Codex: skill-inventory.md に category 列なし (→ T3.1) |
| H21 | Micro-Skills: 単一責任の 50 行以下 skill | Already | **Already** | KISS 原則で既実装 |
| H22 | Pipeline pattern: DO NOT proceed until ゲートを明示 | Partial | **Partial→Partial維持** | skill-patterns.md Pipeline セクションに gate 記述あるが `## Critical` top 配置は未記載 (→ H39 selective) |
| H23 | Guard pattern: 危険操作前の確認プロンプト | Already | **Already** | careful skill + hook で実装済み |
| H24 | Gate pattern: 外部 API 呼び出し前バリデーション | Already | **N/A→Already修正** | Codex: 実装済みだが skill-patterns.md の Gate セクション記述が薄い |
| H25 | skill trigger は動詞から始める | Already | **Already** | テンプレートで指定済み |
| H26 | instructions に tool call の例を含める | Partial | **Partial** | 一部 skill のみ |
| H27 | skill の冪等性: 同じ入力で同じ出力 | Already | **Already** | determinism-boundary.md に記述済み |
| H28 | skill テスト: dry-run モードを提供する | Partial | **Partial** | skill-audit の dry-run は実装済みだが skill-creator 側未対応 |
| H29 | deprecated skill は 30 日後に archive | Already | **Already** | harness-stability.md に 30 日ルール |
| H30 | skill description の A/B テスト | N/A | **N/A** | 個人用途では ROI 低 |
| H31 | skill の scope: user / project / local の 3 層 | Already | **Already** | CLAUDE.md に明記済み |
| H32 | skill は 1 つの目的・1 つの動詞 | Already | **Already** | KISS 原則 |
| H33 | skill folder の assets/ に参照データ置く | Already | **Already** | skill-creator テンプレートで生成 |
| H34 | skill の version 管理 (CHANGELOG.md 相当) | N/A | **N/A** | overhead > benefit |
| H35 | skill の依存関係を明示 (depends_on frontmatter) | N/A | **N/A** | skillnet_integration.md で関係タイプとして管理 |
| H36 | skill 実行ログを JSONL で記録 | Already | **Already** | session-observer で実装済み |
| H37 | skill の token 消費量を測定・報告する | Partial | **Partial** | session_observer は cache_read/create 抽出済みだが skill 単位の breakdown なし |
| H38 | enabled skill 数を 20 以下に保つ | Already | **Already** | skill-audit Step 0 の tier 管理 |
| H39 | `## Critical` を全 skill top に置く | Already | **N/A→selective修正** | Codex: knowledge skill に強要不適切。Pipeline/Guard/Gate のみ (→ H39 selective) |
| H40 | skill の ownership: 作成者・更新日を frontmatter に | Already | **Already** | date frontmatter が標準 |
| H41 | skill の eval を CI に統合する | N/A | **N/A** | 個人 dotfiles では CI なし |
| H42 | negative example を trigger セクションに含める | Already | **Already** | negative-routing pattern で実装済み |

**集計 (最終)**: Exists 29 / Partial 13 / Not_found 1 (H10)

---

## Phase 2.5 Refine — Codex + Gemini 統合

### Codex 批評 (cmux Worker fail → `codex exec --skip-git-repo-check -m gpt-5.5 --sandbox read-only --config model_reasoning_effort="xhigh"` 直接呼び出しで実行)

cmux Worker は terminal 不在のため fail した。`codex exec` 直接呼び出しで `--skip-git-repo-check` を付加して成功。以下 6 質問への Codex 回答全文:

**Q1: Pass 2 で見落とした手法はあるか?**
> H7 の判定が誤り。run_eval.sh を確認すると SKILL.md のみ append しており、scripts/ references/ assets/ を含む skill folder 全体はコンテキストに入っていない。これは "Already" ではなく "Partial" であり T1 の根拠となる実装 Gap が存在する。H12/H13 の 3-arm eval も同様で aggregate.py に --three-arm フラグが未実装な点を明示すべき。

**Q2: 過大評価 (Partial を Already と誤判定) した箇所はあるか?**
> H20 (use-case category 分類) は skill-inventory.md を見ると tier 列はあるが Doc/Workflow/MCP-Enhance/Reference の 4-category 列は存在しない。Partial が正しい。H22 (Pipeline gate) も skill-patterns.md に Pipeline セクションはあるが "DO NOT proceed until" を `## Critical` ヘッダで最上部に置く設計は未記載、Partial 維持が正しい。

**Q3: N/A に降格すべき Partial はあるか?**
> H39 (全 skill への `## Critical` 必須化) は N/A が正しい。knowledge skill に強制すると可読性が下がる。Pipeline/Guard/Gate 型のみへの選択適用として H39 selective に分離すべき。H30 (A/B テスト) は個人用途で N/A 維持が適切。

**Q4: Already に降格すべき Partial はあるか?**
> H24 (Gate pattern バリデーション) は careful skill + hook で実装済み。ただし skill-patterns.md の Gate セクションの記述が薄いという観点では Partial にも見える。実装は存在するので Already 寄りだが、documentation gap として記録するに留める。

**Q5: 採用判断の前提に誤りはあるか?**
> H18 (Subagent Inheritance) は "Anthropic 公式 PDF の主張" として扱っているが、Gemini grounding で community 推測由来の可能性がある。PDF 原文に "subagent inheritance" という用語が明示されているか確認が必要。確認できなければ N/A が正しい。

**Q6: 採用優先度 Top 3 は何か?**
> 1. T1 (3-arm eval 基盤) — eval 精度が全 skill の品質判断基盤になるため最高優先。2. T2 (description token tax 計測) — token 消費の可視化は即効性が高い。3. H10 hook (README.md block) — lefthook に 1 行追加するだけで強制できる最小コスト。

### Gemini grounding (5 項目)

**信頼性メモ**: gitconnected.com / agentskills.io 由来の情報 (Negative Triggers / Checklist / Micro-Skills / Subagent Inheritance / 別定義 5D) は community 推測の可能性があり、Anthropic 公式 PDF に記載があるかの grounding 確認が必要。以下の判定は Gemini の web search 結果に基づく。

**項目 1: API 進化 — claude.ai/skills エンドポイントの最新状況**
> 2026-01 時点で skills API は claude.ai (pro/team) での UI 経由作成が主。API 経由の programmatic create は未公開 (waitlist 段階)。dotfiles での SKILL.md ベース管理は引き続き有効。

**項目 2: anthropics/skills GitHub repo の最新状況**
> 2026-05 時点で anthropics/skills は public repo として存在。community contributions あり。dotfiles の skill 構造と概ね一致するが、folder 命名規則に軽微な差異 (skill-creator vs creator) あり。直接の互換性確認は未実施。

**項目 3: community trends — description token tax の実態**
> community では "token tax" という用語が定着しており 1000-1500 字 budget が経験則として広まっている。Anthropic 公式 PDF の記述と整合。T2 採用を支持。

**項目 4: Hierarchy — Micro-Skill の定義**
> Anthropic 公式と community で定義が分岐している。公式: "単一責任・50 行以下"。community (agentskills.io 等): "composite skill の atomic unit"。dotfiles では KISS 原則での実装が近い。採用時は公式定義に準拠する。

**項目 5: Cache & Token economy — skill eval コスト**
> 3-arm eval を毎 commit で実行するとキャッシュなしで 10k-30k token/eval。prompt cache (TTL 5 min) を活用すれば 70-80% 削減可能。T1 実装時にキャッシュ戦略を含めることを推奨。

### 統合判断: 6 → 3 件 → 5 件確定

Codex 批評で H7 gap 確認 (T1 根拠強化)、H20 gap 確認 (T3 根拠強化)、H39 selective 分離。H18 (Subagent Inheritance) は PDF 原文確認できず棄却。

初期 6 候補 → Codex 批評後 3 件 (T1/T2/T3) → ユーザー Triage で H10 hook + H39 selective の 2 件追加 → **最終 5 件確定**。

---

## Phase 3 Triage 結果

ユーザー回答による最終確定:

| タスク | 内容 | 規模 | 決定 |
|--------|------|------|------|
| T1 | 3-arm eval 基盤 (run_eval.sh + aggregate.py + SKILL.md 更新) | M | **採用** |
| T2 | description token tax 計測 (skill-audit Step 0.6 新設) | S | **採用** |
| T3 | category 軸 + outcomes rubric | S | **採用** |
| H10 hook | README.md block lefthook hook | S | **採用** |
| H39 selective | Pipeline/Guard/Gate のみ `## Critical` top 化 | S | **採用** |
| H18 | Subagent Inheritance | — | **棄却** (PDF 原文未確認) |
| H16 | 全 skill `## Critical` 必須化 | — | **棄却** (knowledge skill 不適切) |
| H26 | instructions への tool call 例追加 | — | **棄却** (overhead > benefit) |
| H30 | A/B テスト | — | **N/A** |
| H34 | version 管理 | — | **N/A** |

---

## Phase 4 採用タスクリスト

### T1: 評価基盤の修正 (M)

**T1.1** `~/.claude/skills/skill-creator/scripts/run_eval.sh`
- 変更: SKILL.md append のみ → skill folder 全体ロード (scripts/ references/ assets/ を含む) に修正
- 検証: `bash run_eval.sh --dry-run` で folder contents がコンテキストに含まれることを確認

**T1.2** `~/.claude/skills/skill-creator/scripts/aggregate.py`
- 変更: `--three-arm` フラグ実装。arm_a/arm_b/arm_c.json を受け取り `delta_skill_vs_terse` と `delta_terse_vs_baseline` を出力
- 検証: `python aggregate.py --three-arm arm_a.json arm_b.json arm_c.json` が JSON 出力を返すこと

**T1.3** `~/.claude/skills/skill-creator/SKILL.md`
- 変更: Step 2.5 と Step 3 に「full-package eval が default になった (scripts/references/assets を含む folder 全体をロード)」旨を追記
- 検証: diff で追記行の存在確認

**T1.4** `~/.claude/skills/skill-audit/SKILL.md`
- 変更: Step 3「Optional: 3-arm evaluation」セクションの「現時点での最小実装」を「正式実装」に書き換え。`--three-arm` フラグの使用例を追記
- 検証: diff で書き換え行の存在確認

### T2: Description Token Tax (S)

**T2.1** `~/.claude/skills/skill-audit/SKILL.md`
- 変更: Step 0.5 と Step 0.7 の間に **Step 0.6: Description Token Tax** を新設
  - enabled skill count を `ls ~/.claude/skills/` でカウント
  - 各 skill の description 字数を合算
  - budget 目安: 1000-1500 字相当
  - over-budget 時: Top heaviest skill を retire または trim 推奨
- 検証: skill-audit 実行時に Step 0.6 が出力されること

### T3: Category 軸 + outcomes rubric (S)

**T3.1** `~/.claude/references/skill-inventory.md`
- 変更: 各 tier の skill リストに **use-case category 列** (Doc / Workflow / MCP-Enhance / Reference) を追加
- 検証: `grep -c "Doc\|Workflow\|MCP-Enhance\|Reference"` で全 tier に category が付与されていること

**T3.2** `~/.claude/skills/skill-audit/SKILL.md`
- 変更: 5D Quality Scan (Step 0) に **outcomes-not-features rubric** を追加
  - description が「動詞+名詞+outcome」で始まるか
  - "features" の列挙になっていないか
  - 静的検査: `grep -E "^(Add|Run|Generate|Check|Analyze|Build)"` で先頭動詞を確認
- 検証: rubric セクションが Step 0 内に存在すること

### H10 hook 化 (S)

**H10.1** `lefthook.yml` (dotfiles repo root)
- 変更: pre-commit hook 追加 — `find .config/claude/skills -name README.md` で見つかれば block
  ```yaml
  pre-commit:
    commands:
      no-skill-readme:
        run: |
          if find .config/claude/skills -name README.md | grep -q .; then
            echo "ERROR: skill folder に README.md は置かない (SKILL.md を使う)"
            exit 1
          fi
  ```
- 検証: `.config/claude/skills/test/README.md` を作成して commit → block されること

**H10.2** `~/.claude/references/skill-writing-principles.md` (存在しなければ skill-patterns.md に追記)
- 変更: 動的 enforcement (lefthook) の仕組みを documentation に追記。「validation-checklist の静的ルール (README.md 禁止) を lefthook pre-commit で動的に補強」の旨を 1 段落追加
- 検証: diff で追記行の存在確認

### H39 selective (S)

**H39.1** `~/.claude/references/skill-patterns.md`
- 変更: Pipeline pattern セクションに以下を追記:
  > **`## Critical` section を top に置く** — Pipeline gate ("DO NOT proceed until") は Section header としてもまとめて SKILL.md の最上部近くに配置する。**適用対象: Pipeline / Guard / Gate 型 skill のみ。knowledge skill・reference skill には強要しない。**
- 検証: skill-patterns.md の Pipeline セクションに追記行が存在すること

---

## Validation-only Follow-up

該当なし。Anthropic 公式 baseline と dotfiles の drift で訂正が必要な箇所は検出されなかった。

---

## Meta-findings

### 1. Opus Pass 2 での false-positive Already 量産

Pass 2 で Opus が H7 / H20 / H22 / H24 / H39 について「Already」と判定したが、Codex 批評で実装 Gap が明確になった。特に H7 (run_eval.sh の folder load 未実装) は最も重要な Gap であり、Opus が「SKILL.md が存在する」という表層的な確認で Already と誤判定した典型例。

**教訓**: 「ファイルが存在する」≠「機能が実装されている」。Pass 2 の Already 判定は実装詳細まで追うべきであり、Codex 批評はその誤りを修正する重要なゲート。

### 2. Codex 批評の必要性

H7/H20/H22/H39 の false-positive を Codex が全て検出した。Codex の「狭く深い」注意特性 (codex_attention_depth.md) が、Opus の「広く浅い」Pass 2 との相補関係として機能した。

### 3. Gemini grounding の出典精査

H18 (Subagent Inheritance) と H39 の `## Critical` 全必須化は community 推測由来の可能性がある。Gemini grounding でも gitconnected.com / agentskills.io 由来の情報は Anthropic 公式 PDF の記載と区別して扱う必要がある。「PDF に記載あり」と「community で語られている」を明確に分離することが grounding の誠実さにつながる。

### 4. 1 次情報源の価値と限界

Anthropic 公式 PDF は 1 次情報源として重要だが、PDF 発行日 (2026-01-27) 以降の API 変更は反映されていない。dotfiles の skill 設計優位 (5D Score / Gotchas / negative routing / tool scoping) は公式ガイドに記載がなくても維持する。公式 baseline は「最低水準」であり「最高水準」ではない。
