---
source: https://arxiv.org/abs/2604.01194v1
date: 2026-04-04
status: integrated
---

## Source Summary

### 主張

プロンプトインジェクション検出は、コンテキスト全体ではなく因果的に重要な断片に絞り、明示的ルールで判定することで、長文でもスケールし説明可能になる。

### 手法

- **Context Attribution**: Transformer の attention 重みを利用し、因果的に重要なコンテキスト断片を特定。スライディングウィンドウ方式で sink token を検出し、K 個の非重複ウィンドウを圧縮コンテキスト C* として抽出
- **10種ルールベース検出**: instruction hijacking, system override, credential theft, resource exfiltration, output manipulation, attention diversion, task expansion, unrelated requests, external redirection, system spoofing
- **ベナインルール**: タスク遂行に必要なツール呼び出し、タスク完了のためのコンテキスト命令、タスク指定ソースのコンテンツ、流出指示を伴わない機密情報の存在
- **GRPO ファインチューニング**: 20,000サンプル、BLEUベース報酬。訓練中にルール引用率が自発的に創発
- **説明可能な出力**: 推論プロセス + バイナリ判定 + 悪意テキスト抽出

### 根拠

- 4 エージェントベンチマーク（AgentDojo ASR 0.01, InjecAgent 0.04, WASP 0.02, AgentDyn 0.00）
- 6 長文コンテキストデータセットで最低または準最低 ASR
- 6 LLM ファミリ（Qwen, GPT-4, Claude, Gemini）でクロスモデル汎化: ASR ≤ 1%, Utility 低下 ≤ 4%
- DataSentinel, PromptGuard, PIGuard, GPT-OSS-Safeguard を全て上回る

### 前提条件

- Transformer ベース LLM（attention 重みへのアクセスが必要）
- A100 GPU で約 8.2 秒/検出（選択的適用が前提）

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Context Attribution（attention ベース因果コンテキスト特定） | Gap | 未実装。全テキストに正規表現を適用する方式 |
| 2 | 10種ルール分類体系 | Partial | `mcp-response-inspector.py` に regex パターンはあるが体系的10種分類は未整理 |
| 3 | ベナインルール（偽陽性抑制の明示的ルール） | Partial | hook に例外ロジックはあるが「何が正常か」の明示的定義がない |
| 4 | GRPO ファインチューニング | N/A | ローカルモデルの fine-tuning は当環境のスコープ外 |
| 5 | スライディングウィンドウ sink token 検出 | N/A | attention 重みへのアクセスが必要、API 利用では不可 |
| 6 | ルール引用による説明可能な検出理由 | Gap | 検出時は stderr/ログに記録のみ。構造化された推論チェーンなし |

### Already 項目の強化分析

| # | 既存の仕組み | 論文が示す弱点 | 強化案 |
|---|-------------|-------------|--------|
| A1 | `prompt-injection-detector.py`（正規表現） | 長文で偽陽性増加 | MCP レスポンスの直近 N 行にスキャン範囲を限定するオプション |
| A2 | `mcp-response-inspector.py`（soft warning のみ） | binary decision + 悪意テキスト抽出が推奨 | 高信頼度パターンに block モード追加 |
| A3 | `security-reviewer` agent（Blind-first） | ルールセットに照らした体系的チェックが推奨 | 10種ルール分類をチェックリスト reference として追加 |
| A4 | `agent-security` wiki | AgentWatcher の知見未反映 | wiki 記事に論文知見を追記 |
| A5 | `agency-safety-framework.md` | ルール引用創発は Blind-first と相補的 | 構造化ルール準拠推論パターンを reference に追記 |

## Integration Decisions

全項目を取り込み:

1. **[Partial→統合] 10種ルール分類体系** — `references/injection-rule-taxonomy.md` 新規作成
2. **[Partial→統合] ベナインルール** — 上記 reference にベナインルール4種を含める
3. **[Gap→統合] 検出理由の構造化** — `mcp-response-inspector.py` のログに該当ルール ID を付記
4. **[強化] mcp-response-inspector block モード** — 環境変数で段階的昇格
5. **[強化] security-reviewer チェックリスト** — `review-checklists/injection-rules.md` 新規作成
6. **[強化] agent-security wiki 更新** — AgentWatcher の知見追記

## Plan

| # | タスク | 対象ファイル | 依存 |
|---|--------|-------------|------|
| T1 | 10種ルール分類 + ベナインルール reference | `references/injection-rule-taxonomy.md`（新規） | — |
| T2 | security-reviewer チェックリスト | `references/review-checklists/injection-rules.md`（新規） + `agents/security-reviewer.md`（参照追加） | T1 |
| T3 | mcp-response-inspector block モード + ルール ID ログ | `scripts/policy/mcp-response-inspector.py`（修正） | T1 |
| T4 | agent-security wiki 更新 | `docs/wiki/concepts/agent-security.md`（修正） | T1 |
