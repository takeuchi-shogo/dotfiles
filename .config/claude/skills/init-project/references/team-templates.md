# Team Templates (init-project `--team` mode)

`/init-project --team` の詳細フロー。個人 harness と区別した team project 向け scaffold 処理。

## Team Mode の 3 形態

| コマンド | 動作 |
|---------|------|
| `/init-project --team` | `<dotfiles>/templates/team-project/base/` を current repo に展開 (7 ファイル) |
| `/init-project --team --variant <name>` | base 展開後、variant を上書き (concrete example で placeholder の一部を埋める) |
| `/init-project --team --apply-to <dir>` | 既存 team project を Read → gap 分析 → diff 提示 → 承認後に書き込み |

**variant 一覧** (一覧は `<dotfiles>/templates/team-project/variants/` を ls で取得):
- `nextjs-go-connect-gcpaws` — 本業系 (Next.js + Go + Connect RPC + GCP/AWS)
- `nextjs-trpc-hasura-aws` — 副業系 (Next.js + tRPC + Hasura + AWS)

## Phase: Team Detect (team mode 専用の検出)

通常の Phase 1 Detect に加え、team 向けの質問を追加:

```
- team 規模は? (1-2 / 3-5 / 6+) — 人数で Zone 分割の粒度が変わる
- GitHub team 名を使うか? (@org/team-foo) — YES なら CODEOWNERS に team 記法
- 認証・決済コードを含むか? — NO なら auth-payment-policy.md をスキップ
- 既存 CLAUDE.md / docs/ はあるか? — YES なら --apply-to モード推奨
```

## Phase: Team Scaffold (新規 project)

```
1. Read <dotfiles>/templates/team-project/base/ の全ファイル
2. (variant 指定時) Read <dotfiles>/templates/team-project/variants/<name>/ の全ファイル
   → base とマージ (同名ファイルは variant が優先)
3. Placeholder 置換 (対話的に収集)
   - {{PROJECT_NAME}}, {{*_OWNER_GH}}, {{*_PATHS}}, {{*_VERIFY_CMD}} etc.
   - 不明なものは空のまま残す (user が後で埋める)
4. Write to current repo:
   - CLAUDE.md, docs/facts.md, docs/zones/OWNERSHIP.md,
     docs/decisions/0000-template.md, docs/security/auth-payment-policy.md,
     .github/CODEOWNERS, README の team-template セクション
   - variant を使った場合: docs/decisions/0001-tech-stack.md も追加
5. 完了報告: 残った placeholder 一覧 + 次ステップ (branch protection の設定等)
```

## Phase: Team Apply-To (既存 project)

**新しい script を書かない**。既存の `document-factory` agent + Read/Write で実装する。

```
1. Read <project-dir>/CLAUDE.md, docs/, .github/CODEOWNERS (存在する場合)
2. Read <dotfiles>/templates/team-project/base/ の全ファイル
3. Gap 分析 (Opus が実行):
   - 存在しないファイル → Missing
   - 存在するが section が不足 → Partial (どのセクションが足りないか)
   - 存在して十分 → OK
4. ユーザーに diff 提示:
   === CLAUDE.md の差分 ===
   + (新規セクション) §4 Ownership & Zones
   + (新規セクション) §5 Execution Boundaries
   ...
   === 新規作成 ===
   + docs/facts.md (新規)
   + docs/zones/OWNERSHIP.md (新規)
   ...
5. AskUserQuestion: "全部承認 / 個別選択 / なし"
6. 承認されたものだけ Write:
   - 既存 CLAUDE.md は **上書きしない** (section を追記)
   - 既存 docs/ がある場合は merge で判断
7. Placeholder 置換の対話
8. 完了報告
```

### Apply-To の既存ファイル扱い原則

| 既存状態 | team template | 動作 |
|---------|--------------|------|
| CLAUDE.md が空 | CLAUDE.md.tpl | 新規作成 |
| CLAUDE.md が既存 (数行) | CLAUDE.md.tpl | 差分セクションを提案、上書きしない |
| CLAUDE.md が既存 (厚い) | CLAUDE.md.tpl | diff 提示のみ、手動 merge を促す |
| docs/facts.md が無い | facts.md.tpl | 新規作成 |
| .github/CODEOWNERS が無い | CODEOWNERS.tpl | 新規作成 |
| .github/CODEOWNERS が既存 | CODEOWNERS.tpl | diff 提示、手動 merge |

## Integration with `/init-project` 既存フロー

team mode は通常の 5 層構造 (CLAUDE.md / skills / hooks / docs / Local CLAUDE.md) のうち以下を担当:

- **CLAUDE.md**: team 版 template (§1-12 の構造)
- **docs/**: facts.md, zones/OWNERSHIP.md, decisions/, security/
- **skills/ / hooks/**: team mode では**生成しない** (個人 harness との翻訳は team-harness-patterns.md 参照)
- **Local CLAUDE.md**: 従来通り (team mode 固有の処理なし)

## Delegation

実際のファイル生成は既存の `document-factory` agent に委譲可能:

```
document-factory agent に渡す:
  - target directory
  - template source path (dotfiles/templates/team-project/base or variants/*)
  - placeholder 置換マップ
  - 既存ファイル merge 戦略 (for --apply-to)
```

## Post-Scaffold 推奨アクション

team mode 完了後に user に提示する:

1. **Branch protection 設定**: GitHub Settings → Branches → main
   - Require pull request reviews
   - Require review from Code Owners ← 重要
   - Include administrators (推奨)
2. **CODEOWNERS の team 名検証**: `@org/team-foo` が存在するか GitHub で確認
3. **高リスクパス確認**: `{{AUTH_PATHS}}`, `{{PAYMENT_PATHS}}` が実コードに合致しているか
4. **ADR-0001 起票**: variant を使った場合は tech-stack ADR を team で review
5. **README に Claude Code セクション追加**: 使用時の起動方法・前提設定

## 関連資料

- Template 本体: `<dotfiles>/templates/team-project/`
- 適用手順の詳細: `<dotfiles>/templates/team-project/APPLY.md`
- 個人 → team 翻訳マップ: `<dotfiles>/.config/claude/references/team-harness-patterns.md`
- 設計根拠: `<dotfiles>/docs/plans/completed/2026-04-23-team-harness-template-plan.md`
