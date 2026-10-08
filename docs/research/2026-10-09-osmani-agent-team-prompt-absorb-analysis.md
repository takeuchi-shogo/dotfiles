---
title: Addy Osmani の agent team プロンプト (X @0xCodila 経由)
date: 2026-10-09
status: integrated
family: multi-agent-orchestration
source:
  - https://x.com/0xCodila/status/2107956794320355681
  - https://claude.dev/blog/getting-the-most-out-of-opus-5-5/
  - https://addyosmani.com/blog/claude-code-agent-teams/
---

# Osmani agent team prompt absorb

## Source Summary

**主張**: 投稿 (2026-10-07) は motion-design 向けプロンプトの宣伝。引用されている記事 (2026-10-05)「How to Get Money for Creating Motion Design with Opus 5.5 & Fable 5.5」は収益化ガイドで、Paid Partnership (Viktor) の紹介リンクが付いている。この記事は採用の根拠に使わない。取り込み対象は添付画像の「agent team」プロンプトで、Addy Osmani 名義。次の 4 つを編集したものとされる。

- claude.dev/blog/getting-the-most-out-of-opus-5-5/
- addyosmani.com/blog/claude-code-agent-teams/
- addyosmani/agent-skills の `planning-and-task-breakdown`
- 同 `incremental-implementation`

**手法** (M1-M13):

- M1 受け入れ条件つきの小さなタスク
- M2 最初は read-only で探索
- M3 teammate ごとにファイルの持ち主を決める
- M4 依存関係つきの共有タスクリスト
- M5 並列化の 3 分類 (安全 / 順次必須: DB migration・共有 state・依存チェーン / 調整が要る: 契約を先に決める)
- M6 薄い縦切りスライス。壊れた状態で残さない
- M7 subagent の報告は証拠を確認してから受け入れる
- M8 teammate を待つ
- M9 main との diff をレビュー。merge を止めるのは file:line と失敗の示し方がある指摘だけ
- M10 未確認は未確認と書き、どこを探したかを添える
- M11 止まるのは blocked のときか破壊的操作の前だけ
- M12 TASKS.md のチェックリスト
- M13 毎回の終わりに Blocked on me / Changed / Found の 3 見出し

**根拠の検証状況**:

- 取得経路は fxtwitter API (WebFetch) と画像 Read。Chrome 拡張はタイムアウトした。
- claude.dev の投稿は Addy Osmani 名義で、次の 3 文が WebFetch で確認できた。
  - "End every run with three headings: Blocked on me, Changed, Found"
  - "Put status notes in the same message as your next action"
  - "When a subagent reports back, check its evidence before you accept it"
- M5 の 3 分類は claude.dev の投稿にない。同投稿は migration をサービスごとに subagent へ分割する提案に留まる。3 分類の出どころは agent-skills 側とみられるが、こちらでは未確認。
- Gemini は「Osmani は 2026-09 に Anthropic へ移った」と述べたが、独立には確認していない。

**前提条件**: Claude Code の agent teams / subagent で、複数のエージェントが同じ repo を並列に触る運用。

## Saturation Gate (Phase 1.5)

family は `multi-agent-orchestration`。N = ベースライン 17 + 新規 3 (2026-08-02 codex-orchestrator 採用 1 / 2026-08-03 torukona 採用 0 / 2026-08-03 intent-cli implemented) + skipped 0 = 20。採用率は 20% 以上で PASS (warning)。Step 4.5 は発火しない。

著者 @0xCodila は 2026-07-25 の graph-engineering absorb と同じ。

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| M1 | 受け入れ条件つき小タスク | Already | `task-decomposition-guide.md:27` の INVEST |
| M2 | read-only 探索が先 | Already | `workflow-guide` の Explore |
| M3 | ファイル所有権 | Already | `session-pool-guide.md:41-43` |
| M4 | 依存つき共有タスクリスト | Already | `subagent-delegation-guide` の Agent Teams `blockedBy` |
| M5 | 並列化の 3 分類 | Partial | 下の Pass 2 を参照 |
| M6 | 薄い縦切りスライス | Already | `pr-splitting-patterns.md:19` |
| M7 | subagent の証拠確認 | Partial | 受け手側の検証規律が未明文 |
| M8 | teammate を待つ | Already | `subagent-delegation-guide.md:568` |
| M9 | diff レビュー / merge 阻止の条件 | Already | review skill の BLOCK / Critical、codex-reviewer の "Do NOT pad" |
| M10 | 未確認の明示 + 探索範囲 | Partial | M7 と同じ穴 |
| M11 | blocked か破壊的操作前だけ止まる | Already | Claude Code system prompt + `references/auto-accept-policy.md` |
| M12 | TASKS.md | N/A | `PLANS.md` の Progress と Surprises & Discoveries が担う |
| M13 | 3 見出しの締め | 棄却 | 下の Integration Decisions を参照 |

Pass 1 の Sonnet Explore は M11 を not_found と報告したが、grep しただけの 2 ファイルを読んでいなかった。Opus の再確認と Codex の指摘で `auto-accept-policy.md` が該当すると分かり、Already に直した。この誤判定は採用した M7+M10 のルールがそのまま当てはまる実例になった。

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | M1-M4, M6, M8 の既存ガイド群 | 見当たらない | なし | 強化不要 |
| S2 | review skill / codex-reviewer (M9) | 見当たらない。code-review family は飽和 | なし | 強化不要 |
| S3 | `subagent-delegation-guide.md` の「並列コード書き込みの危険性」と「Shared File Detection Rule」(M5) | 契約先行と直列化は既に書いてある。穴は Parallelizability Gate の表が推論依存の軸しか持たず、この 2 節へ導かないこと。「DB migration」も名指しされていない | Gate 表の直下に 1 段落。2 節へリンクし、DB migration・共有 state・lockfile を順次必須、共有 API は契約先行と明記 | 強化可能 |
| S4 | M11 の既存規律 | Codex の訂正で N/A から Already に変更 | なし | 強化不要 |

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| M7+M10 | subagent 報告の受け手側検証 | 採用 | Handoff Packet の直後に「### 報告を受け取る側の検証」を新設。exists / not_found に使った file:line は自分で開く。not_found には探した root・query / command・除外範囲を必須とし、欠けるなら Unconfirmed に落とす。置き場は受け手側の guide (`subagent-delegation-guide.md`)。送り手側の `subagent-framing.md` には置かない (Codex) |
| M13 | 3 見出しの締め | 棄却 | Osmani の claude.dev 投稿は公式に推奨している。ただし毎回強制すると prose の出力スタイルと衝突する。無人実行には progress.md と error report (`unattended-pipeline.md`) が既にある。Codex も前提のずれを指摘 |
| M12 | TASKS.md | N/A | `PLANS.md` が同じ役割を持つ |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S3 | Gate 表への導線 (M5) | 採用 | 新規ルールは足さない。既存 2 節への参照と、名指しされていなかった DB migration の追記だけにした |
| S1, S2, S4 | M1-M4, M6, M8, M9, M11 | スキップ | 既存で足りる。足すと instruction DRY 違反 |

## Phase 2.5 批評

- **Codex** (`codex exec` gpt-5.6-terra / read-only / xhigh / `project_doc_max_bytes=0`。cmux が無いため fallback)。冒頭の結論は次のとおり。
  「結論：採用は P1（M7+M10）だけで十分です。P2 は導線改善に留めます。変更はしていません。」
  訂正は 3 件。M11 を N/A から Already へ、M5 を Partial から Already (強化可能) へ、M13 は前提のずれとして棄却。
- **Gemini** (agy grounding)。並列 agent team の主な失敗は、前提の衝突や migration 競合と、捏造された証拠 (テストしていない pass 報告) だとした。トークンコストは 3-10 倍。代替案として worktree 隔離と、決定論的な hook / CI gate を挙げた。出典 URL は個別に検証していない。割り引いて読む。

## Plan

### Task 1: subagent 報告の受け手側検証 (M7+M10) と Gate 導線 (M5)
- **Files**: `.config/claude/references/subagent-delegation-guide.md` (+11 行)
- **Changes**: Parallelizability Gate 表の直下に導線 1 段落 (L1064 付近)。Handoff Packet の直後に「### 報告を受け取る側の検証」(L1077 付近)
- **Size**: S
- **Verify**: 上記の 2 アンカーが存在することを確認済み。`task validate-configs` は通過

## 教訓

1. 同じ family でまた、収穫は新しい機構ではなく受け手側の規律だった。送り手側の枠組みは出尽くしている。
2. Pass 1 の not_found は、探した範囲が書いていなければ信用しない。この absorb 自体が、採用したルールの実演になった。
3. 宣伝記事の外側に、正当な一次ソースが埋まっていることがある。Gemini の「事実」ラベルに頼らず、一次ソースを直接取って確かめる。
