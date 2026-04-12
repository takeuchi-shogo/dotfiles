# スキル執筆原則

hamelsmu/evals-skills (meta-skill.md) から適応した、スキル品質を高める 7 つの原則。
スキル作成・改善時に SKILL.md を通すチェックリストとして使用する。

## 1. 指示を書け、知恵を書くな (Write directives, not wisdom)

エージェントには「何をするか」を指示する。「なぜ重要か」の説明は最小限に。

**Bad:** "ドメインエキスパートに生の JSON を読ませないことが重要です。これはアノテーションのボトルネックの最大の原因です。ドメインエキスパートはエンジニアではありません。"

**Good:** "すべてのデータをドメインに最も読みやすい表現でフォーマットする。"

**Bad:** "ROUGE スコアを主要な評価指標として使用することは問題があります。なぜなら表面的なテキスト重複を測定するからです..."

**Good:** "特定の失敗モードに基づく binary pass/fail 評価を使用する。ROUGE, BERTScore, cosine similarity を主要指標にしない。"

**例外**: 指示に従わないと重大な結果を招く場合のみ、1文の「なぜ」を添える。

### 1.1. Invert Test — 反対の結論を導けるか？

skill が conclusion を先取りしていないかを検証する測定可能なテスト。skill を反転した question で呼び出し、反対側の結論に到達できるかを試す。

**Bad:** `/investigate-whistleblower` が常に「silenced された」結論に到達する（どんな evidence でも silenced と判定する）

**Good:** 同じ skill で「complaint は unfounded だった」にも evidence に応じて到達できる

**テスト手順:**

1. skill を本来の question（例: "Was X silenced?"）で呼ぶ
2. 同じ skill を反転 question（例: "Was X's complaint unfounded?"）で呼ぶ
3. 両方が **その場の evidence に基づいて** 異なる結論を出せるか確認
4. 常に同じ側に寄るなら、skill は conclusion を先取りしている prompt の disguise である

**適用範囲:**
- 判断系 skill（investigate, review, validate, debate）
- 評価系 skill（scoring, rating, audit）
- 除外: guard 系 skill（careful, freeze）や pipeline 系 skill（epd, spike）は pass/fail で良い

出典: Garry Tan "Thin Harness, Fat Skills" Principle 2 (Teach Thinking, Not Conclusions)

## 2. 一般知識を削れ (Cut general knowledge)

エージェントが既に知っていることは書かない。ドメイン固有の手順・テンプレート・閾値のみ残す。

**削除対象:**
- 定義（「トレースとは完全な記録で...」）
- 重要性の説明（「エラー分析は最もROIの高い活動で...」）
- フレームワーク一覧（「FastHTML, Streamlit, Gradio, ...が使えます」）
- 動機づけ（「スプレッドシートは失敗します、なぜなら...」）
- 学術引用

**残す対象:**
- ドメイン固有の手順（エージェントが知り得ないもの）
- 具体例付きテンプレート
- 数式と閾値
- ドメイン固有のアンチパターン

## 3. ビルドタスクにスコープを絞れ (Scope to the build task)

スキルがアノテーションアプリ構築なら、全文がそのアプリ構築に役立つべき。

**削除対象:**
- プロセス助言（「週次レビューセッションを設定する」）
- 組織ガイダンス（「3-5人のアノテーターチームを編成する」）
- プロジェクト管理（「開発時間の60-80%をエラー分析に充てる」）

**テスト:** 「この文はエージェントの仕事（何かを構築する or ユーザーをプロセスに導く）に役立つか？」 No なら削除。

## 3.5. スキル化の閾値 (When to create a skill)

**5ステップ以上 × 2回以上の再発** をスキル化の閾値とする。

- 5ステップ未満: memory のメモや references/ のチェックリストで十分
- 5ステップ以上でも1回きり: スキル化のコスト（作成・保守）に見合わない
- 閾値を超えたら: `/skill-creator` で形式化し、再利用可能にする

## 4. 良いデフォルトから始めよ (Start with good defaults)

最もシンプルで正しいアプローチを最初に提示する。高度なテクニックは前提条件を明示してから。

**Bad:** ランダムサンプリング、不確実性サンプリング、失敗駆動サンプリングを同等の選択肢として列挙。

**Good:** "ランダムサンプルから始める。自動評価器がある場合は不確実性サンプリングを追加（評価器が一致しないトレース）。本番監視がある場合は失敗駆動サンプリングを追加（ガードレールやユーザー苦情がトリガーされたトレース）。"

## 5. 具体的に書け (Be concrete)

曖昧な指示は無意味。良い例を示す。

**Bad:** "明確な pass/fail 基準を書け。"

**Good:**
```
Pass: メールがクライアントを名前で呼び、保存済み検索から
少なくとも1つの物件を参照している。
Fail: メールが汎用的な挨拶（「お客様各位」）を使用するか、
クライアントの保存済み検索の物件に一切言及していない。
```

## 6. 警告は指示かアンチパターンに変換せよ (Convert warnings)

「やってはいけないこと」セクションの長い説明は、2つのアプローチに変換する:

**アプローチ A — 本文中の指示に統合:**
- "Binary ラベルを使え、Likert スケールではなく"（フィードバック収集セクション内）
- "最終出力だけでなくフルトレースを表示せよ"（データ表示セクション内）

**アプローチ B — 末尾の簡潔なアンチパターンリスト:**
- ROUGE や cosine similarity を主要評価指標として使用する
- トレースで観察していない失敗モードの評価器を構築する
- 1-5 スケールで評価する（binary pass/fail ではなく）

**アンチパターンは1行ずつ。** 段落が必要なら、それは「知恵」—指示に変換して本文に入れる。

## 7. 参照は1階層まで (No nested references)

SKILL.md → reference.md は OK。reference.md → detail.md は禁止。

- SKILL.md は 500 行以下を目標
- 超えたら reference/ に分割（1階層まで）
- 大きな参照ファイル（300行超）には目次を含める
- 参照ファイルからさらに別ファイルへの参照は作らない

## Anti-Patterns セクションの標準化

全スキルの SKILL.md に `## Anti-Patterns` セクションを含めることを推奨する。

**形式（デフォルト: ❌/✅ 対比テーブル）:**

```markdown
## Anti-Patterns

| # | ❌ Don't | ✅ Do Instead |
|---|---------|--------------|
| 1 | エラー分析を完了する前に評価器を構築する | まずトレースを分析し失敗モードを特定する |
| 2 | Likert スケール (1-5) で評価する | binary pass/fail を使用する |
```

**テーブル形式のメリット:**
- Bad → Good の対比で「代わりに何をすべきか」が明確
- 番号付きで参照しやすい
- 箇条書きより情報密度が高い

**適用判断:**
- 繰り返し違反されるルールには Good/Bad 例を併記（feedback_bad_example_pattern.md 参照）
- 1回の観察のみの場合はアンチパターンに追加しない

## Metadata フィールド

frontmatter の `metadata` セクションに以下のフィールドを含めることを推奨する。

**必須フィールド:**
- `pattern`: スキルの設計パターン（pipeline, reviewer, generator 等）

**推奨フィールド:**
- `version`: セマンティックバージョニング（例: `1.0.0`）。破壊的変更時にメジャーを上げる
- `category`: スキルの分類。以下から選択:
  - `workflow` — epd, spike, rpi, autonomous
  - `quality` — review, validate, verification-before-completion
  - `generation` — spec, frontend-design, autocover
  - `research` — research, absorb, debate, gemini
  - `operations` — morning, daily-report, weekly-review, timekeeper
  - `tooling` — codex, codex-review, webapp-testing
  - `architecture` — senior-architect, senior-backend, senior-frontend
  - `knowledge` — obsidian-*, digest, eureka, continuous-learning
  - `security` — careful, freeze, security-review
  - `meta` — skill-creator, skill-audit, ai-workflow-audit, improve

**オプショナルフィールド:**
- `sources`: スキルの知識ソース（例: `"Harrison Chase: Builder or Reviewer"`）

## Setup Config & Persistent State — 標準スキーマ

スキルが初期設定（Slack channel、repo、API key 等）や履歴状態（過去の standup、diff、decision log 等）を必要とする場合、以下の標準配置に従う。
アドホックに `~/.claude/` 配下に直接書き込むと他スキルと衝突するため、必ず以下の namespace を使う。

### Setup Config — `config.json`

スキルディレクトリ直下に `config.json` を置く（git 管理対象）。初回起動時にスキーマと照合し、未設定フィールドがあればユーザーに質問して埋める。

```jsonc
// .config/claude/skills/{skill}/config.json
{
  "$schema": "./config.schema.json",  // 任意（IDE 補完用）
  "version": "1.0.0",
  "required_setup": ["slack_channel", "repo_url"],  // setup detection 対象
  "slack_channel": "#standup",
  "repo_url": "https://github.com/org/repo"
}
```

**Setup detection フロー** (SKILL.md に必ず書く):

1. スキル起動時、まず `config.json` を読む
2. `required_setup` の各フィールドが空なら `AskUserQuestion` で埋める
3. 取得値を `config.json` に書き戻す（コミットはユーザー判断に委ねる）
4. 秘密情報（token, API key）は `config.json` に**絶対に書かない** → `~/.config/{skill}/secrets.env` か `keychain` に分離

### Persistent State — `~/.claude/skill-data/{skill}/`

スキル自身が過去ログ・履歴・学習データを持つ場合は、`~/.claude/skill-data/{skill-name}/` 配下に置く（**git 管理外**、XDG 類似の namespace）。

```
~/.claude/skill-data/
├── standup/
│   ├── history.jsonl        # 過去の standup (append-only)
│   └── last-run.json        # 前回実行メタデータ
├── decision/
│   └── decisions.jsonl      # /decision の決定ログ
└── {skill}/
    └── ...                  # 任意の state file
```

**命名規約:**

- ディレクトリ名はスキル名と完全一致（frontmatter `name:`）
- append-only ログは `.jsonl`（1行1イベント）
- snapshot は `.json`
- サイズが 10MB を超えたら rotate（`history-{YYYY-MM}.jsonl` 形式）

**読み書きパターン:**

```python
from pathlib import Path
import json
import re

# skill_name は frontmatter から取得し、必ず validation を通す
# 外部入力 (cli 引数、env var、user message) から直接埋め込まない
SKILL_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")

def skill_data_dir(skill_name: str) -> Path:
    if not SKILL_NAME_RE.match(skill_name):
        raise ValueError(f"invalid skill name: {skill_name!r}")
    root = (Path.home() / ".claude" / "skill-data").resolve()
    target = (root / skill_name).resolve()
    # containment check — symlink/.. 等で root 外に出ていないか
    target.relative_to(root)
    target.mkdir(parents=True, exist_ok=True)
    return target

SKILL_DATA = skill_data_dir("standup")

# append
with (SKILL_DATA / "history.jsonl").open("a") as f:
    f.write(json.dumps({"date": "2026-04-11", "items": [...]}) + "\n")

# read last N entries
lines = (SKILL_DATA / "history.jsonl").read_text().splitlines()[-5:]
```

> **セキュリティ注記**: `skill_name` を `..`, 絶対パス, symlink 越しに解釈させると任意パス書き込みの温床になる。`^[a-z0-9-]+$` の validation と `Path.resolve().relative_to(root)` の containment check を必ず通す。

### いつ採用するか（判断フロー）

```
スキルに設定/状態が必要か？
├─ No → 両方とも不要（デフォルト）
├─ 設定のみ（slack_channel 等）        → config.json のみ
├─ 状態のみ（履歴、diff 等）           → skill-data/ のみ
└─ 両方必要                            → config.json + skill-data/
```

**NG パターン:**

- スキル本文にパス/設定をハードコード（ユーザー毎に変わるため）
- `~/.claude/` 直下にファイル散乱（namespace 衝突）
- `config.json` に秘密情報を書く
- セッション毎に `skill-data/` 全体を読み直す（必要部分のみ tail/head）

### 出典

Anthropic "Skills for Claude Code" (2026-04): "Some skills need setup config — Slack channel, repo, environment. Pattern: config.json inside skill. If missing → Claude asks user." を dotfiles namespace に適合。

## Decision Table ガイダンス

類似スキルとの使い分けが曖昧な場合、`## Decision: X vs Y vs Z` セクションを追加する。

**形式:**

```markdown
## Decision: spike vs rpi vs epd

| 状況 | 推奨 | 理由 |
|------|------|------|
| 仕様が曖昧、実現可能性が不明 | `/spike` | 最小実装で検証 |
| 仕様は明確、複雑度が中程度 | `/rpi` | Research→Plan→Implement |
```

**配置ルール:**
- Anti-Patterns セクションの直前、または Shortcuts セクションの直前に配置
- テーブルは 3-5 行に収める（多すぎると判断が遅くなる）
- 推奨列はコマンド名を使う（`/spike` 等）

## 8. 出力を自己スコアリングせよ (Self-score your output)

スキルの出力品質を継続的に測定するため、出力末尾に自己評価を付与する。
このスコアは `skill-executions.jsonl` に記録され、AutoEvolve の改善ループで使用される。

**形式:**
```
Score: [1-10]
Reason: [1文 — 何が良かったか、何が不足か、次回改善点]
```

**スコア基準:**
- 9-10: スキルの stated criteria を完全に満たし、追加価値も提供
- 7-8: criteria をほぼ満たす。軽微な改善余地あり
- 5-6: criteria の一部を満たすが、明確な欠落がある
- 3-4: criteria の大半を満たせていない
- 1-2: ほぼ失敗。根本的な問題あり

**適用ルール:**
- 新規作成・改善するスキルに段階的に導入する（既存スキルの一斉変更はしない）
- Pipeline 型スキル（/improve, /epd 等）の最終出力に付与する
- Guard 型スキル（/freeze, /careful 等）は対象外（pass/fail で十分）
- Score は `scoring-config.json` の `outputSignal.thresholds` で信号分類される

## 9. 動的境界マーカー問題 — 条件分岐で 2^N にキャッシュが爆発する

> Claude Code 本体 Ch04 "Talking to Claude" の `DANGEROUS_uncachedSystemPromptSection` 命名規約と
> "2^N Problem" の知見に基づく。スキル / エージェント定義で条件分岐コンテンツを不用意に書くと、
> prompt cache が条件の組み合わせ数だけ分裂し、コスト / レイテンシ共に急激に悪化する。

### 罠の構造

スキル本文やシステムプロンプトに `if X then A else B` という条件分岐を書くと、
N 個の独立した分岐条件があるだけでキャッシュエントリは **2^N** 通りに増える。

- 条件 1 つ → 2 パターン
- 条件 3 つ → 8 パターン
- 条件 5 つ → 32 パターン
- 条件 10 つ → 1024 パターン（キャッシュヒット率は実質 0）

Claude Code 本体はこの罠を避けるために、静的コンテンツは `systemPromptSection(name, compute)` で書き、
動的コンテンツは明示的に `DANGEROUS_uncachedSystemPromptSection(name, compute, reason)` と命名している。

### スキル作成時の実践ルール

| パターン | Good | Bad |
|----------|------|-----|
| 動的値の埋め込み | セッション ID, 時刻, カレントパスを**含めない** | `現在時刻: ${new Date()}` をプロンプト先頭に |
| ユーザー属性の参照 | `CLAUDE.md` / MEMORY.md 側に書き、スキル本文は参照しない | スキル本文で「ユーザーが Go エンジニアなら X」と分岐 |
| 条件付きセクション | 必要なら別スキルに分離して on-demand invocation | 1 スキル内で `<important if="...">` を乱発 |
| 環境差分の吸収 | hook で環境変数を検出し、プロンプト外で処理 | スキル本文に OS 判定を書く |

### チェックリスト（スキル PR 前）

- [ ] スキル本文にセッション固有値（ID、時刻、乱数、カレントパス）が埋め込まれていないか
- [ ] `<important if="...">` の条件数が 3 以下に収まっているか（超えるならスキル分割）
- [ ] 動的置換トークン (`{{var}}`) がキャッシュ境界の前にあるか（境界後で OK）
- [ ] ユーザー属性による分岐を含む場合、そのスキルは「動的」と明記しているか

### キャッシュ境界の原則

```
[system prompt 固定部]          ← 全ユーザー共有キャッシュ（最大の cost saving）
  ↓
[CLAUDE.md 静的部]               ← user 共有キャッシュ
  ↓
[スキル / エージェント定義]       ← session 内キャッシュ
  ↓
[--- 動的境界マーカー ---]        ← ここから先は毎リクエスト再計算
  ↓
[現在時刻 / セッション ID / etc] ← DANGEROUS: 上に書かない
```

**原則**: スキルは動的境界マーカーの**上**に配置されるため、動的内容を混ぜない。
動的値が必要な場合は hook で後挿入するか、スキル自身を動的スキルとして分離する。
