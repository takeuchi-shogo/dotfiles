---
source: "AI Agent Traps" (Franklin et al., Google DeepMind, SSRN 6372438)
date: 2026-04-02
status: analyzed
---

## Source Summary

### 主張
自律型AIエージェントがWeb上で活動する際、**情報環境そのものが攻撃面**（Agent Traps）になる。Webページや外部リソースに埋め込まれた敵対的コンテンツがエージェントを誤誘導・悪用する脅威を、エージェントの機能アーキテクチャに基づく6カテゴリで体系的に分類した初の論文。

### 手法（6カテゴリ・22攻撃ベクトル）

**1. Content Injection Traps** (Target: Perception)
- Web-Standard Obfuscation: CSS/HTML隠蔽（display:none, aria-label, viewport外配置）→ WASP ベンチで最大86%部分制御
- Dynamic Cloaking: サーバー側でエージェント指紋認証し、人間とは別コンテンツ配信
- Steganographic Payloads: 画像バイナリ内に命令埋込
- Syntactic Masking: Markdown/LaTeX構文で命令を隠蔽

**2. Semantic Manipulation Traps** (Target: Reasoning)
- Biased Phrasing & Framing: 権威的・感情的表現でフレーミング効果を悪用
- Oversight & Critic Evasion: 「教育目的」「セキュリティ監査」フレーミングで安全フィルタ回避
- Persona Hyperstition: モデルの「人格」ナラティブがフィードバックループ化（Grok "RoboStalin"、Claude "spiritual bliss"）

**3. Cognitive State Traps** (Target: Memory & Learning)
- RAG Knowledge Poisoning: 検索コーパスに偽情報注入
- Latent Memory Poisoning: 内部メモリに時限爆弾的データ注入（0.1%未満の汚染で80%超の攻撃成功率）
- Contextual Learning Traps: few-shot例・報酬シグナルの汚染

**4. Behavioural Control Traps** (Target: Action)
- Embedded Jailbreak Sequences: 外部リソース内に dormant jailbreak
- Data Exfiltration Traps: confused deputy 攻撃で機密漏洩（成功率80%超）
- Sub-agent Spawning Traps: 悪意あるサブエージェント生成を誘発（成功率58-90%）

**5. Systemic Traps** (Target: Multi-Agent Dynamics)
- Congestion Traps / Interdependence Cascades / Tacit Collusion / Compositional Fragment Traps / Sybil Attacks

**6. Human-in-the-Loop Traps** (Target: Human Overseer)
- Approval Fatigue 誘発、Automation Bias 悪用、フィッシングリンク誘導

### 根拠
280件の静的Webページデータセット、WASPベンチマーク（86%部分制御）、AndroidWorld（93%攻撃成功率）、メモリポイズニング（0.1%汚染で80%成功率）、Sub-agent Spawning（58-90%成功率）等の実証データ。

### 前提条件
エージェントが外部の非信頼コンテンツ（Web、MCP、外部リポジトリ）を推論時に取り込む環境で有効。閉じた環境やオフライン環境では一部脅威が不適用。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Latent Memory Poisoning | **Gap** | メモリファイル(.md)に整合性検証なし |
| 2 | Syntactic Masking | **Partial** | zero-width/ANSI/null/base64は検出、Markdown/LaTeX隠蔽は未対応 |
| 3 | Approval Fatigue | **Gap** | MAX_RETRIES=2はあるが、認知疲労誘発攻撃への対策なし |
| 4 | Dynamic Cloaking | N/A | Webブラウジングエージェント向け |
| 5 | Steganographic Payloads | N/A | 画像を命令として処理しない |
| 6 | RAG Knowledge Poisoning | N/A | RAG未使用 |
| 7 | Systemic Traps (5種) | N/A | 単一ユーザー環境 |
| 8 | Contextual Learning Traps | **Partial** | skills内のfew-shotは管理下、外部コンテンツ経由のICL歪みへの明示的ガードなし |

### Already 項目の強化分析

| # | 既存の仕組み | 論文が示す弱点 | 強化案 |
|---|-------------|-------------|--------|
| A1 | mcp-response-inspector.py | CSS display:none, aria-label, viewport外配置を未検出 | HTML構造パターンの検出正規表現追加 |
| A2 | Depth-1 Rule | サブエージェントプロンプトへの外部コンテンツ混入は未考慮 | subagent-delegation-guide.md に注意喚起追記 |
| A3 | agency-safety-framework.md (認知バイアス3種) | Framing Effect, Lost in the Middle, 感情的コンテキスト未記載 | バイアステーブル拡張 |
| A4 | Codex Review Gate (dual-model) | 「教育目的」フレーミングでcritic回避可能 | reviewerプロンプトにCritic Evasion耐性注記 |
| A5 | claude-code-threats.md | Compositional Fragment Traps未記載 | 脅威カタログ拡張 |
| A6 | prompt-injection-detector.py | 外部リソース内のdormant jailbreakはPreToolUseで検出不可 | mcp-response-inspector.pyの検出パターン拡充 |

## Integration Decisions

全10項目を選択:
- Gap/Partial: #1 (Latent Memory Poisoning), #2 (Syntactic Masking), #3 (Approval Fatigue), #8 (Contextual Learning)
- Already強化: A1-A6 すべて

## Plan

See: `docs/plans/2026-04-02-agent-traps-integration.md`
