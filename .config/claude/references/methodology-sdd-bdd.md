---
status: reference
last_reviewed: 2026-04-23
---

# 開発方法論ガイド: SDD / BDD / TDD

3つの方法論の使い分けと組み合わせパターン。
各スキルの詳細は参照先を読むこと -- ここでは要点と判断基準のみ記載する。

---

## 1. SDD (Spec-Driven Development)

**原則**: "plan is good → code is good" (Boris Cherny)

仕様書は **人間の思考を整理するツール** であり、agent への入力は副次的効果。
仕様書の精密さには天井がある（Precision Ceiling）-- spec がコードと 1:1 対応に収束したら、書き足すのをやめてコードを書く。

### Spec-first ワークフロー

```
Idea → /spec → Review → /spike or /rpi → /validate
```

| ステップ | 何をするか | 成果物 |
|---------|-----------|--------|
| Idea | 課題・要求の言語化 | 口頭 or Issue |
| `/spec` | 構造化プロンプト（Prompt-as-PRD）生成 | `docs/specs/{feature}.prompt.md` |
| Review | acceptance criteria の検証可能性を確認 | spec 更新 |
| `/spike` or `/rpi` | プロトタイプ or 本実装 | コード |
| `/validate` | acceptance criteria との照合 | Pass/Fail |

### /spec の2モード

| モード | 起動 | 質問数 | 用途 |
|-------|------|--------|------|
| **Standard** | `/spec` | 2-5 問 | M 規模、要件がほぼ見えている |
| **Deep Interview** | `/spec --interview` | 10-40+ 問 | L 規模、不確実性が高い |

Deep Interview 完了後は **Session Handoff** -- 新セッションで spec を実行し、インタビュー履歴によるコンテキスト汚染を避ける。

### Precision Ceiling（spec → code 切り替えサイン）

以下の兆候が出たら spec を書き足すのをやめ、`/spike` で実装に移る:

- DB スキーマの全カラム定義を書き始めた
- 擬似コードが実装の 1/3 を超えた
- 条件分岐を網羅的に記述している
- 型定義・インターフェースを詳細に書いている
- 「agent に伝わるように」と何度も書き直している

詳細: `skills/spec/SKILL.md`

---

## 2. BDD (Behavior-Driven Development)

**3フェーズ**: Discovery → Formulation → Automation

ユーザーの振る舞い期待を Given/When/Then 形式で明文化し、それを自動テストに変換する。

### /interviewing-issues との連携（4段階）

```
PARSE → CLARIFY → CRITERIA → OUTPUT
```

| Phase | 内容 | ツール |
|-------|------|--------|
| **PARSE** | Issue 解析、曖昧箇所の特定 | `gh issue view` + コードベース確認 |
| **CLARIFY** | 3-7 個の選択肢付き質問 | AskUserQuestion |
| **CRITERIA** | Given/When/Then で受け入れ条件を定義 | ユーザー確認 |
| **OUTPUT** | 構造化仕様を出力 | `/fix-issue` へチェーン可能 |

### Given/When/Then テンプレート

```gherkin
Given: [前提条件 -- システムの初期状態]
 When: [トリガー -- ユーザーの操作やイベント]
 Then: [期待結果 -- 検証可能な振る舞い]
```

CLARIFY での質問は **選択肢付き** を優先し、往復を最小化する。
回答不十分な場合のみ追加質問（最大 2 ラウンド）。

詳細: `skills/interviewing-issues/SKILL.md`

---

## 3. TDD (Test-Driven Development)

**サイクル**: Red → Green → Refactor

| Phase | 何をするか |
|-------|-----------|
| **Red** | 失敗するテストを先に書く |
| **Green** | テストを通す最小限のコードを書く |
| **Refactor** | テストが通る状態を維持しつつコードを改善する |

TDD は **設計ツール** として機能する -- テストを先に書くことで API の使い勝手を実装前に検証できる。

詳細: `skills/test/SKILL.md`

---

## 4. 方法論選択ガイド

### 状況別推奨

| 状況 | 推奨方法論 | コマンド |
|------|-----------|---------|
| 要件が曖昧、何を作るか不明 | SDD | `/spec` → `/spike` |
| Issue はあるが仕様が不明確 | BDD | `/interviewing-issues` |
| 仕様は明確、実装の正しさを担保したい | TDD | テスト先行で `/rpi` |
| 大規模で不確実性が高い | SDD → BDD → TDD | `/spec` → `/interviewing-issues` → `/rpi` |
| 仕様明確で中規模 | TDD or BDD | `/rpi` |
| バグ修正（再現手順あり） | TDD | Red（再現テスト）→ Green（修正） |

### 規模別デフォルト

| 規模 | デフォルト方法論 | 理由 |
|------|----------------|------|
| **S** | なし（直接実装） | オーバーヘッドが価値を上回る |
| **M** | BDD or TDD | 受け入れ条件 or テスト先行で品質担保 |
| **L** | SDD → BDD → TDD | 全層を順に適用して不確実性を段階的に除去 |

### 不確実性別の組み合わせパターン

| 不確実性 | パターン | フロー |
|---------|---------|--------|
| **高** | SDD → BDD → TDD | `/spec` → `/interviewing-issues` → テスト先行実装 |
| **中** | BDD → TDD | Given/When/Then 定義 → テスト先行実装 |
| **低** | TDD のみ | Red → Green → Refactor |

### 大規模 + 高不確実性のフロー

SDD + BDD + TDD を順に適用:

```
/spec(SDD) → /spike → /validate(BDD) → Decide → /rpi(TDD) → Review(3軸) → Commit
```

仕様が明確な場合は `/rpi` で直接実装に入る。

---

## 5. Anti-Patterns

| NG パターン | 理由 |
|------------|------|
| 仕様が曖昧なまま TDD を始める | テストが仕様の代替にはならない。何をテストすべきか自体が不明 |
| L 規模で SDD をスキップ | 手戻りコストが高い。spec で方向性を固めてから実装する |
| spec を過剰精密化してから TDD もやる | 二重管理。Precision Ceiling に達したらコードに移る |
| BDD の Given/When/Then を抽象的に書く | 「正しく動作する」は検証不能。具体的な入出力を書く |
| S 規模に全方法論を適用 | オーバーヘッドが価値を上回る。直接実装して verify |
| テストなしで「仕様書があるから大丈夫」 | spec は意図の記録。実行可能な検証はテストでしかできない |

---

## 6. 関連リファレンス

| リソース | パス |
|---------|------|
| Spec スキル | `skills/spec/SKILL.md` |
| Interview スキル | `skills/interviewing-issues/SKILL.md` |
| Test スキル | `skills/test/SKILL.md` |
| EPD ワークフロー | `references/workflow-guide.md` (EPD セクション) |
| Precision Ceiling | `skills/spec/references/precision-ceiling.md` |
| 規模別ワークフロー | `references/workflow-guide.md` (6段階プロセス) |
