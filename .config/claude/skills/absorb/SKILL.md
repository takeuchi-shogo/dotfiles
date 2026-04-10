---
name: absorb
description: "外部記事・論文・リポジトリの知見を現在のセットアップに統合する。ギャップ分析→選別→統合プラン生成。記事を貼って「活かしたい」「考えて」と言われたときに使用。Triggers: '活かしたい', '取り込みたい', '考えて', 'absorb', '統合して', 'この記事', 'integrate'. Do NOT use for: 単純な記事要約（直接回答で十分）、リサーチ（use /research）、ノート保存（use /note or /digest）。"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion, WebFetch
user-invocable: true
metadata:
  pattern: pipeline
---

# /absorb — 外部知見の統合

外部の記事・論文・リポジトリの知見を分析し、現在のセットアップに取り込む統合プランを生成する。

## Trigger

- 記事 URL やテキストを貼って「活かしたい」「考えて」「取り込みたい」と言われたとき
- 論文やリポジトリを分析して改善点を抽出したいとき
- 他人の Claude Code 設定やワークフローを参考にしたいとき

## Workflow

```
/absorb {URL or テキスト}
  Phase 1: Extract    → 記事の要点を構造化抽出          [Haiku / Gemini]
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

## Phase 1: Extract（要点抽出） [Haiku / Gemini に委譲]

**委譲先の選択:**
- URL / テキスト → `Agent(model: "haiku")` で WebFetch + 構造化抽出
- リポジトリ全体 → Gemini（1M コンテキストが必要）

**Haiku / Gemini への指示内容:**

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

Codex と Gemini を **並列** で起動する:

### Codex: 分析批評

`codex-rescue` サブエージェント（または `/dispatch` 経由の cmux Worker）に以下を依頼:

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

## Phase 5.5-5.7: 後処理 [Sonnet BG に委譲]

Phase 5 の実行判断後、以下の後処理を `Agent(model: "sonnet", run_in_background: true)` にまとめて委譲する。
ユーザーへの確認が必要な項目（Wiki Update, Obsidian Bridge）は **Phase 5 で Opus がまとめて確認** してから委譲する。

### Opus がユーザーに確認する内容（Phase 5 の末尾で一括確認）

```
後処理について確認します:
1. Wiki 更新 — docs/wiki/ の INDEX を更新しますか？ (Yes/No)
2. Obsidian 保存 — Literature Note として Vault に保存しますか？ (Yes/No)
(Wiki Log は自動追記します)
```

### Sonnet BG への委譲内容

確認結果に応じて、承認された項目のみ Sonnet BG に委譲する:

**Wiki Update（承認時のみ）:**
- `docs/wiki/` が存在する場合、INDEX 更新 + 関連概念の追加/更新

**Obsidian Bridge（承認時のみ）:**
- 分析レポートを `/digest` 互換の Literature Note 形式に変換
- **Sonnet BG に `obsidian:obsidian-cli` または `obsidian:obsidian-markdown` skill の呼び出しを委譲**し、Vault の `05-Literature/lit-{author}-{title-slug}.md` に保存する
- frontmatter: created, tags (type/literature, topic/...), source (title, author, url, type)
- セクション: Key Takeaways, Summary, My Thoughts, Action Items, Related Notes
- **NG**: `mcp__obsidian__write_note` を直接呼ぶこと。obsidian-skills plugin が提供する skill 経由が正規ルート。MCP 直接呼びは `mcp-audit.py` の VeriGrey Tool Filter で soft block される（absorb の SKILL.md に `mcp-tools: obsidian` が宣言されていないため）。さらに PostHog "Meet agents at their abstraction level" 原則の観点からも、低レベル MCP より skill abstraction を使うべき

**Wiki Log（自動・確認不要）:**
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

## Anti-Patterns

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
