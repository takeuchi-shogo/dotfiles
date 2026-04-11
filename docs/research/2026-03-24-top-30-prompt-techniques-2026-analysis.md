---
source: "Top 30 Prompt Techniques That Actually Work in 2026 (darkzodchi / zodchiii)"
date: 2026-03-24
status: skipped
---

## Source Summary

### 主張
Claude 4.6 向けのプロンプト技法30個を紹介。「2024年のプロンプティングは古い」として、最新モデルに適した手法を提唱。

### 手法（構造化抽出）
- **Part 1 (基礎10個)**: 明示的指示、XML タグ、Context-first 配置、Few-shot examples、WHY の説明、「わからない」許可、出力形式指定、完了条件定義、否定制約、反復前提
- **Part 2 (上級10個)**: Extended thinking、Prompt chaining、Context files (.md)、Contract 型 system prompt、Reverse brainstorming、Self-evaluation loop、Prefill 廃止（主張）、1M context window 活用、Agent-mode prompting、Multi-persona debate
- **Part 3 (テンプレート10個)**: Code review / Research / Writing / Debugging / Architecture / Data analysis / Email / Learning / Creative brainstorm / Full template

### 根拠の評価
- 「30%+ 改善」の数値主張が2箇所あるが、測定方法・ベンチマーク・引用元なし
- 「Prefill Is Dead」は公式アナウンスへの参照なし。API changelog で未確認
- 「Karpathy の agentic engineering」は具体的引用なし
- Dario Amodei の Davos 2026 発言は引用元動画未確認

### 前提条件
- 対象読者: Claude Code / API の初心者〜中級者
- コンテンツマーケティング記事（Telegram チャンネル誘導あり）
- 技術的正確性より読みやすさ・拡散性を優先した構成

## Gap Analysis

| # | 技法 | 判定 | 根拠 |
|---|------|------|------|
| 1 | Be Explicit | Already | CLAUDE.md `core_principles` + スキル/エージェント定義 |
| 2 | XML Tags | Already | CLAUDE.md が `<important if>`, `<core_principles>` 等で構造化 |
| 3 | Context First | Already | Progressive Disclosure (CLAUDE.md -> references -> rules) |
| 4 | Few-Shot Examples | Already | `evaluator-calibration-guide.md`, Good/Bad 併記パターン |
| 5 | Explain WHY | Already | `harness-rationale.md`, 各指示に理由添付 |
| 6 | "I Don't Know" | Already | `derivation-honesty.md`, `overconfidence-prevention.md` |
| 7 | Output Format | Already | スキルごとに `templates/` で出力形式定義 |
| 8 | "Done" Definition | Already | `completion-gate.py`, `graduated-completion.md`, `/verification-before-completion` |
| 9 | Negative Constraints | Already | `constraints-library.md`, Anti-Patterns セクション, rules/ deny |
| 10 | Iterate | Already | Plan -> Implement -> Review -> Verify の反復構造 |
| 11 | Extended Thinking | Already | Codex delegation で reasoning effort 制御 |
| 12 | Prompt Chaining | Already | EPD (Spec->Spike->Validate->Build->Review), `/rpi` |
| 13 | Context Files | Already | CLAUDE.md + references/ + rules/ + agents/ 多層構造 |
| 14 | Contract Prompt | Already | `agents/*.md` が Role/Goal/Constraints/Output 構造 |
| 15 | Reverse Brainstorming | Already | `codex-risk-reviewer.md` failure mode, brainstorming skill |
| 16 | Self-Evaluation | Already | `/review` 並列レビューア + `completion-gate.py` |
| 17 | Prefill Is Dead | N/A | CLI 利用のため無関係。記事の主張も未検証 |
| 18 | 1M Context | Already | Gemini skill (1M), `gemini-delegation.md` |
| 19 | Agent-Mode | Already | `workflow-guide.md` Plan->Implement->Review->Verify |
| 20 | Multi-Persona | Already | `/debate` skill + `debate-personas.md` |
| 21-30 | Templates | Already | 各スキルが専用テンプレート保持。記事より高機能 |

## Integration Decisions

全30項目が Already または N/A。統合対象なし。

### 判断理由

記事は「個人が手動で適用するプロンプトテクニック集」であり、当セットアップは同じ原則を「システムレベルの自動化」として実装済み。具体的な差異:

1. **手動 vs 自動**: 記事は各技法を毎回手動適用する前提。当セットアップは hooks/skills/agents で自動適用
2. **単発 vs 多層**: 記事は1つの技法を1箇所に適用。当セットアップは同じ原則を複数レイヤーで強制（例: 「不確実なら明示」→ derivation-honesty rule + overconfidence-prevention rule + completion-gate hook）
3. **テンプレート vs ワークフロー**: 記事の Part 3 はコピペ用テンプレート。当セットアップはテンプレートをスキルのワークフロー内に組み込み、前後の検証ステップと連動

### 記事の批判的評価（調査メモ）

- 30項目のうち Claude 4.6 固有の知見は実質ゼロ。大半は 2023-2024 年から知られた汎用手法
- Part 3 (10テンプレート) を「techniques」に数えるのは水増し
- 「30%+」の定量的主張は再現不能（測定方法・ベンチマーク不明）
- Telegram チャンネル誘導を含むコンテンツマーケティング記事としてのバイアスあり
- 初心者向けのまとめとしては悪くないが、経験者には既知の内容

## Plan

なし（統合対象なし）
