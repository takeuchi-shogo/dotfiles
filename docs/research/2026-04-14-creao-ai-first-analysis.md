---
status: active
last_reviewed: 2026-04-23
---

# CREAO AI-First Strategy 記事分析レポート

**日付**: 2026-04-14
**ソース**: "Why Your 'AI-First' Strategy Is Probably Wrong" by CREAO CTO
**分析対象**: 個人 Claude Code dotfiles ハーネス (/Users/takeuchishougo/dotfiles)
**フェーズ**: Extract → Analyze (Sonnet Explore) → Refine (Codex + Gemini 並列批評) → Triage → Plan

## Phase 1: 記事要点 (Extract)

### 中核主張
AI-first ≠ AI-assisted。AI-assisted (Cursor/Copilot 追加) は効率 +10-20% 止まり。AI-first はプロセス・アーキテクチャ・組織を全面再設計する。

### Harness Engineering 定義 (OpenAI 2026/02 命名)
エンジニアの主要仕事は「コードを書く」ではなく「エージェントが有用な仕事をできるようにする」。失敗時の問いは "try harder" ではなく "what capability is missing, and how do we make it legible and enforceable for the agent?"

### 主要手法 (10 項目)
1. モノリポ化 ("fragmented codebase is invisible to agents. A unified one is legible.")
2. GitHub Actions 6 段階パイプライン (Verify CI → Build/Deploy Dev → Test Dev → Deploy Prod → Test Prod → Release)。No optional phases. No manual overrides. Deterministic.
3. PR ごとに 3 並列 Claude Opus 4.6 レビュー: (1) code quality (2) security (3) dependency scan。suggestions ではなく gates
4. CloudWatch = central nervous system. "If AI can't read the logs, it can't diagnose the problem."
5. 自己治癒ループ: 9:00 UTC 毎日 Claude Sonnet 4.6 が CloudWatch クエリ → エラーパターン分析 → executive health summary → Teams 配信。+1 時間 triage engine が 9 次元 severity スコア → Linear 自動チケット。dedup + regression 再オープン。修正後 triage engine が再検証 → 自動 close
6. Architect (1-2 人) vs Operator のロール分離
7. Build the testing harness BEFORE scaling agents (順序制約)
8. "We don't fire an engineer for a production bug. We improve the review process." (no-blame improvement)
9. AI-native を全機能 (marketing, release notes, socials) に展開
10. Model capability がクロック (Opus 4.5 → 4.6 で質的変化)

## Phase 2: ギャップ分析 (Sonnet Explore 初回判定)

| # | 手法 | 初回判定 | dotfiles 内の該当 |
|---|------|---------|------------------|
| 1 | harness engineering principle | exists | CLAUDE.md ("Humans steer. Agents execute."), docs/wiki/concepts/harness-engineering.md, docs/agent-harness-contract.md |
| 2 | unified codebase for agent visibility | partial | symlink 統一は自然発生的、明文原則なし |
| 3 | deterministic CI/CD gates | exists | completion-gate.py (MAX_RETRIES=2, no bypass), lefthook, --no-verify 禁止 |
| 4 | parallel review passes | exists | triage-router の 3 並列 (code-reviewer + golang-reviewer + codex-reviewer) |
| 5 | circuit-breaker auto-rollback | partial | completion-gate retry 上限 / AutoEvolve verdict 記録のみ |
| 6 | structured observability | exists | observability-signals.md, session_events.py, error-rate-monitor.py |
| 7 | daily automated health summary | exists | daily-health-check.sh (launchd 21:00) |
| 8 | error triage + severity scoring | partial | failure-clusterer.py, failure-taxonomy.md / "読み手なし" Gap 2 High |
| 9 | dedup + regression reopening | partial | create-issue で gh 類似検出 / 自動再オープン未実装 |
| 10 | feature flags / kill switch | not_found | チーム機能 = N/A |
| 11 | merge queue / stacked PRs | not_found | チーム機能 = N/A |
| 12 | Architect vs Operator split | partial | "Humans steer. Agents execute." 哲学あり / 明示ロール名なし |
| 13 | criticism-first mindset | partial | adversarial-evaluation-criteria.md, gaming-detector.py / pre-mortem checklist なし |
| 14 | no-blame review improvement | partial | CLAUDE.md Foundation "ミスで信頼は壊れない" / 構造化なし |
| 15 | AI-native across all functions | partial | obsidian-content, timekeeper, auto-morning-briefing.sh が点在 |

## Phase 2.5: Refine (Codex + Gemini 並列批評)

### Codex の指摘: Opus が自信過剰に `exists` を付けている

冒頭: 「このギャップ分析は『概念・部品の存在』を『CREAO 記事レベルの運用強制』と取り違えている箇所が多いです」

**判定修正** (exists → partial):
- **#1 harness principle**: 思想 exists、運用 contract partial。"failure → capability gap" を標準処理として強制していない
- **#3 deterministic gates**: 局所的には強いが GitHub Actions 6 段階相当ではない。"local deterministic verification exists" が正確
- **#4 parallel review**: dotfiles は「言語・深さ・モデル」並列。CREAO は「code quality / security / dependency」責務ドメイン並列で性質が違う
- **#6 structured observability**: `observability-signals.md` 自ら「記録のみ、読み取り側なし」と認めている。記録装置であり神経系ではない
- **#7 daily health summary**: summary → triage → ticket → fix verification → close の閉ループが欠落

**見落とし項目 (4 件追加)**:
- **#16 Build testing harness BEFORE scaling agents** (順序制約): dotfiles は agent/skill/AutoEvolve/observability が先に肥大化、後追いで検証面を足している = **逆順**
- **#17 Prompts disposable, systems durable**: 昇格判断基準が散在 = partial
- **#18 SOPs as operational contract** (手順+入力+終了条件+失敗分岐): 単なる skill inventory では弱い = partial
- **#19 Criticism as first-class artifact**: adversarial-evaluation は近いが PR/plan/health loop に流す思想までは弱い = partial
- **#20 No optional phases / no manual override**: completion gate は強いが全工程一本道化ではない = partial

**個人 dotfiles では害になるもの**:
- **自動チケット化**: 注意資源の負債化。条件付き (N 回再発 + 自動修復不能) のみに限定すべき
- **常時 3 Opus レビュー**: コスト/レイテンシ/false positive 過多。risk-based escalation が適切
- **自動 rollback**: 未コミット作業・symlink・local state を壊す。checkpoint + suggested revert patch へ
- **No manual override**: 硬すぎる。override 禁止ではなく override reason の構造化ログへ

**Codex の結論** (抽象原理 4 つ):
dotfiles が取り込むべきは企業儀式ではなく、次の 4 つに絞るべき:
1. 観測可能にする
2. 判断をゲート化する
3. 批評を成果物にする
4. 失敗を capability gap として durable artifact に変える

### Gemini の補強 (別視点)

- OpenAI 2026/02 "harness engineering" 公式発表 URL **未確認**、記事自体も公開検索で未特定 → 一次ソースが弱い
- CREAO モデルは **10-50 人規模での局所最適解** であり普遍パラダイムではない
- AI 生成コードの 2 年目以降の認知負債データ不足、長期保守性の空白
- 代替パラダイム: Swarm Agent 型 / Human-in-the-loop Selection 型 / Deterministic CI/CD + Limited Autonomy

## Phase 3: Triage (選別結果 = フルセット)

### 取り込み: A1 + A2 + A3 + B1 + B3

| 番号 | 項目 | 対応する Codex 抽象原理 |
|------|------|------------------------|
| A1 | Record-only observability を action loop に接続 | 観測可能にする |
| A2 | Review 並列を責務ドメイン並列へ再定義 | 判断をゲート化する |
| A3 | SOP → skill/rule/task 昇格基準を一本化 | 失敗を capability gap として durable artifact に変える |
| B1 | Pre-mortem checklist 新設 | 批評を成果物にする |
| B3 | CLAUDE.md core_principles に 4 原理を明記 | 全原理の基盤 |

### 取り込まない (固定)

- 自動チケット化 (注意資源の負債化)
- 常時 3 Opus レビュー (コスト/FP 過多)
- 自動 rollback (symlink/local state 破壊)
- No manual override (硬すぎる)
- #10 feature flags, #11 merge queue (チーム機能)

## Phase 4: 統合プラン概要

詳細は `docs/plans/2026-04-14-creao-absorb-plan.md` 参照。規模: **L** (7 ファイル変更、1 新規)。

実行順序: B3 (基盤) → A3 (メタレベル) → A1/A2/B1 (並列) → 検証 → /review

## 参照

- Codex 批評全文: /tmp/absorb-codex-out.txt (Codex CLI exec 結果, セッション終了後削除)
- Gemini 補完: セッション内取得、外部保存なし
