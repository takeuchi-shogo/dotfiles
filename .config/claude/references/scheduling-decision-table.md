# Scheduling Decision Table — どの仕組みでスケジュールを組むか

> 出典: Warp `oz-skills/scheduler` (2026-05-06 absorb)。`docs/research/2026-05-07-warp-oz-skills-absorb-analysis.md` の T5。
>
> 関連: `references/managed-agents-scheduling.md` (cloud Managed Agents 詳細)。

「いつ何かを実行する」ニーズが出たとき、まずこの 3 つの境界質問に答える。

## Step 1: 境界質問（必ずこの順で）

1. **クラウドで動かす必要があるか？** — マシンが寝ていても実行されてほしいか
2. **「タスク」か「リマインダー」か？** — 副作用を伴う実行なのか、人間に通知するだけなのか
3. **同一会話の中で待つのか？** — 今のセッション内で完結するのか、未来のセッションに持ち越すのか

回答の組み合わせで以下の 5 機構から 1 つに収束する。

## Step 2: 決定表

| 用途 | 機構 | コマンド/ツール | 実行コンテキスト | 永続性 |
|------|------|---------------|---------------|--------|
| **同一セッション内で N 分後に再開** | `ScheduleWakeup` | runtime tool | 今の会話（cache 維持） | セッション終了で消える |
| **同一セッション内で polling/loop** | `/loop` (skill) | `/loop 5m /foo` または dynamic | 今の会話 | セッション終了で消える |
| **未来の特定時刻に 1 回 / cron で繰り返す（クラウド）** | `/schedule` (skill) | `schedule` skill / Managed Agent routine | 別環境の Claude セッション | リソース消えるまで永続 |
| **OS レベルの定期 job** | `CronCreate` | runtime tool（cron-style） | OS の cron 経由で起動 | 削除するまで永続 |
| **複雑な多段タスクをセッション跨ぎで自走** | `/autonomous` (skill) | autonomous skill | 別セッションを生成 | task 完了まで |

## Step 3: 選択フローチャート

```
START
  │
  ├─ 「今の会話の中で N 分待ちたい」(<60min)
  │    └─→ ScheduleWakeup（cache 温存目的なら 60-270s 推奨）
  │
  ├─ 「同じ条件で何度も polling したい」(同一セッション)
  │    └─→ /loop（dynamic か interval 指定）
  │
  ├─ 「マシンが寝ても future の特定時刻に動かしたい」
  │    ├─ クラウド可: /schedule（Managed Agent routine）
  │    └─ ローカル必須: CronCreate（OS cron）
  │
  ├─ 「人間への通知だけで OK（副作用なし）」
  │    └─→ /timekeeper の朝/夕リマインダー、または OS notification
  │
  └─ 「複数セッション・長時間・自走」
       └─→ /autonomous
```

## Step 4: アンチパターン

| NG パターン | 何が起きるか | 代わりに |
|-------------|------------|---------|
| `/loop 5m` を 24h 走らせる | cache miss + token tax 累積 | `/schedule` で別セッション生成 |
| `ScheduleWakeup(3600)` を多用 | 5min cache TTL 超で cache miss | `/loop dynamic` か `/schedule` |
| polling のために `time.sleep()` で 5 分ブロック | bash timeout (120s) に当たる | `Monitor` か `ScheduleWakeup` |
| cron job をローカル UI 通知の代替にする | OS依存・通知パイプライン無し | `/timekeeper` か OS notification |
| 1 回限りの remind を `/loop` で組む | 撤退条件曖昧 | `/schedule once at <time>` |

## Step 5: クラウド vs オンデバイスの線引き

Warp の `scheduler` skill は **明示的にクラウド agent scheduling を回避** している（自社の Oz cloud との利益相反を避ける design choice）。当 dotfiles は逆に **両方を持っており用途で使い分ける**:

| 性質 | オンデバイス推奨 | クラウド推奨 |
|------|---------------|------------|
| 機密情報を扱う | ✅ CronCreate / `/timekeeper` | — |
| マシン off でも実行必須 | — | ✅ `/schedule` (Managed Agent) |
| 副作用が PR/issue/Slack 投稿 | どちらでも可 | ✅ Managed Agent (token 永続) |
| 人間への通知のみ | ✅ オンデバイス | — |
| 失敗 retry/observability 必要 | — | ✅ Managed Agent (履歴付き) |

## 撤退条件

- ScheduleWakeup を 30 日以上使っていない → ScheduleWakeup の awareness が失われている合図
- `/loop` と `/schedule` の混同が `friction-events.jsonl` に 3 件以上 → この決定表を CLAUDE.md `<important>` に昇格
