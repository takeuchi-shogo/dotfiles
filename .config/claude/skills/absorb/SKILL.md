---
name: absorb
description: "外部記事・論文・リポジトリの知見を現在のセットアップに統合する。ギャップ分析→選別→統合プラン生成。記事を貼って「活かしたい」「考えて」と言われたときに使用。Triggers: '活かしたい', '取り込みたい', '考えて', 'absorb', '統合して', 'この記事', 'integrate'. Do NOT use for: 単純な記事要約（直接回答で十分）、リサーチ（use /research）、ノート保存（use /note or /digest）。"
origin: self
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion, WebFetch
user-invocable: true
metadata:
  pattern: pipeline
---

# /absorb — 外部知見の統合

外部の記事・論文・リポジトリの知見を分析し、現在のセットアップに取り込む統合プランを生成する。

## Philosophy: Thoroughness over Helpfulness

記事の主張を helpful に取り込まない。網羅的な検証の上で取捨選択する。

- 既存仕組みの存在確認だけで Already と判定しない (Pass 2 + Phase 2.5 で強化可能性を検証する)
- **skip は許容するが「似ている」という類似度だけで skip しない** — Saturation Gate の skip は各手法を prior と1対1照合 (per-method 台帳) して立証する。照合先を名指しできない手法は novel 扱いで skip 不可 (立証責任は採用判断だけでなく skip 判断にも課す)
- 取捨選択は **Pruning-First** — 新規追加より既存強化を優先する
- ベンチマーク数値や「best X」主張は単独の採用根拠にしない (評価バイアス前提で読む)
- 記事著者のベンダーバイアス（自社製品優位の前提）を常に想定する

> 出典: Onyx DeepResearch 設計哲学 "Prefer being thorough over being helpful"（Akshay Pachaar 2026-04）を /absorb 文脈に翻訳。

## Trigger

- 記事 URL やテキストを貼って「活かしたい」「考えて」「取り込みたい」と言われたとき
- 論文やリポジトリを分析して改善点を抽出したいとき
- 他人の Claude Code 設定やワークフローを参考にしたいとき

## Workflow

```
/absorb {URL or テキスト}
  Phase 1: Extract    → 記事の要点を構造化抽出          [Haiku / Gemini]
  Phase 1.5: Saturation Gate → 同分野 absorb 飽和の早期検出  [Opus + Bash]
  Phase 2: Analyze    → 現状とのギャップ分析            [Sonnet Explore → Opus]
  Phase 2.5: Refine   → セカンドオピニオン + 周辺知識補完 [Codex + Gemini 並列]
  Phase 3: Triage     → ユーザーと「何を取り込むか」を選別 [Opus]
  Phase 4: Plan       → 統合プラン生成 + レポート保存     [Opus → Sonnet]
  Phase 5: Handoff    → 実行（同一セッション or 新セッション） [Opus]
  Phase 5.5-5.7       → Wiki/Obsidian/Log               [Sonnet BG]
```

## Delegation Policy

**Opus は判断・統合・ユーザー対話に専念する。それ以外は委譲する。**

| Phase | 委譲先 | Opus の役割 |
|-------|--------|------------|
| 1: Extract | Haiku（URL/テキスト）/ Gemini（リポジトリ） | 結果の受け取りのみ |
| 2: Analyze Pass 1 | Sonnet (Explore) | キーワードリストの作成 |
| 2: Analyze Pass 2 | Opus | 強化判断（委譲不可） |
| 2.5: Refine | Codex + Gemini **並列** | 批評の統合・テーブル修正 |
| 3: Triage | Opus | ユーザー対話（委譲不可） |
| 4: Plan | Opus → Sonnet | プラン策定 → レポート書き出し委譲 |
| 5+: Wiki/Obsidian/Log | Sonnet BG | 書き込み作業を並列委譲 |

large-context absorb で Codex CLI が 14 分程度 no-progress になった場合は、Codex 側を失敗として記録し、Gemini-only の Phase 3 fallback に進んでよい。fallback 理由と未取得の Codex 批評は分析レポートに明記する。

## Phase 1: Extract（要点抽出） [Haiku / Gemini に委譲]

### Phase 1.0: 取得経路の決定 (gate)

`/absorb` は引用 faithfulness が要件のため、**Haiku 内部要約による silent truncation を許容しない**。URL が渡された場合、最初に取得経路を決定する:

1. **C1 用途オーバーライドが優先**: `/absorb` は本質的に「原文引用が必要」な分析であるため、`web-fetch-policy.md` の **C1 オーバーライド** が trusted/non-trusted 判定に**先行**する。trusted ドメインであっても **`obsidian:defuddle` 経由で full markdown 取得**する (Haiku copyright filter ~125 字の引用制限を回避するため)
2. C1 オーバーライドが適用されない例外的な要約用途のみ、trusted 判定に進む:
   - URL のドメインを `.config/claude/data/trusted-domains.json` (`trusted_domains`) と照合
   - **trusted の場合**: `Agent(model: "haiku")` で WebFetch + 構造化抽出 OK
   - **trusted 外の場合 (Zenn/Qiita/note/blog/Wikipedia 等)**: WebFetch 禁止
3. **trusted 外で C1 がない場合のフォールバック**: 以下のいずれか
   - `obsidian:defuddle` skill (curl + defuddle で full markdown 取得)
   - Jina Reader (`https://r.jina.ai/<url>`)
   - Gemini grounding (`/gemini` skill, 1M コンテキスト)
4. 経路選択の根拠は `references/web-fetch-policy.md` の decision table + 用途別オーバーライド (C1/C2) に従う

Phase 1 出力 JSON に **`fetch_metadata`** を含める:

```json
{
  "fetch_metadata": {
    "url": "https://...",
    "domain": "...",
    "trusted": true,
    "route": "webfetch | defuddle | jina | gemini",
    "received_bytes": 12345,
    "visible_chars": 6789
  },
  "主張": "...",
  "手法": [...],
  "根拠": "...",
  "前提条件": "..."
}
```

### Phase 1.1: 構造化抽出 [委譲]

**委譲先の選択:**
- URL (trusted) / テキスト → `Agent(model: "haiku")` で WebFetch + 構造化抽出
- URL (non-trusted) → Sonnet で `obsidian:defuddle` 取得 + 構造化抽出 (Haiku は要約圧縮があるため不可)
- リポジトリ全体 → Gemini（1M コンテキストが必要）

**委譲先への指示内容:**

> 以下のソースから構造化抽出を行い、JSON で返してください:
> - **主張**: 記事が提唱していること（1-3文）
> - **手法**: 具体的なテクニック・パターン（箇条書き、各手法に検索用キーワード2-3語を付与）
> - **根拠**: なぜそれが有効か（データ、事例）
> - **前提条件**: どんなコンテキストで有効か

**WebFetch 失敗時のフォールバック（委譲先が処理）:**
1. WebSearch で記事タイトル/URL を検索し、キャッシュやミラーを探す
2. それも失敗 → 「取得失敗」を返す → Opus が `AskUserQuestion` でユーザーにテキスト貼り付けを依頼
3. 空レスポンスのまま Phase 2 に進んではならない

Opus は返された構造化抽出をユーザーに要約表示する（詳細は内部用）。

## Phase 1.5: Saturation Gate（飽和検出） [Opus + Bash]

**目的**: 同分野の absorb を 3 件以上繰り返して採用 0 を量産する **永続ループ** を Phase 2 に入る前に検出し、ユーザーに skip 選択肢を提示する。`/absorb` 自身の Pruning-First 違反を mechanism で防ぐ。

判定ルール・family taxonomy・閾値・skip 時のショートカットは `references/topic-family-saturation.md` に定義する。

### Step 1: Family 判定 [Opus]

Phase 1 抽出結果 (主張 + 手法) を `references/topic-family-saturation.md` の taxonomy で照合する。
- 該当 family なし → **PASS** (Phase 2 へ進む、新分野扱い)
- 該当 family あり → Step 2 へ

### Step 2: 過去 absorb 件数の集計 [Bash]

```bash
# 例: obsidian-second-brain family
grep -i -E "obsidian|second brain|PARA|vault" \
  /Users/takeuchishougo/dotfiles/docs/research/_index.md \
  | grep -E "absorb|analysis" | wc -l
```

`docs/research/_index.md` から同 family の過去 absorb 件数 N を集計する。
集計手順の詳細とフォールバック (ファイル名 enumeration) は reference 参照。

### Step 3: 採用率の推定 [Opus]

N >= 3 なら、各エントリ本文の以下マーカーで採用度合いを推定:
- 採用 0 / Reference Only / reject / 棄却 → 採用なし
- 採用 N 件 / Gap / 強化採用 (N >= 1) → 採用あり

採用率 = (採用ありエントリ数) / N

### Step 3.5: 手法 delta 計算 [Opus] — false-skip ガード

N >= 3 かつ採用率 < 20% で SATURATED 候補となった場合、**skip 判定の前に必ず実行する**。
飽和判定だけで skip すると、新規論点 (architecturally novel claims) を含む N+1 件目を見逃す。

> **本セクションと reference の Step 3.7 は同一手順を指す。** SKILL.md は workflow 内の挿入位置を強調するため Step 3.5、reference は既存 Step 3.5/3.6 (証拠記録/件数集計) と並べるため Step 3.7。両ファイル実装は同一。

1. Phase 1 抽出結果の **手法リスト** (current_methods) を抽出 (Phase 1 出力 JSON の `手法` フィールド、list of strings)
2. 同 family の直近 3 件の analysis report (`docs/research/*-absorb-analysis.md`) を Read し、各レポートの「手法」「主張」セクションから prior 手法 set を構築
   - **Read 失敗 / 「手法」セクション欠落の場合**: `prior_methods = unknown` として記録し、Step 4 で `AskUserQuestion` 経由 manual override 強制 (空集合扱いで false-novel 過大評価防止)
3. **per-method 照合台帳を作る (集合演算で丸めない — skip の立証責任)**:
   current_methods の **各手法を1行ずつ** 次の表に分類する。「全部似てる」と一括で丸める判断は禁止。

   | current 手法 | verdict | matched_prior (rehash のみ必須・3点セット) |
   |--------------|---------|---------------|
   | <手法名> | rehash / novel / ambiguous | `<report ファイル名>` の `<prior heading か引用句>` + 同等性の理由1文 |

   - **rehash** (= 既出ゆえ delta から除外): prior のどの手法と意味的同等かを `matched_prior` に**名指しで**書く。必須3点: (1) レポートのファイル名 (2) prior の heading か引用句 (3) なぜ同等かの理由1文。**次のいずれかなら rehash 無効 → `novel` か `ambiguous` に倒す**: `matched_prior` が空欄 / family label だけの広い一致 (例「どちらも second-brain 系」) / 引用句が出せない。「似ている」という類似度の主観だけで rehash にしない (例: 「IPARAG 採用」を rehash にするなら「`2026-XX-cyril.md` の "9-folder 構造採用" / 両者とも PARA 派生の固定フォルダ階層で同一」と名指す)。迷ったら ambiguous
   - **ambiguous** (半 novel): novel に計上しつつ `ambiguous_count` に別途記録し Step 4 提示時に明示
   - **novel**: prior に対応物を名指しできない
   - 過去 absorb で **明示的に Reject 済み** の手法 (rejection registry: `references/rejected-techniques.md` 参照、存在しなければ analysis report の "Reject" 明示記載) は **再評価対象** として novel に含める。ただし bounded recursion 条件:
     - 同一手法で **直近 12 ヶ月以内に 3 回以上** light-phase2 で Reject 再確認済なら novel から **除外** (永続ループ防止)
4. `delta_methods` = verdict が `novel` または `ambiguous` の行集合。`delta = |delta_methods|` を整数で記録 (**Step 4 の閾値判定・Step 5/5.5 の検証対象は常にこの `delta_methods` = novel + ambiguous**。ambiguous を落とさない)。**非整数値は禁止** — Opus は台帳の行数を返す。各 rehash 行に `matched_prior` 3点が揃って初めて delta から除外できる (名指しなき rehash は無効 → novel)
5. **台帳を保持する** — Step 6 (skip) / Step 5.5 (light-phase2) で skip/絞り込みの立証根拠として log・mini report に残す

判定への影響 (Step 4 参照):
- delta >= 2 → **SATURATED-but-novel** → `light-phase2` 強制提示
- delta == 1 → **SATURATED-borderline** → ユーザー判断 (3 択提示)
- delta == 0 → **SATURATED-pure-rehash** → 従来通り continue/skip 2 択
- `prior_methods = unknown` → **DELTA-UNKNOWN** → Step 5 で manual override 強制 (`light-phase2` 推奨、暗黙 PASS 禁止)

### Step 4: 判定と分岐 [Opus + AskUserQuestion]

| 条件 | 判定 | アクション |
|------|------|----------|
| N < 3 | **PASS** | Phase 2 へ通常進行 |
| N >= 3 & 採用率 >= 20% | **PASS (warning)** | Phase 2 へ進むが「重複領域」と user に告知 |
| N >= 3 & 採用率 < 20% & delta >= 2 | **SATURATED-but-novel** | `AskUserQuestion` で `light-phase2` / continue / skip (light-phase2 推奨) |
| N >= 3 & 採用率 < 20% & delta == 1 | **SATURATED-borderline** | `AskUserQuestion` で `light-phase2` / continue / skip (3 択、推奨なし) |
| N >= 3 & 採用率 < 20% & delta == 0 | **SATURATED-pure-rehash** | `AskUserQuestion` で continue / skip (skip 推奨) |
| N >= 3 & 採用率 < 20% & prior_methods == unknown | **DELTA-UNKNOWN** | `AskUserQuestion` で `light-phase2` / continue / skip (light-phase2 推奨) |

### Step 5: SATURATED 時の AskUserQuestion

delta_methods (novel + ambiguous) の有無で提示内容を切り替える。**どちらのテンプレも Step 3.5 の per-method 照合台帳を選択肢の前に必ず提示する** — 台帳を見せずに skip/light-phase2 の選択肢を出すのは禁止 (skip の立証は事後ログではなく user が判断する前提条件)。台帳が未完成なら選択肢を出さず先に台帳を埋める。

**SATURATED-but-novel / SATURATED-borderline / DELTA-UNKNOWN (delta >= 1 or unknown):**

```
この記事は topic family "<family>" の N 件目です:
  過去事例: <最新 3 件のファイル名>
  採用率: X% (Y 件中 Z 件で採用あり)
  検証対象 delta_methods (delta=D, novel + ambiguous): <delta_methods のリスト>
  ambiguous (半 novel 判定): <ambiguous_count> 件
  prior_methods 取得: <ok | unknown (理由: Read 失敗 / セクション欠落 等)>

  per-method 照合台帳 (全 current 手法、rehash は matched_prior 3点付き):
  <台帳をそのまま貼る — rehash 行は matched_prior の引用句+理由まで見せる>

選択肢:
  - light-phase2: delta_methods D 件だけ Phase 2 で検証 (Phase 2.5 省略可、mini レポート作成)
  - continue: フル workflow (Phase 2-5 + Phase 2.5) に進む
  - skip: log.md 1 行で閉じる (delta_methods も無視)
```

**SATURATED-pure-rehash (delta == 0):**

```
この記事は topic family "<family>" の N 件目、新規論点なし (delta = 0、完全な再パッケージ):
  過去事例: <最新 3 件のファイル名>
  採用率: X%

  per-method 照合台帳 (全 current 手法が rehash であることの立証 — これを見て skip を判断する):
  <台帳をそのまま貼る。各行に matched_prior (ファイル名 + 引用句 + 同等性の理由) が埋まっていること。
   1 行でも matched_prior が空 / family label だけ / 引用句なし なら delta>=1 となりこのテンプレは使わない>

skip にしますか？ (台帳の各 rehash に納得できれば skip 推奨)

選択肢:
  - skip: Wiki Log に台帳付きで追記して終了
  - continue: 念のため Phase 2 へ進む (台帳の照合に疑いがある場合)
```

### Step 5.5: light-phase2 選択時のショートカット [Opus]

Step 3.5 で抽出した delta_methods (novel + ambiguous) だけを対象に絞り込み Phase 2 を実行する。**ただし全 current 手法の照合台帳 (rehash として除外した分も含む) を mini report に必須セクションとして残す** — 除外側の立証が成果物から消えると light-phase2 が「最も楽な抜け道」になるため:

1. **Phase 2 Pass 1 (Sonnet Explore)** — delta_methods のキーワードだけを渡す (full method list ではなく)
2. **Phase 2 Pass 2 (Opus)** — Already/Partial/Gap/N/A 判定
3. **Phase 2.5 (Codex+Gemini) は省略可** — light flag。Gap 判定 >= 1 件出た場合は自動昇格で continue (フル workflow) に切り替えるかを `AskUserQuestion` で確認
4. **Phase 3 (Triage)** — adopt 候補があれば AskUserQuestion で選別
5. **Phase 4 (Plan + mini report)** — `docs/research/YYYY-MM-DD-{slug}-absorb-analysis.md` を作成、frontmatter に `status: light-phase2-only` を明記
   - **mini レポート定義**: frontmatter + Source Summary + Pass 1/Pass 2 judgment table + adopted/rejected decisions + **per-method 照合台帳 (全 current 手法、rehash として除外した分も `excluded as rehash` として matched_prior 付きで残す)** のみ。Phase 2.5 セクションは省略可
6. **Phase 5 (Handoff)** — 採用候補が S 規模なら即実行、それ以上は通常 handoff

log.md 追記時の operation 表記:
- adopt 候補が **1 件以上** → `ingest (light Phase 2)`、本体に「採用 N 件」明記
- adopt 候補が **0 件確定** → `ingest-skip (light Phase 2, adopt=0)`、本体に「Phase 2 まで検証したが全て Already/N/A」明記し skip 同等扱い

### Step 6: skip 選択時のショートカット [Opus]

Phase 2-5 をスキップして以下のみ実行:

1. `docs/wiki/log.md` に追記:
   ```
   ## [YYYY-MM-DD] ingest-skip | <記事タイトル>
   - ソース: <URL or タイトル>
   - 理由: topic family "<family>" saturated-pure-rehash (N 件目, 採用率 X%, delta=0)
   - 根拠: <Step 3.5 で記録した evidence (採用ありエントリの grep ヒット文字列リスト)>
   - per-method 照合台帳 (delta=0 の立証 — 各 current 手法 → matched_prior の名指し):
     - <current 手法 A> → `<report ファイル名>` の <prior 手法名> (rehash)
     - <current 手法 B> → `<report ファイル名>` の <prior 手法名> (rehash)
     - (全 current 手法を列挙。名指しできない手法が1つでもあれば delta>=1 となり skip しない)
   - 該当 family のキーワード hit: <Step 1 で照合したキーワード>
   - スキップ判定: Phase 1.5 gate
   ```
2. MEMORY.md 索引には追記しない (Reference Only 以下のため)
3. Phase 5.5-5.7 (Wiki INDEX / Obsidian / Wiki Log フル更新) も実行しない (log.md 1 行のみ)

### Step 7: Stale-Plan Audit — 過去採用タスクの棚卸し

PASS / SATURATED どちらの判定でも、N >= 1 (同 family に過去 absorb が存在) なら実行する。
過去採用タスクが時間経過で陳腐化していないか mechanism で audit する Phase 1.5 の姉妹機能。

判定基準・実行手順は `references/topic-family-saturation.md` Step 7 に定義する (こちらが正)。

要点:
- 同 family の最新 3 件の analysis report frontmatter を確認
- `status` 既に明示 (implemented / superseded / retired / partially-superseded) → audit skip
- `date` から 30 日未満 → audit skip (実装猶予期間)
- それ以外 → `AskUserQuestion` で `implemented / superseded / narrowed / retired / kept` を user に選択させ frontmatter を更新
- `kept` 選択は明示的判断であり `kept-by: YYYY-MM-DD` を必須記録 (暗黙的放置との区別)

### Safety rules

- **詳細は `references/topic-family-saturation.md` を参照すること (こちらが正)**。本ファイルの Safety rules は要約。矛盾がある場合は reference が優先。
- 採用率・delta 算出の根拠が不明確な場合は **`AskUserQuestion` で明示判断を強制** する (暗黙 PASS は禁止 — core principle "暗黙フォールバック・モック・NO-OP 絶対禁止" 準拠)
- ユーザーが事前に「飽和でも見たい」「強制 continue」と指示している場合は gate を skip
- 同一 family に分類するか判断が割れる場合: **どちらの family にも分類しない** ことを明示判断として記録する (silently に family なし扱いするのは暗黙フォールバック)
- 新分野の記事を誤って既存 family に誤分類するリスクが見えた場合は `AskUserQuestion` で確認

## Phase 2: Analyze（ギャップ分析 + 強化分析） [Sonnet Explore → Opus]

現在のセットアップと記事の知見を **2パス** で比較する。

### Pass 1: 存在チェック [Sonnet (Explore) に委譲]

Phase 1 で抽出した各手法のキーワードを `Agent(model: "sonnet", subagent_type: "Explore")` に渡す。

**Sonnet への指示内容:**

> 以下のキーワードリストについて、このプロジェクト内に関連する仕組みが存在するか調査してください。
> 各キーワードについて: (1) 関連ファイルパス (2) 該当箇所の要約 (3) 存在判定（exists / partial / not_found）を返してください。
> CLAUDE.md, MEMORY.md も確認対象に含めてください。

Opus は Sonnet の調査結果を受けて、各手法について以下を判定する:

| 判定 | 意味 |
|------|------|
| **Already** | 仕組みが存在する（既存ファイルを特定） |
| **Partial** | 部分的に実装。差分を明示 |
| **Gap** | 未実装。取り込み価値あり |
| **N/A** | 当セットアップには不要（理由を添える） |

### Pass 2: 強化チェック [Opus]

Already と判定した各項目について、記事の具体例（失敗事例・成功事例）と既存の仕組みを突き合わせ、強化余地があれば簡潔に併記する。Pass 1 で Sonnet が返したファイル内容を活用し、不足があれば追加で Read する（Already 項目あたり最大 2 ファイル）。

判定結果:

| 判定 | 意味 |
|------|------|
| **Already (強化不要)** | 記事の知見が既存の仕組みに完全にカバーされている |
| **Already (強化可能)** | 仕組みは存在するが、記事の知見で具体的に改善できる点がある |

強化可能な項目には、具体的な強化案（どのファイルの何をどう変えるか）を併記する。

### 出力テーブル

分析結果は以下の形式でユーザーに提示する:

```
## Gap / Partial / N/A
| # | 手法 | 判定 | 現状 |

## Already 項目の強化分析
| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
```

2つのテーブルを分けることで、「新規追加」と「既存強化」を明確に区別する。

ユーザーに分析結果をテーブルで提示する（Phase 2.5 の前に一度見せる）。

## Phase 2.5: Refine（セカンドオピニオン + 周辺知識補完） [Codex + Gemini 並列]

**Phase 2 の分析テーブルをユーザーに提示した後、必ず実行する。スキップ不可。**

> **Why Codex + Gemini (model-family diversity)**: Opus による Phase 2 判定は self-preference bias を持つ (Claude artifact を Claude 系だけで裁かない)。Codex (OpenAI) と Gemini (Google) を**異なるモデルファミリ**で並列起動するのは quorum (多数決) のためではなく、**bias mitigation** として位置づける。判定の修正は単純多数決ではなく、Opus が両者の指摘を統合・取捨選択する。
> 出典: CREAO Self-Healing Agent Harness 記事 (2026-04-29) の Tri-judge panel 設計を /absorb 文脈に翻訳。

Codex と Gemini を **並列** で起動する:

### Codex: 分析批評

**呼び出し方 (正規パス)**: cmux Worker を起動して Codex に依頼する。1-hop で observable (send-key/read-screen)、permission storm/silent stall を回避できる。

```bash
~/dotfiles/scripts/runtime/launch-worker.sh --model codex --task "<prompt>"
# → stdout に "workspace:N w-<id>-codex" が返る
# 結果ファイル: ${DISPATCH_RESULT_DIR:-/tmp/cmux-results}/w-<id>-codex.md (default は /tmp/cmux-results)
```

> **注意 (sandbox)**: `launch-worker.sh` の codex case は **default sandbox** で起動する (read-only ではない)。read-only 保証が必要な分析批評では下記の `codex exec --sandbox read-only` 直接呼び出しを使う。

> **注意 (cmux 不在環境)**: CI/SSH 単独環境で cmux が無い場合、`launch-worker.sh` は exit 1 する。fallback として `codex exec` を直接使う。

軽量・単発・cmux 外でよい場合は `codex exec` の直接呼び出しでも可:

```bash
codex exec --skip-git-repo-check -m gpt-5.5 --sandbox read-only \
  --config model_reasoning_effort="xhigh" "<prompt>" 2>/dev/null
```

**NG パターン (両方失敗事例あり、使用禁止)**:
- `Skill(skill: "codex:rescue", args: "--background ...")` — Permission Storm (settings.json allow に zsh -lc 内部パターン未追加で 15-30 prompts 連続発火) + 6-hop chain (Skill → command → fork → subagent → node → codex CLI) で観察不能 + `status: orphaned` 残骸が `~/.claude/plugins/data/codex-openai-codex/state/.../jobs/` に蓄積 (retention 機構なし)
- `Agent(subagent_type: "codex:codex-rescue")` の直接起動 — 中継 subagent は 162s で完了するが、内部 codex CLI が "Considering citation strategy" reasoning 段階でサイレント終了し最終 assistant message を出さず孤立 (2026-05-16 観測)

**プロンプト内容 (依頼テンプレート)**:

> 以下は外部記事のギャップ分析結果です。この分析に対して批評してください:
> 1. **見落とし**: 記事の手法で分析から漏れているものはないか
> 2. **過大評価**: Gap と判定したが実は既存の仕組みでカバーできるものはないか
> 3. **過小評価**: Already (強化不要) と判定したが実は強化すべきものはないか
> 4. **前提の誤り**: 記事の前提条件と当セットアップの文脈が合わない手法はないか
> 5. **優先度の提案**: 取り込むなら何を最優先にすべきか
>
> {Phase 2 の分析テーブル全体}
> {Phase 1 の記事要約}

### Gemini: 周辺知識補完

Gemini CLI（Google Search grounding 付き）に以下を依頼:

> 以下の記事の主張について、周辺知識を補完してください:
> 1. この手法を採用した他のプロジェクトの成功/失敗事例
> 2. 記事が言及していない制約やトレードオフ
> 3. より新しい代替手法があればその概要
>
> {Phase 1 の記事要約}

### Opus: 統合

両方の結果を受けて:
1. 分析テーブルを修正（判定の変更があれば反映）
2. 修正箇所をユーザーに明示（「Codex の指摘で X を Gap → Already に変更」等）
3. 修正後テーブルを提示してから Phase 3 に進む

## Phase 3: Triage（選別） [Opus]

`AskUserQuestion` で取り込み対象を **2段階** で選別する。

### Step 1: Gap / Partial の選別

```
以下の Gap/Partial 項目のうち、取り込みたいものを選んでください:

1. [Gap] ○○パターンの追加 — 効果: △△
2. [Partial] ○○の強化 — 現状: XX、記事推奨: YY
3. [Gap] ○○の導入 — 効果: △△

全部 / 番号選択 / なし（分析結果だけ保存）
```

### Step 2: Already (強化可能) の選別

Already (強化可能) 項目がある場合、Gap/Partial とは別に提示する:

```
以下の Already 項目に強化ポイントがあります。取り込みますか？

1. [強化] ○○に △△ を追加 — 既存: XX が YY を未カバー
2. [強化] ○○の重み調整 — 根拠: 記事の事例 ZZ

全部 / 番号選択 / なし
```

- 「全部」を選ばれた場合、優先順位を確認
- 「なし」の場合は Phase 4 をスキップし、分析レポートだけ保存
- Gap/Partial と Already 強化は独立に選択できる（片方だけ取り込むことも可能）

## Phase 4: Plan（統合プラン生成） [Opus → Sonnet]

選別された項目から統合プランを生成する。

### プランの成果物は記事次第

固定の出力先はない。記事の内容に応じて適切な成果物を提案する:

| 記事の種類 | 主な成果物例 |
|-----------|-------------|
| ベストプラクティス | rules/ 追加、references/ 追加、CLAUDE.md 修正 |
| 論文・研究 | 新スキル作成、エージェント追加、設計 spec |
| ツール・ライブラリ | scripts/ 追加、スキル改善、hook 追加 |
| セキュリティ | policy hook 追加、deny rules 追加 |
| ワークフロー | スキル修正、コマンド追加、settings.json 変更 |

### プラン生成ルール（Opus が担当）

1. 各タスクは具体的なファイルパスと変更内容を含む
2. タスク間の依存関係を明示
3. 規模を推定: S（1ファイル）/ M（2-5ファイル）/ L（6ファイル超）
4. L 規模の場合は `docs/plans/` にプランを保存

### 分析レポートの書き出し [Sonnet に委譲]

Opus がプラン策定を完了した後、レポートの書き出しを `Agent(model: "sonnet")` に委譲する。

**Sonnet への指示内容:**

> 以下の分析結果を `docs/research/YYYY-MM-DD-{slug}-analysis.md` に保存してください。
> テンプレート: `templates/analysis-report.md`
> {Phase 1 の構造化抽出}
> {Phase 2 + 2.5 の修正済みテーブル}
> {Phase 3 の選択/スキップ結果}
> {Phase 4 のタスクリスト}

### MEMORY.md への記録

MEMORY.md にはポインタ + 1行サマリのみ追記する。詳細は分析レポートに任せる。
既存のメモリエントリと重複する場合は更新で対応し、新規追加しない。

## Phase 5: Handoff（実行判断） [Opus]

プランの規模に応じて実行方法を提案:

| 規模 | 提案 |
|------|------|
| S | その場で実行 |
| M | ユーザーに確認後、同一セッションで実行 |
| L | プラン保存 → 新セッションで `/rpi` or 手動実行 |

## Phase 5.5-5.7: 後処理

Phase 5 の実行判断後、以下の後処理を **並列実行** する。委譲先は処理内容で分ける:

| 処理 | 実行者 | 理由 |
|------|--------|------|
| Wiki INDEX 更新 | Sonnet BG (`Agent(model: "sonnet", run_in_background: true)`) | 単純なファイル編集 |
| Wiki Log 追記 | Sonnet BG (Wiki Update と同じ agent に統合可) | 単純な append |
| **Obsidian Bridge** | **Opus 自身が main session で `Skill` tool 呼び出し** | subagent からの skill ネスト呼び出しは stall する (実測: 600s no progress) |
| MEMORY.md ポインタ追記 | Opus 自身が Edit | MEMORY.md は常時コンテキスト、Opus の方が状態を正確に把握 |

ユーザーへの確認が必要な項目（Wiki Update, Obsidian Bridge）は **Phase 5 で Opus がまとめて確認** してから実行する。

### Opus がユーザーに確認する内容（Phase 5 の末尾で一括確認）

```
後処理について確認します:
1. Wiki 更新 — docs/wiki/ の INDEX を更新しますか？ (Yes/No)
2. Obsidian 保存 — Literature Note として Vault に保存しますか？ (Yes/No)
(Wiki Log は自動追記します)
```

### 処理ごとの実行詳細

確認結果に応じて、承認された項目のみ実行する:

**Wiki Update（承認時のみ、Sonnet BG）:**
- `docs/wiki/` が存在する場合、INDEX 更新 + 関連概念の追加/更新
- 同じ Sonnet BG agent に Wiki Log 追記も統合して委譲する（1 agent で完結）

**Obsidian Bridge（承認時のみ、Opus 自身が main session で実行）:**
- 分析レポートを `/digest` 互換の Literature Note 形式に変換
- **Opus が `Skill` tool で `obsidian:obsidian-markdown` または `obsidian:obsidian-cli` を直接呼び出す**
- 保存先: Vault の `05-Literature/lit-{author}-{title-slug}.md`
- frontmatter: created, tags (type/literature, topic/...), source (title, author, url, type)
- セクション: Key Takeaways, Summary, My Thoughts, Action Items, Related Notes
- **重要 (stall 防止)**: subagent (Sonnet BG / general-purpose) から `Skill` tool を呼ぶと skill ネスト呼び出しが timeout する (実測: 600s no progress で fail)。**必ず Opus main session で `Skill` tool を直接呼ぶこと**
- **フォールバック**: skill が利用不能なら `Write` tool で Vault パスに直接書き込み (frontmatter + セクション構造を保持)
- **NG**: `mcp__obsidian__write_note` を直接呼ぶこと。obsidian-skills plugin が提供する skill 経由が正規ルート。MCP 直接呼びは `mcp-audit.py` の VeriGrey Tool Filter で **enforcement される (`sys.exit(2)` による hard block、soft warning ではない)**。absorb の SKILL.md に `mcp-tools: obsidian` が宣言されていないため scope violation 扱い。さらに PostHog "Meet agents at their abstraction level" 原則の観点からも、低レベル MCP より skill abstraction を使うべき

**Wiki Log（自動・確認不要、Sonnet BG）:**
- `docs/wiki/log.md` に ingest エントリを追記

```markdown
## [YYYY-MM-DD] ingest | {記事タイトル}

- ソース: {URL or タイトル}
- 判定: {Gap N個, Partial N個, Already N個, N/A N個}
- 取り込み: {選択された項目の概要}
```

## Usage

```
/absorb https://example.com/article       # URL から
/absorb                                    # テキスト貼り付け後に実行
/absorb docs/research/existing-report.md   # 既存レポートの再分析
```

## Gotchas

| NG | 理由 |
|----|------|
| 手法ごとに個別ディレクトリを Glob/Grep で走査する | Read 爆発で doom_loop/exploration_spiral を誘発。Sonnet Explore に委譲する |
| ギャップ分析せずに全部取り込む | 既存と重複したり、不要な複雑さを招く |
| MEMORY.md に詳細を書く | ポインタのみ。詳細は分析レポートに |
| 分析せずにプランだけ作る | Already/N/A を見落とし無駄な作業が発生 |
| 記事の主張を無批判に受け入れる | 前提条件が合わない手法を導入してしまう。Phase 2.5 で Codex + Gemini の批評を必ず通す |
| 1記事から10以上の変更を出す | 消化不良になる。優先度上位3-5個に絞る |
| **Already と判定して深掘りを止める** | **仕組みの存在 ≠ 記事の知見で強化不要。Pass 2 + Phase 2.5 で必ず検証する** |
| **Phase 2.5 (Refine) をスキップする** | **スキップ不可。Opus の判断バイアスを補正するために Codex + Gemini の並列批評は必須** |
| **Opus が Extract や探索を自分でやる** | **定型作業は Haiku/Sonnet に委譲する。Opus は判断・統合・ユーザー対話に集中** |
| **subagent (Sonnet BG / general-purpose) から `Skill` tool で obsidian skill を呼び出す** | **実測で 600s no progress stall (2026-04-19)。skill ネスト呼び出しは Opus main session で実行する。Phase 5.6 Obsidian Bridge は Opus 直接実行が原則** |
| **trusted 外ドメイン (Zenn/Qiita/note/Wikipedia 等) で WebFetch を直接使う** | **Claude Code v2.1.126 の WebFetch は内部 Haiku 要約 + 100k chars truncation がある (`docs/research/2026-05-06-webfetch-haiku-summary-absorb-analysis.md`)。引用 faithfulness が壊れるため `obsidian:defuddle` / Jina Reader / Gemini grounding に切替。詳細: `references/web-fetch-policy.md`** |
| **Phase 1.5 (Saturation Gate) をスキップする** | **同分野 absorb 3 件目以降の永続ループを防ぐ唯一の mechanism。Phase 1 完了後に必ず実行する。判定基準: `references/topic-family-saturation.md`** |
| **「似ているから」と類似度だけで rehash 判定し delta=0 で skip する** | **skip は「事実 (per-method 照合済み)」なら許容するが「似ている」という主観では不可。rehash には `matched_prior` (prior レポートのファイル名 + 手法名) の名指しを必須にし、名指しできない手法は novel に倒す。skip ログに照合台帳を残し「楽な skip」を後から検証可能にする (Step 3.5 / Step 6)** |
| **Pass 1 で Sonnet が返した「強化余地メモ」を Pass 2 で検証せず採用候補に昇格させる** | **Sonnet は generic feature noun (例: "Extended Thinking", "Bulk Processing", "Session History") から実装機会を想像で膨らませる傾向がある (Gap fabrication)。Pass 2 で必ず「記事原文に specific 提案があるか」を引用照合し、Sonnet imagination は除外する。Pass 1 出力の「強化余地メモ」は Pass 2 で照合される候補リストであり、line 54 の Pass 2「強化判断」(Opus 委譲不可) で確定する。詳細: `memory/feedback_absorb_sonnet_imagination.md`** |
| **未知の用語 (Cowork / Cloud Agents / Connectors 等) を grounding せずに "factually dubious" と即断する** | **Anthropic 公式機能は 2025-2026 で急速に追加されている。dotfiles の前提知識が stale な可能性。Phase 1 出力 (Haiku/Sonnet 抽出結果) を Opus がレビューするタイミングで未知の用語が含まれていた場合、Phase 2 に入る前に Gemini grounding で公式 docs 確認を先行する。実例: 2026-05-22 absorb で "Cowork tab" を dubious 判定したが公式実在を確認、dotfiles 内の stale guide が露出した** |
| **採用 0 = 記事から得るものなし、と即終了する** | **記事の framing が dotfiles 内の stale fact / drift を露出することがある (validation-only follow-up)。"article-backed novel instruction" と "platform drift validation triggered by article" を別 ledger で扱う。後者は採用件数に数えないが、分析レポートに `## Validation-only Follow-up` セクションを追記し、対象ファイル + drift 内容 + 訂正方針を明記して actionable にする (`docs/research/2026-05-22-khairallah-40-features-absorb-analysis.md` の "Validation-only Follow-up" 表を参考にする)** |

## Chaining

- **分析レポートから実装**: `/rpi docs/research/YYYY-MM-DD-{slug}-analysis.md`
- **大規模統合**: `/epd` の Phase 1 (Spec) に分析レポートを入力
- **深掘り調査**: 記事が不十分なら `/research` で補完調査
- **wiki 更新**: `/compile-wiki update` で差分レポートを wiki に反映
- **Obsidian保存**: Vault の `05-Literature/` に Literature Note として保存

## Skill Assets

- 分析レポートテンプレート: `templates/analysis-report.md`
- 統合プランテンプレート: `templates/integration-plan.md`
- 取捨選択基準: `references/triage-criteria.md`
- 飽和検出基準 (Phase 1.5): `references/topic-family-saturation.md`
