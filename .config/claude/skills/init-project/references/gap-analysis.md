# Gap Analysis フレームワーク

既存プロジェクトに Claude Code 構造を適応する際の分析・アップグレードフレームワーク。
`--upgrade` フラグで起動される。

---

## Pandey 5層チェックリスト

### Layer 1: CLAUDE.md（Repo Memory）

> **存在 ≠ 十分** (`rules/common/existence-vs-sufficiency.md`): 各項目は「あるか」だけでなく「十分か」も評価する。

```bash
test -f CLAUDE.md && wc -l CLAUDE.md
```

- [ ] 存在するか
- [ ] 100 行以内か
- [ ] WHY（プロジェクトの目的・役割）を含むか — **十分性**: 1行の概要ではなく、新参者が文脈を掴める程度に具体的か
- [ ] WHAT（ディレクトリマップ / 技術スタック）を含むか — **十分性**: 主要ディレクトリが網羅されているか
- [ ] HOW（ワークフロー / コマンド一覧）を含むか — **十分性**: ビルド・テスト・デプロイの具体的コマンドが書かれているか

### Layer 2: Skills（再利用可能なワークフロー）

```bash
ls -d .claude/skills/ 2>/dev/null && ls .claude/skills/*/SKILL.md 2>/dev/null | wc -l
```

- [ ] `.claude/skills/` が存在するか
- [ ] 1 つ以上のスキルがあるか

### Layer 3: Hooks（ガードレール）

```bash
grep -c '"hooks"' .claude/settings.json 2>/dev/null
```

- [ ] `.claude/settings.json` に hooks 設定があるか
- [ ] formatter hook があるか
- [ ] テスト / lint 関連の hook があるか

### Layer 4: Progressive Context（docs/）

```bash
ls docs/architecture.md docs/decisions/ docs/playbooks/ docs/runbooks/ 2>/dev/null
```

- [ ] architecture.md（またはそれに相当するもの）があるか
- [ ] ADR があるか
- [ ] runbook / playbook があるか

### Layer 5: Local CLAUDE.md（リスキーモジュール）

```bash
find . -maxdepth 4 -name 'CLAUDE.md' -not -path './CLAUDE.md' -not -path './.git/*' 2>/dev/null
```

- [ ] リスキーモジュール近くに CLAUDE.md があるか
- [ ] gotchas / invariants が記載されているか

---

## 現在レベル判定

```
Layer 1 のみ                           → S
Layer 1 + (Layer 2 or Layer 4)         → M
Layer 1 + Layer 3 + (Layer 4 or 5)     → L
```

具体的なスコアリング:

| 存在する層 | 判定 |
|---|---|
| なし | 未初期化（フル初期化を提案） |
| L1 のみ | S |
| L1 + L4 | M |
| L1 + L2 | M |
| L1 + L2 + L4 | M → L アップグレード推奨（L3 hooks 追加で L に格上げ可能） |
| L1 + L2 + L3 | L（L4/L5 推奨だが L として扱う） |
| L1 + L3 + L4 | L |
| L1 + L3 + L5 | L |
| L1 + L2 + L3 + L4 + L5 | L（フルスペック） |

---

## ギャップ分析出力フォーマット

```
📊 現在のレベル: M

   Layer 1 (CLAUDE.md):      ✅ 存在 (72行)
   Layer 2 (Skills):         ❌ 未設定
   Layer 3 (Hooks):          ❌ 未設定
   Layer 4 (Docs):           ✅ architecture.md あり
   Layer 5 (Local CLAUDE.md): ❌ 未設定

🔄 アップグレード提案 (M → L):
   1. .claude/settings.json に hooks 設定を追加
   2. src/auth/CLAUDE.md を生成（リスキーモジュール検出）
   3. docs/decisions/ に ADR テンプレートを追加

(1) 提案通りにアップグレード
(2) 一部のみ選択
(3) キャンセル
```

---

## 上書き防止ルール

1. **既存 CLAUDE.md は絶対に上書きしない**
2. 既存ファイルがある場合 → 「追記提案」として差分を提示
3. ユーザーが明示的に承認した場合のみマージ
4. `.claudeignore` は既存エントリを保持しつつ不足分を追加
5. `.claude/settings.json` が存在する場合 → hooks セクションのみ追加提案

---

## アップグレードフロー

### S → M

1. document-factory (mode: constitution) に `references/workflow-guide.md` 生成を委譲
2. 検出言語に応じて `.claude/rules/{lang}.md` を直接生成
3. document-factory (mode: context) に `docs/architecture.md` 生成を委譲

### M → L

1. `.claude/settings.json` に基本 hooks 設定を追加
2. リスキーモジュールを検出し、ユーザー選択後に Local CLAUDE.md を生成
3. `docs/decisions/` に ADR テンプレートを追加
4. CI が存在する場合 → setup-background-agents を実行

### 部分アップグレード

ユーザーが「一部のみ選択」した場合:
- 選択された項目のみ実行
- 残りは「次回提案」としてスキップ
- 実行結果を報告し、再度 `--upgrade` で残りを追加可能と案内
