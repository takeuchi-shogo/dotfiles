---
title: Pre-generation Contract Pattern
topics: [skill]
sources: [2026-04-10-ui-quality-3layers-article-analysis.md, 2026-04-20-karpathy-skills-absorb-analysis.md, 2026-06-14-claude-fable5-system-prompt-absorb-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 3
confidence: established
---

# Pre-generation Contract Pattern

## 概要

生成を開始する前に、品質基準を「照合可能な契約」として SKILL.md に埋め込むパターン。「設計参考として書いてある」だけでなく「生成中に実際に照合される」形で定義することで、局所最適化（1画面完璧主義）が全体破綻につながる因果を事前の制約設定で断ち切る。

核心的な洞察は「Must/Important/Optional の義務付けの差を明示すること」にある。品質項目を分類するだけでなく、skip 可否・記録義務・照合タイミングを項目ごとに明確に宣言する。

## Must / Important / Optional の3層

| 層 | 義務付け | skip 可否 | 主な用途 |
|----|----------|-----------|----------|
| **Must** | 生成中に照合。skip 不可 | 不可 | コンポーネント準拠・型安全・命名規則など客観検証可能な最低限の基準 |
| **Important** | 主要ステップで確認 | 明示的 skip + 記録必須 | UX 一貫性・エラーハンドリング网羅など主観要素を含む中間基準 |
| **Optional** | 余裕があれば | 記録不要 | 感動品質・追加ポリッシュなど、なくても動作上問題ない項目 |

## Good 例 vs Bad 例

### Good（照合できる契約）

```markdown
## Must Contract
- [ ] designTokens の color/spacing のみ使用（ハードコード禁止）
- [ ] 全インタラクティブ要素に aria-label または aria-describedby
- [ ] TypeScript strict モード違反ゼロ
- [ ] 命名規則: コンポーネント PascalCase / hooks camelCase with use prefix
```

### Bad（設計参考止まり）

```markdown
## 品質基準
- ユーザビリティが高いこと
- アクセシビリティを考慮する
- コードがきれいであること
```

Bad 例の問題: 「高い」「考慮する」「きれい」は照合不可能。Must に書いても形骸化する。

## アンチパターン

- **抽象的 Must**: 「UX が良い」「コードがきれい」など客観的照合不可能な Must は形骸化の確実な予兆
- **Must 6個超**: Must が増えるほど、照合漏れと形骸化のリスクが高まる。Must は 4-5 個に絞る
- **L3 感動品質の Must 化**: 「感動させる」「ユーザーを驚かせる」相当の抽象的項目を Must にしない。Optional または削除
- **Optional 肥大化**: Optional が 10 個を超えると読まれなくなる。Important か削除を検討する
- **固定比率の偽精密**: 「Must=52%/Important=36%/Optional=12%」のような数値固定は偽精密。義務付けの差（Must/Important/Optional）で表現すれば十分

## Constitutional AI との対応

SKILL.md への検証基準埋め込みは Constitutional AI（arXiv:2212.04037）のアプローチと構造的に同一である。Constitutional AI が「行動前に照合される原則」を定義するように、Pre-generation Contract は「生成前に宣言し生成中に照合される品質原則」を定義する。差異は粒度: Constitutional AI は高レベルな倫理原則、Pre-generation Contract はスキル固有の工学的チェックリスト。

## 他の分類体系との対応

- **Kano モデルとの類似**: L1/L2/L3 の品質層定義は、Kano モデルの must-be quality（不満足要因）/ one-dimensional quality（線形満足度）/ attractive quality（感動要因）と構造的に近い。ただし Gemini の推測に基づく対応で Google Search grounding は未検証であり、dotfiles での運用とは独立した学術的文脈として参照するに留める `[INFERRED, conf=45]`
- **Hook Enforcement 3分類との対応**: Hook Philosophy ADR (0006) が定めた deterministic block / semantic advisory / human judgment という enforcement 層の3分類は、Must/Important/Optional という義務付けの3層と対応関係を持つ。Must は「生成中に照合し skip 不可」という点で deterministic block に近く、Important は semantic advisory（明示的 skip + 記録）、Optional は human judgment（判断に委ねる）に対応する。ただし Must Contract 自体は機械的 hook ではなく生成中の self-check であり、hard enforcement を避ける Karpathy の設計哲学とも矛盾しない `[INFERRED, conf=60]`
- **Fable5 severity ラベル体系との類似**: Anthropic 公式システムプロンプト（通称 Claude Fable 5、非公式再構成版）の LIMIT 1/2/3・SEVERE/NON-NEGOTIABLE という段階的 severity ラベルは、深刻度に応じて義務付けを変える点で Must/Important/Optional と同型の構造を持つ。ただし Fable5 は単一巨大プロンプトへの直書きで Progressive Disclosure を伴わない点が dotfiles の階層設計と異なる `[EXTRACTED, conf=55]`

## dotfiles での適用

`skill-writing-guide.md` に **Pre-generation Contract Pattern** セクションとして実装済み。`/rpi` コマンド（`.config/claude/commands/rpi.md`）の Phase 1/2/3 に Must Contract (4項目) + Important Contract (3項目) を埋め込んでいる。

パイロットプロトコル（次回 /rpi 3回使用後に効果測定）:
- 撤退条件: オーバーヘッドが逆効果 or Must 項目が形骸化 → `git revert` で rollback
- 昇格条件: 判断迷いが明確に減る（主観 +1 以上）かつオーバーヘッド軽微（+5分未満/セッション）

昇格候補: `/review`, `/epd` への同パターン展開。

### 事後ゲートとの役割分担

Fable5 absorb分析（2026-06-14）の Codex 批評で、Pre-generation Contract を `completion-gate.py` などの事後ゲートの「完全代替」とみなす判定は誤りと訂正された。生成中の self-check（Pre-generation Contract）と Stop 時・テスト時に発火するゲート（completion-gate.py）は異なる粒度をカバーする別レイヤーの補完関係にあり、`skill-writing-guide.md` にその役割分担を明記した。高 stakes な skill にのみ selective に埋め込む運用とする `[EXTRACTED, conf=80]`。

Must Contract 項目には、危険・非直感・高コストのいずれかに該当する場合のみ 1 文の rationale を添える（inline rationale の境界）。これにより契約の遵守率を上げつつ、全項目への rationale 付与による冗長化を防ぐ `[EXTRACTED, conf=70]`。

PLANS.md の Required Sections に Success Criteria が追加され、`completion-gate.py` が plan frontmatter の `success_criteria:` を読んで照合する配線が完成した（Karpathy 原則4「Goal-Driven Execution」の absorb 由来）。これは「事前宣言 → 生成中/完了時に照合」という Pre-generation Contract と同じ構造を Plan 層で実現した別実装である `[EXTRACTED, conf=75]`。

## 関連概念

- [スキル設計](skill-design.md) — SKILL.md の DBS rubric・Independent Evaluability との統合基盤
- [品質ゲート](quality-gates.md) — 生成後の多段検証と Pre-generation Contract の補完関係（事前宣言 vs 事後検証）
- [仕様駆動開発](spec-driven-development.md) — 仕様段階での品質基準定義と契約の接続
- [ハーネスエンジニアリング](harness-engineering.md) — Hook Philosophy ADR (0006) の deterministic block / semantic advisory / human judgment 3分類と Must/Important/Optional の対応

## ソース

- [UI Quality 3-Layers 分析レポート](../../research/2026-04-10-ui-quality-3layers-article-analysis.md) — UIデザインスタジオ記事「Claude Code の SKILL.md に品質3層定義を書いたら 40 画面のデザインが破綻しなくなった」の統合分析。Codex 批評で L3 感動品質を排除、固定比率を義務差ベースに変換
- [Karpathy Skills absorb 分析](../../research/2026-04-20-karpathy-skills-absorb-analysis.md) — LLM コーディング4大失敗パターン対策の absorb。Hook Philosophy ADR (0006) と PLANS.md Success Criteria 接続が Pre-generation Contract と対応する enforcement 層を成文化
- [Claude Fable 5 System Prompt absorb 分析](../../research/2026-06-14-claude-fable5-system-prompt-absorb-analysis.md) — Anthropic 公式システムプロンプト（非公式再構成版）の craft 分析。completion-gate との役割分担・inline rationale の境界を Pre-generation Contract に追記
