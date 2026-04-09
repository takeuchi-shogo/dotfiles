---
source: "https://claude.com/blog/the-advisor-strategy"
date: 2026-04-10
status: integrated
---

## Source Summary

**主張**: 大規模モデル（Opus）をアドバイザーとして小規模モデル（Sonnet/Haiku）の実行部と組み合わせることで、Opusに近い性能を大幅に低いコストで実現できる。Executor が困難な判断に直面した場合のみ Advisor に相談する。

**手法**:
- Advisor-Executor パターン（二層モデル分割、ボトムアップ escalation）
- サーバー側アドバイザーツール（単一 API リクエスト内統合）
- トークン効率化設計（Advisor 出力を 400-700 tokens に制限）
- 動的相談トリガー（Executor が困難検知時のみ呼び出し）
- Advisor response types（plan / correction / stop signal）
- 相談回数上限（max_uses: 3）

**根拠**:
- SWE-bench Multilingual: Sonnet + Opus Advisor が単独 Sonnet より 2.7pt 向上
- BrowseComp: Haiku + Opus Advisor が 41.2%（単独 19.7% の 2倍以上）
- コスト: Haiku + Opus Advisor は単独 Sonnet より 85% 低コスト
- Bolt CEO テスティモニアル:「より優れた建築的決定」

**前提条件**: Executor の自己認識能力、Claude family 内の same-stack 連携、構造化可能なタスク

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Advisor-Executor パターン / 役割分離 | Already | CLAUDE.md `<agent_delegation>` でトップダウン委譲が定義済み。model-expertise-map.md でドメイン×モデルスコアリング |
| 2 | サーバー側アドバイザーツール | N/A | API レベル機能。ローカルハーネスでは直接制御不可。Managed Agents 移行時に再検討 |
| 3 | トークン効率化設計 / コスト最適化 | Already | resource-bounds.md の出力制御系、agent-config-standard.md の max_tokens |
| 4 | 動的相談トリガー | Partial | error-to-codex.py, suggest-gemini.py, change-surface-advisor.py で広義パターンあり。executor 内の同一ループ相談は未実装 |
| 5 | ベンチマーク検証 / 性能測定 | Already | scripts/eval/, benchmark-dimensions.md, AutoEvolve 評価ループ |
| 6 | Advisor response types (plan/correction/stop) | Gap | サブエージェント返却が一律テキスト。stop signal の概念なし |
| 7 | Advisor-mode A/B 評価プロトコル | Partial | eval framework はあるが advisor-mode 専用の比較軸なし |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | `<agent_delegation>` トップダウン委譲 | 記事はボトムアップ設計。Executor が主体的に判断困難を検知 | 中間相談プロトコル + advisor response types を追加 | 強化可能 |
| S2 | resource-bounds.md のグローバル出力制御 | role-specific 制約なし。advisor の max_uses, token cap, no-tools ルールが未定義 | advisor 役割固有の制約を定義 | 強化可能 |
| S3 | scripts/eval/ + benchmark-dimensions.md (Setup Health 6次元) | モデル組み合わせのコスト対性能比較ではない | advisor invocation rate, token share, cost/task 等の計測軸を追加 | 強化可能 |

## Refine (Phase 2.5)

### Codex 批評の主要指摘
- #4 は Gap ではなく Partial（error-to-codex.py 等で広義パターン既存）
- #3, #5 は強化不要ではなく強化可能（role-specific 制約・advisor-mode 評価軸が不足）
- 記事は Claude Platform 固有機能の発表であり、ローカルハーネスとのレイヤー差を先に明示すべき
- 最優先は計測基盤（advisor-mode 評価軸）の整備

### Gemini 周辺調査の主要知見
- **Unknown unknowns 問題**: Executor が「わからないことをわかっていない」場合は相談不可（FrugalGPT, AutoMix, RouteLLM 共通の未解決課題）
- **レイテンシ不均一**: 動的相談は wall clock time コストが別問題
- **先行研究**: FrugalGPT (Stanford), AutoMix (NeurIPS 2024), RouteLLM (ICLR 2025), xRouter (RL), MasRouter (ACL 2025)
- **代替手法**: Speculative Cascades (Google, ICLR 2025) は並列実行でレイテンシ均一性に優れる

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 4 | 動的相談トリガーの強化 | 採用 | 中間相談プロトコルを subagent-delegation-guide.md に追加 |
| 6 | Advisor response types | 採用 | plan/correction/stop の型定義を advisor-strategy.md に記載 |
| 7 | Advisor-mode A/B 評価プロトコル | 採用 | benchmark-dimensions.md に Advisor-Mode 評価セクション追加 |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | 委譲プロトコルに中間相談追加 | 採用 | Pattern 4: Advisor Consultation として追加 |
| S2 | Role-specific 制約の定義 | 採用 | advisor-strategy.md に制約テーブルとして定義 |
| S3 | Advisor-mode 評価軸 | 採用 | benchmark-dimensions.md に6指標追加 |

## Plan

### Task 1: Advisor パターン リファレンス作成
- **Files**: `references/advisor-strategy.md` (NEW)
- **Changes**: response types, role-specific 制約, 既知のトレードオフ, 先行研究を包括的に記載
- **Size**: S

### Task 2: 委譲ガイドに中間相談プロトコル追加
- **Files**: `references/subagent-delegation-guide.md` (EDIT)
- **Changes**: Pattern 4: Advisor Consultation を Pattern 3 の後に追加
- **Size**: S

### Task 3: Advisor-mode 評価軸追加
- **Files**: `references/benchmark-dimensions.md` (EDIT)
- **Changes**: Advisor-Mode 評価セクション（3条件比較 + 6指標）を追加
- **Size**: S
