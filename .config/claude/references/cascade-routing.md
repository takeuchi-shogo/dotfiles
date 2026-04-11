# Cascade Routing — Promotion Gate Convention

> **Online cascade**: 安いモデルで試行 → 品質判定 → 昇格 (expensive model へ) または停止。
>
> **着想元**: Chen et al. "FrugalGPT" (Stanford, 2023) および
> "The New Software: CLI, Skills & Vertical Models" (2026-04) の指摘。
> FrugalGPT はカスケード呼び出しで GPT-4 相当の精度を最大 **98% のコスト削減**で達成した。
> 現セットアップの `agent_delegation` は**静的** tier routing (このタスクは Haiku、これは Opus 等)。
> **動的** な promotion gate (試して→判定→昇格) は別レイヤーとして必要。

## 既存との差分

`cascade-parse-strategy.md` は **出力パース失敗時** のリトライ戦略 (同一モデル内での JSON 修復)。
本 convention は **モデル間の昇格** を扱う (Haiku → Sonnet → Opus/Codex)。
両者は補完関係: parse が安定した後に quality-based escalation が走る。

## Convention

Opus がカスケードを意図して子エージェントを起動するとき、`description` に以下のマーカーを含める:

```
[cascade:<name>/step:<N>] <human-readable description>
```

- `<name>`: カスケードの識別子 (例: `article-extract`, `typo-review`)
- `<N>`: 試行番号 (1 から開始)
- 複数の step 呼び出しは同じ `<name>` で linking される

### 例

```python
# Step 1: cheap model で extraction を試行
Agent(
    description="[cascade:article-extract/step:1] JSON抽出",
    model="haiku",
    subagent_type="general-purpose",
    prompt="..."
)

# Step 1 の結果を見て、format violation / empty / 低信頼と判定した場合
# Step 2: 昇格
Agent(
    description="[cascade:article-extract/step:2] JSON抽出 (Haiku失敗後)",
    model="sonnet",
    subagent_type="general-purpose",
    prompt="..."
)
```

## Promotion Criteria (何が昇格 trigger になるか)

Opus が step:1 の結果を見て step:2 へ進むかどうかは以下で判断:

| Trigger | 判定基準 | 次のモデル |
|---------|---------|----------|
| Format violation | 期待 JSON/YAML スキーマと不一致 (2 段階以上の parse 失敗) | 同じ tier の別モデル or 1 tier up |
| Empty result | 空配列/空オブジェクト/"N/A" 等 | 1 tier up |
| Low confidence marker | 出力に "I'm not sure", "ambiguous", "?" 等が多発 | 1 tier up |
| Timeout | agent execution が期待時間の 2x を超過 | 停止 → 別アプローチ検討 |
| Manual review flag | Opus が「これは怪しい」と判断 | 1 tier up または Codex 批評 |

**停止 (Stop) 条件**:
- step:3 に到達しても解決しない場合、ユーザーに `AskUserQuestion` で状況報告
- カスケード全体のトークン消費が skill 単体の予算を超えた場合 (`references/resource-bounds.md` 参照)

## Observation — agent-invocations.jsonl への記録

`scripts/runtime/agent-invocation-logger.py` が description から `[cascade:<name>/step:N]` を抽出し、
`agent-invocations.jsonl` にフィールド `cascade_name` と `cascade_step` を追加する。

集計はダウンストリーム:
- **AutoEvolve `/improve` cycle**: カスケードの成功/失敗パターンを集計し、promotion gate の閾値を提案
- **skill-audit Dominant tier 検出**: 特定 skill の cascade 試行が常に step:2+ に到達する場合、default tier を昇格することを提案
- **Routing Observability Wave 2** (`docs/plans/2026-04-11-routing-observability-closed-loop.md`): attribution phase で cascade chain 単位の outcome quality を紐付け

## Anti-Patterns

| NG | 理由 |
|----|------|
| 全ての Agent 呼び出しに cascade marker を付ける | marker は「昇格の可能性がある場合」のみ。単発呼び出しでは冗長 |
| step:N を再利用する (同一 cascade_name で step:1 を 2 回) | 集計が壊れる。必ず step を monotonic に増やす |
| static tier と cascade を混同する | 「静的に Haiku にルート」は `agent_delegation` の担当。本 convention は**動的昇格** |
| promotion criteria を厳密化しすぎる | Opus の判断を信頼する。hard rule 化すると硬直化する |

## Deletion Trigger

このファイルは debt である。以下の条件で削除検討:

- AutoEvolve が cascade 実績から**自動で** tier routing を調整できるようになること
- かつ、手動の `[cascade:...]` マーカーなしに同等の観測性が得られること

`model-debt-register.md` R-004 と連動する。

## Related

- `cascade-parse-strategy.md` — 出力パース層 (JSON 修復)
- `model-debt-register.md` — model-specific rules の debt 管理
- `scripts/runtime/agent-invocation-logger.py` — marker のパース実装
- `docs/plans/2026-04-11-routing-observability-closed-loop.md` — 計測→attribution→closed-loop の3 Wave
