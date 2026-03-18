# Cursor Configuration Enrichment Design

## Motivation

MSR '26 論文 "Speed at the Cost of Quality" (arxiv:2511.04427) は、Cursor 導入が一過性の速度向上（+281% 初月）と持続的な品質劣化（+41.6% 複雑度、+30.3% 静的解析警告）を引き起こすことを実証した。品質劣化は将来の速度を最大 64.5% 低下させる自己強化サイクルを生む。

現在の dotfiles の Cursor 設定は `global.mdc`（42行）のみで、Claude Code 側の成熟した QA 基盤（rules 15+、agents 28、skills 56+、hooks 15+）と大きな乖離がある。

本設計は、論文の教訓「QA を第一級市民にせよ」を実装し、Claude Code の Progressive Disclosure 設計哲学を Cursor ネイティブ機能に適応する。

## Design Decisions

| 決定 | 選択 | 理由 |
|------|------|------|
| アプローチ | ハイブリッド型 | 共通原則は移植、Cursor 固有機能は新規設計 |
| 言語対象 | TS/React 最優先 + Python/Go/Rust 全移植 | ユーザーは多言語フルスタック |
| 構築スコープ | フル構築 | Rules + Skills + Subagents + Commands + Hooks |
| symlink | 全ディレクトリ dotfiles 管理 | マシン間再現性 |
| 設計思想 | Progressive Disclosure 型 | Cursor の適用メカニズム（Always/Auto/Agent Decides）を活用 |

## Architecture

### Directory Structure

```
.cursor/
├── rules/                          # Rules（MDC フォーマット）
│   ├── global.mdc                  # Always Apply — 共通原則（改修）
│   ├── quality-guard.mdc           # Always Apply — 品質ゲート（論文対策の核心）
│   ├── security.mdc                # Agent Decides — セキュリティルール
│   ├── error-handling.mdc          # Agent Decides — エラーハンドリング
│   ├── testing.mdc                 # Agent Decides — テスト規約
│   ├── typescript.mdc              # Auto Attached — *.ts, *.tsx
│   ├── python.mdc                  # Auto Attached — *.py
│   ├── go.mdc                      # Auto Attached — *.go
│   ├── rust.mdc                    # Auto Attached — *.rs
│   └── react.mdc                   # Auto Attached — *.tsx, *.jsx
├── skills/                         # Skills（SKILL.md フォーマット）
│   ├── review/SKILL.md             # /review — コードレビュー実行
│   ├── commit/SKILL.md             # /commit — conventional commit 生成
│   ├── create-pr/SKILL.md          # /create-pr — PR 作成
│   ├── spec/SKILL.md               # /spec — 仕様書生成
│   ├── test-fix/SKILL.md           # /test-fix — テスト実行→修正ループ
│   ├── refactor/SKILL.md           # /refactor — 安全なリファクタリング
│   └── quality-report/SKILL.md     # /quality-report — 品質メトリクスレポート
├── agents/                         # Subagents
│   ├── verifier.md                 # 実装完了の独立検証
│   ├── reviewer.md                 # コード品質レビュー（readonly）
│   └── security-checker.md         # セキュリティチェック（readonly）
├── commands/                       # Commands（再利用可能なワークフロー）
│   ├── review-code.md              # /review-code — レビュー手順
│   ├── run-tests.md                # /run-tests — テスト実行＋修正
│   └── fix-lint.md                 # /fix-lint — lint 修正ループ
├── hooks/                          # Hook スクリプト
│   └── quality-gate.sh             # Agent 停止時の自動 QA
└── hooks.json                      # Hooks 設定
```

### Rules Application Strategy

| ルール | 適用タイプ | トリガー | 目的 |
|--------|-----------|---------|------|
| `global.mdc` | Always Apply | 全セッション | 共通原則・言語・コミット規約 |
| `quality-guard.mdc` | Always Apply | 全セッション | 論文対策: 複雑度制限・静的解析・レビュー必須 |
| `security.mdc` | Agent Decides | description で判断 | OWASP対策・秘密情報・入力検証 |
| `error-handling.mdc` | Agent Decides | description で判断 | エラーパターン・ログ・リカバリ |
| `testing.mdc` | Agent Decides | description で判断 | テスト規約・カバレッジ・TDD |
| `typescript.mdc` | Auto Attached | `**/*.ts, **/*.tsx` | TS 型システム・strict 設定 |
| `python.mdc` | Auto Attached | `**/*.py` | Python 規約・型ヒント・uv |
| `go.mdc` | Auto Attached | `**/*.go` | Go イディオム・エラー処理・並行性 |
| `rust.mdc` | Auto Attached | `**/*.rs` | 所有権・エラー・trait 設計 |
| `react.mdc` | Auto Attached | `**/*.tsx, **/*.jsx` | Hooks・Server Components・合成 |

> **Note: glob の意図的重複** — `.tsx` ファイルは `typescript.mdc` と `react.mdc` の両方が Auto Attach される。
> これは意図的な設計: TS の型規約と React のコンポーネント規約を同時に適用する。Claude Code でも同様に共存している。

> **Always Apply のコンテキストコスト試算** — `global.mdc`（~60行）+ `quality-guard.mdc`（~80行）= 常時 ~140行。
> Cursor の推奨上限500行/ファイルに対し、2ファイル合計でも十分に軽量。

### quality-guard.mdc: The Paper's Defense

論文が計測した 3 指標に対応する品質ゲート（閾値は Claude Code `rules/common/code-quality.md` と統一）:

1. **Static Analysis Warnings (+30.3%)** → lint/type チェック必須、完了前に全パス確認
2. **Code Complexity (+41.6%)** → 関数50行・ネスト4段・ファイル400行目安/800行上限
3. **Duplicate Line Density (+7.03%)** → DRY 原則の強制、重複検出時はリファクタリング

追加の防御:
- 3ファイル以上の変更は Plan Mode（`Shift+Tab`）必須
- レビューなしのマージ禁止
- 変更後は必ず lint/test 実行

### Skills Design

#### review/SKILL.md
- git diff で変更を取得
- 変更規模に応じたレビュー深度（S/M/L）
- reviewer Subagent を起動して独立レビュー
- 品質チェック: 複雑度、命名、DRY、エラーハンドリング
- セキュリティチェック: 入力検証、秘密情報、注入攻撃
- 発見事項を severity 付きでマークダウン報告

#### commit/SKILL.md
- git diff --staged で変更を分析
- 変更の性質を判定（feat/fix/docs/refactor/chore）
- conventional commit + 絵文字プレフィックス生成
- lint/test の通過を確認してからコミット実行

#### create-pr/SKILL.md
- git log main..HEAD で全コミットを分析
- PR タイトル（70文字以内）+ Summary（1-3 bullet points）+ Test Plan 生成
- gh pr create で作成、URL を返す

#### spec/SKILL.md
- ユーザーのアイデアをインタビュー形式で深掘り
- 構造化された仕様書（目的、要件、受け入れ基準、制約）を生成
- プロジェクトローカルの `docs/specs/` に保存（dotfiles 管理外）

#### test-fix/SKILL.md
- テストフレームワークを自動検出
- 全テスト実行 → 失敗を分類
- 各失敗の根本原因を分析
- 修正を実装 → 再実行 → 全パスまでループ
- 最大3イテレーション、超えたらユーザーに報告

#### refactor/SKILL.md
- リファクタリング対象と目標を確認
- 既存テストの通過を確認（安全ネット）
- 段階的にリファクタリング実行
- 各段階後にテスト再実行
- 変更前後の比較を報告

#### quality-report/SKILL.md
- プロジェクトの lint を実行、警告数を集計
- ファイル別の行数・複雑度を分析
- 重複コードを検出
- 論文の3指標（警告数、複雑度、重複密度）をレポート
- レポートはプロジェクトローカルの `docs/quality/` に保存（dotfiles 管理外）
- 前回レポートとの差分があれば劣化を警告

### Subagents Design

#### verifier.md
- 変更ファイルを特定し関連テストを実行
- lint/type チェック実行
- 「完了」の主張と実際の状態を照合
- 見落としたエッジケースを指摘
- readonly: false（テスト実行のため）

#### reviewer.md
- readonly: true（コードを変更しない）
- 複雑度増加、警告パターン、重複を検出（論文の知見）
- 命名規約、DRY、エラーハンドリングをチェック
- 具体的な改善提案を行単位で報告

#### security-checker.md
- readonly: true
- OWASP Top 10 チェックリスト
- 秘密情報のハードコード検出
- 入力検証・SQLi・XSS パターン検出
- 依存関係の脆弱性チェック

### Commands Design

> **Skills vs Commands の使い分け**: Skills は AI 主導の高度なワークフロー（判断・分岐・サブエージェント委譲を含む）。
> Commands はシンプルな手順書（ステップバイステップ実行）。create-pr は Skills のみに配置し重複を解消。

#### review-code.md
1. git diff で変更を確認
2. 変更ファイルの元のコードを読む
3. 品質チェック: 複雑度、命名、DRY、エラーハンドリング
4. セキュリティチェック: 入力検証、秘密情報、注入攻撃
5. テストカバレッジ確認
6. 発見事項を severity 付きで報告

#### run-tests.md
1. プロジェクトのテストフレームワークを検出
2. 全テスト実行
3. 失敗があれば原因を分析
4. 修正を提案・実装
5. 再実行して通過を確認

#### fix-lint.md
1. lint を実行して警告・エラーを収集
2. 各問題を分類（auto-fix 可能 / 手動修正必要）
3. auto-fix を適用
4. 手動修正が必要なものを1つずつ修正
5. 再実行して全パスを確認

### Hooks Design

> **出典**: Cursor 公式ブログ "[Best practices for coding with agents](https://cursor.com/blog/agent-best-practices)" (2026-01-09) に
> `hooks.json` の `version: 1` + `stop` イベント + `followup_message` によるループ継続が記載。

#### hooks.json
```json
{
  "version": 1,
  "hooks": {
    "stop": [
      {
        "command": "bash .cursor/hooks/quality-gate.sh"
      }
    ]
  }
}
```

#### hooks/quality-gate.sh
- stdin から Agent のコンテキストを受信
- 未コミットの変更があるか確認
- lint を実行、失敗時は `followup_message` で Agent を再起動
- 3回ループしても修正できなければ停止
- JSON で結果を stdout に出力

### symlink.sh Update

既存定義への追加差分:
```diff
 CURSOR_SYMLINK_FILES=(
+  "hooks.json"
 )
 CURSOR_SYMLINK_DIRECTORIES=(
   "rules"            # 既存 — 削除しない
+  "skills"
+  "agents"
+  "commands"
+  "hooks"
 )
```

### Content Conversion Strategy

Claude Code `.md` → Cursor `.mdc` への変換原則:

1. **コピーではなく適応**: Cursor の Agent が理解しやすい形に再構成
2. **500行制限を厳守**: 各ルールファイルは500行以内（[Cursor 公式推奨](https://cursor.com/blog/agent-best-practices)）
3. **description の品質**: Agent Decides ルールは description がトリガー判断基準
4. **Cursor 固有の追記**: Plan Mode、@Branch、Browser Tool 等への言及
5. **Claude Code 固有概念の除外**: hook名、skill名、agent名は含めない

| Claude Code | Cursor | 変換方針 |
|-------------|--------|---------|
| `rules/common/code-quality.md` (113行) | `quality-guard.mdc` に統合 | 核心部分を抽出 |
| `rules/common/security.md` (137行) | `security.mdc` | Agent Decides に適応 |
| `rules/common/error-handling.md` (74行) | `error-handling.mdc` | Agent Decides |
| `rules/common/testing.md` (85行) + `rules/test.md` (66行) | `testing.mdc` | 統合 |
| `rules/common/overconfidence-prevention.md` (61行) | `global.mdc` に一部統合 | 核心のみ |
| `rules/typescript.md` (259行) | `typescript.mdc` | globs: `**/*.ts, **/*.tsx` |
| `rules/python.md` (144行) | `python.mdc` | globs: `**/*.py` |
| `rules/go.md` (232行) | `go.mdc` | globs: `**/*.go` |
| `rules/rust.md` (176行) | `rust.mdc` | globs: `**/*.rs` |
| `rules/react.md` (100行) | `react.mdc` | globs: `**/*.tsx, **/*.jsx` |
| `rules/config.md` (58行) | `global.mdc` に一部統合 | 設定のベスト・プラクティス |

## Acceptance Criteria

### 自動検証可能
1. `.cursor/` 配下に Rules 10 + Skills 7 + Subagents 3 + Commands 3 + Hooks 2 = **25 ファイル**が存在
2. `symlink.sh` が全ディレクトリ + hooks.json を symlink 対象に含む
3. `task symlink` 実行後、`~/.cursor/` に全ファイルが正しくリンクされる
4. `task validate-symlinks` がパスする
5. 全ルールファイルが500行以内: `wc -l .cursor/rules/*.mdc | tail -1` で確認

### 手動検証（Cursor 起動後）
6. Rules の Always Apply ルールが全セッションで読み込まれる — Cursor Settings → Rules で確認
7. Auto Attached ルールが対象ファイル編集時に自動適用される — `.ts` ファイルを開き、typescript ルールが適用されることを確認
8. Skills が `/` コマンドで一覧に表示される — チャットで `/` を入力し、review/commit/create-pr 等が表示されることを確認
9. Subagents が Agent からの委譲で利用可能 — 「verifier を使って検証して」と指示し、委譲されることを確認
10. Commands が `/` コマンドで呼び出し可能 — `/review-code` を入力し実行されることを確認
11. Hooks の quality-gate.sh が Agent 停止時に実行される — Agent にコード変更を依頼し、停止時に lint が実行されることを確認

## File Count Summary

| Category | Count | Files |
|----------|-------|-------|
| Rules | 10 | global, quality-guard, security, error-handling, testing, typescript, python, go, rust, react |
| Skills | 7 | review, commit, create-pr, spec, test-fix, refactor, quality-report |
| Subagents | 3 | verifier, reviewer, security-checker |
| Commands | 3 | review-code, run-tests, fix-lint |
| Hooks | 2 | hooks.json + hooks/quality-gate.sh |
| Infra | 1 | symlink.sh update |
| **Total** | **26** | |

## References

- [arxiv:2511.04427](https://arxiv.org/abs/2511.04427) — "Speed at the Cost of Quality"
- [Cursor Docs: Rules](https://cursor.com/ja/docs/rules)
- [Cursor Docs: Skills](https://cursor.com/ja/docs/skills)
- [Cursor Docs: Subagents](https://cursor.com/ja/docs/subagents)
- [Cursor Blog: Agent Best Practices](https://cursor.com/blog/agent-best-practices) — hooks.json フォーマット出典
- [Qiita: Cursor Commands完全ガイド](https://qiita.com/Enokisan/items/cc173e90bb6e8e5468db)
- [Research: Cursor Quality/Velocity Paper Analysis](../research/2026-03-18-cursor-quality-velocity-paper-analysis.md)
