# Warp oz-skills (15 skill) /absorb 分析レポート

- **日付**: 2026-05-07
- **ソース**: https://github.com/warpdotdev/oz-skills (MIT, 2026 公開)
- **形態**: GitHub repo (15 skills, 3,735 LOC, 平均 249 LOC/skill)
- **判定**: 6 タスク採用 (T1-T6 すべて rubric 移植)、規模 M

## 1. Phase 1: 構造化抽出 (Gemini 委譲)

Warp 社 (ADE: Agentic Development Environment ベンダー、ターミナル企業) が 2026 年に MIT で公開した 15 スキル。GitHub-first orchestration 哲学。

**5 カテゴリ:**
1. **Git/GitHub** (4): create-pull-request / ci-fix / github-bug-report-triage / github-issue-dedupe
2. **Data/Analysis** (2): dbt-model-index / analysis-artifacts
3. **Web Quality Audits** (4): web-performance-audit (chrome-devtools-mcp) / web-accessibility-audit (WCAG POUR) / seo-aeo-audit / webapp-testing (Playwright + with_server.py)
4. **Infrastructure** (2): terraform-style-check / mcp-builder ("workflow tools > API coverage" 哲学)
5. **Productivity** (3): docs-update (24h commit scan, Mintlify/Docusaurus 対応) / scheduler (on-device only) / slack-qa-investigate (read-only, verify-first)

**横断哲学:**
- Minimal diff philosophy (ci-fix, docs-update)
- Verify-before-answering (slack-qa-investigate)
- Boundary drawing (scheduler 明示的に cloud 回避)
- CLI-first / MCP pragmatic / Template-first / GitHub Actions automation-ready

**ベンダー文脈:** Warp 内部スタックは dbt + BigQuery、ターゲット = SRE/DevOps/backend、Oz cloud platform への upsell 戦略。

## 2. Phase 2 分析テーブル (修正後)

### Phase 2 Pass 1 (Sonnet Explore) + Pass 2 (Opus 強化分析) + Phase 2.5 (Codex/Gemini 批評反映)

| # | skill | 判定 | 根拠 |
|---|-------|------|------|
| 1 | create-pull-request | **Already 強化可能** | `/create-pr-wait` + `/pull-request` あり。本質は規約自動学習だけでなく「review/CI/testing skill 呼び出し chain + draft 判定 + PR template 反映 + 既存 PR 検出」全体（Codex 指摘） |
| 2 | ci-fix | **Already 強化可能** | `/gh-fix-ci` (mizchi external) あり。本質は `ci-fix/<branch>` 命名ではなく **permissions 拡張禁止 + pull_request_target 回避 + flaky rerun 禁止** （Codex/Gemini 共通指摘） |
| 3 | github-bug-report-triage | **Partial** | `/interviewing-issues` は forward (vague→spec)、inbound bug report 評価は未実装 |
| 4 | github-issue-dedupe | **Partial** | （Codex: Gap → Partial 修正）Warp 実装は軽量 `gh issue list` + keyword 検索 + manual 比較で十分、semantic 不要。"duplicate confidence rubric" 不在のみが差分 |
| 5 | dbt-model-index | **N/A (pattern 横展開価値あり)** | dbt 不在で N/A。ただし grain/join key/cost control を明記する index pattern は dotfiles の skill/memory/scripts inventory に応用可能（Codex 指摘） |
| 6 | analysis-artifacts | **Partial** | docs/research/ あるが analyses/<name>/ 標準化テンプレなし |
| 7 | web-performance-audit | **Partial** | （Codex: Gap → Partial 修正）chrome-devtools-mcp の trace 部分のみ Gap、UI/console 検証は ui-observer/agent-browser でカバー。Gemini: chrome-devtools-mcp は deprecation 圧力あり |
| 8 | web-accessibility-audit | **Partial** | design-reviewer + web-design-guidelines が UX 寄り、WCAG POUR チェックリストなし |
| 9 | seo-aeo-audit | **N/A** | dotfiles 公開 web ではない。Gemini: AEO は 2026 年基準で実証データ薄い |
| 10 | webapp-testing | **Already 強化不要** | agent-browser CLI ベース (アーキ選択済み)。「先に --help」「reconnaissance-then-action」運用文は流用価値あり（Codex 指摘） |
| 11 | terraform-style-check | **N/A** | 個人スタックに Terraform なし |
| 12 | mcp-builder | **Already 強化可能** | skills-lock 経由 ComposioHQ 配布あり。Warp 版は evaluation 10 問作成まで含む = builder 品質 gate（Codex 指摘） |
| 13 | docs-update | **Partial** | `/check-health` は drift detection。24h commit scan は不要、user-facing change → docs drift 提案 rubric が必要 |
| 14 | scheduler | **Already 強化可能** | `/schedule`+CronCreate+ScheduleWakeup あり。本質は cloud agent / local task / reminder の境界質問強制（Codex 指摘） |
| 15 | slack-qa-investigate | **N/A (pattern 横展開価値あり)** | Slack 統合なし。read-only investigation の strict boundary は subagent 方針（db-reader/safe-git-inspector）と相性良い |

**修正後集計:** Already (強化不要) 1 / Already (rubric 強化可能) 4 / Partial 6 / Gap 0 / N/A 4

## 3. Phase 2.5 統合のキー指摘

### Codex (gpt-5.5) の批評

- **#4/#7 過大評価指摘**: Gap → Partial に降格（Warp 実装も軽量・既存仕組みで部分カバー）
- **#10 過小評価リカバー**: Already-不要のままだが「先に --help」「reconnaissance-then-action」運用文は流用価値あり
- **#5/#15 N/A から pattern 横展開価値あり**: dbt model index の grain/cost control / Slack の read-only boundary
- **重要メタ指摘**: 個人 dotfiles では「skill があるか」ではなく「**既存 skill の gate / rubric / boundary に 3-10 行で吸収できるか**」が判定軸。新 skill 追加は token tax で逆効果
- **Top 3 推奨**: T1 ci-fix policy / T2 docs-update rubric / T3 WCAG POUR

### Gemini の周辺知識補完

- ~1M user 主張曖昧（Warp ターミナル全ユーザー or Oz platform 限定？）
- 60% auto PR も Oz limited の可能性
- chrome-devtools-mcp の deprecation 圧力（Lighthouse CLI 1 行 vs MCP ラッパー複雑度）
- ci-fix/<branch> 命名は Git-Flow / trunk-based と衝突
- AEO は 2026 年基準で実証データ薄、Schema.org validator と差不明
- mizchi/skills (既採用) の方が品質・保守度が上位
- Warp は Cloud upsell エコシステム戦略

### Warp 固有バイアスの逆効果リスク

1. GitHub-first automation 入れすぎ → 個人 repo で PR/branch/comment 操作過剰、read-only と write-action の境界が濁る
2. BigQuery/dbt 前提の artifact discipline → 軽い調査まで `analyses/` scaffold 化で Pruning-First に反する
3. Oz/cloud 由来の scheduler/docs automation → ローカル安全境界より「自動実行可能性」が先に立つリスク

## 4. Phase 3: ユーザー選別結果

### 全 6 タスク採用 (Top 3 + 副次 3)

- **T1 (最優先)**: ci-fix policy 文書化
- **T2**: docs-update rubric を /check-health に統合
- **T3**: WCAG POUR チェックリストを既存 UI review へ
- **T4 (副次)**: PR skill chain rubric を /pull-request に追記
- **T5 (副次)**: scheduling-decision-table.md を作成
- **T6 (副次)**: webapp-testing 運用文を references に学習メモ化

## 5. Phase 4: 統合プラン (実装済み)

### T1: ci-fix policy 文書化
- 新規: `~/.claude/references/ci-fix-policy.md`
- 内容: 3 hard rule (permissions 拡張禁止 / pull_request_target 回避 / flaky rerun 禁止) + minimal-diff 規律 + ブランチ運用 + anti-patterns + 撤退条件
- 参照される側: `/gh-fix-ci`, `/create-pr-wait`, `/pull-request`, `build-fixer` agent

### T2: docs-update rubric を /check-health に統合
- 修正: `~/.claude/skills/check-health/SKILL.md`
- 追加箇所: Step 3.8 "User-facing change → docs drift rubric"
- 内容: 5 シグナル分類表 (CLI flag / API signature / env var / breaking change / skill rename) + 検出スニペット + 判定軸の anti-pattern。24h commit scan は導入せず判定軸を 1 本追加するに留める

### T3: WCAG POUR チェックリストを design-reviewer agent へ
- 修正: `~/.claude/agents/design-reviewer.md`
- 既存の Accessibility セクションを WCAG 2.1/2.2 4 原則 (Perceivable / Operable / Understandable / Robust) に再構成
- 追加: P0/P1/P2 severity 分類 + manual testing チェックリスト (キーボードのみ / VoiceOver/NVDA / 400% ズーム / prefers-reduced-motion)

### T4: PR skill chain rubric を /pull-request に追記
- 修正: `~/.claude/commands/pull-request.md`
- Step 0: Pre-PR Chain Check 追加
- 4 サブステップ: 既存 PR 検出 / PR template 反映 / Pre-PR skill chain 推奨 (review/gh-fix-ci/test-engineer/spec) / Draft 判定

### T5: scheduling-decision-table.md 作成
- 新規: `~/.claude/references/scheduling-decision-table.md`
- 3 境界質問 → 5 機構決定表 (ScheduleWakeup / /loop / /schedule / CronCreate / /autonomous) + 選択フローチャート + アンチパターン + クラウド vs オンデバイス線引き

### T6: agent-browser-server-lifecycle.md
- 新規: `~/.claude/references/agent-browser-server-lifecycle.md`
- 2 rule: 「先に --help」「動的 app は reconnaissance-then-action」+ サーバライフサイクル指針 + with_server.py を採用しない理由

### 影響範囲
- 新規ファイル: 3 個 (ci-fix-policy.md / scheduling-decision-table.md / agent-browser-server-lifecycle.md)
- 既存編集: 3 個 (check-health/SKILL.md / design-reviewer.md / pull-request.md)
- 規模: M (6 ファイル touch)

## 6. 撤退条件

採用した rubric / reference が逆効果になった場合の signal:

| 採用 | 撤退 signal |
|------|------------|
| T1 ci-fix policy | 30 日以内に 3 件以上 friction-events で「policy が邪魔した」記録 → ルール緩和 |
| T2 docs-update rubric | 警告が誤検知率 > 50% → シグナル分類表を絞る |
| T3 WCAG POUR | design review で P0/P1 の判別が機能していない → severity 区分削除 |
| T4 Pre-PR Chain | 「PR 作成が遅くなる」苦情 1 回でスキップフロー強化 |
| T5 scheduling-decision-table | 30 日 unread → CLAUDE.md `<important>` に昇格 OR 削除 |
| T6 agent-browser-lifecycle | webapp-testing skill との重複が出たら 1 ファイルに統合 |

## 7. 出典 / 参考

- ソース記事: https://github.com/warpdotdev/oz-skills (MIT)
- agentskills.io: open spec claim (実態は Warp 主導)
- Anthropic 公式 skills (claude-api 含む 13 個)
- mizchi/skills (21 個, 既採用)
- google/skills (13 個, 既採用)
- ComposioHQ/awesome-codex-skills (mcp-builder 配布元)
- Codex 批評（gpt-5.5、aa1a35e36... → ab184f7c... へ追加批評）
- Gemini 周辺知識補完（grounding API quota 超過のため公開情報ベース）
