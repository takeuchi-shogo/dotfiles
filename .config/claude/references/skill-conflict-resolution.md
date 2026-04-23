---
status: active
last_reviewed: 2026-04-23
---

# Skill Conflict Resolution & Negative Routing

> 出典: Garry Tan "Thin Harness, Fat Skills" 原則 5 (Resolver) への補強
> 紐付け: `CLAUDE.md` の resolver 層, `skill-invocation-patterns.md`

CLAUDE.md の `<important if>` タグは「いつ何を読むか」の positive routing を定義するが、本文書は衝突時の優先度と **negative routing（読まない条件）** を補完する。

## Problem

既存 resolver がカバーしていないケース:

1. **複数 skill が同時に match** — user request がどの skill にも部分 match する
2. **skill 衝突** — skill A と skill B が同じ task を主張する
3. **曖昧な intent** — user request が短すぎてどの skill にも完全 match しない
4. **過剰起動** — 単純な task に L 規模 skill が起動する

## Negative Routing — 読まない条件

以下のケースは明示的に skill を load しない:

| # | トリガー | 例 | 正しい対応 |
|---|---------|----|----------|
| 1 | user が直接回答を要求 | 「skill 使わず直接答えて」「シンプルに」 | 平文で回答 |
| 2 | scope 外の task | debug skill に新機能設計を依頼 | AskUserQuestion で意図確認 |
| 3 | 過剰 skill 起動 | typo 修正に `/epd` | skill なしで直接 Edit |
| 4 | session 中の repeat invoke | 同じ skill を 5 分以内に再実行 | 前回結果を参照、再実行は確認してから |
| 5 | skill の declared scope 外 | frontend skill に backend API 設計を依頼 | 対応する別 skill を提案 |

## Conflict Resolution — 衝突時の優先度

### 優先度ルール（上から順）

1. **User 明示指示 > Skill default** — user が明示的に skill 名を指定した場合は最優先
2. **Process skill > Implementation skill** — brainstorming, debugging 等の process skill が先（使い方を決めてから実装）
3. **Specific > Generic** — 言語特化 skill は言語共通 skill より優先
4. **Recent > Stale** — version が新しい skill を優先
5. **High-confidence match > Low-confidence match** — description が強く match する方を優先

### 衝突検知 — 複数マッチ時の判断フロー

```
複数 skill が match
  ↓
User 指示が明示的か？
  ├─ Yes → 指示通りに選ぶ
  └─ No → 優先度ルール適用
      ↓
   優先度で一意に決まるか？
      ├─ Yes → 選択して実行
      └─ No → AskUserQuestion で user に聞く
```

### 判断に迷ったら聞け

優先度ルールで一意に決まらない場合は、**silent に選択せず AskUserQuestion を使う**。
自動選択で外した場合のコストは、user に 1 回聞くコストより大きい。

## 規模ガード — 過剰起動の防止

task 規模に対して skill が過大な場合は起動しない:

| task 規模 | 適用可能 skill | 適用不可 skill |
|----------|---------------|--------------|
| S (typo, 1 行) | 直接 Edit, `/commit` | `/epd`, `/spike`, `/rpi` |
| M (関数追加, バグ修正) | `/rpi`, `/review`, `/fix-issue` | `/epd` (過剰) |
| L (新機能, リファクタ) | `/epd`, `/spec` → `/rpi` | — |

## Anti-Patterns

| # | ❌ Don't | ✅ Do Instead |
|---|---------|--------------|
| 1 | match した全 skill を順次実行 | 1 skill に絞って実行、不十分なら次を試す |
| 2 | CLAUDE.md に全 skill を列挙 | description ベース match + negative routing rule |
| 3 | 衝突を silent に解決 | 判断がつかなければ AskUserQuestion |
| 4 | 過剰 skill 起動を黙認 | 規模ガードで stop し、直接 Edit を検討 |
| 5 | Negative routing を忘れて「何らかの skill」を常に起動 | 「skill なしで直接答える」も valid な選択肢 |

## 適用タイミング

- skill-creator が新 skill 作成時に既存 skill との description 衝突を検証
- user request が曖昧なときの第一判断ポイント
- session 中に同じ skill が連続 invoke されたときの confirmation
- `/review` の reviewer 選択時

## Build to Delete

この文書は Opus の判断ロジックを明文化したもので、自動 hook 化はしない。
model が衝突・過剰起動を自律的に検出・回避できるようになれば、この文書は不要になる。
