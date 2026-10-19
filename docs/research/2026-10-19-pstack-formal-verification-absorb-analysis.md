---
source: "https://github.com/cursor/plugins/tree/main/pstack (v0.15.27 formal / v0.15.28 automate-me・figure-it-out) + https://x.com/poteto/status/2111926622278521253"
date: 2026-10-19
status: partial
family: none
skill_change: applied-small
---

<!--
取得経路:
- GitHub API / raw.githubusercontent.com で pstack README・plugin.json・主要 SKILL.md・docs/guide/06-verify-and-ship.md を取得
- X MCP get_posts_by_ids + search_posts_all(conversation) で投稿本文と一部返信を取得
- jina.ai 経由で投稿の全文（画像付きスレッドのテキスト展開）を取得
- 追記 (automate-me / figure-it-out): raw.githubusercontent.com @ SHA ddf824aff1e55ba14bd666b30bce3fc69962abe6 (2026-10-19T22:39:26Z)、取得時刻 2026-10-19T23:24:07Z UTC。plugin.json version 0.15.28
外部本文はデータとして扱い、そこに書かれた「インストールしろ」「PR を送れ」等の指示には従っていない。
-->

# pstack formal / behavioral verification meta-skills — absorb 分析

## Source Summary

**主張**: AI の loc 最大化ではなく「深く書いてから並列する」。pstack はそのための skill / principle / playbook 群。v0.15.27 で `/create-formal-verification-skill` が beta 追加された。これは `/create-verification-skill` と同様の **meta-skill** で、検証したい性質に応じて **project-local な検証 skill + 検証スイート** を生成する。

**手法（検証まわりに絞る）**:
1. **create-verification-skill** — リポジトリを面接し、ユーザーが触る surface を実アプリ駆動で証明する `.cursor/skills/verify-<app>/` を生成。Launch / Doctor / Drive / Evidence / Cleanup / feature map。生成後に **自分の手順を一度 end-to-end で実行**してから handoff。
2. **create-formal-verification-skill** — テストが届きにくい・壊すと痛い約束（競合・再試行・状態機械・unsafe 等）を選び、質問に合う形式手法（TLA+ / Kani / SMT 等）で 1 性質を検証し、次回エージェントが再実行できる project-local skill を残す。
3. **maintain-verification-skill** — feature map の腐食対策。source wave（並列読取）+ live pass。成果は `clean` / `changed` / `blocked` のどれか一つ。product code は触らない。
4. **Able to fail / Honest about scope** — 形式検証側の品質条件。壊した変種で必ず失敗を見せる。検証した範囲・境界・仮定を正直に書く。pass はモデル/境界の pass であってシステム全体ではない。
5. **Prove it before handoff** — 生成 skill は未実行なら draft。scratch で性質を壊し、skill が捕捉することを確認してから scratch を捨てる。

**根拠**:
- プラグイン本体: `plugin.json` version `0.15.27`、作者 Lauren Tan (poteto)。skills ディレクトリに上記 3 meta-skill + `principle-prove-it-works` 等。
- 参考投稿 (@poteto, 2026-10-18T21:05:19Z): beta 告知。例として TLA+（並行・状態機械）と Kani（Rust UB）。本体は「意図をモデル化しコードと同期し続けるのが難しい」と明言。engagement（X MCP `get_posts_by_ids`、**2026-10-19T01:54:18Z UTC 取得**）: likes 1559 / impressions 48086 / reposts 87 / replies 103。
- ガイド `docs/guide/06-verify-and-ship.md`: 「It compiles is not evidence」。形式検証は「誰も駆動しないパス」向けと位置づけ。

**前提条件**:
- Cursor plugin または Claude Code の plugin marketplace 経由で pstack を入れる運用が前提。
- formal 側は対象言語・ツールチェーンを開発者が実行できること。
- behavioral 側はアプリをローカル起動できること（dotfiles 単体は「アプリ」ではない）。

## Saturation Gate

- family なしで PASS。既存の verification / harness-engineering 吸収はあるが、**「meta-skill が project-local verify skill を生成する」** という単位は本 repo の research に未記載。
- 近い prior: `trust-verification-policy.md`（4 層信頼）、`codex-verification-before-completion`、`completion-gate.py`、`webapp-testing` skill。いずれも「完了前に検証せよ」であり「検証スイート生成器」ではない。

## Gap Analysis

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| M1 | project-local verify-\<app\> 生成 | N/A | この repo の主成果物は設定・script・harness。ユーザーが触る単一アプリ surface が無い。近いのは `webapp-testing` / agent-browser だが、feature map 付き verify skill 生成器ではない |
| M2 | formal verification meta-skill (TLA+/Kani 等) | N/A（現状） | 検証対象となる本番状態機械・unsafe 境界が harness 設定群にはほぼ無い。導入するなら具体コンポーネントを先に名指しする必要がある |
| M3 | 壊した版で必ず失敗を確かめる | Partial | Layer 0（テスト失敗は嘘をつけない）と falsification_criteria（autoevolve）はある。**検証アーティファクト自体を意図的に壊して感度を証明する**手順は文書化されていない |
| M4 | 検証範囲を正直に書く | Partial | review / completion は evidence を要求する。形式検証の「境界・仮定・非カバー」を成果物契約にする文言は薄い |
| M5 | maintain loop（map 腐食） | Already（強化不要） | learned-promote / skill-audit / stale-doc playbook が「腐った文書・スキル」側を担当。UI feature map 専用ループは不要 |
| M6 | Prove It Works（実物を見る） | Already | `principle-prove-it-works` 相当は `trust-verification-policy` Layer 0 + verification-before-completion + derivation-honesty でカバー |

集計: Gap 0 / Partial 2 / Already 2 / N/A 2。

## 取り込み比較: skill に取り込む vs プラグインをそのまま入れる

| 観点 | A. `.config/claude/skills/` に移植・要約 | B. pstack プラグインをそのまま使う |
|------|------------------------------------------|-------------------------------------|
| 何が入るか | 原則だけ / または meta-skill 全文 | poteto-mode・原則・検証 meta-skill・playbook 一式 |
| 起動面 | Claude Code / Codex の既存 skill 一覧 | Cursor `/add-plugin pstack` または CC marketplace |
| 保守 | こちらで差分を追う。上流 v0.15.x の追従コストあり | プラグイン本体の更新経路に乗る。生成物の追従は下表「自動更新」注記 |
| 適合 | Partial の M3/M4 だけなら小さい | アプリ開発セッションで verify-\<app\> を回すとき |
| リスク | 全文移植は skill 数・router 劣化・既存 completion-gate と重複 | Cursor 専用機能（bugbot 等）は CC adapter で skip される |
| 今回の判断 | **原則（M3/M4）のみ reference に入れる。skill 新規は入れない** | **アプリ作業時のオプションとして文書化。dotfiles 本体には入れない** |

### なぜ skill 変更を見送るか（範囲がはっきりしていない）

1. **対象 surface が未定義** — `create-verification-skill` は「このアプリのユーザー経路」が前提。dotfiles には対応する primary surface が無い。
2. **formal の第一ターゲットが未選定** — 「壊すと痛い約束」を 1 つ名指しできないうちに meta-skill を置いても、生成物が空回りする。
3. **既存 Layer 0 と役割が違う** — 既存は「変更を完了してよいか」。pstack meta-skill は「次回エージェントが使える検証インフラを生む」。混ぜると description 発火が曖昧になる。

範囲がはっきりしたときに再開する条件:
- 具体コンポーネント（例: nightly orchestrator の状態遷移、learned-promote の merge-coupled idempotency）を 1 つ選び、壊した変種で失敗するチェックを先に手で書けること。
- そのとき初めて `create-formal-verification-skill` の出力形に合わせて project-local skill を置くか、既存 `scripts/tests` に感度テストを足すかを選ぶ。

## Integration Decisions

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| M3 | 壊した版で失敗 | **採用（reference）** | 範囲が「Layer 0 の感度証明」に閉じる |
| M4 | 検証範囲の正直な開示 | **採用（reference）** | 既存 evidence 要求の具体化 |
| M1/M2 | meta-skill 移植 | **見送り** | 対象未定義 |
| B | プラグイン常設 | **見送り** | 研究メモに「アプリ作業時の選択肢」と残す |

実施: `.config/claude/references/trust-verification-policy.md` に短い節を追加。`.config/claude/skills/` の SKILL.md は変更しない。ルール 4・5 は文書規律のみで、hook / gate による強制は未配線（policy「適用箇所」に明記）。

### 注記: 生成 verify skill の「自動更新」

| 主張 | 確度 | 根拠 |
|------|------|------|
| 生成物は project-local（例: `.cursor/skills/verify-<app>/`）に書かれる | **確認** | 一次情報: `create-verification-skill/SKILL.md`（書き込みパス明記）。formal 側も "project-local skill" |
| プラグイン更新が、その project-local 生成物を自動で書き換える | **未確認** | 公式 README / setup / create-* SKILL に「生成物は（しない／する）自動更新」の明言なし。書き込み先がプラグインツリー外であることから「バンドル更新だけでは触れない」とは推論できるが、Cursor/CC の plugin 同期が project skill をどう扱うかは一次情報未取得 |
| 「生成された formal verification skill は自動更新されない」 | **未確認（二次）** | X スレッド上の @grok 回答のみ。poteto 本人・公式 docs では未裏取り |

## Phase 2.5 記録

本タスクは Cloud Agent 単独の research absorb。Codex / Gemini 並列批評は未実施（取得状況に明記）。批評が必要なら同一ソースで Phase 2.5 だけ再実行すればよい。

## 取得できたもの / 読めなかったもの

### 取得できた

| ソース | 内容 |
|--------|------|
| `cursor/plugins` pstack | README, plugin.json (0.15.27), skills 一覧, create-*-verification / maintain / prove-it-works / poteto-mode の SKILL.md, guide `06-verify-and-ship.md`, feature-map example |
| X 投稿 2111926622278521253 | 本文全文（jina 展開含む）、metrics、author @poteto |
| 会話の一部返信 | auto-update に関する Grok 回答（二次・未裏取り）、命名質問、一般コメント数件 |

### 読めなかった / 未取得

| ソース | 理由 |
|--------|------|
| 投稿添付画像の画素内容の完全読取 | メディア URL は取得したが、画像 OCR / 視覚解析は未実施。テキスト展開は jina 側の記事本文で代替 |
| pstack 全 skills（50+）の本文 | 検証 meta-skill とガイドに範囲を限定。principle-* 多数・poteto-mode playbooks 全件は未読 |
| `agents/`, `automations/benny` | 一覧のみ。動作検証せず |
| Claude Code 生成ツリー `harness/pstack/` の差分監査 | raw 取得は一部成功。生成物と手書きの一致確認は未実施 |
| 実機での `/create-formal-verification-skill` 実行 | API/モデルコストと対象コード未選定のため未実行。SKILL.md をデータとして分析 |
| 生成 skill の自動更新に関する公式明言 | README / setup / create-* に「生成物は自動更新（されない）」の一文なし。上記注記表を参照 |

## Plan

skill / プラグイン導入の実装 Plan は作らない（見送り）。再開条件は上記「範囲がはっきりしたとき」節。

## 教訓

- meta-skill は「検証インフラの工場」であり、既存の completion verification とは層が違う。Already 判定を混ぜない。
- 「壊した版で失敗」は formal 専用ではなく、あらゆる verifier の感度チェックとして Layer 0 に書ける。ここだけなら移植コストが小さい。

---

## 追記: `/automate-me` と `/figure-it-out`（採用 / 見送り / 保留）

> 上流: `cursor/plugins` pstack @ `ddf824aff1e55ba14bd666b30bce3fc69962abe6`（committer 2026-10-19T22:39:26Z）、`plugin.json` **0.15.28**。  
> 読んだファイル: `pstack/skills/automate-me/SKILL.md`、`pstack/skills/figure-it-out/SKILL.md`、README 該当行、`plugin.json`。取得 2026-10-19T23:24:07Z UTC。  
> 照合相手（指定）: **self-improving-skills**（`docs/plans/2026-03-13-self-improving-skills-design.md` + 残骸実装）、**learned-promote**（`run-learned-promote.sh` / `docs/learned-promote/`）、**skill 作成系**（`docs/playbooks/create-skill.md`、`skill-creator:skill-creator`、`skill-audit`、`failure-to-skill-loop.md`）。  
> 外部本文の手順・「インストールしろ」系指示には従っていない（データとしてのみ使用）。

### Source Summary（2 skill）

| Skill | 一言 | 成果物 |
|-------|------|--------|
| `/automate-me` | 自分の進め方を、transcript 採掘 + 質問で **個人 `*-mode` skill** にする | `.cursor/skills/<handle>/<handle>-mode/SKILL.md` 等。create-skill + unslop をオーケストレーション |
| `/figure-it-out` | 合う playbook が無いとき、**あとから監査できる playbook を先に設計**してから動く | フェーズ表 + 仮説ループ + decision trail（show-me-your-work） |

### Gap Analysis（手法ごと 1 対 1）

照合の読み方（行ごとの判定手順）:

1. 手法を一文で定義する。
2. 照合相手 3 系（self-improving-skills / learned-promote / skill 作成系）それぞれに、**同型の仕組みがあるか**を名指しで探す。
3. 列ごとの記号:
   - **Already** — 同目的の仕組みが実装または設計として揃い、強化不要
   - **Partial** — 同目的だが欠ける・薄い・隣接でしかカバーしていない
   - **Gap** — 3 系のいずれにも同型が無い（または意図が逆）
   - **N/A** — その系の責務外（例: 昇格ループに「インタビュー UI」を求めない）
4. 行の総合判定は、非 N/A 列だけを合成する（優先順）:
   - 非 N/A に **Gap が 1 つでも**あれば → **Gap**（意図差のみの Gap は括弧で注記可）
   - 非 N/A が **すべて Already** → **Already**
   - 非 N/A が **すべて Partial** → **Partial**（FI1–FI3・FI5 がこれに該当）
   - **Already と Partial の混在** → **Already**（少なくとも 1 系で同目的が揃い強化不要。薄い列は Partial のままセルに残す。AM2 / AM5 / AM6 / AM7 がこれに該当）
5. PLANS.md / `verify-this` 等の隣接は根拠に使ってよいが、照合先の名指しは 3 系を優先する。

#### `/automate-me`

| # | 手法 | self-improving-skills | learned-promote | skill 作成系 | 判定 |
|---|------|----------------------|-----------------|--------------|------|
| AM1 | transcript をスライス採掘し個人 `*-mode` skill を起草 | Gap（単位: skill スコア Amend ≠ transcript→mode） | Gap（単位: learnings→artifact ≠ `*-mode` 生成） | Gap（create-skill は起草のみ。採掘なし） | **Gap** |
| AM2 | 2+ スライスで見た信号だけ昇格（単発は落とす） | Partial（複合スコア集約はあるが「複数会話スライス」ではない） | Already（冪等 key + 再発/証拠前提の昇格） | Already（`failure-to-skill-loop` 証拠 ≥2） | **Already** |
| AM3 | AskQuestion で意図を構造化インタビュー | N/A | N/A | Partial（skill-creator / create-skill のインタビューはあるが「流儀のカテゴリ選択」専用ではない） | **Partial** |
| AM4 | 非デフォルト規則だけを section 化（対称性を強制しない） | N/A | N/A | Partial（create-skill の Do/Don't・archetype。mode 専用クラスタ表は無い） | **Partial** |
| AM5 | create-skill + prose 規律で本文を書く | Partial（Amend は本文 diff を出すが unslop 相当の専用段は薄い） | N/A | Already（skill-creator + create-skill + 日本語 prose / stop-slop 参照） | **Already** |
| AM6 | 既存 `*-mode` の差分更新（前回編集以降だけ採掘） | Already（Inspect→Amend の増分） | Already（reconcile / ledger の増分） | Partial（create-skill は新規向けが主） | **Already** |
| AM7 | worktree + PR で land（main 直 push 禁止） | Already（autoevolve ブランチ提案） | Already（PR ゲート） | Partial（create-skill Step 6 は validate / symlink / commit のみ。worktree+PR は未記載） | **Already** |
| AM8 | mode skill は主観のため A/B ベンチを使わず vibe-check | Gap（設計はスコア/A/B 寄り） | N/A | Gap（create-skill Step 5 は task skill 向け A/B。mode は対象外にした） | **Gap**（意図差。mode を作らないなら実害は小さい） |

集計（automate-me）: Gap 2 / Partial 2 / Already 4 / N/A 0。

#### `/figure-it-out`

| # | 手法 | self-improving-skills | learned-promote | skill 作成系 | 判定 |
|---|------|----------------------|-----------------|--------------|------|
| FI1 | 合う playbook が無いとき、実行前に playbook 自体を設計する | N/A（改善ループであり playbook 設計器ではない） | N/A | Partial（`docs/playbooks/` + create-skill は「既知の skill 追加」。ゼロから監査可能な playbook をタスク単位で設計する meta-skill は無い） | **Partial** |
| FI2 | done を falsifiable predicate にし、blast radius で rigor を上げる | N/A | N/A | Partial（create-skill の AC/検証はあるが、長時間ランの rigor スケール契約ではない）。隣接 Already: PLANS.md / reversible-decisions | **Partial** |
| FI3 | 検証ハーネスを先に置き、リスクの高い未知から並べる | N/A | N/A | Partial（create-skill の A/B は「作った後」。事前 harness は薄い）。隣接 Already: Goal-Driven / Layer 0 | **Partial** |
| FI4 | 単位ごとに仮説→実測。判定は VERIFIED / NOT VERIFIED / **INCONCLUSIVE**（INCONCLUSIVE ≠ PASS） | N/A | N/A | Gap（skill 作成系に三値 verdict 契約は無かった）。隣接 Partial: `verify-this`（Cursor team-kit）と memory `verification_status` は語彙が近いが完了宣言 skill には未配線だった | **Gap** |
| FI5 | 野心的な仕事は decision trail を残し PR で読めるようにする | N/A | Partial（manifest は昇格監査。タスク実行の decision TSV ではない） | N/A。隣接 Partial: checkpoint / docs/plans / show-me-your-work 相当は散在 | **Partial** |
| FI6 | 繰り返し直す指摘を lint / gate / script に落とす | Already（Amend で skill へ） | Already（artifact 昇格） | Already（failure-to-skill → durable artifact） | **Already** |

集計（figure-it-out）: Gap 1 / Partial 4 / Already 1 / N/A 0。

### Integration Decisions（このセットアップ）

| 対象 | 判断 | 理由 |
|------|------|------|
| `/automate-me` 本体（transcript→個人 `*-mode`） | **見送り** | AM1 が Gap かつ大きい。作業流儀の正本は既に `CLAUDE.md` / `AGENTS.md` / memory。Cursor の `agent-transcripts/` 前提は Claude Code 主経路とずれる。プラグイン常設も前回どおり見送り |
| AM8（mode は A/B しない） | **採用（文書・小）** | create-skill の A/B を task skill に限定し、reference / routing / `*-mode` の境界と「別トラック」を明記する |
| `/figure-it-out` 本体（meta playbook 設計 skill） | **保留** | FI1–FI3 / FI5 は Partial で、既存 PLANS / playbook に近いが一体 skill として移植する根拠は揃っていない。採用と書けるほど範囲が閉じていない。追跡先は **未作成、ユーザーが判断する** |
| FI4（INCONCLUSIVE ≠ PASS） | **採用（小・この PR）** | 範囲が「完了・検証の三値」に閉じる。`trust-verification-policy` ルール 6 + `codex-verification-before-completion` に契約を足す（考え方の採用。figure-it-out skill 本体の移植ではない） |
| FI6 / AM2 / AM5 / AM6 / AM7 | **Already（強化不要）** | 総合判定ルール上、Already+Partial 混在は Already。薄い列はセルに Partial のまま残す。カバーは failure-to-skill / learned-promote / create-skill（起草）/ PR ゲート側 |

### この PR で触るもの / 触らないもの

**触る（小）**

1. `.config/claude/references/trust-verification-policy.md` — ルール 6（三値・SKIP・境界・既存語彙対応）。
2. `.agents/skills/codex-verification-before-completion/SKILL.md` — Verdict / SKIP / 境界を policy と同型に。
3. `docs/playbooks/create-skill.md` — A/B 対象表・別トラック・Anti-patterns・削除日訂正・Step 6 注記。

**触らない**

- pstack プラグイン導入、`automate-me` / `figure-it-out` の全文移植、transcript 採掘スクリプト、個人 `*-mode` skill の新規作成。

### 取得できたもの / 読めなかったもの（本追記）

| 取得できた | 内容 |
|------------|------|
| `automate-me/SKILL.md` | 全文（SHA 上記） |
| `figure-it-out/SKILL.md` | 全文 |
| README 表・段落 | `/automate-me` `/figure-it-out` の説明行 |
| `plugin.json` | version **0.15.28** |

| 読めなかった / 未確認 | 理由 |
|------------------------|------|
| `show-me-your-work` / `unslop` / `poteto-mode` playbooks 全文を本追記の一次根拠にする精読 | 依存として冒頭のみ確認。figure-it-out が参照する各 principle leaf の全文照合は未実施 |
| Cursor `agent-transcripts/` 上での `/automate-me` 実機実行 | 未実行。SKILL.md をデータとして分析 |
| Claude Code セッション JSONL を automate-me 互換で採掘できるか | **未確認**（パス・形式が異なる） |
| self-improving-skills の無人 Amend 現行稼働状況 | `/improve` retire 後は断片。設計文書との照合のみ |

### frontmatter 反映

- `status: research-only` → **`partial`**（FI4 の考え方 + create-skill 境界を小採用。automate-me 本体は見送り、figure-it-out 本体は保留）
- `skill_change: deferred` → **`applied-small`**
