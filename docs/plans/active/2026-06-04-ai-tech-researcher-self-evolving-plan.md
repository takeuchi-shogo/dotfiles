---
status: active
---

# Plan: 自己進化型 AI tech researcher パイプライン

> **Status**: 設計確定・実装待ち (backlog)。実装は新セッションで `/rpi` から着手する。今セッションでは absorb の Phase 4 (Plan 策定) までを完了している。frontmatter `status: active` は「実装は別セッションが所有する」を意味し、completion-gate の Ralph Loop 対象から除外される (今セッションでの即時実装を強制しない)。

- **Created**: 2026-06-04
- **Source absorb**: `docs/research/2026-06-04-ai-tech-researcher-self-evolving-absorb-analysis.md`
- **Source article**: Zenn「1年間の育休に備えて『勝手に賢くなる』AI情報収集基盤を作った」(tokium_dev, 2026-04-27)
- **Scale**: L (新 skill + 新 script 群 + launchd + JSONL ledger + 段階的自己進化機構)
- **Owner decision**: ユーザーが「新規 AI tech researcher を作る」+「L ロードマップを plans 化」を選択 (Triage で A/B/C 全採用)
- **Guiding constraint**: 記事のフル自己進化を一気に作らない。Codex/Gemini が一致警告した「評価指標ゲーミング + コールドスタート + エコーチェンバー」を各段階で mechanism として封じる。read-only 実験 (Phase 1) から段階的に価値を出し、各段に撤退ポイントを置く。

## Goal

dotfiles に、既存 morning-briefing とは**別軸**の「AI 技術トレンド専用リサーチャー」を構築する。Zenn/Qiita/AI 各社ブログを定期収集 → claude -p で選別レポート化 → **どの情報源が実際にレポートに採用されたか**を ledger に記録し、その採用実績を**補助シグナル**として情報源を**全自動進化**させる (2026-06-05 方針: 記事と同じ「勝手に賢くなる」、人間承認なし)。記事の核 (採用実績フィードバック) を、記事に無かった **algorithmic 安全装置 (MAB/MMR/減衰)** 付きで実装する。

## 軸の分離 (morning-briefing との非重複を固定)

| | morning-briefing (既存・稼働中) | tech-researcher (新規・本plan) |
|---|---|---|
| 目的 | 今日の自分のタスク/予定/CI | AI 技術トレンドの定点観測 |
| ソース | HN top / arXiv cs.AI / 手動 RSS / nightly status | Zenn/Qiita/AI 各社ブログ (自己進化) |
| 出力 | Obsidian Daily Note (朝) | 専用 daily/weekly レポート |
| 進化 | なし (固定ソース) | 採用実績ベースの全自動進化 (MAB/MMR/減衰ガードレール付き) |

**この分離を Decision Log で固定する。** 機能重複が判明したら researcher を morning-briefing へ統合縮退する (撤退条件参照)。

## Success Criteria

- **Phase 1 (MVP, これが最小完了線)**: tech-researcher が launchd で日次稼働し、固定シードソースから記事収集 → claude -p で選別日次レポート生成 → 採用記事の出典ドメインを `sources-ledger.jsonl` に append + 直近30日の採用ドメイン頻度を read-only で集計出力できる。
- **Phase 2-4**: 各 Phase 完了線は下記 Tasks に individual に記載。各 Phase 終了時に「次 Phase に進むか撤退か」を撤退条件で判定する。

## Scope

**触る (新規):**
- `.config/claude/skills/tech-researcher/SKILL.md` — 収集+選別の処理指示 (記事の SKILL.md + shell 2層を踏襲、既存 dispatch/launch-worker パターン流用)
- `scripts/runtime/tech-researcher/collect.sh` — 情報源から記事収集 (morning-briefing の RSS fetch + SSRF対策 + sanitize を流用)
- `scripts/runtime/tech-researcher/report.sh` — claude -p で選別レポート生成 + 採用 ledger 記録
- `scripts/runtime/tech-researcher/aggregate.py` — 採用ドメイン30日集計 (read-only, pure logic)
- `~/Library/LaunchAgents/com.user.tech-researcher.daily.plist` — 日次トリガー
- データ: `~/.cache/tech-researcher/` (sources-ledger.jsonl, adoption-ledger.jsonl, reports/)

**触らない:**
- `auto-morning-briefing.sh` および morning-briefing skill (別軸、非干渉)
- `learned-promotion-loop` / `patterns.jsonl` / `promoted-ledger.jsonl` (運用ログ昇格は別ドメイン。Phase 2 で「採用実績シグナルの ledger 設計」を参考にするのみ、配線はしない)
- 既存 nightly launchd 群 (Phase 4 で health-check に1行統合するのみ)

## Constraints

- `git commit --no-verify` 禁止。lint config 保護。
- データ形式は **JSONL** で開始 (dotfiles 一貫性: patterns.jsonl/promoted-ledger.jsonl 前例。記事は SQLite だが個人規模では JSONL append で十分)。クエリ負荷が問題化したら Phase 2 で SQLite 再評価。
- 外部データ取得は morning-briefing の SSRF 対策 (`^https?://` のみ許可、`curl --` でオプション注入遮断、prompt injection 用 nonce sentinel) を**必ず流用**する。
- claude -p 呼び出しは `--max-turns` 明示 + lock (`acquire_claude_lock` 既存ヘルパ) で暴走/二重実行防止。
- Slack 2軸 (チャンネル/ユーザー監視) は **実装しない** (個人 dotfiles に社内 Slack 監視は N/A、プライバシー境界)。記事4軸のうち「キーワード軸」「Webソース軸」の2軸のみ。

## 撤退条件 (reversible-decisions)

- **R1**: Phase 1 を30日運用して採用ドメイン集計が「既存 morning-briefing RSS と同じ顔ぶれ」しか出さない → 自己進化は YAGNI 確定。Phase 2 以降を中止し read-only 集計だけ残す。
- **R2**: claude -p daily 選別コストが morning-briefing と二重で無駄と判明 → researcher を morning-briefing に統合縮退 (別軸維持をやめる)。
- **R3**: Phase 3 の MAB 探索 / 多様性強制が「探索ノイズばかり」生む (探索枠から採用される良ソースが3サイクルで0) → 探索枠を 0 にして pure 採用ベースに縮退。
- **R4** (2026-06-05 改訂、auto-apply 化に伴い human-reject ベースから mechanism ベースへ): auto 昇格降格が品質を悪化させる兆候を mechanism で検出したら自動進化を凍結し固定ソース運用へ戻す。検出条件 (いずれか): (a) アクティブソースの多様性 (異クラスタ数) が 3サイクル連続で単調減少 (エコーチェンバー進行)、(b) retired したソースが2サイクル以内に再昇格を繰り返す (判定の不安定)、(c) sanity gate の昇格降格上限に毎サイクル張り付く (急変が常態化)。凍結は `evolution-ledger.jsonl` に記録し、ユーザーに Discord 通知 (事後に気づける)。

## 失敗モード (pre-mortem)

- **評価指標ゲーミング (Goodhart)**: 採用数を主指標にすると LLM が「要約しやすい浅いソース」を好み洞察ソースが降格 (Codex+Gemini 一致警告) → 採用数は**補助指標**に留め、LLM-as-judge 多軸 (新規性/信頼性/具体性) + 多様性強制を必須化。
- **コールドスタート**: 新規良ソースが採用実績0で永遠に日の目を見ない (Gemini) → Phase 3 で MAB 探索ボーナス (UCB1/Thompson) 必須。
- **エコーチェンバー**: 採用ソース優先で視点が偏り弱信号が消える (Gemini) → MMR で異クラスタソースを一定割合強制注入。
- **非定常性**: 優良ソースのスパム化に降格ラグ (Gemini) → 採用スコアに時間減衰を入れる。
- **drift 再発**: researcher 自体が autoevolve-runner.sh の二の舞 (cron 未登録で動かないまま放置) → Phase 4 self-audit で launchd 登録を検証。Build to Delete: 「morning-briefing に吸収できれば不要」を設計問とする。
- **二重メンテ**: morning-briefing と機能重複 → 軸分離表を Decision Log で固定、R2 で監視。

## Tasks

### Phase 1 — read-only MVP (S〜M, これが最小完了線)
- **Task 1.1** `collect.sh`: 固定シードソース (Zenn AI topic feed, Qiita AI tag feed, 主要 AI 各社ブログ RSS 3-5本) から記事タイトル+URL を収集。morning-briefing の `extract_feed_titles`/`sanitize_title`/SSRF 対策を流用。
- **Task 1.2** `report.sh`: 収集記事を claude -p に渡し「AI技術トレンドとして重要な記事」を選別 → 日次 markdown レポート生成。選別で**採用した記事の出典ドメイン**を `adoption-ledger.jsonl` に append (`{date, domain, url, title, adopted:true/false}`)。nonce sentinel で prompt injection 防御。
- **Task 1.3** `aggregate.py`: `adoption-ledger.jsonl` を読み直近30日の採用ドメイン頻度を集計 → レポート末尾に「採用上位ドメイン (RSS候補)」を read-only 出力 (自動追加はしない)。
- **Task 1.4** launchd plist: 日次トリガー (時刻は morning-briefing 8:30 と重複回避、例: 平日 9:00 or 夜)。
- **完了線**: 30日 ledger が貯まり、集計が出る。Success Criteria 達成。→ R1 判定ポイント。

> **Phase 2 セキュリティ前提 (review 由来)**: Phase 1 では `sources.txt` が信頼制御の静的ファイルのため SSRF は `^https?://` + `curl --proto/--/--max-filesize` で十分。**Phase 2 で `sources-ledger.jsonl` に外部由来 URL が動的投入されるようになる前に**、host 検証へ private/link-local IP リテラル denylist (`127.`, `169.254.`(IMDS), `10.`, `192.168.`, `::1`, `localhost`) を追加すること (security-reviewer 指摘、defense-in-depth)。

### Phase 2 — source ledger 正式化 + 多軸選別 (M)
- **Task 2.1** `sources-ledger.jsonl`: 情報源を構造化記録 (`{type:keyword|web, value, added_date, score, last_adopted, status:active|candidate|retired}`)。キーワード軸 + Webソース軸の2軸。
- **Task 2.2** LLM-as-judge 多軸選別: report.sh の選別を「採用/不採用」二値から「新規性/信頼性/具体性」多軸スコアに拡張 (Gemini 推奨、単一採用数指標の罠を回避)。
- **Task 2.3** 採用スコアは**補助指標**として記録 (B の思想: `accepted_in_report` / `reused`)。主指標化しない。
- **完了線**: sources-ledger が多軸スコアで情報源を記録できる。
- **依存**: Phase 1 + R1 が「進む」判定。
- **レビュー由来の forward-compat 注意 (2026-06-05 review gate)**:
  - `adoption-ledger.jsonl` に **`source_id` フィールド**を Phase 2 で追加する (現状は domain/url のみ。sources-ledger との join キーが無いと多軸進化で source を一意特定できない)。Phase 1 の既存行は source_id 欠落のまま許容 (migration: 後方互換読みで null 扱い)。
  - `sources-ledger` の **`type:web` の正確な定義**を固定する (feed URL 単位か domain 単位か)。Phase 1 は feed URL 単位で収集・domain 単位で集計しており粒度が混在。Phase 2 で「進化の単位」を明示決定する。
  - **ledger migration/retention 戦略**を Phase 2 着手時に決める (adoption-ledger は無限 append。30日窓集計なので古い行は集計に効かないが、ファイル肥大時の rotation/archive 方針を要決定)。
  - **「adopted block 欠落でスキップした日」と「採用0件の日」の区別**: Phase 1 は前者で ledger 記録自体を skip (捏造防止)、status JSONL の `metric.adopted` + `LEDGER_NOTE` で観測可能。Phase 2 で aggregate がこの 2 状態を集計上どう扱うか (採用率分母から除外するか) を明示する。

### Phase 3 — 安全な全自動進化 (M〜L)
- **Task 3.1** 昇格降格 (**auto-apply、人間承認なし** — 2026-06-05 方針転換): 採用頻度上位ドメインを RSS 候補に自動昇格、長期未採用を candidate→retired に自動降格。承認ゲートの代わりに **sanity gate** を置く: (a) 1サイクルの昇格/降格は各最大 N 件 (急変防止)、(b) retired は即削除せず `candidate` を経由する2段階 (誤降格の復帰余地)、(c) 全 昇格降格を `evolution-ledger.jsonl` に追記し事後監査可能にする。MAB/MMR/減衰 (Task 3.2-3.4) が健全性を担保する前提。
- **Task 3.2** MAB 探索 (UCB1 or Thompson): 実績少ソースに探索ボーナスを付与し収集対象に一定枠で混ぜる (コールドスタート対策)。
- **Task 3.3** 多様性強制 (MMR): 収集/選別で異クラスタソースを一定割合保証 (エコーチェンバー対策)。
- **Task 3.4** 時間減衰: 採用スコアに減衰係数 (非定常性対策)。
- **完了線**: 月次提案で source が承認ベースで進化し、探索枠/多様性枠が機能する。→ R3/R4 判定ポイント。
- **依存**: Phase 2。

### Phase 4 — drift 自己監視 (S, C の採用)
- **Task 4.1** self-audit: tech-researcher の launchd が登録済みかつ直近 N 日に実際に実行されたかを検査する script。
- **Task 4.2** 既存 nightly health-check に1行統合し、未実行 drift を Discord 通知 (autoevolve-runner.sh の「登録漏れで動かない」二の舞防止)。
- **完了線**: researcher が動いていない状態を mechanism で検出できる。
- **依存**: Phase 1 (launchd 存在後ならいつでも実行可、Phase 2-3 と並行可)。

### Phase 5 — absorb-candidate bridge (M, 2026-06-05 追加)
**目的**: 「賢くなるだけ（情報源の自己進化）」を「ハーネス改善にも還元する」へ拡張する。tech-researcher が拾った高価値記事を `/absorb` 候補として surface し、skill/agent/references 改善の入口に繋ぐ。現状 tech-researcher は absorb/learned/autoevolve のどれにも配線されていない消費パイプライン (grep 確認済) — この分断を埋める。

**核心制約 (絶対)**: **候補を surface するだけ。`/absorb` は人間トリガーのまま**。auto-absorb は禁止。理由 = 2 つの進化ループはステークが違う:
| ループ | 自動度 | 根拠 |
|--------|--------|------|
| 情報源の進化 (Phase 3) | 全自動 + ガードレール | フィード選びは低ステーク・可逆 |
| ハーネス改善 (Phase 5→/absorb) | **人間ゲート維持** | skill/agent 変更は高ステーク・判断重。`/absorb` の Saturation Gate / Pruning-First / Thoroughness が noise 取り込みを防ぐ (2026-06-04 tier-list 記事が Saturation Gate で正しく SKIP されたのが証拠) |

- **Task 5.1** harness-relevance シグナル: 「採用 (= AI トレンドとして重要)」と「absorb 価値 (= 自分の harness を改善しうる)」は別概念。Phase 2 の LLM-as-judge 多軸に **`harness_relevance` 軸**を追加 (例: 新 Claude Code 機能 / agent 設計 / prompt 技法 = 高、純研究論文 = 低)。adoption 数を流用しない。
- **Task 5.2** 候補 surface: 日次/週次レポート (と Obsidian `09-TechTrends/`) 末尾に「## /absorb 候補」セクションを追加。harness_relevance 上位記事を、1行の「なぜ harness 改善に効きうるか」+ そのまま叩ける `/absorb <url>` コマンド付きで列挙。**自動実行はしない**。
- **Task 5.3** (任意) 候補→absorb の追跡: どの候補が実際に absorb されたかを read-only 記録 (Phase 5 自身の有効性測定)。ここも auto-loop 化しない。
- **完了線**: 週次レポートに「人間が叩くだけの /absorb 候補リスト」が出る。
- **依存**: Phase 2 (harness_relevance 軸が必要)。Phase 3 とは独立。
- **撤退条件 (R5)**: surface された /absorb 候補が継続的に低価値 (3 サイクル連続で user が無視 or Saturation Gate skip) → bridge は YAGNI、Task 5.2 を撤去し read-only 集計のみ残す。

## 実行順序

1. **Phase 1** (MVP, 単独で価値) → **R1 判定**
2. R1=進む なら **Phase 2** → **Phase 3** (R3/R4 判定)
3. **Phase 4** は Phase 1 後いつでも (Phase 2-3 と並行可)
4. **Phase 5** は Phase 2 後 (harness_relevance 軸に依存)。Phase 3 と並行可

## Progress

- [x] Phase 1: read-only MVP (Task 1.1-1.4) — **2026-06-04 実装完了** (`/rpi`)。
  実装: `scripts/runtime/tech-researcher/{lib/feed.sh, sources.txt, run-tech-researcher.sh, aggregate.py, tests/test_aggregate.py}` + `nightly/launchd-install.sh` に登録1行。
  Phase 1 実装プラン: `tmp/plans/breezy-painting-zebra.md`。
  設計差分: standalone launchd → **nightly ゲート相乗り** (ユーザー選択) で Phase 4 をほぼ無料化。SKILL.md は未作成 (headless `claude -p` は skill 非起動、YAGNI)。
  検証: collect/ledger/aggregate/lock/timeout ガードは DRY_RUN・合成テスト・pytest(8)で実証。
  **2026-06-05 live 走行成功** (53s, status=ok): 23記事収集 → claude -p 選別で **10採用/13不採用** (全件採用でなく宣伝/ポエム/経営論/ニッチを除外、LLM-as-judge が機能) → ledger 23行 (valid JSONL) → 30日集計が差別化採用率 (zenn 36%/hf 80%/qiita 25%) を出力。nonce sentinel injection 防御込みで全パイプライン実証。
  **launchd 登録済み** (`com.user.nightly.tech-researcher` load 済、23:55 起動)。`launchd-install.sh` 実行不要 (既に plist 生成 + load 済)。
  **観測 (未修正・プラン範囲外)**: `nightly-status.sh` の `should_run_today` は `already ran today` チェックが `FORCE_RUN` チェックより先にあり、FORCE_RUN=1 でも同日再実行をバイパスできない (DOW/DOM ゲートのみバイパス)。検証時は last-run マーカー手動削除で対処。FORCE_RUN の文書上の意図 (強制=検証用) と乖離だが共有インフラのため別途棚卸し。
- [ ] R1 判定 (30日運用後)
- [ ] Phase 2: source ledger + 多軸選別
- [ ] Phase 3: 全自動進化 (MAB/MMR/減衰 + auto-apply + sanity gate、human 承認なし)
- [ ] Phase 4: drift 自己監視
- [ ] Phase 5: absorb-candidate bridge (harness 改善還元、人間ゲート維持)
- [ ] R3/R4/R5 判定

## Decision Log

- **2026-06-04**: 軸分離を固定 — morning-briefing (個人タスク/HN/arXiv) と tech-researcher (AI技術トレンド/Zenn/Qiita) は別軸。重複したら R2 で統合縮退。
- **2026-06-04**: データ形式は JSONL で開始 (dotfiles 一貫性)。記事は SQLite だが個人規模では過剰。
- **2026-06-04**: 記事4軸のうち Slack 2軸は N/A (個人利用にプライバシー境界)。キーワード+Web の2軸のみ。
- **2026-06-04**: 採用実績は補助指標に留める (Codex+Gemini 一致警告: 主指標化は評価ゲーミングを招く)。
- **2026-06-04 (実装)**: 実行インフラを **nightly ゲート相乗り**に決定 (standalone launchd を不採用)。実行が `~/.cache/nightly/status-*.jsonl` に自動記録され Phase 4 drift 監視が既存 health-check の JSONL 読みに縮退するため。軸分離は出力先 (Obsidian 非依存、`~/.cache/tech-researcher/`) で担保。
- **2026-06-04 (実装)**: claude -p 暴走防止は `timeout 600s` のみ。`--max-turns` は CLI に非存在、`--tools ""` / `--max-budget-usd` は付与すると `claude -p` が "Execution error" を返すため使用不可 (実地確認)。
- **2026-06-05 (スコープ拡張)**: Phase 5 (absorb-candidate bridge) を追加。tech-researcher は現状 harness 改善ループ (absorb/learned/autoevolve) に未配線の消費パイプライン (grep 確認) → 高価値記事を `/absorb` 候補として surface し skill/agent 改善に還元する。**核心制約: 候補 surface のみ、/absorb は人間トリガー維持** (auto-absorb 禁止)。情報源進化 (全自動) と harness 改善 (人間ゲート) はステークが違うため自動度を分離する。
- **2026-06-05 (方針転換)**: ユーザーが **「全自動で勝手に進化」(記事と同等)** を選択。Phase 3 の **human-in-loop 承認を撤廃**し auto-apply にする。ただし記事に無かった **algorithmic ガードレール (MAB 探索 / MMR 多様性 / 時間減衰) を必須維持** — これらは人間の手間ではなく、評価ゲーミング/コールドスタート/エコーチェンバー (Codex+Gemini 一致警告) を mechanism で封じる装置。「人間は何もしない、システムが健全に自己進化」を実現する。承認ゲートの代替として **sanity gate** (1サイクル昇格降格上限・retired は candidate 経由の2段階・全変更を decision ledger に追記し事後監査可能) を置く。staged rollout (Phase 1 read-only 先行) は cold-start ウォームアップとして維持 (データ蓄積 ~2-3週まで進化は意味を持たない)。

## Surprises & Discoveries
- **2 つの runtime ツリー併存**: top-level `scripts/runtime/` (git 直管理、nightly が直接指す) と `.config/claude/scripts/runtime/` (nix home-manager → `~/.claude/scripts/`)。流用元が分散 — feed ヘルパは後者、`acquire_claude_lock` は前者。tech-researcher は前者ツリーに配置し feed ヘルパを `lib/feed.sh` にコピー。
- **日本語フィードで `tr` が "Illegal byte sequence"**: morning-briefing の `extract_feed_titles` 流用時、UTF-8 ロケールで `tr` が日本語に失敗。`LC_ALL=C tr` (byte 指向) で回避。morning-briefing は英語中心 (HN/arXiv) で未顕在だった。
- **`set -e` + `pipefail` + `grep | head | while` SIGPIPE バグ**: feed の item 数 > `head -n` 上限時、head 早期クローズで grep が SIGPIPE(141) → pipefail で非ゼロ → set -e が中断。qiita (4件<5) だけ動き Zenn/HF (>5件) が黙って0件になる潜在バグ。`$(... | head) || true` + here-string `while <<<` で回避。
- **morning-briefing スクリプトの重複**: top-level `scripts/runtime/auto-morning-briefing.sh` (git 管理外・RSS なし・古い) と `.config/claude/scripts/runtime/auto-morning-briefing.sh` (アクティブ・feed あり) が分岐。**未対応 (本タスク範囲外)** — 別途棚卸し候補。
- **claude -p の "Execution error" / ハング**: `--tools ""`・`--max-budget-usd` 付与で即 "Execution error" (exit 0 のまま本文がエラー)。連続呼び出しで 10 分ハング→timeout も観測。本文先頭 "Execution error" 検出ガードを追加。

## Outcome
- Phase 1 read-only MVP 実装完了 (2026-06-04)。collect → claude 選別 → adoption-ledger → 30日集計 のパイプラインが DRY_RUN/合成テスト/pytest で機能実証済み。
- **2026-06-05 運用完了**: (1) launchd 登録済み (`com.user.nightly.tech-researcher`, 23:55) を確認、(2) **live claude -p 走行成功** (53s, 10/23採用, 差別化集計出力) — Success Criteria 全項目達成。
- **残作業**: (3) コードレビューゲート (claude/codex 回復後)。
- 30日 ledger 蓄積後に R1 判定 → Phase 2 へ。今日の初回 ledger (23行) が起点。
