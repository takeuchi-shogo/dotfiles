---
status: reference
last_reviewed: 2026-08-02
---

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

## 第 2 の劣化軸: 指示遵守の距離減衰

SlopCodeBench が測るのは **コード品質** の反復劣化だが、劣化する対象はもう 1 つある。
**standing policy 文書の拘束力そのもの**だ。

HANDBOOK.md (arXiv:2607.25398, Surge AI 2026-07) は、system prompt / policy file / skills 文書を
context に置いて以降の全行動を統制させるパターンを直接測定し、機序をこう述べる:

> It functions as one more retrieved source whose influence decays with distance:
> across turns, across tool calls

policy 文書は「候補行動をふるいにかける永続的な権威」として機能しない。
**距離 (ターン数・ツール呼び出し数) とともに影響力が減衰する検索ソースの 1 つ**として振る舞う。

### 定量的裏付け

20-124 頁 (中央値 37 頁 / 14.9K トークン) の専門家執筆 SOP を軸にした 65 タスク・824 判定基準で、
厳格採点 (全基準充足のみ合格) の結果:

- 最良構成 **36.2%**、大半のフロンティア構成は 25% 未満 (30 モデル構成 / 20 モデル / 11 プロバイダ)
- 完了試行は平均約 17 ステップ・30 ツール呼び出し
- 1 基準の失敗を許容する pass@1(N-1) にすると多くのモデルでスコアが約 2 倍 = 失敗の大半は単一基準の取りこぼし

### slope/intercept との関係

この軸でも同じ結論が独立に再現される。**推論エフォートを上げても直らない**:

| モデル | エフォート増の効果 |
|--------|------------------|
| Opus 4.8 | +3.0pt |
| Sonnet 4.6 | +2.7pt |
| Fable 5 | +2.0pt |
| GPT-5.5 | 変化なし |
| GLM 5.2 | **-2.7pt (悪化)** |

トークンを費やすことも遵守を買わない (GPT-5.5 は約 13K トークンで 21.5%、
Opus 4.8 max は約 60K トークン・約 3 倍のコストで同水準)。

つまり「プロンプトは intercept を改善するが slope は変わらない」は、コード品質だけでなく
**指示遵守にも当てはまる**。追加の熟考は「見落とした推論」にしか効かず「見落とした読解」には効かない。

論文自身の提言も同じ方向を向く — policy をモデル外の決定論的 tool-call guard にコンパイルすること。
これは `CLAUDE.md` の「Static-checkable rules は mechanism に寄せる」と一致する。

### 含意

- CLAUDE.md を丁寧に書くことは intercept にしか効かない。長い作業ほど効き目が落ちる
- 長さを増やして拘束力を上げようとするのは逆効果になりうる (14.9K トークンの SOP で 36.2%)
- 守らせたいルールが static-checkable なら hook / deny rule に落とす。落とせないものは
  「距離が伸びたら効かない」前提で設計する

出典: `docs/research/2026-07-31-handbook-md-instruction-following-absorb-analysis.md`

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
