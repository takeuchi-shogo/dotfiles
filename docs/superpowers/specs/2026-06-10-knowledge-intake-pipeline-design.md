---
status: design
---

# Design: Knowledge Intake Pipeline（記事インテイクの自動化と配線統合）

- **Created**: 2026-06-10
- **Scale**: L+（複数サブシステム。段階分割し、最初の増分 SP0 のみを本 design の実装対象とする）
- **Depends on**: ① nightly wake（PR #71, merged bb1d9fd）— Phase 2 の朝 push が利用
- **Related**: `docs/plans/active/2026-06-04-ai-tech-researcher-self-evolving-plan.md`（収集層）/ `docs/plans/active/2026-06-02-skillopt-objective-lane-optimization-plan.md`（eligibility classifier・rejected buffer）/ `docs/superpowers/specs/2026-05-31-learned-promotion-loop-design.md`（auto-triage/calibration gate）

## 1. Goal（北極星）

朝/夜の idle 時間に、**記事の徘徊（発見）・absorb のコピペ（統合の前処理）・作業待ち（同期実行の待ち）を機械的に自動化**し、人間は判断だけを高速ゲートで行う。同時に、これまで**配線が繋がっていない／活かしきれていない既存資産を整備して繋ぐ**。

「夜勤マシン化」(①) の自然な延長: 収集だけでなく、収集物の前処理・統合導線まで idle 時間で進める。

## 2. Grounded wiring state（現状の配線断 — 2026-06-10 監査）

| パイプライン | 状態 | 根拠 |
|---|---|---|
| tech-researcher → 下流 consumer | **完全断線**。report/ledger を消費するものは Discord status 通知以外ゼロ | grep（adoption-ledger/reports/09-TechTrends の参照）一致なし |
| /absorb・/digest の自動トリガー | **手動のみ** | runtime/launchd に自動起動なし（promote-patterns.py の言及のみ） |
| learned 昇格ループ | **ledger 空・非流通** | pattern/promote jsonl 不在。memory「promoted-ledger 空のまま」と一致 |
| `scripts/learner/` | **ほぼ空**（reviewer-calibration.py 1個） | 大半 decommission 済 |

要約: **収集層は動くが、統合・消費層が全断**。19個の自動ジョブが回るが出力同士が繋がっていない。

## 3. Critical constraint: /improve postmortem → 設計制約 C1–C5

「完全無人 absorb」を文字通り作ると、retire 済の `/improve`（false-positive 工場）を再建する。退役記録から故障モードを抽出し、各々に対策機構を割り当てる（postmortem-driven design）。

| # | 故障モード（出典） | 設計制約 | 機構（既存資産の再利用優先） |
|---|---|---|---|
| F1 | 対象ミスマッチ＝客観正解キーの無い判断タスクを最適化（skillopt分析:76「false-positive 死の根因」） | **C1: 入口で eligibility 分類**。mechanical（照合可能）だけ自動、judgment は人間ゲートへ | SkillOpt objective-lane の "optimizer eligibility classifier"（Gap#6, 設計済）を再配線 |
| F2 | A/B delta±2pp 自動 merge＝frozen judge/human anchor 無し→Goodhart（skillopt:41,49） | **C2: judgment は auto-merge 禁止**。人間ゲート＝anchor。機械スコアにも drift 検出 | auto-triage / calibration-verdict-logger をゲートに |
| F3 | 認知負荷で retire（improve-policy） | **C3: 低認知負荷**。top3–5・pre-digest・30秒判断。溢れたら保留、全dump禁止 | ② clickable・低ボリューム設計 |
| F4 | 下流孤児カスケード＝/improve 退役で 15MB 死蔵（decommission-log） | **C4: 単一ソース＋浅い consumer**。深い node 連鎖を作らない。各片が独立・観測可能 | ledger=単一ソース、consumer は直接読むだけ |
| F5 | 設計済み・未配線が貯まる（skillopt:77） | **C5: 繋いで使ってから次を作る**。未配線機構を貯めない | 各増分は CONNECTED かつ USED が完了条件 |

## 4. Architecture（北極星パイプライン）

```
DISCOVER ──→ PREP ───────────→ QUEUE ──[fast gate]──→ INTEGRATE ──→ LEARN
tech-       eligibility分類→     ②消費層    人間30秒        承認分のみ      承認/却下を
researcher  mechanicalのみ      (clickable  approve/        absorb/digest   source選別・
(既存)      draft生成           ・朝/端末)  reject/edit     実行→memory     prep品質へ
            (SP2: objective-                (auto-triage     更新           還元
            lane再利用)                      再利用)                       (calibration)
```

- **単一ソース = `~/.cache/tech-researcher/adoption-ledger.jsonl`**（url/title/domain/scores{novelty,reliability,concreteness}/date/adopted を保持。新DB不要）。
- **mechanical lane（無人）vs judgment lane（fast gate）** の分離が C1 の体現。
- 明示的スコープ外（YAGNI）: embedding / GraphRAG / Neo4j / queue→worker→DB。既存 ledger で全要件を満たす。

## 5. Decomposition（サブプロジェクト）

各 SP は独立の spec→plan→implement サイクル（C5: 1増分ずつ CONNECTED & USED）。

| SP | 内容 | 依存 | 本design の扱い |
|---|---|---|---|
| **SP0** | **② 消費層（QUEUE+GATE）**: ledger を clickable に surface | ①(済) | **本design の実装対象** |
| SP1 | 配線監査の統合: 死蔵/孤児/未配線の地図化と再接続計画 | — | roadmap（別 /rpi） |
| SP2 | PREP 自動化: 本文 fetch + eligibility 分類 + absorb 下書き生成 | SP0, SkillOpt plan | roadmap |
| SP3 | Fast gate: 朝トリアージ（auto-triage 再利用、approve/reject/edit） | SP0/SP2 | roadmap |
| SP4 | INTEGRATE: 承認分の absorb/digest 実行 | SP3 | roadmap |
| SP5 | LEARN: calibration を source選別・prep品質へ還元 | SP3, tech-researcher Phase3 | roadmap |

**SP0 先行の根拠（C4/C5）**: 消費する習慣（gate 面）を先に証明しないと、PREP 自動化(SP2) は次の死蔵になる。観測可能にするため人間入りで loop を先に回す。

## 6. SP0（②）詳細設計 — 最初の増分

### 6.1 共通コア: `trends-lib`（ランキング/描画の単一化, DRY）
- 入力: adoption-ledger.jsonl
- 処理: `adopted=true` を抽出 → url で dedup → score でソート（**1次: novelty+concreteness 降順 / tiebreak: reliability**）→ 直近 N 日窓
- 出力: 構造化リスト（title, url, domain, scores, date）。pull/push の両 consumer が共有。
- 配置案: `scripts/runtime/tech-researcher/lib/trends-select.py`（既存 tech-researcher 配下に co-locate）

### 6.2 Phase 1（①非依存・wake/sudo 不要・MVP）
1. **`task trends`（pull）**: ターミナルで直近 N 日の top adopted を `title — URL` + score badge で表示。クリック可能（Ghostty/iTerm の URL）。既読管理なし（直近 N 日表示=YAGNI）。
   - Taskfile target `trends:` → trends-select.py を人間可読フォーマットで出力。
2. **ターミナル初回起動 digest（push①）**: zsh `precmd`/`.zshrc` ガードで「その日初回の対話シェル」のみ当日 top M を自動表示。
   - 1日1回ガード: stamp `~/.cache/tech-researcher/digest-shown-YYYY-MM-DD`。
   - 高速・ネットワーク無し（ledger 読むだけ）。シェル起動を体感で遅くしない（< 数十 ms 目標、stamp ヒット時は即 return）。

### 6.3 Phase 2（①=#71 に依存・要 sudo 検証）
3. **朝の固定時刻 Discord push（push②）**: launchd ~8:00、前夜 top3 を `[title](URL)`（スマホでタップ可）の専用 embed で push。**ops status 通知と別フォーマット**＝editorial を ops ノイズから分離（痛み「埋没」を解消）。
   - 既存 `notify-discord.sh` は status 用。**別関数/別メッセージ**として実装（status 通知は変更しない）。
4. **朝 wake の確保**: `pmset repeat` は wake 1枠（①が夜22:15 で使用済）。→ 夜間バッチ完了時に**翌朝の one-time `pmset schedule wake` を再arm**。時刻は `nightly-wake.env` に `NIGHTLY_MORNING_WAKE_HH/MM` を追記（単一真実源を踏襲）。

### 6.4 既知リスク / Open question（Phase 2）
- **`pmset schedule` は sudo を要する可能性**。launchd user ジョブは無人 sudo 不可 → 再arm が成立しない懸念。
  - 緩和案（Phase 2 着手時に検証）: (a) passwordless sudoers を pmset に限定付与（セキュリティ tradeoff・要承認）/ (b) 朝 wake を諦め「ユーザーが朝 Mac を開いた時に launchd RunAtLoad で push」/ (c) Phase 1（端末初回起動）で十分なら Phase 2 を見送る。
  - **判断は Phase 2 着手時。Phase 1 は本リスクと無関係に完結する。**

## 7. Isolation / units / interfaces

| ユニット | 役割 | 依存 | テスト可能性 |
|---|---|---|---|
| `trends-select.py` | ledger→ランク済リスト（純関数的） | ledger ファイル | 固定 ledger fixture で決定論的にテスト可 |
| `task trends` | pull 表示 | trends-select.py | 出力フォーマットの snapshot |
| zsh first-open hook | push① トリガー | trends-select.py, stamp | stamp ガードの単体確認 |
| morning-push (Phase 2) | push② | trends-select.py, notify-discord webhook | DRY_RUN で webhook 抑制（既存 NIGHTLY_NOTIFY_DISABLE 流用） |

各ユニットは ledger を直接読むだけで相互依存が浅い（C4）。1つ壊れても他は機能する。

## 8. Testing
- `trends-select.py`: 固定 ledger fixture（adopted 混在・dup url・score 同点）で順序/dedup/窓を検証。
- `task trends`: 出力に URL が含まれ score 順であることを確認。
- first-open hook: stamp 有/無で 1日1回発火を確認。シェル起動オーバーヘッド計測。
- morning-push: DRY_RUN で payload 構造（clickable `[title](url)`）を検証、実 webhook は叩かない。

## 9. Risks & reversibility（撤退条件）
- **死蔵化リスク（最大）**: ② を作っても読まなければ次の死蔵。→ **撤退条件**: Phase 1 稼働 2 週間で `task trends`/digest を一度も使わなければ、push② を作らず Phase 1 を縮退 or 撤去（C5 の自己適用）。
- **可逆性**: 全て追加（既存 tech-researcher / notify-discord / nightly-wake.env を破壊しない）。Taskfile target・zsh hook・launchd は個別に外せる。
- **C1–C5 違反の自己監査**: SP2 以降で「judgment を auto-merge していないか」「未配線機構を貯めていないか」を各 plan の完了条件に含める。

## 10. 確定事項 / 先送り
- **確定**: 単一ソース=ledger / mechanical-auto + judgment-gate / ②先行 / embedding等スコープ外 / Phase 1 が MVP。
- **先送り（Phase 2 着手時）**: pmset schedule の sudo 可否、朝 push の最終トリガー方式、N/M の具体値。
- **先送り（SP1+）**: 配線監査の統合スコープ、SkillOpt objective-lane の再配線範囲。
