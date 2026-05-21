---
name: topic-family-saturation
description: /absorb Phase 1.5 で同分野 absorb の飽和を検出するための family taxonomy と閾値定義
type: reference
last_reviewed: 2026-05-22
---

# Topic Family Saturation Detection

`/absorb` Phase 1.5 (Saturation Gate) で使用する判定基準。
同分野の absorb を繰り返して採用 0 を量産する **永続ループパターン** を mechanism で早期検出する。

## なぜ必要か

`/absorb` は Phase 1 から Phase 5 までフル workflow が ~10-15 分 + 数千 token 消費する。
同分野の記事を 3 件以上 absorb 済みで採用率が低い場合、4 件目も同じ結論 (Reference Only) に
収束する確率が高い。Pruning-First 原則を skill 自身が破る dead-weight ループとなる。

**実例 (2026-05-21)**: Shushant Lakhyani "AI Second Brain" を absorb したところ、
同分野 (Obsidian + PARA + CLAUDE.md + Second Brain) で過去 4 件 absorb 済み・全て Reference Only
中心であることが Pass 1 完了後に判明。フル workflow が無駄になった。これを防ぐ。

## Family Taxonomy

初期 4 族 (実績ベース)。新しい飽和パターンを観測したら追加する。

| Family ID | キーワード (case-insensitive, OR) | 過去事例 |
|-----------|---------------------------------|---------|
| `obsidian-second-brain` | `obsidian`, `second brain`, `PARA`, `vault`, `session log` のうち **3 つ以上** hit | Cyril x3, akira_papa, Karpathy Second Brain Modified, Hermes |
| `skill-graphs` | `skill graph`, `atom`, `molecule`, `compound`, `skill composition` のうち **2 つ以上** | Skill Graphs 2.0, Tan thin-harness, Atomic Skills |
| `harness-engineering` | `harness`, `hook`, `scaffold`, `agent platform`, `harness everything` のうち **3 つ以上** | AlphaSignal Harness, Harness Pipeline BAN, Cursor harness, Self-Healing |
| `claude-code-tips` | `claude code tips`, `hidden features`, `N tricks`, `N tips`, `cheat code` のうち **2 つ以上** | Boris 30 Tips, Three-Model Stack, 73% Overhead 9 Patterns |

判定はユーザー固有のため、taxonomy は wash-out しない長期パターンのみを登録する。
1 回限りの記事タイトル一致では追加しない。

## 検出手順

Phase 1 完了直後に Phase 1.5 として実行する。

### Step 1: Family 候補を判定する

Phase 1 の構造化抽出結果 (主張 + 手法) を taxonomy の各キーワードリストで照合する。
複数 family に hit した場合、hit 数が最大の family を採用する (同数なら全 family を OR で検査)。

該当 family なし → Saturation gate **PASS** (Phase 2 へ進む)。新分野扱い。

### Step 2: 過去 absorb 件数を集計する

```bash
# 例: obsidian-second-brain family のキーワードで _index.md を grep
grep -i -E "obsidian|second brain|PARA|vault" /Users/takeuchishougo/dotfiles/docs/research/_index.md \
  | grep -E "absorb|analysis" \
  | wc -l
```

`docs/research/_index.md` を grep し、family に属する過去 absorb のエントリ数 N を数える。
正確な集計が困難な場合は、Bash で `ls docs/research/*-absorb-analysis.md` を列挙して
ファイル名から family 推定 (タイトルキーワードマッチ) も可。

### Step 3: 採用率を推定する

エントリ本文に対し case-insensitive + スペース揺れ吸収パターンで採用度合いを推定する:

- **採用なし指標** (regex `i` flag、`\s*` で空白揺れ吸収):
  - `採用\s*0` (採用 0 / 採用0 / 採用　0)
  - `採用\s*ゼロ`
  - `[Rr]eference[\s-]?[Oo]nly` (Reference Only / reference-only / REFERENCE ONLY)
  - `reject(ed)?` / `棄却` / `不採用`
- **採用あり指標**:
  - `採用\s*[1-9]\d*\s*件` (採用 1 件以上)
  - `\bGap\b` (Gap N 件 / Gap として採用)
  - `強化採用` / `partial 採用`

採用率 ≒ (採用ありエントリ数) / N

### Step 3.5: 推定根拠を記録する

採用ありエントリ数のカウントに使った具体的な grep ヒット文字列を変数 `evidence` として保持する (Step 6 の log.md 追記で使用)。
例: `evidence = ["採用 4 件 in Karpathy", "Reference Only in Cyril-x3"]`

### Step 3.7: 手法 delta 計算 — false-skip ガード [必須]

採用率 < 20% で SATURATED 候補となった場合、**skip 判定の前に必ず実行する**。
飽和判定だけで skip すると、新規論点 (architecturally novel claims) を含む N+1 件目を見逃す。
これは 2026-05-22 の "One-Folder Obsidian System" 事例で確認された false-skip 失敗モードである。

1. Phase 1 抽出結果から **手法リスト** を取得 (Phase 1 出力 JSON の `手法` フィールド)
2. 同 family の直近 3 件の analysis report (`docs/research/*-absorb-analysis.md`) を Read し、
   各レポートの「手法」「主張」セクションから既知手法 set を構築
3. `novel_methods = current_methods - union(prior_methods)` を計算
   - 完全一致だけでなく **意味的同等** で判定 (例: 「9-folder IPARAG」と「multi-folder hierarchy」は同一)
   - 過去 absorb で **明示的に Reject 済み** の手法 (例: one-folder vs IPARAG の真逆設計提案) は **再評価対象** として novel に含める。Reject の根拠が文書化されていれば次の Phase 2 で即時 N/A 判定でき低コスト
4. `delta = |novel_methods|` を記録 (これを Step 4 と Step 5 が使う)

判定への影響 (Step 4 参照):
- `delta >= 2` → **SATURATED-but-novel** → `light-phase2` 強制提示
- `delta == 1` → **SATURATED-borderline** → 3 択 (light-phase2 / continue / skip)
- `delta == 0` → **SATURATED-pure-rehash** → 従来通り 2 択 (continue / skip、skip 推奨)

### Step 4: 判定とアクション

| 条件 | 判定 | アクション |
|------|------|----------|
| N < 3 | PASS | Phase 2 へ通常進行 |
| N >= 3 かつ 採用率 >= 20% | PASS (warning) | Phase 2 へ進むが「重複領域」と user に告知 |
| N >= 3 かつ 採用率 < 20% かつ delta >= 2 | **SATURATED-but-novel** | `AskUserQuestion` で `light-phase2` (推奨) / `continue` / `skip` |
| N >= 3 かつ 採用率 < 20% かつ delta == 1 | **SATURATED-borderline** | `AskUserQuestion` で `light-phase2` / `continue` / `skip` (推奨なし) |
| N >= 3 かつ 採用率 < 20% かつ delta == 0 | **SATURATED-pure-rehash** | `AskUserQuestion` で `continue` / `skip` (skip 推奨) |

### Step 5: SATURATED 時の AskUserQuestion テンプレ

novel_methods の有無で提示内容を切り替える。

**SATURATED-but-novel / SATURATED-borderline (delta >= 1) テンプレ:**

```
この記事は topic family "<family>" の N 件目です:
  過去事例: <最新 3 件のファイル名>
  採用率: X%（Y 件中 Z 件で採用あり）
  検出された新規論点 (delta=D): <novel_methods のリスト>

選択肢:
  - light-phase2: 新規論点 D 件だけ Phase 2 で検証 (Phase 2.5 省略可、mini レポート作成)
  - continue: フル workflow (Phase 2-5 + Phase 2.5) に進む
  - skip: log.md 1 行で閉じる (新規論点も無視)
```

**SATURATED-pure-rehash (delta == 0) テンプレ:**

```
この記事は topic family "<family>" の N 件目です:
  過去事例: <最新 3 件のファイル名>
  採用率: X%
  新規論点: なし (delta = 0、完全な再パッケージ)

フル absorb workflow を実行しますか？

選択肢:
  - continue: 念のため Phase 2 へ進む
  - skip: Wiki Log に 1 行だけ追記して終了 (推奨)
```

### Step 6: skip 選択時のショートカット

Phase 2-5 をスキップして以下のみ実行:

1. `docs/wiki/log.md` に追記:
   ```
   ## [YYYY-MM-DD] ingest-skip | <記事タイトル>
   - ソース: <URL or タイトル>
   - 理由: topic family "<family>" saturated-pure-rehash (N 件目, 採用率 X%, delta=0)
   - 根拠: <Step 3.5 で記録した evidence (grep ヒット文字列リスト)>
   - 該当 family のキーワード hit: <Step 1 で照合したキーワード>
   - スキップ判定: Phase 1.5 gate
   ```
2. MEMORY.md の外部知見索引には追記しない (Reference Only 以下のため)
3. Phase 5.5-5.7 (Wiki/Obsidian/Log) も実行しない (log.md だけ)

### Step 6.5: light-phase2 選択時のショートカット

Step 3.7 で抽出した novel_methods だけを対象に絞り込み Phase 2 を実行する:

1. **Phase 2 Pass 1** — novel_methods のキーワードだけを Sonnet Explore に渡す (full method list ではなく)
2. **Phase 2 Pass 2** — Opus が Already/Partial/Gap/N/A 判定 (novel_methods に限定)
3. **Phase 2.5 (Codex+Gemini) は省略可** — light flag。ユーザーが明示希望すれば実行
4. **Phase 3 (Triage)** — adopt 候補があれば AskUserQuestion で選別
5. **Phase 4 (Plan + mini report)** — `docs/research/YYYY-MM-DD-{slug}-absorb-analysis.md` を作成、frontmatter に `status: light-phase2-only` を明記
6. **Phase 5 (Handoff)** — 採用候補が S 規模なら即実行、それ以上は通常 handoff
7. **log.md operation** は `ingest (light Phase 2)` (`ingest-skip` ではない)

## 判定の安全側ルール

- **採用率算出の根拠が不明確な場合は `AskUserQuestion` で明示判断を強制** する (暗黙 PASS は禁止 — CLAUDE.md core principle "暗黙フォールバック・モック・NO-OP 絶対禁止" 準拠):
  ```
  採用率の判定根拠が不明確です:
    family: <family>
    N: <count>
    検出した採用ありエントリ: <evidence>
    検出した採用なしエントリ: <evidence>
    判定不能の理由: <reason — 例: 表記揺れで grep が分類できない/該当 entry の本文が要約のみ等>

  どう扱いますか？
    - manual-count: ユーザーが手動で _index.md を読んで採用率を返す
    - continue: gate を通過させてフル absorb workflow に進む
    - skip: SATURATED とみなして ingest-skip ログのみ残す
  ```
- ユーザーが明示的に「飽和でも見たい」と指示している場合は gate を skip
- 同一 family に分類するか判断が割れる場合: **どちらの family にも分類しない** ことを明示判断として記録する (sliently に family なし扱いするのは暗黙フォールバック)
- 新分野の記事を誤って既存 family に誤分類するリスクが見えた場合は `AskUserQuestion` で確認

## Anti-Patterns

| NG | 理由 |
|----|------|
| 単一キーワードの hit で family 確定 | false positive が増える。N キーワード以上 hit を必須に |
| 採用率 0% でも user 確認なしに自動 skip | 新しい角度を持つ N 件目を見逃す。**必ず AskUserQuestion** |
| family taxonomy にタイトル一致だけで追加 | 永続パターンのみ登録する。3 件以上の累積実績が前提 |
| skip 後に MEMORY.md 索引へ追記 | Reference Only 以下は索引も汚すだけ。log.md だけに残す |
| **delta 計算をスキップして即 skip 判定** | **2026-05-22 で確認された false-skip 失敗モード。SATURATED 候補でも Step 3.7 (手法 delta) は必須実行。delta >= 1 なら light-phase2 を選択肢に出す** |
| **過去の Reject 済み手法を novel から除外する** | Reject 根拠が古い・誤っている可能性。novel 扱いして Phase 2 で再評価し、文書化された Reject 根拠があれば即時 N/A で低コスト |

## 関連

- `/absorb` Phase 1.5 — このリファレンスを参照して判定
- `references/improve-policy.md` — Pruning-First philosophy の源流
- `docs/research/_index.md` — 集計対象のインデックス
