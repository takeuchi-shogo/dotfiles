---
name: improve-codebase-architecture
description: >
  コードベースを能動的に探索し、深化候補を診断する。インターフェース/シーム/深さ/
  局所性の語彙で、削除テスト (deletion test) を判定の核心に置く。
  週次または開発サージ後に実行。
  Triggers: 'アーキテクチャ改善', 'モジュール改善', 'codebase architecture',
  'deep module', '削除テスト', 'deepening', 'コード構造改善', 'module depth'.
  Do NOT use for: 機能実装（use /rpi）、リファクタリング実行（use /refactor-session）、
  コード品質監査（use /audit）。
origin: self
allowed-tools: Read, Glob, Grep, Bash, Agent, AskUserQuestion
metadata:
  pattern: diagnosis
  origin: mattpocock/skills/improve-codebase-architecture@2026-04-26 + agent-native-code-design.md
disable-model-invocation: true
---

# improve-codebase-architecture — コードベース構造の改善診断

コードベースを能動的に探索し、フリクションのある箇所を「深化候補」として提示する。
判定の核心は **削除テスト** — 削除して複雑性が散るなら稼いでいる、消えるなら pass-through。

## 用語

詳細は [LANGUAGE.md](LANGUAGE.md) を参照。共通語彙 8 つを使う:

- **モジュール (Module)**: インターフェースと実装を持つもの。粒度を問わない
- **インターフェース (Interface)**: 呼び出し側が知るべき全事実 (型 + 不変条件 + 順序 + エラー + 設定 + 性能特性)
- **実装 (Implementation)**: モジュールの中身。アダプターと区別する
- **深さ (Depth)**: インターフェースに対するレバレッジ
- **シーム (Seam)**: 編集なしで挙動を変えられる場所 (Feathers の用語)
- **アダプター (Adapter)**: シームに座ってインターフェースを満たす具体物
- **レバレッジ (Leverage)**: 深さから呼び出し側が得るもの
- **局所性 (Locality)**: 深さから保守側が得るもの

**必須原則** (詳細は [LANGUAGE.md](LANGUAGE.md)):

- **削除テスト**: 削除して複雑性が消えれば pass-through、N 箇所に散れば稼いでいる
- **インターフェース = テスト面**: 奥をテストしたいならモジュールの形が間違い
- **アダプター 1 個 = 仮説、2 個 = 本物のシーム**: 横断して変わらないならシーム不要

## いつ使うか

- **週次**: `/weekly-review` の後に定期実行
- **開発サージ後**: 大量のコードが追加された後
- **エージェントの困りごと**: ファイル間を行ったり来たりして迷っている時
- **新プロジェクト参入時**: コードベース構造を理解するついでに

## Process

### Step 1: 探索

- `docs/glossary.md` (ubiquitous-language の出力) と `docs/adr/*.md` を最初に読む (各 ADR は上限 50 行)
  - 存在しなければサイレントに進む。「作りましょう」は提案しない
  - **ただし出力先頭に `⚠️ glossary.md 未整備、診断精度低下の可能性` を表示**
- Agent (subagent_type=Explore) で構造を歩く
- フリクションのある箇所を有機的に列挙
- **探索予算: 最大 20 操作** (Read/Grep/Glob 合計)

### Step 2: 診断

5 観点を **削除テストを当てる箇所の検出ヒューリスティック** として使う。観点ごとに診断手段が異なる:

| 観点 | 削除テスト | 補助診断 |
|------|-----------|---------|
| 1 浅いモジュール (関数 1-5 行委譲、`utils/`/`helpers/` 散在) | Yes | - |
| 2 テスタビリティ過剰分離 (純粋関数切出 / 呼出側にロジック残存) | Yes | - |
| 3 概念の分散 (同接頭辞ファイル多ディレクトリ散在) | No (構造) | grep 同名/接頭辞 |
| 4 Grep 困難な命名 (`export default` 多用、汎用名) | No (静的) | export default / 汎用名 grep |
| 5 テスト配置 (`__tests__/` 集約、命名対応なし) | No (静的) | ディレクトリ走査 |

**観点 1, 2 は削除テストを適用** — 削除して複雑性が散るなら稼いでいる、消えるなら pass-through。観点 3-5 は静的診断で検出する (削除テストは適用不可)。

### Step 3: 候補の提示 (最大 5 件)

各候補:

- **対象モジュール** (file paths)
- **問題**: なぜフリクションがあるか (LANGUAGE 語彙で)
- **解決方向**: 何が変わるか (具体的なインターフェース提案はまだしない)
- **効果**: レバレッジと局所性、テストがどう改善するか
- **規模**: S / M / L

```markdown
## コードベース構造レポート

### スコアカード
| 観点 | 状態 | 候補数 |
|------|------|-------|
| 浅いモジュール | ⚠️ | 3 |
| 過剰分離     | ✅ | 0 |
| 概念分散     | ⚠️ | 2 |
| Grep         | ✅ | 0 |
| テスト配置   | ❌ | 5 |

### 候補 (削除テスト適用後)
1. {モジュール} — {問題} / {解決方向} / {効果} / {規模}
```

**ADR 衝突は friction が大きい時のみ surface**。
**Step 4 までインターフェース提案はしない** — grilling 前に形を出さない。

ユーザーに `AskUserQuestion` で「どれを掘り下げる？」と問う。

### Step 4: Grilling loop

候補が選ばれたら、対話で設計ツリーを下る。4 軸に限定:

- **制約**: 何が固定されているか
- **依存**: 依存カテゴリ ([DEEPENING.md](DEEPENING.md) の 4 分類) のどれか
- **シーム後ろの形**: 深くしたモジュールの中身
- **残るテスト**: インターフェースで何を検証するか

副作用 (inline):

- ドメイン用語が `docs/glossary.md` になければ ubiquitous-language skill 経由で追記提案
- ユーザーが load-bearing な理由で却下したら **ADR 候補を示し `/decision` skill 起動を提案** (このスキル自身は ADR.md を Write しない)
- 代替インターフェースを探りたいなら [INTERFACE-DESIGN.md](INTERFACE-DESIGN.md) へ (**デフォルト 1 案、ユーザーが複数案要求した時のみ 3-4 並列**)

### Step 5: ハンドオフ

`AskUserQuestion`:

- `/refactor-session` にチェーン (実行)
- `/create-issue` で Issue 化
- 記録のみ

## Anti-Patterns

| NG | 理由 |
|----|------|
| 全ファイルを Read | 探索予算 (20 操作) 超過 |
| 直接編集 | このスキルは診断のみ |
| 理想設計の押し付け | 既存文脈尊重、段階的改善 |
| 5 件超えの提案 | 焦点喪失 |
| Step 3 でインターフェース提案 | grilling 前に形を出すな |
| ADR 衝突を全部 surface | ノイズ、friction が大きい時のみ |
| component / boundary / API と呼ぶ | 語彙統制違反 ([LANGUAGE.md](LANGUAGE.md) 参照) |

## Chaining

- **前**: `/weekly-review` (定期) / `/audit` (品質補完)
- **後**: `/refactor-session` (実行) / `/create-issue` (Issue 化)
- **サブ**: [DEEPENING.md](DEEPENING.md), [INTERFACE-DESIGN.md](INTERFACE-DESIGN.md), [LANGUAGE.md](LANGUAGE.md)
- **参照**: `references/agent-native-code-design.md` (5 原則: Grep-able / Collocated / 機能単位 / テスト報酬 / API 境界)
