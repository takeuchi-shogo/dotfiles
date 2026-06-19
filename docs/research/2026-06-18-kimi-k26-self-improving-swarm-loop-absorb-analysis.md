---
source: "The Self-Improving Loop: a 300-agent swarm on Kimi K2.6, verified by Opus 4.8"
date: 2026-06-18
family: multi-agent-orchestration + self-improving-loop (cross-family)
status: implemented
adopted: 1
verdict: saturated-but-1-adopt
---

## Source Summary

**主張**: オープンウェイト Kimi K2.6 で 300 並列サブエージェント × 4000 step の swarm を回し、Opus 4.8 を verify gate に置くと self-improving loop が作れるという 10-step playbook。記事は Kimi.ai 自社製品マーケ（DeepSeek アナロジー、$0.95/M 価格訴求）。

**手法**:
1. spec を書け（Prompt-as-PRD）
2. 実行前に decomposition plan を読め
3. wasteful に並列 + bounded context
4. real files 出力
5. honest model で verify（refute only）
6. workflow を skill 化
7. 自前文書を knowledge 化
8. verify feedback を CONSTRAINTS.md に焼け
9. skill replay で複利
10. loop を background agent 化

**根拠**: Kimi K2.6 実行事例（ベンダー自社データ）。外部 benchmark との比較なし。

**前提条件**: 低単価オープンウェイトモデルの大量並列実行が前提。Claude Code harness（API 従量課金 + subagent 階層制限）とは経済的・構造的に異なる。

---

## Gap Analysis（Pass 1: 存在チェック）

| # | 手法 | 判定 | 既存の実装 |
|---|------|------|-----------|
| 1 | spec を書け | Already | `.config/claude/skills/spec/SKILL.md`（/spec Prompt-as-PRD） |
| 2 | plan を読め | Already | `.config/claude/commands/rpi.md` + `PLANS.md` + plan 承認ゲート |
| 3 | 並列 + bounded context | Already | `docs/adr/0003-multi-model-orchestration.md`（Orchestrator-Subagent）+ Workflow parallel() |
| 4 | real files 出力 | Already | /spec OUTPUT + code-reviewer.md の COMPLETION CONTRACT（structured output） |
| 5 | honest model verify | Already | `.config/claude/agents/codex-reviewer.md`（異種モデル Review Gate）+ Generator-Verifier パターン |
| 6 | workflow を skill 化 | Already | `.config/claude/skills/skill-creator/SKILL.md` + promote-learnings + retrospective-codify |
| 7 | 自前文書 knowledge 化 | Already | `.config/claude/skill-data/memory-vec/`（KNN 意味検索）+ obsidian-knowledge |
| 8 | verify feedback 恒久ルール化 | Already | `.config/claude/skills/promote-learnings/SKILL.md`（learned 昇格ループ、patterns.jsonl → CLAUDE.md rules） |
| 9 | skill replay 複利 | Already | skill chain メタデータ + skill-creator（専用ファイル不在、KISS） |
| 10 | loop を background 化 | Already | `scripts/runtime/nightly/launchd-install.sh` + nightly バッチ群 + Routines |

記事固有の novel = Kimi K2.6 製品（300 agents/$0.95M）のみ → Claude Code harness では N/A。

---

## Saturation Gate 判定

- 合算 N ≈ 14 件目（multi-agent-orchestration N≥6 + self-improving-loop N≥13）
- 最近接 twin: 2026-06-12 fable5-14steps（6 日前、Gap 0）
- **判定: SATURATED-pure-rehash**（delta=0）
- user は continue を選択しフル workflow 実行

---

## Phase 2.5 セカンドオピニオン（Codex + Gemini 並列）

**Codex（gpt-5.5、read-only）**: 「10 項目 Already 判定はほぼ妥当。採用するなら 1 個だけ — cost-arbitrage の条件付きルール。それ以外は採用 0 で妥当。Kimi の差分は手法でなく安価大規模実行の経済性。」

**Gemini（grounding）**: 「Generator-Verifier / Best-of-N は AlphaCode 時代からの標準パターン。Kimi の新規性は製品パッケージング。主観タスクは凡庸な平均値に収束し失敗、verification がボトルネック。SWE-bench で Llama3 8B 250 並列がテストゲートで GPT-4o を凌駕する事例は標準化。」

**Opus 統合**: B（refute-only gate）は `feedback_review_readonly` + gate-not-suggestion + Critic Evasion 耐性で Already。A（cost-arbitrage）のみ borderline だが経済前提が transfer しない（無料 open-weight runner 不在）。user 判断で 1 件採用。

---

## Integration Decisions

### 採用（1件）

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| A | Cost-Arbitrage パターンを `best-of-n-guide.md` に追記 | 採用（S 規模、実装済） | delta=0 の中で唯一 borderline。既存ガイドの「適用条件」節に小節追加で局所変更に収まる |

### 不採用

| # | 項目 | 理由 |
|---|------|------|
| 1–10 | 手法コア全件 | 全 Already（実地検証 + 異種 2 モデルで確認） |
| B | refute-only gate | Already（review-readonly + gate-not-suggestion） |
| Kimi 製品固有 | 300 agents/4000 steps/open-weight 価格 | N/A（Claude Code harness では経済前提が不成立） |

---

## 実装済み変更

**`.config/claude/references/best-of-n-guide.md`** の「適用条件（厳格化）」直後に `### Cost-Arbitrage（安価生成 + 高価 verify-only）` 小節を追記。

条件: 生成が低単価 + deterministic verifier 存在 + p < 0.3 のときのみ cheap workers N≥3 → high-reasoning verifier は refute/select のみ → winner merge。主観評価・高単価生成では通常の階層 routing を使う。

---

## 教訓

- **6 日前 twin（Gap 0）でも user が continue を選んだ場合の価値**: delta=0 の台帳照合が hallucination でないことを Sonnet Explore で裏取りできた。「経済前提が transfer しない」という明確化も異種 2 モデルを通じて得られた。
- **ベンダー記事の読み方**: 手法レベルでは AlphaCode 時代からの標準パターンの再パッケージ。差分は製品の経済性（価格・スケール）にあり、手法の新規性を過大評価しない。
- **family 横断 absorb の構造的天井**: multi-agent-orchestration × self-improving-loop の交差領域は N≥14 で飽和。次回同 family は Phase 1 で固有名詞（著者/製品名）を直 grep → rehash 確認 → reference-only 短絡が適切。
