# レベル別テンプレート

各レベル(S/M/L)の生成物、ファクトリ委譲プロンプト、並列実行マップ。

---

## レベル別生成ファイル一覧

### S（Minimal）

| ファイル | 生成方法 |
|---|---|
| `CLAUDE.md` | document-factory (mode: constitution) |
| `.claudeignore` | document-factory (mode: constitution) |

### M（Standard）

| ファイル | 生成方法 |
|---|---|
| `CLAUDE.md` | document-factory (mode: constitution) |
| `.claudeignore` | document-factory (mode: constitution) |
| `references/workflow-guide.md` | document-factory (mode: constitution) |
| `.claude/rules/{lang}.md` | 直接生成 |
| `docs/architecture.md` | document-factory (mode: context) |

### L（Production）

M の全ファイルに加え:

| ファイル | 生成方法 |
|---|---|
| `.claude/rules/common/security.md` | 直接生成 |
| `.claude/rules/common/testing.md` | 直接生成 |
| `.claude/settings.json` | 直接生成（基本 hooks） |
| `docs/decisions/001-template.md` | document-factory (mode: context) |
| `src/{risky}/CLAUDE.md` | document-factory (mode: context)（検出時のみ） |
| `.github/workflows/` | setup-background-agents（CI 有りの場合） |

---

## ファクトリ委譲プロンプト

### document-factory (mode: constitution)

**S レベル:**
```
以下のプロジェクトの CLAUDE.md と .claudeignore を生成してください。
- プロジェクトパス: {cwd}
- 技術スタック: {tech_stack}
- 最小限の構成（S レベル）: CLAUDE.md は 50 行以内
- references/ や rules/ は生成しない
```

**M/L レベル:**
```
以下のプロジェクトの CLAUDE.md, .claudeignore, references/workflow-guide.md を生成してください。
- プロジェクトパス: {cwd}
- 技術スタック: {tech_stack}
- M/L レベル: CLAUDE.md は 80 行以内
- references/workflow-guide.md で詳細ワークフローを補完
```

### document-factory (mode: context)（architecture.md）

```
以下のプロジェクトの docs/architecture.md を生成してください。
- プロジェクトパス: {cwd}
- 技術スタック: {tech_stack}
- サブシステム概要、依存関係マップ、key abstractions を含める
- Breadcrumb パターンで標準概念は簡潔に
```

### document-factory (mode: context)（Local CLAUDE.md）

```
以下のリスキーモジュールの Local CLAUDE.md を生成してください。
- モジュール: {selected_risky_modules}
- 各モジュールの gotchas と invariants を分析して記述
- 20 行以内で簡潔に
- フォーマット: ## Gotchas / ## Invariants / ## 変更時の注意
```

### document-factory (mode: context)（ADR テンプレート）

```
docs/decisions/001-template.md に ADR テンプレートを生成してください。
フォーマット: Context / Decision / Alternatives Considered / Consequences
```

### setup-background-agents（Skill tool で呼び出し）

```
Skill tool で `/setup-background-agents` を呼び出す。
Agent tool ではなく Skill tool を使用すること（setup-background-agents はスキルであり、エージェントではない）。
- プロジェクトパス: {cwd}
- CI システム: {ci_system}
- 推奨ユースケース: dependency-audit, test-coverage
```

---

## 並列実行マップ

### S
```
document-factory (mode: constitution) (直列)
```

### M
```
┌─ document-factory (mode: constitution) (CLAUDE.md + .claudeignore + workflow-guide)
│
├─ document-factory (mode: context) (docs/architecture.md)           ← 並列
│
└─ [完了後] rules/{lang}.md を直接生成              ← 直列
```

### L
```
┌─ document-factory (mode: constitution) (CLAUDE.md + .claudeignore + workflow-guide)
│
├─ document-factory (mode: context) (docs/architecture.md)           ← 並列
│
├─ document-factory (mode: context) (Local CLAUDE.md)                ← 並列
│
├─ document-factory (mode: context) (ADR テンプレート)               ← 並列
│
├─ setup-background-agents (CI 有りの場合)          ← 並列
│
└─ [全完了後] rules/ + settings.json を直接生成     ← 直列
```

---

## 直接生成テンプレート

### .claude/rules/{lang}.md

言語検出結果に応じて、最小限のルールファイルを生成:

```markdown
# {Language} ルール

- {language-specific convention 1}
- {language-specific convention 2}
- {language-specific convention 3}
```

実際の内容は検出した言語のベストプラクティスを Breadcrumb で記述。

### .claude/rules/common/security.md

```markdown
# セキュリティルール

- ユーザー入力は常にバリデーション・サニタイズする
- シークレットをコードにハードコードしない（環境変数を使用）
- SQL クエリはパラメータ化する（SQL インジェクション防止）
- 認証・認可チェックを API エンドポイントで必ず実施
- HTTPS を強制し、セキュリティヘッダーを設定する
```

### .claude/rules/common/testing.md

```markdown
# テストルール

- 新機能にはユニットテストを必須とする
- テストは独立して実行可能であること（他テストへの依存禁止）
- モックは外部依存のみ。内部ロジックはモックしない
- テスト名は「何を」「どうなるべきか」を明記する
```

### .claude/settings.json（基本 hooks）

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "^(Edit|Write)$",
        "hooks": [
          {
            "type": "command",
            "command": "{formatter_command}"
          }
        ]
      }
    ]
  }
}
```

formatter_command は検出言語に応じて:
- TypeScript/JavaScript: `npx biome check --write $CLAUDE_FILE_PATH` or `npx prettier --write $CLAUDE_FILE_PATH`
- Python: `ruff format $CLAUDE_FILE_PATH`
- Go: `gofmt -w $CLAUDE_FILE_PATH`
- Rust: `rustfmt $CLAUDE_FILE_PATH`
