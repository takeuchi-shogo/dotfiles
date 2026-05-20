# Dashboard Template

`templates/obsidian-vault/Dashboard.md` の使い方・スキーマ・移行方針。

## 設計原則

- **Read-Not-Store**: Dashboard 自身は何も保存しない。query のみ。元ノート (task / daily / project) を更新すれば自動反映
- **3 セクションのみ**: Today / Carryover / Open Loops
- **スキーマ最小化**: 将来 Bases に移行する想定で、必要最小限の property だけ要求

## 要求 property

### Task ノート (任意の folder、`type: task`)

```yaml
---
type: task
status: open  # open | complete
due: 2026-05-19
priority: high  # high | medium | low
---
```

### Daily Note (`07-Daily/YYYY-MM-DD.md`)

```yaml
---
type: daily
date: 2026-05-19
---
```

`## Review` セクション内に `### 明日に持ち越し` を含めると、翌日の Dashboard で Carryover に表示される。`/timekeeper review` が自動で書き込む。

### Active project / area (`01-Projects/*`, `02-Areas/*`)

```yaml
---
type: project  # or "area"
status: open  # open | complete | archived
---
```

`status: open` だけ Dashboard の Open Loops に出る。Client/Revenue/Health は **意図的に含めない** (solo dev には不要)。

## 7 セクション dashboard を採用しない理由

参考記事 (@cyrilXBT 2026-05-19) は 6-section business dashboard (Today's Priorities / Active Projects / Next 7 Days / Client Health / Open Loops / Revenue Pulse) を推奨するが:

- Client / Revenue / Health は agency 文脈、solo dev には不要
- Next 7 Days は Today + Carryover で実質代替可能
- Active Projects 一覧は `01-Projects/` を直接見れば足りる
- 詳細: `docs/research/2026-05-19-cyril-obsidian-dashboard-absorb-analysis.md`

## Dataview 依存への注意 (重要)

**Dataview は 2026 でメンテモード移行。公式 Bases が新標準。**

- 既存 Dataview 資産は当面動作する
- 新規 dashboard を作る場合は Bases ベースを優先検討
- 本テンプレートは「Bases 移行が完了するまでの暫定 minimal 構成」と位置づける
- query 数 3 つに絞り、Bases へ移植する際の作業量を最小化

Bases 公式ドキュメント: <https://help.obsidian.md/Plugins/Bases>

## Verification

1. Vault に `Dashboard.md` を配置
2. Dataview plugin を有効化 (Settings → Community Plugins → Dataview)
3. `07-Daily/` 配下に 1-2 個の daily note を作成 (frontmatter `type: daily, date: YYYY-MM-DD` 付き)
4. `01-Projects/` か `02-Areas/` に `type: project, status: open` のノートを 1 つ作成
5. Dashboard を開き 3 セクションが render されるか確認

## 期待する dashboard 内容

- **Today**: 期日が今日以前で未完了の task が priority 順に最大 10 件
- **Carryover**: 昨日の daily note の `### 明日に持ち越し` セクション
- **Open Loops**: `status: open` のノート 15 件

何も表示されなくても、それは vault に該当ノートが無いだけで dashboard 側の問題ではない。

## Troubleshooting

| 症状 | 原因 |
|------|------|
| query が空 | frontmatter の property 名 typo (`status` を `state` にする等) |
| date 比較が壊れる | 日付は `YYYY-MM-DD` 形式必須 (`2026-5-19` は不可) |
| Carryover に何も出ない | (a) 昨日の daily note の subpath `### 明日に持ち越し` を timekeeper review が正しく書いているか、(b) `WHERE date(file.name) = date(today) - dur(1 day)` の左右が同じ型 (DateTime) になっているか — `string()` を被せると ISO 8601 文字列に変換されて `file.name` (`YYYY-MM-DD`) と一致しなくなる |
| 描画が遅い | `FROM ""` (vault 全体) を使わず、folder 指定で絞る (`FROM "01-Projects"`) |

## 将来計画

- [ ] Bases プラグイン安定化を確認 (2026 Q4 目処)
- [ ] Dashboard を Bases に移植 (Today / Carryover / Open Loops の 3 view)
- [ ] Dataview 版を Archive
