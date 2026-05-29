---
title: "You're Not Slow. You're Single-Threaded: Commanding 300 Agents from One Prompt"
date: 2026-05-30
source_type: vendor-article
source_author: anonymous (Kimi team collaboration, disclosed)
source_url: null (text pasted)
topic_family: multi-agent-orchestration
absorb_mode: light-phase2
status: light-phase2-only
adopt_count: 0
gate_decision: PASS (warning) → light-phase2 (user choice)
related:
  - 2026-05-02-30-subagents-2026-absorb-analysis.md
  - 2026-04-11-multi-agent-coordination-patterns-analysis.md
  - 2026-05-22-anthropic-engineers-token-savings-absorb-analysis.md
---

# Single-Threaded / 300 Agents Swarm — absorb 分析 (light-phase2)

## 判定サマリ

**採用 0 件。** multi-agent orchestration 分野の重複領域 (関連 absorb 6 件・採用率高) かつ
Kimi Agent Swarm のベンダー記事 (末尾 Disclosure で team 協働を明示)。
light-phase2 で novel candidate 3 点のみ検証 → すべて Already (強化不要)。Gap = 0。

## Source Summary

### 主張
ソロビルダーの真のボトルネックはモデルの賢さではなく **single-threaded (1 本のキュー)** であること。
解決は「仕事の形」を line (端から端まで歩く) から grid (同時に走る) へ変えること。
orchestrator + 多数の並列 sub-agent (Kimi K2.6 Agent Swarm で最大 300 agent / 4,000 steps) が
そのシェイプを提供する。「どのモデルが最高スコアか」ではなく「どう 4 つのキューを得るか」を問え。

### 手法 (Phase 1 抽出 — 将来の delta 計算用 prior_methods)
1. Orchestrator パターン (lead agent が分解・spawn・watch・stitch)
2. Skill-profile routing (worker を得意 skill でマッチング)
3. Per-worker scoped memory (各 sub-agent が独自 context + 共有 operational space)
4. Auto-recovery (stall/garbage worker を検出して reassign/regenerate)
5. Decompose before delegate (独立に走る部分に分解)
6. Match worker to work (specialist > generalist、research/writing/checking を分離)
7. Design state externally (running brief / pinned summary を人間が保持)
8. Plan for failure on purpose (checking step を追加)
9. Job-shape 見極め (wide+independent+files → swarm / narrow+deep → single agent)
10. Brief like a team (role/goal, scope/guardrails, numbered deliverables, output format)
11. Read the plan before run (orchestrator の分解計画を投入前にレビュー)
12. Verify risky parts first (numbers/citations を人間が検証)
13. Re-run slices not whole job (surgical re-run)
14. Parallelism costs (short/deep task に swarm は逆効果 = "new over-engineering")

### 根拠
Kimi 自社報告: 並列で end-to-end ~80% 短縮 / ~4.5x speedup、ceiling 100+ files / 100k-word review /
20k-row dataset。**すべて vendor figures** で著者自身「My own runs have not touched those ceilings」
「it still gets individual facts wrong. Verify before you act」と caveat。

### 前提条件
ソロビルダー / wide + independent + ファイル成果物のジョブ。Kimi K2.6 固有のスケール (300-worker pool)。

## Phase 1.5 Gate 判定

- topic_family: `multi-agent-orchestration` (taxonomy 未登録だが実質 family、関連 6 件)
- N=6, 採用率 ~100% → 形式判定 **PASS (warning)**、連続 reject trend なし
- ベンダーバイアス + generic 啓蒙 + 事前見立て「ほぼ全て Already」をユーザーに提示
- ユーザー選択: **light-phase2** (novel 論点だけ検証、Phase 2.5 省略)

## Pass 1 / Pass 2 Judgment Table (novel candidate のみ)

事前見立てで Already 確実な 11 手法 (1,2,3,5,6,7,8,9,10,12,13,14 のうち明白なもの) は
Sonnet Explore に投げず、borderline 3 点に絞って検証した。

| # | novel candidate | Pass 1 (Sonnet) | Pass 2 (Opus) | 既存の仕組み / 根拠 |
|---|---|---|---|---|
| 4 | Auto-recovery (failed worker regenerate/reassign) | partial | **Already (強化不要)** | `scripts/runtime/collect-result.sh:78-94` が error pattern 検知 → 自動リトライ (MAX_RETRY=2) → escalate。`failure-escalation-protocol.md` で 2 回失敗時 Issue+worktree。記事の「reassign to *different* worker」は Kimi 300-worker pool 前提で cmux 有限 Worker に **N/A**。「confident-wrong 検出」は記事自身が人間 verify に委譲 (item 12) しており dotfiles の `verification-before-completion` + `codex-reviewer` でカバー済 |
| 9 | Job-shape triage gate (wide/independent vs narrow/deep) | exists | **Already (強化不要)** | `subagent-delegation-guide.md` Task Parallelizability Gate が「embarrassingly parallel vs 逐次推論」を Google Research 2025 実証 (+81% / 並列劣化リスク) 付きで判定。`task-decomposition-guide.md` 分割シグナル (10 ファイル超 / 3 独立変更)、`dispatch/SKILL.md` 6 段階ルーティング。記事主張を完全包含 |
| 11 | Orchestrator plan review-before-run | exists | **Already (強化不要)** | `codex-plan-reviewer.md` (M/L で Spec/Plan/Risk/Human-decision 4 観点批評 + Requires Escalation rubric)、`workflow-guide.md` Plan レビュー gate (M/L 必須)、`research/SKILL.md` Step 2 ユーザー承認必須。dotfiles の方が手厚い |

## Decisions

- **採用: 0 件。** 3 つの novel candidate すべて Already (強化不要)。
- Gap = 0 のため light-phase2 自動昇格 (Gap>=1 で full workflow) に該当せず、Phase 2.5 省略。
- 記事のコア 14 手法は dotfiles の **Workflow tool** (pipeline/parallel/fan-out + `.filter(Boolean)` +
  tool description 内の "Reaching for 300 workers on a one-worker job is the new over-engineering"
  警告まで)、subagent-delegation-guide、model-routing、task-decomposition-guide、
  verification-before-completion、codex-plan-reviewer で網羅済み。
- ベンダー数値 (300/80%/4.5x) は vendor figures につき採用根拠にせず。

## Meta-findings

1. **`multi-agent-orchestration` を topic-family-saturation.md の taxonomy 追加候補**:
   関連 absorb 6 件 (30-subagents / multi-agent-coordination / MoE / PostHog / token-savings / CORAL) で
   「3 件以上の累積実績 + wash-out しない長期パターン」条件を満たす。ただし採用率が高い (~100%) family なので
   gate の主目的 (採用 0 量産の永続ループ検出) には合致しにくく、登録しても PASS warning 止まり。
   → 別途 skill 改善タスクとして検討 (本 absorb スコープ外)。
2. **採用率高 family でも light-phase2 は有効**: 「重複領域だが念のため」を full workflow で回さず、
   borderline 3 点に絞ることで Sonnet Explore 1 回 + Phase 2.5 省略で完結。事前見立ての検証コストを最小化した。
3. ベンダー記事 (Kimi 協働 disclosed) + generic 啓蒙という 2 シグナルは事前見立ての精度を上げる強い指標だった。
