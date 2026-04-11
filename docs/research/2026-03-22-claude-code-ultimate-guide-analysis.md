---
source: https://github.com/FlorianBruniaux/claude-code-ultimate-guide
date: 2026-03-22
status: analyzed
---

## Source Summary

Claude Code の総合学習ガイド（コミュニティ主導、CC BY-SA-4.0）。
Stars 2,075、Forks 321。作者: Florian Bruniaux。

### 主張
「使い方の暗記」ではなく「なぜそう動くのか」を理解させるアプローチ。
セキュリティ脅威インテリジェンス（CVE + 悪意スキル検知）の組み込みが差別化要素。

### 手法
1. 48 Mermaid ダイアグラム（12カテゴリ）
2. TDD/SDD/BDD をエージェント文脈で再解釈
3. 14+ CVE マッピング + Snyk ToxicSkills 監査データ
4. 155+ 実用テンプレート（agents/commands/hooks/skills/scripts等）
5. Context Engineering（予算計算、canary、CI drift検出）
6. TypeScript製 MCP サーバー（17ツール）
7. 4プロファイルクイズ（Junior/Senior/Power User/PM）
8. ロール別ガイド（CTO/CEO/PM/Tech Lead）
9. 115+ リソース評価（5段階体系的評価）
10. machine-readable 形式（llms.txt, YAML）
11. チートシート（PDF + Markdown）

### 根拠
- Snyk ToxicSkills: 3,984スキル中36.82%にセキュリティ欠陥
- CVE-2026-0755 (CVSS 9.8) 等の具体的脆弱性追跡
- 研究引用: Veracode, ACM, Cortex.io

### 前提条件
- Claude Code CLI ユーザー向け（公式ドキュメントではない）
- README上の数値に内部不一致あり（ダイアグラム41vs48、テンプレート218vs155等）

## Gap Analysis

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Mermaid ダイアグラム集 | Partial | スキル内に一部あるが集中管理なし |
| 2 | TDD 方法論 | Already | superpowers:test-driven-development |
| 3 | SDD/BDD 方法論 | Gap | 未実装 |
| 4 | CVE 追跡 | Already | references/claude-code-threats.md + 57 policy scripts |
| 5 | 悪意スキル検知 | Already | mcp-audit.py + threats DB |
| 6 | Prompt Injection 検出 | Partial | 汎用セキュリティhookのみ、専用detector なし |
| 7 | Context Engineering | Already | resource-bounds.md + context-monitor.py |
| 8 | MCP サーバー | N/A | テンプレートあり。ガイド検索用MCPは用途が異なる |
| 9 | ���イズ | Gap | profile-drip はあるが体系的評価なし |
| 10 | ロール別ガイド | N/A | 個人dotfilesなので不要 |
| 11 | リソース評価体系 | Partial | MEMORY.md に記録あるが構造化フォーマットなし |
| 12 | llms.txt | Gap | 未実装 |
| 13 | チートシート | Gap | 未実装 |
| 14 | テンプレート数 | Already | 178+ (skills62+agents31+commands28+policy57) |
| 15 | GitHub Actions | Already | setup-background-agents でカバー |

## Integration Decisions

全7項目を取り込み:
1. [Gap] SDD/BDD 方法論ガイド
2. [Partial] Prompt Injection 検出 hook
3. [Gap] llms.txt / machine-readable 形式
4. [Gap] チートシート
5. [Partial] リソース評価の体系化
6. [Gap] 自己評価クイズ
7. [Partial] Mermaid ダイアグラム集

## Plan

docs/plans/2026-03-22-ultimate-guide-absorption.md に記載
