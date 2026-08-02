---
title: Codex を Sol オーケストレータ + Luna Max worker に組む (X @Tz_2022 / @antonioleivag)
date: 2026-08-02
status: light-phase2-only
family: multi-agent-orchestration
source:
  - https://x.com/Tz_2022/status/2083568833164419449
  - https://x.com/antonioleivag/status/2083583482375065731
---

# Codex orchestrator-worker subagent absorb

## Source Summary

2 本とも同じ主張。Codex の中で `gpt-5.6-sol` をメインに残してオーケストレータにし、
`~/.codex/agents/luna-worker.toml` に `model = "gpt-5.6-luna"` の custom agent を定義して
worker に回す。境界の明確なサブタスク (コードレビュー、モジュール分析、独立実装、テストデバッグ)
を worker に渡し、メインのコンテキスト汚染を減らす。設定作成は Codex 自身に依頼し、
バージョン互換確認・diff 表示・有効性確認までやらせる。

コメント欄に有力な反論が複数ある。

- @IFITALEX: 実測で Luna Max の総合効率は sol medium を大きく下回った
- @defaiscope: subagent 実行後の復核こそが本当のコスト。細かく割るほど復核回数が増える
- @TheAngryPit: max より xhigh。max は出力トークン 2 倍、コスト 2 倍、ttft がずっと長い
- @lamara953: subagent は speed=priority にしかできず、クォータ消費が 2.5 倍
- @hungv47: herdr を使えば custom agent 不要で任意モデルを直接起動できる

## Saturation Gate (Phase 1.5)

family `multi-agent-orchestration` の N≈16 件目。採用率が低く SATURATED 判定。
delta = 3 (novel 1 + ambiguous 2) のため SATURATED-but-novel、user 選択で `light-phase2`。

## per-method 照合台帳 (全 8 手法)

| # | 記事の手法 | verdict | matched_prior |
|---|-----------|---------|---------------|
| 1 | `~/.codex/agents/<name>.toml` に custom subagent を定義 | excluded as rehash | `2026-06-20-jey-build-claude-subagents-absorb-analysis.md` #4「custom subagent = `.claude/agents/` の MD+YAML」。定義ファイルで名前付き agent を宣言する同一概念の Codex 方言 |
| 2 | orchestrator=強モデル / worker=安価モデル | excluded as rehash | 同 report #2「fleet economics・model routing」→ `references/model-routing.md` の Tier 表。役割ごとにモデルを変える同一主張 |
| 3 | worker に「スコープを勝手に広げるな」guardrail | excluded as rehash | 同 report #17「independent+disposable/repeated は委譲」+ `.config/claude/CLAUDE.md`「委譲は task + guardrails + exit criteria で渡す」。委譲時に境界を明示する同一規律 |
| 4 | 設定変更を LLM にやらせ diff / CLI 互換 / **有効性**を確認させる | **ambiguous** | 近いのは `docs/playbooks/codex-config-changes.md:38-43` の最低検証コマンド群だが、あれは静的検証だけで「実際に効いているか」を含まない |
| 5 | worker の effort は `max` でなく `xhigh` | **novel** | prior 4 本に `reasoning_effort` / `xhigh` の grep hit ゼロ |
| 6 | subagent 結果の復核コストが節約分を食う | **ambiguous** | `subagent-delegation-guide.md:760-780`「統合コスト」が近いが、あれは親の認知負荷であり経済的相殺の議論ではない |
| 7 | 弱いモデル worker は手戻りで総合効率が劣る | excluded as rehash | `2026-06-18-kimi-k26-self-improving-swarm-loop-absorb-analysis.md`「経済前提 (無料 open-weight runner) は Claude harness に transfer しない」。安価モデルの見かけの得を疑う同型の警告 |
| 8 | herdr で任意モデルを直接起動すれば subagent 不要 | excluded as rehash | `2026-07-25-herdr-agmsg-orchestration-wall-absorb-analysis.md`。herdr Worker と cmux Worker の境界表として採用済 |

## Phase 2 判定 (delta_methods のみ)

| # | 手法 | 判定 | 根拠 |
|---|------|------|------|
| 4 | config の有効性確認 | **Gap → 採用** | `task validate-configs` は構文と参照整合のみ。ランタイム確認は無い。この欠落が下記 V1-V4 を 5 ヶ月放置させた |
| 5 | effort は max でなく high/xhigh | **Already (ルール存在) + live が違反** | `references/workflow-guide.md:718-729` の effort 表、`references/model-routing.md:109`「default は `high`」。ルールは揃っていて live config だけが `max` だった |
| 6 | 復核コストの相殺 | **Already (強化不要)** | `subagent-delegation-guide.md:760-780` の統合コスト欄 + `:776`「5 分以内ならオーバーヘッドが本体を上回る」。新設は instruction DRY 違反 |

Phase 2.5 (Codex + Gemini 並列批評) は light-phase2 のため省略。
採用判断の根拠が外部記事の解釈でなく自機での実測だったため、第三者批評の必要度が低いと判断した。

## 記事の中核主張は成立しない (実測)

codex-cli 0.144.6 で `spawn_agent` のパラメータを列挙させた:

```
task_name
message
fork_turns
```

`agent_type` が無い。`.codex/agents/*.toml` に custom agent を定義しても選ぶ手段がない。
記事の手順をそのまま実行しても luna_worker は呼ばれない。

## Validation-only Follow-up (記事の framing が露出した実バグ)

| # | 内容 | 証拠 | 対処 |
|---|------|------|------|
| V1 | Codex の名前付き custom agent 機構が現行 CLI に無い | 上記実測 | `negative-knowledge.md` に撤退条件つきで記録 |
| V2 | `.codex/agents/*.toml` 12 個が `~/.codex/` へ未配備 | `nix/home/default.nix:103` は `.codex/AGENTS.md` のみ link。`:114` で `.cursor/agents` は link 済という非対称 | 配備せず削除 (V1 のため配備しても動かない) |
| V3 | 9+ 箇所が「12 個稼働中」と断定 | `.codex/AGENTS.md:121,142` / `codex-subagent-reference.md:11-19` (表題が "Configured") / `docs/playbooks/codex-subagent-usage.md:20-37` / `docs/agent-harness-contract.md:154-155` / `.agents/skills/codex-review/SKILL.md:44-55` ほか | 削除・実測事実に差し替え |
| V4 | 失敗記録が伝播しなかった | `docs/plans/2026-03-17-codex-subagents-improvement.md:410`「custom agent 名 `pr_explorer` / `reviewer` は `unknown agent_type` 扱いとなり、built-in subagent へフォールバックした」`:433`「登録されない理由は未解明」 | 歴史記録として保存 (編集しない) |
| V5 | live `~/.codex/config.toml` の drift | `model`: luna vs sol / `effort`: max vs high / `review_model`: `gpt-5.5` vs `gpt-5.6-terra` | dotfiles 側に収束 |
| V6 | hooks 二重定義 warning | `warning: loading hooks from both /Users/takeuchishougo/.codex/hooks.json and /Users/takeuchishougo/.codex/config.toml; prefer a single representation for this layer` | config.toml 側の pilot ブロック (echo だけの NO-OP) を削除 |

## 採用 (1 件) / 棄却 (7 件)

採用は #4 のみ。`change-surface-matrix.md` に「agent に設定を書かせたら diff / 形式互換 / **有効性** の 3 点を確認する」を追記した。
残り 7 件は rehash か Already。

記事から得た新規ルールは 1 件だが、記事の framing で照らした結果 6 件の drift/実バグが出た。

## 教訓

**「配線されているか」を検査しない限り、ドキュメントは自分で自分を強化する。**

2026-03-17 の時点で「custom agent が登録されない」ことは実地テストで判明していて、
plan doc に正直に記録されていた。にもかかわらず後続の 9 ドキュメントは
その記録を読まずに「12 個 configured」と書き、互いを参照して確からしさを上げていった。
`codex-subagent-reference.md` の表題は "Configured Custom Agents" で、
`2026-04-29-symphony` の absorb は「`reviewer` / `security_auditor` 12 read-only agents で実装済み」と
Already 判定の根拠に使っている。存在確認が品質保証に化けた典型
(`feedback_absorb_already_deepdive.md` と同型)。

検査器は 1 行で足りた。CLI にパラメータ名を列挙させるだけでよかった。
