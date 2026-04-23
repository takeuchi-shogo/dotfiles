---
source: "A Closer Look at Harness Engineering from Top AI Companies (AlphaSignal)"
date: 2026-04-24
status: integrated
integration_target: docs/plans/active/2026-04-19-harness-everything-absorb-plan.md (M2 subtasks)
related_absorb: 2026-04-19-harness-everything-absorb-analysis.md (重複度高。独自 contribution 3 点のみ採択)
---

## Source Summary

**主張**: 「If you're not the model, you're the harness.」2026 年は harness engineering が技術的・経済的 moat。同じモデルでも harness 次第で性能が劇的に変動 (LangChain Terminal Bench 2.0 で GPT-5.2-Codex が 52.8% → 66.5%、+13.7pt)。Vercel はツールを 80% 削除して性能向上。Opus 4.7 の self-verification により harness の一部は model に吸収され「2ヶ月で dead weight 化」するリスクがある。

**手法**（抽出）:
- OpenAI: Map not Manual、Strict Dependency Flow (Types→Config→Repo→Service→Runtime→UI)、Distributed AGENTS.md、Codex-written Linters
- Anthropic: Planner/Generator/Evaluator 分離 (GAN 式)、Meta-harness (brain/hands/session decouple + durable event log)、Managed Agents beta (April 9, 2026)
- ThoughtWorks: Guide×Sensor × Computational×Inferential 4軸分類、Harnessability (tech stack の agent-friendliness)
- LangChain: Reasoning Sandwich (plan=high, build=reduced, verify=high で 66.5% vs 全段 max=53.9%)
- 共通: Build to Delete / Temporariness (harness は model capability gap への一時的な賭け)

**根拠**:
- LangChain Terminal Bench 2.0: same model, harness 差で +13.7pt
- Vercel: tool 80% 削除で性能向上
- OpenAI Sora Android: 4 engineers × 28 days、99.9% crash-free、Codex が PR 70%
- Anthropic Managed Agents: 構造化ファイル生成 +10pt、$9 solo broken vs $200 managed working (22x cost)
- Opus 4.7 release (April 16, 2026): SWE-bench Verified 80.8% → 87.6%、CursorBench 58% → 70%、self-verification 追加

**前提条件**: OpenAI approach は大規模既存リポ向き (greenfield 弱)、Anthropic multi-agent は品質重視で cost 22x 許容が必要、ThoughtWorks framework は語彙のみで turnkey でない。個人 dotfiles 環境では Sora スケール事例は直接移植不可。

---

## Gap Analysis (Pass 1: 存在チェック)

Sonnet (Explore) 委譲結果を基に判定。

| # | 手法 | 判定 | 主要ファイル | 詳細 |
|---|------|------|-------------|------|
| 1 | Reasoning Sandwich | partial | `.config/claude/references/model-routing.md:7-14` / `docs/adr/0003` | Codex reasoning effort 制御あり、stage 別自動配分なし |
| 2 | Map not Manual | partial | `docs/adr/0004`, `docs/adr/0006:1-40` | pre-commit deterministic block あり、層間依存強制は未実装 |
| 3 | Strict Dependency Flow | partial (修正) | ADR-0001/0006 部分カバー | 「どこで止めるか」整理済みだが layer import 強制は未実装 |
| 4 | Distributed AGENTS.md | exists | root + `.codex/AGENTS.md` + `.config/claude/CLAUDE.md` | tool 別分散あり、module 密度まで降りていない |
| 5 | Agent-written Linter | partial | `2026-04-19 plan M2` | 自動生成は planning 段階 |
| 6 | Planner/Generator/Evaluator 分離 | partial | product-reviewer / design-reviewer 並列 | 単方向審査のみ、GAN 式フィードバックなし |
| 7 | Meta-harness | partial | Managed Agents research 済 | SDK 未導入、ローカル checkpoint はファイルベース |
| 8 | 4軸分類 (Guide/Sensor × Comp/Inf) | gap | ADR-0006 3 分類と**直交** | harness 全体の設計語彙として追加価値 |
| 9 | Harnessability | partial (修正) | — | CLI/docs/config の agent-friendliness として Q3/M1 に接続可能 |
| 10 | Build to Delete | partial | CLAUDE.md core_principles, `harness-stability.md` | 30 日評価は Q1 で計画、model 吸収追跡なし |
| 11 | Tool Deletion Pattern | partial | improve-policy.md | Vercel 80% は reference data |
| 12 | Behavior Verification | partial | `/validate` + product-reviewer | 自動 acceptance criteria コンパイラは未実装 (記事も未解決と認定) |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | model-routing.md reasoning effort | Reasoning Sandwich 定量データ (+13.7pt) | Codex Spec/Plan Gate + Review Gate に stage 別推奨 budget **手動チェックリスト** を pin | 強化可能 (自動化不要) |
| S2 | root + tool 別 AGENTS.md | OpenAI の per-module 密度 | ADR-0007 thin+thick と照合し密度評価。現状で足りている判断 | 強化不要 |
| S3 | product/design-reviewer 並列 | Playwright behavior eval の欠落 | ui-observer + Playwright MCP の接続は Opus 4.7 self-verification 出現で価値低下中 | 強化不要 (model 吸収) |
| S4 | CLAUDE.md Build to Delete + harness-stability 30d | Opus 4.7 による **harness dead-weight 吸収** (時間圧強) | dead-weight-scan に `superseded_by_model: <version>` タグ追加、evaluator 系 skill/hook に capability overlap 注記 | 強化可能 (最優先) |

## Phase 2.5 Refinement (Codex 批評反映)

Codex (`codex-rescue` subagent, reasoning high) が以下を指摘:

1. **(3) Strict Dependency Flow を Gap → Partial に降格**: ADR-0001/0006 で部分カバー済み
2. **(8) 4 軸分類は Gap のまま正しい**: ADR-0006 3 分類とは orthogonal (hook 採用基準 vs harness 全体設計)
3. **Reasoning Sandwich の stage-aware 自動化は不要**: 運用複雑性が増える。**手動チェックリスト pin** が適切
4. **Opus 4.7 dead-weight 吸収 (B) が最優先**: 時間圧が最も強い。A (Sandwich) / C (4軸分類) は棄却候補だったが、ユーザー判断で全3点採択
5. **プラン統合方針**: 新規 plan 不要。2026-04-19 M2 の **subtask merge** が最小衝突

Gemini の周辺知識補完は 15 tool uses / 15 分で empty return、今回は Codex 批評のみで判断。

## Integration Decisions

### Gap / Partial 採用

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 8 | ThoughtWorks 4 軸分類 | **採用 (Task C)** | ADR-0006 補助 Appendix として語彙追加。最小変更で harness 全体の設計語彙が手に入る |
| その他 Gap/Partial | — | スキップ | 2026-04-19 plan で既にカバー済、または Opus 4.7 self-verification で価値低下 |

### Already 強化採用

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | Reasoning Sandwich 手動チェックリスト | **採用 (Task A)** | Codex Spec/Plan Gate 呼び出し時の stage 別 budget 推奨を 1 箇所に pin |
| S4 | dead-weight-scan `superseded_by_model` タグ | **採用 (Task B、最優先)** | Opus 4.7 吸収時間圧強。M2 subtask merge |
| S2, S3 | — | スキップ | 強化不要 / Opus 4.7 で価値低下 |

## Plan

**統合先**: `docs/plans/active/2026-04-19-harness-everything-absorb-plan.md` の Wave 2 / M2 セクション末尾に subtask 3 件を merge。

### Task A — Reasoning Sandwich 手動チェックリスト pin

- **Files**: `.config/claude/references/model-routing.md` 末尾 に「Stage 別 reasoning budget 推奨表」追加
- **Changes**:
  - plan=high / build=medium / verify=high の表を追加
  - 出典: LangChain Terminal Bench 2.0 data (52.8% → 66.5%、全段 max=53.9%)
  - Codex Spec/Plan Gate 呼び出し時の任意チェックリストであることを明記 (強制ではない)
- **Size**: S (1 ファイル、追加 section のみ)

### Task B — dead-weight-scan に `superseded_by_model` タグ追加 (最優先)

- **Files**: `docs/plans/active/2026-04-19-harness-everything-absorb-plan.md` の M2 セクション内に subtask 追加
- **Changes**:
  - `scripts/lifecycle/dead-weight-scan.py` の output JSONL schema に `superseded_by_model: <version>` field 追加
  - scan 時は既定で None、手動でタグ付け可能 (Opus 4.7 release 時点で evaluator 系 skill/hook に付与)
  - AutoEvolve Phase 1 の削除提案で、capability overlap がある場合は `superseded_by_model` を理由として提示
- **Size**: S (M2 実装に組み込み、schema 追加のみ)

### Task C — ADR-0006 に 4 軸分類 Appendix 追加

- **Files**: `docs/adr/0006-hook-philosophy.md` 末尾に Appendix 追加
- **Changes**:
  - ThoughtWorks の Guide×Sensor × Computational×Inferential 4 軸分類を紹介
  - 3 分類 (Deterministic Block / Semantic Advisory / Human Judgment) とのマッピング例
  - 例: `protect-linter-config.py` = Computational × Guide (Deterministic Block)、`codex-reviewer` = Inferential × Sensor (Semantic Advisory)
- **Size**: S (1 ファイル、Appendix section のみ)

**総規模**: S × 3 (3 ファイル、追加のみ)。既存 M2 と併せて 1 日以内で完了可能。

**依存関係**:
- Task A, C: 独立、即実装可
- Task B: M2 本体実装後に subtask として組み込み (B は schema 拡張のみ)

**撤退条件**:
- Task A: チェックリストが無視される/混乱を招く場合は削除
- Task B: `superseded_by_model` タグが手動運用に繋がらない場合は、model version から自動推論する仕組みに差し替え検討
- Task C: 4 軸分類が 3 分類と混乱する場合は Appendix を削除し、単なる reference として残す

---

## References

- 元記事 (AlphaSignal, 2026-04 前後): "A Closer Look at Harness Engineering from Top AI Companies"
- 関連 absorb: `docs/research/2026-04-19-harness-everything-absorb-analysis.md` (重複度高)
- Codex 批評: Phase 2.5 で実施 (`codex-rescue` subagent、reasoning high、84s)
- ADR-0006: `docs/adr/0006-hook-philosophy.md`
- 統合 plan: `docs/plans/active/2026-04-19-harness-everything-absorb-plan.md`
