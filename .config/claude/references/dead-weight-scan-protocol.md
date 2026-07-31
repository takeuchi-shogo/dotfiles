---
status: reference
last_reviewed: 2026-04-23
---

# Dead Weight Scan Protocol

> 「何をやめられるか？」を定期的に問う棚卸しチェックリスト。
> 出典: Anthropic "Harnessing Claude's Intelligence" (2026-04-02) — モデル進化に伴い、過去に有効だった指示が dead weight 化する。

## トリガー

- `/improve` の Step 5 陳腐化チェック（自動）
- モデルアップグレード後の初回セッション（手動推奨）
- CLAUDE.md が 150 行を超えた場合（check-claudemd-lines.sh で自動検知）
- **MEMORY.md が 200 行または索引エントリ 50 件を超えた場合**（2026-04-11 追加。検知は `memory-status` スキルでの手動運用。将来的に `check-memory-lines.sh` として自動化候補）
- **lessons-learned.md が 50 エントリを超えた場合**（improve-policy.md の容量管理に準拠、検知は `/improve` Garden フェーズで手動確認）

## スキャン対象と問い

### 1. CLAUDE.md の `<important if>` ブロック

各ブロックについて:
- この条件分岐は現行モデルでまだ必要か？（モデルがデフォルトで守る動作ではないか）
- 過去のインシデント起因の指示なら、そのインシデントはまだ再現しうるか？

### 2. Compaction / Context 管理ルール

- compaction fallback の閾値はモデル能力に見合っているか？
- context anxiety 対策（reset, checkpoint 頻度）は過剰ではないか？

### 3. references/ のルール・チェックリスト

- 統合済み記事由来のルールで、現行モデルが自然に守るものはないか？
- 3ヶ月以上参照されていない reference は本当に必要か？
- 容量上限（improve-policy.md）を超えたら必ず降格候補を出す:
  - `lessons-learned.md` 50 エントリ: verify PASS 10+ 連続を昇格 or `situation-strategy-map.md` へ降格
  - MEMORY.md 200 行 / 索引 50 件: 参照頻度の低い項目を `_index.md` へ外出し
  - CLAUDE.md 150 行: `<important if>` ブロックを references/ へ外出し

### 4. hooks / scripts

- policy hook が防いでいるミスを現行モデルはまだ犯すか？
- hook の正規表現が過剰にマッチして false positive を出していないか？

### 5. エージェント定義

- サブエージェントの指示で、現行モデルに不要な「当たり前」の指示はないか？
- 古いモデル向けの workaround（冗長な例示、ステップバイステップ強制）が残っていないか？

## 判定基準

| 判定 | アクション |
|------|----------|
| **Dead weight** | 削除。commit message に理由を記録 |
| **Possibly stale** | 1セッション無効化して副作用を観察。問題なければ削除 |
| **Still needed** | 維持。次回スキャン時に再評価 |

## モデル世代交代時の ablation

上のスキャンは「維持」がデフォルトで、削除する側に立証責任を課す。モデル世代が変わったときだけ、
**振る舞い指示に限って極性を反転する** — 新モデルで寄与を示せない指示は unproven として扱う。

根拠: `harness-stability.md` の 30 日ルールは、低頻度だが重大な safety hook を短期観測で消さないためにある。
一方で **旧モデルでの 30 日利用実績は、新モデルでその prompt がまだ必要な証拠にならない**。
この 2 種を同じ削除規則で扱うと keep bias が育つ。

### 実験対象と除外

| 区分 | 既定 | 例 |
|------|------|-----|
| 振る舞い指示 | **default = unproven** (寄与を示せたものだけ残す) | CLAUDE.md の作法・様式指示、agent 定義の冗長な手順、旧モデル向け workaround |
| 機械的安全制約 | **default = keep** (実験対象外) | permission deny、不可逆操作のゲート、injection 検出、lint config 保護 |

安全側を ablate しない。モデルの injection 耐性が上がっても、被害半径を抑える層としての価値は変わらない。

### セルを混ぜない

独立変数を 1 つに保つ。以下は**別々の実験**であり、まとめて 1 回で判断しない。

1. global CLAUDE.md の振る舞い指示
2. skill の常時ロード分 (frontmatter description の総量) と skill 本文
3. hook / 機械的制約 — 原則として除外 (上表)
4. `tools/system-prompt-patcher/` の独自パッチ (現在 5 件、`task setup` の標準経路で無測定適用)
5. `CLAUDE_CODE_SIMPLE=1` — **極端な対照専用**。tool prompt まで消えるため、CLAUDE.md が不要という証拠にはならない。credentials と外部書き込みのない隔離環境に限る

### 手順

1. 固定 task set を先に決める (直近セッションから 5-10 件、成功/失敗が判定できるもの)
2. 物理削除ではなく**可逆に無効化**する — `skillOverrides`、パッチの `task restore-claude`、ブロック単位のコメントアウト
3. baseline (現状) と minimal (無効化後) を同じ task set で比較する
4. 戻すのは **同じ失敗が 2 回以上再現した一文・一機構だけ**。1 回の失敗では戻さない
5. 結果を `docs/decommission-log.md` に記録する。維持した項目も「なぜ残したか」を書く

### 測定軸

成功率だけでは足りない。「テストは通るが余計に 5 分考える」も劣化として数える。

- 再指示回数 / 人間の介入回数
- 検証コマンドの実行率
- 誤った安全判断の有無
- 消費トークンと所要時間
- skill の誤発火

### 撤退条件

比較に 2 セッション以上かかる、または task set の判定が割れて結論が出ない場合は中断し、baseline に戻す。
ablation は harness を良くするための手段であり、それ自体が作業を増やしているなら失敗している。

## Anti-Patterns

- 「念のため残す」は dead weight を増やす最大の原因。判断に迷ったら `Possibly stale` として実験
- 一度に大量削除しない。1サイクル最大 5 項目の除去に制限
- 削除時は git で追跡可能にし、必要なら `git revert` で復元できるようにする
