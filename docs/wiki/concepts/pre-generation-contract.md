---
title: Pre-generation Contract Pattern
topics: [skill]
sources: [2026-04-10-ui-quality-3layers-article-analysis.md]
updated: 2026-04-10
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

## dotfiles での適用

`skill-writing-guide.md` に **Pre-generation Contract Pattern** セクションとして実装済み。`/rpi` コマンド（`.config/claude/commands/rpi.md`）の Phase 1/2/3 に Must Contract (4項目) + Important Contract (3項目) を埋め込んでいる。

パイロットプロトコル（次回 /rpi 3回使用後に効果測定）:
- 撤退条件: オーバーヘッドが逆効果 or Must 項目が形骸化 → `git revert` で rollback
- 昇格条件: 判断迷いが明確に減る（主観 +1 以上）かつオーバーヘッド軽微（+5分未満/セッション）

昇格候補: `/review`, `/epd` への同パターン展開。

## 関連概念

- [スキル設計](skill-design.md) — SKILL.md の DBS rubric・Independent Evaluability との統合基盤
- [品質ゲート](quality-gates.md) — 生成後の多段検証と Pre-generation Contract の補完関係（事前宣言 vs 事後検証）
- [仕様駆動開発](spec-driven-development.md) — 仕様段階での品質基準定義と契約の接続

## ソース

- [UI Quality 3-Layers 分析レポート](../../research/2026-04-10-ui-quality-3layers-article-analysis.md) — UIデザインスタジオ記事「Claude Code の SKILL.md に品質3層定義を書いたら 40 画面のデザインが破綻しなくなった」の統合分析。Codex 批評で L3 感動品質を排除、固定比率を義務差ベースに変換
