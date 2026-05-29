---
title: "14 Claude Code sub-agents I built in 60 days, 4 survived — absorb 分析"
date: 2026-05-30
source_type: blog/listicle (個人実験記録)
source_title: "14 Claude Code sub-agents I built in 60 days, 4 survived. The other 10 just burned tokens."
family: subagent-design (未登録 family / claude-code-tips 隣接)
status: implemented
adopted: 1  # 記事由来 novel (#10 named anti-pattern)。#6 は discoverability 統合
validation_only: 1  # agent count drift 33→22 訂正
phase_2_5: codex (read-only) + gemini (grounding) 並列実行済
---

# 14 sub-agents / 4 survived — absorb 分析

## Source Summary

個人の 60 日実験記録。47K LOC TypeScript リポジトリでサブエージェントを 14 個作り、4 個だけが生存（直近 7 日に 4 回以上呼ばれたもの）。

**主張**:
- サブエージェントは 1 起動 ~20K token のオーバーヘッドを背負う
- 生存 3 条件: (1) 単一責任 (one verb) (2) 境界のある入力 (3) 観測可能な出力 (事前にスキーマを書ける)
- 作成前 7 問 go/no-go チェックリスト
- 死因: 決定的 CLI (npm audit/tsc) のラッパー化 / 逐次タスク / 親が既に持つ文脈の再取得 / runtime データ不在 / 些末タスク / 共有ファイル協調
- 監査するとチームのサブエージェントの 60-70% は削除できる

## Phase 1.5 Saturation Gate

- 登録 4 family のキーワード閾値は未達 → 該当 family なし扱い (PASS)
- ただし隣接領域 (30-subagents-2026 / multi-agent-coordination / MoE / PostHog) に過去 absorb 複数。採用率は健全 (>20%) で dead-weight ループではない
- **判定: PASS** + 「30-subagents-2026 (2026-05-02) と強く重複」を Phase 2 で重点突合

## Pass 1/Pass 2 Judgment

| # | 手法 | 判定 | 根拠 |
|---|---|---|---|
| 1 | 20K spawn overhead | Already | `subagent-delegation-guide` 3-4x オーバーヘッド / 5分以内→直接実行。20K は community 値で公式裏付けなし (Gemini) |
| 3 | 単一責任 / one verb | Already | `agent-design-lessons §3,5` + `codex-subagents.md` |
| 4 | 境界のある入力 | Already | delegation Mental Test「結論だけで十分か」 |
| 5 | 観測可能な出力 | Already | Return Contract (token budget) + `code-reviewer` COMPLETION CONTRACT + `agent-invocation-logger.py` |
| 8 | read-only ツール | Already | `tool-scoping-guide.md` + `disallowedTools` |
| 9 | モデル振り分け | Already | `model-routing.md` |
| 11 | 逐次タスク回避 | Already | Task Parallelizability Gate / Sequential 原則 |
| 12 | 親文脈の再取得回避 | Already | Context Inheritance Policy |
| 13 | count ceiling | Already | Subagent Count Ceiling (但し count drift あり、後述) |
| 14 | Self-Rejection | Already | Self-Rejection Rule Pattern (codify 済) |
| 10 | 決定的 CLI を subagent 化しない | **Gap (modest)** | 原則は `agent-design-lessons:261` 等で済。**named anti-pattern としての表札のみ novel** |
| 6 | 作成前 go/no-go 7問 | **Partial (discoverability)** | 判断基準は全て既存に分散。新ゲートではない |
| 2 | 生存メトリクス (7日4回) | N/A | harness-stability 30日評価 + dead-weight-scan-protocol でカバー。記事数値は n=1 恣意的 |
| 7 | YAML テンプレート | N/A | `agent-config-standard.md` 既存 |

## Phase 2.5 (Codex + Gemini)

**Codex (read-only, file:line 根拠付き)**:
- #10 は novel ではない (`agent-design-lessons:261` static→mechanism, `delegation:1039/1141` 1-2 unit→直接)。価値は短い名前のみ → 1 行で十分
- #6 も既存原則の再編集。価値は discoverability。`docs/playbooks/add-agent.md` Step 0 に薄く統合する程度
- **count drift は #6 より優先度高**: `agent-design-lessons:369` + `docs/wiki/INDEX.md:37` が「33個」、実数 22。Count Ceiling 判断材料の腐敗
- 最終判定「厳密には採用 0 + drift 訂正が正解、最大でも #10 を 1 行」

**Gemini (grounding、楽観バイアス込みで割引)**:
- 20K は community 実測で公式裏付けなし → Already 判定を支持
- 設計 3 原則は 2026 標準 → Already 支持
- Agent Teams (2026.02) / A2A を新潮流として確認 (既存 `managed-agents-*.md` でカバー)
- 記事の具体例を "Acrid project / Drift Checker" と hallucinate (記事原文と不一致、割引)

## Adopted (実装済 S 規模)

1. **#10 named anti-pattern** — `subagent-delegation-guide.md` Anti-patterns 表に 1 行追加（決定的 CLI ラッパー禁止）
2. **#6 discoverability** — `docs/playbooks/add-agent.md` に Step 0 go/no-go preflight 追加（CLI/親文脈/逐次/責務重複の 4 チェック）

## Validation-only Follow-up (採用件数に非計上)

| 対象 | drift 内容 | 訂正 |
|---|---|---|
| `agent-design-lessons.md:369,375,377` | agent 実数「33個」(2026-05-02) | 実数 **22個** (2026-05-30、`_archived/` 除外)、余裕 17→28 に訂正 |
| `docs/wiki/INDEX.md:37` | 同上「33個 余裕 17」 | 「22個 余裕 28」に訂正 |

記事の pruning テーマが Count Ceiling の判断材料の腐敗を露出した。

## Rejected

- #2 生存メトリクス (per-agent 7日4回 tracking): harness-stability 30日評価 + dead-weight-scan-protocol で機能カバー、記事数値は n=1 恣意的
- #7 YAML テンプレート: `agent-config-standard.md` 既存

## Meta

- 隣接 family の高成熟度により、想定どおり低収率 (記事 novel 採用は実質 1 件)。Phase 2.5 が私の Pass 2 over-judgment (#10/#6 を Gap/Partial と過大評価) を correctness fix 優先に修正
- Codex が `add-agent.md` の存在 (Pass 1 見落とし) と count drift の 2 箇所目 (INDEX.md) を発見。bias mitigation + context recovery の両効果
