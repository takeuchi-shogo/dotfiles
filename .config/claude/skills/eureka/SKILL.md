---
name: eureka
description: >
  技術ブレイクスルーを構造化テンプレートで即座に記録する。問題→洞察→実装→指標→再利用パターン。
  発見の鮮度が高いうちに記録し、AutoEvolve learnings と連携。
  /eureka で手動起動。
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Eureka — Technical Breakthrough Capture

## Trigger

`/eureka {description}` で起動。引数なしの場合は直近の会話から自動抽出を試みる。

## Workflow

1. **Capture** — ブレイクスルーの内容を特定
2. **Structure** — テンプレートに従って構造化
3. **Save** — breakthroughs/ に保存、INDEX.md を更新
4. **Link** — AutoEvolve learnings に pattern として emit

## Step 1: Capture

引数がある場合はそれをブレイクスルー概要とする。
ない場合は直近の会話を分析し、以下を特定:

- 解決された問題
- 核心的な洞察
- 予想外だったこと

## Step 2: Structure

以下のテンプレートで `breakthroughs/YYYY-MM-DD-{kebab-case-name}.md` を作成:

```
# {Title}

**Date:** {YYYY-MM-DD}
**Tags:** {comma-separated tags}
**Impact:** {Low | Medium | High | Critical}

## Problem

{何が問題だったか。症状と制約を具体的に}

## Insight

{核心的な洞察。なぜこれが解決策になったか}

## Implementation

{具体的な実装。コードスニペットがあれば含める}

## Metrics

{Before/After の定量比較。測定可能なもの}

## Reusable Pattern

{この知見を抽象化した汎用パターン。他のプロジェクトでも使えるように}
```

## Step 3: Save & Index

1. ファイルを `breakthroughs/` に保存
2. `breakthroughs/INDEX.md` を更新（なければ作成）:

```
# Breakthroughs Index

| Date | Title | Tags | Impact |
|------|-------|------|--------|
| {date} | [{title}](./{filename}) | {tags} | {impact} |
```

新しいエントリは先頭に追加（最新が上）。

## Step 4: AutoEvolve 連携

保存後、以下の pattern イベントを emit するよう提案:

```
category: "pattern"
message: "eureka: {title}"
importance: 0.8+ (Impact に応じて)
```

## Anti-Patterns

- 長文を書こうとして鮮度を失う（簡潔に、後で refinement）
- 問題なしに洞察だけ書く（必ず Problem → Insight のペアで）
- Metrics を省略する（定量化できなくても Before/After の定性比較を書く）
