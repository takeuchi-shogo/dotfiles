---
source: "Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets (arxiv:2604.02460)"
authors: "Dat Tran, Douwe Kiela (Stanford University)"
date: 2026-04-08
status: analyzed
---

## Source Summary

**主張**: マルチエージェント（MAS）のシングルエージェント（SAS）に対する報告されてきた優位性は、計算量の非対称・API トークン水増し・ベンチマーク暗記の3つのアーティファクトで説明できる。thinking token 予算を揃えると SAS が一貫して MAS と同等以上。

**理論基盤**: Data Processing Inequality (DPI) — `I(Y; C) ≥ I(Y; M)`。メッセージパッシングのたびに情報が失われるため、完全コンテキストにアクセスできる SAS は理論上 MAS を下回らない。

**手法**:
1. thinking token 予算（100〜10,000）を揃えた公平比較
2. 3モデルファミリー（Qwen3-30B, DeepSeek-R1-70B, Gemini-2.5-Flash/Pro）× 2データセット（FRAMES, MuSiQue 4-hop）
3. 5つの MAS アーキテクチャ（Sequential, Subtask-parallel, Parallel-roles, Debate, Ensemble）
4. コンテキスト劣化実験（masking, substitution, deletion, distractors）
5. パラフレーズ実験（暗記耐性チェック）

**根拠**: 95% bootstrap CI 付きの定量結果、全モデル・全予算帯で再現

## Key Findings

### 1. メイン結果（全モデル平均）

| 予算 | SAS | Sequential (最強MAS) | 勝者 |
|------|-----|---------------------|------|
| 100 | 0.290 | 0.364 | MAS |
| 500 | 0.390 | 0.376 | SAS |
| 1,000 | 0.418 | 0.379 | SAS |
| 2,000 | 0.421 | 0.389 | SAS |
| 5,000 | 0.427 | 0.386 | SAS |
| 10,000 | 0.426 | 0.387 | SAS |

- 100トークンの極小予算でのみ MAS が勝つ（SAS が十分な推論深度を確保できない）
- 1,000〜2,000トークンで性能が頭打ち — それ以上は収穫逓減
- Debate が MAS の中で最も競争力があるが、予算を揃えた SAS には及ばない

### 2. モデル別結果

- **Gemini-2.5-Pro**: FRAMES 10k で SAS 0.700 vs Sequential 0.690 → 最高性能モデルでも SAS 優位維持
- **DeepSeek-R1-70B**: MuSiQue 5k で SAS 0.419 vs Sequential 0.323 → OSS モデルでは SAS 優位がより顕著
- **Gemini 世代間**: Flash-Lite → 3-Pro-Preview まで全世代で SAS ≥ MAS

### 3. コンテキスト劣化実験（Qwen3, 1kトークン固定）

| 劣化手法 | α=0.3 | α=0.5 | α=0.7 |
|----------|-------|-------|-------|
| Masking | SAS勝ち | 同等 | **MAS勝ち** |
| Substitution | SAS勝ち | 同等 | **MAS勝ち** |
| Deletion | SAS勝ち | 同等 | SAS僅差 |
| Distractors | SAS勝ち | SAS勝ち | SAS勝ち |

- MAS が競争力を持つのは情報が「壊れている」場合（masking/substitution）のみ
- 情報が「消えている」場合（deletion）や妨害情報がある場合は SAS が依然優位
- DPI の理論予測と一致

### 4. エラー分析（Gemini, MuSiQue 1k）

| ケース | 件数 | SAS の特徴 | MAS の特徴 |
|--------|------|-----------|-----------|
| MAS正解/SAS不正解 | 72 | 過少探索（エンティティ4.8個） | 広い探索（エンティティ9.5個）が救う |
| SAS正解/MAS不正解 | 124 | 制約アンカリングで精度維持 | 過剰探索でドリフト |
| 両方正解 | 265 | 収束前に制約再チェック | 同上 |
| 両方不正解 | 714 | 両方とも制約に立ち戻れず漂流 | 同上 |

### 5. Gemini API トークン水増し

- Gemini-2.5-Flash SAS 10k予算: API報告 1,687 vs 推定実トークン 359 → **4.7倍水増し**
- 可視テキスト量は予算増加に関わらず頭打ち（Flash で約350トークンで plateau）
- 既存の MAS 優位性報告はこの水増しによる偽の比較に基づく可能性

### 6. パラフレーズ実験

- 軽いパラフレーズ（正規表現）: 性能低下 — 質問が難読化
- 深いパラフレーズ（LLM意味保存）: 性能向上 — 元の質問に暗記アーティファクトがある証拠

## Gap Analysis (Pass 1: 存在チェック)

| # | 知見 | 判定 | 詳細 |
|---|------|------|------|
| 1 | SAS > MAS（予算揃え） | Already | CLAUDE.md の agent_delegation ルール: Opus は判断・統合に集中、委譲は情報損失を考慮して判断 |
| 2 | Debate が最強 MAS | Already | `/debate` スキルが存在。Codex/Gemini に同じ質問を投げて独立視点を収集 |
| 3 | MAS の価値 = コンテキスト劣化条件 | Partial | 暗黙的に理解されているが、委譲判断基準として明文化されていない |
| 4 | 極小予算では MAS が勝つ | Partial | Haiku への委譲ルールはあるが、トークン予算が少ない場合の委譲戦略は未定義 |
| 5 | 1k-2k トークンで性能頭打ち | Not yet | サブエージェントの thinking token 予算最適化の知見として未反映 |
| 6 | API トークン水増し問題 | Awareness | Gemini のトークン計測の不正確性を認識すべき。コスト見積もりに影響 |
| 7 | ベンチマーク暗記の脆弱性 | Awareness | `/validate` や eval 設計時にパラフレーズ耐性を考慮すべき |

## Actionable Insights（統合候補）

### A1: 委譲判断基準に「コンテキスト劣化条件」を明文化

**現状**: agent_delegation ルールは「自分でやるべきか？」の判断基準を持つが、情報理論的根拠がない
**提案**: 委譲が正当化される条件を DPI に基づいて明文化:
- コンテキストウィンドウが溢れる（= コンテキスト劣化）
- 異なる情報源からの統合が必要（= 分散コンテキスト）
- 極小予算で深い推論が必要（= SAS の推論深度不足）
- 上記以外では SAS（Opus 直接処理）を優先

### A2: サブエージェントの thinking token 予算ガイダンス

**現状**: サブエージェントに予算制約を指定する慣習がない
**提案**: 1,000〜2,000 トークンで性能が頭打ちになる知見を活用。過剰な推論予算は無駄であり、簡潔な指示で十分

### A3: Debate アーキテクチャの正当性確認

**現状**: `/debate` スキルが存在
**提案**: 本論文が Debate を最強 MAS と評価しており、設計方針を裏付ける。ただし予算を揃えた SAS には及ばないため、Debate の使用は「異なるモデル間の視点の多様性」が真に必要な場合に限定

### A4: Gemini トークン計測の注意

**現状**: Gemini を 1M コンテキスト分析やリサーチに使用
**提案**: Gemini の API 報告トークン数は最大 4.7 倍水増しの可能性。コスト見積もり・性能比較時に注意

## 前提条件

- 結果はマルチホップ推論に限定。コード生成・創造的タスク・ツール使用タスクへの一般化は未検証
- OSS モデルでは SAS 優位がやや小さい（Gemini で最も顕著）
- 「予算を揃える」という前提自体が実用上は難しい（API の不透明性）

## References

- arxiv: https://arxiv.org/abs/2604.02460
- 関連内部: `references/workflow-guide.md`（agent_delegation）, `/debate` スキル
- 関連論文: SSD (Self-Distillation) — 構造的変更がモデル選択より効果的という知見と整合
