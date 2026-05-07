---
allowed-tools: Bash(ls *), Bash(wc *)
argument-hint: "[--max-cycles=N] [--no-iterate]"
description: skill / docs / code を並列点検し、整理候補を反復サイクルで「懸念なくなるまで」処理する
---

# /improve — Tidy Orchestrator

skill / ドキュメント / コードを横断点検し、整理候補をユーザー承認 → 該当 skill へ委譲 → 再走査するサイクルを反復する。**提案ゼロのサイクル** で自然収束。

## スコープ

- **対象**: skill 整合性、ドキュメント鮮度、直近変更の品質、コード全体の健全性
- **対象外**:
  - セッションデータの自動学習・履歴蓄積 (autoevolve 系 producer の責務、本コマンドからは参照しない)
  - 機械学習による自動提案生成
  - ユーザー承認なしの自動変更

`/improve` は **薄いオーケストレーター**。実際の検出・修正は専門 skill に委譲する。

## 引数 (`$ARGUMENTS`)

- `--max-cycles=N` (default: `10`) — 反復上限。到達時はユーザーに継続可否を確認
- `--no-iterate` — 1 サイクルだけ実行して終了 (Phase E/F skip)

引数なしの場合は default 動作。

## サイクル定義

### Phase A. 並列点検

以下 4 つを **並列で** 起動 (subagents または slash command 委譲):

| 委譲先 | 検出対象 |
|---|---|
| `skill-audit` | skill description 衝突、health degradation |
| `check-health` | ドキュメント鮮度、参照整合性、コード乖離 |
| `simplify` | 直近変更の重複・冗長・非効率 |
| `audit` | コードベース全体の品質 (security / arch / perf / tests) |

各処理は read-only。書き込みは Phase D まで行わない。

### Phase B. 統合

各結果から整理候補リストを統合する:

- 重複排除 (BM25/trigram 類似度 > 0.85 で同一視)
- 優先度付与: `high` / `medium` / `low` (各 skill の severity を引き継ぐ)
- 各候補に **委譲先** を割当 (例: skill 修正 → `skill-creator`、参照修復 → 直接 Edit)
- 出力フォーマット:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  /improve サイクル N — 整理候補
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[high]
  1. <候補要約> — 検出元: skill-audit / 委譲先: skill-creator
  2. ...

[medium]
  ...

[low]
  ...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase C. 承認

ユーザーに提示:

> 承認する候補の番号を入力してください (例: `1,3,5` / `all` / `high` / `none` / `quit`)

- `all`: 全候補
- `high` / `medium` / `low`: 優先度フィルタ
- `quit`: サイクル即時終了 (Phase D-F skip)
- `none`: このサイクルは何もせず Phase E へ

### Phase D. 委譲実行

承認された候補を 1 件ずつ該当委譲先で実行する:

- `skill-creator` に渡す場合: 「<skill 名> を <検出内容> に従って修正してください」と委任
- 直接 Edit する場合: 影響範囲を提示 → ユーザー確認 → Edit
- 各実行後に成否を表示 (✓ / ✗ + 理由)

委譲先で **新たな質問** が必要になった場合は、その時点でユーザーに確認 (人間 in-the-loop 維持)。

### Phase E. 再走査

`--no-iterate` 指定時はここで終了。それ以外は Phase A を再実行する。

### Phase F. 判定

| 条件 | アクション |
|---|---|
| 提案ゼロ | **収束**。サイクル N で終了、サマリ表示 |
| 残候補あり & サイクル < max-cycles | 次サイクルへ (Phase A から) |
| サイクル >= max-cycles | 「上限 N 到達。続けますか? (y/n)」 |
| ユーザーが quit | 即時終了 |

## 終了サマリ

実行完了時に表示:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  /improve 終了サマリ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  実行サイクル数: N
  終了理由: 収束 / max-cycles / quit
  処理候補: 適用 X / skip Y / 失敗 Z
  影響ファイル: ...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 重要事項

- **ユーザー承認なしの自動変更を絶対に行わない** (Phase C を skip しない)
- **読み取り専用のシグナル** (autoevolve の learnings/) は参照しない (consumer 責務分離)
- **委譲先で完結する** — 本コマンドは検出と承認フローだけを担い、修正ロジックは専門 skill に任せる
- **収束しない場合の暴走防止** — max-cycles と人間 in-the-loop が二重ガード

## 認知負荷の最小化

retire の経緯 (元 autoevolve 版が「認知負荷 > 価値」で 2026-05-03 retire) を踏まえ:

- 1 サイクルあたりのユーザー対話は **承認 1 回** に集約
- 候補が多すぎる場合 (> 20) は high のみ提示、medium/low は次サイクル送り
- 委譲先で詳細質問が必要な場合のみ追加対話
