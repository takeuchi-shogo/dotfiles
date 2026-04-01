---
source: https://randomlabs.ai/blog/skill-chaining — "Skill Chaining and Why Skills Should Be Actions"
date: 2026-04-02
status: integrated
---

## Source Summary

RandomLabs (Slate) の記事。スキルを静的プロンプトではなく動的アクション（contextual behaviors）として扱うべきと主張。

**主張**:
- Knowledge Overhang（モデルが知っているが自発的に使わない知識）をスキルで引き出す
- Skills = episodic memory — スコープ付きコンテキストで活性化→終了時にクリーンアップ
- Orchestration Skills — スキルが他のスキルを参照・シーケンスするメタスキル

**手法**:
1. Knowledge Overhang: OOD知識→in-distribution行動変換
2. Skills as Episodic Memory: スコープ付きコンテキスト、完了後クリーンアップ
3. Thread-based Execution: 隔離ワーカー（権限・コンテキスト・タスクをスコープ）
4. Context Forking: 同期フォークで interactive skill use を実現
5. Orchestration Skills: スキルがスキルを呼ぶメタスキル（スキルチェイン）
6. Rules vs Skills: Progressive Disclosure — ルール＝強制ロード、スキル＝遅延ロード

**根拠**: 人間のスキル学習アナロジー（行動クローニング + 強化学習）。Slate での実装経験。

**前提条件**: マルチスレッドエージェントアーキテクチャ、動的スキル活性化の必要性

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Knowledge Overhang 概念 | N/A | 概念的フレーミング。既存設計思想と一致 |
| 2 | Context Forking | Already | worktree + `/spike`, `/autonomous` |
| 3 | Thread-based Execution | Already | Agent subagent + worktree isolation |
| 4 | Rules vs Skills (Progressive Disclosure) | Already | `<important if>` + Skill tool 遅延ロード |
| 5 | Orchestration Skills | Partial | `/epd`, `/dev-cycle` が部分実装。汎用パターン未定義 |
| 6 | スキル自動活性化 | Partial | `using-superpowers` がモデル判断に依存。環境状態→自動サジェスト未実装 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 判定 |
|---|-------------|---------------|------|
| 2 | worktree + `/spike` | fork の UI シームレス引き継ぎ | 強化不要 — `/checkpoint` + MEMORY で実質カバー |
| 3 | Agent subagent | 圧縮表現の構造化 | 強化不要 — Agent result は十分機能、過剰構造化は YAGNI |
| 4 | `<important if>` + Skill tool | ルールのコンテキスト flood | 強化不要 — conditional tag で軽減済み |

## Integration Decisions

- **#5 Orchestration Skills**: 取り込み → skill-creator planning-guide に Pattern 6 + Chaining 標準フォーマット追加
- **#6 スキル自動活性化**: 取り込み → skill-suggest.py hook 新設（PostToolUse Edit|Write でファイル種別→スキルサジェスト）
- #1-4: 取り込み不要（Already / N/A）

## Plan

| # | タスク | ファイル | 規模 |
|---|--------|---------|------|
| 1 | Chaining セクション標準化 | `skills/skill-creator/references/planning-guide.md` | S |
| 2 | skill-suggest hook 新設 | `scripts/runtime/skill-suggest.py` + `settings.json` | M |
| 3 | 分析レポート保存 | `docs/research/2026-04-02-skill-chaining-actions-analysis.md` | S |
