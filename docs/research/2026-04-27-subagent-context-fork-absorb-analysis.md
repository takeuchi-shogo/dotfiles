---
source: "Keep your Claude Code context clean with Subagents (aitmpl 系記事)"
date: 2026-04-27
status: analyzed
reaffirmed:
  - date: 2026-05-04
    by: "/absorb (Distribution vs Escalation, 2026-05-02)"
    decision: "Forked subagent (CLAUDE_CODE_FORK_SUBAGENT=1) は意図的非採用を再確認。partial 判定ではなく N/A / intentional non-adoption。理由: context cleanliness 哲学（subagent は要約のみ親に返すのが原則）と逆方向であり、現行設計と整合しない。Distribution vs Escalation 記事もこのトレードオフを認めている。"
---

# Subagent Context Fork absorb 分析

## ソース

- 記事: "Keep your Claude Code context clean with Subagents" (aitmpl 系記事)
- 取り込み日: 2026-04-27

## Source Summary

**主張**: 長時間 Claude Code セッションで context が肥大化する問題を Subagents で解決する。Subagent は独自の context window を持ち結果のみ親に返す。さらに `CLAUDE_CODE_FORK_SUBAGENT=1` で親の context を継承させて起動できる。

**手法**:
1. Subagent 定義パターン (Markdown + frontmatter: name, description, tools, model)
2. Subagent 配置スコープ (`.claude/agents/` project vs `~/.claude/agents/` personal)
3. Built-in Explore (codebase 検索を context 汚染なしに実行)
4. Built-in Plan (実装プラン生成を isolated context で)
5. `CLAUDE_CODE_FORK_SUBAGENT=1` 環境変数 (subagent が親 context を full inherit)
6. `/fork` slash command (オンデマンド context fork)
7. Prompt cache prefix sharing (fork children 2-N は input tokens ~10x 安価)
8. context-timeline hook (`npx claude-code-templates@latest --hook monitoring/context-timeline`)

**根拠**: 30 分セッションで 80k tokens の noise が蓄積、compact で重要情報が flatten される問題の実測。

**前提条件**: 長時間セッション、複数の独立調査、context cache を warm に保ちたいユースケース。

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Subagent 定義パターン (frontmatter) | Already | `.config/claude/agents/` に 30 agents、frontmatter は name/description/tools/model + memory/maxTurns/effort 拡張済み |
| 2 | Subagent 配置スコープ | Already | CLAUDE.md L27 で project/user 分離明示、symlink 構造確立 |
| 3 | Built-in Explore | Partial | triage-router で言及あり、search-first では Codex search_specialist 使用。命中率の計測指標は未整備 |
| 4 | Built-in Plan | Already | codex-plan-reviewer で Spec/Plan ゲート化済み |
| 5 | CLAUDE_CODE_FORK_SUBAGENT=1 | Gap | 全体で言及なし |
| 6 | /fork slash command | Gap | commands/ に存在せず |
| 7 | context-timeline hook (aitmpl) | Partial | 独自 context-monitor.py (statusline 用) あり、event timeline / threshold ログは未実装 |
| 8 | Prompt cache 管理 | Already | TTL ~1h、freeze で cache key 安定化、O(N²) token growth 管理済み。hit rate 低下要因の観測は未整備 |

## Codex 批評を反映した修正

| # | 手法 | 修正前 | 修正後 | 修正理由 |
|---|------|--------|--------|----------|
| 5 | CLAUDE_CODE_FORK_SUBAGENT=1 | Gap | N/A (限定実験のみ) | experimental + context cleanliness と逆方向。デフォルト採用は不適 |
| 6 | /fork slash command | Gap | N/A (限定実験のみ) | #5 に依存。例外ケースの手動実験のみとする |
| 7 | context-timeline hook | Partial | Partial → 独自強化 | aitmpl 直採用は不可 (第三者テンプレート)、context-monitor.py 拡張で取り込む |
| 3 | Built-in Explore | Partial | Already (強化可能 - 計測) | 命中率の計測指標が無い点を強化対象に |
| 8 | Prompt cache | Already | Already (強化可能 - 計測) | cache hit rate 低下要因の計測が無い点を強化対象に |

## Already Strengthening Analysis (Pass 2)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | 30 subagents (frontmatter 統一) | — | — | 強化不要 |
| S2 | project vs user スコープ (CLAUDE.md L27) | — | — | 強化不要 |
| S3 | Built-in Explore (triage-router) | "Explore を first-line に" 原則の計測欠如 | triage-router 命中率の観測指標を references/observability-signals.md に追加 | 強化可能 |
| S4 | Built-in Plan (codex-plan-reviewer) | — | — | 強化不要 |
| S5 | context-monitor.py (statusline) | subagent イベント timeline / threshold ログが無い | subagent 起動・完了・context % 閾値越えのイベントを JSONL ログに記録する機能を追加 | 強化可能 |
| S6 | Prompt cache (TTL/freeze) | cache hit rate 低下要因の観測欠如 | cache hit/miss 観測指標を references/observability-signals.md に追加 | 強化可能 |

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 5 | CLAUDE_CODE_FORK_SUBAGENT=1 (default 採用) | スキップ | デフォルト採用は不適。親 context 全継承は context cleanliness と逆方向。限定ガイド (T4) で代替 |
| 6 | /fork slash command (default 採用) | スキップ | #5 に依存。例外ケースの手動実験のみ、experimental 注記必須 |
| 7 | aitmpl context-timeline hook 直採用 | スキップ | 第三者テンプレート (`npx claude-code-templates`) は信頼性・更新追従で不確実。独自強化 (T2) で代替 |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S5 | context-monitor.py に event timeline 追加 (T2) | 採用 | Codex 推奨の最優先項目。statusline 警告と JSONL 記録で observability を補完 |
| S3/S6 | 観測指標 (Explore 命中率/Plan 差し戻し率/cache hit) (T3) | 採用 | Codex 過小評価指摘の解消。3 指標に絞ることでオーバーヘッドを最小化 |
| (補) | /fork 限定実験ガイド (T4) | 採用 | 例外ケースの手動実験のみ。experimental 注記必須、prompt cache prefix sharing の効果計測方法を明記 |

## Plan

### Task 1 (T2): context-monitor.py に event timeline 追加

- **Files**: `scripts/context-monitor.py` 拡張 or 新規 `scripts/context-events.py`
- **Changes**:
  - subagent 起動・完了・context % 閾値越えのイベントを JSONL ログ (`~/.claude/session-state/context-events-{date}.jsonl`) に非同期書き込み
  - 閾値超過時に statusline 警告を表示（既存 statusline との統合）
  - イベントスキーマ: `{ts, event_type, subagent_name, context_pct, session_id}`
- **Size**: M (1-2 ファイル + ログスキーマ設計)

### Task 2 (T3): 観測指標を references/ に追記

- **Files**: `references/observability-signals.md` (既存ファイル確認後、なければ新規)
- **Changes**: Subagent observability 節を追加。以下の 3 指標を定義:
  - triage-router 命中率 (Explore が search_specialist 委譲前に解決した割合)
  - Plan ゲート差し戻し率 (codex-plan-reviewer が block 判定した割合)
  - cache hit rate (session 中の cache hit / total input tokens)
- **Size**: S

### Task 3 (T4): /fork 限定実験ガイド

- **Files**: `references/fork-experiment.md` (新規) or 既存 references/ に追記
- **Changes**:
  - experimental 注記（last verified 2026-04-27）
  - 適用ケース: 親文脈が肥大化して named subagent に説明できない例外のみ
  - デフォルト不採用の理由: context cleanliness と逆方向、Subagent isolation の利点を消す
  - prompt cache prefix sharing の効果計測方法 (fork children 2-N の input tokens 比較)
- **Size**: S

### Task 4 (T5): MEMORY.md ポインタ追記

- **Files**: `~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/MEMORY.md`
- **Changes**: 外部知見索引セクションに 1 行追加 (リンク + 要約)
- **Size**: S

## Risks & Tradeoffs

- **計測指標の肥大化リスク**: T3 の観測指標を増やしすぎると observability burden が増える。Codex 指摘の 3 指標に絞ることで回避
- **/fork 実験ガイドの陳腐化リスク**: experimental 機能 (`CLAUDE_CODE_FORK_SUBAGENT=1`) は Anthropic が破壊的変更を加えると無効化。"experimental, last verified 2026-04-27" 注記必須、定期棚卸しで廃止検討
- **context-monitor.py のブロッキングリスク**: 既存 context-monitor.py は statusline 用で同期実行。event timeline 書き込みを同期で追加すると statusline がブロックされる。非同期 (subprocess / asyncio) で実装必須
- **aitmpl 依存の回避**: `npx claude-code-templates` は外部テンプレートのため直採用を避けた。将来 aitmpl が公式化した場合は再評価

## 棄却

- `CLAUDE_CODE_FORK_SUBAGENT=1` デフォルト採用: context cleanliness と逆方向、Subagent isolation 利点を消す
- `/fork` slash command デフォルト採用: 同上、例外限定の手動実験のみ
- aitmpl context-timeline hook 直採用: 第三者テンプレート依存、独自 context-monitor.py 拡張で代替

## 関連リンク

- 強化対象: `scripts/context-monitor.py`
- 観測先: `references/observability-signals.md`
- 既存スキル: `/checkpoint`, `/check-context`, `/freeze`
- 関連 absorb: 2026-04-17 context-design-absorb (5層コンテキストデザイン / cwd-aware profile), 2026-04-17 claude-code-session-mgmt (Compact vs Clear matrix / 300-400k multi-hop threshold)
