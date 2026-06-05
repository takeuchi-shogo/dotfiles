---
source: "When AI builds itself (Anthropic Institute, recursive self-improvement)"
url: "https://www.anthropic.com/institute/recursive-self-improvement"
date: 2026-06-05
status: light-phase2-adopted
family: self-evolving-self-improving-agents
adopted: 3
---

## Source Summary

**主張**: AI が AI 開発自体を自動化しつつあり (>80% の本番コードが Claude-authored、コード最適化 ~52x、研究方針判断で Mythos が人間に 64% 勝利)、「再帰的自己改善 = AI が後継を設計・改良する」軌道に乗りつつある。完全な再帰的自己改善はまだ未到達だが、想定より早く来る可能性があり、制御喪失・検証困難・協調不能のリスクを伴う。

**手法 (記事の能力軸)**:
- コード生成/実行の自律化 (agent がファイルを書き・他 agent に委譲)
- 実験自動化 (測定可能ゴールで仮説検証を反復)
- 研究自律性 (open-ended な研究を提案・実行、parallel agent 間で知見共有)
- 判断力の改善 (next-step 判断を評価、研究 taste で人間に勝ち始める)

**根拠**: SWE-bench saturation、CORE-Bench 20%→saturation (15ヶ月)、task time horizon が4ヶ月で倍化、社内で8倍のコードマージ/日、Mythos 51%→64% で人間の研究方針判断を上回る。

**前提条件**: AI が強いのは「明確な成功指標を持つ well-specified task の実行」。人間が保持するのは「研究 taste・問題選定・方針設定・結果の信頼性判断」(inspiration vs perspiration)。協調/検証層は frontier lab・政策スケールの議論。

## Saturation Gate (Phase 1.5)

- **Family**: self-evolving/self-improving agents, **N≥9** (autocontext-recursive / self-evolving-claude-code / subconscious-agent / skill-eval-loop / empirical-prompt-tuning / self-healing-harness / skillopt / ai-tech-researcher / muse-autoskill)
- **採用率**: 過去は技法系で大半 Already。本記事は **性質が異なる** (実装手法ではなく macro/safety/governance 論考)
- **判定**: SATURATED-but-novel (delta≥3)。ユーザーが「実現案を出して」と明示指示のため gate skip、light-phase2 で novel delta のみ検証

## Gap Analysis (per-method 照合台帳)

| # | 記事の論点 | verdict | matched_prior (3点) / Pass2 判定 |
|---|---|---|---|
| 1 | コード生成/実行の自律化 | rehash | `memory/autoevolve_details.md` の「4層ループ」+ multi-model routing。>80% は到達領域 |
| 2 | 実験自動化 (測定可能ゴール反復) | rehash | `2026-04-09-skill-eval-self-improving-loop` + `2026-04-10-universal-verifier` の動的ルーブリック/two-pass |
| 3 | 研究自律性 (open-ended・agent間共有) | rehash | `2026-06-04-ai-tech-researcher` + `/research` 並列 + dispatching-parallel-agents |
| 4 | **判断力の計測 (Mythos 51%→64%)** | **ambiguous → Gap** | 「Humans steer, agents execute」原則は Already だが、**AIの方針判断が自分に追いついているか時系列計測する機構は不在**。decision/timekeeper skill はあるが human-vs-AI judgment duel の記録なし |
| 5 | 検証/協調インフラ (verifiable pause, detectability) | **novel → policy層 N/A** | 多国間 lab 協調は個人 harness に N/A。「監査可能・可逆・freeze」の個人版のみ翻訳可 |
| 6 | **制御喪失 (世代跨ぎで misalignment 複利化)** | **novel → meta-safety Gap** | AutoEvolve の master直変禁止/3ファイル/3連続reject停止 (`improve-policy.md` Rule 17-19) は単一サイクル規律。**安全機構ファイル自体を進化ループが改変できるか + 累積 drift** は未防御。グローバル circuit-breaker も不在 (`freeze` skill は session の Edit ガードであって cron 停止ではない) |
| 7 | **人間レビューが速度ボトルネック化 (自動レビューが本番バグの1/3捕捉)** | **novel → 非対称性 Gap** | Codex Review Gate は有るが**捕捉率の計測がなく、生成だけ自己改善して検証は固定**。未レビュー drift が非対称蓄積 |

## Integration Decisions

| # | 項目 | 判定 | 理由 |
|---|---|---|---|
| 4 | A: 判断 frontier 計測ループ | **採用 (S)** | 記事の核心 (taste は最後の人間領域だが追いつかれつつある) を自分の harness で定量化。委譲境界の根拠が観測可能になる |
| 6 | B: メタ安全層の自己改変防御 | **採用 (M)** | 単一サイクル規律はあるが多サイクルの緩慢な安全侵食が無防御。制御喪失の個人スケール対策 |
| 7 | C: 検証側の自己改善 | **採用 (M)** | 生成と検証の自己改善を対称化。記事の非対称リスクを mechanism で封じる |
| 5 | 多国間協調/verifiable pause | **N/A** | frontier lab/政策スケール。個人 harness に翻訳不可 (silently 落とさず明示棄却) |

## Plan

→ `docs/plans/active/2026-06-05-rsi-governance-frontier-plan.md` (L規模、A+B+C 統合)

## 残す洞察

- **非対称の発見**: あなたの harness は「実行 (execution) の自己改善」に重投資済 (AutoEvolve/tech-researcher)。記事が照らす未踏領域は「判断の計測」と「メタ安全層の保護」。realization の次段階はこの非対称を埋めること。
- **記事の policy 層は N/A だが、その core 概念は個人版に翻訳できる**: verifiable pause → グローバル circuit-breaker + 監査可能 ledger、loss of control → meta-safety 保護ティア、review bottleneck → 検証側の自己改善。
- **family N≥10 だが「実装手法 absorb の飽和」≠「安全性視点の飽和」**。過去9件は全て「どう自己進化するか」で、「自己進化が壊れるとき何が起きるか」を扱ったのは本記事が初。棚卸し角度の採用価値あり。
