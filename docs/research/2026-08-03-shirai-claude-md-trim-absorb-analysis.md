---
title: "CLAUDE.md と AGENTS.md を削ったら、AI コーディングがグンと賢くなった (absorb 分析)"
date: 2026-08-03
source_url: https://note.com/o_ob/n/nd19cba8e11d7
source_author: 白井暁彦 (note, 2026-07-30)
source_type: blog-post
source_retrieval: "note.com は trusted 外のため defuddle CLI で full markdown 取得 (28187 bytes)。WebFetch は Haiku 要約が挟まるため C1 オーバーライドで不使用"
family: context-file クラスタ (N=8)
saturation: "PASS (warning) — N>=3 だが採用率 50% 超で閾値クリア。Step 7 stale-plan audit は直近 3 件が implemented×2 / plan-created (3日前) で全て skip"
phase_2_5: "Codex only (Gemini は IneligibleTierError で sunset)"
status: implemented
scale: S×3 + M×1 (M はプランのみ)
adopted_tasks:
  - "V1: reader ゼロの negative-knowledge.md を writer 2 本ごと撤去"
  - "T3: project CLAUDE.md から global と重複する一般則を除去"
  - "T4: japanese-ai-prose.md に「リンクの示し方」を追加"
  - "T5: doctor:context プラン作成 (実装は別途)"
type: absorb-analysis
---

# CLAUDE.md と AGENTS.md を削ったら、AI コーディングがグンと賢くなった (absorb 分析)

## Source (記事の要点)

主張: CLAUDE.md / AGENTS.md を短くするのが目的ではなく「必要な情報を、必要な場所に、必要なタイミングで読み込ませる構造」へ変える。長く使い込まれた指示書は禁止事項とトラウマの塊になり、重要な指示が埋もれる。

根拠: 著者個人の実践 (AICU Japan の複数リポジトリ運用)。定量データなし。

前提: 複数リポジトリ・チーム運用・GitHub Issue で責任者に依頼できる体制。

抽出した手法 13 件 (M1-M13):

- M1 静的指示書に「現在地」(進捗・完了ToDo・引き継ぎ) を書かない。進捗は Issue、引き継ぎは handoff、作業ログは日付つきファイルへ
- M2 グローバル CLAUDE.md には全プロジェクト共通ルールのみ。プロジェクト固有は各リポジトリへ移し、グローバルには参照の一文だけ残す
- M3 残すのは「踏むと壊れる罠」。判断基準は「この文章がなくても AI はコードやテストから正しい結論へ到達できるか」
- M4 長い仕様は別ドキュメントへ分離し、参照先と「いつ読むか」だけを書く (progressive disclosure)
- M5 作業ログに混ざった設計思想を蒸留し、一時的進捗は削除して原則だけを一文で移す
- M6 「やらないこと」は禁止だけでなく理由 + 代替手段を一文で書く
- M7 禁止のネガティブ表現をポジティブ表現に置き換える。ネガ過多は agent の「体感インテリジェンス」を下げ近視眼的な例外実装を誘発する
- M8 未使用の skill / plugin を「インストール時の期待」でなく「実際の利用履歴」で無効化する (削除でなくオフ + バックアップ)
- M9 削減は可逆に。一度に全部消さず、変更後に実タスクで挙動を観察する
- M10 成果指標を行数・ファイルサイズにしない。見るべきは「重要な制約へ到達しやすくなったか」
- M11 `/doctor` で棚卸しを始める
- M12 Issue を日付入りメモリにしてセッション断絶 (トークン切れ・Rate Limit・再起動) の穴を防ぐ
- M13 Issue/PR/報告の URL は相対でなく完全形。「次に人間が開く場所」を毎回フル URL で示す

## Phase 1.5 Saturation Gate

family = context-file クラスタ。既存 7 件 (agents-md 系 ×3 / 12-rule-claude-md / 2026-07-25 anthropic-context-engineering / 2026-07-31 handbook-md / 2026-07-31 boris-cherny-ablation / 2026-08-02 context-files-ablation) に対し本記事が 8 件目。採用率 50% 超のため PASS (warning)、delta 計算は不要。

Step 7 stale-plan audit: 直近 3 件は boris=implemented / context-files-ablation=implemented / handbook=plan-created (3 日前、30 日猶予内) で全件 audit skip。

## Phase 2 + 2.5 判定表

Pass 1 は Sonnet Explore に委譲、Pass 2 は Opus、Phase 2.5 は Codex (gpt-5.6-terra, xhigh)。

| # | 手法 | Pass 2 | Codex 後 | 根拠 |
|---|------|--------|----------|------|
| M1 | 進捗を静的指示書に書かない | Already | Already | `PLANS.md` の Plan Retirement + `references/resume-anchor-contract.md` の Plan / HANDOFF.md / RUNNING_BRIEF.md 3層分離 + `/checkpoint` |
| M2 | global は共通ルールのみ | Already | **Partial に降格** | project CLAUDE.md の「Think before coding」「Sanity check」「最小変更」が global の `<core_principles>` と重複。global 自身の「指示の重複を作らない (instruction DRY)」に抵触 |
| M3 | 残すのは踏むと壊れる罠 | Already (強化可能) | **Partial に降格** | `CLAUDE.md:28`「Static-checkable rules は mechanism に寄せる」は存在するが、罠ストア本体の `references/negative-knowledge.md` が機能不全 (下記 V1) |
| M4 | progressive disclosure | Already | **Partial に降格** | `<important if>` 7 ブロックは遅延ロードではなく注意ルーティング。global CLAUDE.md 122 行は毎セッション全文ロードされ、タグを解釈して除去する処理は harness 内に存在しない。分離自体 (references/ 165 ファイル) は達成済 |
| M5 | 作業ログから原則を蒸留 | Already | Already (根拠差し替え) | Pass 1 が挙げた `improve-policy.md` は `status: deprecated` (2026-05-03)。現行の実配線は patterns.jsonl → `/promote-learnings` → promoted-ledger.jsonl |
| M6 | 禁止 + 理由 + 代替 | Already (強化可能) | Already (強化可能) | `rules/common/core-invariants.md` 5 件中 3 件に代替あり。Codex: 「必ず一文で代替」は不要で、安全不変条件は明示禁止のまま hook で強制するのが正しい |
| M7 | 禁止をポジティブ表現に | N/A | **検証仮説 (保留)** | 否定指示の性能低下には先行研究がある (Jang et al. arXiv:2209.12711 ほか) が、記事の「体感インテリジェンス低下」までは立証されない。こちらが出した「global CLAUDE.md の『禁止』は 122 行中 3 件」という密度カウントも指標として不十分と指摘された。ユーザー判断で保留 |
| M8 | 利用履歴で skill 無効化 | Already | Already | `settings.json` の `skillOverrides` 48 件 + `scripts/policy/skill-tracker.py` + `skillListingBudgetFraction` |
| M9 | 可逆削減 + 実タスク確認 | Already | Already | `references/dead-weight-scan-protocol.md` (固定 task set / baseline vs minimal / 1サイクル最大5項目) + `harness-stability.md` の 30 日評価 |
| M10 | 行数を指標にしない | Already | Already (方針のみ) | dead-weight-scan-protocol の測定軸は再指示回数 / 誤った安全判断 / トークンで行数を使っていない。ただし baseline と minimal を実測した比較ログが 1 件も残っていない |
| M11 | `/doctor` で棚卸し | Partial | Partial | `task doctor` と `/check-health` はある。足りないのは常時ロード量の一枚可視化 |
| M12 | Issue を日付メモリに | Partial | Partial (価値低) | `references/failure-escalation-protocol.md` は harness/tool 失敗時に限定され rate limit は明示的に対象外。Plan / HANDOFF / RUNNING_BRIEF / Decision Journal が強い代替。Codex: 「単独運用だから不要」は理由として弱く、未計画の後回し作業だけを Issue 化する狭い運用なら成立する |
| M13 | 報告はフル URL | Gap | **Partial に降格** | `skills/create-issue/SKILL.md:135` と `commands/pull-request.md:97` に URL 表示の規定が既にある。Codex: 「常にフル URL」ではなく用途を限定すべきで、secrets 設定画面 URL の常時出力は情報露出にあたる |

**記事由来の新規 instruction は 0 件。** 8 件目の飽和 family として想定どおり。

## Phase 2.5 で Codex が覆した点

1. **M4 が最大の見落とし** — `<important if>` を progressive disclosure と数えていたが、条件ブロック自体は毎回ロードされる。「注意を向けさせるルーティング」と「必要時だけ読み込ませる構造」は別物
2. **Pass 1 が休眠 artifact を根拠にした** — `improve-policy.md` は 2026-05-03 に deprecated。memory `feedback_dormant_artifact_edits.md` が警告していた失敗パターンの再発
3. **M13 は Gap ではなく Partial** — 既存規定を見落としたうえ、secrets 画面 URL の常時出力という情報露出リスクを見落としていた
4. **M7 の N/A は根拠不足** — 否定指示の劣化には先行研究があり、「N/A で閉じる」には自分の密度カウントが弱すぎた

## Validation-only follow-up — `negative-knowledge.md` の死蔵

記事の「実際の利用履歴を見る」「絆創膏だらけ」という framing で照らして見つかった、記事とは無関係の実バグ。

- reader が skills / commands / agents のどこにも存在しない (grep 0 件)
- `commands/improve.md:14` が「セッションデータの自動学習・履歴蓄積 (autoevolve 系 producer の責務、本コマンドからは参照しない)」と明示的に除外している
- 唯一の設計文書 `references/improve-policy.md` は `status: deprecated` (2026-05-03)
- 中身は 207 行中 200 行が `tmpa_dkp8ap` 等のテスト用一時ディレクトリ名。Reason 列は全行空欄、実プロジェクトの記録はゼロ
- 原因: writer (`scripts/learner/session-learner.py:220`) が `AUTOEVOLVE_DATA_DIR` を無視して canonical パスにハードコード書き込みするためテストが隔離されない。さらに 200 行ローテートが実データを全て evict していた
- 2026-07-31 の Boris Cherny absorb (該当レポート「副次の観測 (未対応、要判断)」節) が「テスト分離の欠陥」として flag 済だが未修正で、その後さらに約 200 行増えた

書き手を直しても読み手がいないため、修正ではなく撤去を選んだ。

## 実施した変更

### V1: negative-knowledge の撤去 (S)

- `.config/claude/references/negative-knowledge.md` 削除
- `scripts/learner/session-learner.py` の `_extract_negative_patterns` (81 行) と呼び出しを削除
- `scripts/runtime/error-rate-monitor.py` の `append_to_negative_knowledge` (43 行) と呼び出しを削除
- `references/observability-signals.md` の 3 行を実態に合わせて修正
- `docs/decommission-log.md` に退役記録を追記
- `error-rate-monitor.py` の stderr `[ERROR_RATE_SPIKE]` 警告 (人間が読む唯一の消費経路) は存置

### T3: project CLAUDE.md の重複除去 (S)

「Think before coding」「Sanity check」を「Scope discipline」1 節に統合。global の `<core_principles>` および `<important if implement>` と重複する 5 行を削除し、global にない具体 (スコープ提案の分離 / 200 行 → 50 行の閾値) だけを残した。「Editing rules」の「Don't refactor things that aren't broken」も global の最小インパクトと同義のため削除。

### T4: リンクの示し方 (S)

`references/japanese-ai-prose.md` に「リンクの示し方」節を追加し、`templates/claude-md/rules.md` の prose ブロックに 1 行のポインタを足して global CLAUDE.md を再生成した。

Codex の指摘に従い「常にフル URL」ではなく 3 場面 (外部状態を変えた後 / handoff / 障害報告) に限定。対象別に、リポジトリ内コードは `path:line`、外部共有は commit 固定 permalink、PR/Issue と CI はフル URL と使い分ける。secrets 設定画面の URL は書かない。

新規ファイルを作らず既存 reference に足したのは、この reference を読み込む `<important if>` ブロックの発火条件 (PR description / Issue body / memo / commit body / doc) が対象場面とそのまま一致するため。

### T5: プランのみ (M)

`docs/plans/active/2026-08-03-doctor-context-inventory-plan.md` を作成。実装は別途。

## 見送り

- **M7 (禁止表現の極性)** — 検証仮説として保留。ablation を回すなら安全不変条件を除外し、同一タスク群で「明示禁止」と「行動＋代替」を比較する。直前の absorb (2026-08-02 context-files-ablation) が「差がないと言うには検出力がいる」を結論しており、文体極性の A/B は費用対効果が悪い
- **M12 (Issue を日付メモリに)** — 代替が強く、狭い運用に絞っても得るものが少ない
- **M6 の「必ず一文で代替を書く」** — Codex の指摘どおり、安全不変条件は明示禁止のまま hook で強制するのが正しい

## 教訓

- **飽和 family でも副産物で元が取れる。** 記事由来の新規 instruction は 0 件だったが、「実際の利用履歴を見る」という framing で reader ゼロの store が 1 件出た。これは Boris Cherny absorb (2026-07-31) の「absorb は本体の採用より副産物のバグ検出で元が取れることがある」の 2 例目
- **既知の flag は放置すると悪化する。** `negative-knowledge.md` のテスト汚染は 3 日前の absorb が指摘済だったが「scope 外」として送られ、その間に 200 行増えてローテートが実データを追い出した。副次観測を Issue 化しないと次の absorb まで動かない
- **「分離してある」と「遅延ロードされる」は別物。** `<important if>` を progressive disclosure と数えたのは過大評価だった。条件タグは読み手 (モデル) への合図であって、ロード機構ではない
- **Pass 1 の根拠は deprecated frontmatter を必ず確認する。** memory `feedback_dormant_artifact_edits.md` が既に警告していたのに再発した

## Phase 2.5 の実行記録

1 回目の `codex exec` は exit 124 で終了した。stderr が出力したのは `Reading additional input from stdin...` のみで、stdin を閉じずに起動した呼び出し側のミス。`< /dev/null` を足して再実行し exit=0 で批評を取得した。Codex 側の no-progress ではない。

Gemini は `IneligibleTierError` で sunset のため Phase 2.5 は Codex 単独。Google 系モデルの批評は取得していない。
