---
title: スキル呼び出しパターン
topics: [skill]
sources: [2026-04-12-tan-thin-harness-fat-skills-analysis.md, 2026-04-09-12-claude-patterns-analysis.md, 2026-04-09-claude-code-automation-guide-analysis.md, 2026-04-14-hermes-personal-analyst-analysis.md, 2026-04-23-agents-md-patterns-absorb-analysis.md, 2026-04-26-skill-md-15min-guide-absorb-analysis.md, 2026-04-29-claude-skills-six-laws-absorb-analysis.md, 2026-05-09-skill-usage-tally.md, 2026-05-20-claude-code-large-codebase-absorb-analysis.md, 2026-05-23-anthropic-complete-guide-building-skills-absorb-analysis.md, 2026-06-02-agents-best-practices-absorb-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 11
confidence: established
---

# スキル呼び出しパターン

## 概要

同一スキルを異なる「world」（呼び出し文脈・前提状態・モデル）で再利用するための設計パターン。Garry Tan の "Thin Harness, Fat Skills" 原則 #10「Invocation Pattern」に基づく。スキルはモノリシックな手順書ではなく、文脈に応じてパラメータ化・分岐できる再利用単位として設計する。

## 核心概念: World とは何か

「World」とは、スキルが呼ばれる際の前提状態の集合である。同じスキルでも world が違えば振る舞いを変える必要がある。World の構成要素:

- **呼び出し元のフェーズ** — 計画中か、実装中か、レビュー中か
- **前提ファイルの存在** — plan ファイルがあるか、コミットがあるか
- **モデルコンテキスト** — Opus, Sonnet, Haiku のどれが動いているか
- **スコープ** — 単一ファイルか、複数ディレクトリか

## 実装済み事例

### 1. `/improve` の World 分岐

`/improve` スキルは呼び出し文脈によって動作を変える:

- **AutoEvolve BG 文脈**: セッション終了後の自動呼び出し。変更は max 3 ファイル・master 直変禁止
- **手動呼び出し文脈**: ユーザーの明示的な改善指示。スコープ制限なし
- **フックからの呼び出し**: post-test 分析後の自動提案。提案のみでコミットしない

### 2. `/absorb` の World 分岐

`/absorb` スキルは統合対象の状態によって Phase をスキップ:

- **URL world**: WebFetch → 要約 → Gap 分析 → 取り込み
- **テキスト world**: 要約をスキップして Gap 分析へ
- **Already 判定 world**: 取り込みをスキップして批評のみ実行

### 3. `/research` のモデル world

`/research` は並列サブエージェント数をモデルに応じて調整:

- **Opus world**: 深いシングルスレッド分析
- **Sonnet world**: 並列 3 サブエージェントで速度優先
- **Haiku world**: 軽量 WebFetch + 要約のみ

### 4. モデルルーティングの World

`claude-hooks` (Rust, `user-prompt`) フックは呼び出しコンテキスト（タスクの複雑さ・ファイル数・エラー種別）を world として解釈し、委譲先モデルを動的に決定する。

### 5. 階層 World（global / project / module）

CLAUDE.md の3層スコープ（global / project / module）と `<important if>` 条件タグは、階層レベルという world を選択的ロードで表現するパターン。AGENTS.md 系記事の分析では、この3層構造が Progressive Disclosure の入口として機能し、下位層への委譲によってコンテキスト汚染を防ぐことが確認されている。

### 6. 新規リソース検知の World

新しい MCP server が `.claude.json` / `.mcp.json` に追加されたタイミングを world として検知し、`skill-creator` 起動をヒント通知する PostToolUse hook（`mcp-skill-hint.py`）。自動生成はせず、通知のみに留めてスキル品質を担保する設計。

## 設計原則

1. **World をパラメータとして明示しない** — スキルは自律的に world を検出する。ユーザーに world を宣言させない
2. **デフォルト world を定義する** — 文脈が不明な場合のフォールバック動作を必ず定義する
3. **World 間の副作用を分離する** — ある world での実行が別 world の前提を壊さない
4. **Invert Test を各 world に適用する** — 「この world でスキルを呼ばない理由があるか？」を確認する
5. **description の質が invocation 頻度を左右する** — description が50文字未満だと呼出頻度が3-5倍低下する傾向（100 Skills リバースエンジニアリング調査）。最初の250文字にユースケースを埋め込み、`[What]+[When]+[Key capabilities]` 形式で明示する
6. **near-miss negative example で誤発火を防ぐ** — trigger phrase には「似ているが発火すべきでないリクエスト」の否定例を最低3つ添えることで、隣接する world との誤認識を減らす

## Invert Test

スキルが新しい world をサポートする前に行う検証:

> 「このスキルをこの文脈で*使わない*理由があるか？」

Invert Test で NO（使わない理由がない）なら world をサポートする。YES（使わない理由がある）なら別スキルとして分離するか、`Do NOT use for:` に明記する。

## 関連概念

- [スキル設計](skill-design.md) — スキルの基本設計原則
- [スキル競合解決](skill-conflict-resolution.md) — 複数スキルが同一トリガーに応答する場合の処理
- [スキルチェイニング](skill-chaining.md) — スキルを連鎖させるパターン

## ソース

- [Tan "Thin Harness, Fat Skills" 分析](../../research/2026-04-12-tan-thin-harness-fat-skills-analysis.md) — 原則 #10 Invocation Pattern, #2 Invert Test の解説と dotfiles への適用
- [12 Claude Patterns 分析](../../research/2026-04-09-12-claude-patterns-analysis.md) — Claude活用12パターンを分析、全項目を既存スキル強化に統合
- [Claude Code 日常自動化ガイド分析](../../research/2026-04-09-claude-code-automation-guide-analysis.md) — 日常自動化7プロンプトを分析、実現可能性ラベルなど2件採用
- [Hermesパーソナルアナリスト活用体験記分析](../../research/2026-04-14-hermes-personal-analyst-analysis.md) — Hermesアナリスト記事分析、大半既存資産で充足、情報源拡張のみ追加
- [AGENTS.md is a model upgrade 分析](../../research/2026-04-23-agents-md-patterns-absorb-analysis.md) — AGENTS.md記事分析、sprawl監査等7タスク採用(module化棄却)
- [SKILL.md 15分ガイド分析](../../research/2026-04-26-skill-md-15min-guide-absorb-analysis.md) — SKILL.md初級ガイドを分析、成熟済みで不採用と判定
- [Claude Code Skills 6つの設計法則分析](../../research/2026-04-29-claude-skills-six-laws-absorb-analysis.md) — Skill設計6法則を分析、near-miss例等2件を軽量統合
- [Skill / Slash Command Usage Tally レポート](../../research/2026-05-09-skill-usage-tally.md) — 200セッションのスラッシュコマンド使用頻度を集計
- [Claude Code in Large Codebases: Best Practices](../../research/2026-05-20-claude-code-large-codebase-absorb-analysis.md) — 大規模コードベース記事は既存実装で全カバー、新規採用なし
- [The Complete Guide to Building Skills for Claude](../../research/2026-05-23-anthropic-complete-guide-building-skills-absorb-analysis.md) — 公式Skillsガイドから3-arm eval基盤など5件採用
- [agents-best-practices (provider-neutral)](../../research/2026-06-02-agents-best-practices-absorb-analysis.md) — provider-neutral harness skillを分析、8原則は全Already、reference扱いで不採用
