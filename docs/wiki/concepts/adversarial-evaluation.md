---
title: 敵対的評価
topics: [security, evaluation]
sources: [2026-03-27-harness-v2-adversarial-honesty-deep-analysis.md, 2026-03-23-verigrey-greybox-agent-validation-analysis.md, 2026-04-02-ai-agent-traps-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 11
confidence: established
---

# 敵対的評価

## 概要

敵対的評価（Adversarial Evaluation）は、AIエージェントの品質・安全性・堅牢性をストレステストするための手法群である。Generator-Evaluator分離による自己評価バイアスの排除、グレーボックスファジングによる脆弱性発見、Agent Traps（情報環境そのものを攻撃面とした誘導手法）への防御が3つの柱となる。dotfilesでは`codex-reviewer`/`security-reviewer`のBlind-first評価、`prompt-injection-detector.py`、`completion-gate.py`によってこれらを実装している。

## 主要な知見

- **Generator-Evaluator分離の必然性** — 「Claudeは平凡な作品を素晴らしいと自画自賛する」（Anthropic公式告白）。自己評価バイアスはモデル能力向上でも解消しない構造的問題
- **Evaluator Rationalization（FM-018）** — QAエージェントが正当な問題を発見しても「大したことない」と自分を納得させて承認するパターン
- **Harness v1→v2の教訓** — Sprint構造・Contract Negotiationは除去されたが、Generator-Evaluator分離とDefinition of Doneは除去されなかった
- **VeriGreyグレーボックスファジング** — ツール呼び出しシーケンスをカバレッジ指標として使い、ブラックボックス比+10〜90ppのインジェクション発見率
- **コンテキストブリッジング攻撃** — 悪意あるタスクをユーザーの本来タスクに文脈接続する変異。除去すると-25.8ppの発見率低下
- **Agent Traps 6カテゴリ** — Content Injection / Semantic Manipulation / Cognitive State / Behavioural Control / Systemic / Human-in-the-Loop
- **Latent Memory Poisoning** — 0.1%未満のコーパス汚染で80%超の攻撃成功率。RAGを持つエージェントの深刻な脆弱性
- **Sub-agent Spawning Traps** — 悪意あるサブエージェント生成誘発で58〜90%の成功率
- **Tool Filter防御** — ITSRを最も下げつつUTSRへの影響が最小。タスクスコープ動的ホワイトリストが最有効策
- **Controllability分離とTwo-pass scoring** — Computer Use Agent検証器では、エージェント自身のミスと環境障害（CAPTCHA等）を明示的に二値分類し、テキストアクションとスクリーンショットを突き合わせるTwo-pass scoringでハルシネーションを検出する
- **Self-preference Biasと異モデル評価の必須化** — 同モデルファミリーの評価者は生成物を甘く評価する構造的バイアスがある（Reward Hacking・Holdout Contamination・Evaluator Driftと並ぶ既知リスク）。対策としてsession_id切替だけでなく異ベンダーの評価者を必須化し、local memoryを分離する契約を明記する
- **Hallucination Defenseとfile:line specificity閾値** — LLMによる監査は虚偽のfile:line引用（存在しない行の指摘）を生成しうるため、最低1関数・±10行の具体性閾値を設け、複数エージェント間の判断不一致は「両論併記」で残しconflictを隠さない
- **Tri-judge panelによるself-preference bias相殺とoutcome-over-trajectory原則** — Anthropic/OpenAI/Googleなど3ベンダー横断の評価パネルでバイアスを相殺し、評価は経路（ツール呼び出し回数・リトライ）ではなく最終成果のみで判定する。ただし儀式化（人手校正の定例化・9次元severityダイヤル化）は個人ハーネスでは過剰
- **Silent success監査の実害発見** — `except: pass`によるエラー握り潰しやtestランナー例外時の`return True`（silent成功扱い）は、file:line単位の深い推論でしか発見できない実害であり、fail loud原則（サイレントスキップ・サイレント成功の禁止）で塞ぐ
- **Citation hallucinationへの警戒** — 同じ質問でGemini groundingを2回独立実行すると、結論は一致するが引用URLが完全にdisjoint（別物）になるケースがあり、grounding結果を単独の採用根拠にしてはならない

## 実践的な適用

dotfilesでの実装状況：

| 手法 | 実装状況 | 担当コンポーネント |
|------|---------|-----------------|
| Generator-Evaluator分離 | Implemented | `codex-reviewer` + `code-reviewer`並列レビュー |
| Blind-first評価 | Implemented | `security-reviewer`のadversarial framing |
| Steerable adversarial review | Implemented | `/codex:adversarial-review` |
| プロンプトインジェクション検出 | Partial | `prompt-injection-detector.py`（技術パターンのみ） |
| コンテキストブリッジング検出 | Gap | 自然言語文脈接続型は未検出 |
| MCP出力内容検査 | Gap | `mcp-audit.py`は入力監査のみ |
| ツール呼び出しシーケンス異常検出 | Partial | `stagnation-detector.py`でパターン反復検出 |

`security-reviewer`エージェントにBlind-first + adversarial framingを統合済み。3層プロンプトインジェクション対策は`docs/plans/2026-03-25-3-layer-injection-defense-integration.md`で計画中。

## 関連概念

- [エージェントセキュリティ](agent-security.md) — OWASP MCP Top 10とAgent Trapsの対応関係
- [エージェント評価](agent-evaluation.md) — TPR/TNR/Rogan-Gladen補正を含む評価キャリブレーション
- [品質ゲート](quality-gates.md) — completion-gate.pyとCodex Review Gateの連携

## ソース

- [Harness v2 × Adversarial Evaluation深層分析](../../research/2026-03-27-harness-v2-adversarial-honesty-deep-analysis.md) — Anthropic Harness v1→v2進化とGenerator-Evaluator分離の根拠
- [VeriGrey: Greybox Agent Validation](../../research/2026-03-23-verigrey-greybox-agent-validation-analysis.md) — ツール呼び出しシーケンスをカバレッジ指標としたファジング手法と実験データ
- [AI Agent Traps](../../research/2026-04-02-ai-agent-traps-analysis.md) — 情報環境を攻撃面とした6カテゴリ22攻撃ベクトルの体系的分類
- [The Art of Building Verifiers for Computer Use Agents](../../research/2026-04-10-universal-verifier-cua-analysis.md) — CUA検証器論文を分析、失敗帰属分離など全7項目採用
- [Empirical Prompt Tuning skill](../../research/2026-04-19-empirical-prompt-tuning-absorb-analysis.md) — mizchiのプロンプト評価スキルを分析、tool_uses計測等を優先採用
- [Tech-Debt-Skill (ksimback) absorb分析](../../research/2026-04-26-tech-debt-skill-absorb-analysis.md) — 技術負債監査スキルを分析、/auditへ9項目統合
- [The Self-Healing Agent Harness absorb分析](../../research/2026-04-29-self-healing-harness-absorb-analysis.md) — 自己修復ハーネス記事を分析、outcome-over-trajectory等3件採用
- [12-rule CLAUDE.md absorb分析](../../research/2026-05-10-12-rule-claude-md-absorb-analysis.md) — 12ルールCLAUDE.md記事を分析、silent success監査等2件のみ採用
- [32 Claude Code hacks](../../research/2026-05-31-32-claude-code-hacks-absorb-analysis.md) — 32個のCC hacks記事、ultracode表記追記のみ採用
- [The Self-Verifying Loop: 300 agents, 4,000 steps](../../research/2026-06-20-kimi-k26-self-verifying-loop-absorb-analysis.md) — Kimiベンダー第2弾記事も全rehash、採用0確定
- [Position: Coding Benchmarks Are Misaligned with Agentic Software Engineering](../../research/2026-07-04-coding-benchmarks-misaligned-absorb-analysis.md) — ベンチマーク不整合position paperは既存哲学と一致、採用0だが引用価値あり
