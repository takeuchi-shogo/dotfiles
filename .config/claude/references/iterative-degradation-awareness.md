# Iterative Degradation Awareness

SlopCodeBench (Orlanski et al., 2026) が実証した、エージェントの反復的コード品質劣化に関する知見。
レビューアー・ワークフロー設計・プロンプト設計の全てに影響する。

## Core Insight: Slope vs Intercept

プロンプトによる品質指示（KISS, YAGNI, anti-slop）は **intercept（初期品質）を改善** するが、
**slope（反復ごとの劣化速度）は変わらない**。

```
Quality
  ↑
  │  ╲  anti_slop (intercept↑, slope同一)
  │   ╲╲
  │    ╲ ╲  baseline
  │     ╲  ╲
  │      ╲   ╲
  └───────────→ Iterations
```

### 含意
- CLAUDE.md の原則は「最初の1回」には効くが、5回目の変更には不十分
- **プロンプトだけでは劣化を止められない** — ツーリングレベルの介入が必要
- 初期品質を上げる努力は無駄ではない（intercept が高ければ劣化が許容範囲を超えるまでの猶予が長い）

## 主要な劣化パターン

### 1. God Function 化（Compounding in Single Function）
新ロジックが既存関数にパッチされ、focused callable に分割されない。

**典型例**: main() が CC=29→285、84行→1099行に膨張。
9つのコマンド分岐が同じ parsing scaffold をコピペ。

**検出シグナル**:
- 同一関数への複数回の変更（git blame で確認可能）
- CC が 10 を超える関数への分岐追加
- 関数内の elif/case チェーンの成長

### 2. 構造的 Duplication
Verbosity 成長の 66% は構造的クローン（同じ構造で値だけ異なるコード）。

**検出シグナル**:
- 同じ引数パース / バリデーションパターンの繰り返し
- ほぼ同一の条件分岐ブロック

### 3. 初期アーキテクチャの複利効果
C1 でハードコードした言語固有ロジックが C2, C5 で cascading rewrite を引き起こす。

**防止策**:
- /spec, /spike で「この設計は将来の仕様変更に対して extensible か」を明示的に評価
- ハードコードよりもインターフェース / プラグイン設計を優先

## レビューでの適用

### 劣化検出の質問
レビュー時に以下を意識する:

1. **「この変更は既存関数を肥大化させていないか？」**
   - 新ロジックが既存の大関数に追加されている場合 → 分割を提案
2. **「新しいロジックは focused callable に分割されているか？」**
   - 1つの関数が複数の責務を持ち始めていないか
3. **「構造的なコピペが発生していないか？」**
   - 同じパターンが値だけ変えて繰り返されていないか
4. **「テストが通っているから OK」で終わらせていないか？」**
   - テストスイートは structural decay を検出できない（論文の主要発見）

## ワークフローへの適用

| フェーズ | 適用 |
|---------|------|
| /spec | 拡張性評価: 「将来の仕様追加で cascading rewrite が起きないか」 |
| /spike | プロトタイプの設計判断が後続に与える影響を意識 |
| /review | CC-9 Iterative Slop Detection チェック |
| /simplify | God function 化パターンの検出 |
| /refactor-session | 蓄積された slop の定期的清掃 |

## 出典

Orlanski, G. et al. (2026). "SlopCodeBench: Benchmarking How Coding Agents Degrade Over Long-Horizon Iterative Tasks." arXiv:2603.24755.
https://www.scbench.ai
