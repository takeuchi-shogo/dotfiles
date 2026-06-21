# Skill Audit Grader Quota — Design Note

**Date**: 2026-06-21
**Status**: Draft (recommendation, not yet implemented)
**Source**: [2026-06-20 audit](../benchmarks/2026-06-20-audit.md) Open Question #4 + #5

## Problem

`/skill-audit` の A/B benchmark フェーズで、subagent から起動した `compare.sh` が `claude -p` を呼ぶ際に **親セッションの quota を共有して枯渇する**。2026-06-20 監査では 4 subagent 並列で `subagent_tokens` 335–520 (実質ゼロ) で全件失敗、12 grade 中 3 件のみ partial が残った。

同じ failure mode は 2026-05-27 監査でも記録済 ("subagent-driven A/B runs stalled at watchdog due to nested `claude -p`")。構造的に未解決。

## なぜ起きるか

```
parent Claude Code session   ← quota pool
  ├─ Agent(subagent)         ← 同じ quota pool
  │   └─ Bash: run_eval.sh
  │       ├─ claude -p (with_skill)   ← 同じ quota pool ← 並列で N 倍消費
  │       └─ claude -p (without_skill) ← 同じ quota pool
  └─ Agent(subagent) × 3      ← さらに並列
```

`claude -p` は Anthropic API の同じ subscription quota を消費するため、subagent N × evals M × arms 2 = N × M × 2 倍の token を一気に消費する。

## 選択肢

### A. シリアル化 (subagent ループを 1 つに)

`/skill-audit` の Step 3 を 4 件 → 1 件ずつ順に subagent 起動に変更。

- 利点: 既存スクリプト無変更、quota 圧迫が 1/N に。
- 欠点: 壁時計 4× 遅い (10 min → 40 min)。
- 工数: SKILL.md の "Scale-Aware Execution" 表を変更するだけ。S。

### B. 単一 subagent で全 4 件直列処理

「4 subagent 起動」ではなく「1 subagent が 4 skill を順に処理」に変更。subagent 内で `claude -p` 起動は 1 つずつ。

- 利点: subagent 起動オーバーヘッドも削減 (token / 時間)。
- 欠点: 進捗が見えにくい、1 件失敗で全停止リスク。
- 工数: SKILL.md ワークフロー書き換え。M。

### C. grader を Haiku に切り替え (`--model haiku`)

`compare.sh` の `claude -p` 呼び出しに `--model haiku-4-5` を渡し、grader だけ低コストモデルにする。

- 利点: with_skill / without_skill の生成は通常モデル、評価のみ Haiku で quota 圧迫激減 (~10×安価)。
- 欠点: 判定品質が落ちる可能性 (実測必要)。
- 工数: `compare.sh` 1 行追加 + reasoning effort 検証。S。

### D. grader を Codex `gpt-5.5` に切り替え

Codex CLI で評価を回す。Anthropic quota から独立。

- 利点: Anthropic quota とは独立、Codex の深い推論で判定品質向上の可能性。
- 欠点: **Claude Code Bash tool から Codex は到達不能** (TTY 不在 / silent exit — memory feedback_codex_bash_tool_unreachable.md)。bounded timeout + 短プロンプトで動くケースもある (2026-06-20 実証) が不安定。
- 工数: compare.sh 全面書き換え + Codex 経路の安定化検証。M-L。

### E. grader を Gemini に切り替え

Gemini CLI で評価を回す。

- 利点: 1M context、Anthropic quota とは独立。
- 欠点: **`gemini -p` は 2026-06 時点で IneligibleTierError** (Code Assist for individuals sunset — memory feedback_gemini_cli_sunset.md)。Antigravity 移行が必要。
- 工数: 経路再開待ち。N/A 現時点。

## 推奨

**A (シリアル化) + C (Haiku grader) を組み合わせる** が最小手数で最大効果。

| 軸 | 効果 |
|---|---|
| quota 消費 | 並列 4× → 直列 1× (A) + grader 1/10 (C) = ~40× 削減 |
| 壁時計 | 4× 遅延 (10 → 40 min) を許容 |
| 判定品質 | Haiku grader の品質を 2-3 件で実測してから本採用 |
| 実装 | SKILL.md 1 行 + compare.sh 1 行 = S |

Codex (D) / Gemini (E) は本道の解だが、現時点では transport が壊れていて頼れない。A+C で凌ぐ。

## 次のステップ (not in this PR)

1. `compare.sh` に `--model haiku-4-5` オプションを追加 (env var or flag)
2. `skill-audit` SKILL.md の Step 3 "Scale-Aware Execution" 表を直列前提に変更 (3-6 は serial, 7+ は 2 batch × serial)
3. Haiku grader で 3 件の grading を実行し品質を Opus grader と比較 (calibration run)
4. 問題なければ default を Haiku、Opus は `--high-stakes` flag で opt-in に

## 関連メモリ

- `feedback_codex_bash_tool_unreachable.md` — Codex Bash 到達不能
- `feedback_gemini_cli_sunset.md` — Gemini CLI sunset
- `feedback_model_fable_classifier_outage.md` — model 切替の副作用
