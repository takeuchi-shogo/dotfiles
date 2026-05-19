---
title: "Claude Code in Large Codebases: Best Practices (absorb)"
date: 2026-05-20
source_type: article
source_author: "Anthropic Applied AI team (Alon Krifcher, Charmaine Lee, Chris Concannon 他)"
source_url: "https://claude.com/blog/how-claude-code-works-in-large-codebases-best-practices-and-where-to-start"
source_published: 2026-05-14
series: "Claude Code at scale 第 1 弾"
absorb_verdict: "D (取り込みなし) — 既存実装が全主張をカバー済。Pruning-First 違反を回避"
adopted_tasks: []
deferred_tasks: []
rejected_main_claims: []
pruning_first_failure: true
key_lesson: "Pass 1 で scripts/runtime/skill-* ディレクトリを直接列挙しなかったため、Task 1/2/3 全て既存重複を Phase 4 直前まで見落とした"
---

## Section 1: 記事の主張 (Phase 1 構造化抽出)

### 記事情報

- **URL**: https://claude.com/blog/how-claude-code-works-in-large-codebases-best-practices-and-where-to-start
- **著者**: Anthropic Applied AI team (Alon Krifcher, Charmaine Lee, Chris Concannon 他)
- **公開**: 2026-05-14
- **Series**: "Claude Code at scale" 第 1 弾
- **fetch_metadata**: route=defuddle, domain=claude.com, trusted=true, visible_chars ~9000

### 核心主張

**Large codebase での Claude Code 成功は model 選択ではなく harness 設計で決まる。** CLAUDE.md / Hooks / Skills / Plugins / MCP の 5 拡張点 + LSP / Subagents 2 capability がパフォーマンスを決定する。

記事の中心文: "The harness is built from five extension points... determines how Claude Code performs more than the model alone."

### 7 コンポーネント (Claude Code Harness)

| # | コンポーネント | 記事の説明 |
|---|--------------|----------|
| 1 | CLAUDE.md files | 毎セッション読み込み。lean かつ階層的 (root → subdirectory) に保つ |
| 2 | Hooks | イベント駆動スクリプト。自動化と継続改善に使う |
| 3 | Skills | タスクタイプ別の再利用可能なエキスパートナレッジ、オンデマンドロード |
| 4 | Plugins | Skills/Hooks/Config をまとめた配布可能バンドル |
| 5 | LSP integrations | シンボルレベルのコードナビゲーション。多言語コードベースで critical |
| 6 | MCP servers | 内部ツール・API との接続 |
| 7 | Subagents | 探索と編集を分離した独立 Claude インスタンス |

### 15 手法 (詳細)

1. Agentic search (RAG インデックスなし) — リアルタイムでファイルを読みリファレンスを辿る
2. CLAUDE.md 階層化 — root pointer + subdirectory init
3. Stop hook による self-improvement
4. Start hook による動的 context 注入
5. Skills の path-scoped progressive disclosure
6. Plugins 配布 (managed marketplace 経由)
7. LSP integration によるシンボルベース検索
8. MCP servers による内部ツール接続
9. Subagents 分離 (探索と編集を別インスタンスに)
10. Subdirectory init (monorepo 対応)
11. Subdirectory 単位での scoped test/lint
12. `permissions.deny` のバージョン管理
13. Codebase map (table of contents)
14. 3-6 ヶ月の config review cadence (model 進化に合わせて)
15. DRI / agent manager role + cross-functional WG 設置

### 根拠

Anthropic Applied AI team の large-codebase deployment 観察。具体事例:
- multi-million-line monorepo
- decades-old legacy codebase
- distributed microservices
- retail enterprise での plugin 配布
- C/C++ enterprise での LSP 活用

### 前提条件

conventional software engineering 環境 (engineers as primary contributors, Git, standard directory structure)。solo dev・小規模プロジェクトは対象外。

### 著者バイアス評価

- **信頼性**: Anthropic 公式記事。第三者 content farm とは異なり技術主張は原則信頼できる
- **バイアス源**: 自社 deployment 観察のみに基づく推奨。他ツール (Cursor/Continue/Aider) との比較なし
- **注意点**: 3-6 ヶ月 cadence 等は Anthropic 独自主張であり、業界標準ではない可能性がある

---

## Section 2: Gap Analysis (Pass 1: 存在チェック)

### Pass 1 初期判定 (Sonnet Explore)

| # | 手法 | Pass 1 判定 | 詳細 |
|---|------|------------|------|
| 1 | Agentic search (RAG なし) | Already | Claude Code デフォルト動作。dotfiles 側で制御不要 |
| 2 | CLAUDE.md 階層化 | Already | root CLAUDE.md + subdirectory 構造 (.config/claude/CLAUDE.md 等) 実装済 |
| 3 | Stop hook self-improvement | Already | completion-gate.py + session-learner.py + friction-events.jsonl で実装済 |
| 4 | Start hook 動的 context | Already | settings.json の hooks.Start に複数スクリプト登録済 |
| 5 | Skills path-scoped | Partial (誤判定) | Pass 1 は allowed-tools (tool scoping) と混同。実際は Already (後述) |
| 6 | Plugins 配布 | N/A | solo dev、managed marketplace 不要 |
| 7 | LSP integration | Already | settings.json に LSP 設定済 |
| 8 | MCP servers | Already | settings.json に複数 MCP server 登録済 |
| 9 | Subagents 分離 | Already | agents/ 配下に探索・編集分離の subagent 実装済 |
| 10 | Subdirectory init | N/A | dotfiles は monorepo ではない |
| 11 | Scoped test/lint | Partial (low margin) | Taskfile global で十分。dotfiles は単一ディレクトリ構造 |
| 12 | permissions.deny バージョン管理 | Already | .config/claude/settings.json が dotfiles に含まれ git 管理済 |
| 13 | Codebase map | Already | references/decision-tables-index.md + docs/specs/ が実質 map として機能 |
| 14 | 3-6 ヶ月 cadence | Partial (誤判定) | Pass 1 は harness-stability.md (30 日削除) と混同。実際は Already (後述) |
| 15 | DRI / cross-functional WG | N/A | solo dev |

---

## Section 3: Pass 2 訂正 + Phase 2.5 (Gemini のみ)

### Pass 2 (Opus) 訂正

Sonnet Pass 1 の誤判定 2 件を修正:

**誤判定 1: #5 Skills path-scoped (Partial → Already)**
- Pass 1 は `allowed-tools` (permission scoping) を path-scoped activation と混同した
- 実際は `.config/claude/scripts/runtime/skill-suggest.py` の `PATH_MAP` で実装済
  - `.config/claude/skills/` → `/skill-creator` を提案
  - `docs/specs/` → `/spec` を提案 (他 3 パターンあり)
- 判定: **Already (強化不要)**

**誤判定 2: #14 3-6 ヶ月 cadence (Partial → Already)**
- Pass 1 は `harness-stability.md` (30 日削除評価) と性質が異なるものを同一視した
- 実際は `.config/claude/scripts/runtime/skill-pruning-eval-reminder.sh` が 30 日サイクルで評価 reminder を生成
- 記事の「3-6 ヶ月」は model 進化に合わせた config 見直し。dotfiles は harness-stability.md で 30 日サイクルで対応
- 判定: **Already (model release trigger 概念のみ軽微な追加余地あり)**

### Phase 2.5: Gemini (API quota 枯渇でメモリベース検証に降格)

**Codex (`Skill(codex:rescue)`) は stall**: 120s wakeup 設定後も結果到着せず。memory ポリシー「stall 2 回 max、独自検証で進む」に従い skip。

**Gemini-explore (メモリベース)** で発見した追加観点:

1. **3-6 ヶ月 cadence は業界標準ではなく Anthropic 独自主張** — Cursor/Continue/Aider に類似推奨なし。model release 周期との相関も未検証。
2. **Skill description token tax 12.3K は記事が言及しない隠れトレードオフ** — 107 skills × 115 token avg。記事は Skills のメリットのみ述べ、常時税コストを省略している。
3. **`CLAUDE_CODE_FORK_SUBAGENT=1` は記事言及なし** — dotfiles で試験運用中 (memory `2026-04-27 subagent-context-fork`)。記事の subagents 分離は conceptual 説明のみ。
4. **競合上の理由で RAG/cadence/cost を矮小化している可能性** — Anthropic 公式記事として合理的なバイアス源。

---

## Section 4: 最重要発見 — Pruning-First 失敗 (既存重複の見落とし)

Phase 4 (Plan) 直前で既存 skill 監視スクリプトを発見し、当初検討していた Task 1/2/3 が全て既存実装と重複していた。

### 既存重複マッピング

| 当初 Task 案 | 既存実装 | パス | 重複度 |
|------------|---------|------|--------|
| Path-scoped skill activation | `skill-suggest.py` (PostToolUse hook、PATH_MAP で `.config/claude/skills/` → `/skill-creator`、`docs/specs/` → `/spec` 等 4 パターン) | `.config/claude/scripts/runtime/skill-suggest.py:40-45` | **完全重複** |
| Config review cadence 実装 | `skill-pruning-eval-reminder.sh` (30 日サイクル、Track A retire/Track B 分割、catch-up window 付き) | `.config/claude/scripts/runtime/skill-pruning-eval-reminder.sh` | **強い重複** (30 日 vs 3-6 ヶ月の差のみ) |
| Skill token tax 監視 | `skill-count-alert.sh` (THRESHOLD=110、記事の 107 skill 数と一致) | `.config/claude/scripts/runtime/skill-count-alert.sh:6` | **強い重複** (count と token tax は強相関) |

### なぜ見落としたか

Pass 1 (Sonnet Explore) が `scripts/runtime/skill-*` ディレクトリを直接列挙せず、`.config/claude/skills/` の SKILL.md と `settings.json` のみを深掘りした。監視スクリプト群 (`skill-suggest.py`, `skill-pruning-eval-reminder.sh`, `skill-count-alert.sh`) は Pass 1 のキーワード検索に「監視」「reminder」「tracker」「alert」が含まれていなかったため、見落とされた。

---

## Section 5: 修正後最終判定テーブル

| # | 手法 | 最終判定 | 対応実装 |
|---|------|---------|---------|
| 1 | Agentic search | Already | Claude Code デフォルト動作 |
| 2 | CLAUDE.md 階層化 | Already | root + .config/claude/ 階層構造 |
| 3 | Stop hook self-improvement | Already | `completion-gate.py`, `session-learner.py` |
| 4 | Start hook 動的 context | Already | `settings.json` hooks.Start |
| 5 | Skills path-scoped activation | Already | `skill-suggest.py:40-45` PATH_MAP |
| 6 | Plugins 配布 | N/A | solo dev |
| 7 | LSP integration | Already | settings.json |
| 8 | MCP servers | Already | settings.json |
| 9 | Subagents 分離 | Already | `agents/` 配下 + `CLAUDE_CODE_FORK_SUBAGENT=1` (試験) |
| 10 | Subdirectory init | N/A | dotfiles は monorepo 非対象 |
| 11 | Scoped test/lint | Partial (low margin) | Taskfile global で dotfiles は十分 |
| 12 | permissions.deny バージョン管理 | Already | `settings.json` が dotfiles git 管理 |
| 13 | Codebase map | Already | `references/decision-tables-index.md` |
| 14 | 3-6 ヶ月 cadence | Already (軽微な余地) | `skill-pruning-eval-reminder.sh` 30 日サイクル |
| 15 | DRI / cross-functional WG | N/A | solo dev |

**Already: 10 / N/A: 3 / Partial (low margin): 1 / Already (軽微余地): 1**

---

## Section 6: Integration Decisions

### Triage 結果: D (取り込みなし)

**ユーザー判断**: 取り込みなし、分析レポートのみ保存。

**理由**: 既存実装が記事の主張を全てカバーしており、新規実装は Pruning-First 違反になる。

| 手法 | 判定 | 理由 |
|------|------|------|
| Path-scoped skill activation | Reject (Already) | `skill-suggest.py` で完全実装済 |
| Config review cadence | Reject (Already) | `skill-pruning-eval-reminder.sh` で実装済 |
| Skill token tax 監視 | Reject (Already) | `skill-count-alert.sh` THRESHOLD=110 で実質カバー |
| Subagent context fork 強化 | Reject (Already) | 試験運用中。別 spike で評価が適切 |
| major model release trigger 追加 | スキップ (軽微) | `harness-stability.md` への 1 行追記で足りるが、記事の「3-6 ヶ月」は検証されていない独自主張 |
| Plugins / DRI / WG | N/A | solo dev で組織配布不要 |

---

## Section 7: 教訓 (Lessons learned)

### L1: Sonnet Pass 1 の浅さ — スクリプト列挙の明示が必要

**発生**: Pass 1 で `scripts/runtime/skill-*` 群を見落とし、Task 1/2/3 を Phase 4 直前まで既存重複と気づかなかった。

**根本原因**: Sonnet は `.config/claude/skills/` の SKILL.md と `settings.json` のみを深掘りし、`scripts/runtime/` の監視スクリプト群を探索しなかった。キーワードに「監視」「reminder」「tracker」「alert」が含まれていなかった。

**改善策**: 今後の `/absorb` では Pass 1 の探索キーワードに以下を明示的に含める:
- `scripts/runtime/` の直接ディレクトリ列挙
- キーワード: 監視 / reminder / tracker / alert / weekly / count / threshold

### L2: Phase 2.5 の bias mitigation 機能不全 — 追加検証 step が必要

**発生**: Codex stall + Gemini quota 枯渇で三角測量が動かず、Opus Pass 2 判定が補正されないまま Phase 4 に進みかけた。

**改善策**: Phase 2.5 で 2 つとも degraded した場合は Phase 4 (Plan) 前に最低限の追加検証 step を挟む:

```bash
find .config/claude/scripts -type f -name "skill-*" | sort
find .config/claude/scripts -type f -name "*alert*" -o -name "*reminder*" | sort
```

### L3: Anthropic 公式記事のバイアス — 自社観察 ≠ 業界標準

**発見**: 3-6 ヶ月 cadence は Cursor/Continue/Aider に類似推奨なし。Anthropic の internal deployment 観察からの推奨であり、普遍的な best practice として扱うには独立した検証が必要。

**方針**: Anthropic 公式記事は content farm より信頼性が高いが、自社製品に有利な主張 (RAG を使わない agentic search が優れる、Plugins 配布が重要 等) は competitive バイアスとして識別する。

### L4: 既存機構の machine-readable 索引の不在

**発見**: 「もうほぼ全部実装済み」という認識は概ね正しかったが、「どの監視スクリプトが記事のどの主張をカバーするか」のマッピングを当初自動的に引き出せなかった。

**方針 (YAGNI — 今は実装しない)**: `scripts/runtime/` の capability 索引作成は 3 回同じ見落としが発生したら検討する。今回は 1 回目。

---

## Section 8: 関連 memory リンク

- `feedback_absorb_thoroughness.md` — Pass 1 浅さの繰り返し防止 (Codex/Claude Parity absorb 由来)
- `feedback_codex_invocation_pattern.md` — Codex stall 時の独自検証先行ポリシー
- `feedback_stall_proceed_with_evidence.md` — stall 2 回 max ルール
- `2026-04-27-subagent-context-fork-absorb-analysis.md` — `CLAUDE_CODE_FORK_SUBAGENT=1` 試験運用の背景
- `docs/plans/2026-05-08-skill-pruning-evaluation-plan.md` — skill-pruning-eval-reminder.sh の元計画
- `.config/claude/scripts/runtime/skill-suggest.py` — PATH_MAP による path-scoped skill activation
- `.config/claude/scripts/runtime/skill-pruning-eval-reminder.sh` — 30 日 cadence 実装
- `.config/claude/scripts/runtime/skill-count-alert.sh` — skill token tax 代替監視 (THRESHOLD=110)
