---
source: https://nonstructured.com/zen-of-ai-coding/
date: 2026-03-23
status: integrated
---

## Source Summary

**著者**: Yoav Aviram（WhiteBoar 共同創業者）
**公開日**: 2026-03-02

AIコーディング時代の16原則を提唱。コードの限界費用崩壊に伴い、価値の重心が「実装」から「判断・設計・フィードバックループ・失敗予測」へ移行するという主張。

**主要な手法**:
- タイトなフィードバックループ（テスト→CI/CD→ログの3層）
- 暫定アーキテクチャ（リファレンス実装 > 抽象仕様）
- マルチモデルレビュー（異なるモデルが異なる問題を発見）
- 速度の規律（Fast rubbish is still rubbish）
- エージェント向けサービス設計（AX is the new UX）
- 失敗モードの事前予測（ガードレール・監視・権限分離）

**前提条件**: AI エージェントが主要スタックで competent に動作する環境。著者はAIエージェント企業の共同創業者であり、エージェント導入のポジティブ面に重心がある点に留意。

## Gap Analysis

| # | 原則 | 判定 | 根拠 |
|---|------|------|------|
| 1 | Software development is dead | Already | CLAUDE.md: Plan→Implement フロー |
| 2 | Code is cheap | Already | completion-gate.py, /review 並列レビュー |
| 3 | Refactoring is easy | Already | /spike スキル |
| 4 | So is repaying technical debt | Already | /refactor-session スキル |
| 5 | All bugs are shallow | Already | codex-reviewer + code-reviewer 並列、非対称コンテキスト |
| 6 | Create tight feedback loops | Already | workflow-guide.md 6段階プロセス |
| 7 | Any stack is your stack | N/A | 当セットアップ自体がスタック横断ツール |
| 8 | Agents are not just for coding | N/A | dotfiles はコーディングツール設定リポジトリ |
| 9 | Context bottleneck is in your head | Already | subagent-delegation-guide.md: Task Parallelizability Gate |
| 10 | Build for a changing world | Partial | delegation rules でマルチモデル対応。モデル追加手順が暗黙的 |
| 11 | Buy vs. Build → Build | N/A | プロダクト戦略。スコープ外 |
| 12 | Fast rubbish is still rubbish | Already | KISS/YAGNI/overconfidence-prevention.md |
| 13 | Software is liability | N/A | comprehension-debt-policy.md が部分カバー |
| 14 | Moats are more expensive | N/A | ビジネス戦略。スコープ外 |
| 15 | Build for agents (AX) | Partial | aci-tool-design.md に ACI あり。AX 観点なし |
| 16 | Anticipate modes of failure | Already | agency-safety-framework.md + failure-taxonomy.md |

## Integration Decisions

- **#15 AX 観点**: `references/aci-tool-design.md` に AX 設計チェックリストを追加。エージェントがサービスの消費者として利用する場合の6項目チェックリスト
- **#10 モデル切替え柔軟性**: `references/workflow-guide.md` に「新モデル追加ランブック」を追加。delegation rule 作成から agent-router 更新までの5ステップ手順

## Plan

| タスク | 対象ファイル | 規模 |
|--------|-------------|------|
| AX チェックリスト追加 | `references/aci-tool-design.md` | S |
| 新モデル追加ランブック | `references/workflow-guide.md` | S |
