---
name: spike
description: "プロトタイプファースト開発。worktree で隔離し、最小実装 → Product Validation まで行う。アイデアの素早い検証に使用。テスト・lint 不要。"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, EnterWorktree
user-invocable: true
---

# Spike: Prototype-First Development

アイデアを素早くプロトタイプ化し、Product Validation（acceptance criteria 照合）まで行う。
テスト・lint は不要。目的は「正しいものを作っているか」の検証。

## Workflow

```
/spike {idea or feature name}
  1. Spec Check    → docs/specs/ に spec があるか確認
  2. Spec Create   → なければ /spec を実行して生成
  3. Isolate       → worktree で隔離環境を作成
  4. Implement     → 最小実装（動くことが最優先）
  5. Validate      → /validate で acceptance criteria を照合
  6. Report        → 結果をまとめて報告
```

## Step 1-2: Spec Check / Create

1. `docs/specs/{feature}.prompt.md` を検索
2. 存在しなければ、spec スキルを呼び出して生成する
3. spec の Prompt セクションを実装の入力として使用する

## Step 3: Isolate

worktree を使用してメインブランチから隔離する:

1. EnterWorktree ツールで `spike/{feature}` ブランチを作成
2. または Agent ツールの `isolation: "worktree"` を使用

## Step 4: Implement

実装のルール:

- **動くことが最優先**: コード品質は二の次
- **テスト不要**: spike のコードは捨てる前提
- **lint 不要**: フォーマットは気にしない
- **最小限**: spec の Requirements を満たす最小コード
- **ハードコード可**: 設定値等は直書きでOK

## Step 5: Validate

validate スキルを呼び出して acceptance criteria を検証する。

## Step 6: Report

以下のフォーマットで結果を報告:

```
## Spike Report: {feature}

**Spec**: docs/specs/{feature}.prompt.md
**Branch**: spike/{feature}
**Validation**: ✅ PASS / ❌ FAIL / ⚠️ PARTIAL

### Findings
- 実装で分かったこと
- 想定と違ったこと
- 技術的な課題や制約

### Recommendation
- ✅ Proceed: 正式実装に進む（/rpi を使用）
- 🔄 Pivot: アプローチを変更して再 spike
- ❌ Abandon: この機能は見送り
```

## After Spike

- **Proceed**: worktree のコードは参考として残す。正式実装は `/rpi` で新たに行う
- **Pivot**: spec を更新して再度 `/spike`
- **Abandon**: worktree を削除、spec の status を `abandoned` に更新

## Anti-Patterns

- spike のコードをそのまま本番に持ち込む（必ず /rpi で正式実装）
- テストやリファクタリングに時間をかける（spike は検証が目的）
- spec なしで spike する（何を検証するか不明確になる）
- 長時間の spike（目安: 30分以内の作業量に収める）
