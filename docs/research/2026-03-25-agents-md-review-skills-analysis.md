---
source:
  - https://www.builder.io/blog/agents-md
  - https://zenn.dev/penpeen/articles/93d318a99d329e
date: 2026-03-25
status: integrated
---

## Source Summary

### Article 1: AGENTS.md (Builder.io)

AI agent 向けの標準ガイドファイル `AGENTS.md` の提唱。Project Overview / Do's & Don'ts / File-Level Tests / Real Examples の4セクション構成。エージェントが毎回コードベースを再発見するコストを排除し、一貫性のある出力を得る。

### Article 2: Claude Code Review Skills (Zenn/penpeen)

Claude Code の Skills 機能でカスタムレビューを構築する実践記事。主要手法:
- **2パスレビューサイクル**: 全列挙 -> 重要度フィルタで critical 指摘がノイズに埋もれるのを防止
- **Pre-diff 影響範囲調査**: diff を見る前に呼び出し元・依存を調査し、表面上安全な変更の破壊的影響を検出
- **動的ガイドライン選択**: cross-cutting.md + 言語/FW 別チェックリストの条件付き注入
- **自己改善ループ**: レビュー後にカバー外パターンを検出し、ガイドライン追加を提案

## Gap Analysis

### Article 1: AGENTS.md

| # | Hand Method | Judgment | Current |
|---|------------|----------|---------|
| 1 | AGENTS.md as standardized file | Already | CLAUDE.md + AGENTS.md + GEMINI.md 3ツール対応 |
| 2 | Project Overview section | Already | CLAUDE.md + AGENTS.md 両方に記載 |
| 3 | Do's and Don'ts | Already | core_principles + rules/ directory |
| 4 | File-Level Tests (test examples) | Already | rules/ に OK/NG コード例 |
| 5 | Real code examples | Already | rules/ に具体的コードスニペット |

**結論**: 全5手法が既存で完全カバー。Gap なし。

### Article 2: Claude Code Review Skills

#### Gap / Partial

| # | Hand Method | Judgment | Current |
|---|------------|----------|---------|
| 1 | 2-pass review cycle | **Gap** | code-reviewer は1パス出力。Synthesis の confidence フィルタはあるが個別レビューアー内の再評価なし |
| 2 | Pre-diff impact investigation | **Partial** | cross-file-reviewer に PRE_ANALYSIS あるが /review フローに未統合 |
| 3 | Cross-cutting checklist | **Partial** | security-baseline.md はあるが全 PR 共通チェックリストなし |

#### Already (Enhancement Check)

| # | Existing | Article's Insight | Enhancement |
|---|----------|------------------|-------------|
| 4 | review-checklists/ per language | cross-cutting.md 常時適用 | -> Gap #3 で対応 |
| 5 | AutoEvolve + findings persistence | 直接ガイドライン追加提案 | code-reviewer に [NEW_PATTERN] 検出を追加 |
| 6 | Progressive Disclosure | 50行ルール + Skills 拡張 | 強化不要 |
| 7 | Project-level CLAUDE.md | Repo-specific design principles | N/A (dotfiles は app 開発リポジトリではない) |

## Integration Decisions

**取り込み (4件)**:
1. code-reviewer に2パスレビュー手順を追加 (`agents/code-reviewer.md`)
2. /review Step 1.3 に Impact Pre-scan を追加 (`skills/review/SKILL.md`)
3. cross-cutting.md チェックリスト新規作成 (`references/review-checklists/cross-cutting.md`)
4. code-reviewer にガイドライン自己提案 [NEW_PATTERN] を追加 (`agents/code-reviewer.md`)

**スキップ**: Article 1 の全手法 (Already)、Article 2 の repo-specific design principles (N/A)

## Changes Made

- `agents/code-reviewer.md`: 2パスレビュー手順 + ガイドライン自己提案セクション追加
- `skills/review/SKILL.md`: Step 1.3 Impact Pre-scan 追加 + cross-cutting.md 常時注入ルール追加
- `references/review-checklists/cross-cutting.md`: 新規作成 (CC-1 ~ CC-7)
