---
name: debate
description: >
  複数AIモデル(Codex/Gemini)に同じ質問を投げ、独立した視点を収集・統合する。
  Triggers: 'AとBどちらが良い', 'トレードオフ', 'trade-off', '比較して', 'pros and cons',
  'この設計の問題点', 'セカンドオピニオン', 'second opinion', '技術選定', 'which is better'.
  Do NOT use for factual questions with clear answers — use WebSearch or gemini skill instead.
origin: self
allowed-tools: Read, Bash, Grep, Glob, Agent
metadata:
  pattern: pipeline
---

# Multi-Model Debate

複数の AI モデルに同じ質問を投げ、clean context の独立した視点を収集し、人間の判断を支援するスキル。

**設計原則**: 人間がオーケストレーター。このスキルは「視点を集めて整理する」だけで、最終判断は人間が行う。

## Workflow

```
1. Question   → ユーザーの質問を明確化
2. Dispatch   → Codex + Gemini に並列投入
3. Collect    → 各モデルの回答を収集
4. Synthesize → 合意点・相違点・独自洞察を整理
5. Present    → 人間に判断材料を提示
```

## Step 1: Question — 質問の整理

ユーザーの質問を以下の形式に整理する:

- **Topic**: 何について判断が必要か
- **Context**: 関連するコード・設計・制約（Read で取得）
- **Alternatives**: 比較対象がある場合は明示

質問を英語のプロンプトに変換する（Codex/Gemini への指示は英語）。

## Step 2: Dispatch — 並列投入

Agent ツールで以下を **1メッセージに並列起動**:

### Codex（深い推論・リスク検出）

```bash
codex exec --skip-git-repo-check -m gpt-5.5 \
  --config model_reasoning_effort="high" \
  --sandbox read-only \
  "{english_prompt}" 2>/dev/null
```

### Gemini（広い視野・エコシステム知識）

```bash
gemini --approval-mode plan -p "{english_prompt}" 2>/dev/null
```

**重要**: 各モデルには同じ質問と同じコンテキストを渡す。独立した判断を得るために、他モデルの回答は見せない。

## Step 3: Collect — 回答収集

各モデルの回答を受け取る。回答が空やエラーの場合:
- Codex 失敗 → Gemini + Claude の2者で進行
- Gemini 失敗 → Codex + Claude の2者で進行
- 両方失敗 → Claude 単独で回答（debate は成立しない旨を報告）

## Step 4: Synthesize — 統合

### 4a. ドメイン判定と Expertise Weighting

1. 質問のドメインを `references/model-expertise-map.md` の Domain Classification Guide に基づき判定する
2. 判定したドメインの各モデルの expertise score を取得する
3. 統合時、各モデルの意見に expertise score で重み付けする: `weighted_opinion = opinion * expertise_score[model][domain]`
4. 重み付けは最終的な推奨の優先度に影響するが、情報の除外は行わない（全意見を提示）

> 根拠: HACRL (arXiv:2603.02604) の Exponential IS — 出力分布が近いエージェントからの学習を優先する。

### 4b. 統合整理

Claude として以下を整理する:

1. **合意点 (Agreement)**: 両モデルが同じ結論に達した点
2. **相違点 (Disagreement)**: 異なる結論や推奨（各モデルの根拠を併記）。expertise score が高いモデルの意見を先に記載
3. **独自の洞察 (Unique Insights)**: 片方だけが指摘した重要な点。expertise score を付記
4. **合意率**: 合意点 / (合意点 + 相違点) × 100%
5. **Claude の所見**: オーケストレーターとして気づいた補足（任意）

## Step 5: Present — 出力フォーマット

```markdown
## Debate: {topic}

### Domain: {domain} (Expertise: Codex {codex_score}, Gemini {gemini_score})

### Codex の視点 (深さ)
{codex_summary}

### Gemini の視点 (幅)
{gemini_summary}

---

### 合意点
- {point}: 両モデルとも {conclusion}

### 相違点
- {point}: Codex → {position_a} / Gemini → {position_b}

### 独自の洞察
- [Codex] {insight}
- [Gemini] {insight}

### 合意率: {N}%

### Claude の所見
{optional_claude_observation}
```

## Debate スタイル

| スタイル | 使い方 | reasoning_effort |
|---------|--------|-----------------|
| **quick** | 素早い初期判断。5分以内 | medium |
| **thorough** | 深い分析。設計判断に | high |
| **adversarial** | 各モデルに相手の主張への反論を追加投入 | high |

### adversarial モード（オプション）

Step 3 の後、追加ラウンドを実行:
- Codex に「Gemini はこう言っている。反論せよ」
- Gemini に「Codex はこう言っている。反論せよ」
- 再度統合して最終的な合意率を算出

## Language Protocol

- Codex/Gemini への指示は英語
- ユーザーへの報告は日本語
- コードや技術用語は原文のまま

## When to Use

- 「A と B どちらが良い？」— 技術選定、ライブラリ比較
- 「この設計の問題点は？」— アーキテクチャレビュー
- 「この計画に穴はないか？」— Plan 批評（L規模の Plan Second Opinion の発展形）
- 「このアプローチで合っているか？」— 方針確認

## When NOT to Use

- 単純な事実確認（→ WebSearch や context7）
- コード実装（→ 直接書く）
- バグ修正（→ debugger / codex-debugger）
- **レイテンシ敏感 / streaming 応答が必要な場面** — /debate は MoA パターン (Proposer 並列 → Aggregator 統合) であり、最終層の Aggregator が first token を決めるまで応答開始できない (TTFT penalty)。バッチ処理・壁打ちには向くが、インタラクティブ応答には不向き (出典: Wang et al. "Mixture-of-Agents Enhances LLM Capabilities" ICLR 2025 — failure mode #1)
- **コスト敏感 / トークン予算がタイトな場面** — 複数モデル呼び出しで単一モデルの 3-7 倍の API コスト。/debate を呼ぶ前に「本当に複数視点が必要か」を自問する

## Skill Assets

- 討論結果テンプレート: `templates/debate-synthesis.md`
- 討論スタイルガイド: `references/debate-styles.md`

## Anti-Patterns

| NG | 理由 |
|----|------|
| 明確な正解がある質問に使う | 事実確認は WebSearch で十分。debate はトレードオフ判断用 |
| モデル間の多数決で決める | 多数＝正しいではない。論拠の質で判断する |
| 結果を統合せず個別回答を並べる | 合成なしの並列出力は判断材料にならない |
