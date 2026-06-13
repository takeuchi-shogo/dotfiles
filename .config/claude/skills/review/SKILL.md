---
name: review
description: >
  コード変更のレビューを実行。変更規模に応じてレビューアーを自動選択・並列起動し、結果を統合する。
  コード変更後の Review 段階で使用、または /review で手動起動。
  言語固有チェックリストは references/review-checklists/ に配置。code-reviewer のプロンプトに注入して使用。
  Triggers: 'レビューして', 'review', 'コードレビュー', 'セルフレビュー', 'check my code'.
  Do NOT use for: 直近の差分確認のみ（use git diff）、100行超の Codex レビュー（use /codex-review）、Product 観点の検証（use /validate）。
origin: self
allowed-tools: Read, Bash, Grep, Glob, Agent
hooks:
  PreToolUse:
    - matcher: "Edit|Write"
      hooks:
        # 決定論ゲート (旧 type:prompt LLM judge は Verdict/承認済みでも
        # false-block したため command 化。詳細: scripts/policy/review-phase-gate.py)
        - type: command
          command: python3 $HOME/.claude/scripts/policy/review-phase-gate.py
metadata:
  pattern: reviewer
  version: 1.0.0
  category: quality
---

# Code Review Orchestrator

コード変更に対して、適切なレビューアーを自動選択・並列起動し、結果を統合するオーケストレーター。

## Workflow

```
1. Pre-analysis  → git diff で変更を分析
2. Scaling       → 行数・内容からレビュアー構成を決定
3. Dispatch      → Agent ツールで1メッセージに並列起動
4. Synthesis     → 結果を統合し templates/review-output.md 形式で出力
4.5 Visual Output → 指摘を difit --comment でインライン表示（指摘 1 件以上時）
```

## Review Principles (Google eng-practices)

レビューの primary purpose と feedback の規律を定義する。すべての reviewer 起動 (Step 3) に先立ち、本セクションの原則を適用する。

### Principle 1: Positive Principle — Code Health Improvement (#1)

- レビューの **primary purpose** は "overall code health の改善" であり "完璧の追求" ではない
- **approve 基準**: CL が code health を改善する (= 既存より良い状態にする) なら approve する。完璧である必要はない
- code health の評価軸: 可読性 / テスト網羅性 / 設計 (結合度・依存方向) / 保守性 / 動作正当性
- 「完璧でないから block」は anti-pattern。「現状より悪化させる」または「致命的問題がある」ときのみ block する
- Verdict 計算式 (`agents/code-reviewer.md` "Mandatory Output Format") は本原則の operationalization である
  - `MUST ≥ 1 → BLOCK` の "MUST" は **致命的問題 = 現状より悪化** (security/bug/GP 違反) の operationalization であり、本原則と矛盾しない

### Principle 2: Evidence-Based Feedback (#2)

- すべての review コメントは以下のいずれかを根拠として引用すること:
  - **Technical facts**: 計測可能な事実 (benchmark / profile / 仕様書記載)
  - **Data**: 過去 incident / regression 履歴 / production metrics
  - **Principles**: spec / RFC / language spec / established best practices (Google style guide, Go Code Review Comments 等)
- **NG**: "I think" / "feels wrong" / "好みの問題" 単独 (= opinion)
- **例外**: 明示的に "個人的な好み" と label した提案 → `[NIT]` 扱いに限定
- 開発者からの pushback (反論) を受けた場合、Evidence を改めて提示する義務を負う (`agents/code-reviewer.md` Section D pushback-who-is-right)
- 詳細 rubric: `references/review-consensus-policy.md` "Evidence-Based Feedback Rubric"

### Principle 3: Design-First Feedback Gate (#6)

Google eng-practices `navigate.md` の navigate-three-steps を AI review に転用したもの。

- レビュー進行順: **broad** (設計・アーキテクチャ) → **specific** (実装詳細) → **nit** (スタイル)
- **設計上の重大問題** を発見した場合、詳細コメントより**先に**返却する (design-first gate)
- design-first gate の発動条件 (いずれか):
  - アーキテクチャ変更が必要 (層の境界 / 責務分離 / 依存方向)
  - API 境界の問題 (公開シグネチャ / プロトコル不整合)
  - 不可逆な設計決定 (DB schema / public API / migration)
- gate 発動時: Findings 冒頭に `[DESIGN_FIRST]` セクションを置き、specific / nit は返却しない (designer の検討待ち)
- 例: 「`[DESIGN_FIRST]` 本 CL は `Repository` が `Service` に依存しています (依存方向の逆転)。具体的コメント返却前に設計再検討をお願いします」
- 設計問題が解消されたら、specific / nit を別 round で返却する

### Principle 4: Author Preference Authority (#23)

Google eng-practices `standard.md` "Principles" 由来。**style guide / project convention にない領域では author の choice を尊重する**。Principle 2 (Evidence-Based) と直交する独立原則 — 「証拠がない」だけでなく「証拠があっても領域外なら従う」を明示化する。

- **適用範囲**: 命名 (引数名・ローカル変数名) / コード並び順 / 抽象化の粒度 / コメントの分量 / etc. のうち、以下の判定で「style guide / convention にない」と判定されたもの
- **判定フロー** (Step 1 → Step 2 を順に確認、両方 No のとき Principle 4 適用):
  1. 該当する style guide (Google Style Guide / Effective Go / TypeScript handbook / 内部 `references/review-checklists/*.md`) に明文化されているか?
     - **Yes** → reviewer の指摘は valid。Principle 2 で Evidence を提示。判定終了
     - **No** → Step 2 へ進む
  2. 該当する project convention があるか? (本リポジトリ内 5 箇所以上で同パターン使用 = empirical convention)
     - **Yes** → reviewer の指摘は valid (Principle 2 Empirical evidence)。判定終了
     - **No** → Principle 4 適用、author choice 尊重
  - **empirical convention 検証手順**: `grep -rn "<pattern>" .` で 5 件以上ヒットする場合のみ "Yes"。grep コストが高い・パターンが曖昧で検証不能な場合は "No" として author choice 尊重 (誤検出より過小検出を優先 = author autonomy 保護)
- **Principle 4 適用時の reviewer 行動**:
  - 指摘自体を出さない (NIT も含めて抑制)
  - どうしても提案したい場合は `[FYI]` ラベル + "個人的な好み" 注記必須 (severity = FYI 限定)
  - **NG**: `[NIT] 変数名 u は短すぎる` (style guide 根拠なし、convention 根拠なし、reviewer 個人好み)
  - **OK**: `[FYI] 個人的な好みですが、変数名 u は readability の観点で user の方が好みです` (FYI + 明示)
- **目的**: AI reviewer の主観 NIT 量産を抑制し、author の autonomy を保護する。Google "Reviewers should not be picky about every little detail" の operationalize
- **Evidence-Based (Principle 2) との関係**:
  - Principle 2: 「指摘するなら根拠を引用しろ」(根拠の品質)
  - Principle 4: 「領域外なら指摘するな」(指摘範囲の制限)
  - 両者は AND で適用 — Evidence あり ∧ 領域内 → 指摘 valid
- **CC-8 Linguistic Anti-patterns との関係**: CC-8 (名前と振る舞いの矛盾) は project convention に該当するため Principle 4 の例外 = 指摘 valid

## Step 0: Tier Preflight (deterministic)

レビュー構成を決める前に、決定論スクリプトで tier (light/standard/deep) を判定する。
リスクカテゴリ (High/Medium/Low) の判定基準は `references/reviewer-routing.md` の
リスクカテゴリ自動判定表が single source of truth — 表をここに複製しない。

1. diff 情報を取得（Step 1.2 で取得する値の先取り）: `git diff --stat` / `git diff --name-only`
2. 変更ファイルパスと内容シグナルから risk_class を判定（reviewer-routing.md の表に従う）
3. tier を決定論で判定:

   ```bash
   echo '{"diff_stat": {"insertions": <N>, "deletions": <N>}, "files": [...], "risk_class": "<High|Medium|Low>"}' \
     | python3 ~/.claude/scripts/policy/review-tier.py
   ```

4. tier に応じて以降の Step を分岐:

| tier | 挙動 |
| --- | --- |
| **light** | reviewer 起動と Codex Gate を省略。Verify のみ実施し、Step 4 相当として `## Verdict` に `PASS [LIGHT TIER]` + 判定理由 (script の reason) を出力。Run Metrics は `reviewers: []` で記録する (Step 4 参照) |
| **standard** | 現行どおり Step 1 以降を実施（Step 2 の行数スケール表に従う） |
| **deep** | Step 1 以降を実施し、Step 2 の構成に `codex-reviewer` + `security-reviewer` を必須追加（reviewer-routing.md の High リスクオーバーライドと同じ扱い） |

> light は三重ガード（Low リスク ∧ ≤10行 ∧ docs/test-only）を全て満たす場合のみ。
> 判定が不能・曖昧な場合 script は standard に倒す（品質側に安全）。

## Step 1: Pre-analysis

### Step 1.1: Diff Scope Mode の選択

レビュー対象の scope は **mode を明示的に分岐**して選ぶ。state を曖昧にしたまま `git diff HEAD` を打つと「何を review したか」が後で再現できない。

| Mode | 対象 | コマンド | 適用条件 |
|------|------|---------|----------|
| **local (uncommitted)** | 未コミットの patch | `git diff HEAD` | 実際に unstaged/staged/untracked がある時のみ |
| **staged only** | staged change のみ | `git diff --cached` | commit 直前の最終確認 |
| **branch (PR work)** | コミット済の branch | `gh pr view --json baseRefName --jq .baseRefName` で BASE 取得 → `git diff origin/$BASE...HEAD` | PR review、push 済 branch、open PR |
| **commit (landed work)** | 既に land した単一 commit | `git diff <COMMIT>^..<COMMIT>` | clean main 上での post-merge audit、stack 内の特定 commit |

#### Caveat: "A clean local review only proves there is no local patch"

`local` mode で「指摘ゼロ」が出ても、それは **unstaged/staged 変更が無い (or 軽微)** を示すだけで、push 済 / PR で merge 待ちの差分は対象外。**committed / pushed / PR 作業を対象にする場合は `branch` か `commit` mode に切り替える** こと。helper の docs が "dirty work first" と書いてあるからといって `local` を強制してはならない。

> 出典: openclaw/agent-skills `autoreview` SKILL "Use this only when the patch is actually unstaged/staged/untracked in the current checkout. For committed, pushed, or PR work, point the helper at the commit or branch diff instead; do not force `--mode local` / `--uncommitted` just because the helper docs mention dirty work first. A clean local review only proves there is no local patch"

### Step 1.2: 基本情報の収集

```bash
git diff --stat HEAD
git diff --name-only HEAD
```

以下を特定する:

- **変更行数**: insertions + deletions の合計
- **言語**: 変更ファイルの拡張子
- **コンテンツシグナル**: diff 内容からスペシャリストの必要性を判定

## Step 1.3: Impact Pre-scan（30行以上の変更）

diff を見る**前に**、変更された関数・型の呼び出し元を特定する。
表面上は安全な変更でも、呼び出し元を考慮すると破壊的変更になるケースを防ぐ。

**code-review-graph MCP が利用可能な場合**（優先）:
1. `detect_changes_tool` で risk-scored な変更分析を取得
2. `get_impact_radius_tool` (depth=2) で間接依存を含む blast radius を取得
3. risk score が 0.7 超の関数は Step 2 で自動的にスペシャリスト追加の判断材料にする
4. 結果を Step 3 で各レビューアーのプロンプトに含める

**MCP が利用不可の場合**（フォールバック）:
1. `git diff --name-only HEAD` で変更ファイルを取得
2. 各ファイルの diff から、**追加・削除・シグネチャ変更された export 関数/型** を抽出
3. `Grep` で各 export の呼び出し元を検索（上位5件まで）
4. 結果を以下の形式でまとめ、Step 3 で各レビューアーのプロンプトに含める:

```
### Impact Context
- `funcX()` in file_a.ts → called by: file_b.ts:15, file_c.ts:42
- `TypeY` in file_a.ts → referenced by: file_d.ts:8
```

- 10行以下の変更・export のないファイルのみの変更ではスキップ
- PRE_ANALYSIS モードの `cross-file-reviewer` と異なり、ここでは**簡易版**（Grep 1回/export）に留める

## Step 1.4: Navigation Order (Google navigate.md)

Google eng-practices `navigate.md` のファイルナビゲーション順を AI review に転用する。Principle 3 (Design-First Gate) が **severity 順** を規定するのに対し、本 Step は **どのファイルから読むか** を規定する (直交)。

### ファイル読み順 (推奨)

1. **Main file first**: 変更の **主目的** を含むファイルを最初に読む
   - 判定基準 (優先度順):
     - PR description / commit message で言及された file
     - 変更行数が最大の non-test file
     - `handler` / `controller` / `service` 等の entry point 名を持つ file
   - 主目的を把握することで、以降のファイルを「主目的への貢献」として読める
2. **Affected files next**: main file が export する関数・型を caller として使う file を辿る
   - Step 1.3 Impact Pre-scan の出力 (export → caller マッピング) を活用
   - **Step 1.3 skip 時 (10 行以下 or export なし) の fallback**: Step 1.2 の `git diff --name-only HEAD` から caller を手動トレース (`Grep` で 1-2 件のみ確認、簡易版で可)
   - main file の変更が caller 側で適切に反映されているか確認
3. **Trivial files last**: 以下は最後に読む (生成コード / 依存変更 / docs)
   - `.pb.go` / `_gen.go` / lockfile / `.mod` / `.sum`
   - test snapshot fixture (`__snapshots__/*` / `testdata/*`)
   - `.md` / コメントのみ変更ファイル
   - これらは構造的問題を含む確率が低く、最後に読むことで cognitive load を主要変更に集中できる

### Pass 1 (Full Enumeration) との関係

- Step 1.4 は **読む順** を規定するが、Pass 1 (`agents/code-reviewer.md` Step 2) の **全ファイル enumeration 必須** ルールは維持
- 順序最適化は cognitive load 削減のためであり、カバレッジ削減ではない
- 30 行以下の変更ではスキップ可 (file 数 < 3 のとき順序最適化の ROI なし)

### Trivial file の severity 抑制

trivial files (生成コード / lockfile / snapshot) の指摘は原則 `[NIT]` 以下に抑制する (false positive リスク高 + 通常 reviewer の管轄外)。例外: lockfile に脆弱なバージョンが pin されている等の security issue は `[MUST]` 維持。

## Step 1.5: Design Rationale Check（M/L のみ）

M/L 規模の変更では、レビュー開始前に Design Rationale の存在を確認する（S は免除）。

確認項目（`references/comprehension-debt-policy.md` 参照）:
1. **What**: この変更は何を解決するか — 記述があるか
2. **Why this approach**: なぜこのアプローチか（却下した代替案含む）— 記述があるか
3. **Risk mitigation**: 何が壊れうるか、どう防いでいるか — 記述があるか

- Plan ファイル、コミットメッセージ、または PR 説明に含まれているか確認
- 不十分な場合はレビュー冒頭で `must:` として指摘し、記述を求める

## Step 2: Scaling Decision

### レビュアー構成（行数ベース）

| 変更規模 | 構成                                                                                                       | 最大N |
| -------- | ---------------------------------------------------------------------------------------------------------- | ----- |
| ~10行    | レビュー省略（Verify のみ）— Step 0 の light tier に統合（light 条件を満たさない ~10行 変更は standard）                          | 0 |
| ~30行    | `code-reviewer`（言語チェックリスト注入）+ `codex-reviewer`                                                                        | 2 |
| ~50行    | 上記 + `edge-case-hunter` + `cross-file-reviewer`（2+ファイル時のみ）                                                              | 4 |
| ~200行   | 上記 + `golang-reviewer`（Go変更時）/ `typescript-reviewer`（.ts/.tsx/.js/.jsx変更時）+ **Gemini セキュリティレビュー**            | 6 |
| 200行超  | 上記全て + スペシャリスト（3-way: Claude + Codex + Gemini）                                                                        | 8 |

> **Scaling Note**: レビューア数の増加は合意コスト（矛盾の検出・解決）を増大させる。
> 上限を超えるスペシャリスト候補がある場合、コンテンツシグナルの強さでトリアージし上限内に収める。
> 詳細: `references/review-consensus-policy.md`

### 言語固有チェックリスト（プロンプト注入）

`code-reviewer` のプロンプトに、**cross-cutting + 該当言語**のチェックリストを Read して注入する:

| 拡張子              | 参照ファイル                                  |
| ------------------- | --------------------------------------------- |
| **全レビュー共通**  | `references/review-checklists/cross-cutting.md` |
| `.ts/.tsx/.js/.jsx` | `references/review-checklists/typescript.md`  |
| `.go`               | `references/review-checklists/go.md`          |
| `.py`               | `references/review-checklists/python.md`      |
| `.rs`               | `references/review-checklists/rust.md`        |
| 複数言語混在        | 該当する全チェックリストをプロンプトに含める  |

> **cross-cutting.md は常時注入する。** 言語固有チェックリストは追加で注入する。

### プロジェクト特化レビューアー（ペルソナレビュー）

プロジェクトのレビューデータが存在する場合、汎用レビューアーに加えてペルソナレビューアーを起動する。
チームメンバーの指摘パターンを事前検出し、PR 提出前に修正する目的。

| 条件 | レビューアー | 役割 |
|------|-------------|------|
| `.claude/data/reviewers/ma-reviews.json` 存在 + Go/Proto 変更あり | `reviewer-ma` | 命名規約・アーキテクチャ・Entity 設計・責務分離 |
| `.claude/data/reviewers/mu-reviews.json` 存在 + Go/Proto/Dart 変更あり | `reviewer-mu` | GORM 安全性・フィルタ設計・テスト網羅性・ドキュメント配置 |

- **行数閾値なし**: レビュー対象（10行超）であれば ma/mu は常に起動する。小さな変更にこそ命名・設計の問題が潜む
- **省略不可**: データファイルが存在するプロジェクトでは、レビューアー構成の上限 (最大N) にカウントしない追加枠として扱う
- `golang-reviewer` との併用。golang-reviewer は汎用 Go ベストプラクティス、ma/mu はリポジトリ固有パターン
- データファイルの存在チェック: `ls .claude/data/reviewers/{ma,mu}-reviews.json 2>/dev/null`
- ma/mu はプロジェクト特化のため、capability score テーブルには含めず、Synthesis では `[PERSONA]` タグで区別する
- Synthesis で ma/mu の指摘が golang-reviewer/code-reviewer と重複する場合、ペルソナ側の具体的な修正案を優先する

### 個人レビュー学習（review-learnings 注入）

`.claude/data/review-learnings/` が存在する場合、変更ファイルのドメインに該当する learnings md を Read して `code-reviewer` のプロンプトに注入する。過去に自分が受けた指摘パターンを PR 提出前に検出する目的（ma/mu ペルソナと同じ枠組みの観点ルール版、匿名化済み・観点別）。

- 存在チェック: `ls .claude/data/review-learnings/*.md 2>/dev/null`
- ドメイン判定: `.claude/data/review-learnings/index.md` の domain マップ表を Read し、変更ファイルパス → 対応する `<domain>.md` を解決する（マップはリポジトリごとに index.md で定義する。マップに該当しないパスは注入なし）
- cross-cutting チェックリストと同様に、該当ドメインの md を追加注入する（複数ドメインに跨る変更は該当する全 md を注入）
- 全体像と出典内訳も `.claude/data/review-learnings/index.md` を参照

### コンテンツベースのスペシャリスト自動検出

行数に関係なく、diff の内容にマッチするスペシャリストを追加する。
ただし **50行以上の変更** でのみ適用（10行以下はレビュー自体を省略）。

| diff 内のシグナル  | スペシャリスト          | 検出パターン                                                       |
| ------------------ | ----------------------- | ------------------------------------------------------------------ |
| エラーハンドリング | `silent-failure-hunter` | `catch`, `recover`, `fallback`, `retry`, `on.*error`, `try {`      |
| 新しい型定義       | `type-design-analyzer`  | `type `, `interface `, `struct `, `enum ` の追加行                 |
| テスト変更         | `pr-test-analyzer`      | `_test.go`, `.test.ts`, `.spec.ts`, `__tests__/` のファイル変更    |
| コメント大量変更   | `comment-analyzer`      | `/** */`, `///`, `# ` のブロック追加（10行以上）                   |
| nil/ポインタ操作   | `nil-path-reviewer`     | `*`, `nil`, `Option`, `.Get()`, ポインタ型フィールドの追加/変更    |
| spec file 存在     | `product-reviewer`      | `docs/specs/*.prompt.md` がリポジトリに存在                        |
| UI 変更            | `design-reviewer`       | `.tsx`, `.css`, `.scss`, `.html`, `.vue`, `.svelte` のファイル変更 |
| L規模/API境界変更  | `longevity-reviewer`    | 200行以上の変更、または API 境界ファイル（handler, controller, api, endpoint, route, server）の変更 |
| 依存・設定変更     | `security-reviewer`     | `package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`, `*.lock`, `.yaml`, `.toml` のファイル変更 |

### Multi-Model Triangulation（高リスク変更の多モデル検証）

以下のいずれかに該当する変更では、通常のレビューアー構成に加えて **3-way 検証** を自動適用する。
debate skill の三角測量パターンを review フローに統合したもの。

**発動条件**（いずれか1つ）:
- セキュリティ関連の変更（auth, crypto, input validation, permission）かつ 30行以上
- CLAUDE.md, settings.json, hooks の変更（ハーネス変更）
- API 境界の破壊的変更（export シグネチャの変更）

**適用方法**:
- 通常の reviewer 構成（Step 2 テーブル）で選定されたレビューアーに加えて、 `codex-reviewer` と Gemini セキュリティレビューの **両方** が自動的に含まれることを保証する
- 既に含まれている場合は重複追加しない
- 3-way の結果は Step 4 Synthesis で Capability-Weighted Synthesis（ルール14）に従って統合する

**注意**: 200行超の変更では既に 3-way レビューが適用されるため、このルールは **200行未満の高リスク変更** で主に効果を発揮する。

### Gemini セキュリティレビュー（3-way レビュー、~200行以上）

~200行以上の変更では、Codex(深さ) + Claude(幅) に加えて **Gemini(セキュリティ・エコシステム)** を投入する。
3つの独立した視点で盲点を最小化する（claude-octopus の 3-way review パターン）。

**Gemini への起動方法**: Agent ツールで `gemini-explore` エージェントを他レビューアーと並列起動。プロンプト例:

> Review the following git diff from a security and ecosystem perspective.
> Check: dependency risks, known CVE patterns, OWASP Top 10 violations,
> better alternatives in the ecosystem, and community anti-patterns.
> Output: [CRITICAL/HIGH/MEDIUM] file:line - description

### 戦略的整合性チェック（"On the Loop" レビュー）

"The Self-Driving Codebase" の知見: 「技術的に正しいが戦略的に間違っている」変更を検出する。

**spec file が存在する場合** (`docs/specs/*.prompt.md`):
- `product-reviewer` を**必須**レビューアーとして追加（行数に関わらず、50行以上で適用）
- プロンプトに spec file のパスを含め、acceptance criteria との整合性を検証

**product-reviewer への追加指示**:
- 変更が spec の acceptance criteria を満たしているか
- スコープクリープ（spec にない機能の追加）がないか
- spec が意図する問題を実際に解決しているか
- 技術的に正しくても、ユーザー課題の解決から外れていないか

### Adversarial Framing 選択

レビュー対象の性質に応じて、reviewer 起動時のプロンプトに Framing を注入する。
Framing は Step 3 (Dispatch) で各 reviewer の Agent prompt に追加する。agent 定義自体は変更しない。

| 対象シグナル | Framing | プロンプト注入 |
|-------------|---------|--------------|
| security 変更（auth, crypto, input validation） | Adversarial | 「脆弱性が存在すると仮定し、攻撃者の視点で検証せよ」 |
| UX/デザイン変更（.tsx, .css, .html） | Skeptical | 「AI Slop パターン（均一スペーシング、紫青グラデーション、定型 CTA）を疑え」 |
| ロジック/アルゴリズム変更 | Neutral + Edge-case Probe | （デフォルト。追加 Framing なし） |
| ドキュメント変更（.md, コメント） | Accuracy-first | 「コードとの乖離を探せ。陳腐化した記述を検出せよ」 |
| インフラ/設定変更（settings.json, CI, hooks） | Conservative | 「既存動作への影響を最優先で検証せよ。後方互換性を確認せよ」 |

**制約** (agency-safety-framework.md 準拠):
- Adversarial framing は security-reviewer にのみ強く適用
- 汎用 reviewer (code-reviewer, edge-case-hunter) には Adversarial を使わない（false positive 増加リスク）
- 合成フェーズ (Step 4) では Framing を使わない（中立的に統合）

## Step 3: Dispatch

**Agent ツールで1メッセージに全レビューアーを並列起動する。**

#### 起動モード

全レビューアーは read-only（Read, Bash, Glob, Grep のみ）のため、plan モードを指定しない。
Agent ツールの `mode` パラメータは省略するか `"default"` を使う。
`"plan"` を指定するとターンが plan 承認に消費され、レビュー出力が途中終了するリスクがある。

#### フレーミング注入

各レビューアーの prompt 先頭に **Sync フレーミング**（`references/subagent-framing.md`）を付加する:

> あなたはサブエージェントです。結果は親エージェントに返され、統合されます。
> 要点を簡潔にまとめてください。詳細な説明より、発見事項と推奨アクションを優先してください。

各エージェントへのプロンプトには以下を含める:

- レビュー対象の git diff
- 変更ファイルのパス一覧
- プロジェクトの CLAUDE.md（存在する場合）

詳細なルーティング情報は `references/reviewer-routing.md` を参照。

## Step 4: Synthesis

全レビューアーの結果を `templates/review-output.md` のフォーマットに従って統合する。

統合ルール:

1. **セマンティック重複排除**: 同一ファイル ±10行以内 + 同一 failure_mode の指摘は最高信頼度の1件に統合。統合元は「(他 N 件のレビューアーも同様の指摘)」と注記
2. **信頼度ブースト**: 複数の独立したレビューアーが同じ問題を指摘した場合、信頼度を `max(scores) + 5`（上限100）に引き上げ
3. **対立検出**: 同じ箇所で矛盾する指摘がある場合、両方残して `[CONFLICT]` タグを付与
4. **重要度順**: Critical → Important → Watch の順に整理
5. **アクション明示**: 各指摘に対して「修正必須」「検討推奨」「要注意」を付与
6. **判定**: Critical が1件以上 → BLOCK。Important が3件以上 → NEEDS_FIX。それ以外 → PASS。Watch は判定に影響しない
7. **信頼度フィルタ**: confidence < 60 の指摘を除外
8. **既存コード除外**: diff の追加行以外への指摘を除外
9. **linter 重複除外**: フォーマッター・linter が検出すべき問題を除外
10. **戦略的整合性**: spec file 存在時、product-reviewer の「spec 不整合」指摘は Critical として扱う
11. **合意率メトリクス**: `agreement_rate = 1 - (conflict_count / total_findings)`。conflict_count は同一ファイル+-5行で矛盾する指摘の組数。レポートの Agreement Rate フィールドに記入する。算出は全レビュー構成で実施（3-way に限定しない）
12. **収束停滞検出**: 以下のいずれかで `[CONVERGENCE STALL]` フラグを立て、verdict を `NEEDS_HUMAN_REVIEW` にする: (a) Critical 矛盾（2+レビューアが同一箇所で PASS vs BLOCK）、(b) Verdict 分裂（PASS と NEEDS_FIX が同数）、(c) Agreement Rate < 70%。詳細: `references/review-consensus-policy.md`
13. **外れ値検出**: codex-reviewer **以外**のレビューアーを対象に、指摘が他と 20% 未満しか重ならない AND 指摘数が平均の 3x 以上の場合、`[OUTLIER]` タグを付与し verdict 計算から除外（情報は保持）。codex-reviewer は Outlier 判定の対象外とし、常に `[DEEP_REASONING]` タグで verdict 計算に含める。詳細: `references/review-consensus-policy.md`
14. **Capability-Weighted Synthesis**: 全レビュー構成（2体以上）で `references/reviewer-capability-scores.md` の capability score でレビューアーの指摘を重み付けする。`effective_weight = capability_score[reviewer][domain] * severity_multiplier` (Critical=3, Important=2, Watch=1)。同一指摘が複数レビューアーから出た場合は重みを合算。合成レポートの指摘一覧を effective_weight 降順でソートする。詳細: `references/review-consensus-policy.md` Section 7
15. **Codex 指摘の必須対応**: codex-reviewer の Critical/Important 指摘は個別に対応を明記すること。「他レビューアーが指摘していない」「外れ値に見える」は無視の理由にならない。Codex の deep reasoning による指摘は verdict 計算から除外してはならない（`[DEEP_REASONING]` タグで常時保持）。詳細: `references/review-consensus-policy.md` Section 4
16. **Synthesis Output Verbosity Constraint (MoA verbosity guard)**: マルチレビューア合成レポートは MoA (Mixture of Agents) パターンの既知の failure mode として**冗長化**しやすい (Wang et al. ICLR 2025 — failure mode #2)。以下を守る: (a) 各 finding の finding フィールドは 2 文以内、(b) 同じ根本原因の指摘は 1 件に集約し「他 N 件も同様指摘」と注記、(c) Watch 指摘は 5 件を超えたら「上位 5 件のみ表示、残りは review-findings.jsonl で参照」に切り詰める、(d) 合成レポート全体が 400 行を超える場合は「Critical のみ詳細、Important は 1 行要約」に圧縮する。verbosity は Signal 低下を意味し、ユーザー体験を損なう。詳細: `references/review-consensus-policy.md` Section 5
17. **ペルソナレビューアーの統合**: reviewer-ma/mu の指摘は `[PERSONA]` タグを付与する。verdict 計算には含めるが、外れ値検出（ルール13）の対象外とする。ペルソナ指摘が汎用レビューアーと重複する場合、ペルソナ側の具体的な修正案（suggestion ブロック、リファクタリングコード）を統合レポートに採用する

### Layer 0 優先ルール（Trust Verification Policy）

レビュー verdict の最終判定前に、Layer 0（決定論的検証）の状態を確認する:

- テスト未実行の場合: verdict に関わらず `[TESTS NOT RUN]` 警告を合成レポートに付加する
- テスト失敗中の場合: verdict を自動的に `BLOCK` に引き上げる
- 全 reviewer が PASS でもテスト未実行なら PASS とみなさない
- code-reviewer の出力に `Applied Checklists:` 行が欠落している場合: 合成レポートに `[CHECKLIST MANIFEST MISSING]` 警告を付加する

Ref: `references/trust-verification-policy.md`

### Mandatory Review Dimensions（4観点必須チェック）

全てのレビューで以下の4観点を必ず確認し、合成レポートに結果を明記する。
速さより品質担保が第一。時間をかけてよい。

| 観点 | チェック内容 | 未確認時のアクション |
|------|-------------|-------------------|
| **影響範囲** | 変更が他ファイル・モジュール・呼び出し元に影響しないか。Step 1.3 Impact Pre-scan の結果を参照し、暗黙の契約変更・間接依存も調査する | レポートに `[IMPACT UNCHECKED]` 警告 |
| **スタイル一貫性** | 既存のコーディングスタイル・パターン・命名規則から逸脱していないか。言語チェックリスト（Step 2）の結果を参照 | レポートに `[STYLE UNCHECKED]` 警告 |
| **セキュリティ** | 脆弱性・インジェクション・認証/認可の懸念がないか。OWASP Top 10 を基準に確認 | レポートに `[SECURITY UNCHECKED]` 警告 |
| **仕様整合性** | spec file が存在する場合は acceptance criteria との整合性、存在しない場合はユーザーの意図・要件との整合性を確認 | レポートに `[SPEC UNCHECKED]` 警告 |

合成レポートの末尾に4観点の確認状況を出力する:

```
## Review Dimensions
- Impact Scope: ✅ checked (影響範囲 N files, 問題なし)
- Style Consistency: ✅ checked
- Security: ✅ checked
- Spec Compliance: ✅ checked / ⚠️ no spec file
```

### Behavior Verification 推奨（UI 変更検出時）

変更ファイルに UI ファイル（`.tsx`, `.css`, `.scss`, `.html`, `.vue`, `.svelte`）が含まれる場合、
合成レポートに以下の推奨を追加する:

```
## Behavior Verification
💡 UI 変更が検出されました。コードレビューに加えて、以下の検証を推奨します:
- `/webapp-testing` でブラウザ動作を確認
- Product Spec がある場合、spec の行動記述と実際の画面挙動を突き合わせ
```

根拠: コードレビューは構造的正しさを検証するが、ユーザーから見た振る舞いの検証は別プロセスが必要（Warp "Spec & Verify"）。

### Negative Signal Review Rule（AI 沈黙 = 盲点シグナル）

verdict が **PASS** かつ Critical/Important 指摘が **0 件** の変更のうち、以下を**すべて**満たす場合、合成レポートに `[NEGATIVE SIGNAL]` 推奨を付加する:

- 変更規模が **M/L**（S は免除）
- 変更が **logic / security / API 境界 / harness** のいずれかを触る
- spec file (`docs/specs/*.prompt.md`) または番号付き ADR (`docs/adr/[0-9]*.md`、`template.md`/`README.md` は除く) が存在する、または comprehension_confidence < 4（Coverage Check 算出後に判定）

出力する推奨:

```
## Negative Signal Review
⚠️ AI レビューは指摘ゼロでしたが、対象が <logic/security/API/harness> です。
「AI が何も言わなかった箇所」こそ仕様由来の盲点が残りやすい。
PASS で閉じる前に、仕様書/ADR/要件と実装の整合を 5-10 分かけて確認してください。
- 確認軸の例: 空配列/境界値の扱い、リトライ/エラー条件、ページネーション境界が仕様どおりか
```

- **verdict は PASS のまま**（新ステータスは作らない）。これは block ではなく、人間の注意配分を促す推奨
- AI のカバー率が中途半端に高い領域（Logic 層、バグ検出 recall ~50-60%）ほど「AI が見たから大丈夫」という自動承認の油断が生じる、という認知バイアス（automation complacency）への対策
- 出典: 「コードレビューの6段階と AI/人間の境界」(2026-06, zenn/kenimo49)。Stage4 (Logic, AI 60%) の中間ゾーンが最も油断を生むという知見

### Coverage Check

レビューの網羅性を検証し、見落としを防ぐ。

1. **ファイルカバレッジ**: 変更ファイル数 vs レビューで言及されたファイル数の比率を算出し、レポートに `File Coverage: N/M (X%)` として出力
2. **大規模変更警告**: 100 行超の変更で全ファイルに言及がない場合、`[LOW COVERAGE]` 警告を付与
3. **comprehension_confidence スコア**: レビュー全体の理解度を 1-5 で評価し、レポート末尾に出力

```
## Comprehension Confidence
comprehension_confidence: ?/5
```

- 5: 全変更の意図・影響を完全に理解してレビュー
- 4: ほぼ全体を理解、一部不明箇所あり
- 3: 主要な変更は理解、周辺の影響は未確認
- 2: 部分的にしか理解できていない
- 1: 変更の意図が不明確

### Run Metrics 記録

Synthesis 完了後、main agent が run 単位の計測を 1 行記録する（reviewer サブエージェントには書かせない）:

- Step 3 dispatch 前後の `date +%s` から wall-clock duration を概算
- 各 reviewer の findings 数・confidence 分布を集計
- `emit_review_metrics()` で `review-metrics.jsonl` に append
- light tier の run も `reviewers: []` で記録する（light 発火率の計測）

スキーマと記録コマンドの詳細: `references/findings-and-feedback.md` の「Run Metrics」セクション。
フィールド名は `review_tier`（`tier` は learnings パイプラインの別概念のため使わない）。

## Step 4.5: Visual Output (difit)

Step 4 の合成レポート出力後、指摘が 1 件以上ある場合に difit を起動してレビュー結果をインラインコメントとして可視化する。

### 変換ルール

Step 4 の各 finding を以下の形式に変換する:

```
finding: { reviewer, file, line, confidence, finding }
  ↓
--comment '<json>'
```

JSON の構造:
```json
{
  "type": "thread",
  "filePath": "<file>",
  "position": { "side": "new", "line": <line> },
  "body": "[<reviewer>] <finding>"
}
```

- `position.side`: 追加行は `"new"`、削除行への指摘は `"old"` を使う
- `line` が範囲の場合: `"line": {"start": <start>, "end": <end>}`
- `confidence` が 80 未満の finding は body に `(confidence: N)` を付記
- **JSON 生成は `python3 -c` や `jq` を使い、シェルで手書きエスケープしない**（ダブルクォート、バックスラッシュ、改行等のエスケープ漏れを防ぐ）
- **秘密情報（トークン、パスワード、API キー等）は `--comment` body に絶対に含めない**
- **コメント数の上限**: Critical/Important 指摘を優先し、最大 20 件まで。超過時は Watch を省略する（ARG_MAX 制限対策）

### 起動コマンド

```bash
# Step 6 (Findings Persistence) の後に起動する（difit はサーバーとして動作し Ctrl+C まで返らないため）
npx -y difit <target> \
  --comment '<json1>' \
  --comment '<json2>' \
  ... &
```

- `<target>` は Step 1 で使用した diff 対象と同じにする（`.`, `staged`, `@ main` 等）
- difit のブランチ比較は `difit @ main` 形式（`main..HEAD` は不可）
- Critical/Important 指摘が 0 件の場合は difit を起動せず、テキストレポートのみ出力する
- `&` でバックグラウンド起動し、Step 5 以降のフロー（Fix Cycle → Findings Persistence）を阻害しない
- difit 起動後、ユーザーにブラウザで確認可能な旨を伝える

### 既存出力との関係

- テキストレポート（`templates/review-output.md` 形式）は**従来通り出力する**
- `review-findings.jsonl` への保存（Step 6）も**従来通り実行する**
- difit は追加の可視化レイヤーであり、既存の出力を置き換えない

## Step 5: Review-Fix Cycle

Step 4 の verdict に応じて、修正→再レビューのサイクルを実行する。

```
Review → verdict 判定
  ├─ PASS           → Step 6 (Findings Persistence) → タスク完了をユーザーに報告
  ├─ NEEDS_FIX      → 指摘を修正 → Validate → 差分のみ再 Review → verdict 再判定
  ├─ BLOCK          → 指摘を修正 → Validate → フル再 Review → verdict 再判定
  └─ NEEDS_HUMAN_REVIEW → ユーザーに判断を委ねる
```

### Fix-Validate ゲート

Fix と Re-Review の間に挟む軽量な修正品質チェック。
Re-Review は「新たな問題があるか？」を問うが、Validate は「この修正は正しいか？」を問う。
不適切な修正を Re-Review に回す前に弾くことで、ループの収束を加速する。

#### チェック項目

各修正について以下を判定する:

1. **根本原因対処**: 指摘の根本原因に対処しているか、症状のみの修正（バンドエイド）か
2. **スコープ適切性**: 修正が指摘のスコープに収まっているか（過剰な変更を含んでいないか）
3. **副作用リスク**: 修正が新たな問題を導入する可能性がないか（型不整合、import 破損等）

#### 判定結果

| 結果 | アクション |
|------|-----------|
| **VALID** | Re-Review に進む |
| **BAND-AID** | `[BAND-AID]` タグ付与 + 根本原因の修正案を併記。Critical 指摘の修正がバンドエイドの場合、自己修正を試みる（1回のみ） |
| **OVER-SCOPED** | 修正を指摘スコープに絞り込んで再修正 |

- Validate で自己修正した場合、修正後に再度 Validate を通す（最大1回。2回目で VALID にならなければそのまま Re-Review へ）
- Validate は Re-Review より軽量: 修正 diff と元の指摘の突き合わせのみで、新たな問題の探索はしない

### サイクルルール

1. **PASS**: 修正不要。Step 6 に進み、完了をユーザーに報告する
2. **NEEDS_FIX**: Important 指摘を修正後、**Fix-Validate ゲート**を通し、**修正差分のみ**を対象に再レビューする（レビューアー構成は修正行数で再スケーリング。ただし codex-reviewer は初回起動時は再スケーリングに関わらず必ず再起動する）
3. **BLOCK**: Critical 指摘を修正後、**Fix-Validate ゲート**を通し、**全変更**を対象にフルレビューを再実行する（codex-reviewer を必ず含める）
4. **NEEDS_HUMAN_REVIEW**: レビュー結果をユーザーに提示し、判断を委ねる
5. **最大サイクル数**: 3回。3回で PASS にならない場合はユーザーにエスカレーションする
6. **修正なし判定**: 再レビューで新規指摘がゼロなら PASS に昇格する
7. **コード振り子検出**: 2回目以降の再レビュー時、前回修正との diff を取り revert パターン（A→B→A）を検出する。検出時は `[CODE OSCILLATION]` フラグ + directive pinning を適用する。詳細: `references/review-consensus-policy.md` §3.1
8. **Fix → focused test rerun + review rerun の二重 rerun**: review-triggered fix がコードを変更したら、(a) **focused test rerun** (影響を受けるテストのみ、全テスト不要) を行い、(b) そのうえで structured review を rerun する。**fix 後に test 未実行のまま PASS にしてはならない** (Layer 0 Trust Verification の延長)。focused 範囲は fix で変更したファイル + Step 1.3 Impact Pre-scan の caller 関連テストに絞る。出典: openclaw/agent-skills `autoreview` SKILL "If a review-triggered fix changes code, rerun focused tests and rerun the structured review helper"

### 完了報告

サイクルが PASS で終了したら、ユーザーに以下を報告する:
- 変更サマリ（何を変えたか）
- レビュー結果（PASS + 主要な確認ポイント）
- **`[NITS_REMAIN]` タグ付き PASS の場合**: 残存 NIT/FYI を一覧表示し、対応するか保留するかをユーザー判断に委ねる (Google "LGTM with comments" の operationalize、詳細: `agents/code-reviewer.md` "Verdict 補助タグ" セクション)
  - 例: `PASS [NITS_REMAIN: 2 NIT, 1 FYI]` → 「approve しましたが、以下 3 件は対応任意です: [NIT] file:42 ..., [NIT] file:88 ..., [FYI] file:120 ...」
- 次のアクション提案（commit / 追加作業など）

### Harness Review Flag

PASS 後、ハーネスファイル（scripts/, settings.json, CLAUDE.md, agents/）が変更対象に含まれていた場合、completion-gate の mandatory review gate を解除するためにフラグを書き出す:

```bash
python3 "$HOME/.claude/scripts/lib/harness_review_flag.py" write
```

このフラグは変更ファイルセットのハッシュで管理されるため、フラグ書き出し後に追加編集があると自動的に無効化される。

## Step 6: Findings Persistence（フィードバックループ）

Step 4 の統合後、最終レポートに含まれる各指摘を `review-findings.jsonl` に保存する。
git commit 時に `claude-hooks` post-bash (review-feedback 機能) が指摘の受入/却下を自動判定し、
レビューアーの精度追跡を可能にする。

- 保存スクリプト (Python + emit_review_finding)
- ID 生成ルール `rf-YYYY-MM-DD-NNN`
- failure_mode マッピング (FM-XXX、`references/failure-taxonomy.md` 参照)

詳細フロー: [`references/findings-and-feedback.md`](references/findings-and-feedback.md) の Step 6 セクション。

## Step 6.5: Explicit Feedback Collection（指摘精度の明示的フィードバック）

verdict が **NEEDS_FIX** または **BLOCK** の場合のみ実行する。
PASS の場合は Step 7 に進む。

Critical/Important 指摘を番号付きで表示し、accept/reject/partial/deferred をバッチ形式で確認 → `update_finding_outcome()` で記録。

主要ルール:
- CONSIDER/Watch 指摘は表示せず auto_diff に委ねる
- 10 件超は MUST のみ表示
- explicit 優先 (R-05): 後続の auto_diff で上書きされない

詳細フロー (バッチパーサ + 表示フォーマット): [`references/findings-and-feedback.md`](references/findings-and-feedback.md) の Step 6.5 セクション。

## Step 7: Review Quality Feedback（オプション）

レビュー完了後、ユーザーにレビュー品質のフィードバックを求める。明示的なフィードバックがあった場合のみ
`~/.claude/skill-data/review/review-feedback.jsonl` に記録 (毎回中断しない)。

詳細フォーマット: [`references/findings-and-feedback.md`](references/findings-and-feedback.md) の Step 7 セクション。

## Data Storage

レビュー結果のサマリを `~/.claude/skill-data/review/reviews.jsonl` に append-only 蓄積。
AutoEvolve が定期的に分析し、頻出パターンを rules/ に反映する。

詳細フォーマット: [`references/findings-and-feedback.md`](references/findings-and-feedback.md) の Data Storage セクション。

## Anti-Patterns

| # | ❌ Don't | ✅ Do Instead |
|---|---------|--------------|
| 1 | レビューアーを直接 Skill ツールで起動する | Agent ツールで1メッセージに並列起動する |
| 2 | 行数だけでスペシャリストを判断する | コンテンツシグナルも分析して選定する |
| 3 | レビュー結果をそのまま列挙する | 統合・重複排除して構造化する |
| 4 | 10行以下の変更に対してフルレビューを実行する | Verify のみで十分 |
| 5 | findings の保存を省略する | `review-findings.jsonl` に保存してフィードバックループを維持する |
| 6 | レビュー実行中に nested reviewer や reviewer panel を **追加で**再起動する (Step 3 で並列起動した構成を途中で変える、別 skill から `/review` を入れ子で呼ぶ等) | 1 bundle / 1 engine / 1 result で完結する。Step 3 で並列起動した reviewer 構成を最後まで使い、必要なら Step 5 Re-Review (差分のみ or フル) で再走させる。出典: openclaw/agent-skills `autoreview` SKILL "Do not invoke built-in `codex review`, nested reviewers, or reviewer panels from inside the review. The helper builds one bundle, calls one selected engine, validates one structured result, and stops" |
| 7 | verdict `PASS` 後に "better wording" / "nicer clean line" / "second opinion" 目的で追加レビューを走らせる | helper / synthesis が「accepted/actionable findings ゼロ」で exit したら停止する。terse な output でもそのまま clean result として報告する。出典: openclaw/agent-skills `autoreview` SKILL "Stop as soon as the helper exits 0 with no accepted/actionable findings. Do not run an extra review just to get a nicer 'clean' line, a second opinion, or clearer closeout wording" |

## Gotchas

- **staged vs unstaged の混同**: `git diff --cached` はステージ済みのみ、`git diff` は未ステージのみ、`git diff HEAD` は両方を含む。レビュー対象に応じて使い分けること
- **レビュアー起動の順序依存**: Agent ツールで並列起動する際、全レビュアーを1メッセージにまとめないと逐次実行になる
- **言語チェックリストの Read 忘れ**: code-reviewer にチェックリストを注入し忘れると、汎用レビューしか行われない。Step 2 の言語判定を省略しないこと
- **信頼度フィルタの閾値**: confidence 80未満のフィルタが厳しすぎると、有効な指摘も消える。初回は閾値なしで実行し、ノイズを見てから調整
- **codex-reviewer との重複**: code-reviewer と codex-reviewer が同じ指摘をすることがある。Synthesis ステップで重複排除すること

## Skill Assets

- 統合レポートテンプレート: `templates/synthesis-report.md`
- diff 統計抽出: `scripts/extract-diff-stats.sh` — `sh scripts/extract-diff-stats.sh [ref]` で JSON 出力
