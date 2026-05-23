---
name: output-review
description: >
  毎週金曜 15 分で「今週 Claude の出力でダメだったもの」を棚卸しし、修正ルールを抽出して
  CLAUDE.md / feedback memory / skill に codify する weekly cadence。
  Triggers: 'output-review', '今週の Claude 出力レビュー', 'feedback loop', '金曜レビュー'.
  Do NOT use for: 日次 belief 振り返り (use /timekeeper review)、GTD 棚卸し (use /weekly-review)、
  個別タスクの retro (use retrospective-codify)、コード変更レビュー (use /review)。
origin: self
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash(ls *), Bash(cat *), Bash(grep *), Bash(date *)
metadata:
  cadence: weekly-friday-15min
---

# Weekly Claude Output Review

「今週 Claude が出した output のうち、自分の standard に届かなかったもの」を 3 質問で棚卸しし、
**修正ルールを抽出して codify** する weekly feedback loop。

## なぜ必要か

- 個別の訂正は `retrospective-codify` で都度 capture できるが、**棚卸しの時間枠** がないと
  「忙しさで流した訂正」が rule に昇格しない
- `/timekeeper review` (日次) は belief 変化と未解決の問いを拾うが、
  「Claude output 品質」に専用フォーカスしない
- `/weekly-review` (GTD) は Issue + Inbox の棚卸しで、AI 出力品質とは直交

→ 週 1 回 15 分、Claude 出力品質だけを review する dedicated time が compounding effect を生む。

## When to Run

- **推奨**: 毎週金曜 17:00 前後、15 分間
- **代替**: 週末・月曜朝でも可。重要なのは **毎週同じ時刻** に固定すること
- **頻度**: 週 1 回。日次にすると粒度が細かすぎ、月次にすると訂正の記憶が薄れる

## Workflow (15 分)

### Step 1: 今週のセッション棚卸し (3 分)

```bash
# 今週の session log を列挙 (session_observer 経由)
ls -lt ~/.claude/projects/-Users-takeuchishougo-dotfiles/observer/sessions/ \
  | head -20
# 直近の retrospective-codify / feedback_*.md 追記を確認
ls -lt /Users/takeuchishougo/.claude/projects/-Users-takeuchishougo-dotfiles/memory/feedback_*.md \
  | head -10
```

「今週どんな仕事を Claude にやらせたか」を 30 秒で思い出す。

### Step 2: 3 質問 (10 分)

記事 #29 verbatim (Khairallah 30 Workflows, 2026-05-23):

**Q1. 今週の Claude 出力で、自分の standard に届かなかったものは何か？**
- 具体的にどの output か (PR 文 / commit message / spec / explanation / code)
- 何がダメだったか (vague / 形式違反 / tone ミスマッチ / 仕様取りこぼし / Sonnet imagination 等)
- 訂正したか、流したか

**Q2. どの instruction (CLAUDE.md / skill / memory) を変えればその出力は防げたか？**
- 既存 rule のどこに穴があったか
- 新規 rule を追加すべきか、既存 rule を強化すべきか
- どのファイル (`CLAUDE.md` / `references/*.md` / `skills/*/SKILL.md` / `memory/feedback_*.md`) に
  codify するのが適切か

**Q3. 来週の workflow に追加すべき新しい task はあるか？**
- 来週も同じ output を出す予定があるか
- その時に Q1 の問題を防ぐ workflow 変更が必要か (新 skill / hook / pre-flight check 等)

### Step 3: Codify (2 分)

Q2 の答えを **その場で codify** する。後回しにすると忘れる。

| 修正の種類 | 保存先 | Tool |
|---|---|---|
| 1 回限りの訂正 | `memory/feedback_*.md` (新規 or 既存追記) | Edit |
| 複数 skill 横断ルール | `CLAUDE.md` (project or global) | Edit |
| 特定 skill 内ルール | `skills/{skill}/SKILL.md` の Anti-Patterns or Output Self-Check | Edit |
| 自動化可能な検出 | hook 追加候補として `docs/plans/` に保存 (実装は別タスク) | Write |

**codify したら本セッションで完結**。来週金曜まで持ち越さない。

## Anti-Patterns

| NG | 理由 |
|----|------|
| 「特に問題なかった」で 5 分で終わらせる | 訂正は無意識に流している。意図的に思い出す 10 分が必要 |
| 棚卸しだけで codify しない | rule に昇格しない訂正は再発する。Step 3 をスキップしない |
| 月曜まで持ち越す | 訂正の記憶は週末で薄れる。金曜中に codify する |
| 個別タスクの retro と混同 | retrospective-codify は 1 タスク完了時。本 skill は **週次の棚卸し** で粒度が違う |
| 5 件以上 codify しようとする | 15 分で codify できる範囲 (1-3 件) に絞る。残りは来週へ |

## Differences vs 既存 skill

| skill | 主題 | cadence | 出力 |
|---|---|---|---|
| `/timekeeper review` | belief 変化・未解決の問い | 日次 (夕方) | Daily Note に追記 |
| `/weekly-review` | GitHub Issue + Obsidian Inbox 棚卸し | 週末 | 優先度再見直し |
| `retrospective-codify` | 1 タスク完了時の「先に失敗→後に成功」 codify | タスク完了時 | ast-grep rule / skill / CLAUDE.md |
| **`/output-review`** | **Claude 出力品質の棚卸し + rule 抽出** | **毎週金曜 15 分** | **feedback_*.md / CLAUDE.md / SKILL.md 更新** |

## Chaining

- 個別 task の retro が必要なら → `retrospective-codify`
- codify したルールを skill に embed したいなら → `superpowers:writing-skills`
- hook 化候補が見つかったら → `docs/plans/` に保存して別セッションで実装

## 出典

- Khairallah "30 Claude Workflows" #29 (2026-05-23): 3 質問 verbatim
- `docs/research/2026-05-23-khairallah-30-workflows-absorb-analysis.md` — 採用理由と既存 skill との直交性の根拠
