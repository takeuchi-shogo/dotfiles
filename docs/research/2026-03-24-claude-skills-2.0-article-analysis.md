---
source: "How to build Claude Skills 2.0 Better than 99% of People (Medium article)"
date: 2026-03-24
status: integrated
---

## Source Summary

**主張**: Claude Skills は再利用可能な知識・手順のパッケージで、SKILL.md の metadata 精度がトリガー精度を決定する。Progressive Disclosure（3層構造）でトークン効率を最適化する。

**手法**:
- YAML frontmatter（name + description）でメタデータ定義
- SKILL.md 500行上限、超過分は reference/ に分割
- 「Claude が知らないことだけ書く」原則
- 指示の自由度（高/中/低）をタスク特性に合わせる
- Plugin マーケットプレイス経由のスキル共有
- MCP = ツール提供、Skills = ワークフロー定義の役割分担

**根拠**: 記事は概念レベルでは正確だが、具体的なコマンドやリポジトリ名（`anthropics/skills`, `document-skills@anthropic-agent-skills`）に複数の誤りあり。

**前提条件**: 記事は入門〜中級者向け。Claude Code CLI とClaude.ai Web版の区別が曖昧。

## Gap Analysis

| # | 手法 | 判定 | 根拠 |
|---|------|------|------|
| 1 | Progressive Disclosure | Already | `skill-writing-guide.md:22-37` に3層構造を明記 |
| 2 | 500行上限 | Already | `skill-writing-principles.md:97` 全65スキルが344行以下 |
| 3 | 「Claude が知らないことだけ書く」 | Already | 原則#2「一般知識を削れ」 |
| 4 | Metadata description の精度 | **Partial** | 原則は存在するが適用率が低い（後述） |
| 5 | 指示の自由度分類 | Partial | `compact-instructions.md` にエージェント粒度指針あり |
| 6 | Plugin マーケットプレイス | Already | 3マーケットプレイス、10プラグイン |
| 7 | MCP + Skills 役割分担 | Already | 実運用で併用 |

### 品質メトリクス（定量ギャップ）

| メトリクス | 現状 | 目標 |
|-----------|------|------|
| `Do NOT use for:` (負の境界) | 30/65 (46%) | 80%+ |
| `Triggers:` (正のトリガー) | 21/65 (32%) | 80%+ |
| `Anti-Patterns` セクション | 26/65 (40%) | 60%+ |
| `metadata:` フィールド | 62/65 (95%) | 100% |

## Integration Decisions

全4項目を統合:
- **A**: 35スキルに `Do NOT use for:` を追加
- **B**: 44スキルに `Triggers:` を追加
- **C**: 39スキルに Anti-Patterns セクション追加
- **D**: 3スキル (careful/freeze/hook-debugger) に metadata フィールド追加

## Plan

6並列エージェントでバッチ実行。詳細は `docs/plans/2026-03-24-skill-description-quality-improvement.md` を参照。
