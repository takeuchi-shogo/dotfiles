---
title: スキル呼び出しパターン
topics: [skill]
sources: [2026-04-12-tan-thin-harness-fat-skills-analysis.md]
updated: 2026-04-12
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

`agent-router.py` フックは呼び出しコンテキスト（タスクの複雑さ・ファイル数・エラー種別）を world として解釈し、委譲先モデルを動的に決定する。

## 設計原則

1. **World をパラメータとして明示しない** — スキルは自律的に world を検出する。ユーザーに world を宣言させない
2. **デフォルト world を定義する** — 文脈が不明な場合のフォールバック動作を必ず定義する
3. **World 間の副作用を分離する** — ある world での実行が別 world の前提を壊さない
4. **Invert Test を各 world に適用する** — 「この world でスキルを呼ばない理由があるか？」を確認する

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
