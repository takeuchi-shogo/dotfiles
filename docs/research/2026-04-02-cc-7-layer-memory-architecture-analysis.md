---
source: "How Anthropic Built 7 Layers of Memory and a Dreaming System for Claude Code (video breakdown)"
date: 2026-04-02
status: integrated
---

## Source Summary

**主張**: Claude Code は 7層のメモリアーキテクチャで有限コンテキスト問題を解決。各層は段階的にコストが高くなるが、安い層が高い層の発動を防ぐ設計。

**手法**:
1. **Layer 1: Tool Result Storage** — 閾値超過でディスク永続化、ContentReplacementState でキャッシュ安定
2. **Layer 2: Microcompaction** — 3種（時間ベース60分/キャッシュ編集API/APIレベル context_management）
3. **Layer 3: Session Memory** — 10セクション構造化テンプレートで継続的メモ維持。compaction 時に summary として即注入（API呼び出し不要）
4. **Layer 4: Full Compaction** — 9セクション要約 + analysis/summary 2フェーズ出力 + 3回失敗サーキットブレーカー
5. **Layer 5: Auto Memory Extraction** — メインエージェントとの相互排他、2ターン予算効率化
6. **Layer 6: Dreaming** — クロスセッション4フェーズ統合（Orient→Gather→Consolidate→Prune）、PIDロック、Bash read-only
7. **Layer 7: Cross-Agent Communication** — CacheSafeParams、fork byte-identical prefix、SendMessage ルーティング

**設計原則**:
1. Layered Defense, Cheapest First — 安い層が高い層を防ぐ
2. Prompt Cache Preservation — byte-identical prefix の維持に全力
3. Isolation with Sharing — fork は state 隔離 + cache 共有
4. Circuit Breakers Everywhere — 3回失敗停止、10分スロットル、PIDロック
5. Graceful Degradation — 各層が静かに失敗 → 次の層がキャッチ
6. Feature Flags as Kill Switches — GrowthBook で即時ロールバック
7. Mutual Exclusivity — Context Collapse↔Autocompact、Main writes↔Background extraction

**根拠**: サーキットブレーカー未導入時 250K API calls/day 浪費、キャッシュヒット/ミスで $0.003 vs $0.60 差

**具体的閾値**:
- autocompact: context window - 20K (output reserve) - 13K (buffer)
- Session Memory compact: minTokens 10K, minTextBlockMessages 5, maxTokens 40K
- Dreaming: 10分スロットル、60分 stale lock detection
- Microcompact (time-based): 60分アイドル、keepRecent 5
- Circuit breaker: 3回連続失敗で停止
- Token estimation: 4 bytes/token (text), 2 bytes/token (JSON)

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | 7-Layer Hierarchy Model | Gap | harness-10-principles #5 は3層レベル。7層の体系的マッピングなし |
| 2 | Dreaming 4フェーズ統合 | Partial | /improve が類似だが4フェーズの構造化度が低い。Prune/Index が弱い |
| 3 | Circuit Breaker 具体化 | Partial | stagnation-detector.py が部分実装。汎用パターンなし |
| 4 | Compaction 2フェーズ出力 | Gap | compact-instructions.md に保留優先度はあるが概念なし |
| 5 | Microcompaction 3メカニズム | N/A | CC 内蔵。ハーネスレベルで制御不可 |
| 6 | ContentReplacementState | N/A | CC 内蔵 |
| 7 | Fork Message Construction | N/A | CC 内蔵 |
| 8 | Feature Flags as Kill Switches | N/A | settings.json で代替済み |

### Already 強化分析

| # | 既存の仕組み | 記事の知見 | 強化案 |
|---|-------------|-----------|--------|
| A | compact-instructions.md 3戦略 | 7層モデルでハーネス介入層を明示すべき | 7層マッピング参照追加 |
| B | compact-instructions.md Cache安定性 | 6つのキャッシュ保全パターン | 避けるべき操作の具体リスト |
| C | resource-bounds.md 閾値 | CC内部の具体的閾値公開 | 閾値リファレンス追記 |
| D | /improve (AutoEvolve) | "Look only for things you already suspect matter" | ナロースキャン原則追記 |
| E | error-handling + fallback | 階層的グレースフルデグレーション | フォールバックチェーン明示化 |

## Integration Decisions

全項目取り込み。5タスクに統合:
- T1: references/cc-7-layer-memory-model.md 新規 (Gap#1 + Already A)
- T2: compact-instructions.md 強化 (Gap#4 + Already B)
- T3: improve-policy 強化 (Gap#2 + Already D)
- T4: resource-bounds.md CC閾値追記 (Already C)
- T5: failure-taxonomy.md 追記 (Gap#3 + Already E)

## Plan

依存: T1 → T2。T3-T5 は独立。
