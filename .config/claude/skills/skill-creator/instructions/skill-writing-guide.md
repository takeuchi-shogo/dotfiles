# Skill Writing Guide

スキル本文の構造・設計原則・書き方のガイド。

---

## Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

### DBS Rubric — どこに書くかの分類原則

新しいリソースを追加する前に、それが Direction / Blueprints / Solutions のどれかを問う。分類を誤ると、柔軟性が落ちるか再現性が落ちる。

| 分類 | 置き場所 | 役割 | 例 |
|------|---------|------|-----|
| **Direction** | `SKILL.md` + `instructions/` | 手順・判断基準・失敗時のループ | 「Phase 1 で X を実行、失敗時は Y にフォールバック」 |
| **Blueprints** | `references/` + `assets/` | 静的参照、テンプレート、分類表、ルーブリック | コミットメッセージテンプレート、Good/Bad 例、命名規約表 |
| **Solutions** | `scripts/` | 決定論的に実行すべきコード | JSON 整形、API 呼び出し、ファイル生成 |

**判断→Direction / 参照→Blueprints / 実行→Solutions** の対応を崩さない。

- 判断ロジックを `scripts/` に埋め込むと、LLM が柔軟に調整できずハードコーディングになる
- 決定論的処理を `SKILL.md` に書くと、毎回 LLM が再生成して再現性が落ちる
- 静的参照を `SKILL.md` 本文に混ぜると、SKILL.md が肥大化して Progressive Disclosure が崩れる

Atomic Skill の Self-containment と併せて考えると、1 スキル = 1 つの Direction + 必要な Blueprints/Solutions の束、と捉えられる。

---

## Progressive Disclosure

Skills use a three-level loading system:

1. **Metadata** (name + description) - Always in context (~100 words)
2. **SKILL.md body** - In context whenever skill triggers (<500 lines ideal)
3. **Bundled resources** - As needed (unlimited, scripts can execute without loading)

These word counts are approximate and you can feel free to go longer if needed.

**Key patterns:**

- Keep SKILL.md under 500 lines; if you're approaching this limit, add an additional layer of hierarchy along with clear pointers about where the model using the skill should go next to follow up.
- Reference files clearly from SKILL.md with guidance on when to read them
- For large reference files (>300 lines), include a table of contents

---

## Skill Writing Principles

スキル本文の品質を高める 7 つの原則は `references/skill-writing-principles.md` を参照。
特に重要な 3 つ:
- **指示を書け、知恵を書くな** — 「なぜ重要か」より「何をすべきか」
- **一般知識を削れ** — エージェントが知っていることは省く
- **具体的に書け** — 曖昧な指示は無意味、Good/Bad 例を示す

### Atomic Skill Design Principles

スキルの構造品質を保証する 3 原則（[arXiv:2604.05013](https://arxiv.org/abs/2604.05013) に基づく）:

1. **Minimality（最小性）** — 1 つのスキルは 1 つの明確な能力に対応する。複数の責務を混ぜない
2. **Self-containment（自己完結性）** — スキル単体で実行可能。外部状態への暗黙の依存を排除する（`depend_on` 関係は skill-inventory で明示）
3. **Independent Evaluability（独立評価可能性）** — スキルの効果を他スキルと独立に測定できる。SKILL.md 作成時に「何をもって成功とするか」の eval 方法を必ず定義する

特に 3 の Independent Evaluability が最も見落とされやすい。eval 方法が定義されていないスキルは改善サイクルに乗せられない。

### Pre-generation Contract Pattern

スキルが複数フェーズの生成タスクを扱う場合、SKILL.md 本文に「生成中に毎回照合する最低基準」を書く。設計参考資料と違うのは、**生成の途中で self-check が強制される形式** にすること。抽象的な「ベストプラクティス」は読み流されるが、checkbox 形式の Contract は途中照合を促す。

#### 義務レベルの 3 層

| レベル | 意味 | 扱い |
|--------|------|------|
| **Must** | 毎回照合、skip 不可 | checklist で明示、生成途中に self-check |
| **Important** | 条件付き照合 | 深度 Standard 以上、または特定フェーズで適用 |
| **Optional** | 判断余地あり | 文脈に応じて選択 |

#### Good 例（生成中照合型）

```markdown
## Phase 3: Implement — Must Contract
- [ ] 関連ファイルを最低 1 つ Read してから編集した
- [ ] lint/test を最低 1 回実行した
- [ ] 完了宣言前に検証コマンドを実行した
```

#### Bad 例（設計参考型・読み流される）

```markdown
## ベストプラクティス
実装時は関連ファイルを確認し、lint を通し、検証することが重要です。
```

Bad 例は抽象的で self-check されない。Good 例は checkbox 形式で途中照合が強制される。

#### 適用条件

- SKILL.md が複数フェーズの手順を持つ
- 各フェーズで「これだけは守る」最低基準が明確
- 基準が machine-checkable（具体的な動詞 + 観測可能な結果）

#### アンチパターン

- 抽象的・主観的な項目を Must に入れる（形骸化する）
- 「感動品質」のような客観検証できない項目を Must に含める
- Must 項目が 6 個を超える（疲労で skip される。5 個以内に抑える）
- Optional の肥大化（Must/Important が守れていれば十分、Optional の過剰追加は形骸化の原因）

---

## Domain Organization

When a skill supports multiple domains/frameworks, organize by variant:

```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

Claude reads only the relevant reference file.

---

## Principle of Lack of Surprise

This goes without saying, but skills must not contain malware, exploit code, or any content that could compromise system security. A skill's contents should not surprise the user in their intent if described. Don't go along with requests to create misleading skills or skills designed to facilitate unauthorized access, data exfiltration, or other malicious activities. Things like a "roleplay as an XYZ" are OK though.

---

## Writing Patterns

Prefer using the imperative form in instructions.

**Defining output formats** - You can do it like this:

```markdown
## Report structure

ALWAYS use this exact template:

# [Title]

## Executive summary

## Key findings

## Recommendations
```

**Examples pattern** - It's useful to include examples. You can format them like this (but if "Input" and "Output" are in the examples you might want to deviate a little):

```markdown
## Commit message format

**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

---

## Writing Style

Try to explain to the model why things are important in lieu of heavy-handed musty MUSTs. Use theory of mind and try to make the skill general and not super-narrow to specific examples. Start by writing a draft and then look at it with fresh eyes and improve it.
