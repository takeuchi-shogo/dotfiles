---
source: https://arxiv.org/abs/2511.04427
title: "Speed at the Cost of Quality: How Cursor AI Increases Short-Term Velocity and Long-Term Complexity in Open-Source Projects"
authors: Hao He, Courtney Miller, Shyam Agarwal, Christian Kästner, Bogdan Vasilescu
venue: MSR '26 (23rd International Conference on Mining Software Repositories)
date: 2026-03-18
status: analyzed
---

## Source Summary

806 の GitHub リポジトリを対象に、Cursor 導入の因果効果を差分の差分法（DiD）で推定した大規模実証研究。
**核心的発見**: Cursor は短期的な開発速度を大幅に上げるが、コード品質を持続的に劣化させ、
その品質劣化が長期的な速度低下を引き起こす自己強化サイクルを生む。

## Key Findings

### 1. 速度向上は一過性

| 期間 | Lines Added | Commits |
|------|-------------|---------|
| 1ヶ月目 | **+281%** | +55.4% |
| 2ヶ月目 | +48.4% | +14.5% |
| 3ヶ月目以降 | 有意差なし | 有意差なし |
| 全体ATT | +28.6% (±13.7%) | +2.63% (非有意) |

### 2. 品質劣化は持続的

| 指標 | 全体ATT | 傾向 |
|------|---------|------|
| Static Analysis Warnings | **+30.3%** (±6.66%) | 持続・強化 |
| Code Complexity (認知的複雑度) | **+41.6%** (±7.62%) | 持続・強化 |
| Duplicate Line Density | +7.03% (非有意) | — |

### 3. 品質→速度の因果チェーン (Panel GMM)

- コード複雑度 100% 増 → 将来の Lines Added **64.5% 減少**
- Static Analysis Warnings 100% 増 → 将来の Lines Added **50.3% 減少**
- Cursor の速度向上は、警告 ~5x 増 or 複雑度 ~3x 増で完全に相殺される

### 4. 自己強化サイクル

```
Cursor 導入 → 速度大幅向上(一過性)
           → 技術的負債蓄積(持続的)
           → 複雑度・警告増加
           → 将来の速度低下
           → さらなる負債蓄積...
```

## Implications

### ツール設計者への提言
- **品質保証を第一級市民にする**: "Quality assurance needs to be a first-class citizen in the design of agentic AI coding tools"
- AI コーディングツールに静的解析・複雑度チェックを組み込むべき

### 実践者への提言
- **意図的なプロセス適応が必要**: "Deliberate process adaptations—those that scale quality assurance with AI-era velocity—are necessary to realize sustained benefits"
- AI 時代の速度に合わせて QA をスケールさせる仕組みが不可欠

## 方法論の信頼性

- Borusyak et al. (2024) imputation estimator による差分の差分法
- 傾向スコアマッチング（AUC 0.83–0.91）
- Sargan テスト（計器変数妥当性）、AR(2) テスト（系列相関なし）合格
- ロバストネスチェック: 高寄稿者サブセット、アクティブリポジトリ、代替ツール汚染除外

## 限界

- `.cursorrules` をコミットしたリポジトリのみ（暗黙的利用は捕捉できない）
- Intent-to-treat 設計（利用強度の異質性を平均化）
- JavaScript/TypeScript/Python 中心（Go/Rust 等は対象外）
- OSS 限定（プロプライエタリへの一般化は不明）
- 急速なLLM進化により、研究期間中のモデル能力が異なる

## Gap Analysis（現 dotfiles 設定との対比）

| # | 論文の知見 | 現状 | 判定 |
|---|-----------|------|------|
| 1 | QA を第一級市民にする | Claude Code: 充実した hook/review 基盤。**Cursor: 最小限の global.mdc のみ** | **Gap** |
| 2 | 静的解析の自動実行 | Claude Code: completion-gate.py。Cursor: 「完了前にlint実行」の指示のみ | **Gap** |
| 3 | コード複雑度の監視 | Claude Code: golden-check.py。Cursor: 明示的な複雑度ガードなし | **Gap** |
| 4 | Plan-first ワークフロー | Claude Code: plan-lifecycle.py。Cursor: 「曖昧なタスクはplan」の指示あり | **Partial** |
| 5 | レビュープロセス | Claude Code: 並列 review agents。Cursor: レビュー指示なし | **Gap** |
| 6 | 言語別ルール | Claude Code: rules/{typescript,python,go,rust}.md。Cursor: 言語別なし | **Gap** |
| 7 | セキュリティルール | Claude Code: security.md + threats.md。Cursor: 基本のみ | **Gap** |
| 8 | Skills/Commands | Claude Code: 60+ skills。Cursor: なし | **Gap** |
| 9 | Subagents | Claude Code: 20+ agents。Cursor: なし | **Gap** |
| 10 | Hooks (自動化) | Claude Code: 15+ hooks。Cursor: なし | **Gap** |

## Integration Decisions

論文の知見 + Cursor 最新機能（Rules, Skills, Subagents, Commands, Hooks）を組み合わせ、
Claude Code で構築済みの QA 基盤を Cursor にも適用する。

### 実装タスク

1. **Rules の充実化**: 言語別ルール、品質ガード、セキュリティルールを `.cursor/rules/` に追加
2. **Skills の導入**: `.cursor/skills/` に review, commit 等の基本スキルを追加
3. **Subagents の導入**: `.cursor/agents/` に verifier, reviewer 等を追加
4. **Commands の導入**: `.cursor/commands/` に PR作成、テスト実行等を追加
5. **Hooks の導入**: `.cursor/hooks.json` で自動 QA ゲートを設定

## References

- [arxiv:2511.04427](https://arxiv.org/abs/2511.04427) — 原論文
- [Cursor Docs: Rules](https://cursor.com/ja/docs/rules) — ルール公式ドキュメント
- [Cursor Docs: Skills](https://cursor.com/ja/docs/skills) — スキル公式ドキュメント
- [Cursor Docs: Subagents](https://cursor.com/ja/docs/subagents) — サブエージェント公式ドキュメント
- [Cursor Blog: Agent Best Practices](https://cursor.com/blog/agent-best-practices) — エージェントベストプラクティス
- [Qiita: Cursor Commands完全ガイド](https://qiita.com/Enokisan/items/cc173e90bb6e8e5468db) — Commands 解説
